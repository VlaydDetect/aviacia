"""Чистые функции приёмки телеметрии по ТЗ и строкам матрицы.

Каждый критерий возвращает собственный вердикт, предел и основание измерения. Отсутствие
обязательного измерения считается ``FAIL``; физически неприменимый критерий явно отмечается
``SKIP``. Запуск стенда, сравнение обучающих политик и допуск моделей находятся в других
runtime-модулях: этот файл ничего не знает о transport, dashboard или SFT.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass

from ismpu.config.criticality import NY_ALLOWED, NZ_ALLOWED, SINK_ALLOWED_FPM
from ismpu.config.requirements import (
    CENTERLINE_ALIGN_AT_30M_M,
    COURSE_DEVIATION_MAX_DEG,
    GLIDESLOPE_DEVIATION_MAX_DEG,
    GLIDESLOPE_GEAR_FAULT_MAX_DEG,
    GLIDESLOPE_STAB_FAULT_MAX_DEG,
    HEADING_FAULT_MAX_DEG,
    HEADING_HOLD_UNTIL_KTS,
    TOUCHDOWN_FIRST_THIRD_M,
    XTE_NWS_FAIL_MAX_M,
    XTE_ROLLOUT_MAX_M,
    XTE_TAXI_MAX_M,
)
from ismpu.control.failures import FailureMode

PASS, FAIL, SKIP = "PASS", "FAIL", "SKIP"


@dataclass
class Criterion:
    """Один пункт ТЗ: предел, измеренное значение, вердикт и его причина."""

    name: str
    tz_ref: str
    limit: float
    measured: float | None
    verdict: str
    reason: str = ""
    evaluation_basis: str = ""
    lower_limit: float | None = None
    """Основание измерения, например истинный курс относительно оси ВПП."""

    def as_dict(self) -> dict:
        """Вернуть сериализуемую строку отчёта без отдельной DTO-схемы."""
        return asdict(self)


def _check(
    name: str,
    tz_ref: str,
    limit: float,
    measured,
    *,
    applicable: bool,
    na_reason: str = "",
) -> Criterion:
    """Проверить симметричный допуск; отсутствующее обязательное значение — отказ."""
    if not applicable:
        return Criterion(name, tz_ref, limit, None, SKIP, na_reason)
    if measured is None or not math.isfinite(float(measured)):
        return Criterion(name, tz_ref, limit, None, FAIL, "нет измерения")
    value = float(measured)
    excess = abs(value) - limit
    return Criterion(
        name,
        tz_ref,
        limit,
        value,
        PASS if excess <= 0.0 else FAIL,
        "" if excess <= 0.0 else f"превышение допуска на {excess:.2f}",
    )


def _range_check(
    name: str,
    tz_ref: str,
    lower: float,
    upper: float,
    measured,
    *,
    evaluation_basis: str = "",
) -> Criterion:
    """Проверить несимметричный интервал; отсутствующее измерение — отказ."""
    if measured is None or not math.isfinite(float(measured)):
        return Criterion(
            name, tz_ref, upper, None, FAIL, "нет измерения", evaluation_basis, lower
        )
    value = float(measured)
    ok = lower <= value <= upper
    return Criterion(
        name,
        tz_ref,
        upper,
        value,
        PASS if ok else FAIL,
        "" if ok else f"вне диапазона [{lower:.2f}, {upper:.2f}]",
        evaluation_basis,
        lower,
    )


HEADING_CRITERION_FAILURES = frozenset(
    {
        FailureMode.REVERSE_LEFT_FAIL,
        FailureMode.REVERSE_RIGHT_FAIL,
        FailureMode.ENGINE_OUT_LEFT,
        FailureMode.ENGINE_OUT_RIGHT,
        FailureMode.THRUST_LEFT_DEGRADED,
        FailureMode.THRUST_RIGHT_DEGRADED,
    }
)
"""Отказы тяги/реверса, для которых пункт 5.1.3.3 задаёт допуск курса ±5°."""


def evaluate_tz(diagnostics: dict, scenario) -> list[Criterion]:
    """Преобразовать наземные метрики запуска в вердикты раздела 5 ТЗ."""
    failures = set(getattr(scenario, "failures", ()) or ())
    nws_failed = FailureMode.NWS_FAIL in failures
    thrust_failed = bool(failures & HEADING_CRITERION_FAILURES)

    # При отказе NWS пункт 5.1.3.2 разрешает ±5 м до полной остановки.
    rollout_limit = XTE_NWS_FAIL_MAX_M if nws_failed else XTE_ROLLOUT_MAX_M
    rollout_ref = "5.1.3.2 (отказ NWS)" if nws_failed else "5.1.3.1"
    final_speed = diagnostics.get("final_speed_kts")
    reached_taxi = final_speed is not None and final_speed < HEADING_HOLD_UNTIL_KTS
    taxi_applicable = reached_taxi and not nws_failed
    taxi_na_reason = (
        "отказ NWS: 5.1.3.2 разрешает ±5 м до полной остановки, "
        "допуск руления не применяется"
        if nws_failed
        else "эпизод не дошёл до скорости руления — фазы не было"
    )

    # Пункт 5.1.3.3 относится только к нарушению тяги/реверса и скорости ≥30 kt.
    no_samples = diagnostics.get("samples", 0) == 0
    heading_measured = no_samples or diagnostics.get("heading_max_deg") is not None
    heading_applicable = thrust_failed and heading_measured
    if not thrust_failed:
        heading_na_reason = (
            "штатная работа (5.1.3.1) — требования по курсу ТЗ не задаёт; "
            "±5° относится к 5.1.3.3 (нарушение тяги/реверса)"
        )
    else:
        heading_na_reason = (
            f"эпизод целиком ниже {HEADING_HOLD_UNTIL_KTS:.0f} узлов — "
            "требование удержания курса не применяется"
        )

    heading = _check(
        "heading_max",
        "5.1.3.3",
        HEADING_FAULT_MAX_DEG,
        diagnostics.get("heading_max_deg"),
        applicable=heading_applicable,
        na_reason=heading_na_reason,
    )
    heading.evaluation_basis = "runway_relative_true_heading"

    return [
        _check(
            "xte_rollout_max",
            rollout_ref,
            rollout_limit,
            diagnostics.get("xte_rollout_max_m"),
            applicable=True,
        ),
        _check(
            "xte_taxi_max",
            "5.1.3.1 (руление)",
            XTE_TAXI_MAX_M,
            diagnostics.get("xte_taxi_max_m"),
            applicable=taxi_applicable,
            na_reason=taxi_na_reason,
        ),
        heading,
    ]


def evaluate_matrix_run(matrix_run, metrics: dict) -> list[Criterion]:
    """Оценить выбранную строку матрицы, не смешивая требования соседних фаз."""
    code = matrix_run.code
    deviations = metrics.get("max_deviations", {})

    def approach(course: float | None = None, glideslope: float | None = None):
        """Собрать только угловые критерии, относящиеся к данному шифру А."""
        criteria = []
        if course is not None:
            item = _check(
                "approach_course_max", "ТЗ 5.1.2", course,
                deviations.get("approach_course_deg"), applicable=True,
            )
            item.evaluation_basis = "ILS_localizer_angular_deviation"
            criteria.append(item)
        if glideslope is not None:
            item = _check(
                "approach_glideslope_max", "ТЗ 5.1.2", glideslope,
                deviations.get("approach_glideslope_deg"), applicable=True,
            )
            item.evaluation_basis = "ILS_glideslope_angular_deviation"
            criteria.append(item)
        return criteria

    def landing(*, align_at_30m: bool = True):
        """Собрать критерии выравнивания и первого касания."""
        touchdown = metrics.get("touchdown") or {}
        criteria = []
        if align_at_30m:
            item = _check(
                "axis_at_30m", "ТЗ 5.1.1.2", CENTERLINE_ALIGN_AT_30M_M,
                deviations.get("approach_axis_at_30m_m"), applicable=True,
            )
            item.evaluation_basis = "nearest_radio_altitude_sample_to_30m"
            criteria.append(item)
        criteria.extend([
            _range_check(
                "touchdown_distance", "ТЗ 5.1.1.2", 0.0,
                TOUCHDOWN_FIRST_THIRD_M, touchdown.get("along_track_m"),
                evaluation_basis="distance_from_runway_threshold_along_centerline",
            ),
            _check(
                "touchdown_sink", "Приложение 1", SINK_ALLOWED_FPM,
                touchdown.get("vertical_speed_fpm"), applicable=True,
            ),
        ])
        vapp = touchdown.get("vapp_kt")
        if vapp is None or not math.isfinite(float(vapp)):
            criteria.append(Criterion(
                "touchdown_speed", "Приложение 1", 0.0, None, FAIL,
                "нет VAPP для вычисления диапазона",
            ))
        else:
            criteria.append(_range_check(
                "touchdown_speed", "Приложение 1", 0.96 * float(vapp),
                float(vapp) + 10.0, touchdown.get("indicated_airspeed_kts"),
                evaluation_basis="0.96*VAPP..VAPP+10kt",
            ))
        criteria.extend([
            _check(
                "touchdown_normal_load", "Приложение 1", NY_ALLOWED,
                touchdown.get("normal_load_g"), applicable=True,
            ),
            _check(
                "touchdown_lateral_load", "Приложение 1", NZ_ALLOWED,
                touchdown.get("lateral_load_g"), applicable=True,
            ),
        ])
        return criteria

    def rollout(limit: float):
        """Собрать критерий осевой линии для нормального или отказного пробега."""
        return [_check(
            "xte_rollout_max",
            "ТЗ 5.1.3.2" if limit == XTE_NWS_FAIL_MAX_M else "ТЗ 5.1.3.1",
            limit, deviations.get("rollout_xte_m"), applicable=True,
        )]

    def thrust_fault():
        """Добавить курс ±5° для строки с отказом тяги или реверса."""
        item = _check(
            "heading_max", "ТЗ 5.1.3.3", HEADING_FAULT_MAX_DEG,
            deviations.get("runway_heading_deg"), applicable=True,
        )
        item.evaluation_basis = "runway_relative_true_heading_above_30kt"
        return rollout(XTE_ROLLOUT_MAX_M) + [item]

    if code == "А.1.1":
        return approach(COURSE_DEVIATION_MAX_DEG, GLIDESLOPE_DEVIATION_MAX_DEG) + [
            _check(
                "axis_at_30m", "ТЗ 5.1.1.2", CENTERLINE_ALIGN_AT_30M_M,
                deviations.get("approach_axis_at_30m_m"), applicable=True,
            )
        ]
    if code == "А.1.2":
        return landing(align_at_30m=False)
    if code.startswith("А.2."):
        return approach(glideslope=GLIDESLOPE_GEAR_FAULT_MAX_DEG) + landing()
    if code.startswith("А.3."):
        return approach(glideslope=GLIDESLOPE_STAB_FAULT_MAX_DEG) + landing()
    if code.startswith("А.4."):
        heading = _check(
            "approach_runway_heading_max", "ТЗ 5.1.2.4", HEADING_FAULT_MAX_DEG,
            deviations.get("approach_runway_heading_deg"), applicable=True,
        )
        heading.evaluation_basis = "runway_relative_magnetic_track"
        return [heading] + landing()
    if code == "Б.1.1":
        return rollout(XTE_ROLLOUT_MAX_M)
    if code == "Б.1.2":
        return [_check(
            "xte_taxi_max", "ТЗ 5.1.3.1 (руление)", XTE_TAXI_MAX_M,
            deviations.get("taxi_xte_m"), applicable=True,
        )]
    if code.startswith("Б.2."):
        return rollout(XTE_NWS_FAIL_MAX_M)
    if code.startswith("Б.3."):
        return thrust_fault()
    if code == "Б.4.1":
        return (
            approach(COURSE_DEVIATION_MAX_DEG, GLIDESLOPE_DEVIATION_MAX_DEG)
            + landing()
            + rollout(XTE_ROLLOUT_MAX_M)
            + [_check(
                "handover_slew_ratio", "Матрица Б.4.1", 1.0,
                metrics.get("handover", {}).get("max_rate_ratio"), applicable=True,
            )]
        )
    if code == "Б.4.2":
        heading = _check(
            "approach_runway_heading_max", "ТЗ 5.1.2.4", HEADING_FAULT_MAX_DEG,
            deviations.get("approach_runway_heading_deg"), applicable=True,
        )
        heading.evaluation_basis = "runway_relative_magnetic_track"
        return [heading] + landing() + thrust_fault()
    raise ValueError(f"для шифра матрицы {code!r} не определены критерии")


def verdict_of(criteria: list[Criterion]) -> str:
    """Вернуть ``FAIL``, если провален хотя бы один применимый критерий."""
    return FAIL if any(item.verdict == FAIL for item in criteria) else PASS
