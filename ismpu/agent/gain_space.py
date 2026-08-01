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
from collections.abc import Sequence
from typing import Any

import numpy as np
from numpy.typing import ArrayLike, NDArray

from ismpu.config.regulators import (
    GAIN_KEYS,
    N_GAINS,
    REGULATOR_ORDER,
    GainKey,
    GainMap,
    RegulatorKey,
)
from ismpu.config.scenarios import DEFAULT, SCENARIOS, PidConfig, ScenarioConfig
EXPAND = 2.0        # расширение физического диапазона за пределы наблюдённого в пресетах
_EPS = 1e-6         # отступ от ±1 при atanh (устойчивость на краях полосы)

def _slot_order() -> list[tuple[RegulatorKey, GainKey]]:
    """15 слотов в каноническом порядке: REGULATOR_ORDER × (kp, ki, kd)."""
    return [(reg, k) for reg in REGULATOR_ORDER for k in GAIN_KEYS]


def _regulator_config(config: ScenarioConfig, regulator: RegulatorKey) -> PidConfig:
    """Возвращает PID-секцию сценария без динамического доступа к полям dataclass."""
    if regulator == "runway_center_pid":
        return config.runway_center
    if regulator == "pid_brake_l":
        return config.brake_l
    if regulator == "pid_brake_r":
        return config.brake_r
    if regulator == "pid_rev_l":
        return config.rev_l
    if regulator == "pid_rev_r":
        return config.rev_r
    raise ValueError(f"Неизвестный регулятор: {regulator}")


def _collect_preset_values(reg: RegulatorKey, key: GainKey) -> list[float]:
    """Все значения gain'а `key` регулятора `reg` по всем пресетам SCENARIOS."""
    vals: list[float] = []
    for cfg in SCENARIOS.values():
        d = _regulator_config(cfg, reg)
        v = d.get(key)
        if v is not None and v > 0.0:
            vals.append(float(v))
    return vals


def _build_table() -> tuple[
    list[tuple[RegulatorKey, GainKey]],
    NDArray[np.float64],
    NDArray[np.float64],
    NDArray[np.float64],
    NDArray[np.float64],
    NDArray[np.float64],
]:
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
        default[i] = float(_regulator_config(DEFAULT, reg)[key])
    return slots, ref, s, lo, hi, default


SLOTS, GAIN_REF, GAIN_S, GAIN_LO, GAIN_HI, GAIN_DEFAULT = _build_table()


def _by_reg(arr: Sequence[float]) -> GainMap:
    """Плоский массив (15,) → вложенный словарь {reg: {kp/ki/kd: value}} (для Shield/obs)."""
    return {reg: {k: float(arr[SLOTS.index((reg, k))]) for k in GAIN_KEYS} for reg in REGULATOR_ORDER}


GAIN_REF_MAP = _by_reg(GAIN_REF)
GAIN_S_MAP = _by_reg(GAIN_S)
GAIN_LO_MAP = _by_reg(GAIN_LO)
GAIN_HI_MAP = _by_reg(GAIN_HI)
GAIN_DEFAULT_MAP = _by_reg(GAIN_DEFAULT)


def gain_norm_scalar(value: float, reg: RegulatorKey, key: GainKey) -> float:
    """Скалярная нормировка одного коэффициента в [−1, 1]: `clip(log(value/ref)/s)`."""
    ref = GAIN_REF_MAP[reg][key]
    s = GAIN_S_MAP[reg][key]
    r = math.log(max(float(value), 1e-12) / ref) / s
    return -1.0 if r < -1.0 else 1.0 if r > 1.0 else r


# --------------------------------------------------------------------------- #
# Прямое/обратное отображение z ↔ gain (numpy; тензорные версии — в gain_scheduler)
# --------------------------------------------------------------------------- #

def to_gain(
    z: ArrayLike,
    ref: ArrayLike = GAIN_REF,
    s: ArrayLike = GAIN_S,
) -> NDArray[np.float64]:
    """z → абсолютный gain: `ref · exp(s · tanh(z))`."""
    ref_arr = np.asarray(ref, dtype=np.float64)
    s_arr = np.asarray(s, dtype=np.float64)
    return ref_arr * np.exp(s_arr * np.tanh(np.asarray(z, dtype=np.float64)))


def inv_gain(
    gain: ArrayLike,
    ref: ArrayLike = GAIN_REF,
    s: ArrayLike = GAIN_S,
) -> NDArray[np.float64]:
    """Абсолютный gain → z (инверсия `to_gain`). Клип log-отношения к (−1, 1) перед atanh."""
    gain = np.maximum(np.asarray(gain, dtype=np.float64), 1e-12)
    ratio = np.log(gain / np.asarray(ref, dtype=np.float64)) / np.asarray(s, dtype=np.float64)
    ratio = np.clip(ratio, -1.0 + _EPS, 1.0 - _EPS)
    return np.arctanh(ratio)


def gain_norm(
    gain: ArrayLike,
    ref: ArrayLike = GAIN_REF,
    s: ArrayLike = GAIN_S,
) -> NDArray[np.float64]:
    """Нормировка gain'а в [−1, 1] для Observation: `clip(log(gain/ref)/s)` (= tanh(z))."""
    gain = np.asarray(gain, dtype=np.float64)
    ratio = np.log(np.maximum(gain, 1e-12) / np.asarray(ref, dtype=np.float64)) / np.asarray(s, dtype=np.float64)
    return np.clip(ratio, -1.0, 1.0)


def default_bias() -> NDArray[np.float64]:
    """Bias голов (15,), при котором z→bias даёт выход ≈ GAIN_DEFAULT (безопасный старт)."""
    return inv_gain(GAIN_DEFAULT)


def slot_index(reg: RegulatorKey, key: GainKey) -> int:
    return SLOTS.index((reg, key))


def snapshot() -> dict[str, Any]:
    """Сериализуемый слепок gain-пространства (входит в normalization.snapshot / чекпоинт)."""
    return {
        "slots": [f"{reg}:{key}" for reg, key in SLOTS],
        "ref": GAIN_REF.tolist(), "s": GAIN_S.tolist(),
        "lo": GAIN_LO.tolist(), "hi": GAIN_HI.tolist(),
        "default": GAIN_DEFAULT.tolist(), "expand": EXPAND,
    }
