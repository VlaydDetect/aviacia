"""Матрица прогонов и её связь с единым реестром сценариев."""

import json
from dataclasses import replace
from pathlib import Path

import pytest

from ismpu.config.approach import (
    APPROACH_CONFIGS,
    APPROACH_DEFAULT,
    ICS_CLEAR_WEATHER_APPROACH,
)
from ismpu.config.run_matrix import (
    RUN_MATRIX, MATRIX_CASES, MATRIX_RUNS, RUN_BY_ID, APPROACH_CASES, GROUND_CASES,
    APPROACH_CONDITIONS, GROUND_CONDITIONS, CASE_BY_CODE, CATALOG_PATH, COLUMNS,
    SOURCE_SHA256, THROUGH_PROFILE_CODES, TOTAL_RUNS, resolve_matrix_run,
)
from ismpu.config.scenarios import (
    ProfileStatus,
    SCENARIOS,
    compose_matrix_scenario,
    resolve_scenario,
    scenario_for_matrix_run,
    select_scenario,
)
from ismpu.config.segments import FlightSegment
from ismpu.control.failures import FailureMode
from ismpu.control.system import ControllingSystem
from ismpu.tools.import_run_matrix import import_workbook
from ismpu.utils.converts import Converts


def test_catalog_is_an_exact_reproducible_import_of_the_customer_workbook():
    root = Path(__file__).resolve().parents[1]
    workbook = root / "docs" / "Матрица_прогонов_ПИД_ИСМПУ.xlsx"
    committed = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))

    assert import_workbook(workbook) == committed
    assert SOURCE_SHA256 == "277a8610ea30f2b8dd2307bbf68fc2854ada5dcb350012aa94ab07a64d179785"
    assert len(COLUMNS) == 16
    assert len(MATRIX_RUNS) == len(RUN_MATRIX) == TOTAL_RUNS == 280
    assert len({run.matrix_run_id for run in MATRIX_RUNS}) == 280
    assert all(tuple(run.cells) == COLUMNS for run in MATRIX_RUNS)
    assert len(MATRIX_RUNS[0].operator_setup) == 13
    assert len(MATRIX_RUNS[0].result_template) == 3
    assert RUN_BY_ID["А.1.1/2"].cells["Отказ / режим"] == "—//—"
    assert RUN_BY_ID["А.1.1/10"].cells["Ветер: скорость, м/с"] == "10 → 0"
    assert RUN_BY_ID["Б.4.2/2"].cells["Критерии успеха"] == "Критерии А.4.1 и Б.3.1"


def test_matrix_totals_and_derived_code_groups_match_the_workbook():
    assert len(MATRIX_CASES) == 22
    assert len(APPROACH_CASES) == 12 and len(GROUND_CASES) == 10
    assert sum(case.runs for case in APPROACH_CASES) == 156
    assert sum(case.runs for case in GROUND_CASES) == 124
    assert len([run for run in MATRIX_RUNS if run.sheet_role == "approach"]) == 156
    assert len([run for run in MATRIX_RUNS if run.sheet_role == "ground"]) == 124
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
        approach_run="А.4.1/4",
        rollout_run="Б.3.1/11",
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
    assert scenario.matrix_runs == {
        FlightSegment.APPROACH: "А.4.1/4",
        FlightSegment.ROLLOUT: "Б.3.1/11",
    }
    assert scenario.conditions_for(FlightSegment.APPROACH).weather.wind_speed_kts == \
        pytest.approx(10.0 * Converts.MS_TO_KTS)
    assert scenario.conditions_for(FlightSegment.ROLLOUT).weather.runway_friction == 2.0


def test_drafts_are_never_selected_automatically():
    with pytest.raises(ValueError, match="нет допущенных сценариев"):
        select_scenario(
            (FailureMode.NWS_FAIL,), aircraft_profile="mc21",
            segment=FlightSegment.ROLLOUT,
        )
    selected = select_scenario(
        (FailureMode.NWS_FAIL,), aircraft_profile="mc21",
        segment=FlightSegment.ROLLOUT, include_draft=True,
    )
    assert selected.scenario_id == "nws_fail"
    assert selected.is_draft("mc21", FlightSegment.ROLLOUT)


def test_telemetry_selection_never_guesses_an_ambiguous_matrix_row():
    selected = select_scenario(
        (FailureMode.NWS_FAIL,),
        scenarios=(
            scenario_for_matrix_run("Б.2.1/1"),
            scenario_for_matrix_run("Б.2.2/1"),
            SCENARIOS["nws_fail"],
        ),
        include_draft=True,
    )
    assert selected is SCENARIOS["nws_fail"]


def test_b42_has_phase_specific_engine_and_reverse_failures():
    scenario = SCENARIOS["b_4_2_through_engine_out"]
    assert scenario.conditions_for(FlightSegment.APPROACH).failures == frozenset({
        FailureMode.ENGINE_OUT_LEFT,
    })
    assert scenario.conditions_for(FlightSegment.ROLLOUT).failures == frozenset({
        FailureMode.ENGINE_OUT_LEFT, FailureMode.REVERSE_LEFT_FAIL,
    })


def test_through_rows_expand_to_fixed_profiles_and_keep_one_selected_run():
    scenario = scenario_for_matrix_run("Б.4.2/2")
    assert THROUGH_PROFILE_CODES["Б.4.2"] == {
        FlightSegment.APPROACH: "А.4.1",
        FlightSegment.ROLLOUT: "Б.3.1",
    }
    assert scenario.matrix_runs == {
        FlightSegment.APPROACH: "Б.4.2/2",
        FlightSegment.ROLLOUT: "Б.4.2/2",
    }
    assert scenario.provenance[FlightSegment.APPROACH] == "a_4_1_engine_out_high"
    assert scenario.provenance[FlightSegment.ROLLOUT] == "b_3_1_reverse_left_fail"
    assert scenario.conditions_for(FlightSegment.APPROACH).failures == frozenset({
        FailureMode.ENGINE_OUT_LEFT,
    })
    assert scenario.conditions_for(FlightSegment.ROLLOUT).failures == frozenset({
        FailureMode.ENGINE_OUT_LEFT, FailureMode.REVERSE_LEFT_FAIL,
    })


def test_control_profile_has_one_base_per_code_and_sparse_run_override():
    scenario = scenario_for_matrix_run("Б.1.1/2")
    source = scenario.aircraft_controls["mc21"]
    profile = replace(
        source,
        statuses={**source.statuses, FlightSegment.ROLLOUT: ProfileStatus.TUNED},
        run_overrides={
            "Б.1.1/2": {
                FlightSegment.ROLLOUT: {"brake_l": {"kp": 0.4321}},
            },
        },
    )
    configured = replace(
        scenario,
        aircraft_controls={**scenario.aircraft_controls, "mc21": profile},
    )
    effective = configured.control_for("mc21", FlightSegment.ROLLOUT)
    base = source.for_segment(FlightSegment.ROLLOUT)
    assert effective.brake_l["kp"] == 0.4321
    assert base.brake_l["kp"] != 0.4321
    assert effective.brake_l is not base.brake_l
    assert configured.control_status("mc21", FlightSegment.ROLLOUT) is ProfileStatus.TUNED
    assert not configured.is_draft("mc21", FlightSegment.ROLLOUT)
    assert not configured.is_accepted("mc21", FlightSegment.ROLLOUT)
    assert configured.to_dict() == type(configured).from_dict(configured.to_dict()).to_dict()

    with pytest.raises(ValueError, match="неизвестное поле override"):
        replace(source, run_overrides={
            "Б.1.1/2": {FlightSegment.ROLLOUT: {"unknown": 1.0}},
        })


def test_matrix_run_id_and_segment_must_match_exactly():
    assert resolve_matrix_run("B.1.1/02").matrix_run_id == "Б.1.1/2"
    with pytest.raises(KeyError, match="<шифр>/<номер>"):
        resolve_matrix_run("Б.1.1")
    with pytest.raises(ValueError, match="rollout, а не к approach"):
        compose_matrix_scenario("wrong", approach_run="Б.1.1/1")
    scenario = scenario_for_matrix_run("Б.1.1/1")
    with pytest.raises(ValueError, match="не совпадает"):
        replace(
            scenario,
            matrix_codes={FlightSegment.ROLLOUT: "Б.2.1"},
        )


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
