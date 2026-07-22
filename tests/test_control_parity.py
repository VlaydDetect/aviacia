"""Тесты паритета после выноса контура из main.ipynb в пакет ismpu.

Полный паритет траектории требует работающего стенда (проверяется вручную). Здесь
проверяются детерминированные компоненты и сквозная связность контура на фейковом
стенде: численные значения PID, геодезия трекера, эталонная скорость и один такт
`control_step`.
"""

import math

import numpy as np
import pytest

from ismpu.control.pid import PIDController
from ismpu.control.runway_tracker import RunwayTracker
from ismpu.control.trajectory import ReferenceTrajectory, VelocityLaw
from ismpu.control.system import ControllingSystem
from ismpu.config.scenarios import DEFAULT
from ismpu.config.runway import RWY_START_LAT, RWY_START_LON, RWY_HEADING_TRUE

from fakes import static_sim, telemetry, decode_outputs


# --------------------------------------------------------------------------- #
# PIDController — известные значения (защита от изменения численного поведения)
# --------------------------------------------------------------------------- #

def test_pid_proportional_and_integral_accumulation():
    pid = PIDController(kp=1.0, ki=0.0, kd=0.0, min_out=-10.0, max_out=10.0)
    # Первый такт: prev_error is None -> derivative=0, output = kp*error
    assert pid.compute(2.0, 0.05) == pytest.approx(2.0)
    assert pid.integral == pytest.approx(0.1)
    # Второй такт: integral += 1*0.05 -> 0.15, kp*error = 1.0
    assert pid.compute(1.0, 0.05) == pytest.approx(1.0)
    assert pid.integral == pytest.approx(0.15)


def test_pid_filtered_derivative():
    pid = PIDController(kp=0.0, ki=0.0, kd=1.0, min_out=-100.0, max_out=100.0, der_filter_tf=0.1)
    assert pid.compute(2.0, 0.05) == pytest.approx(0.0)  # первый такт: D=0
    # alpha = 0.05/(0.05+0.1) = 1/3; raw = (1-2)/0.05 = -20; filtered = -20/3
    assert pid.compute(1.0, 0.05) == pytest.approx(-20.0 / 3.0)


def test_pid_anti_windup_clamp():
    pid = PIDController(kp=0.0, ki=1.0, kd=0.0, min_out=-100.0, max_out=100.0, anti_windup=0.05)
    # integral += 2*0.05 = 0.1, но зажимается anti_windup до 0.05
    assert pid.compute(2.0, 0.05) == pytest.approx(0.05)
    assert pid.integral == pytest.approx(0.05)


def test_pid_output_clamped_to_bounds():
    pid = PIDController(kp=100.0, ki=0.0, kd=0.0, min_out=-1.0, max_out=1.0)
    assert pid.compute(5.0, 0.05) == pytest.approx(1.0)   # насыщение сверху
    assert pid.compute(-5.0, 0.05) == pytest.approx(-1.0)  # насыщение снизу


def test_pid_zero_dt_returns_zero():
    pid = PIDController(kp=1.0, ki=1.0, kd=1.0)
    assert pid.compute(3.0, 0.0) == 0.0


# --------------------------------------------------------------------------- #
# RunwayTracker — геодезия и знак cross-track error
# --------------------------------------------------------------------------- #

def test_xte_zero_at_runway_start():
    tracker = RunwayTracker()
    assert tracker.get_cross_track_error(RWY_START_LAT, RWY_START_LON) == pytest.approx(0.0, abs=1e-6)


def test_xte_sign_right_is_positive():
    tracker = RunwayTracker()
    # Точка в 10 м справа от порога (курс ВПП + 90°)
    lat, lon = tracker.destination(RWY_START_LAT, RWY_START_LON, tracker.theta_rwy + np.pi / 2, 10.0)
    assert tracker.get_cross_track_error(lat, lon) == pytest.approx(10.0, abs=0.1)


def test_xte_sign_left_is_negative():
    tracker = RunwayTracker()
    lat, lon = tracker.destination(RWY_START_LAT, RWY_START_LON, tracker.theta_rwy - np.pi / 2, 10.0)
    assert tracker.get_cross_track_error(lat, lon) == pytest.approx(-10.0, abs=0.1)


def test_guidance_on_centerline_small_heading_error():
    tracker = RunwayTracker(lookahead_min=10.0, lookahead_gain=1.8, xte_gain=2.0)
    g = tracker.guidance(RWY_START_LAT, RWY_START_LON, RWY_HEADING_TRUE, ground_speed=50.0)
    assert set(g) == {"xte", "along", "lookahead", "heading_error_deg", "desired_heading_deg"}
    assert g["xte"] == pytest.approx(0.0, abs=1e-6)
    assert abs(g["heading_error_deg"]) < 15.0
    assert g["lookahead"] == pytest.approx(10.0 + 1.8 * 50.0)


# --------------------------------------------------------------------------- #
# ReferenceTrajectory — эталонная кривая скорости
# --------------------------------------------------------------------------- #

def test_gauss_bell_endpoints_and_monotonicity():
    traj = ReferenceTrajectory(v_start_kts=200.0, v_target_kts=10.0, braking_distance_m=3000.0)
    assert traj.get_reference_speed(0.0) == pytest.approx(traj.v_start_ms)
    assert traj.get_reference_speed(3000.0) == pytest.approx(traj.v_target_ms)
    assert traj.get_reference_speed(5000.0) == pytest.approx(traj.v_target_ms)  # за пределами
    # Монотонно убывает
    assert traj.get_reference_speed(0.0) > traj.get_reference_speed(500.0) > traj.get_reference_speed(1500.0)


def test_equally_slow_law_endpoints():
    traj = ReferenceTrajectory(200.0, 10.0, 3000.0, law=VelocityLaw.EQUALLY_SLOW)
    assert traj.get_reference_speed(0.0) == pytest.approx(traj.v_start_ms)
    assert traj.get_reference_speed(3000.0) == pytest.approx(traj.v_target_ms)


# --------------------------------------------------------------------------- #
# Сквозная связность контура на фейковом стенде
# --------------------------------------------------------------------------- #

def test_control_step_emits_five_bounded_commands():
    sim, conn = static_sim(groundspeed_ms=50.0)
    controller = ControllingSystem(sim)
    DEFAULT.apply(controller)

    stop = controller.control_step(0.05, telemetry(50.0))

    assert stop is False
    assert len(conn.sent_outputs) == 1
    brake_l, brake_r, rev_l, rev_r, rudder = decode_outputs(conn.sent_outputs[-1])
    for value in (brake_l, brake_r, rev_l, rev_r, rudder):
        assert math.isfinite(value)
    assert 0.0 <= brake_l <= 1.0
    assert 0.0 <= brake_r <= 1.0
    assert -1.0 <= rev_l <= 0.0
    assert -1.0 <= rev_r <= 0.0
    assert -1.0 <= rudder <= 1.0


def test_nws_fail_preset_injects_failure():
    """NWS_FAIL активирует отказ руления: steering_eff→0, руль обнуляется на выходе."""
    from ismpu.config.scenarios import NWS_FAIL

    sim, conn = static_sim(groundspeed_ms=50.0)
    controller = ControllingSystem(sim)
    NWS_FAIL.apply(controller)

    assert controller.failures.state.steering_eff == 0.0  # отказ активирован
    controller.control_step(0.05, telemetry(50.0))
    # apply_failures обнулил руль перед отправкой (удержание — дифф. торможением/тягой)
    assert decode_outputs(conn.sent_outputs[-1])[4] == pytest.approx(0.0)


def test_default_preset_leaves_all_actuators_healthy():
    from ismpu.config.scenarios import DEFAULT

    controller = ControllingSystem(static_sim()[0])
    DEFAULT.apply(controller)

    assert controller.failures.state.steering_eff == 1.0  # отказ не активирован


def test_control_step_stops_and_sends_nothing_on_missing_telemetry():
    from ismpu.envs.ics_sim import Telemetry

    sim, conn = static_sim()
    controller = ControllingSystem(sim)
    DEFAULT.apply(controller)

    dropped = Telemetry(lat=RWY_START_LAT, lon=RWY_START_LON, groundspeed_ms=None,
                        heading_true_deg=float(RWY_HEADING_TRUE))
    stop = controller.control_step(0.05, dropped)

    assert stop is True
    assert conn.sent_outputs == []


def test_control_step_stops_on_invalid_frame_even_with_numeric_fields():
    """Стенд при обрыве связи отдаёт НУЛИ с valid=False, а не None.

    Проверка «поле is None» пропустила бы groundspeed = 0.0 дальше, где он тут же выглядел бы
    как «достигнута скорость руления», и эпизод молча засчитался бы пройденным.
    """
    from ismpu.envs.ics_sim import Telemetry

    controller = ControllingSystem(static_sim()[0])
    DEFAULT.apply(controller)

    assert controller.control_step(0.05, Telemetry.invalid()) is True
