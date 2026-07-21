"""Разбиение train/holdout и контракт воспроизводимости (шаг 6).

Два свойства, ради которых всё это делается:
* разбиение **устойчиво к добавлению** новых сценариев (иначе результаты приёмки не
  сравниваются между прогонами);
* стохастика X-Plane названа поимённо и превращается в требование реплик (иначе один прогон
  при болтанке выдаётся за доказательство).
"""

import pytest

from ismpu.control.failures import FailureMode
from ismpu.envs.scenario import Scenario, SCENARIO_PRESETS
from ismpu.envs.scenario_generator import ScenarioGenerator
from ismpu.envs.weather import WeatherState, WEATHER_PRESETS
from ismpu.config.scenarios import SCENARIOS
from ismpu.envs.splits import (
    split_scenarios, holdout_reason, is_marked_holdout, has_holdout_failure,
    assert_no_leakage, _hash_unit, HOLDOUT_FAILURE_FAMILIES, DEFAULT_HOLDOUT_FRACTION,
)
from ismpu.envs.reproducibility import (
    contract_for, required_replicas, stochastic_sources, worst_replica,
    XPLANE_NATIVE_TURBULENCE, XPLANE_NATIVE_GUST, XPLANE_WIND_VARIABILITY,
    DEFAULT_MIN_REPLICAS,
)


def _scenario(sid, *, failures=(), weather=None):
    return Scenario(scenario_id=sid, seed=0, control=SCENARIOS["default"],
                    weather=weather or WEATHER_PRESETS["clear_dry"],
                    failures=tuple(failures))


# --------------------------------------------------------------------------- #
# Хеш-основа
# --------------------------------------------------------------------------- #

def test_hash_is_stable_and_in_range():
    """SHA-256, а не встроенный hash(): последний рандомизирован солью процесса."""
    assert _hash_unit("nominal") == _hash_unit("nominal")
    assert 0.0 <= _hash_unit("whatever") < 1.0
    assert _hash_unit("a") != _hash_unit("b")


def test_hash_matches_a_known_value():
    """Пин на конкретное значение: смена алгоритма перетасовала бы всё разбиение молча."""
    import hashlib
    digest = hashlib.sha256(b"nominal").digest()
    assert _hash_unit("nominal") == pytest.approx(
        int.from_bytes(digest[:8], "big") / float(1 << 64))


# --------------------------------------------------------------------------- #
# Причины попадания в holdout
# --------------------------------------------------------------------------- #

def test_marker_in_the_name_forces_holdout():
    assert is_marked_holdout("nws_holdout")
    assert is_marked_holdout("UNSEEN_combo")       # регистр не важен
    assert not is_marked_holdout("nominal")
    assert holdout_reason(_scenario("wet_holdout")) == "marker"


def test_reserved_failure_families_never_reach_training():
    """Отказы без своего откалиброванного пресета — единственное место, где виден перенос."""
    for failure in HOLDOUT_FAILURE_FAMILIES:
        scenario = _scenario(f"case_{failure.name}", failures=(failure,))
        assert has_holdout_failure(scenario)
        assert holdout_reason(scenario) == "reserved_failure_family"

    # А отказы со своим пресетом остаются в обучении.
    assert not has_holdout_failure(_scenario("nws", failures=(FailureMode.NWS_FAIL,)))


def test_hash_topup_reaches_the_requested_fraction():
    scenarios = [_scenario(f"gen-{i:04d}") for i in range(400)]
    split = split_scenarios(scenarios, fraction=0.2)
    assert 0.15 < split.holdout_fraction < 0.25       # хеш равномерен, но не идеален
    assert all(r == "hash_topup" for r in split.reasons.values())


def test_every_holdout_entry_carries_a_named_reason():
    scenarios = [_scenario("nominal"), _scenario("x_holdout"),
                 _scenario("eng", failures=(FailureMode.ENGINE_OUT_LEFT,))]
    split = split_scenarios(scenarios)
    for scenario in split.holdout:
        assert split.reasons[scenario.scenario_id] in {
            "marker", "reserved_failure_family", "hash_topup"}


# --------------------------------------------------------------------------- #
# Ключевое свойство: устойчивость к добавлению
# --------------------------------------------------------------------------- #

def test_adding_scenarios_does_not_reshuffle_existing_assignments():
    """Ради этого хеш и выбран вместо shuffle(seed): иначе новый сценарий менял бы разбиение
    целиком, и приёмка переставала бы сравниваться между прогонами."""
    original = [_scenario(f"gen-{i:04d}") for i in range(50)]
    first = split_scenarios(original)
    before = {s.scenario_id: "holdout" for s in first.holdout}
    before.update({s.scenario_id: "train" for s in first.train})

    extended = original + [_scenario(f"gen-{i:04d}") for i in range(50, 120)]
    second = split_scenarios(extended)
    after = {s.scenario_id: "holdout" for s in second.holdout}
    after.update({s.scenario_id: "train" for s in second.train})

    for scenario_id, assignment in before.items():
        assert after[scenario_id] == assignment


def test_split_is_deterministic_across_calls_and_order():
    scenarios = [_scenario(f"gen-{i:04d}") for i in range(60)]
    a = split_scenarios(scenarios)
    b = split_scenarios(list(reversed(scenarios)))
    assert ({s.scenario_id for s in a.holdout} == {s.scenario_id for s in b.holdout})


def test_split_rejects_an_invalid_fraction():
    with pytest.raises(ValueError, match="fraction"):
        split_scenarios([_scenario("a")], fraction=1.5)


# --------------------------------------------------------------------------- #
# Защита от утечки
# --------------------------------------------------------------------------- #

def test_leakage_check_passes_on_a_clean_split():
    split = split_scenarios(ScenarioGenerator(seed=0).battery())
    assert_no_leakage(split)


def test_leakage_check_catches_a_duplicated_scenario():
    split = split_scenarios([_scenario("nominal"), _scenario("x_holdout")])
    split.train.append(split.holdout[0])          # тот же сценарий в обеих частях
    with pytest.raises(ValueError, match="утечка"):
        assert_no_leakage(split)


def test_leakage_check_catches_a_reserved_family_in_training():
    split = split_scenarios([_scenario("nominal")])
    split.train.append(_scenario("smuggled", failures=(FailureMode.ENGINE_OUT_LEFT,)))
    with pytest.raises(ValueError, match="семейство отказов"):
        assert_no_leakage(split)


def test_acceptance_battery_reserves_the_engine_failure_case():
    """В приёмочном наборе отказ двигателя обязан оказаться в holdout."""
    split = split_scenarios(ScenarioGenerator(seed=0).battery())
    holdout_ids = {s.scenario_id for s in split.holdout}
    assert "engine_out_left" in holdout_ids
    assert split.reasons["engine_out_left"] == "reserved_failure_family"
    assert split.train      # обучающая часть не пуста


# --------------------------------------------------------------------------- #
# Контракт воспроизводимости
# --------------------------------------------------------------------------- #

def test_calm_weather_is_bit_reproducible():
    contract = contract_for(_scenario("nominal", weather=WEATHER_PRESETS["clear_dry"]))
    assert contract.external_stochastic_sources == ()
    assert contract.bit_reproducible
    assert contract.replica_validation_required is False
    assert contract.min_replicas == 1


def test_turbulence_makes_the_episode_non_reproducible():
    """Сид у нас, реализация болтанки — у X-Plane. Значит один прогон ничего не доказывает."""
    weather = WeatherState(turbulence=4.0)
    contract = contract_for(_scenario("bumpy", weather=weather))
    assert XPLANE_NATIVE_TURBULENCE in contract.external_stochastic_sources
    assert contract.replica_validation_required is True
    assert not contract.bit_reproducible
    assert contract.min_replicas == DEFAULT_MIN_REPLICAS


def test_each_stochastic_source_is_named_separately():
    assert stochastic_sources(WeatherState(gust_kts=10.0)) == (XPLANE_NATIVE_GUST,)
    assert stochastic_sources(WeatherState(variability_pct=0.5)) == (XPLANE_WIND_VARIABILITY,)
    combined = stochastic_sources(WeatherState(turbulence=1.0, gust_kts=5.0, variability_pct=0.3))
    assert set(combined) == {XPLANE_NATIVE_TURBULENCE, XPLANE_NATIVE_GUST, XPLANE_WIND_VARIABILITY}


def test_gusty_preset_requires_replicas():
    assert required_replicas(_scenario("g", weather=WEATHER_PRESETS["gusty_crosswind"])) > 1
    assert required_replicas(_scenario("c", weather=WEATHER_PRESETS["clear_dry"])) == 1


def test_contract_records_the_deterministic_inputs():
    scenario = SCENARIO_PRESETS["nws_fail"]
    contract = contract_for(scenario)
    assert contract.deterministic_inputs["control_preset"] == scenario.control.name
    assert "NWS_FAIL" in contract.deterministic_inputs["failures"]
    assert contract.as_dict()["scenario_id"] == scenario.scenario_id


def test_worst_replica_is_taken_not_the_average():
    """ТЗ задаёт пределы как границы — усреднение прятало бы единичный выход за допуск."""
    results = [{"total_loss": 1.0}, {"total_loss": 9.0}, {"total_loss": 2.0}]
    assert worst_replica(results)["total_loss"] == 9.0
    assert worst_replica([]) is None
    assert worst_replica([{"total_loss": None}]) is None
