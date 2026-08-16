"""Регрессии чистых вердиктов ТЗ: пределы, применимость и отсутствие данных."""

from ismpu.config.requirements import (
    HEADING_FAULT_MAX_DEG,
    XTE_NWS_FAIL_MAX_M,
    XTE_ROLLOUT_MAX_M,
    XTE_TAXI_MAX_M,
)
from ismpu.config.scenarios import SCENARIOS
from ismpu.control.failures import FailureMode
from ismpu.runtime.evaluate import FAIL, PASS, SKIP, evaluate_tz, verdict_of


def _diagnostics(**overrides):
    """Вернуть полный штатный набор метрик с запасом до каждого допуска."""
    values = {
        "samples": 500,
        "xte_rollout_max_m": 1.0,
        "xte_taxi_max_m": 0.4,
        "heading_max_deg": 2.0,
        "final_speed_kts": 8.0,
    }
    values.update(overrides)
    return values


def _by_name(criteria, name):
    """Найти один именованный критерий и сделать дубликат заметным в тесте."""
    matches = [item for item in criteria if item.name == name]
    assert len(matches) == 1
    return matches[0]


def test_clean_episode_passes_every_criterion():
    criteria = evaluate_tz(_diagnostics(), SCENARIOS["left_reverse_fail"])
    assert verdict_of(criteria) == PASS
    assert all(item.verdict == PASS for item in criteria)


def test_each_criterion_is_reported_separately():
    criteria = evaluate_tz(
        _diagnostics(xte_rollout_max_m=9.0), SCENARIOS["left_reverse_fail"]
    )
    assert _by_name(criteria, "xte_rollout_max").verdict == FAIL
    assert _by_name(criteria, "xte_taxi_max").verdict == PASS
    assert _by_name(criteria, "heading_max").verdict == PASS
    assert verdict_of(criteria) == FAIL


def test_missing_measurement_fails_it_does_not_pass_conditionally():
    criterion = _by_name(
        evaluate_tz(
            _diagnostics(xte_rollout_max_m=None), SCENARIOS["default"]
        ),
        "xte_rollout_max",
    )
    assert criterion.verdict == FAIL
    assert criterion.measured is None
    assert "нет измерения" in criterion.reason


def test_non_finite_measurement_also_fails():
    criteria = evaluate_tz(
        _diagnostics(heading_max_deg=float("nan")), SCENARIOS["left_reverse_fail"]
    )
    assert _by_name(criteria, "heading_max").verdict == FAIL


def test_inapplicable_criterion_is_skipped_with_a_visible_reason():
    criteria = evaluate_tz(
        _diagnostics(xte_taxi_max_m=None, final_speed_kts=70.0),
        SCENARIOS["default"],
    )
    criterion = _by_name(criteria, "xte_taxi_max")
    assert criterion.verdict == SKIP
    assert criterion.reason
    assert verdict_of(criteria) == PASS


def test_no_samples_at_all_fails_rather_than_skips():
    empty = _diagnostics(
        samples=0,
        xte_rollout_max_m=None,
        heading_max_deg=None,
        final_speed_kts=None,
        xte_taxi_max_m=None,
    )
    failed = evaluate_tz(empty, SCENARIOS["left_reverse_fail"])
    assert _by_name(failed, "xte_rollout_max").verdict == FAIL
    assert _by_name(failed, "heading_max").verdict == FAIL
    assert verdict_of(failed) == FAIL

    nominal = evaluate_tz(empty, SCENARIOS["default"])
    assert _by_name(nominal, "xte_rollout_max").verdict == FAIL
    assert verdict_of(nominal) == FAIL


def test_nws_failure_relaxes_the_rollout_tolerance():
    diagnostics = _diagnostics(xte_rollout_max_m=4.0)
    nominal = evaluate_tz(diagnostics, SCENARIOS["default"])
    nws = evaluate_tz(diagnostics, SCENARIOS["nws_fail"])

    assert _by_name(nominal, "xte_rollout_max").verdict == FAIL
    assert _by_name(nominal, "xte_rollout_max").limit == XTE_ROLLOUT_MAX_M
    assert _by_name(nws, "xte_rollout_max").verdict == PASS
    assert _by_name(nws, "xte_rollout_max").limit == XTE_NWS_FAIL_MAX_M
    assert FailureMode.NWS_FAIL in SCENARIOS["nws_fail"].failures


def test_taxi_tolerance_is_stricter_than_rollout():
    criteria = evaluate_tz(
        _diagnostics(xte_rollout_max_m=2.0, xte_taxi_max_m=2.0),
        SCENARIOS["default"],
    )
    assert _by_name(criteria, "xte_rollout_max").verdict == PASS
    assert _by_name(criteria, "xte_taxi_max").verdict == FAIL
    assert XTE_TAXI_MAX_M < XTE_ROLLOUT_MAX_M


def test_heading_limit_comes_from_requirements():
    criteria = evaluate_tz(
        _diagnostics(heading_max_deg=HEADING_FAULT_MAX_DEG + 0.5),
        SCENARIOS["left_reverse_fail"],
    )
    criterion = _by_name(criteria, "heading_max")
    assert criterion.limit == HEADING_FAULT_MAX_DEG
    assert criterion.verdict == FAIL


def test_heading_criterion_applies_only_to_thrust_and_reverse_faults():
    diagnostics = _diagnostics(heading_max_deg=9.0)
    nominal = _by_name(
        evaluate_tz(diagnostics, SCENARIOS["default"]), "heading_max"
    )
    reverse = _by_name(
        evaluate_tz(diagnostics, SCENARIOS["left_reverse_fail"]), "heading_max"
    )
    assert nominal.verdict == SKIP
    assert "5.1.3.1" in nominal.reason
    assert reverse.verdict == FAIL
    assert reverse.tz_ref == "5.1.3.3"


def test_heading_criterion_records_measurement_basis():
    criterion = _by_name(
        evaluate_tz(_diagnostics(), SCENARIOS["left_reverse_fail"]),
        "heading_max",
    )
    assert criterion.evaluation_basis == "runway_relative_true_heading"
    assert criterion.as_dict()["evaluation_basis"] == "runway_relative_true_heading"


def test_nws_failure_does_not_stack_the_taxi_tolerance():
    diagnostics = _diagnostics(xte_taxi_max_m=3.0)
    nominal = _by_name(
        evaluate_tz(diagnostics, SCENARIOS["default"]), "xte_taxi_max"
    )
    nws = _by_name(
        evaluate_tz(diagnostics, SCENARIOS["nws_fail"]), "xte_taxi_max"
    )
    assert nominal.verdict == FAIL
    assert nws.verdict == SKIP
    assert "до полной остановки" in nws.reason
    assert _by_name(
        evaluate_tz(diagnostics, SCENARIOS["nws_fail"]), "xte_rollout_max"
    ).limit == XTE_NWS_FAIL_MAX_M
