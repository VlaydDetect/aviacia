"""Управление на всём интервале полёта: заход → касание → пробег → руление.

Проверяется **стыковка**, а не аэродинамика: какой стимул рукопожатия уходит на стенд, какие
каналы заявлены на каждом участке, в какой момент заход передаёт управление пробегу и что
последним видит стенд при выходе. Сам воздушный закон проверяется отдельно
(`test_approach_channel.py`), сам пробег — тоже (`test_control_parity.py`, `test_ics_sim.py`).
"""

import pytest

from ismpu.config.constants import DT
from ismpu.config.ics import (
    ControlValid, ROLLOUT_CONTROL_MASK, AIRBORNE_CONTROL_MASK, FlightPhase,
    ENGAGE_MIN_RADIO_ALTITUDE_FT, ENGAGE_AIR_READY_DWELL_S, ENGAGE_MIN_READY_FRAMES,
    TERMINAL_RADIO_ALTITUDE_FT,
)
from ismpu.control.flight import (
    FlightSegment, ApproachRefused, is_airborne, initial_segment, touched_down,
)
from ismpu.control.system import ControllingSystem
from ismpu.envs.ics_sim import ICSSim, Telemetry
from ismpu.envs.scenario import SCENARIO_PRESETS
from ismpu.io.ics_connector import ControlModeState
from ismpu.io.ics_engagement import IcsEngagement, EngagementInputs, EngagementState

from fakes import (
    airborne_inputs, engaged_inputs, FakeConnector, HandshakeBench, ScriptedFlightBench, telemetry,
)


class _Clock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


def _air(**overrides):
    base = dict(all_gear_on_ground=False, groundspeed_kts=140.0, radio_altitude_ft=1200.0,
                agent_is_active=0, telemetry_valid=True)
    base.update(overrides)
    return EngagementInputs(**base)


def _pump(eng, clock, inputs, ticks, *, dt=0.05):
    for _ in range(ticks):
        eng.step(inputs)
        eng.on_frame_sent(eng.mode_ai_ready)
        clock.advance(dt)


# --------------------------------------------------------------------------- #
# Рукопожатие в воздухе
# --------------------------------------------------------------------------- #

def test_airborne_stimulus_reaches_approach_after_the_full_dwell():
    """Воздушное включение — это фронт `Off → Approach` после выдержки, а не сразу Approach."""
    clock = _Clock()
    eng = IcsEngagement(clock=clock)

    eng.step(_air())
    assert eng.state is EngagementState.READY_DWELL
    assert eng.control_mode is ControlModeState.Off     # во время выдержки строго Off
    assert eng.mode_ai_ready == 1

    ticks = int(ENGAGE_AIR_READY_DWELL_S / 0.05) + 5
    _pump(eng, clock, _air(), ticks=ticks)
    assert eng.state is EngagementState.COMMAND_APPROACH
    assert eng.control_mode is ControlModeState.Approach
    assert eng.engaged is False                          # стенд ещё не активен


def test_airborne_dwell_is_longer_than_the_ground_one():
    """2.2 с — подтверждённое на стенде значение; наземные 2.0 для захода недостаточны."""
    clock = _Clock()
    eng = IcsEngagement(clock=clock)
    _pump(eng, clock, _air(), ticks=int(2.0 / 0.05) + 1)   # ровно наземная выдержка
    assert eng.state is EngagementState.READY_DWELL         # для воздуха ещё мало
    _pump(eng, clock, _air(), ticks=6)
    assert eng.state is EngagementState.COMMAND_APPROACH


def test_no_airborne_stimulus_below_the_altitude_threshold():
    """Ниже 400 футов стенд управление не отдаёт — гнать туда стимул бессмысленно."""
    clock = _Clock()
    eng = IcsEngagement(clock=clock)
    _pump(eng, clock, _air(radio_altitude_ft=ENGAGE_MIN_RADIO_ALTITUDE_FT - 1.0), ticks=200)
    assert eng.state is EngagementState.IDLE


def test_missing_radio_altitude_is_not_treated_as_the_ground():
    """Необъявленная радиовысота — «стенд не сообщил», а не «ноль футов».

    Иначе ВС в воздухе с молчащим радиовысотомером получил бы наземный стимул `0 → 4`.
    """
    clock = _Clock()
    eng = IcsEngagement(clock=clock)
    _pump(eng, clock, _air(radio_altitude_ft=None), ticks=200)
    assert eng.state is EngagementState.IDLE
    assert "радиовысота" in eng.blocking_reason(_air(radio_altitude_ft=None))


def test_touchdown_hands_the_approach_over_to_rollout():
    """После касания режим меняется на пробег — но не раньше: смена режима на глиссаде
    сбрасывает автопилот стенда."""
    clock = _Clock()
    eng = IcsEngagement(clock=clock)
    _pump(eng, clock, _air(), ticks=int(ENGAGE_AIR_READY_DWELL_S / 0.05) + 5)
    assert eng.state is EngagementState.COMMAND_APPROACH

    # Фаза выравнивания режим не меняет.
    eng.step(_air(radio_altitude_ft=30.0,
                  flight_phase=int(FlightPhase.LAND_FLARE_AND_TOUCHDOWN)))
    assert eng.state is EngagementState.COMMAND_APPROACH

    eng.step(_air(all_gear_on_ground=True, radio_altitude_ft=0.0, groundspeed_kts=135.0,
                  flight_phase=int(FlightPhase.LAND_RUN)))
    assert eng.state is EngagementState.COMMAND_ROLLOUT
    assert eng.control_mode is ControlModeState.Rollout
    assert eng.adopted is False        # заход довели мы, это передача, а не подхват


def test_activity_loss_in_the_terminal_window_does_not_drop_the_approach():
    """Ниже 80 футов потеря `AgentIsActive` не повод бросать органы: до земли секунды."""
    clock = _Clock()
    eng = IcsEngagement(clock=clock)
    _pump(eng, clock, _air(agent_is_active=1), ticks=int(ENGAGE_AIR_READY_DWELL_S / 0.05) + 5)
    assert eng.engaged is True

    eng.step(_air(agent_is_active=0, radio_altitude_ft=TERMINAL_RADIO_ALTITUDE_FT - 10.0))
    assert eng.engaged is True                # окно удерживает уже полученное подтверждение

    eng.step(_air(agent_is_active=0, radio_altitude_ft=TERMINAL_RADIO_ALTITUDE_FT + 200.0))
    assert eng.engaged is False               # выше окна — обычное правило


def test_the_terminal_window_never_creates_a_confirmation():
    """Окно только удерживает подтверждение. Само оно включения не даёт."""
    clock = _Clock()
    eng = IcsEngagement(clock=clock)
    eng.request_approach()
    _pump(eng, clock, _air(agent_is_active=0, radio_altitude_ft=40.0), ticks=20)
    assert eng.engaged is False


# --------------------------------------------------------------------------- #
# Участки полёта
# --------------------------------------------------------------------------- #

def test_a_frame_without_a_bench_packet_is_never_airborne():
    """Синтетический кадр — «нечем судить», а не «в воздухе».

    На таких кадрах работают весь наземный контур и среда обучения; уход в воздушный закон
    сломал бы их молча.
    """
    assert is_airborne(telemetry(50.0)) is False
    assert initial_segment(telemetry(50.0)) is FlightSegment.ROLLOUT
    assert is_airborne(Telemetry.invalid()) is False
    assert initial_segment(None) is FlightSegment.ROLLOUT


def test_airborne_frame_starts_on_the_approach():
    telem = Telemetry.from_ics(airborne_inputs(radio_altitude_ft=1200.0))
    assert is_airborne(telem) is True
    assert initial_segment(telem) is FlightSegment.APPROACH


def test_touchdown_is_any_main_gear_not_the_nose():
    """Носовая стойка обжимается позже основных — ждать её значит пропустить начало пробега."""
    left_only = Telemetry.from_ics(airborne_inputs(radio_altitude_ft=0.0,
                                                   LeftGearWeightOnWheels=1))
    assert touched_down(left_only) is True

    nose_only = Telemetry.from_ics(airborne_inputs(radio_altitude_ft=0.0,
                                                   NoseGearWeightOnWheels=1))
    assert touched_down(nose_only) is False


def test_the_segment_machine_only_moves_forward():
    """«Козление» после касания снимает обжатие на секунду — назад в заход возвращаться нельзя."""
    controller = ControllingSystem()
    SCENARIO_PRESETS["default"].apply_control(controller)
    controller.begin_flight(Telemetry.from_ics(airborne_inputs(radio_altitude_ft=1200.0)))
    assert controller.segment is FlightSegment.APPROACH

    touchdown = Telemetry.from_ics(airborne_inputs(radio_altitude_ft=0.0,
                                                   LeftGearWeightOnWheels=1,
                                                   RightGearWeightOnWheels=1))
    controller.control_step(DT, touchdown, send=False)
    assert controller.segment is FlightSegment.ROLLOUT

    # Кадр «снова в воздухе» участок не возвращает.
    controller.control_step(DT, Telemetry.from_ics(airborne_inputs(radio_altitude_ft=60.0)),
                            send=False)
    assert controller.segment is FlightSegment.ROLLOUT


def test_the_rollout_default_keeps_the_existing_ground_behaviour():
    """Без `begin_flight` участок остаётся пробегом — среда обучения на это и опирается."""
    controller = ControllingSystem()
    SCENARIO_PRESETS["default"].apply_control(controller)
    assert controller.segment is FlightSegment.ROLLOUT
    controller.control_step(DT, telemetry(60.0), send=False)
    assert controller.state.cmd_elevator == 0.0        # воздушный закон не вмешивался
    assert controller.segment is FlightSegment.ROLLOUT


def test_the_first_ground_tick_is_computed_by_the_ground_channels():
    """В такте касания команда обязана быть уже наземной, а не последней командой захода."""
    controller = ControllingSystem()
    SCENARIO_PRESETS["default"].apply_control(controller)
    controller.begin_flight(Telemetry.from_ics(airborne_inputs(radio_altitude_ft=1200.0)))

    touchdown = Telemetry.from_ics(engaged_inputs(GroundSpeed=140.0))
    controller.control_step(DT, touchdown, send=False)
    assert controller.segment is FlightSegment.ROLLOUT
    assert controller.state.cmd_elevator == 0.0
    assert controller.state.cmd_rev_l < 0.0            # реверс уже выпущен


# --------------------------------------------------------------------------- #
# Условия прерывания захода (перенос супервизора эталона, а не только его закона)
# --------------------------------------------------------------------------- #

def test_approach_is_refused_in_a_non_landing_flap_configuration():
    """Таблицы захода МС-21 к чистому крылу неприменимы — вести по ним нельзя.

    Молчаливая подмена запасной конфигурацией опаснее отказа: уставка скорости шла бы к VAPP
    посадочной конфигурации, а весь мониторинг огибающей молчал бы, сравнивая с порогами той же
    неприменимой таблицы. Эталон в этой ситуации не отправляет ни одного кадра.
    """
    controller = ControllingSystem()
    clean_wing = Telemetry.from_ics(airborne_inputs(radio_altitude_ft=1200.0, FlapsAngle=0.0))
    with pytest.raises(ApproachRefused) as exc:
        controller.begin_flight(clean_wing)
    assert "механизация" in str(exc.value)

    # Штатная посадочная конфигурация — обе допустимы, независимо от настроенной запасной.
    for flaps in (27.0, 36.0):
        ok = ControllingSystem()
        assert ok.begin_flight(
            Telemetry.from_ics(airborne_inputs(radio_altitude_ft=1200.0, FlapsAngle=flaps))
        ) is FlightSegment.APPROACH


def test_losing_ils_validity_aborts_the_approach():
    """Нулевое отклонение при снятой валидности неотличимо от «точно на оси»."""
    controller = ControllingSystem()
    SCENARIO_PRESETS["default"].apply_control(controller)
    controller.begin_flight(Telemetry.from_ics(airborne_inputs(radio_altitude_ft=1200.0)))

    blind = Telemetry.from_ics(airborne_inputs(radio_altitude_ft=1200.0, LocDeviationValid=0))
    assert controller.control_step(DT, blind, send=False) is True
    assert controller.abort_reason is not None
    assert controller.state.cmd_elevator == 0.0


def test_ils_loss_inside_the_terminal_window_does_not_abort():
    """Ниже 80 футов до земли секунды — бросать органы там хуже, чем доработать."""
    controller = ControllingSystem()
    SCENARIO_PRESETS["default"].apply_control(controller)
    controller.begin_flight(Telemetry.from_ics(airborne_inputs(radio_altitude_ft=1200.0)))

    low = Telemetry.from_ics(airborne_inputs(radio_altitude_ft=TERMINAL_RADIO_ALTITUDE_FT - 20.0,
                                             LocDeviationValid=0, GSDeviationValid=0))
    assert controller.control_step(DT, low, send=False) is False
    assert controller.abort_reason is None


def test_the_segment_is_not_decided_by_a_frame_without_a_bench_packet():
    """Первый `read_telemetry` может вернуться по таймауту — это не «мы на полосе».

    Машина участков идёт только вперёд, поэтому решение по пустому кадру было бы необратимым:
    автомат включения ушёл бы в `Approach` по более поздним кадрам, а команду считали бы
    наземные каналы — на стенд полетели бы нулевой руль высоты и «пройденная дистанция»,
    интегрируемая в полёте.
    """
    controller = ControllingSystem()
    SCENARIO_PRESETS["default"].apply_control(controller)

    assert controller.begin_flight(Telemetry.invalid()) is FlightSegment.ROLLOUT
    controller.control_step(DT, Telemetry.from_ics(airborne_inputs(radio_altitude_ft=1500.0)),
                            send=False)
    assert controller.segment is FlightSegment.APPROACH      # решение пересмотрено на живом кадре


def test_a_decided_rollout_is_never_revised():
    """Пересмотр — только для отложенного решения, не для принятого."""
    controller = ControllingSystem()
    SCENARIO_PRESETS["default"].apply_control(controller)
    assert controller.begin_flight(Telemetry.from_ics(engaged_inputs())) is FlightSegment.ROLLOUT
    controller.control_step(DT, Telemetry.from_ics(airborne_inputs(radio_altitude_ft=1500.0)),
                            send=False)
    assert controller.segment is FlightSegment.ROLLOUT


# --------------------------------------------------------------------------- #
# Маска и содержимое команды по участкам
# --------------------------------------------------------------------------- #

def _engaged_airborne_sim(**overrides):
    """(sim, conn), где стенд уже принял воздушное управление (`ControlMode = Approach`)."""
    conn = FakeConnector(airborne_inputs(**overrides))
    sim = ICSSim(connector=conn)
    sim.engagement.request_approach()
    sim.read_telemetry()
    assert sim.engaged
    return sim, conn


def test_airborne_frame_declares_only_the_airborne_channels():
    sim, conn = _engaged_airborne_sim()
    controller = ControllingSystem(sim)
    SCENARIO_PRESETS["default"].apply_control(controller)
    controller.begin_flight(sim.read_telemetry())
    controller.control_step(DT)

    out = conn.sent_outputs[-1]
    assert out.ControlValidMask == int(AIRBORNE_CONTROL_MASK)
    assert out.ControlMode is ControlModeState.Approach
    assert ControlValid.BRAKE_LEFT not in ControlValid(out.ControlValidMask)
    assert out.BrakeLeftCmd == 0.0 and out.BrakeRightCmd == 0.0
    assert out.NoseWheelTillerCmd == 0.0
    assert out.ModeSpeed == 1 and out.ModeThrust == 1
    # Фазовые флаги молчат весь заход: объявление фазы меняет продольный закон стенда.
    assert out.ModeFlare == 0 and out.ModeFlareArm == 0
    assert out.ModeAlign == 0 and out.ModeRollout == 0 and out.ModeTaxi == 0


def test_airborne_frame_carries_the_commands_in_icd_units():
    sim, conn = _engaged_airborne_sim(RollAngle=4.0, IndicatedAirspeed=150.0)
    controller = ControllingSystem(sim)
    SCENARIO_PRESETS["default"].apply_control(controller)
    controller.begin_flight(sim.read_telemetry())
    controller.control_step(DT)

    out = conn.sent_outputs[-1]
    state = controller.state
    assert out.ElevatorCmd == state.cmd_elevator          # g, без пересчёта
    assert out.AileronCmd == state.cmd_aileron            # градусы
    assert out.ThrottleLeftRate == state.cmd_throttle_l_rate
    assert out.ThrottleRightRate == state.cmd_throttle_r_rate
    # Абсолютное положение маской не заявлено, но передаётся одинаковым на оба двигателя.
    assert out.ThrottleLeft == out.ThrottleRight == state.cmd_throttle_norm
    assert 0.0 <= out.ThrottleLeft <= 1.0


def test_quality_fields_are_reported_on_the_approach():
    """ТЗ 5.1.5: показатели выдерживания — отчёт, идущий вместе с командой."""
    sim, conn = _engaged_airborne_sim(LocDeviation=0.03, MagneticHeading=80.0)
    controller = ControllingSystem(sim)
    SCENARIO_PRESETS["default"].apply_control(controller)
    controller.begin_flight(sim.read_telemetry())
    controller.control_step(DT)

    out = conn.sent_outputs[-1]
    assert out.QualityLateralError > 0.0
    assert out.QualityHeadingError > 0.0


def test_quality_fields_are_reported_on_the_rollout_too():
    """На пробеге показатели считает наземный канал — в **метрах** от осевой, а не в точках КРМ.

    Иначе стенд получал бы либо замороженные величины момента касания (в единицах курсового
    маяка), либо постоянные нули при старте с полосы — «идеальное выдерживание» при любом сносе.
    """
    from fakes import kinematic_sim

    sim, bench = kinematic_sim(speed=60.0, lateral=6.0)
    controller = ControllingSystem(sim)
    SCENARIO_PRESETS["default"].apply_control(controller)
    controller.control_step(DT)

    out = bench.sent_outputs[-1]
    assert out.QualityLateralError == pytest.approx(6.0, abs=0.5)   # метры от оси
    assert out.QualitySpeedError > 0.0                              # узлы от эталонной кривой


def test_ground_frame_still_declares_only_the_ground_channels():
    """Регресс: расширение структуры не должно протащить руль высоты в маску пробега."""
    from fakes import engaged_sim

    sim, conn = engaged_sim(GroundSpeed=120.0)
    controller = ControllingSystem(sim)
    SCENARIO_PRESETS["default"].apply_control(controller)
    controller.control_step(DT)

    out = conn.sent_outputs[-1]
    assert out.ControlValidMask == int(ROLLOUT_CONTROL_MASK)
    assert out.ElevatorCmd == 0.0 and out.AileronCmd == 0.0
    # Скорости РУД на пробеге — свой, законный канал (им задаётся реверс); нулевыми они быть
    # не обязаны. А вот абсолютного положения на земле мы не выдаём.
    assert out.ThrottleLeft == 0.0 and out.ThrottleRight == 0.0


# --------------------------------------------------------------------------- #
# Полный прогон
# --------------------------------------------------------------------------- #

def test_a_whole_flight_runs_from_approach_to_taxi(monkeypatch):
    """Сквозной прогон: рукопожатие в воздухе → заход → касание → пробег → руление.

    Стенд сценарный (`ScriptedFlightBench`) — он проигрывает снижение и касание независимо от
    наших команд. Проверяется цепочка участков и режимов, а не то, как ВС слушается руля.
    """
    monkeypatch.setattr("ismpu.envs.ics_sim.time.sleep", lambda _s: None)

    bench = ScriptedFlightBench(radio_altitude_ft=600.0, descent_fps=40.0)
    sim = ICSSim(connector=bench)
    controller = ControllingSystem(sim)
    SCENARIO_PRESETS["default"].apply_control(controller)

    first = sim.read_telemetry()
    assert controller.begin_flight(first) is FlightSegment.APPROACH

    assert sim.warm_up(timeout_s=30.0) is True
    assert sim.engagement.control_mode is ControlModeState.Approach

    segments_seen = []
    for _ in range(4000):
        segments_seen.append(controller.segment)
        if controller.control_step(DT):
            break
    else:
        pytest.fail("прогон не завершился за отведённые такты")

    assert FlightSegment.APPROACH in segments_seen
    assert FlightSegment.ROLLOUT in segments_seen
    assert controller.hand_over_to_taxi() is True
    assert controller.segment is FlightSegment.TAXI

    modes = [o.ControlMode for o in bench.sent_outputs]
    # Порядок режимов на проводе: Off (выдержка) → Approach (заход) → Rollout → Taxi.
    ordered = [m for i, m in enumerate(modes) if i == 0 or m is not modes[i - 1]]
    assert ordered == [ControlModeState.Off, ControlModeState.Approach,
                       ControlModeState.Rollout, ControlModeState.Taxi]

    masks = {o.ControlMode: o.ControlValidMask for o in bench.sent_outputs}
    assert masks[ControlModeState.Approach] == int(AIRBORNE_CONTROL_MASK)
    assert masks[ControlModeState.Rollout] == int(ROLLOUT_CONTROL_MASK)


def test_the_airborne_handshake_is_actually_transmitted_before_approach():
    """Стенд включается по полученной готовности, а не по нашему представлению о ней."""
    bench = HandshakeBench(airborne_inputs(radio_altitude_ft=900.0, AgentIsActive=0),
                           target_mode=ControlModeState.Approach)
    sim = ICSSim(connector=bench)
    sim.read_telemetry()
    assert sim.engaged is False

    import ismpu.envs.ics_sim as ics_sim_module
    real_sleep = ics_sim_module.time.sleep
    try:
        ics_sim_module.time.sleep = lambda _s: None
        assert sim.warm_up(timeout_s=30.0) is True
    finally:
        ics_sim_module.time.sleep = real_sleep

    armed = [o for o in bench.sent_outputs
             if o.ControlMode is ControlModeState.Off and o.ModeAIReady == 1]
    assert len(armed) >= ENGAGE_MIN_READY_FRAMES     # выдержка действительно передана
    assert all(o.ControlValidMask == 0 for o in armed)   # до включения каналы не заявляются
    assert bench.sent_outputs[-1].ControlMode is ControlModeState.Approach
