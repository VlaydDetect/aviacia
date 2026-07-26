"""Сборка классического контура из неизменяемой конфигурации."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ismpu.control.pid import PIDController

if TYPE_CHECKING:
    from ismpu.config.scenarios import ScenarioConfig
    from ismpu.control.system import ControllingSystem


def build_pids(config: "ScenarioConfig") -> dict[str, PIDController]:
    return {
        "runway_center_pid": PIDController(**config.runway_center),
        "pid_brake_l": PIDController(**config.brake_l),
        "pid_brake_r": PIDController(**config.brake_r),
        "pid_rev_l": PIDController(**config.rev_l),
        "pid_rev_r": PIDController(**config.rev_r),
    }


def apply_control_config(
    config: "ScenarioConfig",
    controller: "ControllingSystem",
) -> "ControllingSystem":
    from ismpu.config.approach import APPROACH_PRESETS
    from ismpu.control.failures import FailureMode

    controller.setup(
        build_pids(config),
        lookahead_min=config.lookahead_min,
        lookahead_gain=config.lookahead_gain,
        xte_gain=config.xte_gain,
        steering_brake_gain=config.steering_brake_gain,
        steering_rev_gain=config.steering_rev_gain,
        law=config.law,
    )
    controller.setup_approach(APPROACH_PRESETS[config.approach])
    if config.failure is not FailureMode.NONE:
        controller.apply_failure(config.failure)
    return controller
