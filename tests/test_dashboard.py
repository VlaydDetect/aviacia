import json
from types import SimpleNamespace
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from ismpu.control.system import ControllingSystem
from ismpu.envs.scenario import Scenario
from ismpu.gui.dashboard import DashboardServer, DashboardState, VIEW_SPECS
from ismpu.runtime.run_recorder import RunRecorder

from tests.fakes import telemetry


def configured_controller():
    controller = ControllingSystem()
    scenario = Scenario.from_preset("default")
    scenario.apply_control(controller, "mc21")
    sample = telemetry(groundspeed_ms=75.0)
    controller.control_step(0.05, sample, send=False)
    return controller, scenario, sample


def test_dashboard_has_nine_views_for_eight_unique_pids():
    assert [view.label for view in VIEW_SPECS] == [
        "Roll", "Pitch", "Flare", "Air Speed", "Steer",
        "Brake L", "Brake R", "Reverse L", "Reverse R",
    ]
    assert len({view.pid_key for view in VIEW_SPECS}) == 8
    assert next(view for view in VIEW_SPECS if view.key == "flare").pid_key == "pitch"


def test_monitor_only_and_npgs_tuning_locks(tmp_path):
    controller, scenario, _ = configured_controller()
    monitor = DashboardState(controller, scenario=scenario, export_root=tmp_path)
    with pytest.raises(PermissionError):
        monitor.update_gains("roll", {"kp": -6.0})

    tuning = DashboardState(
        controller,
        scenario=scenario,
        tune_enabled=True,
        npgs_active=True,
        export_root=tmp_path,
    )
    result = tuning.update_gains("roll", {"kp": -6.0, "ki": 0.01})
    assert result["kp"] == -6.0
    with pytest.raises(PermissionError):
        tuning.update_gains("brake_l", {"kp": 0.2})
    with pytest.raises(ValueError):
        tuning.update_gains("roll", {"kp": "nan"})


def test_gain_change_increments_config_revision_and_is_recorded(tmp_path):
    controller, scenario, _ = configured_controller()
    recorder = RunRecorder(
        root=tmp_path, backend="xplane", aircraft_profile="mc21", scenario=scenario)
    state = DashboardState(
        controller, scenario=scenario, recorder=recorder, tune_enabled=True)
    revision = controller.config_revision

    state.update_gains("roll", {"kp": -6.0})

    assert controller.config_revision == revision + 1
    assert recorder.recent_events[-1].event == "gains"
    recorder.finish({"stop_reason": "interrupted"})


def test_capture_export_and_replay_common_run(tmp_path):
    controller, scenario, sample = configured_controller()
    recorder = RunRecorder(
        root=tmp_path / "runs",
        backend="xplane",
        aircraft_profile="a330-300",
        scenario=scenario,
        start="rollout",
    )
    recorder.record(sample, controller, elapsed_s=0.05)
    recorder.finish()

    state = DashboardState(
        controller,
        sim=SimpleNamespace(
            backend_name="xplane", aircraft_profile_name="a330-300"
        ),
        scenario=scenario,
        recorder=recorder,
        tune_enabled=True,
    )
    state.capture(elapsed_s=0.05)
    payload = state.payload()
    assert len(payload["views"]) == 9
    assert payload["views"][4]["latest"]["segment"] == "rollout"
    assert payload["header"]["aircraft_profile"] == "a330-300"
    assert set(payload["header"]["segment_sources"]) == {
        "approach", "rollout", "taxi",
    }
    assert set(payload["header"]["segment_conditions"]) == {
        "approach", "rollout", "taxi",
    }
    assert payload["header"]["recording_failed"] is False
    assert state.export_gains().is_file()

    replay = DashboardState.from_csv(recorder.directory)
    replay_payload = replay.payload()
    assert replay_payload["replay"]["summary"]["rows"] == 1
    assert replay_payload["views"][0]["locked"] is True
    assert replay_payload["views"][5]["latest"]["kp"] is not None


def test_dashboard_http_api_is_local_and_monitor_only():
    controller, scenario, _ = configured_controller()
    state = DashboardState(controller, scenario=scenario)
    state.capture(elapsed_s=0.1)
    server = DashboardServer(state, port=0).start()
    base = f"http://{server.address[0]}:{server.address[1]}"
    try:
        with urlopen(base + "/api/views", timeout=2) as response:
            views = json.load(response)
        assert len(views) == 9

        request = Request(
            base + "/api/gains/roll",
            data=b'{"kp": -5}',
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with pytest.raises(HTTPError) as error:
            urlopen(request, timeout=2)
        assert error.value.code == 403
    finally:
        server.stop()

    with pytest.raises(ValueError):
        DashboardServer(state, host="0.0.0.0", port=0)


def test_dashboard_replays_roman_csv(tmp_path):
    path = tmp_path / "roman.csv"
    path.write_text(
        "time_s,ground_speed_kt,ra_ft,ias_kt,pitch_deg,roll_deg,vs_fpm,"
        "track_magnetic_deg,roll_kp,pitch_kp,speed_kp\n"
        "0.0,150,1000,140,2.0,1.0,-750,75,-7,0.01,0.2\n",
        encoding="utf-8",
    )
    replay = DashboardState.from_csv(path)
    payload = replay.payload()

    assert payload["replay"]["summary"]["rows"] == 1
    assert payload["views"][0]["latest"]["value"] == 1.0
    assert payload["views"][1]["latest"]["value"] == 2.0
    assert payload["views"][3]["latest"]["kp"] == 0.2
