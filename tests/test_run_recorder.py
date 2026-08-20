import csv
import json
import time
from dataclasses import fields
from threading import Event
from types import SimpleNamespace

import pytest

from ismpu.control.system import ControllingSystem
from ismpu.config.scenarios import Scenario, scenario_for_matrix_run
from ismpu.config.segments import FlightSegment
from ismpu.runtime.run_recorder import TELEMETRY_FIELDS, RunRecorder
from ismpu.io.ics_connector import ICSInputs, ICSOutputs

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
    recorder.record(
        sample,
        controller,
        elapsed_s=0.05,
        runtime_timing={
            "runtime_rx_s": 0.01,
            "runtime_control_start_s": 0.011,
            "runtime_control_end_s": 0.012,
            "runtime_tx_s": 0.012,
            "runtime_telemetry_age_s": 0.001,
            "runtime_stale_rx_dropped": 0,
        },
    )
    assert recorder.sample_count == 1
    assert recorder.directory.exists()

    exported = recorder.export_gains(controller, label="dashboard")
    recorder.finish({"accepted": True})

    expected = {
        "manifest.json", "raw-rx.jsonl", "raw-tx.jsonl", "telemetry.csv",
        "approach.csv", "ground.csv", "events.jsonl", "candidates", "report.json",
    }
    assert {path.name for path in recorder.directory.iterdir()} == expected
    assert (recorder.directory / "manifest.json").is_file()
    assert (recorder.directory / "telemetry.csv").is_file()
    assert (recorder.directory / "report.json").is_file()
    assert exported.is_file()
    assert scenario.control_for("mc21", FlightSegment.ROLLOUT).brake_l["kp"] == original_kp

    metadata = json.loads(
        (recorder.directory / "manifest.json").read_text(encoding="utf-8"))
    assert metadata["aircraft_profile"] == "a330-300"
    assert metadata["scenario"]["schema_version"] == 3
    assert set(metadata["scenario"]["aircraft_controls"]) == {"mc21", "a330-300"}
    assert metadata["execution_id"] == recorder.execution_id
    assert len(metadata["matrix_catalog_sha256"]) == 64
    assert len(metadata["matrix_source_sha256"]) == 64
    assert metadata["matrix_run_ids"] == {}
    assert set(metadata["scenario"]["conditions"]) == {"approach", "rollout", "taxi"}
    assert metadata["frequency_hz"] == 20.0
    assert metadata["schema_version"] == 4
    assert metadata["samples"] == 1
    assert metadata["git"].keys() == {"revision", "dirty"}

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
    assert rows[0]["tick_id"] == "1"
    assert rows[0]["dt"] == "0.05"
    assert rows[0]["scenario_id"] == scenario.scenario_id
    assert rows[0]["config_revision"] == "0"
    assert rows[0]["runtime_rx_s"] == "0.01"
    assert rows[0]["runtime_tx_s"] == "0.012"
    ground_tolerances = json.loads(rows[0]["ground_tolerances"])
    assert ground_tolerances["segment"] == "rollout"
    assert ground_tolerances["xte_limit_m"] == 3.0

    with (recorder.directory / "ground.csv").open(encoding="utf-8", newline="") as stream:
        assert len(list(csv.DictReader(stream))) == 1
    with (recorder.directory / "approach.csv").open(encoding="utf-8", newline="") as stream:
        assert list(csv.DictReader(stream)) == []

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
        (recorder.directory / "manifest.json").read_text(encoding="utf-8"))
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
    assert all(f"ics_out_{field.name}" in row for field in fields(ICSOutputs))


def test_streaming_flush_is_readable_before_finish_and_memory_is_bounded(tmp_path):
    controller = ControllingSystem()
    scenario = Scenario.from_preset("default")
    scenario.apply_control(controller, "mc21")
    recorder = RunRecorder(
        root=tmp_path, backend="xplane", aircraft_profile="mc21",
        scenario=scenario, flush_interval_s=999.0, ring_size=2,
    )

    for index in range(3):
        sample = telemetry(groundspeed_ms=80.0 - index)
        controller.control_step(0.05, sample, send=False)
        recorder.record(sample, controller, elapsed_s=0.05 * (index + 1))
    recorder.flush()

    with (recorder.directory / "telemetry.csv").open(
        encoding="utf-8", newline=""
    ) as stream:
        assert len(list(csv.DictReader(stream))) == 3
    assert len(recorder.recent_samples) == 2
    assert not hasattr(recorder, "_rows")
    recorder.finish({"stop_reason": "completed", "conditions_valid": True})


def test_slow_writer_never_blocks_the_control_thread_and_preserves_order(tmp_path):
    controller = ControllingSystem()
    scenario = Scenario.from_preset("default")
    scenario.apply_control(controller, "mc21")
    recorder = RunRecorder(
        root=tmp_path, backend="ics", aircraft_profile="mc21", scenario=scenario)
    recorder.start()
    entered, release = Event(), Event()
    original = recorder._write_item

    def slow_write(kind, payload):
        if kind == "row":
            entered.set()
            release.wait(1.0)
        original(kind, payload)

    recorder._write_item = slow_write
    started = time.perf_counter()
    for tick in range(2):
        sample = telemetry(groundspeed_ms=80.0 - tick)
        controller.control_step(0.05, sample, send=False)
        recorder.record(sample, controller, elapsed_s=0.05 * (tick + 1))
    elapsed = time.perf_counter() - started

    assert elapsed < 0.1
    assert entered.wait(1.0)
    release.set()
    recorder.finish()
    with (recorder.directory / "telemetry.csv").open(
        encoding="utf-8", newline=""
    ) as stream:
        assert [row["tick_id"] for row in csv.DictReader(stream)] == ["1", "2"]


def test_writer_queue_overflow_invalidates_run_without_waiting(tmp_path):
    scenario = Scenario.from_preset("default")
    recorder = RunRecorder(
        root=tmp_path, backend="ics", aircraft_profile="mc21", scenario=scenario,
        writer_queue_size=1,
    )
    recorder.start()
    recorder.flush()
    entered, release = Event(), Event()
    original = recorder._write_item

    def blocked_write(kind, payload):
        entered.set()
        release.wait(1.0)
        original(kind, payload)

    recorder._write_item = blocked_write
    assert recorder._enqueue(("event", {"event": "first"}))
    assert entered.wait(1.0)
    assert recorder._enqueue(("event", {"event": "queued"}))
    started = time.perf_counter()
    assert not recorder._enqueue(("event", {"event": "overflow"}))
    assert time.perf_counter() - started < 0.1
    assert recorder.recording_failed
    assert "переполнена" in recorder.recording_error
    release.set()
    recorder.finish()


def test_recording_failure_never_escapes_into_control_and_invalidates_result(tmp_path):
    controller = ControllingSystem()
    scenario = Scenario.from_preset("default")
    scenario.apply_control(controller, "mc21")
    recorder = RunRecorder(
        root=tmp_path, backend="ics", aircraft_profile="mc21", scenario=scenario)
    recorder.start()
    recorder._streams["telemetry"].close()  # имитация ошибки диска во время append
    sample = telemetry(groundspeed_ms=80.0)
    controller.control_step(0.05, sample, send=False)

    recorded = recorder.record(sample, controller, elapsed_s=0.05)
    recorder.flush()  # writer-поток должен успеть увидеть имитацию ошибки диска

    assert recorded.tick_id == 1
    assert recorder.recording_failed
    assert recorder.recording_error
    assert recorder.sample_count == 1
    recorder.finish({"stop_reason": "completed", "conditions_valid": True})
    manifest = json.loads(
        (recorder.directory / "manifest.json").read_text(encoding="utf-8"))
    report = json.loads(
        (recorder.directory / "report.json").read_text(encoding="utf-8"))
    assert manifest["recording_failed"] is True
    assert report["acceptance_valid"] is False
    assert report["sft_eligible"] is False


def test_raw_packet_files_keep_exact_udp_json_and_only_observed_tx(tmp_path):
    class Connector:
        observer = None

        def set_packet_observer(self, observer):
            self.observer = observer

    connector = Connector()
    scenario = Scenario.from_preset("default")
    recorder = RunRecorder(
        root=tmp_path, backend="ics", aircraft_profile="mc21", scenario=scenario)
    assert recorder.attach_sim(SimpleNamespace(connector=connector))
    recorder.start()
    rx = b'{"GroundSpeed":1,"SomeFutureSignal":{"x":42}}'
    tx = b'{"ControlMode":3,"ModeAIReady":1,"ControlValidMask":14108}'

    connector.observer("rx", rx, ("10.0.0.1", 3030))
    connector.observer("tx", tx, ("10.0.0.1", 3030))
    recorder.finish({"stop_reason": "interrupted"})

    assert (recorder.directory / "raw-rx.jsonl").read_bytes() == rx + b"\n"
    assert (recorder.directory / "raw-tx.jsonl").read_bytes() == tx + b"\n"
    manifest = json.loads(
        (recorder.directory / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["raw_packets"] == {"rx": 1, "tx": 1}
    events = [json.loads(line) for line in (
        recorder.directory / "events.jsonl").read_text(encoding="utf-8").splitlines()]
    assert any(event["event"] == "handshake" for event in events)
