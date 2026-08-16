"""Типы и порядок коэффициентов пяти наземных PID-регуляторов.

Модуль намеренно не описывает обучающее действие, веса каналов или прямые выходы сети на
актуаторы. Оба SFT-регрессора выдают только
абсолютные ``kp/ki/kd``; их segment-specific layout задаёт :mod:`ismpu.runtime.sft`.

Этот маленький модуль нужен лишь для разрыва циклических импортов между конфигурацией и
``ControllingSystem`` и для единого написания ключей наземного словаря ``pids``.
"""

from typing import TYPE_CHECKING, Literal, TypeAlias

if TYPE_CHECKING:
    from ismpu.control.pid import PIDController


GainKey: TypeAlias = Literal["kp", "ki", "kd"]
"""Единственные параметры PID, которые имеет право изменять SFT runtime."""

RegulatorKey: TypeAlias = Literal[
    "runway_center_pid", "pid_brake_l", "pid_brake_r", "pid_rev_l", "pid_rev_r",
]
"""Ключи пяти stateful PID-регуляторов наземного контура."""

PidMap: TypeAlias = dict[RegulatorKey, "PIDController"]
"""Полный словарь PID, который принимает ``ControllingSystem.setup``."""

REGULATOR_ORDER: tuple[RegulatorKey, ...] = (
    "runway_center_pid", "pid_brake_l", "pid_brake_r", "pid_rev_l", "pid_rev_r",
)
"""Стабильный порядок наземных регуляторов для сериализации и диагностики."""

GAIN_KEYS: tuple[GainKey, ...] = ("kp", "ki", "kd")
"""Стабильный порядок тройки коэффициентов в checkpoint и телеметрии."""
