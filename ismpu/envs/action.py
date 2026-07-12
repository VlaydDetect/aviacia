"""Action Space — мультипликативные поправки актора → классический контур (§6).

Действие: вектор `(17,)` = `[α×15, w_lon, w_lat]` (тот же layout, что `Corrections`
в Shield). `α` — множители к базовым `(kp, ki, kd)` пяти регуляторов; `w_lon/w_lat` —
веса влияния каналов. `IDENTITY_ACTION` (все α=1, веса=1) обязана воспроизводить
классику бит-в-бит (инвариант §1).

Границы `ACTION_LOW/HIGH` совпадают с уровнем 1 Shield; жёсткая гарантия — Shield
(§8), а не свойство сети. Применение: `apply_corrections` пишет эффективные gain'ы в
`controller.pids` и веса в каналы; при переданном `shield` проходит через
`guard_coefficients` (уровни 1-2).
"""

import numpy as np

from ismpu.agent.shield import (
    Corrections, ACTION_DIM, N_ALPHA, apply_gains_to_pids,
)

ALPHA_LOW, ALPHA_HIGH = 0.5, 1.5
WEIGHT_LOW, WEIGHT_HIGH = 0.0, 2.0

ACTION_LOW = np.array([ALPHA_LOW] * N_ALPHA + [WEIGHT_LOW, WEIGHT_LOW], dtype=np.float32)
ACTION_HIGH = np.array([ALPHA_HIGH] * N_ALPHA + [WEIGHT_HIGH, WEIGHT_HIGH], dtype=np.float32)
IDENTITY_ACTION = np.array([1.0] * N_ALPHA + [1.0, 1.0], dtype=np.float32)

assert len(IDENTITY_ACTION) == ACTION_DIM


def decode(action) -> Corrections:
    """Плоский вектор действия → `Corrections`."""
    return Corrections.from_vector(np.asarray(action, dtype=float))


def _effective_gains(corrections: Corrections, base_gains: dict) -> dict:
    eff = {}
    for reg, g in base_gains.items():
        ap, ai, ad = corrections.alpha.get(reg, (1.0, 1.0, 1.0))
        eff[reg] = {"kp": g["kp"] * ap, "ki": g["ki"] * ai, "kd": g["kd"] * ad}
    return eff


def apply_corrections(corrections: Corrections, base_gains: dict, controller, shield=None):
    """Применяет поправки к контуру. Возвращает `(effective_gains, shield_report|None)`.

    С `shield` — эффективные gain'ы и клип весов берутся из `guard_coefficients`
    (уровни 1-2). Без `shield` — прямое умножение поправок на базу (identity → база).
    """
    if shield is not None:
        eff, safe, report = shield.guard_coefficients(corrections, base_gains)
        w_lon, w_lat = safe.w_lon, safe.w_lat
    else:
        eff = _effective_gains(corrections, base_gains)
        w_lon, w_lat = corrections.w_lon, corrections.w_lat
        report = None

    apply_gains_to_pids(controller.pids, eff)
    controller.set_channel_weights(w_lon, w_lat)
    return eff, report
