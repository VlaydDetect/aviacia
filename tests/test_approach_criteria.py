import math

import pytest

from ismpu.control.approach_criteria import ApproachCriteriaMonitor
from ismpu.control.system import ControllingSystem
from ismpu.envs.ics_sim import Telemetry
from ismpu.envs.scenario import Scenario

from tests.fakes import airborne_inputs


def frame(ra_ft=500.0, **overrides):
    return Telemetry.from_ics(airborne_inputs(ra_ft, **overrides))


def test_a11_uses_magnetic_track_and_actual_flight_path_angle():
    monitor = ApproachCriteriaMonitor()
    sample = monitor.observe(
        frame(
            RunwayHeading=75.0,
            MagneticHeading=70.0,
            TrkAngleMagnetic=75.4,
        ),
        flight_path_angle_deg=-3.2,
    )

    assert sample.status == "OK"
    assert sample.course_error_deg == pytest.approx(0.4)
    assert sample.glideslope_error_deg == pytest.approx(0.2)

    assert monitor.observe(frame(300.0), -3.0).status == "COMPLETE"
    verdict = monitor.verdict()
    assert verdict.passed
    assert verdict.sample_count == 1


def test_a11_waits_for_capture_then_records_later_limit_excursion():
    monitor = ApproachCriteriaMonitor()
    assert monitor.observe(
        frame(600.0, RunwayHeading=75.0, TrkAngleMagnetic=77.0), -4.0
    ).status == "WAITING_CAPTURE"
    assert monitor.observe(
        frame(550.0, RunwayHeading=75.0, TrkAngleMagnetic=75.1), -3.1
    ).status == "OK"
    assert monitor.observe(
        frame(400.0, RunwayHeading=75.0, TrkAngleMagnetic=76.0), -3.1
    ).status == "LIMIT"
    monitor.observe(frame(299.0), -3.0)

    verdict = monitor.verdict()
    assert verdict.status == "FAIL"
    assert "course limit exceeded" in verdict.reasons


def test_a11_rejects_non_finite_values():
    monitor = ApproachCriteriaMonitor()
    sample = monitor.observe(
        frame(500.0, TrkAngleMagnetic=math.nan), -3.0
    )
    assert sample.status == "INVALID"
    monitor.observe(frame(300.0), -3.0)
    assert monitor.verdict().status == "FAIL"


def test_a11_monitor_is_wired_to_approach_without_driving_go_around():
    controller = ControllingSystem()
    Scenario.from_preset("default").apply_control(controller)
    first = frame(
        500.0,
        RunwayHeading=75.0,
        TrkAngleMagnetic=75.1,
        VerticalSpeed=-730.0,
        GroundSpeed=140.0,
    )
    controller.begin_flight(first)
    assert not controller.control_step(0.05, first, send=False)
    assert controller.approach_criteria.sample_count == 1

    cutoff = frame(299.0)
    assert not controller.control_step(0.05, cutoff, send=False)
    assert controller.approach_criteria.cutoff_reached
    assert controller.go_around is None
