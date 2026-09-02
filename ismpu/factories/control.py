"""Сборка классического контура из неизменяемой конфигурации."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ismpu.control.pid import PIDController

if TYPE_CHECKING:
    from ismpu.config.scenarios import GroundControlConfig
    from ismpu.control.system import ControllingSystem


def build_pids(config: "GroundControlConfig") -> dict[str, PIDController]:
    def build(spec: dict) -> PIDController:
        values = dict(spec)
        anti_windup = float(values.get("anti_windup", 10.0))
        values.setdefault("integral_min", -anti_windup)
        values.setdefault("integral_max", anti_windup)
        values.setdefault("derivative_on_measurement", True)
        values.setdefault("conditional_anti_windup", True)
        values.setdefault("exact_discretization", True)
        values.setdefault("clamp_dt", True)
        values.setdefault("der_filter_tf", 0.25)
        values.setdefault("tracking_tau_s", 0.5)
        return PIDController(**values)

    return {
        "runway_center_pid": build(config.runway_center),
        "pid_brake_l": build(config.brake_l),
        "pid_brake_r": build(config.brake_r),
        "pid_rev_l": build(config.rev_l),
        "pid_rev_r": build(config.rev_r),
    }


def apply_ground_control(
    config: "GroundControlConfig",
    controller: "ControllingSystem",
) -> "ControllingSystem":
    controller.setup(
        build_pids(config),
        lookahead_min=config.lookahead_min,
        lookahead_gain=config.lookahead_gain,
        xte_gain=config.xte_gain,
        steering_brake_gain=config.steering_brake_gain,
        steering_rev_gain=config.steering_rev_gain,
        law=config.law,
        target_speed_kts=config.target_speed_kts,
        braking_distance_m=config.braking_distance_m,
        completion_rule=config.completion_rule,
        steering_rate_per_s=config.steering_rate_per_s,
        brake_rate_per_s=config.brake_rate_per_s,
        reverse_rate_per_s=config.reverse_rate_per_s,
        failure_yaw_compensation_gain=config.failure_yaw_compensation_gain,
        taxi_throttle_kp_per_kt=config.taxi_throttle_kp_per_kt,
        taxi_throttle_max_norm=config.taxi_throttle_max_norm,
        taxi_throttle_deadband_kts=config.taxi_throttle_deadband_kts,
    )
    return controller
