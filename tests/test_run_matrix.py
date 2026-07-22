"""Матрица прогонов: сверка с таблицей Заказчика и подключение к запуску и SFT."""

import pytest

from ismpu.config.approach import APPROACH_PRESETS, APPROACH_DEFAULT
from ismpu.config.run_matrix import (
    RUN_MATRIX, APPROACH_CASES, GROUND_CASES, APPROACH_CONDITIONS, GROUND_CONDITIONS,
    CASE_BY_CODE, CASE_BY_PRESET, TOTAL_RUNS, ground_cases, cases_for_segment,
)
from ismpu.config.scenarios import SCENARIOS
from ismpu.control.failures import FailureMode
from ismpu.control.system import ControllingSystem
from ismpu.envs.scenario import SCENARIO_PRESETS, resolve_preset, matrix_battery, select_scenario
from ismpu.config.runway import RWY_HEADING_TRUE
from ismpu.envs.weather import decompose_wind
from ismpu.runtime.pretrain import (
    PretrainRunConfig, build_scenarios, matrix_preset_names,
)


# --------------------------------------------------------------------------- #
# Сверка с таблицей
# --------------------------------------------------------------------------- #

def test_matrix_totals_match_the_customer_spreadsheet():
    """22 шифра, 156 + 124 = 280 прогонов — итоги с листа «Легенда»."""
    assert len(RUN_MATRIX) == 22
    assert len(APPROACH_CASES) == 12 and len(GROUND_CASES) == 10
    assert sum(c.runs for c in APPROACH_CASES) == 156
    assert sum(c.runs for c in GROUND_CASES) == 124
    assert TOTAL_RUNS == 280


def test_condition_catalogue_sizes():
    """13 условий у захода (П.1–П.5) и 15 у ВПП (У.1–У.8) — по строкам справочника."""
    assert len(APPROACH_CONDITIONS) == 13
    assert len(GROUND_CONDITIONS) == 15


def test_taxi_skips_the_aquaplaning_condition():
    """«Слой воды 5 мм … для руления не применяется» — прямая оговорка справочника."""
    taxi = CASE_BY_CODE["Б.1.2"]
    assert taxi.runs == 14
    assert all(c.code != "У.7" for c in taxi.conditions)


def test_crosswind_conditions_carry_the_side_they_claim():
    """«Слева» и «справа» должны давать боковую составляющую разного знака.

    Ветер в `WeatherState` хранится скоростью и направлением, и перепутанный знак здесь не
    заметен глазом — он всплыл бы только тем, что пресет подбирается под зеркальные условия.
    """
    left = next(c for c in GROUND_CONDITIONS if c.code == "У.2-L10")
    right = next(c for c in GROUND_CONDITIONS if c.code == "У.2-R10")
    cross_l, _ = decompose_wind(left.weather.wind_speed_kts, left.weather.wind_dir_from_degt,
                                RWY_HEADING_TRUE)
    cross_r, _ = decompose_wind(right.weather.wind_speed_kts, right.weather.wind_dir_from_degt,
                                RWY_HEADING_TRUE)
    assert cross_l < 0.0 < cross_r
    assert cross_r == pytest.approx(-cross_l, abs=1e-6)
    assert cross_r == pytest.approx(10.0 * 1.94384449244, abs=1e-3)   # 10 м/с в узлах


def test_headwind_and_tailwind_have_opposite_signs():
    head = next(c for c in APPROACH_CONDITIONS if c.code == "П.4-H")
    tail = next(c for c in APPROACH_CONDITIONS if c.code == "П.4-T")
    _, h = decompose_wind(head.weather.wind_speed_kts, head.weather.wind_dir_from_degt,
                          RWY_HEADING_TRUE)
    _, t = decompose_wind(tail.weather.wind_speed_kts, tail.weather.wind_dir_from_degt,
                          RWY_HEADING_TRUE)
    assert h > 0.0 > t


def test_low_visibility_conditions_are_rvr_300():
    for code in ("П.5", "У.8"):
        cond = next(c for c in APPROACH_CONDITIONS + GROUND_CONDITIONS if c.code == code)
        assert cond.weather.visibility_m == pytest.approx(300.0)


# --------------------------------------------------------------------------- #
# Что телеметрия не различает
# --------------------------------------------------------------------------- #

def test_ambiguous_cases_really_share_their_bench_faults():
    """Пометка «неотличимы» должна опираться на факт, а не на комментарий.

    Если два шифра объявлены неразличимыми, их набор отказов в телеметрии обязан совпадать —
    иначе пометка вводит в заблуждение и мешает там, где автоподбор как раз сработал бы.
    """
    for case in RUN_MATRIX:
        for other_code in case.ambiguous_with:
            other = CASE_BY_CODE[other_code]
            assert set(case.bench_faults) == set(other.bench_faults), (
                f"{case.code} и {other_code} объявлены неотличимыми, но отказы разные")


def test_nose_gear_variants_are_indistinguishable_by_telemetry():
    """`FaultNWS` — один байт: заедание в нейтрали, с уводом и ограничение диапазона равны."""
    codes = ("Б.2.1", "Б.2.2", "Б.2.3")
    faults = {CASE_BY_CODE[c].bench_faults for c in codes}
    assert faults == {(FailureMode.NWS_FAIL,)}
    for code in codes:
        assert set(CASE_BY_CODE[code].ambiguous_with) == set(codes) - {code}


# --------------------------------------------------------------------------- #
# Пресеты
# --------------------------------------------------------------------------- #

def test_every_case_has_a_preset():
    for case in RUN_MATRIX:
        assert case.preset in SCENARIOS, f"{case.code}: нет пресета {case.preset}"
        assert SCENARIOS[case.preset].matrix_code == case.code


def test_all_matrix_presets_are_drafts():
    """Заготовки под настройку. Ни один не должен выглядеть откалиброванным."""
    for case in RUN_MATRIX:
        assert SCENARIOS[case.preset].draft is True


def test_drafts_are_never_selected_automatically():
    """Автоподбор берёт только выверенные пресеты — иначе пробег пойдёт на непроверенных."""
    chosen = select_scenario(failures=(FailureMode.NWS_FAIL,))
    assert chosen.control.draft is False
    assert chosen.scenario_id == "nws_fail"


def test_approach_cases_point_at_their_own_airborne_preset():
    """Шифр захода настраивает воздушный контур, поэтому и пресет захода у него свой."""
    for case in cases_for_segment("approach"):
        assert SCENARIOS[case.preset].approach == case.preset
        assert case.preset in APPROACH_PRESETS
        assert APPROACH_PRESETS[case.preset].draft is True


def test_ground_cases_keep_the_confirmed_airborne_settings():
    """Наземные шифры воздушный контур не трогают — кроме сквозных, где заход часть прогона."""
    for case in cases_for_segment("rollout") + cases_for_segment("taxi"):
        assert SCENARIOS[case.preset].approach == "default"
    assert SCENARIOS["b_4_1_through"].approach == "a_1_2_flare"
    assert SCENARIOS["b_4_2_through_engine_out"].approach == "a_4_1_engine_out_high"


def test_draft_presets_do_not_share_gain_dictionaries_with_their_parent():
    """Словари копируются: иначе настройка черновика молча меняла бы родителя."""
    parent = SCENARIOS["nws_fail"]
    draft = SCENARIOS["b_2_1_nws_stuck_neutral"]
    assert draft.runway_center == parent.runway_center
    assert draft.runway_center is not parent.runway_center
    assert draft.brake_l is not parent.brake_l


def test_applying_a_matrix_preset_sets_up_both_segments():
    """Сквозной шифр обязан настроить и пробег, и заход — иначе отказ на глиссаде не покрыт."""
    controller = ControllingSystem()
    SCENARIO_PRESETS["b_4_2_through_engine_out"].apply_control(controller)
    assert controller.approach_channel.config.name == "a_4_1_engine_out_high"
    assert set(controller.pids) == {"runway_center_pid", "pid_brake_l", "pid_brake_r",
                                    "pid_rev_l", "pid_rev_r"}


def test_setup_approach_rebuilds_the_regulators():
    """Пересборка, а не переписывание: интеграл прошлого захода в новый переносить нельзя."""
    controller = ControllingSystem()
    first = controller.approach_channel
    controller.approach_channel.pitch_pid.integral = 3.0
    second = controller.setup_approach(APPROACH_DEFAULT)
    assert second is not first
    assert second.pitch_pid.integral == 0.0


# --------------------------------------------------------------------------- #
# Ручной запуск и SFT
# --------------------------------------------------------------------------- #

def test_presets_resolve_by_matrix_code_in_either_alphabet():
    """Исполнитель за пультом оперирует шифром, а не именем переменной."""
    assert resolve_preset("Б.3.1").scenario_id == "b_3_1_reverse_left_fail"
    assert resolve_preset("б.3.1").scenario_id == "b_3_1_reverse_left_fail"
    assert resolve_preset("B.3.1").scenario_id == "b_3_1_reverse_left_fail"   # латиница
    assert resolve_preset("А.1.2").scenario_id == "a_1_2_flare"
    assert resolve_preset("a.1.2").scenario_id == "a_1_2_flare"
    assert resolve_preset("default").scenario_id == "default"
    with pytest.raises(KeyError):
        resolve_preset("Ж.9.9")


def test_matrix_battery_follows_the_table_order():
    """Матрица предписывает идти сверху вниз: настройка предыдущего — вход следующего."""
    battery = matrix_battery()
    assert [s.control.matrix_code for s in battery] == [c.code for c in RUN_MATRIX]
    assert [s.control.matrix_code for s in matrix_battery("taxi")] == ["Б.1.2"]


def test_sft_skips_uncalibrated_presets_by_default(capsys):
    """Метка SFT — коэффициенты пресета. У черновика их ещё нет, учить на них нечему."""
    cfg = PretrainRunConfig(variants_per_preset=1)
    scenarios = build_scenarios(cfg)
    assert scenarios, "должны остаться откалиброванные пресеты"
    assert all(not s.control.draft for s in scenarios)
    assert "пропущены неоткалиброванные" in capsys.readouterr().out


def test_sft_can_be_pointed_at_named_presets(capsys):
    """Матрица настраивается по частям — доснять один шифр должно быть дешевле полного SFT."""
    cfg = PretrainRunConfig(variants_per_preset=2, presets=("default", "nws_fail"))
    scenarios = build_scenarios(cfg)
    assert {s.control.name for s in scenarios} == {"default", "nws_fail"}
    assert len(scenarios) == 4


def test_including_drafts_in_sft_is_loud(capsys):
    """Осознанное включение черновика возможно, но молчаливым быть не должно."""
    cfg = PretrainRunConfig(variants_per_preset=1, presets=("b_1_1_rollout",),
                            include_drafts=True)
    scenarios = build_scenarios(cfg)
    assert [s.control.name for s in scenarios] == ["b_1_1_rollout"]
    assert "ВНИМАНИЕ" in capsys.readouterr().out


def test_sft_refuses_unknown_presets():
    with pytest.raises(KeyError):
        build_scenarios(PretrainRunConfig(presets=("нет_такого",)))


def test_matrix_preset_names_lists_only_ground_segments():
    """Заход в SFT не идёт: обучаемый слой планирует коэффициенты пробега, а не захода."""
    names = matrix_preset_names(only_calibrated=False)
    assert names == tuple(c.preset for c in ground_cases())
    assert all(not n.startswith("a_") for n in names)
    # Пока ни один шифр не настроен — список откалиброванных пуст, и это честно.
    assert matrix_preset_names() == ()
