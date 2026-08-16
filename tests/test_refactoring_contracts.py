import ast
import inspect
import struct
from copy import deepcopy
from pathlib import Path

import pytest

from ismpu.config.json_config import (
    scenario_from_document,
    scenario_to_document,
)
from ismpu.config.runway_profiles import UUEE_06R
from ismpu.config.segments import FlightSegment
from ismpu.control.failures import FailureMode
from ismpu.control.runway_tracker import RunwayTracker
from ismpu.control.system import ControllingSystem
from ismpu.envs.ics_sim import ICSSim
from ismpu.config.scenarios import Scenario
from ismpu.io.xplane_connector import XPlaneConnector
from ismpu.envs.xplane_sim import XPlaneSim
from ismpu.gui.dashboard import DashboardState
from ismpu.runtime.run_recorder import RunRecorder
from tests.fakes import FakeConnector, static_sim, telemetry
from tests.test_xplane_backend import MockXPlaneConnector


class DatagramSocket:
    def __init__(self):
        self.sent = []
        self.closed = False

    def settimeout(self, timeout):
        self.timeout = timeout

    def sendto(self, packet, address):
        self.sent.append((packet, address))

    def close(self):
        self.closed = True


def test_production_cli_uses_the_unified_runtime_without_working_ics(monkeypatch):
    from ismpu.runtime import loop

    captured = {}
    monkeypatch.setattr(loop, "main", lambda **kwargs: captured.update(kwargs))

    assert loop.cli(["default", "--aircraft-profile", "mc21", "--start", "approach"]) == 0
    assert captured["backend"] == "ics"
    assert captured["aircraft_profile"] == "mc21"
    assert captured["start"] == "approach"
    assert loop.cli(["--aircraft-profile", "mc21", "--run-id", "Б.2.2/4"]) == 0
    assert captured["run_id"] == "Б.2.2/4"
    assert "working_ics" not in inspect.getsource(loop)
    assert "live_main" not in inspect.getsource(loop)


def test_production_modules_never_import_the_working_ics_reference():
    """Эталон разрешён тестам, но не должен стать скрытым runtime dependency."""
    package = Path(__file__).resolve().parents[1] / "ismpu"
    offenders = []
    for path in package.rglob("*.py"):
        if "working_ics" in path.parts:
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            modules = []
            if isinstance(node, ast.Import):
                modules = [item.name for item in node.names]
            elif isinstance(node, ast.ImportFrom):
                modules = [node.module or ""]
            if any(name.startswith("ismpu.working_ics") for name in modules):
                offenders.append(str(path.relative_to(package)))
    assert offenders == []


def test_runtime_uses_explicit_matrix_run_id_without_telemetry_guessing(monkeypatch):
    from ismpu.runtime import loop

    sim, _ = static_sim()
    captured = {}

    def unexpected_guess(*args, **kwargs):
        raise AssertionError("telemetry guess")

    monkeypatch.setattr(loop, "build_sim", lambda *args, **kwargs: sim)
    monkeypatch.setattr(loop, "select_for_telemetry", unexpected_guess)
    monkeypatch.setattr(
        loop,
        "run",
        lambda controller, backend, scenario, **kwargs: captured.update(
            scenario=scenario, start=kwargs["start"]),
    )

    with pytest.raises(ValueError, match="--run-id"):
        loop.main("Б.2.2", backend="ics", aircraft_profile="mc21")
    loop.main(backend="ics", aircraft_profile="mc21", run_id="Б.2.2/4")

    assert captured["scenario"].matrix_runs == {
        FlightSegment.ROLLOUT: "Б.2.2/4",
    }
    assert captured["start"] == "rollout"


def test_xplane_connector_emits_the_native_wire_contract():
    """DREF/CMND/VEHS bytes are the contract; a duplicate client is not an oracle."""
    sock = DatagramSocket()
    connector = XPlaneConnector(sock=sock, start_receiver=False)

    connector.send_dref("sim/test/value", 0.25)
    connector.send_command("sim/operation/pause_on")
    connector.send_position(
        lat=1.0,
        lon=2.0,
        elevation_m=3.0,
        roll_deg=4.0,
        pitch_deg=5.0,
        heading_true_deg=6.0,
    )

    expected_position = struct.pack(
        "<4sxidddfff", b"VEHS", 0, 1.0, 2.0, 3.0, 6.0, 5.0, 4.0
    )
    assert [packet for packet, _ in sock.sent] == [
        struct.pack("<4sxf500s", b"DREF", 0.25, b"sim/test/value"),
        struct.pack("<4sx500s", b"CMND", b"sim/operation/pause_on"),
        expected_position,
        expected_position,
    ]


def test_subscription_retries_with_diagnostics():
    sock = DatagramSocket()
    connector = XPlaneConnector(sock=sock, start_receiver=False)
    with pytest.raises(TimeoutError, match=r"127\.0\.0\.1:49000.*sim/test"):
        connector.subscribe(
            ["sim/test"], frequency_hz=20, timeout_s=0.03, retry_interval_s=0.01
        )
    packets = [struct.unpack("<4sxii400s", packet) for packet, _ in sock.sent]
    assert packets[0][2] == 1
    assert len(packets) >= 2


def test_ics_shutdown_is_idempotent_and_releases_every_channel():
    connector = FakeConnector()
    sim = ICSSim(connector=connector, aircraft_profile="mc21")
    first = sim.shutdown(frames=2, dt=0.0)
    second = sim.shutdown(frames=50, dt=0.0)
    assert first is second
    assert first.successful
    assert connector.closed
    assert len(connector.sent_outputs) == 2
    assert all(packet.ControlValidMask == 0 for packet in connector.sent_outputs)
    assert all(int(packet.ControlMode) == 0 for packet in connector.sent_outputs)


def test_scenario_json_v3_supports_unregistered_profile_roundtrip():
    original = Scenario.from_preset("default", scenario_id="external-json", seed=17)
    document = scenario_to_document(original)
    document["aircraft_controls"]["experimental"] = deepcopy(
        document["aircraft_controls"]["mc21"]
    )
    document["aircraft_controls"]["experimental"]["rollout"]["pids"]["brake_l"]["kp"] = 0.123
    restored = scenario_from_document(document)
    assert restored.scenario_id == "external-json"
    assert restored.control_for("experimental", FlightSegment.ROLLOUT).brake_l["kp"] == 0.123
    assert scenario_to_document(restored) == document


def test_scenario_json_v2_remains_readable_after_control_profile_split():
    document = scenario_to_document(Scenario.from_preset("default"))
    document["schema_version"] = 2
    document.pop("matrix_runs")
    for profile in document["aircraft_controls"].values():
        profile["draft_segments"] = [
            segment for segment, status in profile.pop("statuses").items()
            if status == "draft"
        ]
        profile.pop("run_overrides")

    restored = scenario_from_document(document)
    assert restored.is_draft("mc21", FlightSegment.ROLLOUT)
    assert restored.control_for("mc21", FlightSegment.APPROACH).name == "ics_clear_weather"


@pytest.mark.parametrize("profile", ["mc21", "a330-300"])
def test_scenario_json_v1_requires_an_explicit_legacy_profile_override_for_a330(profile):
    v2 = scenario_to_document(Scenario.from_preset("default"))
    rollout = v2["aircraft_controls"]["mc21"]["rollout"]
    legacy = {
        "schema_version": 1,
        "scenario_id": "legacy",
        "seed": 5,
        "control": {
            "name": "external-control",
            "draft": False,
            "pids": rollout["pids"],
            "guidance": rollout["guidance"],
            "mixing": rollout["mixing"],
            "trajectory": rollout["trajectory"],
            "approach": "default",
        },
        "weather": v2["conditions"]["rollout"]["weather"],
        "failures": [],
        "approach": {},
        "touchdown": {},
        "sensor_noise": {},
    }
    restored = scenario_from_document(legacy, legacy_aircraft_profile=profile)
    assert set(restored.aircraft_controls) == {profile}
    assert restored.control_for(profile, FlightSegment.ROLLOUT).brake_l == rollout["pids"]["brake_l"]
    if profile == "a330-300":
        assert restored.control_for(profile, FlightSegment.APPROACH).name == \
            "xplane_a330_approach"


def test_scenario_from_dict_exposes_v1_profile_override_and_preserves_matrix_metadata():
    v2 = scenario_to_document(Scenario.from_preset("default"))
    rollout = v2["aircraft_controls"]["mc21"]["rollout"]
    legacy = {
        "schema_version": 1,
        "scenario_id": "legacy-matrix",
        "seed": 7,
        "control": {
            "name": "external-control",
            "failure": "ENGINE_OUT_LEFT",
            "draft": True,
            "matrix_code": "Б.4.2",
            "pids": rollout["pids"],
            "guidance": rollout["guidance"],
            "mixing": rollout["mixing"],
            "trajectory": rollout["trajectory"],
            "approach": "a_4_1_engine_out_high",
        },
        "weather": v2["conditions"]["rollout"]["weather"],
    }
    restored = Scenario.from_dict(legacy, legacy_aircraft_profile="mc21")
    assert restored.control_for("mc21", FlightSegment.APPROACH).name == \
        "a_4_1_engine_out_high"
    assert restored.matrix_codes == {
        FlightSegment.APPROACH: "Б.4.2",
        FlightSegment.ROLLOUT: "Б.4.2",
    }
    assert restored.conditions_for(FlightSegment.APPROACH).failures == frozenset({
        FailureMode.ENGINE_OUT_LEFT,
    })


def test_scenario_json_rejects_unknown_fields():
    document = scenario_to_document(Scenario.from_preset("default"))
    document["surprise"] = True
    with pytest.raises(ValueError, match="неизвестные поля"):
        scenario_from_document(document)


def test_runway_profile_delegates_geometry_to_tracker():
    tracker = RunwayTracker()
    assert UUEE_06R.length_m == pytest.approx(tracker.runway_length_m())
    assert UUEE_06R.point_on_centerline(1000.0) == pytest.approx(
        tracker.point_on_centerline(1000.0))


def test_dashboard_http_queue_applies_only_at_tick_boundary(tmp_path):
    controller = ControllingSystem()
    scenario = Scenario.from_preset("default")
    scenario.apply_control(controller, "mc21")
    sample = telemetry(groundspeed_ms=75.0)
    controller.control_step(0.05, sample, send=False)
    recorder = RunRecorder(
        root=tmp_path, backend="xplane", aircraft_profile="mc21",
        scenario=scenario)
    recorder.record(sample, controller, elapsed_s=0.05)
    state = DashboardState(
        controller, scenario=scenario, recorder=recorder, tune_enabled=True)
    old = controller.pids["pid_brake_l"].kp
    pending = state.enqueue_gain_update("brake_l", {"kp": old * 1.1})
    assert pending["status"] == "pending"
    assert controller.pids["pid_brake_l"].kp == old
    applied = state.apply_pending_gain_updates()
    assert applied[0]["status"] == "applied"
    assert controller.pids["pid_brake_l"].kp == pytest.approx(old * 1.1)
    recorder.finish()


def test_xplane_ignores_failures_outside_rollout_contract():
    sim = XPlaneSim(
        connector=MockXPlaneConnector(),
        reload_each_reset=False,
        settle_s=0.0,
    )
    sim.inject_failure(FailureMode.GEAR_CONFIG)
    assert FailureMode.GEAR_CONFIG not in sim.active_failures
    assert FailureMode.GEAR_CONFIG in sim.ignored_failures
    sim.inject_failure(FailureMode.NWS_FAIL)
    assert FailureMode.NWS_FAIL in sim.active_failures
