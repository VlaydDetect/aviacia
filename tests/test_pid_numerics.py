"""Опциональная численность PID (шаг 5): каждый флаг проверяется на том дефекте, который лечит.

Главное свойство — **при значениях по умолчанию поведение бит-в-бит прежнее**: пресеты
откалиброваны под старую численность, и включение любого флага требует перетюна. Поэтому
первый блок тестов фиксирует именно это.
"""

import math

import pytest

from ismpu.config.constants import DT
from ismpu.control.pid import PIDController
from ismpu.control.system import ControllingSystem
from ismpu.envs.sim_interface import XPlaneBackend
from ismpu.control.failures import FailureMode
from ismpu.envs.scenario import SCENARIO_PRESETS

from test_rollout_env import FakeXPC, _scripted_values, _telemetry


def _legacy_reference(errors, *, kp, ki, kd, dt, aw, decay, tf, lo, hi):
    """Независимая реализация ПРЕЖНЕЙ численности — эталон для проверки парити."""
    integral, prev_error, filtered, outputs = 0.0, None, 0.0, []
    for error in errors:
        if decay > 0.0:
            integral *= math.exp(-decay * dt)
        integral += error * dt
        integral = max(-aw, min(aw, integral))

        derivative = 0.0
        if prev_error is not None:
            raw = (error - prev_error) / dt
            alpha = dt / (dt + tf)
            filtered = alpha * raw + (1.0 - alpha) * filtered
            derivative = filtered
        else:
            filtered = 0.0
        prev_error = error

        out = kp * error + ki * integral + kd * derivative
        outputs.append(max(lo, min(hi, out)))
    return outputs


# --------------------------------------------------------------------------- #
# Парити по умолчанию
# --------------------------------------------------------------------------- #

def test_defaults_reproduce_the_legacy_numerics_bit_for_bit():
    params = dict(kp=0.8, ki=0.15, kd=0.05, dt=DT, aw=10.0, decay=0.3, tf=0.1, lo=0.0, hi=1.0)
    errors = [1.0, 0.9, 0.4, -0.2, -0.5, 0.3, 2.0, 2.0, 2.0, -1.0]

    pid = PIDController(kp=0.8, ki=0.15, kd=0.05, min_out=0.0, max_out=1.0,
                        anti_windup=10.0, integral_decay=0.3, der_filter_tf=0.1, name="t")
    got = [pid.compute(e, DT) for e in errors]

    assert got == _legacy_reference(errors, **params)


def test_all_optional_flags_default_to_off():
    pid = PIDController(kp=1.0, ki=0.0, kd=0.0)
    assert pid.derivative_on_measurement is False
    assert pid.conditional_anti_windup is False
    assert pid.exact_discretization is False
    assert pid.tracking_tau_s is None


def test_control_step_is_unchanged_when_tracking_is_off():
    """`_track_applied` вызывается безусловно, но обязан быть no-op без `tracking_tau_s`."""
    telem = _telemetry()

    ctrl = ControllingSystem(XPlaneBackend(xpc=FakeXPC(_scripted_values()), settle_s=0.0, reload_each_reset=False))
    SCENARIO_PRESETS["nws_fail"].apply_control(ctrl)
    for _ in range(5):
        ctrl.control_step(DT, telem, send=True)
    integrals_with_hook = {name: p.integral for name, p in ctrl.pids.items()}

    ctrl2 = ControllingSystem(XPlaneBackend(xpc=FakeXPC(_scripted_values()), settle_s=0.0, reload_each_reset=False))
    SCENARIO_PRESETS["nws_fail"].apply_control(ctrl2)
    for _ in range(5):
        # тот же цикл, но без хука трекинга
        ctrl2.longitudinal_channel.calc_commands(DT, ctrl2.state, telem)
        ctrl2.lateral_channel.calc_commands(DT, ctrl2.state, telem)
        ctrl2.state.clamp_all(ctrl2.pids)
        if ctrl2.state.break_control:
            break
        ctrl2.state.apply_failures(ctrl2.failures.state)
        ctrl2.sim.step(ctrl2.state)

    assert integrals_with_hook == {name: p.integral for name, p in ctrl2.pids.items()}


# --------------------------------------------------------------------------- #
# (а) Back-calculation — главный для нашего контура
# --------------------------------------------------------------------------- #

def test_tracking_is_a_noop_without_tau():
    pid = PIDController(kp=1.0, ki=0.5, kd=0.0, min_out=0.0, max_out=1.0)
    pid.compute(1.0, DT)
    before = pid.integral
    pid.track(0.0, DT)                     # команда «съедена» отказом
    assert pid.integral == before


def test_tracking_unwinds_the_integrator_when_the_actuator_is_dead():
    """При `steering_eff = 0` применяется 0 вместо выхода PID — интегратор обязан это учесть."""
    common = dict(kp=1.0, ki=2.0, kd=0.0, min_out=-1.0, max_out=1.0, anti_windup=10.0)
    blind = PIDController(**common)
    tracked = PIDController(**common, tracking_tau_s=0.5)

    for _ in range(40):
        blind.compute(1.0, DT)
        tracked.compute(1.0, DT)
        tracked.track(0.0, DT)             # актуатор мёртв: применён ноль

    assert blind.integral > tracked.integral          # слепой копит быстрее
    assert tracked.integral < 0.5 * blind.integral    # и заметно


def test_tracking_does_nothing_when_the_command_is_applied_as_computed():
    """Если применено ровно то, что выдал PID, коррекции быть не должно."""
    pid = PIDController(kp=1.0, ki=0.5, kd=0.0, min_out=-1.0, max_out=1.0, tracking_tau_s=0.5)
    for _ in range(10):
        out = pid.compute(0.3, DT)
        before = pid.integral
        pid.track(out, DT)
        assert pid.integral == pytest.approx(before)


def test_tracking_through_control_step_under_a_real_failure():
    """Сквозная проверка: NWS-отказ обнуляет руль, интегратор курсового PID не должен копить."""
    def run(tau):
        ctrl = ControllingSystem(XPlaneBackend(xpc=FakeXPC(_scripted_values(groundspeed=50.0)), settle_s=0.0, reload_each_reset=False))
        SCENARIO_PRESETS["nws_fail"].apply_control(ctrl)
        ctrl.apply_failure(FailureMode.NWS_FAIL)          # steering_eff = 0
        pid = ctrl.pids["runway_center_pid"]
        pid.tracking_tau_s = tau
        pid.ki = max(pid.ki, 0.2)                          # чтобы интеграл вообще был заметен
        telem = _telemetry(groundspeed=50.0)
        for _ in range(30):
            if ctrl.control_step(DT, telem, send=True):
                break
        return abs(pid.integral)

    assert run(0.5) <= run(None)


# --------------------------------------------------------------------------- #
# (б) Производная по измерению
# --------------------------------------------------------------------------- #

def test_derivative_on_measurement_requires_a_measurement():
    pid = PIDController(kp=1.0, ki=0.0, kd=0.1, derivative_on_measurement=True)
    with pytest.raises(ValueError, match="measurement"):
        pid.compute(1.0, DT)


def test_derivative_on_measurement_removes_the_setpoint_kick():
    """Уставка прыгает, объект стоит на месте — D-составляющая не должна реагировать.

    В продольном канале уставка едет по эталонной кривой непрерывно, так что производная по
    ошибке постоянно подмешивает движение уставки вместо динамики объекта.
    """
    measurement = 0.0
    setpoints = [0.0, 0.0, 5.0, 5.0, 5.0]      # скачок уставки на третьем такте

    on_error = PIDController(kp=0.0, ki=0.0, kd=1.0, min_out=-100.0, max_out=100.0,
                             der_filter_tf=0.0)
    on_meas = PIDController(kp=0.0, ki=0.0, kd=1.0, min_out=-100.0, max_out=100.0,
                            der_filter_tf=0.0, derivative_on_measurement=True)

    kicks_error, kicks_meas = [], []
    for sp in setpoints:
        error = sp - measurement
        kicks_error.append(on_error.compute(error, DT))
        kicks_meas.append(on_meas.compute(error, DT, measurement=measurement))

    assert max(abs(v) for v in kicks_error) > 1.0        # рывок от скачка уставки
    assert all(v == pytest.approx(0.0) for v in kicks_meas)   # объект не двигался → нуль


def test_derivative_on_measurement_still_reacts_to_the_plant():
    pid = PIDController(kp=0.0, ki=0.0, kd=1.0, min_out=-100.0, max_out=100.0,
                        der_filter_tf=0.0, derivative_on_measurement=True)
    outputs = [pid.compute(0.0, DT, measurement=m) for m in (0.0, 0.0, 1.0, 2.0)]
    assert any(abs(v) > 1.0 for v in outputs)


# --------------------------------------------------------------------------- #
# (в) Условный anti-windup
# --------------------------------------------------------------------------- #

def test_conditional_anti_windup_blocks_winding_deeper_into_saturation():
    common = dict(kp=1.0, ki=1.0, kd=0.0, min_out=0.0, max_out=1.0, anti_windup=100.0)
    hard = PIDController(**common)
    conditional = PIDController(**common, conditional_anti_windup=True)

    for _ in range(50):                     # длительное насыщение сверху
        hard.compute(5.0, DT)
        conditional.compute(5.0, DT)

    assert conditional.integral < hard.integral


def test_conditional_anti_windup_still_allows_unwinding():
    """Выход ИЗ насыщения должен разрешаться всегда, иначе регулятор залипнет.

    kp намеренно мал: иначе пропорциональная часть насыщает выход сама, интеграл не успевает
    накопиться и проверять было бы нечего (см. соседний тест).
    """
    pid = PIDController(kp=0.1, ki=1.0, kd=0.0, min_out=0.0, max_out=1.0,
                        anti_windup=100.0, conditional_anti_windup=True)
    for _ in range(60):
        pid.compute(1.0, DT)
    saturated = pid.integral
    assert saturated > 0.5                    # интеграл реально накопился...
    assert saturated < 1.0                    # ...но был остановлен на границе насыщения

    for _ in range(30):
        pid.compute(-1.0, DT)                 # ошибка сменила знак
    assert pid.integral < saturated           # раскрутка разрешена


def test_conditional_anti_windup_pins_the_integral_when_p_alone_saturates():
    """Если насыщает уже пропорциональная часть, интегрировать нельзя вообще — и это верно.

    Поведение неочевидное, поэтому зафиксировано отдельно: интеграл не «почти не растёт»,
    а стоит ровно на нуле, пока выход упёрт исключительно из-за P.
    """
    pid = PIDController(kp=1.0, ki=1.0, kd=0.0, min_out=0.0, max_out=1.0,
                        anti_windup=100.0, conditional_anti_windup=True)
    for _ in range(30):
        pid.compute(5.0, DT)                  # kp·e = 5.0 ≫ max_out
    assert pid.integral == 0.0


def test_conditional_anti_windup_matches_plain_behaviour_while_unsaturated():
    common = dict(kp=0.1, ki=0.1, kd=0.0, min_out=-10.0, max_out=10.0, anti_windup=100.0)
    hard = PIDController(**common)
    conditional = PIDController(**common, conditional_anti_windup=True)
    for error in (0.1, 0.2, -0.1, 0.05):
        assert hard.compute(error, DT) == pytest.approx(conditional.compute(error, DT))


# --------------------------------------------------------------------------- #
# (г) Точная дискретизация
# --------------------------------------------------------------------------- #

def test_exact_filter_alpha_matches_the_zoh_solution():
    tf = 0.1
    pid = PIDController(kp=0.0, ki=0.0, kd=1.0, der_filter_tf=tf, exact_discretization=True)
    assert pid._filter_alpha(DT) == pytest.approx(-math.expm1(-DT / tf))
    # Прежняя аппроксимация занижает вес фильтра — на крупном dt расхождение заметно.
    approx = PIDController(kp=0.0, ki=0.0, kd=1.0, der_filter_tf=tf)
    assert approx._filter_alpha(0.5) != pytest.approx(pid._filter_alpha(0.5), rel=1e-3)


def test_exact_and_approximate_converge_as_dt_shrinks():
    tf = 0.1
    exact = PIDController(kp=0.0, ki=0.0, kd=1.0, der_filter_tf=tf, exact_discretization=True)
    approx = PIDController(kp=0.0, ki=0.0, kd=1.0, der_filter_tf=tf)
    assert exact._filter_alpha(1e-4) == pytest.approx(approx._filter_alpha(1e-4), rel=1e-3)


def test_zero_filter_constant_disables_filtering_in_both_modes():
    for exact in (False, True):
        pid = PIDController(kp=0.0, ki=0.0, kd=1.0, der_filter_tf=0.0, exact_discretization=exact)
        assert pid._filter_alpha(DT) == pytest.approx(1.0)


def test_exact_leak_matches_the_closed_form_for_constant_error():
    """Точная утечка = решение dI/dt = e − I/τ при постоянной e, а не приращение e·dt."""
    decay, error, dt = 2.0, 1.0, 0.5
    pid = PIDController(kp=0.0, ki=1.0, kd=0.0, min_out=-100.0, max_out=100.0,
                        anti_windup=100.0, integral_decay=decay, exact_discretization=True)
    pid.compute(error, dt)
    tau = 1.0 / decay
    expected = error * tau * (1.0 - math.exp(-decay * dt))
    assert pid.integral == pytest.approx(expected)

    # Прежняя формула на таком dt заметно завышает: e·dt = 0.5 против точных ≈0.316.
    plain = PIDController(kp=0.0, ki=1.0, kd=0.0, min_out=-100.0, max_out=100.0,
                          anti_windup=100.0, integral_decay=decay)
    plain.compute(error, dt)
    assert plain.integral > pid.integral


def test_exact_leak_converges_to_the_plain_increment_for_small_dt():
    decay, error, dt = 2.0, 1.0, 1e-5
    exact = PIDController(kp=0.0, ki=1.0, kd=0.0, min_out=-100.0, max_out=100.0,
                          anti_windup=100.0, integral_decay=decay, exact_discretization=True)
    plain = PIDController(kp=0.0, ki=1.0, kd=0.0, min_out=-100.0, max_out=100.0,
                          anti_windup=100.0, integral_decay=decay)
    exact.compute(error, dt)
    plain.compute(error, dt)
    assert exact.integral == pytest.approx(plain.integral, rel=1e-4)
