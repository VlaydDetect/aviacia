"""Модель отказов бортового оборудования.

`FailureState` хранит мультипликативные коэффициенты эффективности исполнительных
органов (0.0–1.0); `ControlsState.apply_failures()` умножает на них вычисленные
команды непосредственно перед отправкой, имитируя деградацию/отказ. Перенесено из
main.ipynb без изменений.
"""

from enum import Enum
from dataclasses import dataclass


class FailureMode(Enum):
    NONE = 0

    GEAR_CONFIG = 1

    ENGINE_OUT_LEFT = 2
    ENGINE_OUT_RIGHT = 3

    NWS_FAIL = 4

    REVERSE_LEFT_FAIL = 5
    REVERSE_RIGHT_FAIL = 6

    THRUST_LEFT_DEGRADED = 7
    THRUST_RIGHT_DEGRADED = 8


@dataclass
class FailureState:
    steering_eff = 1.0

    brake_left_eff = 1.0
    brake_right_eff = 1.0

    reverse_left_eff = 1.0
    reverse_right_eff = 1.0

    thrust_left_eff = 1.0
    thrust_right_eff = 1.0

    gear_conflict = False


class FailureManager:
    def __init__(self):
        self.state = FailureState()

    def reset(self):
        self.state = FailureState()

    def activate(self, mode):
        match mode:
            case FailureMode.NWS_FAIL:
                self.state.steering_eff = 0.0

            case FailureMode.ENGINE_OUT_LEFT:
                self.state.thrust_left_eff = 0.0

            case FailureMode.ENGINE_OUT_RIGHT:
                self.state.thrust_right_eff = 0.0

            case FailureMode.REVERSE_LEFT_FAIL:
                self.state.reverse_left_eff = 0.0

            case FailureMode.REVERSE_RIGHT_FAIL:
                self.state.reverse_right_eff = 0.0

            case FailureMode.GEAR_CONFIG:
                self.state.gear_conflict = True
                self.state.brake_left_eff = 0.6
                self.state.brake_right_eff = 0.6
