"""Мониторы допусков захода, пробега и прямого руления.

Отдельно от диагностического `ApproachController._envelope_warnings` (тот только пишет строковые
флаги и ни на что не влияет): здесь формируется **структурный отчёт**, по которому контур решает,
можно ли садиться. Если допуски ТЗ на заходе не выполняются — заход прерывается уходом на второй
круг (`control/system.py`), но само решение о команде принимает контур над монитором, а не монитор.

Пороги: угловые/линейные допуски — из `config/requirements.py` (ТЗ 5.1.1–5.1.3); градация особой
ситуации — из `config/criticality.py` (Приложение 1). Команды мониторы не трогают.
"""

import math
from collections.abc import Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from ismpu.utils.converts import Converts
from ismpu.config.requirements import (
    COURSE_DEVIATION_MAX_DEG, GLIDESLOPE_DEVIATION_MAX_DEG, GLIDESLOPE_GEAR_FAULT_MAX_DEG,
    GLIDESLOPE_STAB_FAULT_MAX_DEG, CENTERLINE_ALIGN_AT_30M_M,
    APPROACH_SPEED_VSR1_MARGIN_KT, APPROACH_SPEED_VFE_MARGIN_KT,
    HEADING_FAULT_MAX_DEG, HEADING_HOLD_UNTIL_KTS,
    XTE_NWS_FAIL_MAX_M, XTE_ROLLOUT_MAX_M, XTE_TAXI_MAX_M,
)
from ismpu.config.criticality import (
    SpecialSituation, lateral_limit_m, lateral_situation, RUNWAY_WIDTH_M,
)
from ismpu.config.segments import FlightSegment
from ismpu.control.failures import FailureMode, FailureState
from ismpu.control.approach import ApproachResult, ApproachTelemetry
from ismpu.config.envelope import ApproachLimits

if TYPE_CHECKING:
    from ismpu.envs.ics_sim import Telemetry

DEFAULT_RUNWAY_WIDTH_M = RUNWAY_WIDTH_M["A"]
"""Ширина ВПП по умолчанию (UUEE — класс A, 60 м), если стенд её не публикует.

Операционные допуски XTE от ширины не зависят; она нужна только для физического предела ВПП и
диагностической градации бокового увода по Приложению 1.
"""


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
    violations: tuple[str, ...]
    landing_allowed: bool


@dataclass(frozen=True)
class GroundToleranceReport:
    """Допуски наземного движения на одном такте без вмешательства в управление."""

    segment: FlightSegment
    speed_kts: float | None
    speed_error_ms: float | None
    xte_m: float | None
    xte_limit_m: float
    xte_ok: bool
    runway_limit_m: float | None
    runway_contained: bool | None
    heading_error_deg: float | None
    heading_limit_deg: float | None
    heading_ok: bool | None
    situation: SpecialSituation | None
    violations: tuple[str, ...]
    within_tolerance: bool


def evaluate_ground_tolerances(
    telemetry: "Telemetry | None",
    segment: FlightSegment,
    *,
    xte_m: float | None,
    heading_error_deg: float | None,
    speed_error_ms: float | None,
    failures: FailureState,
) -> GroundToleranceReport:
    """Проверить ТЗ 5.1.1.2 и 5.1.3 по тем же данным, которыми управляют каналы.

    Скоростная ошибка сохраняется как измерение, но не превращается в вердикт: ТЗ требует
    следовать профилю торможения, не задавая численного допуска к нему. При нарушении XTE или
    курса управление продолжается — после касания отключение корректирующих органов только
    ускорило бы выкатывание.
    """
    violations: list[str] = []
    finite_xte = xte_m is not None and math.isfinite(float(xte_m))
    speed_ms = getattr(telemetry, "groundspeed_ms", None)
    finite_speed = speed_ms is not None and math.isfinite(float(speed_ms))
    speed_kts = float(speed_ms) * Converts.MS_TO_KTS if finite_speed else None

    nws_limited = failures.steering_eff < 1.0
    # Отказ NWS отменяет обычный taxi-handover: допуск ±5 м действует до полной остановки.
    if nws_limited:
        xte_limit = XTE_NWS_FAIL_MAX_M
    elif segment is FlightSegment.TAXI:
        xte_limit = XTE_TAXI_MAX_M
    else:
        xte_limit = XTE_ROLLOUT_MAX_M
    xte_ok = finite_xte and abs(float(xte_m)) <= xte_limit
    if not finite_xte:
        violations.append("XTE_DATA")
    elif not xte_ok:
        violations.append("XTE")

    runway_limit = None
    runway_contained = None
    situation = None
    if segment is FlightSegment.ROLLOUT and finite_xte:
        width = getattr(telemetry, "runway_width_m", None)
        width = (
            float(width)
            if width is not None and math.isfinite(float(width)) and float(width) > 0.0
            else DEFAULT_RUNWAY_WIDTH_M
        )
        runway_limit = lateral_limit_m(width)
        runway_contained = abs(float(xte_m)) <= runway_limit
        if not runway_contained:
            violations.append("RUNWAY_BOUNDARY")
        if finite_speed:
            situation = lateral_situation(float(xte_m), speed_kts, width)

    if not finite_speed:
        violations.append("SPEED_DATA")

    thrust_or_reverse_limited = any((
        failures.thrust_left_eff < 1.0,
        failures.thrust_right_eff < 1.0,
        failures.reverse_left_eff < 1.0,
        failures.reverse_right_eff < 1.0,
    ))
    heading_required = (
        segment is FlightSegment.ROLLOUT
        and thrust_or_reverse_limited
        and (speed_kts is None or speed_kts >= HEADING_HOLD_UNTIL_KTS)
    )
    heading_limit = HEADING_FAULT_MAX_DEG if heading_required else None
    heading_ok = None
    finite_heading = (
        heading_error_deg is not None and math.isfinite(float(heading_error_deg))
    )
    if heading_required:
        heading_ok = finite_heading and abs(float(heading_error_deg)) <= HEADING_FAULT_MAX_DEG
        if not finite_heading:
            violations.append("HEADING_DATA")
        elif not heading_ok:
            violations.append("HEADING")

    finite_speed_error = (
        speed_error_ms is not None and math.isfinite(float(speed_error_ms))
    )
    return GroundToleranceReport(
        segment=segment,
        speed_kts=speed_kts,
        speed_error_ms=float(speed_error_ms) if finite_speed_error else None,
        xte_m=float(xte_m) if finite_xte else None,
        xte_limit_m=xte_limit,
        xte_ok=xte_ok,
        runway_limit_m=runway_limit,
        runway_contained=runway_contained,
        heading_error_deg=float(heading_error_deg) if finite_heading else None,
        heading_limit_deg=heading_limit,
        heading_ok=heading_ok,
        situation=situation,
        violations=tuple(violations),
        within_tolerance=not violations,
    )


def _glideslope_tolerance_deg(
    inp: ApproachTelemetry | None,
    faults: Iterable[FailureMode],
) -> float:
    """Допуск по глиссаде с учётом отказа (ТЗ 5.1.2.1–5.1.2.3), самый мягкий из применимых.

    Отказ стабилизатора (`FaultLeftStab`/`FaultRightStab`) → ± 1°; отказ/неполная конфигурация
    шасси (`FailureMode.GEAR_CONFIG`) → ± 0.7°; иначе штатные ± 0.5°. При нескольких отказах берётся
    наиболее мягкий допуск — держать глиссаду точнее, чем позволяет тяжесть отказа, нельзя.
    """
    tol = GLIDESLOPE_DEVIATION_MAX_DEG
    if FailureMode.GEAR_CONFIG in (faults or ()):
        tol = max(tol, GLIDESLOPE_GEAR_FAULT_MAX_DEG)
    if inp is not None and (inp.FaultLeftStab or inp.FaultRightStab):
        tol = max(tol, GLIDESLOPE_STAB_FAULT_MAX_DEG)
    return tol


def _speed_situation(speed_kt: float, limits: ApproachLimits) -> SpecialSituation:
    """Диагностическая градация приборной скорости по огибающей механизации."""
    if speed_kt <= limits.vsr1_kt:
        return SpecialSituation.HAZARDOUS       # ниже опорной скорости сваливания
    if speed_kt >= limits.vfe_kt:
        return SpecialSituation.MAJOR           # выше предела с выпущенной механизацией
    if speed_kt < limits.vapp_kt:
        return SpecialSituation.MINOR           # ниже VAPP, но выше VSR1
    return SpecialSituation.NORMAL


def evaluate_approach_tolerances(
    telemetry: "Telemetry | None",
    result: ApproachResult,
    limits: ApproachLimits,
    faults: Iterable[FailureMode],
    *,
    at_decision_gate: bool,
) -> ToleranceReport:
    """Проверить допуски захода по текущему такту. Команды не трогает.

    `result` — диагностика воздушного закона (`ApproachResult`) с уже посчитанными отклонениями;
    `limits` — эксплуатационные ограничения (`config/envelope.py`); `faults` — отказы со стенда
    (`Telemetry.faults`). `at_decision_gate` — активен ли гейт совмещения с осью ± 5 м (у высоты
    решения 30 м): выше него боковое отклонение допуском не ограничивается (за него отвечает курс).
    """
    inp = telemetry.approach_inputs if telemetry is not None else None
    violations = []

    course_deg = abs(result.course_deg)
    course_ok = course_deg <= COURSE_DEVIATION_MAX_DEG
    if not course_ok:
        violations.append("COURSE")

    gs_tol = _glideslope_tolerance_deg(inp, faults)
    glideslope_deg = abs(result.glideslope_deg)
    # Do not check the glide path too low when the beacons are no longer visible.
    glideslope_ok = (glideslope_deg <= gs_tol) or (telemetry.radio_altitude_ft > 30)
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
        gs_kts = (telemetry.groundspeed_ms if telemetry is not None else 0.0) * Converts.MS_TO_KTS
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
