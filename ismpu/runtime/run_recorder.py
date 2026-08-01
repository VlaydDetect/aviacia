"""Единый CSV-регистратор прогонов ICS и X-Plane."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from threading import RLock


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
)
PID_TELEMETRY_FIELDS = (
    "kp", "ki", "kd", "value", "setpoint", "error", "output",
    "p", "i", "d", "saturated",
)
TELEMETRY_FIELDS = BASE_TELEMETRY_FIELDS + tuple(
    f"pid_{name}_{field}"
    for name in PID_NAMES
    for field in PID_TELEMETRY_FIELDS
)


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
        "steer": ground["runway_center_pid"],
        "brake_l": ground["pid_brake_l"],
        "brake_r": ground["pid_brake_r"],
        "reverse_l": ground["pid_rev_l"],
        "reverse_r": ground["pid_rev_r"],
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
                      "last_diagnostics", {})
    longitudinal = getattr(getattr(controller, "longitudinal_channel", None),
                           "last_diagnostics", {})
    speed_pair = {
        "value": longitudinal.get("value"),
        "setpoint": longitudinal.get("setpoint"),
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
            "value": lateral.get("value"),
            "setpoint": lateral.get("setpoint"),
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
        self.directory = (Path(root) if root is not None else default_runs_root()) / label
        self.started_at = now
        self._rows: list[dict] = []
        self._sequence = 0
        self._materialized = False
        self._finished = False
        self._lock = RLock()
        self.metadata = {
            "schema_version": 1,
            "started_at": now.isoformat(),
            "backend": backend,
            "aircraft_profile": aircraft_profile,
            "scenario": scenario.to_dict() if hasattr(scenario, "to_dict") else str(scenario),
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
                "cmd_rudder_norm": state.rudder_cmd,
                "cmd_brake_l": state.cmd_brake_l,
                "cmd_brake_r": state.cmd_brake_r,
                "cmd_reverse_l": state.cmd_rev_l,
                "cmd_reverse_r": state.cmd_rev_r,
                "quality_lateral": state.quality_lateral,
                "quality_heading": state.quality_heading,
                "quality_speed": state.quality_speed,
                "loc_deviation": getattr(approach, "LocDeviation", None),
                "gs_deviation": getattr(approach, "GSDeviation", None),
                "magnetic_track_deg": getattr(approach, "TrkAngleMagnetic", None),
                "vertical_speed_fpm": getattr(approach, "VerticalSpeed", None),
            }
            operating_points = pid_operating_points(controller)
            for name, pid in controller_pids(controller).items():
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
