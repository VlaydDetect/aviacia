"""Единый источник истины gain-пространства NPGS (план: переход на абсолютные коэффициенты).

Сеть теперь предсказывает **абсолютные** коэффициенты PID (kp/ki/kd для 5 регуляторов),
а не мультипликативные поправки. Параметризация выхода — лог-tanh вокруг референса:

    gain_i = ref_i · exp(s_i · tanh(z_i))          # z=0 → ref_i, полоса [ref·e^{-s}, ref·e^{+s}]
    z_i    = atanh( log(target_i / ref_i) / s_i )   # инверсия (для SFT-целей)

Таблица `ref/s/lo/hi` по 15 слотам `(regulator, kp|ki|kd)` вычисляется программно из
семейства пресетов `config.scenarios.SCENARIOS` и замораживается на импорте:

- `lo_i / hi_i` — физический диапазон = min/max по пресетам, расширенный в `EXPAND` раз
  (сеть может уйти немного за экспертов; Shield всё равно центрируется на пресете).
- `ref_i = sqrt(min·max)` — геометрическая середина (минимизирует |log(target/ref)| →
  лучшее число обусловленности регрессии на широких диапазонах, до ~70× по `ki`).
- `s_i = log(EXPAND · sqrt(max/min))` — симметричная лог-полуширина; так `lo/hi` = края
  полосы, все пресеты (и DEFAULT) строго внутри ⇒ `atanh` целей конечен, а bias-инициализация
  голов на DEFAULT корректна (`s_i ≥ |log(DEFAULT_i/ref_i)|`).

Порядок 15 слотов = `shield.REGULATOR_ORDER` × `(kp, ki, kd)` — совпадает с первыми 15
компонентами 17-мерного действия (`[gains×15, w_lon, w_lat]`). Таблица сериализуется в
`normalization.snapshot()` → чекпоинт полностью фиксирует gain-пространство (детерминизм
поставки). Веса каналов `w_lon/w_lat` сюда НЕ входят (у них своя параметризация `1+tanh`).
"""

from __future__ import annotations

import math

import numpy as np

from ismpu.config.regulators import REGULATOR_ORDER, GAIN_KEYS, N_GAINS
from ismpu.config.scenarios import SCENARIOS, DEFAULT
EXPAND = 2.0        # расширение физического диапазона за пределы наблюдённого в пресетах
_EPS = 1e-6         # отступ от ±1 при atanh (устойчивость на краях полосы)

# Регулятор (по REGULATOR_ORDER) → имя поля-словаря в ScenarioConfig.
_REG_TO_FIELD = {
    "runway_center_pid": "runway_center",
    "pid_brake_l": "brake_l",
    "pid_brake_r": "brake_r",
    "pid_rev_l": "rev_l",
    "pid_rev_r": "rev_r",
}


def _slot_order() -> list[tuple[str, str]]:
    """15 слотов в каноническом порядке: REGULATOR_ORDER × (kp, ki, kd)."""
    return [(reg, k) for reg in REGULATOR_ORDER for k in GAIN_KEYS]


def _collect_preset_values(reg: str, key: str) -> list[float]:
    """Все значения gain'а `key` регулятора `reg` по всем пресетам SCENARIOS."""
    field = _REG_TO_FIELD[reg]
    vals = []
    for cfg in SCENARIOS.values():
        d = getattr(cfg, field)
        v = d.get(key)
        if v is not None and v > 0.0:
            vals.append(float(v))
    return vals


def _build_table():
    slots = _slot_order()
    ref = np.empty(N_GAINS, dtype=np.float64)
    s = np.empty(N_GAINS, dtype=np.float64)
    lo = np.empty(N_GAINS, dtype=np.float64)
    hi = np.empty(N_GAINS, dtype=np.float64)
    default = np.empty(N_GAINS, dtype=np.float64)

    for i, (reg, key) in enumerate(slots):
        vals = _collect_preset_values(reg, key)
        vmin, vmax = min(vals), max(vals)
        lo[i] = vmin / EXPAND
        hi[i] = vmax * EXPAND
        ref[i] = math.sqrt(vmin * vmax)                  # геометрическая середина
        s[i] = math.log(EXPAND * math.sqrt(vmax / vmin))  # = log(hi/ref) = log(ref/lo)
        default[i] = float(getattr(DEFAULT, _REG_TO_FIELD[reg])[key])
    return slots, ref, s, lo, hi, default


SLOTS, GAIN_REF, GAIN_S, GAIN_LO, GAIN_HI, GAIN_DEFAULT = _build_table()


def _by_reg(arr) -> dict:
    """Плоский массив (15,) → вложенный словарь {reg: {kp/ki/kd: value}} (для Shield/obs)."""
    return {reg: {k: float(arr[SLOTS.index((reg, k))]) for k in GAIN_KEYS} for reg in REGULATOR_ORDER}


GAIN_REF_MAP = _by_reg(GAIN_REF)
GAIN_S_MAP = _by_reg(GAIN_S)
GAIN_LO_MAP = _by_reg(GAIN_LO)
GAIN_HI_MAP = _by_reg(GAIN_HI)
GAIN_DEFAULT_MAP = _by_reg(GAIN_DEFAULT)


def gain_norm_scalar(value: float, reg: str, key: str) -> float:
    """Скалярная нормировка одного коэффициента в [−1, 1]: `clip(log(value/ref)/s)`."""
    ref = GAIN_REF_MAP[reg][key]
    s = GAIN_S_MAP[reg][key]
    r = math.log(max(float(value), 1e-12) / ref) / s
    return -1.0 if r < -1.0 else 1.0 if r > 1.0 else r


# --------------------------------------------------------------------------- #
# Прямое/обратное отображение z ↔ gain (numpy; тензорные версии — в gain_scheduler)
# --------------------------------------------------------------------------- #

def to_gain(z, ref=GAIN_REF, s=GAIN_S) -> np.ndarray:
    """z → абсолютный gain: `ref · exp(s · tanh(z))`."""
    return ref * np.exp(s * np.tanh(np.asarray(z, dtype=np.float64)))


def inv_gain(gain, ref=GAIN_REF, s=GAIN_S) -> np.ndarray:
    """Абсолютный gain → z (инверсия `to_gain`). Клип log-отношения к (−1, 1) перед atanh."""
    gain = np.maximum(np.asarray(gain, dtype=np.float64), 1e-12)
    ratio = np.log(gain / ref) / s
    ratio = np.clip(ratio, -1.0 + _EPS, 1.0 - _EPS)
    return np.arctanh(ratio)


def gain_norm(gain, ref=GAIN_REF, s=GAIN_S) -> np.ndarray:
    """Нормировка gain'а в [−1, 1] для Observation: `clip(log(gain/ref)/s)` (= tanh(z))."""
    gain = np.asarray(gain, dtype=np.float64)
    ratio = np.log(np.maximum(gain, 1e-12) / ref) / s
    return np.clip(ratio, -1.0, 1.0)


def default_bias() -> np.ndarray:
    """Bias голов (15,), при котором z→bias даёт выход ≈ GAIN_DEFAULT (безопасный старт)."""
    return inv_gain(GAIN_DEFAULT)


def slot_index(reg: str, key: str) -> int:
    return SLOTS.index((reg, key))


def snapshot() -> dict:
    """Сериализуемый слепок gain-пространства (входит в normalization.snapshot / чекпоинт)."""
    return {
        "slots": [f"{reg}:{key}" for reg, key in SLOTS],
        "ref": GAIN_REF.tolist(), "s": GAIN_S.tolist(),
        "lo": GAIN_LO.tolist(), "hi": GAIN_HI.tolist(),
        "default": GAIN_DEFAULT.tolist(), "expand": EXPAND,
    }
