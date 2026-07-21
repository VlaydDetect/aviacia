"""Тесты паритета после выноса контура из main.ipynb в пакет ismpu.

Полный паритет траектории требует запущенного X-Plane (проверяется вручную).
Здесь проверяются детерминированные компоненты и сквозная связность контура на
мок-коннекторе: численные значения PID, геодезия трекера, эталонная скорость и
один такт `control_step` без симулятора.
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
from ismpu.io.datarefs import LATITUDE, LONGITUDE, GROUNDSPEED, TRUE_PSI


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
# Сквозная связность контура на мок-коннекторе (без X-Plane)
# --------------------------------------------------------------------------- #

class MockXPC:
    """Фейковый коннектор: отдаёт заданную телеметрию, пишет команды в self.sent."""

    def __init__(self, values: dict):
        self.current_dref_values = {k: {"value": v} for k, v in values.items()}
        self.sent = []

    def sendDREF(self, dref, value):
        self.sent.append((dref, value))

    def pauseSIM(self, *a):
        pass

    def sendCMND(self, *a):
        pass


def _nominal_values(groundspeed=50.0):
    return {
        LATITUDE: RWY_START_LAT,
        LONGITUDE: RWY_START_LON,
        GROUNDSPEED: groundspeed,
        TRUE_PSI: RWY_HEADING_TRUE,
    }


def _backend(mock):
    """Бэкенд поверх мок-коннектора: контур зависит только от SimInterface."""
    from ismpu.envs.sim_interface import XPlaneBackend
    return XPlaneBackend(xpc=mock, settle_s=0.0, reload_each_reset=False)


def _telemetry(values: dict):
    """Кадр телеметрии из набора значений DataRef.

    Контур больше не читает коннектор сам — кадр подаётся параметром `control_step`, поэтому
    тесты собирают его так же, как это делает бэкенд.
    """
    from ismpu.envs.sim_interface import Telemetry
    return Telemetry(
        lat=values.get(LATITUDE), lon=values.get(LONGITUDE),
        groundspeed_ms=values.get(GROUNDSPEED), heading_true_deg=values.get(TRUE_PSI),
        valid=None not in (values.get(LATITUDE), values.get(LONGITUDE),
                           values.get(GROUNDSPEED), values.get(TRUE_PSI)),
    )


def test_control_step_emits_five_bounded_commands():
    values = _nominal_values(groundspeed=50.0)
    mock = MockXPC(values)
    controller = ControllingSystem(_backend(mock))
    DEFAULT.apply(controller)

    stop = controller.control_step(0.05, _telemetry(values))

    assert stop is False
    assert len(mock.sent) == 5
    sent = dict(mock.sent)
    for _, val in mock.sent:
        assert math.isfinite(val)
    from ismpu.io.datarefs import (
        LEFT_BRAKE_RATIO, RIGHT_BRAKE_RATIO, THROTTLE_RATIO_L, THROTTLE_RATIO_R, YOKE_HEADING_RATIO,
    )
    assert 0.0 <= sent[LEFT_BRAKE_RATIO] <= 1.0
    assert 0.0 <= sent[RIGHT_BRAKE_RATIO] <= 1.0
    assert -1.0 <= sent[THROTTLE_RATIO_L] <= 0.0
    assert -1.0 <= sent[THROTTLE_RATIO_R] <= 0.0
    assert -1.0 <= sent[YOKE_HEADING_RATIO] <= 1.0


def test_nws_fail_preset_injects_failure():
    """NWS_FAIL активирует отказ руления: steering_eff→0, руль обнуляется на выходе."""
    from ismpu.config.scenarios import NWS_FAIL
    from ismpu.io.datarefs import YOKE_HEADING_RATIO

    values = _nominal_values(groundspeed=50.0)
    mock = MockXPC(values)
    controller = ControllingSystem(_backend(mock))
    NWS_FAIL.apply(controller)

    assert controller.failures.state.steering_eff == 0.0  # отказ активирован
    controller.control_step(0.05, _telemetry(values))
    # apply_failures обнулил руль перед отправкой (удержание — дифф. торможением/тягой)
    assert dict(mock.sent)[YOKE_HEADING_RATIO] == pytest.approx(0.0)


def test_default_preset_leaves_all_actuators_healthy():
    from ismpu.config.scenarios import DEFAULT

    controller = ControllingSystem(_backend(MockXPC(_nominal_values())))
    DEFAULT.apply(controller)

    assert controller.failures.state.steering_eff == 1.0  # отказ не активирован


def test_control_step_stops_and_sends_nothing_on_missing_telemetry():
    values = _nominal_values()
    values[GROUNDSPEED] = None  # выпадение телеметрии
    mock = MockXPC(values)
    controller = ControllingSystem(_backend(mock))
    DEFAULT.apply(controller)

    stop = controller.control_step(0.05, _telemetry(values))

    assert stop is True
    assert mock.sent == []


def test_control_step_stops_on_invalid_frame_even_with_numeric_fields():
    """Бэкенд стенда при обрыве связи отдаёт НУЛИ с valid=False, а не None.

    Проверка «поле is None» пропустила бы groundspeed = 0.0 дальше, где он тут же выглядел бы
    как «достигнута скорость руления», и эпизод молча засчитался бы пройденным.
    """
    from ismpu.envs.sim_interface import Telemetry

    mock = MockXPC(_nominal_values())
    controller = ControllingSystem(_backend(mock))
    DEFAULT.apply(controller)
    dropped = Telemetry(lat=0.0, lon=0.0, groundspeed_ms=0.0, heading_true_deg=0.0, valid=False)

    assert controller.control_step(0.05, dropped) is True
    assert mock.sent == []
