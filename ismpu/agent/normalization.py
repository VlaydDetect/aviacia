"""Фиксированная нормализация Observation Space — единый контракт train ↔ deploy.

Все физические масштабы заданы КОНСТАНТАМИ (не «плавающая» статистика по батчу),
иначе детерминизм при поставке ломается (§5). Значения сериализуются вместе с весами
(`snapshot()`), чтобы инференс на стенде использовал ровно те же масштабы, что и
обучение.

Нормировка приводит признаки примерно к диапазону [-1, 1]. Часть PID-признаков
нормируется по параметрам самого регулятора (anti_windup, min/max, база gain'ов) —
они фиксированы пресетом, поэтому тоже часть контракта.
"""

import math

NORM_VERSION = 2   # v2: NPGS выдаёт абсолютные коэффициенты → gain-пространство (см. gain_space.py)

# --- Глобальные физические масштабы (линейная нормировка x/scale, если не указано иное) ---
XTE_SCALE = 30.0             # cross-track error, м
HEADING_SCALE = 45.0         # heading error, °
LOOKAHEAD_SCALE = 120.0      # look-ahead point, м
SPEED_SCALE = 110.0          # путевая/эталонная скорость, м/с (~200 узлов)
SPEED_ERR_SCALE = 50.0       # ошибка скорости, м/с
ACCEL_SCALE = 5.0            # продольное ускорение, м/с²
WIND_SCALE = 20.0            # компоненты ветра, м/с
FRICTION_SCALE = 15.0        # runway_friction (enum 0..15)
VIS_SCALE = 16000.0          # видимость, м (лог-нормировка)
DERIV_SCALE = 20.0           # отфильтрованная производная PID (масштаб, эмпирический)
# Нормировка коэффициентов PID — в лог-пространстве gain'ов (`agent.gain_space`), т.к.
# сеть теперь предсказывает АБСОЛЮТНЫЕ коэффициенты (не поправки к базе). См. gain_norm там.


def clip_unit(x: float) -> float:
    return -1.0 if x < -1.0 else 1.0 if x > 1.0 else x


def linear(x: float, scale: float, center: float = 0.0) -> float:
    return (x - center) / scale


def log_norm(x: float, scale: float) -> float:
    """Лог-нормировка неотрицательной величины (видимость): log1p(x)/log1p(scale)."""
    x = max(0.0, x)
    return math.log1p(x) / math.log1p(scale)


def symmetric(x: float, lo: float, hi: float) -> float:
    """Отображает [lo, hi] → [-1, 1] (для PID output по его границам)."""
    if hi <= lo:
        return 0.0
    center = 0.5 * (lo + hi)
    half = 0.5 * (hi - lo)
    return clip_unit((x - center) / half)


def snapshot() -> dict:
    """Сериализуемый слепок контракта нормировки (сохраняется вместе с весами).

    Включает таблицу gain-пространства (`gain_space.snapshot()`) — так чекпоинт полностью
    фиксирует и масштабы obs, и отображение z↔коэффициенты PID (детерминизм поставки)."""
    from ismpu.agent import gain_space  # локальный импорт: избегаем цикла на уровне модуля
    return {
        "version": NORM_VERSION,
        "xte": XTE_SCALE, "heading": HEADING_SCALE, "lookahead": LOOKAHEAD_SCALE,
        "speed": SPEED_SCALE, "speed_err": SPEED_ERR_SCALE, "accel": ACCEL_SCALE,
        "wind": WIND_SCALE, "friction": FRICTION_SCALE, "visibility": VIS_SCALE,
        "derivative": DERIV_SCALE, "gain_space": gain_space.snapshot(),
    }
