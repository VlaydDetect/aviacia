"""Применение абсолютных коэффициентов PID, выданных NPGS.

Действие: вектор `(17,)` = `[gains×15, w_lon, w_lat]` (тот же layout, что `GainCommand`):
`gains` — абсолютные `(kp, ki, kd)` пяти регуляторов в порядке `REGULATOR_ORDER`; `w_lon/w_lat`
— веса влияния каналов. `action_low(space)` / `action_high(space)` возвращают физический диапазон
(`agent.gain_space`) + `[0, 2]` для весов.

`reference_action(space)` = коэффициенты DEFAULT выбранного профиля + веса 1.
Для точного воспроизведения классики конкретного сценария — `preset_action(preset_gains)`.

Применение: `apply_corrections` пишет абсолютные gain'ы в `controller.pids` и веса в каналы;
при переданном `shield` проходит через `guard_coefficients` (пресет — якорь безопасности).
"""

from typing import TYPE_CHECKING

import numpy as np
from numpy.typing import ArrayLike, NDArray

from ismpu.agent.shield import GainCommand, Shield, ShieldReport, ACTION_DIM, apply_gains_to_pids
from ismpu.agent.gain_space import GainSpace
from ismpu.config.regulators import GainMap

if TYPE_CHECKING:
    from ismpu.control.system import ControllingSystem

WEIGHT_LOW, WEIGHT_HIGH = 0.0, 2.0

def action_low(space: GainSpace) -> NDArray[np.float32]:
    return np.concatenate([space.lo, [WEIGHT_LOW, WEIGHT_LOW]]).astype(np.float32)


def action_high(space: GainSpace) -> NDArray[np.float32]:
    return np.concatenate([space.hi, [WEIGHT_HIGH, WEIGHT_HIGH]]).astype(np.float32)


def reference_action(space: GainSpace) -> NDArray[np.float32]:
    result = np.concatenate([space.default, [1.0, 1.0]]).astype(np.float32)
    assert len(result) == ACTION_DIM
    return result


def decode(action: ArrayLike) -> GainCommand:
    """Плоский вектор действия → `GainCommand` (абсолютные gain'ы)."""
    return GainCommand.from_vector(np.asarray(action, dtype=float))


def preset_action(preset_gains: GainMap) -> NDArray[np.float64]:
    """17-мерное действие, точно воспроизводящее коэффициенты пресета (веса = 1).

    Возвращает **float64** (не float32) — точный путь записи для парити с классикой:
    `decode` затем даёт ровно пресетные gain'ы, и `apply_corrections(shield=None)`
    записывает их бит-в-бит.
    """
    return np.asarray(GainCommand.from_gains(preset_gains).to_vector(), dtype=np.float64)


def apply_corrections(
    command: GainCommand,
    preset_gains: GainMap,
    controller: "ControllingSystem",
    shield: Shield | None = None,
) -> tuple[GainMap, ShieldReport | None]:
    """Применяет абсолютные gain'ы к контуру. Возвращает `(effective_gains, shield_report|None)`.

    С `shield` — эффективные gain'ы и клип весов берутся из `guard_coefficients` (пресет —
    якорь границ/fallback). Без `shield` — прямая запись абсолютных gain'ов команды.
    """
    if shield is not None:
        eff, safe, report = shield.guard_coefficients(command, preset_gains)
        w_lon, w_lat = safe.w_lon, safe.w_lat
    else:
        eff = {reg: dict(g) for reg, g in command.gains.items()}
        w_lon, w_lat = command.w_lon, command.w_lat
        report = None

    apply_gains_to_pids(controller.pids, eff)
    controller.set_channel_weights(w_lon, w_lat)
    return eff, report
