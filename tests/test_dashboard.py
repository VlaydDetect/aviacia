import json
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from ismpu.config.segments import FlightSegment
from ismpu.control.system import ControllingSystem
from ismpu.config.scenarios import Scenario, scenario_for_matrix_run
from ismpu.gui import dashboard_core
from ismpu.gui.dashboard import DashboardServer, DashboardState, VIEW_SPECS
from ismpu.runtime.promote_candidate import PromotionError, promote_candidate
from ismpu.runtime.run_recorder import RunRecorder

from tests.fakes import telemetry


def _live(tmp_path, *, tune=False, control_mode="classical", scenario=None):
    scenario = scenario or Scenario.from_preset("default")
    controller = ControllingSystem()
    scenario.apply_control(controller, "mc21", FlightSegment.ROLLOUT)
    sample = telemetry(groundspeed_ms=75.0)
    controller.control_step(0.05, sample, send=False)
    recorder = RunRecorder(
        root=tmp_path, backend="xplane", aircraft_profile="mc21",
        scenario=scenario, start="rollout")
    recorder.record(sample, controller, elapsed_s=0.05, dt=0.05)
    state = DashboardState(
        controller, scenario=scenario, recorder=recorder,
        tune_enabled=tune, control_mode=control_mode)
    return controller, scenario, recorder, state, sample


def _post(url, payload):
    return urlopen(Request(
        url, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"}, method="POST"), timeout=2)


def test_dashboard_has_nine_views_and_flare_shares_pitch():
    assert [view.label for view in VIEW_SPECS] == [
        "Roll", "Pitch", "Flare", "Air Speed", "Steer",
        "Brake L", "Brake R", "Reverse L", "Reverse R",
    ]
    assert len({view.pid_key for view in VIEW_SPECS}) == 8
    assert next(view for view in VIEW_SPECS if view.key == "flare").pid_key == "pitch"
    assert not hasattr(DashboardState, "capture")
    assert not hasattr(DashboardState, "update_gains")


def test_incremental_snapshot_uses_recorder_objects_and_stays_small_when_idle(tmp_path):
    _controller, _scenario, recorder, state, _sample = _live(tmp_path)
    first = state.snapshot(-1, "old-run").as_dict()
    assert first["run_id"] == recorder.execution_id
    assert first["reset"] is True
    assert len(first["frames"]) == 1
    assert first["frames"][0]["sample_sequence"] == recorder.recent_samples[0].sequence
    assert first["frames"][0]["views"]["brake_l"]["p"] is not None
    assert "metadata" in first and "latest" in first
    assert len(first["metadata"]["telemetry_fields"]) == 99

    idle = state.snapshot(first["last_sequence"], recorder.execution_id).as_dict()
    assert idle == {
        "run_id": recorder.execution_id,
        "last_sequence": first["last_sequence"],
        "reset": False,
        "frames": [],
        "events": [],
    }
    assert len(json.dumps(idle, separators=(",", ":"))) < 180
    recorder.finish()


def test_live_and_replay_use_the_same_dashboard_snapshot(tmp_path):
    _controller, _scenario, recorder, live, _sample = _live(tmp_path)
    recorder.finish({"stop_reason": "interrupted"})
    live.complete()
    replay = DashboardState.from_csv(recorder.directory)

    live_snapshot = live.snapshot(-1).as_dict()
    replay_snapshot = replay.snapshot(-1).as_dict()
    assert [frame["views"] for frame in live_snapshot["frames"]] == [
        frame["views"] for frame in replay_snapshot["frames"]]
    assert [event["event"] for event in live_snapshot["events"]] == [
        event["event"] for event in replay_snapshot["events"]]
    assert replay_snapshot["metadata"]["replay"]["summary"]["rows"] == 1


def test_flare_view_is_sparse_outside_flare_phase(tmp_path):
    path = tmp_path / "approach.csv"
    path.write_text(
        "tick_id,sequence,time_s,segment,approach_flare_active,"
        "pid_pitch_kp,pid_pitch_ki,pid_pitch_kd,pid_pitch_value,pid_pitch_setpoint\n"
        "1,0,0.0,approach,0,0.01,0.001,0.02,2.0,3.0\n"
        "2,1,0.05,approach,1,0.01,0.001,0.02,2.1,3.1\n",
        encoding="utf-8")
    frames = DashboardState.from_csv(path).snapshot(-1).frames
    assert "flare" not in frames[0]["views"]
    assert frames[1]["views"]["flare"] == frames[1]["views"]["pitch"]


def test_gain_change_is_queued_bumpless_and_records_full_event(tmp_path):
    controller, _scenario, recorder, state, _sample = _live(tmp_path, tune=True)
    pid = controller.pids["pid_brake_l"]
    old_gain, old_output, old_revision = pid.kp, pid.last_output, controller.config_revision
    pending = state.enqueue_gain_update(
        "brake_l", {"kp": old_gain * 1.1},
        revision=old_revision, segment="rollout")
    assert pending["status"] == "pending"
    assert pid.kp == old_gain

    result = state.apply_pending_gain_updates()[0]
    assert result["status"] == "applied"
    assert pid.kp == pytest.approx(old_gain * 1.1)
    assert pid.last_output == pytest.approx(old_output)
    assert controller.config_revision == old_revision + 1
    event = recorder.recent_events[-1]
    assert event.event == "gain_change_applied"
    assert set(event.data) >= {
        "before", "after", "old_revision", "revision", "segment",
        "request_sequence", "matrix_run_id",
    }
    recorder.finish()


def test_stale_segment_rejected_and_revert_uses_same_queue(tmp_path):
    controller, _scenario, recorder, state, sample = _live(tmp_path, tune=True)
    original = controller.pids["pid_brake_l"].kp
    state.enqueue_gain_update("brake_l", {"kp": original * 1.1},
                              revision=0, segment="rollout")
    assert state.apply_pending_gain_updates()[0]["status"] == "applied"
    controller.control_step(0.05, sample, send=False)
    recorder.record(sample, controller, elapsed_s=0.1, dt=0.05)

    state.enqueue_revert(revision=1, segment="rollout")
    reverted = state.apply_pending_gain_updates()[0]
    assert reverted["status"] == "applied"
    assert controller.pids["pid_brake_l"].kp == original
    assert recorder.recent_events[-1].event == "gain_reverted"

    controller.control_step(0.05, sample, send=False)
    recorder.record(sample, controller, elapsed_s=0.15, dt=0.05)
    state.enqueue_gain_update("brake_l", {"kp": original * 1.1},
                              revision=2, segment="rollout")
    controller.segment = FlightSegment.TAXI
    rejected = state.apply_pending_gain_updates()[0]
    assert rejected["status"] == "rejected"
    assert "stale segment" in rejected["reason"]
    assert recorder.recent_events[-1].event == "gain_change_rejected"
    recorder.finish()


@pytest.mark.parametrize("control_mode", ["classical", "sft-shadow"])
def test_active_pid_is_editable_in_classical_and_shadow(tmp_path, control_mode):
    _controller, _scenario, recorder, state, _sample = _live(
        tmp_path, tune=True, control_mode=control_mode)
    assert state.enqueue_gain_update("brake_l", {"kp": 0.11})["status"] == "pending"
    with pytest.raises(PermissionError, match="inactive"):
        state.enqueue_gain_update("roll", {"kp": -6.0})
    recorder.finish()


def test_monitor_replay_and_sft_active_are_read_only(tmp_path):
    _controller, _scenario, recorder, monitor, _sample = _live(tmp_path)
    with pytest.raises(PermissionError):
        monitor.enqueue_gain_update("brake_l", {"kp": 0.11})
    recorder.finish()
    replay = DashboardState.from_csv(recorder.directory)
    with pytest.raises(RuntimeError, match="read-only"):
        replay.enqueue_gain_update("brake_l", {"kp": 0.11})

    _c, _s, active_recorder, active, _t = _live(
        tmp_path / "active", tune=True, control_mode="sft-active")
    with pytest.raises(PermissionError, match="read-only"):
        active.enqueue_gain_update("brake_l", {"kp": 0.11})
    active_recorder.finish()


def test_http_api_is_incremental_pending_and_loopback_only(tmp_path):
    controller, _scenario, recorder, state, _sample = _live(tmp_path, tune=True)
    server = DashboardServer(state, port=0).start()
    base = f"http://{server.address[0]}:{server.address[1]}"
    try:
        with urlopen(base + "/api/state?since=-1", timeout=2) as response:
            first = json.load(response)
        with urlopen(
            base + f"/api/state?since={first['last_sequence']}&run_id={first['run_id']}",
            timeout=2,
        ) as response:
            assert json.load(response)["frames"] == []

        old = controller.pids["pid_brake_l"].kp
        with _post(base + "/api/gains/brake_l", {
            "kp": old * 1.1, "revision": controller.config_revision,
            "segment": "rollout",
        }) as response:
            assert response.status == 202
            assert json.load(response)["status"] == "pending"
        assert controller.pids["pid_brake_l"].kp == old
        assert state.apply_pending_gain_updates()[0]["status"] == "applied"

        with pytest.raises(HTTPError) as error:
            urlopen(base + "/api/state?since=bad", timeout=2)
        assert error.value.code == 400
    finally:
        server.stop()
        recorder.finish()
    with pytest.raises(ValueError):
        DashboardServer(state, host="0.0.0.0", port=0)


def test_server_supplies_ranges_and_html_has_timeline_panels_and_three_scales(tmp_path):
    _controller, _scenario, recorder, state, _sample = _live(tmp_path)
    metadata = state.snapshot(-1).metadata
    brake = next(view for view in metadata["views"] if view["key"] == "brake_l")
    assert set(brake["ranges"]["kp"]) == {"min", "max", "step"}
    assert brake["ranges"]["kp"]["min"] < brake["ranges"]["kp"]["max"]
    html = Path(dashboard_core.__file__).with_name("dashboard.html").read_text(encoding="utf-8")
    for marker in (
        'id="live"', 'id="timeline"', '<option value="30">30 sec</option>',
        '<option value="60">60 sec</option>', '<option value="120">120 sec</option>',
        '<option value="all">Full run</option>', '/api/state?since=${lastSequence}',
        'runId!==data.run_id', 'id="chartSignal"', 'id="chartCommand"',
        'id="chartTerms"', 'Telemetry (99)', 'Save candidate',
    ):
        assert marker in html
    assert "const ranges" not in html
    recorder.finish()


def test_save_candidate_is_full_non_destructive_config(tmp_path):
    scenario = scenario_for_matrix_run("Б.1.1/1")
    controller, _scenario, recorder, state, sample = _live(
        tmp_path, tune=True, scenario=scenario)
    original = scenario.control_for("mc21", FlightSegment.ROLLOUT).brake_l["kp"]
    state.enqueue_gain_update("brake_l", {"kp": original * 1.1},
                              revision=controller.config_revision, segment="rollout")
    state.apply_pending_gain_updates()
    controller.control_step(0.05, sample, send=False)
    recorder.record(sample, controller, elapsed_s=0.1, dt=0.05)
    candidate_path = state.save_candidate()
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    assert candidate_path.name == "rollout-1.json"
    assert candidate["matrix_run_id"] == "Б.1.1/1"
    assert candidate["effective_config"]["brake_l"]["kp"] == pytest.approx(original * 1.1)
    assert set(candidate["hashes"]) == {
        "matrix_catalog_sha256", "matrix_source_sha256", "matrix_row_sha256",
        "base_config_sha256", "effective_config_sha256",
    }
    assert scenario.control_for("mc21", FlightSegment.ROLLOUT).brake_l["kp"] == original
    recorder.finish()


def test_promotion_validates_and_creates_sparse_tuned_override(tmp_path):
    scenario = scenario_for_matrix_run("Б.1.1/1")
    controller, _scenario, recorder, state, sample = _live(
        tmp_path, tune=True, scenario=scenario)
    original = controller.pids["pid_brake_l"].kp
    state.enqueue_gain_update("brake_l", {"kp": original * 1.1}, revision=0,
                              segment="rollout")
    state.apply_pending_gain_updates()
    controller.control_step(0.05, sample, send=False)
    recorder.record(sample, controller, elapsed_s=0.1, dt=0.05)
    candidate = state.save_candidate()
    recorder.finish({"stop_reason": "completed", "conditions_valid": True})
    report_path = recorder.directory / "report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report.update(status="PASS", acceptance_valid=True, recording_failed=False,
                  recording_error=None)
    report["metrics"]["dropout_samples"] = 0
    report_path.write_text(json.dumps(report), encoding="utf-8")

    output = promote_candidate(candidate, verify_replay=True)
    promoted = json.loads(output.read_text(encoding="utf-8"))
    controls = promoted["aircraft_controls"]["mc21"]
    assert controls["statuses"]["rollout"] == "tuned"
    assert controls["run_overrides"]["Б.1.1/1"]["rollout"] == {
        "brake_l": {"kp": pytest.approx(original * 1.1)}}

    with pytest.raises(PromotionError, match="accepted требует PASS") as accepted_error:
        promote_candidate(
            candidate, accepted=True, evidence_root=tmp_path,
            verify_replay=False)
    assert "Б.1.1/1" in str(accepted_error.value)  # tuning-run is not fixed-config evidence

    failed = dict(report, status="FAIL")
    report_path.write_text(json.dumps(failed), encoding="utf-8")
    with pytest.raises(PromotionError, match="не прошёл приёмку"):
        promote_candidate(candidate, verify_replay=False)
    report_path.write_text(json.dumps(report), encoding="utf-8")

    manifest_path = recorder.directory / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["matrix_rows"]["rollout"]["№"] = -1
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(PromotionError, match="matrix row hash"):
        promote_candidate(candidate, verify_replay=False)
    manifest = recorder.manifest
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    changed_manifest = json.loads(json.dumps(manifest))
    changed_manifest["effective_configs"]["rollout"]["control"]["brake_l"]["kp"] *= 1.01
    manifest_path.write_text(json.dumps(changed_manifest), encoding="utf-8")
    with pytest.raises(PromotionError, match="config hash"):
        promote_candidate(candidate, verify_replay=False)
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    tampered = json.loads(candidate.read_text(encoding="utf-8"))
    tampered["hashes"]["effective_config_sha256"] = "0" * 64
    candidate.write_text(json.dumps(tampered), encoding="utf-8")
    with pytest.raises(PromotionError, match="hash mismatch"):
        promote_candidate(candidate, verify_replay=False)


def test_legacy_roman_csv_keeps_missing_pid_terms_unavailable(tmp_path):
    path = tmp_path / "roman.csv"
    path.write_text(
        "time_s,ground_speed_kt,ra_ft,ias_kt,pitch_deg,roll_deg,vs_fpm,"
        "track_magnetic_deg,roll_kp,pitch_kp,speed_kp\n"
        "0.0,150,1000,140,2.0,1.0,-750,75,-7,0.01,0.2\n",
        encoding="utf-8")
    snapshot = DashboardState.from_csv(path).snapshot(-1)
    roll = snapshot.frames[0]["views"]["roll"]
    assert roll["value"] == 1.0
    assert roll["kp"] == -7.0
    assert roll["i"] is None and roll["d"] is None
