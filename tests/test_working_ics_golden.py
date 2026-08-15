"""Characterization baseline of the bench-validated ``working_ics`` approach."""

from __future__ import annotations

import csv
import gzip
import hashlib
import io
import math
import struct
from dataclasses import asdict, fields
from pathlib import Path

from ismpu.control.channels import ControlsState
from ismpu.control.approach import ApproachController
from ismpu.envs.ics_sim import ICSSim, Telemetry
from ismpu.io.ics_connector import ICSInputs as ProductionInputs
from tests.fakes import FakeConnector
from ismpu.working_ics.pid_controller import ClearWeatherILSController, ControllerConfig
from ismpu.working_ics.protocol import (
    AIRBORNE_CONTROL_VALID_MASK,
    ControlModeState,
    ICSInputs,
    ICSOutputs,
)
from ismpu.working_ics.rollout_bridge import VlaydRolloutBridge
from ismpu.working_ics.runner import (
    DEFAULT_CONFIG,
    airborne_control_mode,
    airborne_flare_mode,
    main_gear_contact,
    make_airborne_output,
)


FIXTURE = (
    Path(__file__).parent
    / "fixtures"
    / "working_ics"
    / "approach_20260813_135706.csv.gz"
)
SOURCE_SHA256 = "FEC10D6ECBD9A79AA0BD5FD5ACE32DB7CCE13B4E9DFC3277B3B68F93EB7B12FE"
WIRE_SHA256 = "fd3a4a74b73229450bdc10a07d98937ad8affe9ddf3c07dee536414db108333f"
PID_STATE_SHA256 = "9066177e9c80714036d2bf57507ec988490609c8eedd196891ba91e2007b38aa"

INPUT_COLUMNS = {
    "AgentIsActive": "active",
    "FlightPhase": "flight_phase",
    "Latitude": "latitude_deg",
    "Longitude": "longitude_deg",
    "RadioAltitude": "ra_ft",
    "IndicatedAirspeed": "ias_kt",
    "GroundSpeed": "ground_speed_kt",
    "VerticalSpeed": "vs_fpm",
    "PitchAngle": "pitch_deg",
    "RollAngle": "roll_deg",
    "MagneticHeading": "heading_deg",
    "TrkAngleMagnetic": "track_magnetic_deg",
    "BodyPitchRate": "body_pitch_rate_deg_s",
    "BodyNormAccel": "body_norm_accel_g",
    "RunwayHeading": "runway_heading_deg",
    "LateralDeviation": "lateral_deviation",
    "LocDeviation": "loc_ddm",
    "GSDeviation": "gs_ddm",
    "NoseGearWeightOnWheels": "nose_gear_wow",
    "LeftGearWeightOnWheels": "left_gear_wow",
    "RightGearWeightOnWheels": "right_gear_wow",
    "SlatsAngle": "slats_angle_deg",
    "FlapsAngle": "flaps_angle_deg",
    "StabilizerAngle": "stabilizer_angle_deg",
    "ElevatorLeftAngle": "elevator_left_angle_deg",
    "ElevatorRightAngle": "elevator_right_angle_deg",
    "AileronLeftAngle": "aileron_left_angle_deg",
    "AileronRightAngle": "aileron_right_angle_deg",
    "RudderAngle": "rudder_angle_deg",
    "EngLeftThrust": "eng_left_thrust",
    "EngRigntThrust": "eng_right_thrust",
    "LeftThrottleAngle": "left_throttle_angle_deg",
    "RightThrottleAngle": "right_throttle_angle_deg",
    "WindDirectionTrue": "wind_direction_true_deg",
    "WindSpeed": "wind_speed_kt",
}

RESULT_COLUMNS = {
    "aileron": "aileron_cmd_deg",
    "elevator": "elevator_cmd",
    "rudder": "rudder_cmd_deg",
    "throttle_left_rate": "throttle_left_rate_cmd_deg_s",
    "throttle_right_rate": "throttle_right_rate_cmd_deg_s",
    "throttle_norm": "throttle_cmd_norm",
    "throttle_target_angle_deg": "throttle_target_angle_deg",
    "throttle_left_hold_norm": "throttle_left_position_cmd_norm",
    "throttle_right_hold_norm": "throttle_right_position_cmd_norm",
    "loc_dots": "loc_dots",
    "gs_dots": "gs_dots",
    "target_heading_deg": "target_heading_deg",
    "target_roll_deg": "target_roll_deg",
    "target_vs_fpm": "target_vs_fpm",
    "target_flight_path_angle_deg": "target_flight_path_angle_deg",
    "target_pitch_deg": "target_pitch_deg",
    "vertical_correction_deg": "vertical_correction_deg",
    "flight_path_angle_deg": "flight_path_angle_deg",
    "estimated_aoa_deg": "estimated_aoa_deg",
    "reference_aoa_deg": "reference_aoa_deg",
    "mach": "mach",
    "target_ias_kt": "target_ias_kt",
    "vapp_kt": "vapp_kt",
    "vsr1_kt": "vsr1_kt",
    "vfe_kt": "vfe_kt",
    "alpha_prot_deg": "alpha_prot_deg",
    "alpha_sw_deg": "alpha_sw_deg",
    "alpha_margin_deg": "alpha_margin_deg",
    "roll_limit_deg": "roll_limit_deg",
    "flare_progress": "flare_progress",
    "flare_entry_radio_altitude_ft": "flare_entry_ra_ft",
    "flare_entry_vertical_speed_fpm": "flare_entry_vs_fpm",
    "touchdown_vertical_speed_limit_fpm": "touchdown_vs_limit_fpm",
    "touchdown_speed_min_kt": "touchdown_speed_min_kt",
    "touchdown_speed_max_kt": "touchdown_speed_max_kt",
    "touchdown_pitch_limit_deg": "touchdown_pitch_limit_deg",
}

CANONICAL_RESULT_FIELDS = {
    "aileron": "aileron_deg",
    "elevator": "elevator_g",
    "rudder": "rudder_deg",
    "throttle_left_rate": "throttle_left_rate_deg_s",
    "throttle_right_rate": "throttle_right_rate_deg_s",
    "throttle_norm": "throttle_norm",
    "throttle_target_angle_deg": "throttle_target_angle_deg",
    "loc_dots": "loc_dots",
    "gs_dots": "gs_dots",
    "target_heading_deg": "target_heading_deg",
    "heading_error_deg": "heading_error_deg",
    "target_roll_deg": "target_roll_deg",
    "target_vs_fpm": "target_vs_fpm",
    "target_pitch_deg": "target_pitch_deg",
    "vertical_correction_deg": "vertical_correction_deg",
    "flight_path_angle_deg": "flight_path_angle_deg",
    "target_flight_path_angle_deg": "target_flight_path_angle_deg",
    "estimated_aoa_deg": "estimated_aoa_deg",
    "reference_aoa_deg": "reference_aoa_deg",
    "mach": "mach",
    "target_ias_kt": "target_ias_kt",
    "roll_limit_deg": "roll_limit_deg",
    "flare_progress": "flare_progress",
    "flare_entry_radio_altitude_ft": "flare_entry_radio_altitude_ft",
    "flare_entry_vertical_speed_fpm": "flare_entry_vertical_speed_fpm",
}

EXPECTED_HANDSHAKE = (
    b'{"ControlValidMask":31,"ControlMode":0,"ElevatorCmd":0.0,"AileronCmd":0.0,'
    b'"RudderCmd":0.0,"ThrottleLeftRate":0.0,"ThrottleRightRate":0.0,'
    b'"ThrottleLeft":0.0,"ThrottleRight":0.0,"NoseWheelTillerCmd":0.0,'
    b'"RudderPedalCmd":0.0,"BrakeLeftCmd":0.0,"BrakeRightCmd":0.0,'
    b'"AirbrakeCmd":0.0,"ReverseLeftCmd":0,"ReverseRightCmd":0,"ModeAIReady":1,'
    b'"ModeLocCapture":0,"ModeLocTrack":0,"ModeGSCapture":0,"ModeGSTrack":0,'
    b'"ModeFlareArm":0,"ModeFlare":0,"ModeAlignArm":0,"ModeAlign":0,'
    b'"ModeRolloutArm":0,"ModeRollout":0,"ModeTaxiArm":0,"ModeTaxi":0,'
    b'"ModeSpeed":0,"ModeThrust":0,"WarningFlags":0,"QualityLateralError":0.0,'
    b'"QualityHeadingError":0.0,"QualitySpeedError":0.0,"reserved":null}'
)

EXPECTED_FIRST_LANDING = (
    b'{"ControlValidMask":31,"ControlMode":2,"ElevatorCmd":0.02446685925183906,'
    b'"AileronCmd":0.9335430187675585,"RudderCmd":0.0,'
    b'"ThrottleLeftRate":0.47166733282071643,'
    b'"ThrottleRightRate":0.47166733282071643,'
    b'"ThrottleLeft":0.37582647094320915,"ThrottleRight":0.37582647094320915,'
    b'"NoseWheelTillerCmd":0.0,"RudderPedalCmd":0.0,"BrakeLeftCmd":0.0,'
    b'"BrakeRightCmd":0.0,"AirbrakeCmd":0.0,"ReverseLeftCmd":0,'
    b'"ReverseRightCmd":0,"ModeAIReady":1,"ModeLocCapture":0,"ModeLocTrack":0,'
    b'"ModeGSCapture":0,"ModeGSTrack":0,"ModeFlareArm":0,"ModeFlare":1,'
    b'"ModeAlignArm":0,"ModeAlign":0,"ModeRolloutArm":0,"ModeRollout":0,'
    b'"ModeTaxiArm":0,"ModeTaxi":0,"ModeSpeed":1,"ModeThrust":1,'
    b'"WarningFlags":0,"QualityLateralError":0.003260614193548387,'
    b'"QualityHeadingError":0.03320124193547258,'
    b'"QualitySpeedError":1.5110170000000096,"reserved":null}'
)

EXPECTED_LAST_AIRBORNE = (
    b'{"ControlValidMask":31,"ControlMode":2,"ElevatorCmd":0.05846693815109519,'
    b'"AileronCmd":0.8244786965791737,"RudderCmd":0.0,'
    b'"ThrottleLeftRate":0.31066367029429726,'
    b'"ThrottleRightRate":0.31132679029429877,'
    b'"ThrottleLeft":0.3936462271943206,"ThrottleRight":0.3936462271943206,'
    b'"NoseWheelTillerCmd":0.0,"RudderPedalCmd":0.0,"BrakeLeftCmd":0.0,'
    b'"BrakeRightCmd":0.0,"AirbrakeCmd":0.0,"ReverseLeftCmd":0,'
    b'"ReverseRightCmd":0,"ModeAIReady":1,"ModeLocCapture":0,"ModeLocTrack":0,'
    b'"ModeGSCapture":0,"ModeGSTrack":0,"ModeFlareArm":0,"ModeFlare":0,'
    b'"ModeAlignArm":0,"ModeAlign":0,"ModeRolloutArm":0,"ModeRollout":0,'
    b'"ModeTaxiArm":0,"ModeTaxi":0,"ModeSpeed":1,"ModeThrust":1,'
    b'"WarningFlags":0,"QualityLateralError":0.0024454606451612903,'
    b'"QualityHeadingError":0.004529999999988377,'
    b'"QualitySpeedError":1.1637000000000057,"reserved":null}'
)

EXPECTED_FIRST_ROLLOUT = (
    b'{"ControlValidMask": 14108, "ControlMode": 3, "ElevatorCmd": 0.0, '
    b'"AileronCmd": 0.0, "RudderCmd": 0.0, "ThrottleLeftRate": -8.0, '
    b'"ThrottleRightRate": -8.0, "ThrottleLeft": 0.0, "ThrottleRight": 0.0, '
    b'"NoseWheelTillerCmd": 0.0, "RudderPedalCmd": 0.0, "BrakeLeftCmd": 0.0, '
    b'"BrakeRightCmd": 0.0, "AirbrakeCmd": 0.0, "ReverseLeftCmd": 0, '
    b'"ReverseRightCmd": 0, "ModeAIReady": 1, "ModeLocCapture": 0, '
    b'"ModeLocTrack": 0, "ModeGSCapture": 0, "ModeGSTrack": 0, '
    b'"ModeFlareArm": 0, "ModeFlare": 0, "ModeAlignArm": 0, "ModeAlign": 0, '
    b'"ModeRolloutArm": 0, "ModeRollout": 1, "ModeTaxiArm": 0, "ModeTaxi": 0, '
    b'"ModeSpeed": 0, "ModeThrust": 0, "WarningFlags": 0, '
    b'"QualityLateralError": 0.0, "QualityHeadingError": 0.0, '
    b'"QualitySpeedError": 0.0, "reserved": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}'
)


def _rows() -> list[dict[str, str]]:
    raw = gzip.decompress(FIXTURE.read_bytes())
    assert hashlib.sha256(raw).hexdigest().upper() == SOURCE_SHA256
    rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8"))))
    assert len(rows) == 1482
    return rows


def _state(row: dict[str, str]) -> ICSInputs:
    values = {field.name: 0 for field in fields(ICSInputs)}
    values.update({name: float(row[column]) for name, column in INPUT_COLUMNS.items()})

    # These source fields were not logged. The chosen values reproduce the recorded Mach
    # exactly and are explicit provenance, not invented measurements.
    values["RadioAltitudeValid"] = 1
    values["TrueAirspeedValid"] = 1
    values["AirfieldTemp"] = 0.0
    values["TrueAirspeed"] = (
        float(row["mach"]) * 38.967854 * math.sqrt(273.15)
    )
    return ICSInputs(**values)


def _assert_numeric_result(index: int, row: dict[str, str], result) -> None:
    for attribute, column in RESULT_COLUMNS.items():
        actual = float(getattr(result, attribute))
        expected = float(row[column])
        assert abs(actual - expected) <= 1e-12, (index, attribute, actual, expected)

    assert int(result.flare_armed) == int(row["flare_armed"])
    assert int(result.flare_active) == int(row["flare_active"])
    assert int(result.terminal_hold_active) == int(row["terminal_hold_active"])
    assert result.flap_configuration == row["flap_configuration"]
    assert ";".join(result.envelope_warnings) == row["envelope_warnings"]


def _replay() -> dict[str, object]:
    controller = ClearWeatherILSController(ControllerConfig.from_json(DEFAULT_CONFIG))
    wire_hash = hashlib.sha256()
    pid_state_hash = hashlib.sha256()
    previous_time = 0.0
    next_send = 0.0
    packet_count = 0
    first_landing = None
    last_airborne = None
    flare_start = None
    mode_flare_start = None
    touchdown_index = None
    first_state = None
    touchdown_state = None

    for index, row in enumerate(_rows()):
        state = _state(row)
        first_state = first_state or state
        time_s = float(row["time_s"])
        result = controller.update(state, time_s - previous_time)
        previous_time = time_s
        _assert_numeric_result(index, row, result)

        for name, pid in (
            ("roll", controller.roll_pid),
            ("pitch", controller.pitch_pid),
            ("speed", controller.speed_pid),
        ):
            for gain in ("kp", "ki", "kd"):
                assert getattr(pid.config, gain) == float(row[f"{name}_{gain}"])
            assert abs(pid.config.ki * pid.integral - float(row[f"{name}_i_term"])) <= 1e-12

        pid_state_hash.update(struct.pack(
            ">9d",
            *(
                value
                for pid in (controller.roll_pid, controller.pitch_pid, controller.speed_pid)
                for value in (pid.integral, pid.derivative, pid._previous_measurement)
            ),
        ))

        mode = airborne_control_mode(state)
        flare_mode = airborne_flare_mode(state)
        assert mode.name == row["control_mode"]
        assert int(flare_mode) == int(row["mode_flare"])
        if flare_start is None and result.flare_active:
            flare_start = index
        if mode_flare_start is None and flare_mode:
            mode_flare_start = index
        if main_gear_contact(state):
            touchdown_index = index
            touchdown_state = state

        if not main_gear_contact(state) and time_s >= next_send:
            packet = make_airborne_output(state, result, mode, flare_mode).to_json_bytes()
            wire_hash.update(len(packet).to_bytes(4, "big"))
            wire_hash.update(packet)
            packet_count += 1
            if first_landing is None and mode is ControlModeState.Landing:
                first_landing = (index, packet)
            last_airborne = (index, packet)
            next_send = time_s + 0.05

    return {
        "wire_sha256": wire_hash.hexdigest(),
        "pid_state_sha256": pid_state_hash.hexdigest(),
        "packet_count": packet_count,
        "first_landing": first_landing,
        "last_airborne": last_airborne,
        "flare_start": flare_start,
        "mode_flare_start": mode_flare_start,
        "touchdown_index": touchdown_index,
        "first_state": first_state,
        "touchdown_state": touchdown_state,
        "final_pid_states": tuple(
            (pid.integral, pid.derivative, pid._previous_measurement)
            for pid in (controller.roll_pid, controller.pitch_pid, controller.speed_pid)
        ),
    }


def test_real_approach_replays_deterministically_to_touchdown():
    first = _replay()
    assert _replay() == first

    assert first["wire_sha256"] == WIRE_SHA256
    assert first["pid_state_sha256"] == PID_STATE_SHA256
    assert first["packet_count"] == 728
    assert first["flare_start"] == 930
    assert first["mode_flare_start"] == 1177
    assert first["first_landing"] == (1394, EXPECTED_FIRST_LANDING)
    assert first["last_airborne"] == (1480, EXPECTED_LAST_AIRBORNE)
    assert first["touchdown_index"] == 1481
    assert first["final_pid_states"] == (
        (-2.176706301999266, -0.013366216031188375, 0.008682251),
        (3.6777079645398203, -0.8576434383494449, 5.876602),
        (-8.81658270328894, -0.14433552706004185, 138.820892),
    )


def test_production_approach_matches_working_ics_on_every_golden_frame():
    """Канонический контур и формирователь пакета совпадают с эталоном до 1e-12."""
    rows = _rows()
    reference = ClearWeatherILSController(ControllerConfig.from_json(DEFAULT_CONFIG))
    production = ApproachController()
    command = ControlsState()

    first_input = ProductionInputs.from_dict(asdict(_state(rows[0])))
    sim = ICSSim(
        connector=FakeConnector(first_input),
        aircraft_profile="mc21",
        validate_conditions=False,
    )
    sim.engagement.request_approach()
    sim.read_telemetry()
    assert sim.engaged

    previous_time = 0.0
    next_send = 0.0
    packet_count = 0
    for index, row in enumerate(rows):
        source = _state(row)
        production_input = ProductionInputs.from_dict(asdict(source))
        telemetry = Telemetry.from_ics(production_input)
        sim._last_telemetry = telemetry
        sim.engagement.step(sim._engagement_inputs(telemetry))

        time_s = float(row["time_s"])
        dt = time_s - previous_time
        previous_time = time_s
        expected = reference.update(source, dt)
        actual = production.calc_commands(dt, command, telemetry)

        for expected_name, actual_name in CANONICAL_RESULT_FIELDS.items():
            assert abs(float(getattr(actual, actual_name))
                       - float(getattr(expected, expected_name))) <= 1e-12, (
                index, expected_name)
        assert actual.flare_armed is expected.flare_armed
        assert actual.flare_active is expected.flare_active
        assert actual.terminal_hold_active is expected.terminal_hold_active
        assert actual.envelope_warnings == expected.envelope_warnings
        assert actual.limits is not None
        for name in (
            "table_weight_kg", "vapp_kt", "vsr1_kt", "vfe_kt", "alpha_prot_deg",
            "alpha_sw_deg", "touchdown_vertical_speed_limit_fpm",
            "touchdown_speed_min_kt", "touchdown_speed_max_kt",
            "touchdown_pitch_limit_deg",
        ):
            assert abs(float(getattr(actual.limits, name))
                       - float(getattr(expected, name))) <= 1e-12, (index, name)
        assert actual.limits.flap_configuration.value == expected.flap_configuration
        assert abs(
            actual.limits.alpha_prot_deg - actual.estimated_aoa_deg
            - expected.alpha_margin_deg
        ) <= 1e-12

        for actual_pid, expected_pid in zip(
            (production.roll_pid, production.pitch_pid, production.speed_pid),
            (reference.roll_pid, reference.pitch_pid, reference.speed_pid),
        ):
            assert abs(actual_pid.integral - expected_pid.integral) <= 1e-12
            assert abs(actual_pid.filtered_derivative - expected_pid.derivative) <= 1e-12
            assert abs(-actual_pid._prev_deriv_input
                       - expected_pid._previous_measurement) <= 1e-12

        mode = airborne_control_mode(source)
        if mode is ControlModeState.Landing:
            assert sim.request_landing()
        if not main_gear_contact(source) and time_s >= next_send:
            expected_output = make_airborne_output(source, expected)
            actual_output = sim._to_outputs(command)
            for field in fields(ICSOutputs):
                if field.name == "reserved":
                    continue
                left = getattr(actual_output, field.name)
                right = getattr(expected_output, field.name)
                if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                    assert abs(float(left) - float(right)) <= 1e-12, (index, field.name)
                else:
                    assert left == right, (index, field.name)
            packet_count += 1
            next_send = time_s + 0.05

    assert packet_count == 728


def test_handshake_and_first_rollout_wire_are_frozen_at_the_seam():
    handshake = ICSOutputs(
        ControlValidMask=AIRBORNE_CONTROL_VALID_MASK,
        ControlMode=ControlModeState.Off,
        ModeAIReady=1,
    )
    assert handshake.to_json_bytes() == EXPECTED_HANDSHAKE

    replay = _replay()
    bridge = VlaydRolloutBridge(
        object(),
        ("127.0.0.1", 54059),
        listen_ip="0.0.0.0",
        listen_port=3030,
    )
    sender = ("127.0.0.1", 54059)
    bridge.observe(replay["first_state"], sender)
    bridge.observe(replay["touchdown_state"], sender)
    bridge.sim.request_rollout()

    assert bridge.sim._to_outputs(ControlsState()).to_json_bytes() == EXPECTED_FIRST_ROLLOUT
