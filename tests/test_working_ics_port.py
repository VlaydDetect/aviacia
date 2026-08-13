from types import SimpleNamespace
import socket
from dataclasses import fields

from ismpu.working_ics import runner
from ismpu.working_ics.pid_controller import ClearWeatherILSController, ControllerConfig
from ismpu.working_ics.protocol import (
    AIRBORNE_CONTROL_VALID_MASK,
    ControlModeState,
    ICSInputs,
)
from ismpu.working_ics.rollout_bridge import VlaydRolloutBridge
from ismpu.config.ics import ROLLOUT_CONTROL_MASK
from ismpu.control.channels import ControlsState
from ismpu.io.ics_connector import ControlModeState as BenchControlMode


def test_validated_airborne_packet_contract_is_preserved():
    state = SimpleNamespace(
        IndicatedAirspeed=146.0,
        RadioAltitudeValid=1,
        RadioAltitude=500.0,
    )
    result = SimpleNamespace(
        elevator=0.12,
        aileron=-1.5,
        rudder=0.0,
        throttle_left_rate=0.25,
        throttle_right_rate=0.20,
        throttle_left_hold_norm=0.36,
        throttle_right_hold_norm=0.36,
        loc_dots=-0.03,
        heading_error_deg=0.4,
        target_ias_kt=145.0,
    )

    packet = runner.make_airborne_output(state, result)

    assert packet.ControlValidMask == AIRBORNE_CONTROL_VALID_MASK == 31
    assert packet.ControlMode is ControlModeState.Approach
    assert packet.ModeAIReady == 1
    assert packet.ModeSpeed == 1
    assert packet.ModeThrust == 1
    assert packet.ModeFlareArm == packet.ModeFlare == 0
    assert packet.ModeAlignArm == packet.ModeAlign == 0
    assert packet.ThrottleLeft == packet.ThrottleRight == 0.36


def test_airborne_mode_switches_to_landing_before_the_observed_38ft_dropout():
    approach = SimpleNamespace(RadioAltitudeValid=1, RadioAltitude=40.1)
    landing = SimpleNamespace(RadioAltitudeValid=1, RadioAltitude=40.0)

    assert runner.airborne_control_mode(approach) is ControlModeState.Approach
    assert runner.airborne_control_mode(landing) is ControlModeState.Landing


def test_flare_mode_bit_switches_on_at_100ft_without_arming_other_phase_bits():
    above = SimpleNamespace(
        IndicatedAirspeed=146.0,
        RadioAltitudeValid=1,
        RadioAltitude=100.1,
    )
    at_threshold = SimpleNamespace(
        IndicatedAirspeed=146.0,
        RadioAltitudeValid=1,
        RadioAltitude=100.0,
    )
    result = SimpleNamespace(
        elevator=0.12,
        aileron=-1.5,
        rudder=0.0,
        throttle_left_rate=0.25,
        throttle_right_rate=0.20,
        throttle_left_hold_norm=0.36,
        throttle_right_hold_norm=0.36,
        loc_dots=-0.03,
        heading_error_deg=0.4,
        target_ias_kt=145.0,
    )

    assert runner.make_airborne_output(above, result).ModeFlare == 0
    packet = runner.make_airborne_output(at_threshold, result)
    assert packet.ModeFlare == 1
    assert packet.ModeFlareArm == 0
    assert packet.ModeAlignArm == packet.ModeAlign == 0


def test_flare_mode_bit_clears_at_20ft_while_landing_mode_remains_active():
    above_cutoff = SimpleNamespace(
        IndicatedAirspeed=140.0,
        RadioAltitudeValid=1,
        RadioAltitude=20.1,
    )
    at_cutoff = SimpleNamespace(
        IndicatedAirspeed=140.0,
        RadioAltitudeValid=1,
        RadioAltitude=20.0,
    )
    result = SimpleNamespace(
        elevator=0.05,
        aileron=0.0,
        rudder=0.0,
        throttle_left_rate=0.0,
        throttle_right_rate=0.0,
        throttle_left_hold_norm=0.0,
        throttle_right_hold_norm=0.0,
        loc_dots=0.0,
        heading_error_deg=0.0,
        target_ias_kt=140.0,
    )

    assert runner.make_airborne_output(above_cutoff, result).ModeFlare == 1
    packet = runner.make_airborne_output(at_cutoff, result)
    assert packet.ModeFlare == 0
    assert packet.ControlMode is ControlModeState.Landing


def test_validated_controller_config_is_packaged():
    config = ControllerConfig.from_json(runner.DEFAULT_CONFIG)

    assert config.pitch_pid.kp == 0.2
    assert config.pitch_pid.output_min == -0.5
    assert config.pitch_pid.output_max == 0.5
    assert config.roll_pid.kp == -7
    assert config.landing_flap_fallback == "FLAPS_3"
    assert config.min_pitch_target_deg == -2.0
    assert config.max_pitch_target_deg == 10.0
    assert config.flare_vs_to_pitch_gain_deg_per_fpm == 0.0080
    assert config.flare_pitch_base_deg == 2.35
    assert config.flare_pitch_attitude_damping_gain == 0.10
    assert config.flare_max_pitch_target_deg == 6.5
    assert config.terminal_hold_radio_altitude_ft == 10.0
    assert config.terminal_guidance_cutoff_radio_altitude_ft == 5.0
    assert config.terminal_hold_pitch_target_deg == 6.3


def test_future_go_around_pitch_envelope_does_not_expand_landing_flare():
    config = ControllerConfig.from_json(runner.DEFAULT_CONFIG)

    assert config.max_pitch_target_deg == 10.0
    assert config.flare_max_pitch_target_deg == 6.5
    assert config.flare_max_pitch_target_deg < config.max_pitch_target_deg


def test_roundout_commands_a_material_pitch_increase_before_touchdown():
    def inputs(**overrides):
        return ICSInputs(*[
            overrides.get(field.name, 0) for field in fields(ICSInputs)
        ])

    controller = ClearWeatherILSController(ControllerConfig.from_json(runner.DEFAULT_CONFIG))
    common = {
        "AgentIsActive": 1,
        "RadioAltitudeValid": 1,
        "GroundSpeedValid": 1,
        "GroundSpeed": 141.0,
        "VerticalSpeedValid": 1,
        "IndicatedAirspeedValid": 1,
        "IndicatedAirspeed": 140.0,
        "PitchAngleValid": 1,
        "BodyPitchRateValid": 1,
        "FlapsAngle": 27.0,
    }
    entry = controller.update(inputs(
        **common,
        RadioAltitude=185.0,
        VerticalSpeed=-742.0,
        PitchAngle=3.88,
        BodyPitchRate=0.0,
    ), 0.05)
    roundout = None
    for radio_altitude, vertical_speed, pitch, pitch_rate in (
        (120.0, -735.0, 3.98, 0.12),
        (100.0, -725.0, 4.08, 0.11),
        (80.0, -714.0, 4.14, 0.09),
    ):
        roundout = controller.update(inputs(
            **common,
            RadioAltitude=radio_altitude,
            VerticalSpeed=vertical_speed,
            PitchAngle=pitch,
            BodyPitchRate=pitch_rate,
        ), 0.5)

    assert entry.flare_active
    assert roundout is not None
    assert roundout.target_pitch_deg >= 5.2
    assert roundout.target_pitch_deg > entry.target_pitch_deg + 1.0


def test_terminal_pitch_hold_starts_before_last_five_feet_guidance_cutoff():
    def inputs(**overrides):
        return ICSInputs(*[
            overrides.get(field.name, 0) for field in fields(ICSInputs)
        ])

    config = ControllerConfig.from_json(runner.DEFAULT_CONFIG)
    controller = ClearWeatherILSController(config)
    common = {
        "AgentIsActive": 1,
        "RadioAltitudeValid": 1,
        "GroundSpeedValid": 1,
        "GroundSpeed": 140.0,
        "VerticalSpeedValid": 1,
        "VerticalSpeed": -550.0,
        "IndicatedAirspeedValid": 1,
        "IndicatedAirspeed": 140.0,
        "PitchAngleValid": 1,
        "PitchAngle": 5.7,
        "BodyPitchRateValid": 1,
        "BodyPitchRate": 0.0,
        "RunwayHeadingValid": 1,
        "RunwayHeading": 270.0,
        "TrkAngleMagneticValid": 1,
        "TrkAngleMagnetic": 271.0,
        "RollAngleValid": 1,
        "RollAngle": 0.4,
        "LocDeviationValid": 1,
        "LocDeviation": 0.155,
        "GSDeviationValid": 1,
        "GSDeviation": -0.175,
        "FlapsAngle": 27.0,
    }

    above = controller.update(inputs(**common, RadioAltitude=10.1), 0.25)
    terminal = controller.update(inputs(**common, RadioAltitude=9.9), 0.25)

    assert not above.terminal_hold_active
    assert terminal.terminal_hold_active
    assert terminal.target_heading_deg != 270.0
    assert terminal.target_roll_deg != 0.0
    assert terminal.vertical_correction_deg == 0.0
    assert terminal.target_pitch_deg == config.terminal_hold_pitch_target_deg
    assert terminal.elevator > 0.0

    guidance_cutoff = controller.update(
        inputs(**common, RadioAltitude=4.9),
        0.25,
    )
    assert guidance_cutoff.terminal_hold_active
    assert guidance_cutoff.target_heading_deg == 270.0
    assert guidance_cutoff.target_roll_deg == 0.0

    touchdown = controller.update(inputs(
        **common,
        RadioAltitude=0.3,
        LeftGearWeightOnWheels=1,
    ), 0.05)
    assert not touchdown.terminal_hold_active


def test_live_entrypoint_uses_validated_live_arguments(monkeypatch):
    captured = {}

    def fake_main(argv=None):
        captured["argv"] = argv
        return 17

    monkeypatch.setattr(runner, "main", fake_main)

    assert runner.live_main() == 17
    assert captured["argv"] == [
        "--send",
        "--duration", "600",
        "--dashboard",
        "--dashboard-hold-seconds", "0",
    ]


def test_waits_for_agent_active_without_changing_the_received_sender(monkeypatch):
    inactive = SimpleNamespace(AgentIsActive=0)
    active = SimpleNamespace(AgentIsActive=1)
    received = iter([
        socket.timeout(),
        (active, ("127.0.0.1", 54059)),
    ])
    clock = iter([100.0, 100.1, 100.2])

    def fake_receive(_sock, _timeout):
        item = next(received)
        if isinstance(item, BaseException):
            raise item
        return item

    monkeypatch.setattr(runner, "receive", fake_receive)
    monkeypatch.setattr(runner.time, "monotonic", lambda: next(clock))

    state, sender = runner.wait_for_agent_active(
        object(), inactive, ("127.0.0.1", 3030), 10.0)

    assert state is active
    assert sender == ("127.0.0.1", 54059)


def test_rollout_bridge_preserves_engagement_and_switches_without_off():
    def inputs(**overrides):
        return ICSInputs(*[
            overrides.get(field.name, 0) for field in fields(ICSInputs)
        ])

    bridge = VlaydRolloutBridge(
        object(),
        ("127.0.0.1", 54059),
        listen_ip="0.0.0.0",
        listen_port=3030,
    )
    approach = inputs(
        AgentIsActive=1,
        RadioAltitudeValid=1,
        RadioAltitude=100.0,
        GroundSpeed=140.0,
    )
    bridge.observe(approach, ("127.0.0.1", 54059))

    assert bridge.sim.engaged
    assert bridge.sim.engagement.control_mode is BenchControlMode.Approach

    # The stand may drop AgentIsActive in the final 80 ft.  The existing
    # terminal latch must carry that confirmed session into rollout.
    touchdown = inputs(
        AgentIsActive=0,
        RadioAltitudeValid=1,
        RadioAltitude=1.0,
        GroundSpeed=138.0,
        LeftGearWeightOnWheels=1,
    )
    bridge.observe(touchdown, ("127.0.0.1", 54059))
    bridge.sim.request_rollout()
    packet = bridge.sim._to_outputs(ControlsState())

    assert bridge.sim.engaged
    assert packet.ControlMode is BenchControlMode.Rollout
    assert packet.ControlValidMask == int(ROLLOUT_CONTROL_MASK)
