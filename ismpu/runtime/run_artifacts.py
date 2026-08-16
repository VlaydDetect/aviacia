"""Потоковые артефакты одного полного прогона."""

from __future__ import annotations

import csv
import json
import subprocess
import time
from collections import deque
from collections.abc import Mapping
from dataclasses import asdict, dataclass, fields, is_dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from threading import RLock

from ismpu.config.constants import DT
from ismpu.config.run_matrix import CATALOG_SHA256, SOURCE_SHA256
from ismpu.config.segments import FlightSegment
from ismpu.control.approach import ApproachResult
from ismpu.envs.sim_interface import ApproachData
from ismpu.io.ics_connector import ICSInputs, ICSOutputs


SCHEMA_VERSION = 2
PID_NAMES = (
    "roll", "pitch", "air_speed", "steer",
    "brake_l", "brake_r", "reverse_l", "reverse_r",
)
GROUND_PID_NAMES = frozenset({"steer", "brake_l", "brake_r", "reverse_l", "reverse_r"})

SAMPLE_ID_FIELDS = (
    "execution_id", "tick_id", "sequence", "timestamp_utc", "monotonic_s",
    "time_s", "dt", "scenario_id", "segment", "control_mode",
    "control_valid_mask", "command_sent", "config_revision",
)
NORMALIZED_TELEMETRY_FIELDS = (
    "valid", "lat", "lon", "groundspeed_ms", "ias_ms",
    "heading_true_deg", "heading_magnetic_deg", "track_true_deg",
    "track_magnetic_deg", "runway_heading_true_deg",
    "runway_heading_magnetic_deg", "radio_altitude_ft", "elevation_m", "agl_m",
    "pitch_deg", "roll_deg", "vertical_speed_ms", "p_rad", "q_rad", "r_rad",
    "accel_long_g", "accel_norm_g", "accel_side_g", "wind_speed_ms",
    "wind_dir_from_deg", "runway_length_m", "runway_width_m",
    "lateral_deviation_m", "lateral_deviation_sign", "ils_valid",
    "main_gear_contact", "weight_on_wheels", "flight_phase", "agent_active",
    "faults", "weather",
)
COMMAND_FIELDS = (
    "cmd_elevator_g", "cmd_aileron_deg", "cmd_throttle_norm",
    "cmd_throttle_left_rate", "cmd_throttle_right_rate", "cmd_rudder_norm",
    "cmd_pedal_norm", "cmd_tiller_norm", "cmd_brake_l", "cmd_brake_r",
    "cmd_reverse_l", "cmd_reverse_r", "break_control", "quality_lateral",
    "quality_heading", "quality_speed",
)
GROUND_DIAGNOSTIC_FIELDS = (
    "guidance_xte_m", "guidance_course_error_deg", "guidance_heading_error_deg",
    "guidance_error_deg", "guidance_along_track_m", "guidance_source", "guidance_event",
    "ground_reference_speed_ms", "ground_speed_error_ms", "ground_acceleration_ms2",
    "ground_distance_m", "ground_completion_rule", "ground_completion_reached",
    "ground_reverse_allowed", "lateral_pid_requested", "lateral_pid_limited",
    "lateral_pid_saturated", "allocator_steering_applied",
    "allocator_failure_compensation", "allocator_saturated",
)
ACTUATOR_NAMES = (
    "rudder", "pedal", "tiller", "brake_left", "brake_right", "reverse_left", "reverse_right",
)
ALLOCATOR_TELEMETRY_FIELDS = tuple(
    f"allocator_{stage}_{name}"
    for stage in ("base", "lateral", "requested", "limited")
    for name in ACTUATOR_NAMES
)
ACTUATOR_FEEDBACK_FIELDS = (
    "feedback_rudder_deg", "feedback_nose_wheel_deg",
    "feedback_brake_left_mm", "feedback_brake_right_mm",
    "feedback_throttle_left_deg", "feedback_throttle_right_deg",
    "feedback_thrust_left", "feedback_thrust_right",
    "feedback_longitudinal_accel_g", "feedback_lateral_accel_g",
    "feedback_yaw_rate_rad_s",
)
ICS_INPUT_FIELDS = tuple(item.name for item in fields(ICSInputs))
ICS_OUTPUT_FIELDS = tuple(item.name for item in fields(ICSOutputs))
ICS_TELEMETRY_FIELDS = tuple(f"ics_{name}" for name in ICS_INPUT_FIELDS)
ICS_COMMAND_FIELDS = tuple(f"ics_out_{name}" for name in ICS_OUTPUT_FIELDS)
APPROACH_INPUT_FIELDS = tuple(item.name for item in fields(ApproachData))
APPROACH_RESULT_FIELDS = tuple(item.name for item in fields(ApproachResult))
APPROACH_TELEMETRY_FIELDS = (
    tuple(f"approach_input_{name}" for name in APPROACH_INPUT_FIELDS)
    + tuple(f"approach_{name}" for name in APPROACH_RESULT_FIELDS)
    + ("approach_tolerances", "approach_criteria_a11", "go_around_reason", "abort_reason")
)
PID_TELEMETRY_FIELDS = (
    "kp", "ki", "kd", "value", "setpoint", "error", "output",
    "p", "i", "d", "integral", "derivative", "unconstrained", "saturated",
)
PID_FIELDS = tuple(
    f"pid_{name}_{field_name}"
    for name in PID_NAMES
    for field_name in PID_TELEMETRY_FIELDS
)
TELEMETRY_FIELDS = (
    SAMPLE_ID_FIELDS + NORMALIZED_TELEMETRY_FIELDS + COMMAND_FIELDS
    + GROUND_DIAGNOSTIC_FIELDS + ALLOCATOR_TELEMETRY_FIELDS
    + ACTUATOR_FEEDBACK_FIELDS + APPROACH_TELEMETRY_FIELDS
    + ("ics_raw_json",) + ICS_TELEMETRY_FIELDS + ICS_COMMAND_FIELDS + PID_FIELDS
)


@dataclass(frozen=True)
class RunSample:
    """Один такт: вход, команда и диагностика имеют общий ``tick_id``."""

    execution_id: str
    tick_id: int
    sequence: int
    timestamp_utc: str
    monotonic_s: float
    time_s: float
    dt: float
    scenario_id: str
    segment: str
    control_mode: int | None
    control_valid_mask: int | None
    command_sent: bool
    config_revision: int
    values: Mapping[str, object]

    def as_row(self) -> dict[str, object]:
        row = {name: getattr(self, name) for name in SAMPLE_ID_FIELDS}
        row["command_sent"] = int(self.command_sent)
        row.update(self.values)
        return row


@dataclass(frozen=True)
class RunEvent:
    sequence: int
    timestamp_utc: str
    monotonic_s: float
    time_s: float | None
    tick_id: int | None
    event: str
    segment: str | None
    data: Mapping[str, object]

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def default_runs_root() -> Path:
    return Path(__file__).resolve().parents[2] / "runs"


def controller_pids(controller) -> dict:
    approach = controller.approach_channel
    ground = controller.pids
    return {
        "roll": approach.roll_pid,
        "pitch": approach.pitch_pid,
        "air_speed": approach.speed_pid,
        "steer": ground.get("runway_center_pid"),
        "brake_l": ground.get("pid_brake_l"),
        "brake_r": ground.get("pid_brake_r"),
        "reverse_l": ground.get("pid_rev_l"),
        "reverse_r": ground.get("pid_rev_r"),
    }


def gains_snapshot(controller) -> dict:
    return {
        name: {"kp": pid.kp, "ki": pid.ki, "kd": pid.kd}
        for name, pid in controller_pids(controller).items() if pid is not None
    }


def pid_operating_points(controller, telemetry=None) -> dict:
    """Value/setpoint в нативных единицах регуляторов на входном кадре такта."""
    result = controller.approach_channel.result
    telemetry = telemetry or controller.last_step_telemetry or controller.last_telemetry
    airborne = getattr(telemetry, "approach_inputs", None)
    lateral = getattr(getattr(controller, "lateral_channel", None), "last_diagnostics", None)
    longitudinal = getattr(
        getattr(controller, "longitudinal_channel", None), "last_diagnostics", None)
    speed_pair = {
        "value": getattr(longitudinal, "value", None),
        "setpoint": getattr(longitudinal, "setpoint", None),
    }
    return {
        "roll": {"value": getattr(airborne, "RollAngle", None),
                 "setpoint": result.target_roll_deg},
        "pitch": {"value": getattr(airborne, "PitchAngle", None),
                  "setpoint": result.target_pitch_deg},
        "air_speed": {"value": getattr(airborne, "IndicatedAirspeed", None),
                      "setpoint": result.target_ias_kt},
        "steer": {"value": getattr(lateral, "value", None),
                  "setpoint": getattr(lateral, "setpoint", None)},
        "brake_l": dict(speed_pair), "brake_r": dict(speed_pair),
        "reverse_l": dict(speed_pair), "reverse_r": dict(speed_pair),
    }


def sample_values(telemetry, controller) -> dict[str, object]:
    """Собрать фиксированную CSV-схему без файлового I/O; используется и replay."""
    state = controller.state
    approach_inputs = getattr(telemetry, "approach_inputs", None)
    approach_result = controller.approach_channel.result
    lateral = getattr(getattr(controller, "lateral_channel", None), "last_diagnostics", None)
    longitudinal = getattr(
        getattr(controller, "longitudinal_channel", None), "last_diagnostics", None)
    allocation = getattr(getattr(controller, "ground_allocator", None), "last_diagnostics", None)
    ics_inputs = getattr(telemetry, "ics_inputs", None)
    sim = getattr(controller, "sim", None)
    outputs = (
        getattr(sim, "last_outputs", None)
        if getattr(controller, "last_step_send_attempted", False) else None
    )
    faults = sorted(getattr(item, "name", str(item)) for item in telemetry.faults)
    row: dict[str, object] = {
        "valid": int(bool(telemetry.valid)), "lat": telemetry.lat, "lon": telemetry.lon,
        "groundspeed_ms": telemetry.groundspeed_ms, "ias_ms": telemetry.ias_ms,
        "heading_true_deg": telemetry.heading_true_deg,
        "heading_magnetic_deg": telemetry.heading_magnetic_deg,
        "track_true_deg": telemetry.track_true_deg,
        "track_magnetic_deg": telemetry.track_magnetic_deg,
        "runway_heading_true_deg": telemetry.runway_heading_true_deg,
        "runway_heading_magnetic_deg": telemetry.runway_heading_magnetic_deg,
        "radio_altitude_ft": telemetry.radio_altitude_ft,
        "elevation_m": telemetry.elevation_m, "agl_m": telemetry.agl_m,
        "pitch_deg": telemetry.pitch_deg, "roll_deg": telemetry.roll_deg,
        "vertical_speed_ms": telemetry.vy_ms, "p_rad": telemetry.p_rad,
        "q_rad": telemetry.q_rad, "r_rad": telemetry.r_rad,
        "accel_long_g": telemetry.accel_long_g, "accel_norm_g": telemetry.accel_norm_g,
        "accel_side_g": telemetry.accel_side_g, "wind_speed_ms": telemetry.wind_speed_ms,
        "wind_dir_from_deg": telemetry.wind_dir_from_deg,
        "runway_length_m": telemetry.runway_length_m,
        "runway_width_m": telemetry.runway_width_m,
        "lateral_deviation_m": telemetry.lateral_deviation_m,
        "lateral_deviation_sign": telemetry.lateral_deviation_sign,
        "ils_valid": telemetry.ils_valid,
        "main_gear_contact": int(bool(telemetry.main_gear_contact)),
        "weight_on_wheels": telemetry.weight_on_wheels,
        "flight_phase": _jsonable(telemetry.flight_phase),
        "agent_active": telemetry.agent_is_active, "faults": faults,
        "weather": telemetry.weather,
        "cmd_elevator_g": state.cmd_elevator, "cmd_aileron_deg": state.cmd_aileron,
        "cmd_throttle_norm": state.cmd_throttle_norm,
        "cmd_throttle_left_rate": state.cmd_throttle_l_rate,
        "cmd_throttle_right_rate": state.cmd_throttle_r_rate,
        "cmd_rudder_norm": state.cmd_rudder, "cmd_pedal_norm": state.cmd_pedal,
        "cmd_tiller_norm": state.cmd_tiller, "cmd_brake_l": state.cmd_brake_l,
        "cmd_brake_r": state.cmd_brake_r, "cmd_reverse_l": state.cmd_rev_l,
        "cmd_reverse_r": state.cmd_rev_r, "break_control": state.break_control,
        "quality_lateral": state.quality_lateral, "quality_heading": state.quality_heading,
        "quality_speed": state.quality_speed,
        "guidance_xte_m": getattr(lateral, "xte", None),
        "guidance_course_error_deg": getattr(lateral, "course_error", None),
        "guidance_heading_error_deg": getattr(lateral, "heading_error", None),
        "guidance_error_deg": getattr(lateral, "guidance_error", None),
        "guidance_along_track_m": getattr(lateral, "along_track", None),
        "guidance_source": getattr(lateral, "source", None),
        "guidance_event": getattr(lateral, "event", None),
        "ground_reference_speed_ms": getattr(longitudinal, "setpoint", None),
        "ground_speed_error_ms": getattr(longitudinal, "error", None),
        "ground_acceleration_ms2": getattr(longitudinal, "acceleration_ms2", None),
        "ground_distance_m": getattr(longitudinal, "distance_m", None),
        "ground_completion_rule": getattr(
            getattr(longitudinal, "completion_rule", None), "value", None),
        "ground_completion_reached": int(bool(getattr(longitudinal, "completion_reached", False))),
        "ground_reverse_allowed": int(bool(getattr(longitudinal, "reverse_allowed", False))),
        "lateral_pid_requested": getattr(lateral, "steering_requested", None),
        "lateral_pid_limited": getattr(lateral, "steering_limited", None),
        "lateral_pid_saturated": int(bool(getattr(lateral, "saturated", False))),
        "allocator_steering_applied": getattr(allocation, "steering_applied", None),
        "allocator_failure_compensation": getattr(allocation, "failure_compensation", None),
        "allocator_saturated": list(allocation.saturated) if allocation is not None else None,
        "approach_tolerances": controller.tolerance_report,
        "approach_criteria_a11": controller.approach_criteria.verdict(),
        "go_around_reason": controller.go_around_reason, "abort_reason": controller.abort_reason,
        "ics_raw_json": ics_inputs.raw_fields if ics_inputs is not None else None,
    }
    if allocation is not None:
        for stage in ("base", "lateral", "requested", "limited"):
            vector = getattr(allocation, stage)
            for name in ACTUATOR_NAMES:
                row[f"allocator_{stage}_{name}"] = getattr(vector, name)
        feedback = allocation.feedback
        row.update({
            "feedback_rudder_deg": feedback.rudder_deg,
            "feedback_nose_wheel_deg": feedback.nose_wheel_deg,
            "feedback_brake_left_mm": feedback.brake_left_mm,
            "feedback_brake_right_mm": feedback.brake_right_mm,
            "feedback_throttle_left_deg": feedback.throttle_left_deg,
            "feedback_throttle_right_deg": feedback.throttle_right_deg,
            "feedback_thrust_left": feedback.thrust_left,
            "feedback_thrust_right": feedback.thrust_right,
            "feedback_longitudinal_accel_g": feedback.longitudinal_accel_g,
            "feedback_lateral_accel_g": feedback.lateral_accel_g,
            "feedback_yaw_rate_rad_s": feedback.yaw_rate_rad_s,
        })
    for name in APPROACH_INPUT_FIELDS:
        row[f"approach_input_{name}"] = (
            getattr(approach_inputs, name, None) if approach_inputs is not None else None)
    for name in APPROACH_RESULT_FIELDS:
        row[f"approach_{name}"] = getattr(approach_result, name)
    for name in ICS_INPUT_FIELDS:
        row[f"ics_{name}"] = getattr(ics_inputs, name) if ics_inputs is not None else None
    for name in ICS_OUTPUT_FIELDS:
        row[f"ics_out_{name}"] = getattr(outputs, name) if outputs is not None else None
    operating_points = pid_operating_points(controller, telemetry)
    for name, pid in controller_pids(controller).items():
        if pid is None:
            continue
        prefix = f"pid_{name}_"
        row.update({
            prefix + "kp": pid.kp, prefix + "ki": pid.ki, prefix + "kd": pid.kd,
            prefix + "value": operating_points[name]["value"],
            prefix + "setpoint": operating_points[name]["setpoint"],
            prefix + "error": pid.last_error, prefix + "output": pid.last_output,
            prefix + "p": pid.last_p_term, prefix + "i": pid.last_i_term,
            prefix + "d": pid.last_d_term, prefix + "integral": pid.integral,
            prefix + "derivative": pid.filtered_derivative,
            prefix + "unconstrained": pid.last_unconstrained,
            prefix + "saturated": int(
                pid.last_unconstrained < pid.min_out or pid.last_unconstrained > pid.max_out),
        })
    return row


class RunRecorder:
    """Append-only writer; ошибка диска помечает прогон, но не выходит в control-loop."""

    def __init__(
        self, *, root: str | Path | None = None, backend: str, aircraft_profile: str,
        scenario, start: str | None = None, extra_metadata: dict | None = None,
        flush_interval_s: float = 1.0, ring_size: int = 2400, clock=time.monotonic,
    ) -> None:
        now = datetime.now(timezone.utc)
        self.execution_id = now.strftime("%Y%m%dT%H%M%S.%fZ")
        self.directory = (Path(root) if root is not None else default_runs_root()) / self.execution_id
        self.started_at = now
        self._clock, self._started_monotonic = clock, clock()
        self._last_flush, self._flush_interval_s = self._started_monotonic, max(0.0, flush_interval_s)
        self._scenario, self._sequence, self._event_sequence = scenario, 0, 0
        self._raw_counts = {"rx": 0, "tx": 0}
        self._started = self._finished = False
        self._lock = RLock()
        self._streams: dict[str, object] = {}
        self._writers: dict[str, csv.DictWriter] = {}
        self._attached_connector = None
        self._last_detected: dict[str, object] = {}
        self.recent_samples: deque[RunSample] = deque(maxlen=max(1, int(ring_size)))
        self.recent_events: deque[RunEvent] = deque(maxlen=max(64, min(2048, int(ring_size))))
        self.recording_failed, self.recording_error = False, None
        self.manifest = {
            "schema_version": SCHEMA_VERSION, "execution_id": self.execution_id,
            "started_at": now.isoformat(), "finished_at": None, "stop_reason": None,
            "backend": backend, "aircraft_profile": aircraft_profile,
            "scenario_id": getattr(scenario, "scenario_id", str(scenario)),
            "scenario": scenario.to_dict() if hasattr(scenario, "to_dict") else str(scenario),
            "matrix_catalog_sha256": CATALOG_SHA256, "matrix_source_sha256": SOURCE_SHA256,
            "matrix_run_ids": {segment.value: run_id for segment, run_id in
                               getattr(scenario, "matrix_runs", {}).items()},
            "matrix_rows": _matrix_rows(scenario),
            "effective_configs": _effective_configs(scenario, aircraft_profile),
            "start": start, "frequency_hz": 1.0 / DT, "units": _units_manifest(),
            "schema": {"sample": "RunSample/v2", "event": "RunEvent/v1",
                       "telemetry_columns": len(TELEMETRY_FIELDS)},
            "git": _git_state(), "recording_failed": False, "recording_error": None,
            "samples": 0, "raw_packets": {"rx": 0, "tx": 0}, **(extra_metadata or {}),
        }
        self.metadata = self.manifest

    def attach_sim(self, sim) -> bool:
        connector = getattr(sim, "connector", None)
        setter = getattr(connector, "set_packet_observer", None)
        if setter is None:
            return False
        try:
            setter(self._observe_packet)
            self._attached_connector = connector
            return True
        except Exception as exc:
            self._fail(exc)
            return False

    def start(self) -> None:
        with self._lock:
            self._ensure_started()

    def _ensure_started(self) -> bool:
        if self._started:
            return not self.recording_failed
        if self.recording_failed:
            return False
        try:
            self.directory.mkdir(parents=True, exist_ok=False)
            (self.directory / "candidates").mkdir()
            self._write_json("manifest.json", self.manifest)
            self._write_json("report.json", {"status": "running", "samples": 0})
            for name in ("telemetry", "approach", "ground"):
                stream = (self.directory / f"{name}.csv").open(
                    "w", newline="", encoding="utf-8", buffering=1)
                writer = csv.DictWriter(stream, fieldnames=TELEMETRY_FIELDS)
                writer.writeheader()
                self._streams[name], self._writers[name] = stream, writer
            self._streams["events"] = (self.directory / "events.jsonl").open(
                "w", encoding="utf-8", buffering=1)
            self._streams["raw-rx"] = (self.directory / "raw-rx.jsonl").open("wb")
            self._streams["raw-tx"] = (self.directory / "raw-tx.jsonl").open("wb")
            self._started = True
            self._append_event_unlocked("run_started", data={"backend": self.manifest["backend"]})
            self._flush(force=True)
            return True
        except Exception as exc:
            self._fail(exc)
            return False

    def record(self, telemetry, controller, *, elapsed_s: float, dt: float | None = None) -> RunSample:
        with self._lock:
            if self._finished:
                raise RuntimeError("прогон уже завершён")
            now = datetime.now(timezone.utc)
            segment = controller.segment.value
            sim = getattr(controller, "sim", None)
            outputs = (getattr(sim, "last_outputs", None)
                       if controller.last_step_send_attempted else None)
            try:
                values = sample_values(telemetry, controller)
            except Exception as exc:
                self._fail(exc)
                values = {"valid": int(bool(getattr(telemetry, "valid", False)))}
            sample = RunSample(
                self.execution_id, int(getattr(controller, "tick_id", self._sequence + 1)),
                self._sequence, now.isoformat(), self._clock() - self._started_monotonic,
                float(elapsed_s), float(dt if dt is not None else controller.last_step_dt),
                str(self.manifest["scenario_id"]), segment,
                int(outputs.ControlMode) if outputs is not None else _mode_for(controller),
                int(outputs.ControlValidMask) if outputs is not None else None,
                bool(controller.last_step_sent), int(getattr(controller, "config_revision", 0)), values,
            )
            self._sequence += 1
            self.recent_samples.append(sample)
            if self._ensure_started():
                try:
                    row = {name: _csv_value(sample.as_row().get(name)) for name in TELEMETRY_FIELDS}
                    self._writers["telemetry"].writerow(row)
                    target = "approach" if segment == FlightSegment.APPROACH.value else "ground"
                    self._writers[target].writerow(row)
                    self._detect_events(sample, telemetry, controller)
                    self._flush()
                except Exception as exc:
                    self._fail(exc)
            return sample

    def record_event(self, event: str, *, data: Mapping[str, object] | None = None,
                     time_s: float | None = None, tick_id: int | None = None,
                     segment: str | None = None) -> RunEvent:
        with self._lock:
            self._ensure_started()
            return self._append_event_unlocked(
                event, data=data, time_s=time_s, tick_id=tick_id, segment=segment)

    def _append_event_unlocked(self, event: str, *, data=None, time_s=None,
                               tick_id=None, segment=None) -> RunEvent:
        item = RunEvent(
            self._event_sequence, datetime.now(timezone.utc).isoformat(),
            self._clock() - self._started_monotonic, time_s, tick_id, event, segment,
            dict(data or {}))
        self._event_sequence += 1
        self.recent_events.append(item)
        stream = self._streams.get("events")
        if stream is not None and not self.recording_failed:
            try:
                stream.write(json.dumps(
                    _jsonable(item.as_dict()), ensure_ascii=False, allow_nan=False) + "\n")
            except Exception as exc:
                self._fail(exc)
        return item

    def _observe_packet(self, direction: str, packet: bytes, address) -> None:
        with self._lock:
            if not self._ensure_started():
                return
            try:
                stream = self._streams[f"raw-{direction}"]
                stream.write(packet)
                if not packet.endswith(b"\n"):
                    stream.write(b"\n")
                self._raw_counts[direction] += 1
                if direction == "tx":
                    payload = json.loads(packet.decode("utf-8"))
                    state = (payload.get("ControlMode"), payload.get("ModeAIReady"),
                             payload.get("ControlValidMask"))
                    if state != self._last_detected.get("wire_state"):
                        self._last_detected["wire_state"] = state
                        self._append_event_unlocked("handshake", data={
                            "control_mode": state[0], "mode_ai_ready": state[1],
                            "control_valid_mask": state[2], "peer": list(address)})
                self._flush()
            except Exception as exc:
                self._fail(exc)

    def _detect_events(self, sample: RunSample, telemetry, controller) -> None:
        current = {
            "segment": sample.segment, "control_mode": sample.control_mode,
            "touchdown": bool(telemetry.main_gear_contact), "valid": bool(telemetry.valid),
            "failures": tuple(sorted(getattr(item, "name", str(item)) for item in telemetry.faults)),
            "config_revision": sample.config_revision,
            "saturation": tuple(sorted(name for name in PID_NAMES
                                       if bool(sample.values.get(f"pid_{name}_saturated")))),
            "fallback": controller.go_around_reason or controller.abort_reason,
        }
        event_names = {"segment": "segment", "control_mode": "control_mode", "valid": "dropout",
                       "failures": "failures", "config_revision": "config_revision",
                       "saturation": "saturation", "fallback": "fallback"}
        for key, event in event_names.items():
            previous, value = self._last_detected.get(key), current[key]
            initial_state = key in {
                "segment", "control_mode", "valid", "failures", "config_revision", "saturation"}
            if previous != value and (previous is not None or initial_state or bool(value)):
                self._append_event_unlocked(
                    event, data={"previous": previous, "value": value}, time_s=sample.time_s,
                    tick_id=sample.tick_id, segment=sample.segment)
        if ("touchdown" in self._last_detected and current["touchdown"]
                and not self._last_detected["touchdown"]):
            self._append_event_unlocked(
                "touchdown", data={"groundspeed_ms": telemetry.groundspeed_ms,
                                   "vertical_speed_ms": telemetry.vy_ms},
                time_s=sample.time_s, tick_id=sample.tick_id, segment=sample.segment)
        self._last_detected.update(current)

    @property
    def sample_count(self) -> int:
        return self._sequence

    def flush(self) -> None:
        with self._lock:
            self._flush(force=True)

    def _flush(self, *, force=False) -> None:
        if not self._started or self.recording_failed:
            return
        now = self._clock()
        if not force and now - self._last_flush < self._flush_interval_s:
            return
        for stream in self._streams.values():
            stream.flush()
        self._last_flush = now

    def export_gains(self, controller, *, label="manual") -> Path:
        with self._lock:
            self._ensure_started()
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
            path = self.directory / "candidates" / f"gains-{stamp}.json"
            payload = {"schema_version": 1, "created_at": datetime.now(timezone.utc).isoformat(),
                       "backend": self.manifest["backend"],
                       "aircraft_profile": self.manifest["aircraft_profile"],
                       "scenario": self.manifest["scenario"], "label": label,
                       "gains": gains_snapshot(controller)}
            try:
                path.write_text(json.dumps(_jsonable(payload), ensure_ascii=False, indent=2,
                                           sort_keys=True), encoding="utf-8")
                self._append_event_unlocked("candidate_exported", data={"path": str(path)})
            except Exception as exc:
                self._fail(exc)
            return path

    def finish(self, report: dict | object | None = None) -> None:
        with self._lock:
            if self._finished:
                return
            self._ensure_started()
            runtime_report = _jsonable(report)
            stop_reason = runtime_report.get("stop_reason") if isinstance(runtime_report, dict) else None
            self._append_event_unlocked(
                "completion", data={"stop_reason": stop_reason, "report": runtime_report})
            try:
                self._flush(force=True)
            except Exception as exc:
                self._fail(exc)
            self._close_streams()
            self.manifest.update({
                "finished_at": datetime.now(timezone.utc).isoformat(), "stop_reason": stop_reason,
                "samples": self._sequence, "raw_packets": dict(self._raw_counts),
                "recording_failed": self.recording_failed, "recording_error": self.recording_error})
            try:
                from ismpu.runtime.run_report import build_run_report
                payload = build_run_report(
                    self.directory, scenario=self._scenario, runtime_report=runtime_report,
                    recording_failed=self.recording_failed, recording_error=self.recording_error)
                self._write_json("report.json", payload)
                self._write_json("manifest.json", self.manifest)
            except Exception as exc:
                self._fail(exc)
                self.manifest.update(recording_failed=True, recording_error=self.recording_error)
                try:
                    self._write_json("manifest.json", self.manifest)
                except Exception:
                    pass
            finally:
                if self._attached_connector is not None:
                    try:
                        self._attached_connector.set_packet_observer(None)
                    except Exception:
                        pass
                self._finished = True

    close = finish

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.finish({"exception": str(exc), "stop_reason": "error"} if exc is not None else None)
        return False

    def _close_streams(self) -> None:
        for stream in self._streams.values():
            try:
                stream.close()
            except Exception:
                pass
        self._streams.clear()
        self._writers.clear()

    def _fail(self, exc: Exception) -> None:
        if not self.recording_failed:
            self.recording_failed = True
            self.recording_error = f"{type(exc).__name__}: {exc}"
            self.manifest.update(recording_failed=True, recording_error=self.recording_error)
        self._close_streams()

    def _write_json(self, name: str, payload) -> None:
        path = self.directory / name
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(json.dumps(_jsonable(payload), ensure_ascii=False, indent=2,
                                        sort_keys=True, allow_nan=False), encoding="utf-8")
        temporary.replace(path)


def _mode_for(controller) -> int:
    if controller.segment is FlightSegment.APPROACH:
        return 2 if controller.landing_committed else 1
    return 4 if controller.segment is FlightSegment.TAXI else 3


def _effective_configs(scenario, aircraft_profile: str) -> dict[str, object]:
    result = {}
    for segment in FlightSegment:
        try:
            result[segment.value] = {
                "control": _jsonable(scenario.control_for(aircraft_profile, segment)),
                "conditions": _jsonable(scenario.conditions_for(segment)),
                "matrix_run_id": getattr(scenario, "matrix_runs", {}).get(segment)}
        except (KeyError, AttributeError):
            continue
    return result


def _matrix_rows(scenario) -> dict[str, object]:
    from ismpu.config.run_matrix import resolve_matrix_run

    return {
        segment.value: _jsonable(resolve_matrix_run(run_id).cells)
        for segment, run_id in getattr(scenario, "matrix_runs", {}).items()
    }


def _git_state() -> dict[str, object]:
    root = Path(__file__).resolve().parents[2]
    try:
        revision = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True,
                                  capture_output=True, text=True).stdout.strip()
        dirty = bool(subprocess.run(["git", "status", "--porcelain"], cwd=root, check=True,
                                    capture_output=True, text=True).stdout.strip())
        return {"revision": revision, "dirty": dirty}
    except (OSError, subprocess.SubprocessError):
        return {"revision": None, "dirty": None}


def _units_manifest() -> dict[str, object]:
    return {
        "normalized": {"time_s": "s", "dt": "s", "lat": "deg", "lon": "deg",
                       "groundspeed_ms": "m/s", "ias_ms": "m/s", "elevation_m": "m",
                       "agl_m": "m", "vertical_speed_ms": "m/s",
                       "lateral_deviation_m": "m", "heading_true_deg": "deg",
                       "pitch_deg": "deg", "roll_deg": "deg"},
        "approach_input_*": "native calibrated law units (kt, ft, ft/min, deg)",
        "ics_*": "raw ICSInputs units from ICSInterface.cs",
        "ics_out_*": "raw ICSOutputs units from Входы_САУ.xlsx",
    }


def _csv_value(value):
    value = _jsonable(value)
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False)
    return value


def _jsonable(value):
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, float):
        return value if value == value and abs(value) != float("inf") else None
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return _jsonable(asdict(value))
    if isinstance(value, Mapping):
        return {str(getattr(key, "value", key)): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list, set, frozenset)):
        return [_jsonable(item) for item in value]
    return str(value)
