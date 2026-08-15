import socket
import struct
import time

import pytest

from ismpu.config.aircraft_profiles import A330_300, get_aircraft_profile
from ismpu.config.runway_profiles import UUEE_06R, parse_ils_station
from ismpu.config.scenarios import SCENARIOS, SegmentConditions
from ismpu.control.channels import ControlsState
from ismpu.control.failures import FailureMode
from ismpu.control.flight import FlightSegment
from ismpu.control.system import ControllingSystem
from ismpu.envs.scenario import ApproachSetup, Scenario, SensorNoise, TouchdownSetup
from ismpu.envs.weather import FrictionProfile, WeatherState
from ismpu.envs.xplane_sim import XPlaneSim
from ismpu.io import datarefs as dr
from ismpu.io.xplane_connector import XPlaneConnector


class DatagramSocket:
    def __init__(self):
        self.sent = []
        self.closed = False

    def settimeout(self, value):
        self.timeout = value

    def sendto(self, packet, address):
        self.sent.append((packet, address))

    def close(self):
        self.closed = True


class MockXPlaneConnector:
    def __init__(self):
        self.values = {name: 0.0 for name in A330_300.subscriptions}
        self.values.update({
            dr.LATITUDE: UUEE_06R.threshold_lat,
            dr.LONGITUDE: UUEE_06R.threshold_lon,
            dr.GROUNDSPEED: 80.0,
            dr.TRUE_PSI: UUEE_06R.heading_true_deg,
            dr.MAG_PSI: UUEE_06R.heading_true_deg,
            dr.MAG_TRACK: UUEE_06R.heading_true_deg,
            dr.RADIO_ALT_FT: 2800.0,
            dr.IAS_KTS: 150.0,
            dr.TAS_KTS: 154.0,
            dr.VVI_FPM: -750.0,
            dr.FLAP_RATIO: 0.75,
            dr.NAV1_GS_FLAG: 0.0,
            dr.NAV1_FROM_TO: 1.0,
        })
        self.writes = []
        self.positions = []
        self.commands = []
        self.pauses = []
        self.closed = False
        self.subscribe_calls = []

    def subscribe(self, datarefs, **kwargs):
        self.subscribed = tuple(datarefs)
        self.subscribe_calls.append((self.subscribed, kwargs))

    def clear_samples(self):
        self.commands.append("clear_samples")

    def snapshot(self, **kwargs):
        return dict(self.values)

    def value(self, name, **kwargs):
        return self.values.get(name)

    def send_dref(self, name, value):
        self.writes.append((name, float(value)))
        self.values[name] = float(value)

    def send_position(self, **kwargs):
        self.positions.append(kwargs)

    def sendCTRL(self, **kwargs):
        self.commands.append(("CTRL", kwargs))

    def send_command(self, command):
        self.commands.append(command)

    def sendCMND(self, command):
        self.commands.append(("CMND", command))

    def reload_aircraft(self):
        self.commands.append("reload")

    def fix_all_systems(self):
        self.commands.append("fix")

    def pause(self, flag):
        self.pauses.append(flag)

    def close(self):
        self.closed = True


class ScriptedXPlaneConnector(MockXPlaneConnector):
    def __init__(self, frames):
        super().__init__()
        self.frames = iter(frames)

    def snapshot(self, **kwargs):
        try:
            self.values.update(next(self.frames))
        except StopIteration:
            pass
        return dict(self.values)


def _xplane(mock, **kwargs):
    return XPlaneSim(
        connector=mock,
        reload_each_reset=False,
        settle_s=0.0,
        ils_verify_timeout_s=0.0,
        **kwargs,
    )


def test_rref_subscription_packet_and_freshness():
    sock = DatagramSocket()
    connector = XPlaneConnector(sock=sock, start_receiver=False)
    connector.subscribe((dr.LATITUDE,), frequency_hz=20)

    header, frequency, index, name = struct.unpack("<4sxii400s", sock.sent[0][0])
    assert header == b"RREF"
    assert frequency == 20
    assert index == 1
    assert name.rstrip(b"\0").decode() == dr.LATITUDE

    packet = b"RREF\0" + struct.pack("<if", index, 55.9)
    connector.inject_rref_packet(packet)
    assert connector.value(dr.LATITUDE, max_age_s=1.0) == pytest.approx(55.9)
    connector.inject_rref_packet(packet, timestamp=time.monotonic() - 2.0)
    assert connector.value(dr.LATITUDE, max_age_s=1.0) is None

    connector.close()
    assert sock.closed
    unsubscribe = struct.unpack("<4sxii400s", sock.sent[-1][0])
    assert unsubscribe[1] == 0


def test_profile_rejects_unknown_aircraft_and_clamps_commands():
    mc21 = get_aircraft_profile("mc21")
    with pytest.raises(ValueError, match="не имеет привязки X-Plane"):
        XPlaneSim(connector=MockXPlaneConnector(), aircraft_profile=mc21)
    command = ControlsState(
        cmd_aileron=100.0,
        cmd_elevator=-2.0,
        cmd_rudder=3.0,
        cmd_throttle_norm=2.0,
    )
    values = A330_300.airborne_commands(command)
    assert values[dr.YOKE_ROLL_RATIO] == 1.0
    assert values[dr.YOKE_PITCH_RATIO] == -1.0
    assert values[dr.YOKE_HEADING_RATIO] == 1.0
    assert values[A330_300.throttle_refs[0]] == 1.0


def test_earth_nav_parser_finds_requested_localizer(tmp_path):
    nav = tmp_path / "earth_nav.dat"
    nav.write_text(
        "I\n1200 Version\n"
        "4 55.980000 37.450000 622 11170 18 75.0 IUU6 UUEE UU 06R ILS-cat-I\n",
        encoding="utf-8",
    )
    station = parse_ils_station(nav, "UUEE", "06R")
    assert station.frequency_hz == 111_700_000
    assert station.ident == "IUU6"


def test_xplane_reset_supports_approach_and_rollout(tmp_path):
    custom = tmp_path / "Custom Data"
    custom.mkdir()
    (custom / "earth_nav.dat").write_text(
        "4 55.980000 37.450000 622 11170 18 75.0 IUU6 UUEE UU 06R ILS\n",
        encoding="utf-8",
    )
    mock = MockXPlaneConnector()
    sim = _xplane(mock, xplane_root=tmp_path)
    scenario = Scenario.from_preset("default")

    approach = sim.reset(scenario, start="approach")
    assert sim.engaged
    assert sim.ils_station.frequency_hz == 111_700_000
    assert mock.positions[-1]["elevation_m"] > UUEE_06R.elevation_m + 800.0
    assert approach.valid
    assert approach.approach_inputs is not None

    mock.values.update({name: 1.0 for name in A330_300.gear_refs})
    rollout = sim.reset(scenario, start="rollout")
    assert mock.positions[-1]["elevation_m"] < UUEE_06R.elevation_m + 2.0
    assert rollout.main_gear_contact


def test_failed_approach_setup_releases_overrides_and_pause(tmp_path):
    mock = MockXPlaneConnector()
    sim = _xplane(mock, xplane_root=tmp_path)

    with pytest.raises(FileNotFoundError):
        sim.reset(Scenario.from_preset("default"), start="approach")

    writes = dict(mock.writes)
    assert not sim.engaged
    assert mock.pauses[-1] is False
    assert writes[dr.OVERRIDE_ROLL] == 0.0
    assert writes[dr.OVERRIDE_TOE_BRAKES] == 0.0
    sim.close()


def test_commands_failures_and_close_release_overrides():
    mock = MockXPlaneConnector()
    sim = _xplane(mock)
    scenario = Scenario.from_preset(
        "default", failures=(FailureMode.ENGINE_OUT_LEFT,))
    sim.reset(scenario, start="rollout")
    assert FailureMode.ENGINE_OUT_LEFT in sim.active_failures

    command = ControlsState(
        cmd_brake_l=2.0,
        cmd_brake_r=-1.0,
        cmd_rev_l=-2.0,
        cmd_rev_r=1.0,
        cmd_rudder=2.0,
    )
    sim.step(command)
    writes = dict(mock.writes)
    assert writes[dr.LEFT_BRAKE_RATIO] == 1.0
    assert writes[dr.RIGHT_BRAKE_RATIO] == 0.0
    assert writes[A330_300.throttle_refs[0]] == -1.0
    assert writes[A330_300.throttle_refs[1]] == 0.0

    sim.close()
    assert mock.closed
    writes = dict(mock.writes)
    assert writes[dr.OVERRIDE_ROLL] == 0.0
    assert writes[dr.OVERRIDE_PITCH] == 0.0
    assert writes[dr.OVERRIDE_HEADING] == 0.0
    assert writes[dr.OVERRIDE_THROTTLES] == 0.0
    assert writes[dr.OVERRIDE_TOE_BRAKES] == 0.0


def test_missing_or_stale_required_data_makes_xplane_telemetry_invalid():
    mock = MockXPlaneConnector()
    del mock.values[dr.LATITUDE]
    sim = _xplane(mock)
    assert not sim.read_telemetry().valid
    sim.close()


def test_reload_renews_subscriptions_and_sensor_dropout_is_applied():
    mock = MockXPlaneConnector()
    sim = XPlaneSim(
        connector=mock,
        reload_each_reset=True,
        ready_timeout_s=0.0,
        settle_s=0.0,
    )
    scenario = Scenario.from_preset(
        "default", sensor_noise=SensorNoise(dropout_prob=1.0))
    result = sim.reset(scenario, start="rollout")

    assert len(mock.subscribe_calls) == 2
    assert "clear_samples" in mock.commands
    assert not result.valid
    sim.close()


def test_scenario_roundtrip_and_variable_friction_application():
    weather = WeatherState(
        gust_kts=12.0,
        friction_profile=FrictionProfile(((0.0, 2.0), (100.0, 5.0))),
    )
    scenario = Scenario.from_preset(
        "default",
        seed=17,
        weather=weather,
        approach=ApproachSetup(loc_offset_dots=0.25, gs_offset_dots=-0.2),
        touchdown=TouchdownSetup(lateral_offset_m=1.5),
        sensor_noise=SensorNoise(heading_sigma_deg=0.1),
    )
    assert Scenario.from_dict(scenario.to_dict()).to_dict() == scenario.to_dict()

    mock = MockXPlaneConnector()
    sim = _xplane(mock)
    sim.reset(scenario, start="rollout")
    assert dict(mock.writes)[dr.WX_RUNWAY_FRICTION] == 2.0
    sim.update(150.0)
    assert dict(mock.writes)[dr.WX_RUNWAY_FRICTION] == 5.0
    sim.close()


def test_scripted_xplane_full_approach_rollout_taxi_chain(tmp_path):
    custom = tmp_path / "Custom Data"
    custom.mkdir()
    (custom / "earth_nav.dat").write_text(
        "4 55.980000 37.450000 622 11170 18 75.0 IUU6 UUEE UU 06R ILS\n",
        encoding="utf-8",
    )
    gear_air = {name: 0.0 for name in A330_300.gear_refs}
    gear_ground = {name: 1.0 for name in A330_300.gear_refs}

    def frame(ra, speed, gear):
        return {
            dr.LATITUDE: UUEE_06R.threshold_lat,
            dr.LONGITUDE: UUEE_06R.threshold_lon,
            dr.GROUNDSPEED: speed,
            dr.TRUE_PSI: UUEE_06R.heading_true_deg,
            dr.MAG_PSI: UUEE_06R.heading_true_deg,
            dr.MAG_TRACK: UUEE_06R.heading_true_deg,
            dr.MAGNETIC_VARIATION: 0.0,
            dr.RADIO_ALT_FT: ra,
            dr.IAS_KTS: max(10.0, speed / 0.514444),
            dr.TAS_KTS: max(10.0, speed / 0.514444),
            dr.VVI_FPM: -700.0 if not any(gear.values()) else 0.0,
            dr.FLAP_RATIO: 0.75,
            dr.NAV1_GS_FLAG: 0.0,
            dr.NAV1_FROM_TO: 1.0,
            dr.NAV1_HDEF_DOTS: 0.0,
            dr.NAV1_VDEF_DOTS: 0.0,
            **gear,
        }

    frames = [
        frame(1000.0, 77.0, gear_air),
        frame(500.0, 75.0, gear_air),
        frame(100.0, 72.0, gear_air),
        frame(5.0, 70.0, gear_ground),
        frame(2.0, 40.0, gear_ground),
        # X-Plane publishes groundspeed in m/s; 0.4 m/s is below the
        # configured 2-knot taxi termination threshold.
        frame(2.0, 0.4, gear_ground),
    ]
    mock = ScriptedXPlaneConnector(frames)
    sim = _xplane(mock, xplane_root=tmp_path)
    scenario = Scenario.from_preset("default")
    controller = ControllingSystem(sim)
    scenario.apply_control(controller, "a330-300")

    first = sim.reset(scenario, start="approach")
    assert controller.begin_flight(first) is FlightSegment.APPROACH
    assert sim.warm_up()

    finished = False
    for _ in range(8):
        finished = controller.control_step(0.05)
        if finished:
            break

    assert finished
    assert controller.segment is FlightSegment.ROLLOUT
    assert sim._mode == "rollout"
    assert any(name == dr.YOKE_ROLL_RATIO for name, _ in mock.writes)
    assert any(name == dr.LEFT_BRAKE_RATIO for name, _ in mock.writes)

    assert controller.hand_over_to_taxi()
    assert sim._mode == "taxi"
    sim.close()


def test_segment_conditions_are_applied_as_a_delta_without_repeating_weather():
    mock = MockXPlaneConnector()
    sim = _xplane(mock)
    scenario = SCENARIOS["b_4_2_through_engine_out"]
    left = A330_300.engine_indices[0]
    engine_ref = f"{dr.FAIL_ENGINE}[{left}]"
    reverse_ref = f"{dr.FAIL_REVERSER}[{left}]"

    sim.enter_segment(scenario, FlightSegment.APPROACH)
    assert sim.active_failures == frozenset({FailureMode.ENGINE_OUT_LEFT})
    approach_writes = list(mock.writes)
    assert approach_writes.count((engine_ref, float(dr.FAILURE_ENUM_INOP))) == 1

    boundary = len(mock.writes)
    sim.enter_segment(scenario, FlightSegment.ROLLOUT)
    transition_writes = mock.writes[boundary:]
    assert sim.active_failures == frozenset({
        FailureMode.ENGINE_OUT_LEFT,
        FailureMode.REVERSE_LEFT_FAIL,
    })
    assert (reverse_ref, float(dr.FAILURE_ENUM_INOP)) in transition_writes
    assert all(name != engine_ref for name, _ in transition_writes)
    assert all(name != dr.WX_CHANGE_MODE for name, _ in transition_writes)


def test_ignored_xplane_failure_participates_in_segment_delta_and_is_cleared():
    mock = MockXPlaneConnector()
    sim = _xplane(mock)
    base = SCENARIOS["default"]
    gear = SegmentConditions(
        weather=base.conditions_for(FlightSegment.APPROACH).weather,
        failures=frozenset({FailureMode.GEAR_CONFIG}),
    )
    scenario = Scenario(
        scenario_id="unsupported-delta",
        seed=0,
        aircraft_controls=base.aircraft_controls,
        conditions={
            FlightSegment.APPROACH: gear,
            FlightSegment.ROLLOUT: gear,
            FlightSegment.TAXI: base.conditions_for(FlightSegment.TAXI),
        },
    )

    sim.enter_segment(scenario, FlightSegment.APPROACH)
    sim.enter_segment(scenario, FlightSegment.ROLLOUT)
    assert sim.ignored_failures == frozenset({FailureMode.GEAR_CONFIG})
    sim.enter_segment(scenario, FlightSegment.TAXI)
    assert sim.ignored_failures == frozenset()
