"""Монитор допусков захода в реальном времени + классификация особой ситуации.

Отдельно от диагностического `ApproachChannel._envelope_warnings` (тот только пишет строковые
флаги и ни на что не влияет): здесь формируется **структурный отчёт**, по которому контур решает,
можно ли садиться. Если допуски ТЗ на заходе не выполняются — заход прерывается уходом на второй
круг (`control/system.py`), но само решение о команде принимает контур над монитором, а не монитор.

Пороги: угловые/линейные допуски — из `config/requirements.py` (ТЗ 5.1.1–5.1.2); градация особой
ситуации — из `config/criticality.py` (Приложение 1). Команды монитор не трогает.
"""

from dataclasses import dataclass

from ismpu.utils.converts import Converts
from ismpu.config.requirements import (
    COURSE_DEVIATION_MAX_DEG, GLIDESLOPE_DEVIATION_MAX_DEG, GLIDESLOPE_GEAR_FAULT_MAX_DEG,
    GLIDESLOPE_STAB_FAULT_MAX_DEG, CENTERLINE_ALIGN_AT_30M_M,
    APPROACH_SPEED_VSR1_MARGIN_KT, APPROACH_SPEED_VFE_MARGIN_KT,
)
from ismpu.config.criticality import SpecialSituation, lateral_situation, RUNWAY_WIDTH_M
from ismpu.control.failures import FailureMode

DEFAULT_RUNWAY_WIDTH_M = RUNWAY_WIDTH_M["A"]
"""Ширина ВПП по умолчанию (UUEE — класс A, 60 м), если стенд ширину не публикует. Влияет только
на диагностическую градацию бокового увода, не на триггер ухода (тот — по допуску ТЗ ±5 м)."""


@dataclass(frozen=True)
class ToleranceReport:
    """Результат проверки допусков захода на одном такте.

    `landing_allowed` — все ли допуски ТЗ выполнены (иначе садиться нельзя). `situation` — худшая
    степень особой ситуации по Приложению 1 (диагностика для логов и приёмки, на триггер не влияет).
    """
    course_deg: float
    course_ok: bool
    glideslope_deg: float
    glideslope_tol_deg: float
    glideslope_ok: bool
    speed_kt: float
    speed_ok: bool
    lateral_m: "float | None"
    lateral_ok_at_gate: "bool | None"
    situation: SpecialSituation
    violations: tuple
    landing_allowed: bool


def _glideslope_tolerance_deg(inp, faults) -> float:
    """Допуск по глиссаде с учётом отказа (ТЗ 5.1.2.1–5.1.2.3), самый мягкий из применимых.

    Отказ стабилизатора (`FaultLeftStab`/`FaultRightStab`) → ± 1°; отказ/неполная конфигурация
    шасси (`FailureMode.GEAR_CONFIG`) → ± 0.7°; иначе штатные ± 0.5°. При нескольких отказах берётся
    наиболее мягкий допуск — держать глиссаду точнее, чем позволяет тяжесть отказа, нельзя.
    """
    tol = GLIDESLOPE_DEVIATION_MAX_DEG
    if FailureMode.GEAR_CONFIG in (faults or ()):
        tol = max(tol, GLIDESLOPE_GEAR_FAULT_MAX_DEG)
    if inp is not None and (getattr(inp, "FaultLeftStab", 0) or getattr(inp, "FaultRightStab", 0)):
        tol = max(tol, GLIDESLOPE_STAB_FAULT_MAX_DEG)
    return tol


def _speed_situation(speed_kt: float, limits) -> SpecialSituation:
    """Диагностическая градация приборной скорости по огибающей механизации."""
    if speed_kt <= limits.vsr1_kt:
        return SpecialSituation.HAZARDOUS       # ниже опорной скорости сваливания
    if speed_kt >= limits.vfe_kt:
        return SpecialSituation.MAJOR           # выше предела с выпущенной механизацией
    if speed_kt < limits.vapp_kt:
        return SpecialSituation.MINOR           # ниже VAPP, но выше VSR1
    return SpecialSituation.NORMAL


def evaluate_approach_tolerances(telemetry, result, limits, faults, *,
                                 at_decision_gate: bool) -> ToleranceReport:
    """Проверить допуски захода по текущему такту. Команды не трогает.

    `result` — диагностика воздушного закона (`ApproachResult`) с уже посчитанными отклонениями;
    `limits` — эксплуатационные ограничения (`config/envelope.py`); `faults` — отказы со стенда
    (`Telemetry.faults`). `at_decision_gate` — активен ли гейт совмещения с осью ± 5 м (у высоты
    решения 30 м): выше него боковое отклонение допуском не ограничивается (за него отвечает курс).
    """
    inp = getattr(telemetry, "ics_inputs", None) if telemetry is not None else None
    violations = []

    course_deg = abs(result.course_deg)
    course_ok = course_deg <= COURSE_DEVIATION_MAX_DEG
    if not course_ok:
        violations.append("COURSE")

    gs_tol = _glideslope_tolerance_deg(inp, faults)
    glideslope_deg = abs(result.glideslope_deg)
    glideslope_ok = glideslope_deg <= gs_tol
    if not glideslope_ok:
        violations.append("GLIDESLOPE")

    speed_kt = inp.IndicatedAirspeed if inp is not None else 0.0
    low = limits.vsr1_kt + APPROACH_SPEED_VSR1_MARGIN_KT
    high = limits.vfe_kt - APPROACH_SPEED_VFE_MARGIN_KT
    speed_ok = low < speed_kt < high
    if not speed_ok:
        violations.append("SPEED")

    lateral_m = telemetry.lateral_deviation_m if telemetry is not None else None
    lateral_ok_at_gate = None
    if at_decision_gate and lateral_m is not None:
        lateral_ok_at_gate = abs(lateral_m) <= CENTERLINE_ALIGN_AT_30M_M
        if not lateral_ok_at_gate:
            violations.append("LATERAL")

    # Диагностическая степень особой ситуации (Приложение 1): худшая по параметрам.
    situation = SpecialSituation.NORMAL
    if not course_ok or not glideslope_ok:
        situation = max(situation, SpecialSituation.MAJOR)
    situation = max(situation, _speed_situation(speed_kt, limits))
    if lateral_m is not None:
        gs_kts = (getattr(telemetry, "groundspeed_ms", 0.0) or 0.0) * Converts.MS_TO_KTS
        width = (telemetry.runway_width_m or DEFAULT_RUNWAY_WIDTH_M) if telemetry is not None \
            else DEFAULT_RUNWAY_WIDTH_M
        situation = max(situation, lateral_situation(lateral_m, gs_kts, width))

    landing_allowed = (course_ok and glideslope_ok and speed_ok
                       and lateral_ok_at_gate is not False)

    return ToleranceReport(
        course_deg=course_deg, course_ok=course_ok,
        glideslope_deg=glideslope_deg, glideslope_tol_deg=gs_tol, glideslope_ok=glideslope_ok,
        speed_kt=speed_kt, speed_ok=speed_ok,
        lateral_m=lateral_m, lateral_ok_at_gate=lateral_ok_at_gate,
        situation=situation, violations=tuple(violations), landing_allowed=landing_allowed,
    )
