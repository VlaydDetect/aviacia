"""Общий offline/live контракт двух SFT-регрессоров коэффициентов PID."""

from __future__ import annotations

import hashlib
import json
import math
from collections import deque
from dataclasses import asdict, dataclass, is_dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from ismpu.agent.pid_gain_regressor import GainGuard, GuardResult, Normalization, PidGainRegressor
from ismpu.config.regulators import GAIN_KEYS
from ismpu.config.run_matrix import SOURCE_SHA256
from ismpu.config.segments import FlightSegment
from ismpu.runtime.run_artifacts import controller_pids, sample_values


CONTROL_MODES = frozenset({"classical", "sft-shadow", "sft-active"})
AIR_PID_NAMES = ("roll", "pitch", "air_speed")
GROUND_PID_NAMES = ("steer", "brake_l", "brake_r", "reverse_l", "reverse_r")
PID_STATE_FIELDS = (
    "value", "setpoint", "error", "output", "p", "i", "d", "integral",
    "derivative", "unconstrained", "saturated",
)

_WEATHER_FEATURES = (
    "weather_wind_speed_kts", "weather_wind_dir_from_degt", "weather_gust_kts",
    "weather_turbulence", "weather_variability_pct", "weather_runway_friction",
    "weather_rain_pct", "weather_visibility_m", "weather_temperature_c",
)
_FAILURE_FEATURES = tuple(f"fault_{name}" for name in (
    "GEAR_CONFIG", "ENGINE_OUT_LEFT", "ENGINE_OUT_RIGHT", "NWS_FAIL",
    "REVERSE_LEFT_FAIL", "REVERSE_RIGHT_FAIL", "THRUST_LEFT_DEGRADED",
    "THRUST_RIGHT_DEGRADED",
)) + ("ics_FaultLeftStab", "ics_FaultRightStab")

AIR_FEATURES = (
    "valid", "ils_valid", "radio_altitude_ft",
    "approach_input_LocDeviation", "approach_input_GSDeviation",
    "approach_loc_dots", "approach_gs_dots", "approach_course_deg",
    "approach_glideslope_deg", "approach_input_IndicatedAirspeed",
    "approach_input_TrueAirspeed", "approach_input_GroundSpeed",
    "approach_input_VerticalSpeed", "ias_ms", "groundspeed_ms", "vertical_speed_ms",
    "pitch_deg", "roll_deg", "heading_true_deg", "heading_magnetic_deg",
    "track_true_deg", "track_magnetic_deg", "p_rad", "q_rad", "r_rad",
    "accel_norm_g", "runway_heading_true_deg", "runway_heading_magnetic_deg",
    "lateral_deviation_m", "runway_length_m", "runway_width_m",
    "approach_target_heading_deg", "approach_heading_error_deg",
    "approach_target_roll_deg", "approach_target_vs_fpm", "approach_target_pitch_deg",
    "approach_flare_armed", "approach_flare_active", "approach_flare_progress",
    "approach_terminal_hold_active", "approach_input_FlapsAngle", "ics_SlatsAngle",
    "ics_NoseGearStatus", "ics_LeftGearStatus", "ics_RightGearStatus",
    "ics_NoseGearWeightOnWheels", "ics_LeftGearWeightOnWheels",
    "ics_RightGearWeightOnWheels", "approach_input_LeftThrottleAngle",
    "approach_input_RightThrottleAngle", "ics_EngLeftThrust", "ics_EngRigntThrust",
    "wind_speed_ms", "wind_dir_from_deg", *_WEATHER_FEATURES, *_FAILURE_FEATURES,
) + tuple(
    f"pid_{pid}_{field}" for pid in AIR_PID_NAMES for field in PID_STATE_FIELDS
)

GROUND_FEATURES = (
    "valid", "time_s", "dt", "lat", "lon", "guidance_xte_m",
    "guidance_course_error_deg", "guidance_heading_error_deg", "guidance_error_deg",
    "guidance_along_track_m", "lateral_deviation_m", "heading_true_deg",
    "heading_magnetic_deg", "track_true_deg", "track_magnetic_deg",
    "runway_heading_true_deg", "runway_heading_magnetic_deg", "groundspeed_ms", "ias_ms",
    "ground_reference_speed_ms", "ground_speed_error_ms", "ground_acceleration_ms2",
    "accel_long_g", "accel_side_g", "r_rad", "feedback_yaw_rate_rad_s",
    "runway_length_m", "runway_width_m", "main_gear_contact", "weight_on_wheels",
    "flight_phase", "ground_distance_m", "ground_reverse_allowed",
    "feedback_rudder_deg", "feedback_nose_wheel_deg", "feedback_brake_left_mm",
    "feedback_brake_right_mm", "feedback_throttle_left_deg",
    "feedback_throttle_right_deg", "feedback_thrust_left", "feedback_thrust_right",
    "feedback_longitudinal_accel_g", "feedback_lateral_accel_g", "cmd_rudder_norm",
    "cmd_pedal_norm", "cmd_tiller_norm", "cmd_brake_l", "cmd_brake_r",
    "cmd_reverse_l", "cmd_reverse_r", "wind_speed_ms", "wind_dir_from_deg",
    *_WEATHER_FEATURES, *_FAILURE_FEATURES,
) + tuple(
    f"pid_{pid}_{field}" for pid in GROUND_PID_NAMES for field in PID_STATE_FIELDS
)

FEATURES = {"air": AIR_FEATURES, "ground": GROUND_FEATURES}
PID_NAMES = {"air": AIR_PID_NAMES, "ground": GROUND_PID_NAMES}
GAIN_LAYOUT = {
    segment: tuple(f"{pid}:{gain}" for pid in names for gain in GAIN_KEYS)
    for segment, names in PID_NAMES.items()
}

if any(name.endswith(("_kp", "_ki", "_kd")) for names in FEATURES.values() for name in names):
    raise RuntimeError("current kp/ki/kd must not enter SFT features")


def feature_vector(row: Mapping[str, Any], segment: str) -> np.ndarray:
    """CSV/live row → один кадр схемы сегмента; отсутствующие backend-поля равны нулю."""
    try:
        names = FEATURES[segment]
    except KeyError as exc:
        raise ValueError("segment must be 'air' or 'ground'") from exc
    return np.asarray([_feature_value(row, name) for name in names], dtype=np.float32)


def gain_vector_from_row(row: Mapping[str, Any], segment: str) -> np.ndarray:
    """Цель SFT — фактически записанные kp/ki/kd последнего кадра окна."""
    values = []
    for pid in PID_NAMES[segment]:
        for gain in GAIN_KEYS:
            value = row.get(f"pid_{pid}_{gain}")
            number = _number(value, default=math.nan)
            if not math.isfinite(number):
                raise ValueError(f"missing applied gain pid_{pid}_{gain}")
            values.append(number)
    return np.asarray(values, dtype=np.float64)


def controller_gain_vector(controller, segment: str) -> np.ndarray:
    pids = controller_pids(controller)
    return np.asarray([
        getattr(pids[name], gain)
        for name in PID_NAMES[segment] for gain in GAIN_KEYS
    ], dtype=np.float64)


def apply_gain_vector(controller, segment: str, gains: Sequence[float]) -> None:
    """Единственная runtime-запись сети: bumpless kp/ki/kd, никаких actuator outputs."""
    values = np.asarray(gains, dtype=np.float64).reshape(-1)
    if values.shape != (len(GAIN_LAYOUT[segment]),) or not np.isfinite(values).all():
        raise ValueError("invalid SFT gain vector")
    pids = controller_pids(controller)
    index = 0
    for name in PID_NAMES[segment]:
        triplet = values[index:index + len(GAIN_KEYS)]
        index += len(GAIN_KEYS)
        pid = pids[name]
        current = np.asarray([pid.kp, pid.ki, pid.kd], dtype=np.float64)
        if not np.array_equal(current, triplet):
            pid.set_gains_bumpless(**dict(zip(GAIN_KEYS, triplet)))


def checkpoint_metadata(path: str | Path, payload: Mapping[str, Any]) -> dict[str, Any]:
    target = Path(path)
    with target.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    return {
        "path": str(target), "sha256": digest, "segment": payload["segment"],
        "feature_schema_hash": payload["feature_schema_hash"],
        "matrix_hash": payload["matrix_hash"],
        "aircraft_profile": payload["aircraft_profile"],
        "run_ids": list(payload["run_ids"]),
        "metrics": payload["metrics"], "activation": payload.get("activation", {}),
    }


@dataclass
class _SegmentRuntime:
    model: PidGainRegressor
    checkpoint: dict[str, Any]
    feature_norm: Normalization
    target_norm: Normalization
    guard: GainGuard
    window: deque
    context: tuple[str, int] | None = None
    preset: np.ndarray | None = None
    current: np.ndarray | None = None
    pending: np.ndarray | None = None
    pending_ood: bool = False
    pending_error: str | None = None
    prediction_count: int = 0

    @classmethod
    def build(cls, model: PidGainRegressor, checkpoint: dict[str, Any]) -> "_SegmentRuntime":
        normalization = checkpoint["normalization"]
        bounds = checkpoint["physical_bounds"]
        return cls(
            model=model, checkpoint=checkpoint,
            feature_norm=Normalization.from_snapshot(normalization["features"]),
            target_norm=Normalization.from_snapshot(normalization["targets"]),
            guard=GainGuard(bounds["low"], bounds["high"]),
            window=deque(maxlen=int(checkpoint["window_frames"])),
        )

    def reset(self, key: tuple[str, int], preset: np.ndarray) -> None:
        self.context = key
        self.preset = preset.copy()
        self.current = preset.copy()
        self.pending = None
        self.pending_ood = False
        self.pending_error = None
        self.window.clear()


class SftRuntime:
    """Два независимых оконных inference-контура вокруг классических PID."""

    def __init__(
        self, mode: str = "classical", *,
        air: _SegmentRuntime | None = None,
        ground: _SegmentRuntime | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        if mode not in CONTROL_MODES:
            raise ValueError(f"unknown control mode: {mode}")
        if mode != "classical" and air is None and ground is None:
            raise ValueError(f"{mode} requires at least one SFT checkpoint")
        self.mode = mode
        self.models = {"air": air, "ground": ground}
        self.metadata = dict(metadata or {})
        self.elapsed_s = 0.0
        self.last_result: GuardResult | None = None

    @classmethod
    def from_checkpoints(
        cls,
        *,
        mode: str,
        air_path: str | Path | None = None,
        ground_path: str | Path | None = None,
        backend: str = "xplane",
        aircraft_profile: str | None = None,
    ) -> "SftRuntime":
        if mode == "classical":
            if air_path is not None or ground_path is not None:
                raise ValueError("SFT checkpoints require sft-shadow or sft-active")
            return cls(mode)
        slots: dict[str, _SegmentRuntime | None] = {"air": None, "ground": None}
        metadata: dict[str, Any] = {}
        for segment, path in (("air", air_path), ("ground", ground_path)):
            if path is None:
                continue
            model, checkpoint = PidGainRegressor.load_checkpoint(
                path,
                expected_segment=segment,
                expected_features=FEATURES[segment],
                expected_gain_layout=GAIN_LAYOUT[segment],
                expected_matrix_hash=SOURCE_SHA256,
                expected_aircraft_profile=aircraft_profile,
                require_gate=True,
                require_ics_activation=(backend == "ics" and mode == "sft-active"),
            )
            slots[segment] = _SegmentRuntime.build(model, checkpoint)
            metadata[segment] = checkpoint_metadata(path, checkpoint)
        return cls(mode, air=slots["air"], ground=slots["ground"], metadata=metadata)

    def before_step(self, controller, telemetry, dt: float) -> GuardResult | None:
        """Применить prediction прошлого кадра перед очередным классическим PID-тактом."""
        if self.mode == "classical":
            return None
        segment = _runtime_segment(controller)
        slot = self.models[segment]
        if slot is None:
            self._diagnostics(controller, segment, reason="model_disabled")
            return None
        self._ensure_context(slot, controller, segment)
        telemetry_valid = bool(telemetry is not None and getattr(telemetry, "valid", False))
        go_around = segment == "air" and controller.go_around is not None
        result = slot.guard.guard(
            slot.pending, slot.preset, slot.current, dt,
            window_ready=len(slot.window) == slot.window.maxlen and slot.pending is not None,
            telemetry_valid=telemetry_valid,
            ood=slot.pending_ood,
            model_error="go_around_static" if go_around else slot.pending_error,
        )
        self.last_result = result
        if self.mode == "sft-active":
            apply_gain_vector(controller, segment, result.gains)
        slot.current = result.gains.copy()
        self._diagnostics(
            controller, segment, guard=result,
            prediction=slot.pending, ready=len(slot.window) == slot.window.maxlen,
            predictions=slot.prediction_count,
        )
        return result

    def after_step(self, controller, telemetry, dt: float) -> np.ndarray | None:
        """Добавить завершённый кадр и подготовить prediction для следующего такта."""
        if self.mode == "classical":
            return None
        self.elapsed_s += max(0.0, float(dt))
        segment = _runtime_segment(controller)
        slot = self.models[segment]
        if slot is None:
            self._diagnostics(controller, segment, reason="model_disabled")
            return None
        self._ensure_context(slot, controller, segment)
        if segment == "air" and controller.go_around is not None:
            slot.window.clear()
            slot.pending = None
            self._diagnostics(controller, segment, reason="go_around_static")
            return None
        if telemetry is None or not getattr(telemetry, "valid", False):
            slot.window.clear()
            slot.pending = None
            slot.pending_error = None
            slot.pending_ood = False
            self._diagnostics(controller, segment, reason="telemetry_dropout")
            return None
        row = sample_values(telemetry, controller)
        row.update({"time_s": self.elapsed_s, "dt": float(dt)})
        slot.window.append(feature_vector(row, segment))
        if len(slot.window) < slot.window.maxlen:
            slot.pending = None
            self._diagnostics(
                controller, segment, reason="window_incomplete", ready=False,
                window_frames=len(slot.window),
            )
            return None
        try:
            prediction, ood = slot.model.predict(
                np.stack(slot.window), slot.feature_norm, slot.target_norm)
            slot.pending = prediction
            slot.pending_ood = ood
            slot.pending_error = None
            slot.prediction_count += 1
            self._diagnostics(
                controller, segment, prediction=prediction, ready=True,
                reason="feature_ood" if ood else None,
                predictions=slot.prediction_count,
            )
            return prediction
        except Exception as exc:
            slot.pending = None
            slot.pending_ood = False
            slot.pending_error = f"{type(exc).__name__}:{exc}"
            self._diagnostics(controller, segment, reason=f"model_error:{slot.pending_error}")
            return None

    def _ensure_context(self, slot: _SegmentRuntime, controller, segment: str) -> None:
        key = (segment, int(getattr(controller, "config_revision", 0)))
        if slot.context != key:
            slot.reset(key, controller_gain_vector(controller, segment))

    def _diagnostics(
        self, controller, segment: str, *, guard: GuardResult | None = None,
        prediction: np.ndarray | None = None, ready: bool | None = None,
        reason: str | None = None, predictions: int | None = None,
        window_frames: int | None = None,
    ) -> None:
        previous = getattr(controller, "sft_diagnostics", {})
        data = dict(previous) if previous.get("segment") == segment else {}
        data.update({"mode": self.mode, "segment": segment})
        if ready is not None:
            data["window_ready"] = ready
        if window_frames is not None:
            data["window_frames"] = window_frames
        if prediction is not None:
            data["prediction"] = prediction.tolist()
        if predictions is not None:
            data["prediction_count"] = predictions
        if guard is not None:
            data.update({
                "guarded": guard.gains.tolist(),
                "applied": (
                    guard.gains.tolist() if self.mode == "sft-active"
                    else controller_gain_vector(controller, segment).tolist()),
                "fallback": guard.fallback,
                "rate_limited": guard.rate_limited,
            })
            reason = guard.reason
        data["reason"] = reason
        controller.sft_diagnostics = data


def _runtime_segment(controller) -> str:
    return "air" if controller.segment is FlightSegment.APPROACH else "ground"


def _feature_value(row: Mapping[str, Any], name: str) -> float:
    if name.startswith("fault_"):
        failure_name = name.removeprefix("fault_")
        failures = row.get("faults") or ()
        if isinstance(failures, str):
            try:
                failures = json.loads(failures)
            except json.JSONDecodeError:
                failures = (failures,)
        return float(any(getattr(item, "name", str(item)) == failure_name for item in failures))
    if name.startswith("weather_"):
        key = name.removeprefix("weather_")
        weather = row.get("weather")
        if is_dataclass(weather):
            weather = asdict(weather)
        value = weather.get(key) if isinstance(weather, Mapping) else None
        return _number(value)
    return _number(row.get(name))


def _number(value: Any, default: float = 0.0) -> float:
    if isinstance(value, Enum):
        value = value.value
    if isinstance(value, bool):
        return float(value)
    try:
        result = float(value)
        return result if math.isfinite(result) else default
    except (TypeError, ValueError):
        return default
