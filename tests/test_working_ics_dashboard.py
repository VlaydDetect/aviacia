"""Characterization tests for the bench-validated ``working_ics`` dashboard."""

from __future__ import annotations

import json
from dataclasses import fields
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from ismpu.working_ics import dashboard
from ismpu.working_ics.dashboard import DashboardServer, DashboardState, HTML_PATH
from ismpu.working_ics.pid_controller import ClearWeatherILSController, ControllerConfig
from ismpu.working_ics.protocol import ICSInputs
from ismpu.working_ics.runner import DEFAULT_CONFIG


def _controller() -> ClearWeatherILSController:
    return ClearWeatherILSController(ControllerConfig.from_json(DEFAULT_CONFIG))


def _inputs(**overrides) -> ICSInputs:
    values = {field.name: 0 for field in fields(ICSInputs)}
    values.update({
        "AgentIsActive": 1,
        "RadioAltitudeValid": 1,
        "RadioAltitude": 500.0,
        "IndicatedAirspeed": 145.0,
        "TrueAirspeed": 145.0,
        "GroundSpeed": 142.0,
        "VerticalSpeed": -700.0,
        "PitchAngle": 3.0,
        "RollAngle": 0.5,
        "MagneticHeading": 64.0,
        "TrkAngleMagnetic": 64.0,
        "RunwayHeading": 64.0,
        "FlapsAngle": 27.0,
        "LeftThrottleAngle": 20.0,
        "RightThrottleAngle": 20.0,
    })
    values.update(overrides)
    return ICSInputs(**values)


def _record(state: DashboardState, time_s: float, **overrides) -> None:
    inputs = _inputs(**overrides)
    result = state.controller.update(inputs, 0.05)
    state.record(time_s, inputs, result)


def test_dashboard_records_four_airborne_views_and_diagnostics():
    state = DashboardState(_controller())
    _record(state, 1.2345)

    snapshot = state.snapshot()
    assert snapshot["last_sequence"] == 0
    point = snapshot["points"][0]
    assert point["seq"] == 0
    assert point["t"] == 1.234
    assert set(point) == {"seq", "t", "roll", "pitch", "flare", "speed", "meta"}
    for view in ("roll", "pitch", "flare", "speed"):
        assert set(point[view]) == {"value", "setpoint", "output", "integral"}
    assert point["roll"]["value"] == 0.5
    assert point["pitch"]["value"] == 3.0
    assert point["speed"]["value"] == 145.0
    assert point["flare"]["output"] == 0.0
    assert set(point["meta"]) == {
        "ra", "vs", "loc", "gs", "aoa", "aoa_ref", "mach", "alpha_margin",
        "vapp", "target_ias", "flaps", "flare_armed", "flare", "flare_progress",
        "rudder_cmd", "throttle_cmd", "throttle_target_angle", "warnings",
        "throttle_left", "throttle_right", "thrust_left", "thrust_right", "active",
    }


def test_snapshot_is_incremental_and_a_new_run_resets_sequence(monkeypatch):
    run_ids = iter(("run-a", "run-b"))
    monkeypatch.setattr(dashboard.secrets, "token_hex", lambda _length: next(run_ids))

    first = DashboardState(_controller())
    _record(first, 0.0)
    _record(first, 0.05, RadioAltitude=499.5)
    assert [point["seq"] for point in first.snapshot(-1)["points"]] == [0, 1]
    assert [point["seq"] for point in first.snapshot(0)["points"]] == [1]
    assert first.snapshot(1)["points"] == []
    assert first.snapshot(1)["last_sequence"] == 1
    assert first.run_id == "run-a"

    second = DashboardState(_controller())
    _record(second, 0.0)
    assert second.run_id == "run-b"
    assert second.snapshot()["points"][0]["seq"] == 0


def test_gain_updates_are_immediate_validated_and_share_pitch_with_flare():
    controller = _controller()
    state = DashboardState(controller)

    assert state.update_gains("roll", {"kp": -6.5})["kp"] == -6.5
    flare = state.update_gains("flare", {"kp": 0.25, "ki": 0.005, "kd": 0.07})
    assert flare == {"kp": 0.25, "ki": 0.005, "kd": 0.07}
    assert state.snapshot()["gains"]["pitch"] == flare
    assert controller.pitch_pid.config.kp == 0.25

    with pytest.raises(ValueError, match="unknown loop"):
        state.update_gains("yaw", {"kp": 1.0})
    for invalid in (float("nan"), float("inf"), float("-inf")):
        with pytest.raises(ValueError, match="must be finite"):
            state.update_gains("speed", {"kp": invalid})


def test_http_api_is_incremental_tunable_and_bound_to_loopback():
    state = DashboardState(_controller())
    _record(state, 0.0)
    server = DashboardServer(state, host="127.0.0.1", port=0)
    server.start()
    base_url = f"http://127.0.0.1:{server.port}"
    try:
        assert server.httpd.server_address[0] == "127.0.0.1"
        with urlopen(f"{base_url}/api/state?since=-1", timeout=2.0) as response:
            payload = json.load(response)
        assert payload["run_id"] == state.run_id
        assert payload["last_sequence"] == 0
        assert [point["seq"] for point in payload["points"]] == [0]

        with urlopen(f"{base_url}/api/state?since=0", timeout=2.0) as response:
            assert json.load(response)["points"] == []

        request = Request(
            f"{base_url}/api/gains",
            data=json.dumps({"loop": "speed", "kp": 0.006}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=2.0) as response:
            assert json.load(response)["kp"] == 0.006

        with pytest.raises(HTTPError) as error:
            urlopen(f"{base_url}/api/state?since=bad", timeout=2.0)
        assert error.value.code == 400
    finally:
        server.stop()


def test_dashboard_html_freezes_live_timeline_and_time_windows():
    html = HTML_PATH.read_text(encoding="utf-8")

    for marker in (
        'id="live"',
        'id="timeline"',
        '<option value="30">30 sec</option>',
        '<option value="60">60 sec</option>',
        '<option value="120">120 sec</option>',
        '<option value="all">Full run</option>',
        '/api/state?since=${lastSequence}',
        'runId !== data.run_id',
    ):
        assert marker in html
