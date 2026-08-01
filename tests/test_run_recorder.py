import csv
import json

import pytest

from ismpu.control.system import ControllingSystem
from ismpu.envs.scenario import Scenario
from ismpu.config.segments import FlightSegment
from ismpu.runtime.run_recorder import TELEMETRY_FIELDS, RunRecorder

from tests.fakes import telemetry


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
    assert metadata["scenario"]["schema_version"] == 2
    assert set(metadata["scenario"]["aircraft_controls"]) == {"mc21", "a330-300"}
    assert set(metadata["scenario"]["conditions"]) == {"approach", "rollout", "taxi"}

    with (recorder.directory / "telemetry.csv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 1
    assert rows[0]["segment"] == "rollout"
    assert "pid_pitch_p" in rows[0]
    assert "pid_reverse_r_saturated" in rows[0]

    snapshot = json.loads(exported.read_text(encoding="utf-8"))
    assert snapshot["backend"] == "xplane"
    assert set(snapshot["gains"]) == {
        "roll", "pitch", "air_speed", "steer",
        "brake_l", "brake_r", "reverse_l", "reverse_r",
    }

    with pytest.raises(RuntimeError, match="уже завершён"):
        recorder.record(sample, controller, elapsed_s=0.1)


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
