"""Единый CSV-регистратор прогонов ICS и X-Plane."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, fields, is_dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from threading import RLock

from ismpu.config.run_matrix import CATALOG_SHA256, SOURCE_SHA256
from ismpu.io.ics_connector import ICSInputs


PID_NAMES = (
    "roll", "pitch", "air_speed", "steer",
    "brake_l", "brake_r", "reverse_l", "reverse_r",
)

BASE_TELEMETRY_FIELDS = (
    "sequence",
    "time_s",
    "segment",
    "valid",
    "lat",
    "lon",
    "groundspeed_ms",
    "heading_true_deg",
    "radio_altitude_ft",
    "ias_ms",
    "pitch_deg",
    "roll_deg",
    "vertical_speed_ms",
    "lateral_deviation_m",
    "ils_valid",
    "main_gear_contact",
    "agent_active",
    "cmd_elevator_g",
    "cmd_aileron_deg",
    "cmd_throttle_norm",
    "cmd_rudder_norm",
    "cmd_pedal_norm",
    "cmd_tiller_norm",
    "cmd_brake_l",
    "cmd_brake_r",
    "cmd_reverse_l",
    "cmd_reverse_r",
    "quality_lateral",
    "quality_heading",
    "quality_speed",
    "loc_deviation",
    "gs_deviation",
    "magnetic_track_deg",
    "vertical_speed_fpm",
    "guidance_xte_m",
    "guidance_course_error_deg",
    "guidance_heading_error_deg",
    "guidance_error_deg",
    "guidance_along_track_m",
    "guidance_source",
    "guidance_event",
    "ground_reference_speed_ms",
    "ground_speed_error_ms",
    "ground_acceleration_ms2",
    "ground_distance_m",
    "ground_completion_rule",
    "ground_completion_reached",
    "ground_reverse_allowed",
    "lateral_pid_requested",
    "lateral_pid_limited",
    "lateral_pid_saturated",
    "allocator_steering_applied",
    "allocator_failure_compensation",
    "allocator_saturated",
    "ics_raw_json",
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
ICS_INPUT_FIELDS = tuple(field.name for field in fields(ICSInputs))
ICS_TELEMETRY_FIELDS = tuple(f"ics_{name}" for name in ICS_INPUT_FIELDS)
PID_TELEMETRY_FIELDS = (
    "kp", "ki", "kd", "value", "setpoint", "error", "output",
    "p", "i", "d", "integral", "derivative", "unconstrained", "saturated",
)
TELEMETRY_FIELDS = (
    BASE_TELEMETRY_FIELDS + ALLOCATOR_TELEMETRY_FIELDS + ACTUATOR_FEEDBACK_FIELDS
    + ICS_TELEMETRY_FIELDS + tuple(
    f"pid_{name}_{field}"
    for name in PID_NAMES
    for field in PID_TELEMETRY_FIELDS
))


def default_runs_root() -> Path:
    """Единый каталог прогонов, не зависящий от cwd процесса/Jupyter."""
    return Path(__file__).resolve().parents[2] / "runs"


def controller_pids(controller) -> dict:
    approach = controller.approach_channel
    ground = controller.pids
    return {
        "roll": approach.roll_pid,
        "pitch": approach.pitch_pid,
        "air_speed": approach.speed_pid,
        "steer": ground.get("runway_center_pid", None),
        "brake_l": ground.get("pid_brake_l", None),
        "brake_r": ground.get("pid_brake_r", None),
        "reverse_l": ground.get("pid_rev_l", None),
        "reverse_r": ground.get("pid_rev_r", None),
    }


def gains_snapshot(controller) -> dict:
    return {
        name: {"kp": pid.kp, "ki": pid.ki, "kd": pid.kd}
        for name, pid in controller_pids(controller).items()
    }


def pid_operating_points(controller) -> dict:
    """Value/setpoint pairs in the native units used by every regulator."""
    result = controller.approach_channel.result
    telemetry = controller.last_telemetry
    airborne = getattr(telemetry, "approach_inputs", None)
    lateral = getattr(getattr(controller, "lateral_channel", None),
                      "last_diagnostics", None)
    longitudinal = getattr(getattr(controller, "longitudinal_channel", None),
                           "last_diagnostics", None)
    speed_pair = {
        "value": getattr(longitudinal, "value", None),
        "setpoint": getattr(longitudinal, "setpoint", None),
    }
    return {
        "roll": {
            "value": getattr(airborne, "RollAngle", None),
            "setpoint": result.target_roll_deg,
        },
        "pitch": {
            "value": getattr(airborne, "PitchAngle", None),
            "setpoint": result.target_pitch_deg,
        },
        "air_speed": {
            "value": getattr(airborne, "IndicatedAirspeed", None),
            "setpoint": result.target_ias_kt,
        },
        "steer": {
            "value": getattr(lateral, "value", None),
            "setpoint": getattr(lateral, "setpoint", None),
        },
        "brake_l": dict(speed_pair),
        "brake_r": dict(speed_pair),
        "reverse_l": dict(speed_pair),
        "reverse_r": dict(speed_pair),
    }


class RunRecorder:
    def __init__(
        self,
        *,
        root: str | Path | None = None,
        backend: str,
        aircraft_profile: str,
        scenario,
        start: str | None = None,
        extra_metadata: dict | None = None,
    ) -> None:
        now = datetime.now(timezone.utc)
        label = now.strftime("%Y%m%dT%H%M%S.%fZ")
        self.execution_id = label
        self.directory = (Path(root) if root is not None else default_runs_root()) / label
        self.started_at = now
        self._rows: list[dict] = []
        self._sequence = 0
        self._materialized = False
        self._finished = False
        self._lock = RLock()
        self.metadata = {
            "schema_version": 1,
            "execution_id": self.execution_id,
            "started_at": now.isoformat(),
            "backend": backend,
            "aircraft_profile": aircraft_profile,
            "scenario": scenario.to_dict() if hasattr(scenario, "to_dict") else str(scenario),
            "matrix_catalog_sha256": CATALOG_SHA256,
            "matrix_source_sha256": SOURCE_SHA256,
            "matrix_run_ids": {
                segment.value: run_id
                for segment, run_id in getattr(scenario, "matrix_runs", {}).items()
            },
            "start": start,
            **(extra_metadata or {}),
        }

    def record(self, telemetry, controller, *, elapsed_s: float) -> None:
        """Зафиксировать снимок кадра в памяти без файлового I/O."""
        with self._lock:
            if self._finished:
                raise RuntimeError("прогон уже завершён")
            state = controller.state
            approach = getattr(telemetry, "approach_inputs", None)
            lateral = getattr(
                getattr(controller, "lateral_channel", None), "last_diagnostics", None)
            longitudinal = getattr(
                getattr(controller, "longitudinal_channel", None), "last_diagnostics", None)
            allocation = getattr(
                getattr(controller, "ground_allocator", None), "last_diagnostics", None)
            ics_inputs = getattr(telemetry, "ics_inputs", None)
            row = {
                "sequence": self._sequence,
                "time_s": elapsed_s,
                "segment": controller.segment.value,
                "valid": int(bool(telemetry.valid)),
                "lat": telemetry.lat,
                "lon": telemetry.lon,
                "groundspeed_ms": telemetry.groundspeed_ms,
                "heading_true_deg": telemetry.heading_true_deg,
                "radio_altitude_ft": telemetry.radio_altitude_ft,
                "ias_ms": telemetry.ias_ms,
                "pitch_deg": telemetry.pitch_deg,
                "roll_deg": telemetry.roll_deg,
                "vertical_speed_ms": telemetry.vy_ms,
                "lateral_deviation_m": telemetry.lateral_deviation_m,
                "ils_valid": telemetry.ils_valid,
                "main_gear_contact": int(bool(telemetry.main_gear_contact)),
                "agent_active": int(bool(telemetry.agent_is_active)),
                "cmd_elevator_g": state.cmd_elevator,
                "cmd_aileron_deg": state.cmd_aileron,
                "cmd_throttle_norm": state.cmd_throttle_norm,
                "cmd_rudder_norm": state.cmd_rudder,
                "cmd_pedal_norm": state.cmd_pedal,
                "cmd_tiller_norm": state.cmd_tiller,
                "cmd_brake_l": state.cmd_brake_l,
                "cmd_brake_r": state.cmd_brake_r,
                "cmd_reverse_l": state.cmd_rev_l,
                "cmd_reverse_r": state.cmd_rev_r,
                "quality_lateral": state.quality_lateral,
                "quality_heading": state.quality_heading,
                "quality_speed": state.quality_speed,
                "loc_deviation": getattr(approach, "LocDeviation", None),
                "gs_deviation": getattr(approach, "GSDeviation", None),
                "magnetic_track_deg": telemetry.track_magnetic_deg,
                "vertical_speed_fpm": getattr(approach, "VerticalSpeed", None),
                "guidance_xte_m": getattr(lateral, "xte", None),
                "guidance_course_error_deg": getattr(lateral, "course_error", None),
                "guidance_heading_error_deg": getattr(lateral, "heading_error", None),
                "guidance_error_deg": getattr(lateral, "guidance_error", None),
                "guidance_along_track_m": getattr(lateral, "along_track", None),
                "guidance_source": getattr(lateral, "source", None),
                "guidance_event": getattr(lateral, "event", None),
                "ground_reference_speed_ms": getattr(longitudinal, "setpoint", None),
                "ground_speed_error_ms": getattr(longitudinal, "error", None),
                "ground_acceleration_ms2": getattr(
                    longitudinal, "acceleration_ms2", None),
                "ground_distance_m": getattr(longitudinal, "distance_m", None),
                "ground_completion_rule": getattr(
                    getattr(longitudinal, "completion_rule", None), "value", None),
                "ground_completion_reached": int(bool(getattr(
                    longitudinal, "completion_reached", False))),
                "ground_reverse_allowed": int(bool(getattr(
                    longitudinal, "reverse_allowed", False))),
                "lateral_pid_requested": getattr(lateral, "steering_requested", None),
                "lateral_pid_limited": getattr(lateral, "steering_limited", None),
                "lateral_pid_saturated": int(bool(getattr(lateral, "saturated", False))),
                "allocator_steering_applied": getattr(
                    allocation, "steering_applied", None),
                "allocator_failure_compensation": getattr(
                    allocation, "failure_compensation", None),
                "allocator_saturated": (
                    ";".join(allocation.saturated) if allocation is not None else None),
                # Один JSON-столбец сохраняет имена будущих полей без изменения CSV-схемы
                # посреди прогона и без превращения внешних имён в заголовки CSV.
                "ics_raw_json": (
                    json.dumps(ics_inputs.raw_fields, ensure_ascii=False, sort_keys=True)
                    if ics_inputs is not None else None),
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
            for name in ICS_INPUT_FIELDS:
                row[f"ics_{name}"] = (
                    _jsonable(getattr(ics_inputs, name)) if ics_inputs is not None else None)
            operating_points = pid_operating_points(controller)
            for name, pid in controller_pids(controller).items():
                if pid:
                    prefix = f"pid_{name}_"
                    row.update({
                        prefix + "kp": pid.kp,
                        prefix + "ki": pid.ki,
                        prefix + "kd": pid.kd,
                        prefix + "value": operating_points[name]["value"],
                        prefix + "setpoint": operating_points[name]["setpoint"],
                        prefix + "error": pid.last_error,
                        prefix + "output": pid.last_output,
                        prefix + "p": pid.last_p_term,
                        prefix + "i": pid.last_i_term,
                        prefix + "d": pid.last_d_term,
                        prefix + "integral": pid.integral,
                        prefix + "derivative": pid.filtered_derivative,
                        prefix + "unconstrained": pid.last_unconstrained,
                        prefix + "saturated": int(
                            pid.last_unconstrained < pid.min_out
                            or pid.last_unconstrained > pid.max_out),
                    })
            self._rows.append(row)
            self._sequence += 1

    @property
    def sample_count(self) -> int:
        with self._lock:
            return self._sequence

    def export_gains(self, controller, *, label: str = "manual") -> Path:
        with self._lock:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
            payload = {
                "schema_version": 1,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "backend": self.metadata["backend"],
                "aircraft_profile": self.metadata["aircraft_profile"],
                "scenario": self.metadata["scenario"],
                "label": label,
                "gains": gains_snapshot(controller),
            }
            path = self.directory / f"gains-{timestamp}.json"
            self._write_json(path.name, payload)
            return path

    def finish(self, report: dict | object | None = None) -> None:
        """Один раз сохранить накопленные кадры и итоговые артефакты прогона."""
        with self._lock:
            if self._finished:
                return
            self._ensure_directory()
            self._write_json("metadata.json", self.metadata)
            with (self.directory / "telemetry.csv").open(
                "w", newline="", encoding="utf-8"
            ) as stream:
                writer = csv.DictWriter(stream, fieldnames=TELEMETRY_FIELDS)
                writer.writeheader()
                writer.writerows(self._rows)
            payload = {
                "finished_at": datetime.now(timezone.utc).isoformat(),
                "samples": self._sequence,
                "report": _jsonable(report),
            }
            self._write_json("report.json", payload)
            self._finished = True

    close = finish

    def __enter__(self) -> "RunRecorder":
        return self

    def __exit__(self, exc_type, exc, traceback) -> bool:
        self.finish({"exception": str(exc)} if exc is not None else None)
        return False

    def _ensure_directory(self) -> None:
        if self._materialized:
            return
        self.directory.mkdir(parents=True, exist_ok=False)
        self._materialized = True

    def _write_json(self, name: str, payload: dict) -> None:
        self._ensure_directory()
        (self.directory / name).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )


def _jsonable(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if is_dataclass(value):
        return _jsonable(asdict(value))
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list, set, frozenset)):
        return [_jsonable(item) for item in value]
    return str(value)
