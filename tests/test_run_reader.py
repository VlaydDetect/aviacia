import csv
import json

import pytest

from ismpu.config.runway import RWY_HEADING_TRUE
from ismpu.config.scenarios import Scenario, scenario_for_matrix_run
from ismpu.control.system import ControllingSystem
from ismpu.envs.ics_sim import Telemetry
from ismpu.runtime.run_reader import RunReader
from ismpu.runtime.run_recorder import RunRecorder
from ismpu.runtime.run_report import aggregate_matrix_results
from tests.fakes import airborne_inputs, engaged_inputs


def _frame(speed_kts: float, xte_m: float = 0.0) -> Telemetry:
    return Telemetry.from_ics(engaged_inputs(
        GroundSpeed=speed_kts,
        IndicatedAirspeed=speed_kts,
        RunwayHeadingValid=1,
        RunwayHeading=float(RWY_HEADING_TRUE),
        LateralDeviation=xte_m,
        TrueHeading=float(RWY_HEADING_TRUE),
    ))


def _record_ground_run(tmp_path, scenario=None, *, record_sft_fallback=False):
    scenario = scenario or Scenario.from_preset("default")
    controller = ControllingSystem()
    controller.bind_scenario(scenario, "mc21")
    first = _frame(110.0)
    controller.begin_flight(first)
    recorder = RunRecorder(
        root=tmp_path, backend="ics", aircraft_profile="mc21",
        scenario=scenario, start="rollout",
    )
    for index, speed in enumerate((110.0, 105.0, 100.0), 1):
        frame = _frame(speed, xte_m=0.1 * index)
        controller.control_step(0.05, frame, send=False)
        if record_sft_fallback:
            controller.sft_diagnostics = {
                "mode": "sft-shadow", "segment": "ground", "fallback": index == 2,
                "reason": "test_guard" if index == 2 else None,
            }
        recorder.record(frame, controller, elapsed_s=index * 0.05)
    recorder.finish({"stop_reason": "completed", "conditions_valid": True})
    return recorder


def test_run_reader_streams_samples_events_and_replays_controller(tmp_path):
    recorder = _record_ground_run(tmp_path)
    reader = RunReader(recorder.directory)

    samples = list(reader.samples())
    replay = reader.replay(atol=1e-12, rtol=1e-12)

    assert [sample.tick_id for sample in samples] == [1, 2, 3]
    assert [sample.sequence for sample in samples] == [0, 1, 2]
    assert any(event["event"] == "segment" for event in reader.events())
    assert replay.success, replay.mismatches[:3]
    assert replay.samples == 3
    assert replay.compared_values > 50
    assert replay.max_abs_error <= 1e-12


def test_approach_stream_has_three_pid_states_and_replays_at_1e_12(tmp_path):
    scenario = Scenario.from_preset("default")
    controller = ControllingSystem()
    controller.bind_scenario(scenario, "mc21")
    first = Telemetry.from_ics(airborne_inputs(550.0))
    controller.begin_flight(first)
    recorder = RunRecorder(
        root=tmp_path, backend="ics", aircraft_profile="mc21",
        scenario=scenario, start="approach")
    for index, ra in enumerate((550.0, 540.0, 530.0), 1):
        frame = Telemetry.from_ics(airborne_inputs(ra))
        controller.control_step(0.05, frame, send=False)
        recorder.record(frame, controller, elapsed_s=index * 0.05)
    recorder.finish({"stop_reason": "completed", "conditions_valid": True})

    with (recorder.directory / "approach.csv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 3
    assert rows[0]["approach_input_LocDeviation"] == "0.0"
    assert rows[0]["approach_flare_active"] == "False"
    assert all(rows[0][f"pid_{name}_integral"] for name in ("roll", "pitch", "air_speed"))
    assert RunReader(recorder.directory).replay(atol=1e-12, rtol=1e-12).success


def test_legacy_adapter_does_not_invent_missing_pid_terms(tmp_path):
    path = tmp_path / "working.csv"
    path.write_text(
        "time_s,ra_ft,ias_kt,roll_kp,roll_i_term\n"
        "0.0,100,140,-7.0,0.25\n",
        encoding="utf-8",
    )

    row = next(RunReader(path).rows())

    assert row["pid_roll_kp"] == -7.0
    assert row["pid_roll_i"] == 0.25
    assert row.get("pid_roll_p") is None
    assert row.get("pid_roll_d") is None


def test_report_contains_matrix_metrics_and_aggregation_uses_workbook_columns(tmp_path):
    recorder = _record_ground_run(
        tmp_path, scenario_for_matrix_run("Б.1.1/1"), record_sft_fallback=True
    )
    report = json.loads((recorder.directory / "report.json").read_text(encoding="utf-8"))

    assert report["acceptance_valid"]
    assert report["metrics"]["max_deviations"]["rollout_xte_m"] == pytest.approx(0.3)
    assert report["metrics"]["speed_profile"]["max_abs_error_ms"] is not None
    assert report["metrics"]["saturation"]["ratio"] is not None
    assert report["metrics"]["tz_diagnostics"]["sft_fallbacks"] == 1
    assert report["matrix_results"][0]["Шифр"] == "Б.1.1"
    assert report["matrix_results"][0]["Статус"] in {"PASS", "FAIL"}

    output = aggregate_matrix_results(tmp_path)
    with output.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 1
    assert rows[0]["Шифр"] == "Б.1.1"
    assert rows[0]["Факт. макс. отклонения"]
