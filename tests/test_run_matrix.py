"""Матрица прогонов и её связь с единым реестром сценариев."""

import pytest

from ismpu.config.approach import (
    APPROACH_CONFIGS,
    APPROACH_DEFAULT,
    ICS_CLEAR_WEATHER_APPROACH,
)
from ismpu.config.run_matrix import (
    RUN_MATRIX, APPROACH_CASES, GROUND_CASES, APPROACH_CONDITIONS,
    GROUND_CONDITIONS, CASE_BY_CODE, TOTAL_RUNS, ground_cases,
)
from ismpu.config.scenarios import (
    SCENARIOS,
    compose_matrix_scenario,
    matrix_battery,
    resolve_scenario,
    select_scenario,
)
from ismpu.config.segments import FlightSegment
from ismpu.control.failures import FailureMode
from ismpu.control.system import ControllingSystem
from ismpu.runtime.pretrain import PretrainRunConfig, build_scenarios, matrix_preset_names


def test_matrix_totals_match_the_customer_spreadsheet():
    assert len(RUN_MATRIX) == 22
    assert len(APPROACH_CASES) == 12 and len(GROUND_CASES) == 10
    assert sum(case.runs for case in APPROACH_CASES) == 156
    assert sum(case.runs for case in GROUND_CASES) == 124
    assert TOTAL_RUNS == 280
    assert len(APPROACH_CONDITIONS) == 13
    assert len(GROUND_CONDITIONS) == 15


def test_taxi_skips_the_aquaplaning_condition():
    taxi = CASE_BY_CODE["Б.1.2"]
    assert taxi.runs == 14
    assert all(condition.code != "У.7" for condition in taxi.conditions)


def test_every_case_has_one_full_scenario_and_correct_phase_admission():
    for case in APPROACH_CASES:
        scenario = SCENARIOS[case.preset]
        assert scenario.matrix_codes[FlightSegment.APPROACH] == case.code
        assert not scenario.is_draft("mc21", FlightSegment.APPROACH)
        assert scenario.control_for("mc21", FlightSegment.ROLLOUT)
        expected_failures = frozenset(case.bench_faults)
        assert all(
            scenario.conditions_for(segment).failures == expected_failures
            for segment in FlightSegment
        )

    for case in GROUND_CASES:
        scenario = SCENARIOS[case.preset]
        segment = (
            FlightSegment.TAXI if case.segment == "taxi" else FlightSegment.ROLLOUT)
        assert scenario.matrix_codes[segment] == case.code
        assert scenario.is_draft("mc21", segment)
        if case.segment == "through":
            assert scenario.matrix_codes[FlightSegment.APPROACH] == case.code
            assert not scenario.is_draft("mc21", FlightSegment.APPROACH)


def test_all_approach_cases_use_the_single_working_ics_control_config():
    assert APPROACH_CONFIGS == {
        "ics_clear_weather": ICS_CLEAR_WEATHER_APPROACH,
    }
    for case in APPROACH_CASES:
        config = SCENARIOS[case.preset].control_for("mc21", FlightSegment.APPROACH)
        assert config.name == "ics_clear_weather"
        assert config is not ICS_CLEAR_WEATHER_APPROACH
        assert config.roll_pid == ICS_CLEAR_WEATHER_APPROACH.roll_pid
        assert config.pitch_pid == ICS_CLEAR_WEATHER_APPROACH.pitch_pid
        assert config.speed_pid == ICS_CLEAR_WEATHER_APPROACH.speed_pid
        assert not config.draft


def test_compose_matrix_scenario_combines_air_and_ground_control_and_failures():
    scenario = compose_matrix_scenario(
        "a41-b31",
        approach_case=CASE_BY_CODE["А.4.1"],
        ground_case=CASE_BY_CODE["Б.3.1"],
    )
    assert scenario.control_for(
        "mc21", FlightSegment.APPROACH).name == "ics_clear_weather"
    assert scenario.control_for(
        "mc21", FlightSegment.ROLLOUT).rev_l == \
        SCENARIOS["b_3_1_reverse_left_fail"].control_for(
            "mc21", FlightSegment.ROLLOUT).rev_l
    assert scenario.conditions_for(FlightSegment.APPROACH).failures == frozenset({
        FailureMode.ENGINE_OUT_LEFT,
    })
    assert scenario.conditions_for(FlightSegment.ROLLOUT).failures == frozenset({
        FailureMode.ENGINE_OUT_LEFT,
        FailureMode.REVERSE_LEFT_FAIL,
    })
    assert scenario.provenance[FlightSegment.APPROACH] == "a_4_1_engine_out_high"
    assert scenario.provenance[FlightSegment.ROLLOUT] == "b_3_1_reverse_left_fail"


def test_drafts_are_never_selected_automatically():
    selected = select_scenario(
        (FailureMode.NWS_FAIL,), aircraft_profile="mc21",
        segment=FlightSegment.ROLLOUT,
    )
    assert selected.scenario_id == "nws_fail"
    assert not selected.is_draft("mc21", FlightSegment.ROLLOUT)


def test_b42_has_phase_specific_engine_and_reverse_failures():
    scenario = SCENARIOS["b_4_2_through_engine_out"]
    assert scenario.conditions_for(FlightSegment.APPROACH).failures == frozenset({
        FailureMode.ENGINE_OUT_LEFT,
    })
    assert scenario.conditions_for(FlightSegment.ROLLOUT).failures == frozenset({
        FailureMode.ENGINE_OUT_LEFT, FailureMode.REVERSE_LEFT_FAIL,
    })


def test_applying_each_b42_segment_rebuilds_the_relevant_pids():
    controller = ControllingSystem()
    scenario = SCENARIOS["b_4_2_through_engine_out"]
    scenario.apply_control(controller, "mc21", FlightSegment.APPROACH)
    assert controller.approach_channel.config.name == "ics_clear_weather"
    first = controller.approach_channel
    scenario.apply_control(controller, "mc21", FlightSegment.APPROACH)
    assert controller.approach_channel is not first
    scenario.apply_control(controller, "mc21", FlightSegment.ROLLOUT)
    assert set(controller.pids) == {
        "runway_center_pid", "pid_brake_l", "pid_brake_r", "pid_rev_l", "pid_rev_r",
    }


def test_approach_setup_rebuilds_regulators():
    controller = ControllingSystem()
    first = controller.approach_channel
    controller.approach_channel.pitch_pid.integral = 3.0
    second = controller.setup_approach(APPROACH_DEFAULT)
    assert second is not first
    assert second.pitch_pid.integral == 0.0


def test_scenarios_resolve_by_matrix_code_in_either_alphabet():
    assert resolve_scenario("Б.3.1").scenario_id == "b_3_1_reverse_left_fail"
    assert resolve_scenario("B.3.1").scenario_id == "b_3_1_reverse_left_fail"
    assert resolve_scenario("А.1.2").scenario_id == "a_1_2_flare"
    assert resolve_scenario("A.1.2").scenario_id == "a_1_2_flare"
    with pytest.raises(KeyError):
        resolve_scenario("Ж.9.9")


def test_matrix_battery_follows_the_table_order():
    battery = matrix_battery()
    assert [scenario.matrix_code for scenario in battery] == [case.code for case in RUN_MATRIX]
    assert [scenario.matrix_code for scenario in matrix_battery("taxi")] == ["Б.1.2"]


def test_sft_filters_by_profile_and_draft(capsys):
    scenarios = build_scenarios(PretrainRunConfig(
        variants_per_preset=1, aircraft_profile="mc21", backend="ics",
    ))
    assert scenarios
    assert all(not scenario.is_draft("mc21", FlightSegment.ROLLOUT) for scenario in scenarios)
    assert "пропущены неоткалиброванные" in capsys.readouterr().out


def test_sft_named_presets_and_matrix_names(capsys):
    scenarios = build_scenarios(PretrainRunConfig(
        variants_per_preset=2, presets=("default", "nws_fail"),
        aircraft_profile="mc21", backend="ics",
    ))
    assert {scenario.scenario_id.split("-v", 1)[0] for scenario in scenarios} == {
        "default", "nws_fail",
    }
    assert len(scenarios) == 4
    assert matrix_preset_names(only_calibrated=False) == tuple(
        case.preset for case in ground_cases())
    assert matrix_preset_names() == ()
