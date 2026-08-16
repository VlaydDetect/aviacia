import json
from dataclasses import replace

import pytest

from ismpu.config.run_matrix import MATRIX_RUNS, resolve_matrix_run
from ismpu.config.runway import RWY_HEADING_TRUE
from ismpu.config.scenarios import (
    ProfileStatus, rebind_matrix_run, scenario_for_matrix_run,
)
from ismpu.config.segments import FlightSegment
from ismpu.control.system import ControllingSystem
from ismpu.envs.ics_sim import Telemetry
from ismpu.runtime.campaign import (
    campaign_phase, campaign_rows, campaign_summary, next_campaign_row,
)
from ismpu.runtime.evaluate import PASS, evaluate_matrix_run, verdict_of
from ismpu.runtime.promote_candidate import promote_candidate
from ismpu.runtime.run_artifacts import RunRecorder, gains_snapshot
from ismpu.runtime.run_report import _metrics as report_metrics
from tests.fakes import engaged_inputs


def _metrics():
    return {
        "max_deviations": {
            "approach_course_deg": 0.2,
            "approach_glideslope_deg": 0.2,
            "approach_axis_at_30m_m": 1.0,
            "approach_runway_heading_deg": 1.0,
            "rollout_xte_m": 1.0,
            "taxi_xte_m": 0.5,
            "runway_heading_deg": 1.0,
        },
        "touchdown": {
            "along_track_m": 300.0,
            "vertical_speed_fpm": -200.0,
            "groundspeed_kts": 140.0,
            "indicated_airspeed_kts": 140.0,
            "vapp_kt": 140.0,
            "normal_load_g": 1.2,
            "lateral_load_g": 0.1,
        },
        "handover": {"max_rate_ratio": 1.0},
    }


def test_campaign_order_covers_every_matrix_row_once():
    rows = campaign_rows()

    assert len(rows) == len(MATRIX_RUNS) == 280
    assert len({row.matrix_run_id for row in rows}) == 280
    assert rows[0].matrix_run_id == "Б.1.1/1"
    assert campaign_phase(rows[0]) == 1
    assert campaign_phase(rows[1]) == 2
    assert rows[-1].matrix_run_id == "Б.4.2/2"
    assert campaign_phase(rows[-1]) == 8


def test_each_matrix_code_has_explicit_row_specific_evaluator():
    for row in {item.code: item for item in MATRIX_RUNS}.values():
        criteria = evaluate_matrix_run(row, _metrics())
        assert criteria
        assert verdict_of(criteria) == PASS


def test_direct_taxi_does_not_inherit_rollout_criterion():
    metrics = _metrics()
    metrics["max_deviations"]["rollout_xte_m"] = None

    criteria = evaluate_matrix_run(resolve_matrix_run("Б.1.2/1"), metrics)

    assert [item.name for item in criteria] == ["xte_taxi_max"]
    assert criteria[0].verdict == PASS


def test_axis_at_30m_is_interpolated_only_when_height_is_crossed():
    class Reader:
        manifest = {}

        @staticmethod
        def rows():
            return iter((
                {"time_s": 0.0, "valid": 1, "segment": "approach",
                 "radio_altitude_ft": 100.0, "lateral_deviation_m": 1.0},
                {"time_s": 0.05, "valid": 1, "segment": "approach",
                 "radio_altitude_ft": 95.0, "lateral_deviation_m": 3.0},
            ))

    metrics = report_metrics(Reader())
    target_ft = 30.0 / 0.3048
    expected = 1.0 + (target_ft - 100.0) / (95.0 - 100.0) * 2.0

    assert metrics["max_deviations"]["approach_axis_at_30m_m"] == pytest.approx(expected)


def test_rebind_keeps_sparse_overrides_but_replaces_operator_conditions():
    source = scenario_for_matrix_run("Б.1.1/1")
    controls = dict(source.aircraft_controls)
    mc21 = controls["mc21"]
    controls["mc21"] = replace(mc21, run_overrides={
        "Б.1.1/2": {
            FlightSegment.ROLLOUT: {"brake_l": {"kp": 0.321}},
        },
    })
    source = replace(source, aircraft_controls=controls)

    rebound = rebind_matrix_run(source, "Б.1.1/2")

    assert rebound.matrix_runs == {FlightSegment.ROLLOUT: "Б.1.1/2"}
    assert rebound.control_for(
        "mc21", FlightSegment.ROLLOUT).brake_l["kp"] == pytest.approx(0.321)
    assert rebound.conditions_for(FlightSegment.ROLLOUT).weather == \
        resolve_matrix_run("Б.1.1/2").condition.weather
    with pytest.raises(ValueError, match="а выбран Б.2.1"):
        rebind_matrix_run(source, "Б.2.1/1")


def test_campaign_status_uses_latest_artifacts_and_returns_first_retry(tmp_path):
    for run_id, status, stamp in (
        ("Б.1.1/1", "PASS", "2026-08-16T01:00:00+00:00"),
        ("Б.1.1/2", "FAIL", "2026-08-16T02:00:00+00:00"),
    ):
        directory = tmp_path / run_id.replace("/", "-")
        directory.mkdir()
        scenario = scenario_for_matrix_run(run_id)
        (directory / "manifest.json").write_text(json.dumps({
            "execution_id": directory.name,
            "aircraft_profile": "mc21",
            "started_at": stamp,
            "matrix_run_ids": {
                segment.value: selected for segment, selected in scenario.matrix_runs.items()},
            "scenario": scenario.to_dict(),
        }), encoding="utf-8")
        (directory / "report.json").write_text(json.dumps({
            "status": status,
            "acceptance_valid": True,
            "sft_eligible": False,
        }), encoding="utf-8")

    summary = campaign_summary(tmp_path)

    assert summary["total"] == 280
    assert summary["counts"] == {"FAIL": 1, "PASS": 1, "PENDING": 278}
    assert summary["next"]["matrix_run_id"] == "Б.1.1/2"
    assert next_campaign_row(tmp_path).matrix_run_id == "Б.1.1/2"


def test_accepted_promotion_allows_fixed_row_specific_overrides(tmp_path):
    rows = tuple(item for item in campaign_rows() if item.code == "Б.1.1")
    source = scenario_for_matrix_run(rows[0])
    controls = dict(source.aircraft_controls)
    mc21 = controls["mc21"]
    base_kp = mc21.rollout.brake_l["kp"]
    controls["mc21"] = replace(
        mc21,
        statuses={**mc21.statuses, FlightSegment.ROLLOUT: ProfileStatus.TUNED},
        run_overrides={
            row.matrix_run_id: {
                FlightSegment.ROLLOUT: {
                    "brake_l": {"kp": base_kp * (1.0 + row.run_number / 1000.0)}}
            }
            for row in rows
        },
    )
    source = replace(source, aircraft_controls=controls)
    candidate = None
    for row in rows:
        scenario = rebind_matrix_run(source, row)
        controller = ControllingSystem()
        controller.bind_scenario(scenario, "mc21")
        first = Telemetry.from_ics(engaged_inputs(
            GroundSpeed=110.0, IndicatedAirspeed=110.0,
            RunwayHeadingValid=1, RunwayHeading=float(RWY_HEADING_TRUE),
            LateralDeviation=0.1, TrueHeading=float(RWY_HEADING_TRUE)))
        controller.begin_flight(first)
        recorder = RunRecorder(
            root=tmp_path, backend="ics", aircraft_profile="mc21",
            scenario=scenario, start="rollout")
        for index, speed in enumerate((110.0, 105.0), 1):
            frame = Telemetry.from_ics(engaged_inputs(
                GroundSpeed=speed, IndicatedAirspeed=speed,
                RunwayHeadingValid=1, RunwayHeading=float(RWY_HEADING_TRUE),
                LateralDeviation=0.1, TrueHeading=float(RWY_HEADING_TRUE)))
            controller.control_step(0.05, frame, send=False)
            recorder.record(frame, controller, elapsed_s=index * 0.05, dt=0.05)
        if row is rows[-1]:
            effective = recorder.manifest["effective_configs"]["rollout"]["control"]
            candidate = recorder.export_candidate(
                segment="rollout", config_revision=controller.config_revision,
                effective_config=effective, gains=gains_snapshot(controller))
        recorder.finish({"stop_reason": "completed", "conditions_valid": True})

    output = promote_candidate(
        candidate, accepted=True, evidence_root=tmp_path, verify_replay=True)
    promoted = json.loads(output.read_text(encoding="utf-8"))

    assert promoted["aircraft_controls"]["mc21"]["statuses"]["rollout"] == "accepted"
    assert len(promoted["aircraft_controls"]["mc21"]["run_overrides"]) == len(rows)
