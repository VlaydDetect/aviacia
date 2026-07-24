"""Критерии критичности особых ситуаций МС-21 (Приложение 1 к ТЗ).

Таблица АП-25 оценки степени опасности отказов функциональных систем, связанных с траекторным
движением ЛА: градация Нормальный полёт (БС) → УУП → СС → АС → КС и допустимые интервалы
параметров захода/посадки/пробега. Источник —
`docs/1_1_Приложение_1_Значения_для_опр_степени_критичности_отказа.pdf` (стр. 20–21 источника).

**Это классификатор допусков, а не закон управления** — как и `config/envelope.py`. Числа взяты из
приложения; часть из них (предел вертикальной скорости касания 472 fpm, VAPP/VSR1/α-prot) уже
живёт в `config/envelope.py`, и этот модуль на них ссылается, а не дублирует.

Единицы — стенда: скорости в узлах, боковое отклонение в метрах, вертикальная скорость в фут/мин.
"""

from enum import IntEnum


class SpecialSituation(IntEnum):
    """Степень опасности особой ситуации по АП-25.

    Упорядочена по возрастанию тяжести: сравнения `>=`/`max` осмысленны, поэтому «худшая из»
    ситуаций берётся обычным `max`.
    """
    NORMAL = 0        # БС — нормальный полёт (без отказа)
    MINOR = 1         # УУП — усложнение условий полёта
    MAJOR = 2         # СС — сложная ситуация
    HAZARDOUS = 3     # АС — аварийная ситуация
    CATASTROPHIC = 4  # КС — катастрофическая ситуация


# --------------------------------------------------------------------------- #
# Боковой увод на ВПП / отклонение точки касания от оси (Табл. 1)
# --------------------------------------------------------------------------- #

WHEEL_TRACK_M = 8.6
"""Zш — колея шасси МС-21 по внешним колёсам (Приложение 1, стр. 20)."""

RUNWAY_WIDTH_M = {"A": 60.0, "Б": 45.0, "В": 42.0, "Г": 35.0, "Д": 28.0, "Е": 21.0}
"""Ширина ВПП по классам аэродрома (ИКАО). UUEE — класс A (60 м)."""

MIN_RUNWAY_CLASS = "В"
"""МС-21 эксплуатируется на аэродромах не ниже класса В (FCOM MC.0001 Rev012, стр. 72)."""

LATERAL_MARGIN_M = 5.0
"""Запас до предела: нормальный полёт — Zбок ≤ Zпред − 5 м."""

LATERAL_SPEED_GATE_KTS = 30.0
"""Скорость выкатывания, разделяющая градации бокового увода (та же граница 30 узлов, что и
в ТЗ 5.1.3.3 для снятия требования по удержанию курса)."""


def lateral_limit_m(runway_width_m: float) -> float:
    """Zпред — предельное отклонение оси ВС от оси ВПП (внешнее колесо у кромки).

    Zпред = 0.5·B − 0.5·Zш (Приложение 1, стр. 20). Для UUEE (класс A, 60 м) → 25.7 м.
    """
    return 0.5 * runway_width_m - 0.5 * WHEEL_TRACK_M


def lateral_situation(lateral_m: float, groundspeed_kts: float,
                      runway_width_m: float) -> SpecialSituation:
    """Классификация бокового увода по Табл. 1.

    Норма (БС/УУП): |Zбок| ≤ Zпред − 5 м. СС: в пределах 5 м до Zпред на скорости > 30 узлов,
    либо за Zпред на скорости ≤ 30 узлов. АС: за Zпред на скорости > 30 узлов. Медленное
    приближение к пределу (в 5 м, ≤ 30 узлов) таблицей в СС не отнесено — это ещё норма.
    """
    z = abs(lateral_m)
    zlim = lateral_limit_m(runway_width_m)
    fast = groundspeed_kts > LATERAL_SPEED_GATE_KTS
    if z <= zlim - LATERAL_MARGIN_M:
        return SpecialSituation.NORMAL
    if z <= zlim:
        return SpecialSituation.MAJOR if fast else SpecialSituation.NORMAL
    return SpecialSituation.HAZARDOUS if fast else SpecialSituation.MAJOR


# --------------------------------------------------------------------------- #
# Вертикальная скорость в момент касания, Vу.кас (Табл. 1, стр. 21)
# --------------------------------------------------------------------------- #

SINK_ALLOWED_FPM = 472.0
"""Vу.доп — допустимая вертикальная скорость касания (совпадает с
`ApproachLimits.touchdown_vertical_speed_limit_fpm`)."""
SINK_MINOR_FPM = 600.0        # верх УУП для посадочного веса (≤ 69100 кг)
SINK_MAJOR_FPM = 736.0        # верх СС для посадочного веса
SINK_MINOR_HEAVY_FPM = 480.0  # верх УУП для взлётного веса (69100–79250 кг)
SINK_MAJOR_HEAVY_FPM = 586.0  # верх СС для взлётного веса

VY_LIMIT_MS = -3.05
"""Vу.эксп.пред — эксплуатационный предел (п. 25.473); −3.05 м/с (nу = 2.5)."""
VY_ALLOWED_MS = -2.0
"""Vу.гран.г.п. — граница грубой посадки; −2.0 м/с (nу = 2.0)."""


def sink_situation(sink_fpm: float, *, heavy: bool = False) -> SpecialSituation:
    """Классификация вертикальной скорости касания. `heavy` — взлётный вес 69100–79250 кг."""
    s = abs(sink_fpm)
    minor = SINK_MINOR_HEAVY_FPM if heavy else SINK_MINOR_FPM
    major = SINK_MAJOR_HEAVY_FPM if heavy else SINK_MAJOR_FPM
    if s <= SINK_ALLOWED_FPM:
        return SpecialSituation.NORMAL
    if s <= minor:
        return SpecialSituation.MINOR
    if s <= major:
        return SpecialSituation.MAJOR
    return SpecialSituation.HAZARDOUS


# --------------------------------------------------------------------------- #
# Скорость в момент касания, Vп (Табл. 1, стр. 20)
# --------------------------------------------------------------------------- #

TOUCHDOWN_SPEED_MIN_FACTOR = 0.96
"""Нижняя граница нормы: 0.96·VAPP (совпадает с `ApproachLimits.touchdown_speed_min_kt`)."""
TOUCHDOWN_SPEED_MARGIN_KT = 10.0
"""Верхняя граница нормы: VAPP + 10 узлов (`ApproachLimits.touchdown_speed_max_kt`)."""
VRUNWAY_LIMIT_KTS = 194.0
"""VВПП пред — предельная скорость касания по прочности ВПП (360 км/ч)."""


def touchdown_speed_situation(speed_kt: float, vapp_kt: float) -> SpecialSituation:
    """Классификация скорости касания относительно VAPP и VВПП пред."""
    low = TOUCHDOWN_SPEED_MIN_FACTOR * vapp_kt
    high = vapp_kt + TOUCHDOWN_SPEED_MARGIN_KT
    if low < speed_kt < high:
        return SpecialSituation.NORMAL
    if speed_kt < low:
        return SpecialSituation.MAJOR          # слишком медленно — СС
    if speed_kt < VRUNWAY_LIMIT_KTS:
        return SpecialSituation.MAJOR          # VAPP+10 ≤ Vп < VВПП пред — СС
    return SpecialSituation.HAZARDOUS          # Vп ≥ VВПП пред — АС/КС


# --------------------------------------------------------------------------- #
# Перегрузки в момент касания (Табл. 1, стр. 21)
# --------------------------------------------------------------------------- #

NY_ALLOWED = 2.0     # nу.доп — верх нормы
NY_MINOR = 2.5       # верх УУП (посадочный вес)
NY_MAJOR = 3.0       # верх СС (посадочный вес)
NY_MAJOR_HEAVY = 2.5  # верх СС (взлётный вес)

NZ_ALLOWED = 0.5     # nz.доп — верх нормы
NZ_LIMIT = 0.65      # nz.пред — верх СС


def normal_load_situation(ny: float, *, heavy: bool = False) -> SpecialSituation:
    """Классификация нормальной перегрузки посадочного удара. `heavy` — взлётный вес."""
    n = abs(ny)
    if n <= NY_ALLOWED:
        return SpecialSituation.NORMAL
    if heavy:
        return SpecialSituation.MAJOR if n <= NY_MAJOR_HEAVY else SpecialSituation.HAZARDOUS
    if n <= NY_MINOR:
        return SpecialSituation.MINOR
    if n <= NY_MAJOR:
        return SpecialSituation.MAJOR
    return SpecialSituation.HAZARDOUS


def lateral_load_situation(nz: float) -> SpecialSituation:
    """Классификация боковой составляющей перегрузки касания."""
    n = abs(nz)
    if n <= NZ_ALLOWED:
        return SpecialSituation.NORMAL
    if n <= NZ_LIMIT:
        return SpecialSituation.MAJOR
    return SpecialSituation.HAZARDOUS
