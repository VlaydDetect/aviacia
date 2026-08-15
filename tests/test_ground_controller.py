"""Контракты наземного контура этапа 2."""

from dataclasses import is_dataclass
from unittest.mock import MagicMock

import pytest

from ismpu.config.constants import DT
from ismpu.config.ics import FlightPhase
from ismpu.config.scenarios import SCENARIOS
from ismpu.config.segments import FlightSegment
from ismpu.control.channels import LateralDiagnostics, LongitudinalDiagnostics
from ismpu.control.failures import FailureMode
from ismpu.control.flight import initial_segment
from ismpu.control.ground_allocator import AllocationDiagnostics
from ismpu.control.pid import PIDController
from ismpu.control.system import ControllingSystem
from ismpu.control.trajectory import CompletionRule
from ismpu.envs.ics_sim import Telemetry
from ismpu.envs.sim_interface import RunStopReason
from ismpu.runtime.loop import run
from ismpu.working_ics.pid_controller import PID, PIDConfig
from ismpu.utils.converts import Converts

from tests.fakes import airborne_inputs, engaged_inputs, telemetry


def _direct_ground_frame(
    *, speed_kts: float, xte_m: float = 0.0, fault_nws: bool = False,
) -> Telemetry:
    return Telemetry.from_ics(engaged_inputs(
        GroundSpeed=speed_kts,
        MagneticHeadingValid=1,
        MagneticHeading=64.0,
        TrkAngleMagneticValid=1,
        TrkAngleMagnetic=64.0,
        RunwayHeadingValid=1,
        RunwayHeading=64.0,
        LateralDeviation=xte_m,
        FaultNWS=int(fault_nws),
    ))


def test_ground_pids_use_working_ics_numerics_and_explicit_integrator_limits():
    pids = SCENARIOS["default"].control_for(
        "mc21", FlightSegment.ROLLOUT).build_pids()
    for pid in pids.values():
        assert pid.derivative_on_measurement
        assert pid.conditional_anti_windup
        assert pid.exact_discretization
        assert pid.clamp_dt
        assert pid.dt_min_s == pytest.approx(0.001)
        assert pid.dt_max_s == pytest.approx(0.25)
        assert pid.der_filter_tf == pytest.approx(0.25)
        assert pid.integral_decay == 0.0
        assert pid.integral_min == pytest.approx(-pid.anti_windup)
        assert pid.integral_max == pytest.approx(pid.anti_windup)

    pid = PIDController(
        kp=0.0, ki=1.0, kd=0.0, min_out=-10.0, max_out=10.0,
        integral_min=-0.1, integral_max=0.2,
        derivative_on_measurement=True, conditional_anti_windup=True,
        exact_discretization=True, clamp_dt=True,
    )
    pid.compute(1.0, 10.0, measurement=0.0)
    assert pid.integral == pytest.approx(0.2)


def test_ground_pid_matches_working_ics_for_outputs_and_states():
    config = PIDConfig(
        kp=0.8, ki=0.2, kd=0.1,
        output_min=-1.0, output_max=1.0,
        integrator_min=-0.4, integrator_max=0.7,
        derivative_tau_s=0.25,
    )
    reference = PID(config)
    actual = PIDController(
        kp=config.kp, ki=config.ki, kd=config.kd,
        min_out=config.output_min, max_out=config.output_max,
        integral_min=config.integrator_min, integral_max=config.integrator_max,
        der_filter_tf=config.derivative_tau_s,
        derivative_on_measurement=True,
        conditional_anti_windup=True,
        exact_discretization=True,
        clamp_dt=True,
    )

    for error, measurement, dt in (
        (0.2, 10.0, 0.0),
        (0.8, 10.2, 0.05),
        (3.0, 10.7, 0.5),
        (-2.0, 10.1, 0.02),
        (-0.3, 9.8, -1.0),
    ):
        assert actual.compute(error, dt, measurement) == reference.update(
            error, measurement, dt)
        assert actual.integral == reference.integral
        assert actual.filtered_derivative == reference.derivative


def test_touchdown_initializes_profile_from_measured_speed_and_resets_ground_pids():
    controller = ControllingSystem()
    controller.bind_scenario(SCENARIOS["default"], "mc21")
    controller.begin_flight(Telemetry.from_ics(airborne_inputs(radio_altitude_ft=900.0)))
    controller.pids.clear()

    touchdown_speed_kts = 123.4
    frame = _direct_ground_frame(speed_kts=touchdown_speed_kts)
    controller.control_step(DT, frame, send=False)

    diagnostics = controller.longitudinal_channel.last_diagnostics
    assert controller.segment is FlightSegment.ROLLOUT
    assert controller.longitudinal_channel.trajectory.v_start_ms == pytest.approx(
        touchdown_speed_kts * Converts.KTS_TO_MS)
    assert diagnostics.setpoint == pytest.approx(frame.groundspeed_ms)
    assert diagnostics.error == pytest.approx(0.0)
    assert all(pid.integral == pytest.approx(0.0) for pid in controller.pids.values())


def test_reverse_pid_has_the_correct_sign_above_sixty_knots():
    controller = ControllingSystem()
    SCENARIOS["default"].apply_control(controller, "mc21")
    frame = _direct_ground_frame(speed_kts=120.0)
    controller.longitudinal_channel.begin(frame.groundspeed_ms)
    controller.longitudinal_channel.traveled_distance_m = 2500.0

    diagnostics = controller.longitudinal_channel.compute(DT, frame)

    assert diagnostics.error > 0.0
    assert diagnostics.reverse_allowed
    assert diagnostics.base_reverse_left < 0.0
    assert diagnostics.base_reverse_right < 0.0


def test_ground_step_returns_three_typed_diagnostics_and_rate_limits_handover():
    controller = ControllingSystem()
    SCENARIOS["default"].apply_control(controller, "mc21")
    frame = _direct_ground_frame(speed_kts=100.0, xte_m=8.0)
    controller.longitudinal_channel.begin(frame.groundspeed_ms)
    controller.longitudinal_channel.traveled_distance_m = 2500.0

    assert controller.control_step(DT, frame, send=False) is False

    longitudinal = controller.longitudinal_channel.last_diagnostics
    lateral = controller.lateral_channel.last_diagnostics
    allocation = controller.ground_allocator.last_diagnostics
    assert isinstance(longitudinal, LongitudinalDiagnostics) and is_dataclass(longitudinal)
    assert isinstance(lateral, LateralDiagnostics) and is_dataclass(lateral)
    assert isinstance(allocation, AllocationDiagnostics) and is_dataclass(allocation)
    assert abs(controller.state.cmd_rudder) <= DT * controller.ground_allocator.steering_rate_per_s
    assert controller.state.cmd_brake_l <= DT * controller.ground_allocator.brake_rate_per_s
    assert controller.state.cmd_brake_r <= DT * controller.ground_allocator.brake_rate_per_s
    assert allocation.saturated


def test_tracking_uses_pid_space_when_channel_weight_is_not_one():
    controller = ControllingSystem()
    SCENARIOS["default"].apply_control(controller, "mc21")
    frame = _direct_ground_frame(speed_kts=100.0)
    controller.longitudinal_channel.begin(frame.groundspeed_ms)
    controller.longitudinal_channel.traveled_distance_m = 2500.0
    controller.set_channel_weights(0.5, 1.0)
    tracked = {}
    pid = controller.pids["pid_brake_l"]
    pid.track = lambda applied, dt, commanded_output=None: tracked.update(
        applied=applied, requested=commanded_output)

    controller.control_step(DT, frame, send=False)
    allocation = controller.ground_allocator.last_diagnostics

    assert tracked["requested"] == pytest.approx(
        allocation.base.brake_left / controller.longitudinal_channel.w_lon)
    assert tracked["requested"] == pytest.approx(pid.last_output)


def test_nws_failure_keeps_rudder_and_redistributes_to_differential_brakes():
    controller = ControllingSystem()
    SCENARIOS["nws_fail"].apply_control(controller, "mc21")
    frame = _direct_ground_frame(speed_kts=100.0, xte_m=6.0, fault_nws=True)

    controller.control_step(DT, frame, send=False)

    assert controller.state.cmd_pedal == 0.0
    assert controller.state.cmd_tiller == 0.0
    assert controller.state.cmd_rudder != 0.0
    assert controller.state.cmd_brake_l != controller.state.cmd_brake_r


def test_guidance_dropout_removes_the_previous_turn_immediately():
    controller = ControllingSystem()
    SCENARIOS["default"].apply_control(controller, "mc21")
    controller.control_step(
        DT, _direct_ground_frame(speed_kts=100.0, xte_m=6.0), send=False)
    assert controller.state.cmd_rudder != 0.0

    controller.control_step(
        DT, telemetry(100.0 * Converts.KTS_TO_MS, runway_profile=None), send=False)

    assert controller.lateral_channel.last_diagnostics.event == "guidance_unavailable"
    assert controller.state.cmd_rudder == 0.0
    assert controller.state.cmd_pedal == 0.0
    assert controller.state.cmd_tiller == 0.0
    assert controller.state.cmd_brake_l == pytest.approx(controller.state.cmd_brake_r)
    assert controller.state.cmd_rev_l == pytest.approx(controller.state.cmd_rev_r)


def test_failed_reverse_is_excluded_and_yaw_compensation_uses_remaining_organs():
    controller = ControllingSystem()
    SCENARIOS["left_reverse_fail"].apply_control(controller, "mc21")
    frame = telemetry(120.0 * Converts.KTS_TO_MS)
    controller.longitudinal_channel.begin(frame.groundspeed_ms)
    controller.longitudinal_channel.traveled_distance_m = 2500.0

    controller.control_step(DT, frame, send=False)
    allocation = controller.ground_allocator.last_diagnostics

    assert controller.failures.state.reverse_left_eff == 0.0
    assert allocation.requested.reverse_left == 0.0
    assert allocation.requested.reverse_right < 0.0
    assert allocation.failure_compensation != 0.0
    assert allocation.lateral.rudder != 0.0


def test_reverse_failure_compensation_survives_guidance_dropout():
    controller = ControllingSystem()
    SCENARIOS["left_reverse_fail"].apply_control(controller, "mc21")
    frame = telemetry(120.0 * Converts.KTS_TO_MS, runway_profile=None)
    controller.longitudinal_channel.begin(frame.groundspeed_ms)
    controller.longitudinal_channel.traveled_distance_m = 2500.0

    controller.control_step(DT, frame, send=False)
    allocation = controller.ground_allocator.last_diagnostics

    assert not controller.lateral_channel.last_diagnostics.valid
    assert allocation.failure_compensation != 0.0
    assert controller.state.cmd_rudder == 0.0
    assert controller.state.cmd_brake_l != controller.state.cmd_brake_r


def test_taxi_allocates_to_tiller_and_brakes_only():
    controller = ControllingSystem()
    SCENARIOS["b_1_2_taxi"].apply_control(controller, "mc21", FlightSegment.TAXI)
    controller.segment = FlightSegment.TAXI
    frame = _direct_ground_frame(speed_kts=15.0, xte_m=2.0)

    assert controller.control_step(DT, frame, send=False) is False
    assert controller.state.cmd_rudder == 0.0
    assert controller.state.cmd_pedal == 0.0
    assert controller.state.cmd_tiller != 0.0
    assert controller.state.cmd_rev_l == controller.state.cmd_rev_r == 0.0


def test_bench_taxi_phase_starts_directly_in_taxi():
    frame = Telemetry.from_ics(engaged_inputs(
        FlightPhase=int(FlightPhase.TAXI_IN), GroundSpeed=15.0))

    assert initial_segment(frame) is FlightSegment.TAXI


def test_scenario_completion_rules_match_the_matrix():
    default = SCENARIOS["default"].control_for("mc21", FlightSegment.ROLLOUT)
    full_stop = SCENARIOS["b_1_1_rollout"].control_for(
        "mc21", FlightSegment.ROLLOUT)
    taxi = SCENARIOS["b_1_2_taxi"].control_for("mc21", FlightSegment.TAXI)

    assert (default.target_speed_kts, default.completion_rule) == (
        7.5, CompletionRule.HANDOVER_TAXI)
    assert (full_stop.target_speed_kts, full_stop.completion_rule) == (
        0.0, CompletionRule.FULL_STOP)
    assert (taxi.target_speed_kts, taxi.completion_rule) == (
        15.0, CompletionRule.OPERATOR)

    controller = ControllingSystem()
    full_stop.apply(controller)
    controller.longitudinal_channel.begin(140.0 * Converts.KTS_TO_MS)
    assert controller.control_step(
        DT, telemetry(0.2 * Converts.KTS_TO_MS), send=False) is True

    controller = ControllingSystem()
    taxi.apply(controller)
    controller.segment = FlightSegment.TAXI
    controller.longitudinal_channel.begin(15.0 * Converts.KTS_TO_MS)
    assert controller.control_step(DT, telemetry(0.0), send=False) is False


@pytest.mark.parametrize(
    ("rule", "taxi_requests"),
    ((CompletionRule.FULL_STOP, 0), (CompletionRule.HANDOVER_TAXI, 1)),
)
def test_runtime_requests_taxi_only_for_handover_completion(
    monkeypatch, rule, taxi_requests,
):
    controller = MagicMock()
    controller.segment = FlightSegment.ROLLOUT
    controller.go_around_reason = None
    controller.begin_flight.return_value = FlightSegment.ROLLOUT
    controller.control_step.return_value = True
    controller.longitudinal_channel.trajectory.completion_rule = rule
    sim = MagicMock()
    sim.reset.return_value = _direct_ground_frame(speed_kts=7.5)
    sim.read_telemetry.return_value = sim.reset.return_value
    ticks = iter((0.0, 0.0, 0.0, DT))
    monkeypatch.setattr("ismpu.runtime.loop.time.monotonic", lambda: next(ticks))

    result = run(controller, sim, SCENARIOS["default"])

    assert result.reason is RunStopReason.COMPLETED
    assert controller.hand_over_to_taxi.call_count == taxi_requests


def test_all_old_ground_gains_are_marked_draft_after_allocator_change():
    assert all(
        scenario.is_draft("mc21", segment)
        for scenario in SCENARIOS.values()
        for segment in (FlightSegment.ROLLOUT, FlightSegment.TAXI)
    )
