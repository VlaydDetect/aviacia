"""Уход на второй круг (fallback в воздухе): условия срабатывания и передача управления пилоту.

Проверяется решение (в воздухе, выше высоты решения, при устойчивом невыполнении допусков ТЗ и
убранном реверсе), команда манёвра (взлётный режим + кабрирование + крылья в горизонт) и передача
пилоту по установившемуся набору (снятие заявки каналов). Аэродинамика не моделируется: кадры
набора задаются сценарно, как и в `ScriptedFlightBench`.
"""

from types import SimpleNamespace

import pytest

from ismpu.config.constants import DT
from ismpu.config.requirements import GO_AROUND_CONFIRM_TICKS
from ismpu.config.scenarios import SCENARIOS
from ismpu.control.flight import FlightSegment
from ismpu.control.system import ControllingSystem, GoAroundManeuver
from ismpu.envs.ics_sim import ICSSim, Telemetry
from ismpu.io.ics_connector import ControlModeState

from fakes import airborne_inputs, FakeConnector


def _frame(radio_altitude_ft, **overrides) -> Telemetry:
    return Telemetry.from_ics(airborne_inputs(radio_altitude_ft=radio_altitude_ft, **overrides))


def _armed_controller() -> ControllingSystem:
    """Контур на заходе: `begin_flight` по кадру в воздухе выше 400 футов."""
    c = ControllingSystem()
    c.begin_flight(_frame(1000.0))
    assert c.segment is FlightSegment.APPROACH
    return c


def _drive(controller, frame, ticks) -> bool:
    finished = False
    for _ in range(ticks):
        finished = controller.control_step(DT, telemetry=frame, send=False)
        if finished:
            break
    return finished


def test_tolerance_violation_above_gate_triggers_go_around():
    """Устойчивое превышение курсового допуска выше высоты решения → уход на второй круг."""
    c = _armed_controller()
    bad = _frame(200.0, LocDeviation=0.1)          # ~1.6° по курсу > 0.7°, выше 30 м
    _drive(c, bad, GO_AROUND_CONFIRM_TICKS + 20)   # запас тактов, чтобы тангаж вышел на кабрирование
    assert c.go_around is not None
    assert "COURSE" in c.go_around_reason
    # Команда манёвра: РУД на полный вперёд, кабрирование, крылья в горизонт.
    assert c.state.cmd_throttle_norm == pytest.approx(1.0)
    assert c.state.cmd_throttle_l_rate > 0.0 and c.state.cmd_throttle_r_rate > 0.0
    assert c.state.cmd_elevator > 0.0                              # нос вверх (перегрузка > 0)
    assert c.state.rudder_cmd == pytest.approx(0.0)               # руль направления не работаем
    assert c.approach_channel.result.target_roll_deg == pytest.approx(0.0)  # крылья в горизонт
    assert c.approach_channel.result.go_around is True


def test_debounce_delays_trigger():
    """Один-два кадра за допуском ухода не вызывают — нужен устойчивый выход (дебаунс)."""
    c = _armed_controller()
    _drive(c, _frame(200.0, LocDeviation=0.1), GO_AROUND_CONFIRM_TICKS - 1)
    assert c.go_around is None                       # порог дебаунса ещё не набран


def test_no_go_around_below_decision_height():
    """Ниже высоты решения (30 м) заход не прерывается даже при невыполнении допусков."""
    c = _armed_controller()
    _drive(c, _frame(50.0, LocDeviation=0.1), GO_AROUND_CONFIRM_TICKS + 5)   # 50 футов < 30 м
    assert c.go_around is None


def test_touchdown_wins_over_bad_ils_and_enters_rollout():
    """Касание проверяется до tolerance: начатую посадку не превращаем в уход."""
    c = ControllingSystem()
    c.bind_scenario(SCENARIOS["default"], "mc21")
    c.begin_flight(_frame(1000.0))
    touchdown = _frame(
        0.5,
        LocDeviation=0.1,
        LeftGearWeightOnWheels=1,
    )

    assert c.control_step(DT, telemetry=touchdown, send=False) is False
    assert c.segment is FlightSegment.ROLLOUT
    assert c.go_around is None


def test_touchdown_also_wins_over_an_already_started_go_around():
    """Если набор не состоялся и стойка обжалась, воздушный закон на полосе не продолжается."""
    c = ControllingSystem()
    c.bind_scenario(SCENARIOS["default"], "mc21")
    c.begin_flight(_frame(1000.0))
    c.go_around = GoAroundManeuver(reason="тест", entry_radio_altitude_ft=200.0)
    c.go_around_reason = "тест"

    touchdown = _frame(0.5, LeftGearWeightOnWheels=1)
    assert c.control_step(DT, telemetry=touchdown, send=False) is False
    assert c.segment is FlightSegment.ROLLOUT
    assert c.state.cmd_elevator == pytest.approx(0.0)


def test_no_go_around_on_ground():
    """На пробеге ухода нет — segment guard (козление удерживает защёлка сегмента, тест отдельно)."""
    c = ControllingSystem()
    c.segment = FlightSegment.ROLLOUT
    bad = SimpleNamespace(landing_allowed=False, violations=("COURSE",))
    assert c._should_go_around(_frame(200.0, LocDeviation=0.1), bad) is None


def test_no_go_around_when_reverse_deployed():
    """Если реверс уже включён — взлёт невозможен, ухода нет."""
    c = _armed_controller()
    c.state.cmd_rev_l = -0.5
    bad = SimpleNamespace(landing_allowed=False, violations=("COURSE",))
    assert c._should_go_around(_frame(200.0), bad) is None


def test_go_around_completes_on_established_climb():
    """Устойчивый набор (прирост высоты + положительная верт. скорость) завершает манёвр."""
    c = _armed_controller()
    c.go_around = GoAroundManeuver(reason="тест", entry_radio_altitude_ft=200.0)
    c.go_around_reason = "тест"
    climb = _frame(300.0, VerticalSpeed=600.0)       # +100 футов над входом, набор 600 fpm
    assert c.control_step(DT, telemetry=climb, send=False) is True
    # Воздушные команды сняты — управление отдаётся пилоту.
    assert c.state.cmd_elevator == pytest.approx(0.0)
    assert c.state.cmd_throttle_norm == pytest.approx(0.0)


def test_go_around_starts_with_clean_roll_and_pitch_pid_state():
    c = _armed_controller()
    frame = _frame(200.0, RollAngle=5.0, PitchAngle=2.5, VerticalSpeed=-700.0)
    c.control_step(DT, telemetry=frame, send=False)
    previous_target_pitch = c.approach_channel._target_pitch_deg
    c.approach_channel.roll_pid.integral = 10.0
    c.approach_channel.roll_pid.filtered_derivative = 20.0
    c.approach_channel.pitch_pid.integral = -10.0

    c._start_go_around("тест", frame)
    assert c.approach_channel.roll_pid.integral == 0.0
    assert c.approach_channel.pitch_pid.integral == 0.0
    assert c.approach_channel._target_pitch_deg == previous_target_pitch
    c._go_around_step(DT, frame)

    # У стенда знак проводки инверсный: положительная команда убирает положительный крен.
    # Главное здесь — чистый P-ответ, а не сохранённые ~3° localizer I-term.
    assert c.state.cmd_aileron == c.approach_channel.roll_pid.max_out
    assert c.approach_channel.roll_pid.filtered_derivative == 0.0
    c._go_around_step(DT, frame)
    assert c.state.cmd_elevator > 0.0


def test_go_around_timeout_without_climb_is_an_error():
    c = _armed_controller()
    frame = _frame(200.0, VerticalSpeed=-200.0)
    c._start_go_around("тест", frame)
    c.go_around.elapsed_s = c.approach_channel.config.go_around_max_seconds - DT

    assert c.control_step(DT, telemetry=frame, send=False) is True
    assert c.abort_reason == "go_around_timeout_no_climb"
    assert c.state.cmd_elevator == pytest.approx(0.0)
    assert c.state.cmd_throttle_norm == pytest.approx(0.0)


def test_go_around_hands_off_via_deactivate():
    """После установившегося набора цикл снимает заявку каналов (ControlMode=Off, маска=0)."""
    conn = FakeConnector(airborne_inputs(radio_altitude_ft=300.0))
    c = ControllingSystem(ICSSim(connector=conn, aircraft_profile="mc21"))
    c.begin_flight(_frame(1000.0))
    _drive(c, _frame(200.0, LocDeviation=0.1), GO_AROUND_CONFIRM_TICKS)
    assert c.go_around is not None
    assert _drive(c, _frame(300.0, VerticalSpeed=600.0, LocDeviation=0.1), 50) is True
    # Цикл на остановке отдаёт управление: control_exception снимает заявку каналов.
    c.control_exception()
    assert any(o.ControlValidMask == 0 and o.ControlMode is ControlModeState.Off
               for o in conn.sent_outputs)
