"""Модель отказов бортового оборудования.

`FailureState` хранит мультипликативные коэффициенты эффективности исполнительных органов
(0.0–1.0); `GroundControlAllocator` исключает/ослабляет недоступные каналы до final clamp.

**Источник истины об отказах — стенд.** Раньше набор отказов задавался сценарием и включался
один раз на эпизод. Стенд сообщает фактическую конфигурацию борта телеметрией
(`ICSInputs.Fault*` → `Telemetry.faults`), и контур пересобирает состояние каждый такт
(`ControllingSystem.sync_failures`). Отказ может появиться посреди пробега, и «включили в
начале эпизода» такой случай не покрывает.

Tracking фактически распределённой команды (`ControllingSystem._track_applied`) не даёт
интегратору копить на недоступный или ограниченный орган.
"""

from enum import Enum
from dataclasses import dataclass
from collections.abc import Iterable


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


DEGRADED_THRUST_EFF = 0.5
"""Остаточная эффективность частично деградировавшей тяги. Отказ «тяга снижена», в отличие от
`ENGINE_OUT_*`, не обнуляет двигатель — иначе эти два режима были бы неразличимы."""


@dataclass
class FailureState:
    """Эффективности исполнительных органов. Аннотации типов обязательны: без них `@dataclass`
    не видит ни одного поля, и значения живут как атрибуты класса до первой записи."""
    steering_eff: float = 1.0

    brake_left_eff: float = 1.0
    brake_right_eff: float = 1.0

    reverse_left_eff: float = 1.0
    reverse_right_eff: float = 1.0

    thrust_left_eff: float = 1.0
    thrust_right_eff: float = 1.0

    gear_conflict: bool = False


class FailureManager:
    """Проецирует набор дискретных отказов в эффективности исполнительных органов."""

    def __init__(self) -> None:
        self.state: FailureState = FailureState()

    def reset(self) -> None:
        self.state = FailureState()

    def sync(self, modes: Iterable[FailureMode]) -> FailureState:
        """Привести состояние ровно к набору `modes` (то, что сообщил стенд).

        Пересборка с нуля, а не доначисление: отказ может быть **снят** (борт восстановил канал),
        и накапливающий `activate` оставил бы орган отключённым до конца эпизода.
        """
        self.state = FailureState()
        for mode in modes or ():
            self.activate(mode)
        return self.state

    def activate(self, mode: FailureMode) -> None:
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

            case FailureMode.THRUST_LEFT_DEGRADED:
                self.state.thrust_left_eff = DEGRADED_THRUST_EFF

            case FailureMode.THRUST_RIGHT_DEGRADED:
                self.state.thrust_right_eff = DEGRADED_THRUST_EFF

            case FailureMode.GEAR_CONFIG:
                self.state.gear_conflict = True
                self.state.brake_left_eff = 0.6
                self.state.brake_right_eff = 0.6
