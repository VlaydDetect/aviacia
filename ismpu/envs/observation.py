"""Observation Space — сборка и нормировка вектора состояния (§5).

Собирает один кадр из телеметрии (`Telemetry`), состояния классического контура
(`ControllingSystem`: guidance, эталонная скорость, последние команды, внутреннее
состояние PID×5) и погоды сценария. Плюс **зарезервированные слоты обсервера** (§12,
Этап 7) — сейчас заполняются нулями через `ObserverEstimate`.

Нормировка — фиксированными константами из `agent.normalization` (единый контракт
train↔deploy). Порядок признаков задан `FEATURE_NAMES`; `build(...)` возвращает
`np.ndarray(OBS_DIM,)` в этом порядке. Окно истории собирает `rollout_env`.
"""

from dataclasses import dataclass

import numpy as np

from ismpu.agent.normalization import (
    XTE_SCALE, HEADING_SCALE, LOOKAHEAD_SCALE, SPEED_SCALE, SPEED_ERR_SCALE, ACCEL_SCALE,
    WIND_SCALE, FRICTION_SCALE, VIS_SCALE, DERIV_SCALE,
    linear, log_norm, gain_ratio, symmetric, clip_unit,
)
from ismpu.agent.shield import REGULATOR_ORDER
from ismpu.utils.converts import Converts
from ismpu.control.runway_tracker import RunwayTracker
from ismpu.config.runway import RWY_START_LAT, RWY_START_LON, RWY_END_LAT, RWY_END_LON
from ismpu.envs.weather import decompose_wind

_G = 9.80665  # ускорение свободного падения (перегрузка g → м/с²)


@dataclass
class ObserverEstimate:
    """Оценки PINN-обсервера (§12). Заглушка нулями до Этапа 7."""
    mu_hat: float = 0.0            # коэффициент сцепления
    wind_cross_hat: float = 0.0    # боковой ветер, норм.
    brake_eff: float = 0.0         # эффективность торможения
    nws_eff: float = 0.0           # эффективность руления
    tau_delay: float = 0.0         # задержка динамики

    def to_vector(self) -> list:
        return [self.mu_hat, self.wind_cross_hat, self.brake_eff, self.nws_eff, self.tau_delay]


# --- Порядок признаков (единый контракт; используется в тестах и интерпретации) ---
_GEOMETRY = ["xte", "heading_error", "distance_to_end", "lookahead"]
_SPEED = ["ground_speed", "reference_speed", "speed_error", "long_accel"]
_CONTROLS = ["brake_l", "brake_r", "reverse_l", "reverse_r", "rudder"]
_PID = [f"{reg}:{f}" for reg in REGULATOR_ORDER for f in ("kp", "ki", "kd", "integral", "deriv", "output")]
_FAILURES = ["nws_fault", "reverse_l_fault", "reverse_r_fault"]
_WEATHER = ["wind_along", "wind_cross", "friction", "rain", "visibility"]
_OBSERVER = ["mu_hat", "wind_cross_hat", "brake_eff", "nws_eff", "tau_delay"]

FEATURE_NAMES = _GEOMETRY + _SPEED + _CONTROLS + _PID + _FAILURES + _WEATHER + _OBSERVER
OBS_DIM = len(FEATURE_NAMES)  # 4 + 4 + 5 + 30 + 3 + 5 + 5 = 56


class ObservationBuilder:
    """Строит нормированный вектор наблюдения одного кадра."""

    def __init__(self, runway_length_m: float | None = None):
        tracker = RunwayTracker()
        self.runway_length_m = runway_length_m or tracker.haversine_distance(
            RWY_START_LAT, RWY_START_LON, RWY_END_LAT, RWY_END_LON)

    def build(self, telemetry, controller, base_gains, weather, observer: ObserverEstimate | None = None) -> np.ndarray:
        """Собирает нормированный кадр. При невалидной телеметрии — нулевой вектор."""
        if not telemetry.valid or None in (telemetry.lat, telemetry.lon,
                                           telemetry.heading_true_deg, telemetry.groundspeed_ms):
            return np.zeros(OBS_DIM, dtype=np.float32)

        feats: dict[str, float] = {}

        # --- Геометрия (guidance пересчитывается по текущей телеметрии) ---
        lon_ch = controller.longitudinal_channel
        lat_ch = controller.lateral_channel
        g = lat_ch.tracker.guidance(telemetry.lat, telemetry.lon,
                                    telemetry.heading_true_deg, telemetry.groundspeed_ms)
        feats["xte"] = clip_unit(linear(g["xte"], XTE_SCALE))
        feats["heading_error"] = clip_unit(linear(g["heading_error_deg"], HEADING_SCALE))
        feats["distance_to_end"] = clip_unit(linear(self.runway_length_m - g["along"], self.runway_length_m))
        feats["lookahead"] = clip_unit(linear(g["lookahead"], LOOKAHEAD_SCALE))

        # --- Скорость ---
        gs = telemetry.groundspeed_ms
        ref = lon_ch.trajectory.get_reference_speed(lon_ch.traveled_distance_m)
        accel = (telemetry.accel_long_g or 0.0) * _G
        feats["ground_speed"] = clip_unit(linear(gs, SPEED_SCALE))
        feats["reference_speed"] = clip_unit(linear(ref, SPEED_SCALE))
        feats["speed_error"] = clip_unit(linear(gs - ref, SPEED_ERR_SCALE))
        feats["long_accel"] = clip_unit(linear(accel, ACCEL_SCALE))

        # --- Управление (последнее применённое) ---
        st = controller.state
        feats["brake_l"] = clip_unit(st.cmd_brake_l)
        feats["brake_r"] = clip_unit(st.cmd_brake_r)
        feats["reverse_l"] = clip_unit(-st.cmd_rev_l)   # реверс [-1,0] → магнитуда [0,1]
        feats["reverse_r"] = clip_unit(-st.cmd_rev_r)
        feats["rudder"] = clip_unit(st.rudder_cmd)

        # --- PID × 5 (динамические признаки) ---
        for reg in REGULATOR_ORDER:
            pid = controller.pids[reg]
            b = base_gains[reg]
            feats[f"{reg}:kp"] = gain_ratio(pid.kp, b["kp"])
            feats[f"{reg}:ki"] = gain_ratio(pid.ki, b["ki"])
            feats[f"{reg}:kd"] = gain_ratio(pid.kd, b["kd"])
            aw = pid.anti_windup or 1.0
            feats[f"{reg}:integral"] = clip_unit(pid.integral / aw)
            feats[f"{reg}:deriv"] = clip_unit(pid.filtered_derivative / DERIV_SCALE)
            feats[f"{reg}:output"] = symmetric(pid.last_output, pid.min_out, pid.max_out)

        # --- Отказы (эффективности из FailureState) ---
        fs = controller.failures.state
        feats["nws_fault"] = 1.0 - fs.steering_eff
        feats["reverse_l_fault"] = 1.0 - fs.reverse_left_eff
        feats["reverse_r_fault"] = 1.0 - fs.reverse_right_eff

        # --- Погода ---
        wind_ms = weather.wind_speed_kts * Converts.KTS_TO_MS
        cross, head = decompose_wind(wind_ms, weather.wind_dir_from_degt, telemetry.heading_true_deg)
        friction = (weather.friction_profile.at(lon_ch.traveled_distance_m)
                    if weather.friction_profile else weather.runway_friction)
        feats["wind_along"] = clip_unit(linear(head, WIND_SCALE))
        feats["wind_cross"] = clip_unit(linear(cross, WIND_SCALE))
        feats["friction"] = clip_unit(linear(friction, FRICTION_SCALE))
        feats["rain"] = clip_unit(weather.rain_pct)
        feats["visibility"] = log_norm(weather.visibility_m, VIS_SCALE)

        # --- Обсервер (заглушка) ---
        obs_vec = (observer or ObserverEstimate()).to_vector()
        for name, val in zip(_OBSERVER, obs_vec):
            feats[name] = val

        return np.array([feats[name] for name in FEATURE_NAMES], dtype=np.float32)
