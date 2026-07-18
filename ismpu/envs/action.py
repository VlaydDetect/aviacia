"""Action Space — АБСОЛЮТНЫЕ коэффициенты PID от актора → классический контур.

Действие: вектор `(17,)` = `[gains×15, w_lon, w_lat]` (тот же layout, что `GainCommand`):
`gains` — абсолютные `(kp, ki, kd)` пяти регуляторов в порядке `REGULATOR_ORDER`; `w_lon/w_lat`
— веса влияния каналов. Границы `ACTION_LOW/HIGH` = физический диапазон gain-пространства
(`agent.gain_space`) + `[0, 2]` для весов.

`REFERENCE_ACTION` = коэффициенты DEFAULT + веса 1 (аналог прежнего identity: старт-референс).
Для точного воспроизведения классики конкретного сценария — `preset_action(preset_gains)`.

Применение: `apply_corrections` пишет абсолютные gain'ы в `controller.pids` и веса в каналы;
при переданном `shield` проходит через `guard_coefficients` (пресет — якорь безопасности).
"""

import numpy as np

from ismpu.agent.shield import GainCommand, ACTION_DIM, apply_gains_to_pids
from ismpu.agent import gain_space

WEIGHT_LOW, WEIGHT_HIGH = 0.0, 2.0

ACTION_LOW = np.concatenate([gain_space.GAIN_LO, [WEIGHT_LOW, WEIGHT_LOW]]).astype(np.float32)
ACTION_HIGH = np.concatenate([gain_space.GAIN_HI, [WEIGHT_HIGH, WEIGHT_HIGH]]).astype(np.float32)
REFERENCE_ACTION = np.concatenate([gain_space.GAIN_DEFAULT, [1.0, 1.0]]).astype(np.float32)

assert len(REFERENCE_ACTION) == ACTION_DIM


def decode(action) -> GainCommand:
    """Плоский вектор действия → `GainCommand` (абсолютные gain'ы)."""
    return GainCommand.from_vector(np.asarray(action, dtype=float))


def preset_action(preset_gains: dict) -> np.ndarray:
    """17-мерное действие, точно воспроизводящее коэффициенты пресета (веса = 1).

    Возвращает **float64** (не float32) — точный путь записи для парити с классикой:
    `decode` затем даёт ровно пресетные gain'ы, и `apply_corrections(shield=None)`
    записывает их бит-в-бит.
    """
    return np.asarray(GainCommand.from_gains(preset_gains).to_vector(), dtype=np.float64)


def apply_corrections(command: GainCommand, preset_gains: dict, controller, shield=None):
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
