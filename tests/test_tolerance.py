"""Допуски захода: классификаторы критичности (Приложение 1) и рантайм-монитор.

Проверяются граничные значения таблицы АП-25 (боковой увод, вертикальная скорость и скорость
касания, перегрузки) и то, что `evaluate_approach_tolerances` верно решает `landing_allowed`:
выбор допуска по глиссаде от вида отказа, гейт совмещения с осью ± 5 м, скоростная огибающая.
"""

import pytest

from ismpu.config.criticality import (
    SpecialSituation, lateral_limit_m, lateral_situation, sink_situation,
    touchdown_speed_situation, normal_load_situation, lateral_load_situation,
    WHEEL_TRACK_M, RUNWAY_WIDTH_M,
)
from ismpu.config.envelope import approach_limits, LandingFlapConfiguration
from ismpu.config.segments import FlightSegment
from ismpu.control.approach import ApproachResult
from ismpu.control.failures import FailureState
from ismpu.control.tolerance import evaluate_approach_tolerances, evaluate_ground_tolerances
from ismpu.envs.ics_sim import Telemetry

from fakes import airborne_inputs, engaged_inputs


# --------------------------------------------------------------------------- #
# Классификаторы критичности (config/criticality.py)
# --------------------------------------------------------------------------- #

def test_lateral_limit_formula_matches_appendix():
    """Zпред = 0.5·B − 0.5·Zш: класс A (60 м) → 25.7 м, класс В (42 м) → 16.7 м."""
    assert lateral_limit_m(RUNWAY_WIDTH_M["A"]) == pytest.approx(25.7)
    assert lateral_limit_m(RUNWAY_WIDTH_M["В"]) == pytest.approx(16.7)
    assert WHEEL_TRACK_M == pytest.approx(8.6)


def test_lateral_situation_bands():
    """Норма ≤ Zпред−5 м; у предела на скорости → СС; за пределом на скорости → АС."""
    w = RUNWAY_WIDTH_M["A"]                      # Zпред = 25.7 м, норма ≤ 20.7 м
    assert lateral_situation(20.0, 140.0, w) is SpecialSituation.NORMAL
    assert lateral_situation(21.0, 140.0, w) is SpecialSituation.MAJOR      # у предела, быстро
    assert lateral_situation(21.0, 20.0, w) is SpecialSituation.NORMAL      # у предела, но медленно
    assert lateral_situation(26.0, 140.0, w) is SpecialSituation.HAZARDOUS  # за пределом, быстро
    assert lateral_situation(26.0, 20.0, w) is SpecialSituation.MAJOR       # за пределом, медленно


def test_sink_situation_bands():
    """Пороги вертикальной скорости касания 472 / 600 / 736 fpm (посадочный вес)."""
    assert sink_situation(-400.0) is SpecialSituation.NORMAL
    assert sink_situation(-500.0) is SpecialSituation.MINOR
    assert sink_situation(-700.0) is SpecialSituation.MAJOR
    assert sink_situation(-800.0) is SpecialSituation.HAZARDOUS
    # Взлётный вес — пороги жёстче: 480 / 586 fpm.
    assert sink_situation(-475.0, heavy=True) is SpecialSituation.MINOR
    assert sink_situation(-550.0, heavy=True) is SpecialSituation.MAJOR
    assert sink_situation(-600.0, heavy=True) is SpecialSituation.HAZARDOUS


def test_touchdown_speed_situation_bands():
    """Норма 0.96·VAPP…VAPP+10; слишком медленно/быстро — СС; ≥ VВПП пред (194) — АС."""
    assert touchdown_speed_situation(140.0, 140.0) is SpecialSituation.NORMAL
    assert touchdown_speed_situation(130.0, 140.0) is SpecialSituation.MAJOR
    assert touchdown_speed_situation(160.0, 140.0) is SpecialSituation.MAJOR
    assert touchdown_speed_situation(200.0, 140.0) is SpecialSituation.HAZARDOUS


def test_load_factor_situation_bands():
    """Нормальная перегрузка касания 2.0 / 2.5 / 3.0; боковая — предел 0.65."""
    assert normal_load_situation(1.5) is SpecialSituation.NORMAL
    assert normal_load_situation(2.3) is SpecialSituation.MINOR
    assert normal_load_situation(2.8) is SpecialSituation.MAJOR
    assert normal_load_situation(3.5) is SpecialSituation.HAZARDOUS
    assert normal_load_situation(2.3, heavy=True) is SpecialSituation.MAJOR
    assert lateral_load_situation(0.4) is SpecialSituation.NORMAL
    assert lateral_load_situation(0.6) is SpecialSituation.MAJOR
    assert lateral_load_situation(0.7) is SpecialSituation.HAZARDOUS


# --------------------------------------------------------------------------- #
# Рантайм-монитор (control/tolerance.py)
# --------------------------------------------------------------------------- #

LIMITS = approach_limits(69277.0, LandingFlapConfiguration.FLAPS_3, 0.32)
# VAPP=140, VSR1=113.6, VFE=183 для этой массы/конфигурации.


def _result(course_deg=0.3, glideslope_deg=0.2) -> ApproachResult:
    res = ApproachResult()
    res.course_deg = course_deg
    res.glideslope_deg = glideslope_deg
    return res


def _telemetry(**overrides) -> Telemetry:
    base = dict(IndicatedAirspeed=140.0, LateralDeviation=2.0, RunwayWidth=60.0)
    base.update(overrides)
    return Telemetry.from_ics(airborne_inputs(**base))


def test_within_tolerance_allows_landing():
    tel = _telemetry()
    rep = evaluate_approach_tolerances(tel, _result(), LIMITS, tel.faults, at_decision_gate=True)
    assert rep.landing_allowed
    assert rep.violations == ()
    assert rep.situation is SpecialSituation.NORMAL


def test_course_violation_blocks_landing():
    tel = _telemetry()
    rep = evaluate_approach_tolerances(tel, _result(course_deg=1.0), LIMITS, tel.faults,
                                       at_decision_gate=False)
    assert not rep.landing_allowed
    assert "COURSE" in rep.violations


def test_glideslope_tolerance_loosens_with_fault():
    """0.6° вне штатного допуска 0.5°, но в пределах допуска при отказе шасси (0.7°)."""
    healthy = _telemetry()
    rep = evaluate_approach_tolerances(healthy, _result(glideslope_deg=0.6), LIMITS,
                                       healthy.faults, at_decision_gate=False)
    assert not rep.landing_allowed and rep.glideslope_tol_deg == pytest.approx(0.5)

    gear = _telemetry(FaultLeftLandingGear=1)
    rep = evaluate_approach_tolerances(gear, _result(glideslope_deg=0.6), LIMITS, gear.faults,
                                       at_decision_gate=False)
    assert rep.landing_allowed and rep.glideslope_tol_deg == pytest.approx(0.7)

    stab = _telemetry(FaultLeftStab=1)
    rep = evaluate_approach_tolerances(stab, _result(glideslope_deg=0.9), LIMITS, stab.faults,
                                       at_decision_gate=False)
    assert rep.landing_allowed and rep.glideslope_tol_deg == pytest.approx(1.0)


def test_lateral_gate_only_checked_at_decision_height():
    """Ось ± 5 м проверяется только у гейта; выше него боковое отклонение не ограничивается."""
    tel = _telemetry(LateralDeviation=8.0)
    at_gate = evaluate_approach_tolerances(tel, _result(), LIMITS, tel.faults,
                                           at_decision_gate=True)
    assert not at_gate.landing_allowed and "LATERAL" in at_gate.violations

    above = evaluate_approach_tolerances(tel, _result(), LIMITS, tel.faults,
                                         at_decision_gate=False)
    assert above.landing_allowed and above.lateral_ok_at_gate is None


def test_speed_outside_envelope_blocks_landing():
    slow = _telemetry(IndicatedAirspeed=100.0)                # ниже VSR1 (113.6)
    rep = evaluate_approach_tolerances(slow, _result(), LIMITS, slow.faults, at_decision_gate=False)
    assert not rep.landing_allowed and "SPEED" in rep.violations
    assert rep.situation is SpecialSituation.HAZARDOUS

    fast = _telemetry(IndicatedAirspeed=200.0)                # выше VFE (183)
    rep = evaluate_approach_tolerances(fast, _result(), LIMITS, fast.faults, at_decision_gate=False)
    assert not rep.landing_allowed and "SPEED" in rep.violations


def _ground_telemetry(speed_kts: float) -> Telemetry:
    return Telemetry.from_ics(engaged_inputs(GroundSpeed=speed_kts, RunwayWidth=60.0))


def test_ground_xte_limits_follow_segment_and_nws_authority():
    telemetry = _ground_telemetry(80.0)
    nominal = evaluate_ground_tolerances(
        telemetry, FlightSegment.ROLLOUT, xte_m=4.0, heading_error_deg=0.0,
        speed_error_ms=0.0, failures=FailureState())
    nws = evaluate_ground_tolerances(
        telemetry, FlightSegment.ROLLOUT, xte_m=4.0, heading_error_deg=0.0,
        speed_error_ms=0.0, failures=FailureState(steering_eff=0.0))
    taxi = evaluate_ground_tolerances(
        telemetry, FlightSegment.TAXI, xte_m=1.1, heading_error_deg=0.0,
        speed_error_ms=0.0, failures=FailureState())
    taxi_nws = evaluate_ground_tolerances(
        telemetry, FlightSegment.TAXI, xte_m=4.0, heading_error_deg=0.0,
        speed_error_ms=0.0, failures=FailureState(steering_eff=0.0))

    assert nominal.xte_limit_m == 3.0 and nominal.violations == ("XTE",)
    assert nws.xte_limit_m == 5.0 and nws.within_tolerance
    assert taxi.xte_limit_m == 1.0 and taxi.violations == ("XTE",)
    assert taxi_nws.xte_limit_m == 5.0 and taxi_nws.within_tolerance


def test_ground_monitor_classifies_runway_excursion_and_failure_heading():
    failure = FailureState(reverse_left_eff=0.0)
    fast = evaluate_ground_tolerances(
        _ground_telemetry(80.0), FlightSegment.ROLLOUT,
        xte_m=26.0, heading_error_deg=6.0, speed_error_ms=1.0, failures=failure)
    slow = evaluate_ground_tolerances(
        _ground_telemetry(29.0), FlightSegment.ROLLOUT,
        xte_m=0.0, heading_error_deg=6.0, speed_error_ms=0.0, failures=failure)

    assert fast.runway_limit_m == pytest.approx(25.7)
    assert fast.runway_contained is False
    assert fast.situation is SpecialSituation.HAZARDOUS
    assert fast.heading_limit_deg == 5.0 and fast.heading_ok is False
    assert fast.violations == ("XTE", "RUNWAY_BOUNDARY", "HEADING")
    assert slow.heading_limit_deg is None and slow.heading_ok is None
    assert slow.within_tolerance


def test_ground_monitor_rejects_missing_guidance_and_speed_data():
    report = evaluate_ground_tolerances(
        None, FlightSegment.ROLLOUT, xte_m=None, heading_error_deg=None,
        speed_error_ms=None, failures=FailureState(thrust_left_eff=0.0))

    assert report.violations == ("XTE_DATA", "SPEED_DATA", "HEADING_DATA")
    assert not report.within_tolerance
