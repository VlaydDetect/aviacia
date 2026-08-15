import csv
import json
from dataclasses import fields

import pytest

from ismpu.control.system import ControllingSystem
from ismpu.envs.scenario import Scenario, scenario_for_matrix_run
from ismpu.config.segments import FlightSegment
from ismpu.runtime.run_recorder import TELEMETRY_FIELDS, RunRecorder
from ismpu.io.ics_connector import ICSInputs

from tests.fakes import engaged_inputs, telemetry


def test_run_recorder_writes_replayable_run_and_non_destructive_gain_export(tmp_path):
    controller = ControllingSystem()
    scenario = Scenario.from_preset("default")
    scenario.apply_control(controller, "mc21")
    original_kp = scenario.control_for("mc21", FlightSegment.ROLLOUT).brake_l["kp"]

    recorder = RunRecorder(
        root=tmp_path,
        backend="xplane",
        aircraft_profile="a330-300",
        scenario=scenario,
        start="rollout",
    )
    assert not recorder.directory.exists()

    sample = telemetry(groundspeed_ms=80.0)
    controller.control_step(0.05, sample, send=False)
    recorder.record(sample, controller, elapsed_s=0.05)
    assert recorder.sample_count == 1
    assert not recorder.directory.exists()

    exported = recorder.export_gains(controller, label="dashboard")
    recorder.finish({"accepted": True})

    assert (recorder.directory / "metadata.json").is_file()
    assert (recorder.directory / "telemetry.csv").is_file()
    assert (recorder.directory / "report.json").is_file()
    assert exported.is_file()
    assert scenario.control_for("mc21", FlightSegment.ROLLOUT).brake_l["kp"] == original_kp

    metadata = json.loads(
        (recorder.directory / "metadata.json").read_text(encoding="utf-8"))
    assert metadata["aircraft_profile"] == "a330-300"
    assert metadata["scenario"]["schema_version"] == 3
    assert set(metadata["scenario"]["aircraft_controls"]) == {"mc21", "a330-300"}
    assert metadata["execution_id"] == recorder.execution_id
    assert len(metadata["matrix_catalog_sha256"]) == 64
    assert len(metadata["matrix_source_sha256"]) == 64
    assert metadata["matrix_run_ids"] == {}
    assert set(metadata["scenario"]["conditions"]) == {"approach", "rollout", "taxi"}

    with (recorder.directory / "telemetry.csv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 1
    assert rows[0]["segment"] == "rollout"
    assert "pid_pitch_p" in rows[0]
    assert "pid_brake_l_integral" in rows[0]
    assert "pid_reverse_r_derivative" in rows[0]
    assert "pid_steer_unconstrained" in rows[0]
    assert "pid_reverse_r_saturated" in rows[0]

    snapshot = json.loads(exported.read_text(encoding="utf-8"))
    assert snapshot["backend"] == "xplane"
    assert set(snapshot["gains"]) == {
        "roll", "pitch", "air_speed", "steer",
        "brake_l", "brake_r", "reverse_l", "reverse_r",
    }

    with pytest.raises(RuntimeError, match="уже завершён"):
        recorder.record(sample, controller, elapsed_s=0.1)


def test_recorder_pins_selected_matrix_rows_and_catalog_hash(tmp_path):
    scenario = scenario_for_matrix_run("Б.1.1/3")
    recorder = RunRecorder(
        root=tmp_path,
        backend="ics",
        aircraft_profile="mc21",
        scenario=scenario,
    )
    recorder.finish()
    metadata = json.loads(
        (recorder.directory / "metadata.json").read_text(encoding="utf-8"))
    assert metadata["matrix_run_ids"] == {"rollout": "Б.1.1/3"}
    assert metadata["scenario"]["matrix_runs"] == {"rollout": "Б.1.1/3"}
    assert len(metadata["matrix_catalog_sha256"]) == 64
    assert metadata["matrix_source_sha256"] == \
        "277a8610ea30f2b8dd2307bbf68fc2854ada5dcb350012aa94ab07a64d179785"


def test_unused_recorder_does_not_create_a_second_run_directory(tmp_path):
    controller = ControllingSystem()
    scenario = Scenario.from_preset("default")
    scenario.apply_control(controller, "mc21")
    unused = RunRecorder(
        root=tmp_path,
        backend="ics",
        aircraft_profile="bench",
        scenario=scenario,
    )
    recorder = RunRecorder(
        root=tmp_path,
        backend="xplane",
        aircraft_profile="a330-300",
        scenario=scenario,
        start="rollout",
    )

    sample = telemetry(groundspeed_ms=80.0)
    controller.control_step(0.05, sample, send=False)
    recorder.record(sample, controller, elapsed_s=0.05)
    recorder.finish()

    assert not unused.directory.exists()
    assert [path for path in tmp_path.iterdir() if path.is_dir()] == [
        recorder.directory
    ]


def test_zero_sample_run_has_a_replayable_csv_header(tmp_path):
    scenario = Scenario.from_preset("default")
    recorder = RunRecorder(
        root=tmp_path,
        backend="xplane",
        aircraft_profile="a330-300",
        scenario=scenario,
    )

    recorder.finish()

    with (recorder.directory / "telemetry.csv").open(
        encoding="utf-8", newline=""
    ) as stream:
        reader = csv.DictReader(stream)
        assert tuple(reader.fieldnames or ()) == TELEMETRY_FIELDS
        assert list(reader) == []


def test_recorder_keeps_all_known_ics_fields_and_unknown_raw_fields(tmp_path):
    from ismpu.envs.ics_sim import Telemetry

    controller = ControllingSystem()
    scenario = Scenario.from_preset("default")
    scenario.apply_control(controller, "mc21")
    sample = Telemetry.from_ics(engaged_inputs(
        GroundSpeed=100.0,
        RunwayHeadingValid=1,
        RunwayHeading=64.0,
        LateralDeviation=2.5,
        RudderAngle=2.0,
        NoseWheelAngle=3.0,
        LeftBrakePedal=12.0,
        RightBrakePedal=13.0,
        LeftThrottleAngle=-4.0,
        RightThrottleAngle=-5.0,
        EngLeftThrust=101.0,
        EngRigntThrust=102.0,
        BodyLongAccelValid=1,
        BodyLongAccel=-0.2,
        BodyLatAccelValid=1,
        BodyLatAccel=0.03,
        BodyYawRateValid=1,
        BodyYawRate=1.5,
        SomeFutureSignal={"value": 42},
    ))
    recorder = RunRecorder(
        root=tmp_path,
        backend="ics",
        aircraft_profile="mc21",
        scenario=scenario,
    )

    controller.control_step(0.05, sample, send=False)
    recorder.record(sample, controller, elapsed_s=0.05)
    recorder.finish()

    with (recorder.directory / "telemetry.csv").open(
        encoding="utf-8", newline=""
    ) as stream:
        row = next(csv.DictReader(stream))
    assert len(fields(ICSInputs)) == 99
    assert all(f"ics_{field.name}" in row for field in fields(ICSInputs))
    assert row["ics_RunwayHeading"] == "64.0"
    assert row["ground_reference_speed_ms"]
    assert row["lateral_pid_requested"]
    assert row["allocator_limited_rudder"]
    assert row["allocator_requested_pedal"]
    assert row["feedback_rudder_deg"] == "2.0"
    assert row["feedback_nose_wheel_deg"] == "3.0"
    assert row["feedback_brake_left_mm"] == "12.0"
    assert row["feedback_throttle_right_deg"] == "-5.0"
    assert row["feedback_thrust_left"] == "101.0"
    assert float(row["feedback_yaw_rate_rad_s"]) == pytest.approx(0.0261799388)
    assert json.loads(row["ics_raw_json"]) == {"SomeFutureSignal": {"value": 42}}
