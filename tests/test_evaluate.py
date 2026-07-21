"""Тесты приёмки по ТЗ (Этап 5): вердикты по пунктам, правило «нет данных = FAIL»,
явная неприменимость, гейт допуска чекпоинта и сравнение с baseline'ами.

Логика вердиктов — чистые функции и тестируется без torch и без X-Plane; сквозные прогоны
используют скриптованный бэкенд из `test_ppo` (импорт внутри тестов, чтобы модуль не
пропускался целиком, когда torch недоступен).
"""

import pytest

from ismpu.config.requirements import (
    XTE_ROLLOUT_MAX_M, XTE_TAXI_MAX_M, XTE_NWS_FAIL_MAX_M, HEADING_FAULT_MAX_DEG,
)
from ismpu.control.failures import FailureMode
from ismpu.envs.scenario import SCENARIO_PRESETS
from ismpu.runtime.evaluate import (
    PASS, FAIL, SKIP, evaluate_tz, verdict_of, admit_checkpoint, render_report,
    compare_policies, run_episode, DefaultGainsPolicy, PresetPolicy,
    MAX_SATURATION_RATIO,
)


# --------------------------------------------------------------------------- #
# Хелперы
# --------------------------------------------------------------------------- #

def _diagnostics(**overrides):
    """Диагностика «чистого» эпизода: все пункты ТЗ выполнены с запасом."""
    base = {
        "samples": 500,
        "xte_rollout_max_m": 1.0,
        "xte_taxi_max_m": 0.4,
        "heading_max_deg": 2.0,
        "final_speed_kts": 8.0,          # эпизод дошёл до руления
        "saturation_ratio": 0.1,
        "shield_fallbacks": 0,
        "rate_p95": {"brake_l": 0.05, "brake_r": 0.05, "rudder": 0.02},
    }
    base.update(overrides)
    return base


def _by_name(criteria, name):
    return next(c for c in criteria if c.name == name)


def _battery(diagnostics_list, *, beats_preset=True):
    """Сводка прогона под одной политикой из списка диагностик."""
    episodes = []
    for i, d in enumerate(diagnostics_list):
        criteria = evaluate_tz(d, SCENARIO_PRESETS["default"])
        episodes.append({
            "scenario_id": f"s{i}", "policy": "test", "steps": 100,
            "total_loss": 1.0, "reward": -1.0, "components": {},
            "diagnostics": d, "criteria": [c.as_dict() for c in criteria],
            "verdict": verdict_of(criteria),
        })
    passed = sum(1 for e in episodes if e["verdict"] == PASS)
    return {
        "policy": "test", "episodes": episodes,
        "pass_count": passed, "episode_count": len(episodes),
        "pass_rate": passed / len(episodes) if episodes else 0.0,
        "mean_total_loss": 1.0, "worst_total_loss": 1.0,
        "beats_default": True, "beats_preset": beats_preset,
    }


# --------------------------------------------------------------------------- #
# Вердикты по пунктам ТЗ
# --------------------------------------------------------------------------- #

def test_clean_episode_passes_every_criterion():
    """Сценарий с отказом реверса — тот, где применимы все три критерия сразу."""
    criteria = evaluate_tz(_diagnostics(), SCENARIO_PRESETS["left_reverse_fail"])
    assert verdict_of(criteria) == PASS
    assert all(c.verdict == PASS for c in criteria)


def test_each_criterion_is_reported_separately():
    """Единый сводный вердикт скрыл бы, какое именно требование нарушено."""
    criteria = evaluate_tz(_diagnostics(xte_rollout_max_m=9.0),
                           SCENARIO_PRESETS["left_reverse_fail"])
    assert _by_name(criteria, "xte_rollout_max").verdict == FAIL
    assert _by_name(criteria, "xte_taxi_max").verdict == PASS
    assert _by_name(criteria, "heading_max").verdict == PASS
    assert verdict_of(criteria) == FAIL      # один провал роняет эпизод


def test_missing_measurement_fails_it_does_not_pass_conditionally():
    """Ключевое правило из tz_compliance_audit.md: отсутствие измерения — это FAIL."""
    criteria = evaluate_tz(_diagnostics(xte_rollout_max_m=None), SCENARIO_PRESETS["default"])
    c = _by_name(criteria, "xte_rollout_max")
    assert c.verdict == FAIL
    assert c.measured is None
    assert "нет измерения" in c.reason


def test_non_finite_measurement_also_fails():
    criteria = evaluate_tz(_diagnostics(heading_max_deg=float("nan")),
                           SCENARIO_PRESETS["left_reverse_fail"])
    assert _by_name(criteria, "heading_max").verdict == FAIL


def test_inapplicable_criterion_is_skipped_with_a_visible_reason():
    """Эпизод не дошёл до руления → допуск ±1 м неприменим. Это SKIP, а не тихий пропуск."""
    criteria = evaluate_tz(_diagnostics(xte_taxi_max_m=None, final_speed_kts=70.0),
                           SCENARIO_PRESETS["default"])
    c = _by_name(criteria, "xte_taxi_max")
    assert c.verdict == SKIP
    assert c.reason      # причина обязана быть указана
    assert verdict_of(criteria) == PASS     # неприменимый критерий не роняет эпизод


def test_no_samples_at_all_fails_rather_than_skips():
    """Пустой эпизод — это отсутствие данных, а не неприменимость требования."""
    empty = _diagnostics(samples=0, xte_rollout_max_m=None, heading_max_deg=None,
                         final_speed_kts=None, xte_taxi_max_m=None)
    criteria = evaluate_tz(empty, SCENARIO_PRESETS["left_reverse_fail"])
    assert _by_name(criteria, "xte_rollout_max").verdict == FAIL
    assert _by_name(criteria, "heading_max").verdict == FAIL
    assert verdict_of(criteria) == FAIL

    # В штатном сценарии курс не нормируется вообще — но осевая линия всё равно FAIL.
    nominal = evaluate_tz(empty, SCENARIO_PRESETS["default"])
    assert _by_name(nominal, "xte_rollout_max").verdict == FAIL
    assert verdict_of(nominal) == FAIL


def test_nws_failure_relaxes_the_rollout_tolerance():
    """При отказе NWS руль мёртв, ось держится дифференциальным торможением → ±5 м (5.1.3.2)."""
    d = _diagnostics(xte_rollout_max_m=4.0)     # вне ±3 м, но внутри ±5 м
    nominal = evaluate_tz(d, SCENARIO_PRESETS["default"])
    nws = evaluate_tz(d, SCENARIO_PRESETS["nws_fail"])

    assert _by_name(nominal, "xte_rollout_max").verdict == FAIL
    assert _by_name(nominal, "xte_rollout_max").limit == XTE_ROLLOUT_MAX_M

    assert _by_name(nws, "xte_rollout_max").verdict == PASS
    assert _by_name(nws, "xte_rollout_max").limit == XTE_NWS_FAIL_MAX_M
    assert "NWS" in _by_name(nws, "xte_rollout_max").tz_ref
    assert FailureMode.NWS_FAIL in SCENARIO_PRESETS["nws_fail"].failures


def test_taxi_tolerance_is_stricter_than_rollout():
    """Одно и то же отклонение проходит на пробеге и валится на рулении (±3 м против ±1 м)."""
    criteria = evaluate_tz(_diagnostics(xte_rollout_max_m=2.0, xte_taxi_max_m=2.0),
                           SCENARIO_PRESETS["default"])
    assert _by_name(criteria, "xte_rollout_max").verdict == PASS
    assert _by_name(criteria, "xte_taxi_max").verdict == FAIL
    assert XTE_TAXI_MAX_M < XTE_ROLLOUT_MAX_M


def test_heading_limit_comes_from_requirements():
    criteria = evaluate_tz(_diagnostics(heading_max_deg=HEADING_FAULT_MAX_DEG + 0.5),
                           SCENARIO_PRESETS["left_reverse_fail"])
    c = _by_name(criteria, "heading_max")
    assert c.limit == HEADING_FAULT_MAX_DEG
    assert c.verdict == FAIL


def test_heading_criterion_applies_only_to_thrust_and_reverse_faults():
    """ТЗ задаёт ±5° в 5.1.3.3 («при нарушении тяги или реверса»). В 5.1.3.1 требования нет.

    Применять гейт к штатному сценарию и ссылаться при этом на 5.1.3.3 — значит цитировать
    заказчику пункт, который к сценарию не относится.
    """
    bad_heading = _diagnostics(heading_max_deg=9.0)

    nominal = _by_name(evaluate_tz(bad_heading, SCENARIO_PRESETS["default"]), "heading_max")
    assert nominal.verdict == SKIP
    assert "5.1.3.1" in nominal.reason

    reverse = _by_name(evaluate_tz(bad_heading, SCENARIO_PRESETS["left_reverse_fail"]),
                       "heading_max")
    assert reverse.verdict == FAIL
    assert reverse.tz_ref == "5.1.3.3"


def test_heading_criterion_records_what_it_measured_against():
    c = _by_name(evaluate_tz(_diagnostics(), SCENARIO_PRESETS["left_reverse_fail"]), "heading_max")
    assert c.evaluation_basis == "runway_relative_true_heading"
    assert c.as_dict()["evaluation_basis"] == "runway_relative_true_heading"


def test_nws_failure_does_not_stack_the_taxi_tolerance():
    """5.1.3.2 разрешает ±5 м «до полной остановки» — значит и на скорости руления.

    Применять поверх этого допуск ±1 м значит требовать строже, чем ТЗ.
    """
    d = _diagnostics(xte_taxi_max_m=3.0)      # вне ±1 м, но внутри послабления ±5 м

    nominal = _by_name(evaluate_tz(d, SCENARIO_PRESETS["default"]), "xte_taxi_max")
    assert nominal.verdict == FAIL

    nws = _by_name(evaluate_tz(d, SCENARIO_PRESETS["nws_fail"]), "xte_taxi_max")
    assert nws.verdict == SKIP
    assert "до полной остановки" in nws.reason
    # ...но послабление ±5 м на пробеге при этом продолжает проверяться
    assert _by_name(evaluate_tz(d, SCENARIO_PRESETS["nws_fail"]),
                    "xte_rollout_max").limit == XTE_NWS_FAIL_MAX_M


# --------------------------------------------------------------------------- #
# Гейт допуска чекпоинта
# --------------------------------------------------------------------------- #

def test_clean_battery_is_admitted():
    result = admit_checkpoint(_battery([_diagnostics(), _diagnostics()]))
    assert result.admitted
    assert result.reasons == []


def test_failed_tz_scenario_blocks_admission():
    result = admit_checkpoint(_battery([_diagnostics(), _diagnostics(xte_rollout_max_m=9.0)]))
    assert not result.admitted
    assert any("провалены сценарии" in r for r in result.reasons)


def test_missing_metric_blocks_admission():
    """Отсутствующая метрика = отказ, а не «нет данных — значит нет проблемы»."""
    result = admit_checkpoint(_battery([_diagnostics(saturation_ratio=None)]))
    assert not result.admitted
    assert any("saturation_ratio" in r for r in result.reasons)


def test_sustained_saturation_blocks_admission_even_when_tz_passes():
    """Формально в допуске, но авторитет исчерпан — режим держится на грани."""
    d = _diagnostics(saturation_ratio=MAX_SATURATION_RATIO + 0.1)
    assert verdict_of(evaluate_tz(d, SCENARIO_PRESETS["default"])) == PASS
    result = admit_checkpoint(_battery([d]))
    assert not result.admitted
    assert any("насыщение" in r for r in result.reasons)


def test_shield_fallback_blocks_admission():
    result = admit_checkpoint(_battery([_diagnostics(shield_fallbacks=2)]))
    assert not result.admitted
    assert any("Shield" in r for r in result.reasons)


def test_not_beating_the_preset_blocks_admission():
    """Если сеть не бьёт классику, она не окупается — выпускать её нечего."""
    result = admit_checkpoint(_battery([_diagnostics()], beats_preset=False))
    assert not result.admitted
    assert any("пресет" in r for r in result.reasons)
    # ...но проверку можно снять явно (напр. для промежуточного SFT-чекпоинта)
    assert admit_checkpoint(_battery([_diagnostics()], beats_preset=False),
                            require_beats_preset=False).admitted


def test_idle_channel_rate_is_not_a_rejection_reason():
    """Канал не двигался за эпизод → p95 = None. Это не дефект."""
    d = _diagnostics(rate_p95={"brake_l": 0.05, "rev_l": None})
    assert admit_checkpoint(_battery([d])).admitted


def test_empty_battery_is_rejected():
    result = admit_checkpoint(_battery([]))
    assert not result.admitted


# --------------------------------------------------------------------------- #
# Отчёт
# --------------------------------------------------------------------------- #

def test_report_shows_failures_and_baseline_comparison():
    """Отрицательный результат должен быть виден в отчёте, а не спрятан."""
    comparison = {
        "scenario_count": 1, "scenarios": ["s0"],
        "policies": {"ppo": _battery([_diagnostics(xte_rollout_max_m=9.0)],
                                     beats_preset=False)},
        "baselines": {"default": 2.0, "preset": 0.5},
    }
    admission = admit_checkpoint(comparison["policies"]["ppo"]).as_dict()
    text = render_report(comparison, admission)

    assert "FAIL" in text
    assert "xte_rollout_max" in text
    assert "5.1.3.1" in text
    assert "НЕ ДОПУЩЕН" in text
    assert "**нет**" in text          # «лучше пресета: нет» выделено


# --------------------------------------------------------------------------- #
# Сквозные прогоны на скриптованном бэкенде
# --------------------------------------------------------------------------- #

def _scripted_env(window=4):
    pytest.importorskip("torch")     # ScriptedBackend живёт в модуле с torch-зависимостью
    from test_ppo import ScriptedBackend
    from ismpu.control.system import ControllingSystem
    from ismpu.envs.rollout_env import RolloutEnv
    sim = ScriptedBackend()
    ctrl = ControllingSystem(sim)
    return RolloutEnv(sim, ctrl, history_len=window, shield=None)


def test_run_episode_produces_criteria_and_diagnostics():
    env = _scripted_env()
    result = run_episode(env, SCENARIO_PRESETS["default"], PresetPolicy(), max_steps=400)

    assert result["policy"] == "scenario_preset"
    assert result["verdict"] in (PASS, FAIL)
    assert result["steps"] > 0
    assert {c["name"] for c in result["criteria"]} == {
        "xte_rollout_max", "xte_taxi_max", "heading_max"}
    # objective посчитан из тех же отсчётов, что и reward
    assert result["diagnostics"]["samples"] == result["steps"]
    assert result["total_loss"] == pytest.approx(-result["reward"])


def test_compare_policies_flags_which_baseline_each_policy_beats():
    env = _scripted_env()
    scenarios = [SCENARIO_PRESETS["default"], SCENARIO_PRESETS["nws_fail"]]
    comparison = compare_policies(env, scenarios,
                                  [DefaultGainsPolicy(), PresetPolicy()],
                                  max_steps=300, log=None)

    assert comparison["scenario_count"] == 2
    assert set(comparison["policies"]) == {"default_gains", "scenario_preset"}
    for r in comparison["policies"].values():
        assert r["episode_count"] == 2
        assert r["beats_default"] is not None
        assert r["beats_preset"] is not None
    # Пресет сам себе baseline → не «бьёт» сам себя.
    assert comparison["policies"]["scenario_preset"]["beats_preset"] is False
    assert comparison["baselines"]["preset"] is not None
