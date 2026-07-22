"""Автомат включения управления на стенде.

Два раздельных предмета проверки:

* **исходящий стимул** (`control_mode` / `mode_ai_ready` / состояние) — что мы шлём стенду, чтобы
  он включил управление. Здесь ключевое: `ControlMode` — состояние, а не константа; пока мы шлём
  одно и то же значение каждый такт, перехода нет и стенд не включится никогда;
* **факт включения** (`engaged`) — определяет **стенд** полем `AgentIsActive`, а не наша выдержка.
  Даже полностью выдержанные две секунды сами по себе включения не дают.

Часы инжектируются, поэтому выдержка 2 с проверяется мгновенно.
"""

import pytest

from ismpu.config.ics import (
    ENGAGE_MAX_GROUNDSPEED_KTS, ENGAGE_READY_DWELL_S, ENGAGE_MIN_READY_FRAMES, FlightPhase,
)
from ismpu.io.ics_connector import ControlModeState
from ismpu.io.ics_engagement import IcsEngagement, EngagementInputs, EngagementState


class _Clock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


def _ready(**overrides):
    """Признаки, удовлетворяющие наземным предусловиям стимула (стенд ещё не подтвердил)."""
    base = dict(all_gear_on_ground=True, groundspeed_kts=0.5,
                flight_phase=None, agent_is_active=0, telemetry_valid=True)
    base.update(overrides)
    return EngagementInputs(**base)


def _engine(clock=None):
    return IcsEngagement(clock=clock or _Clock())


TICK_S = 0.05                                        # 20 Гц, как в реальном цикле
TICKS_FOR_DWELL = int(ENGAGE_READY_DWELL_S / TICK_S)  # 40 тактов = 2.0 с
"""Сколько тактов нужно, чтобы выполнились ОБА условия выдержки. При 20 Гц связывающим оказывается
время (2.0 с = 40 тактов), а порог кадров (30 = 1.5 с) — запас на просадку частоты цикла."""


def _pump(eng, clock, inputs, ticks, *, dt=TICK_S, send=True):
    """Имитирует реальный цикл: опрос телеметрии → отправка кадра → шаг часов.

    Отправка обязательна: выдержка засчитывается по кадрам, которые действительно ушли на стенд,
    а не по прошедшему времени.
    """
    for _ in range(ticks):
        eng.step(inputs)
        if send:
            eng.on_frame_sent(eng.mode_ai_ready)
        clock.advance(dt)


# --------------------------------------------------------------------------- #
# Исходное состояние
# --------------------------------------------------------------------------- #

def test_starts_disengaged_and_sends_mode_off():
    eng = _engine()
    assert eng.state is EngagementState.IDLE
    assert eng.engaged is False
    assert eng.control_mode is ControlModeState.Off
    assert eng.mode_ai_ready == 0


# --------------------------------------------------------------------------- #
# Исходящий стимул наземного включения: 0 → 4
# --------------------------------------------------------------------------- #

def test_ground_stimulus_reaches_taxi_after_the_full_dwell():
    clock = _Clock()
    eng = _engine(clock)

    eng.step(_ready())
    assert eng.state is EngagementState.READY_DWELL
    assert eng.mode_ai_ready == 1                # держим готовность, пока идёт выдержка
    assert eng.control_mode is ControlModeState.Off   # ControlMode = Off во время выдержки
    assert eng.engaged is False                 # стенд ещё не подтвердил

    _pump(eng, clock, _ready(), ticks=TICKS_FOR_DWELL - 2)
    assert eng.state is EngagementState.READY_DWELL           # выдержка ещё не набрана
    assert eng.ready_frames_sent >= ENGAGE_MIN_READY_FRAMES   # кадров уже хватает, времени — нет

    # Запас в несколько тактов: ровно на границе накопление 0.05 в float даёт 1.9999999999982,
    # и это артефакт фейковых часов — в продакшене часы монотонные, а не сумма шагов.
    _pump(eng, clock, _ready(), ticks=5)
    assert eng.state is EngagementState.COMMAND_TAXI          # переход 0 → 4 в стимуле
    assert eng.control_mode is ControlModeState.Taxi
    assert eng.engaged is False               # но включение — только по подтверждению стенда


def test_elapsed_time_alone_does_not_advance_without_transmitted_frames():
    """По ICD стенд должен два секунды ПОЛУЧАТЬ ModeAIReady=1.

    Если считать одно лишь время между опросами, то два вызова с разрывом 3 с (таймаут приёма — 1 с,
    плюс пауза GC) продвинули бы стимул до 0→4, не отправив ни одного пакета: стенд отбрасывал бы
    всё подряд, а мы бы гнали переход режима в пустоту.
    """
    clock = _Clock()
    eng = _engine(clock)

    eng.step(_ready())
    clock.advance(3.0)                      # времени с запасом...
    eng.step(_ready())                      # ...но кадры не отправлялись

    assert eng.state is EngagementState.READY_DWELL   # стимул не дошёл до 0 → 4
    assert eng.ready_frames_sent == 0
    assert "кадров" in eng.blocking_reason(_ready())


def test_frames_alone_do_not_advance_without_the_elapsed_time():
    """Обратная защита: 30 кадров можно выпалить за 0.1 с — время тоже обязано пройти."""
    clock = _Clock()
    eng = _engine(clock)
    _pump(eng, clock, _ready(), ticks=ENGAGE_MIN_READY_FRAMES + 10, dt=0.001)

    assert eng.ready_frames_sent >= ENGAGE_MIN_READY_FRAMES
    assert eng.state is EngagementState.READY_DWELL   # прошло ~0.04 с из требуемых 2


def test_dwell_restarts_when_a_precondition_drops_midway():
    """Срыв предусловия обнуляет и время, и счётчик кадров."""
    clock = _Clock()
    eng = _engine(clock)

    _pump(eng, clock, _ready(), ticks=TICKS_FOR_DWELL - 5)
    assert eng.ready_frames_sent > 0

    eng.step(_ready(all_gear_on_ground=False))    # срыв
    assert eng.state is EngagementState.IDLE
    assert eng.mode_ai_ready == 0
    assert eng.ready_frames_sent == 0

    _pump(eng, clock, _ready(), ticks=TICKS_FOR_DWELL - 5)
    assert eng.state is not EngagementState.COMMAND_TAXI   # отсчёт начат заново, а не продолжен


def test_a_frame_without_ready_breaks_the_streak():
    """Требование ICD — непрерывность: пропуск готовности рвёт серию."""
    clock = _Clock()
    eng = _engine(clock)
    _pump(eng, clock, _ready(), ticks=10)
    assert eng.ready_frames_sent == 10

    eng.on_frame_sent(0)                    # ушёл кадр без ModeAIReady
    assert eng.ready_frames_sent == 0


def test_unsent_frames_do_not_count():
    """Неудачная отправка (сокет вернул False) выдержку не продвигает."""
    clock = _Clock()
    eng = _engine(clock)
    _pump(eng, clock, _ready(), ticks=TICKS_FOR_DWELL + 20, send=False)
    assert eng.ready_frames_sent == 0
    assert eng.state is EngagementState.READY_DWELL   # время идёт, но стимул не дошёл до 0 → 4


def test_no_stimulus_without_all_gear_compressed():
    clock = _Clock()
    eng = _engine(clock)
    _pump(eng, clock, _ready(all_gear_on_ground=False), ticks=TICKS_FOR_DWELL * 2)
    assert eng.state is EngagementState.IDLE


def test_no_stimulus_above_the_speed_threshold():
    clock = _Clock()
    eng = _engine(clock)
    _pump(eng, clock, _ready(groundspeed_kts=ENGAGE_MAX_GROUNDSPEED_KTS + 0.1),
          ticks=TICKS_FOR_DWELL * 2)
    assert eng.state is EngagementState.IDLE


def test_speed_threshold_is_interpreted_in_knots():
    """Порог задан в узлах. 1.5 узла — стимул идёт; 2.9 узла — нет.

    Пересчёт телеметрии в м/с перед этой проверкой дал бы ошибку в 1.94 раза и гнал бы стимул
    включения на скорости почти вдвое выше разрешённой.
    """
    clock = _Clock()
    eng = _engine(clock)
    _pump(eng, clock, _ready(groundspeed_kts=1.5), ticks=TICKS_FOR_DWELL + 5)
    assert eng.state is EngagementState.COMMAND_TAXI

    clock2 = _Clock()
    eng2 = _engine(clock2)
    _pump(eng2, clock2, _ready(groundspeed_kts=2.9), ticks=TICKS_FOR_DWELL + 5)
    assert eng2.state is EngagementState.IDLE


def test_invalid_telemetry_does_not_accumulate_dwell():
    clock = _Clock()
    eng = _engine(clock)
    _pump(eng, clock, _ready(), ticks=10)
    eng.step(_ready(telemetry_valid=False))
    assert eng.state is EngagementState.IDLE
    assert eng.ready_frames_sent == 0

    _pump(eng, clock, _ready(telemetry_valid=False), ticks=TICKS_FOR_DWELL * 2)
    assert eng.state is EngagementState.IDLE


# --------------------------------------------------------------------------- #
# Факт включения определяет стенд: AgentIsActive
# --------------------------------------------------------------------------- #

def test_engaged_follows_the_bench_confirmation():
    """Что бы мы ни слали, включены мы только когда стенд ответил AgentIsActive = 1."""
    eng = _engine()
    for _ in range(60):
        eng.step(_ready(groundspeed_kts=100.0, flight_phase=int(FlightPhase.LAND_RUN)))
    assert eng.state is EngagementState.COMMAND_ROLLOUT   # стимул идёт (подхват пробега)
    assert eng.engaged is False                            # но стенд не подтвердил

    eng.step(_ready(groundspeed_kts=100.0, flight_phase=int(FlightPhase.LAND_RUN),
                    agent_is_active=1))
    assert eng.engaged is True                             # стенд принял управление


def test_our_own_dwell_does_not_engage_without_the_bench():
    """Прямой тест главного дефекта: наша выдержка 2 с сама по себе включения не даёт."""
    clock = _Clock()
    eng = _engine(clock)
    _pump(eng, clock, _ready(), ticks=TICKS_FOR_DWELL + 10)   # полная выдержка, но AgentIsActive=0
    assert eng.state is EngagementState.COMMAND_TAXI          # стимул 0→4 отправлен
    assert eng.engaged is False                               # стенд не подтвердил — мы не включены


def test_confirmation_latches_through_a_dropped_packet():
    """Единичный потерянный пакет не должен «выключать» нас на такт."""
    eng = _engine()
    eng.step(_ready(agent_is_active=1))
    assert eng.engaged is True
    eng.step(_ready(agent_is_active=0, telemetry_valid=False))   # таймаут приёма
    assert eng.engaged is True


def test_confirmation_clears_when_the_bench_deactivates():
    """Валидный кадр с AgentIsActive = 0 — стенд снял активацию, значит и мы больше не включены."""
    eng = _engine()
    eng.step(_ready(agent_is_active=1))
    assert eng.engaged is True
    eng.step(_ready(agent_is_active=0))
    assert eng.engaged is False


# --------------------------------------------------------------------------- #
# Подхват уже включённого пробега
# --------------------------------------------------------------------------- #

def test_adopts_rollout_from_the_flight_phase():
    """`ControlMode` нет во входной структуре, поэтому подхват опирается на фазу полёта."""
    eng = _engine()
    eng.step(_ready(all_gear_on_ground=True, groundspeed_kts=110.0,
                    flight_phase=int(FlightPhase.LAND_RUN)))
    assert eng.state is EngagementState.COMMAND_ROLLOUT
    assert eng.control_mode is ControlModeState.Rollout
    assert eng.adopted is True
    assert eng.engaged is False        # подхват задаёт режим, но включение — по AgentIsActive


def test_other_flight_phases_do_not_trigger_adoption():
    eng = _engine()
    eng.step(_ready(groundspeed_kts=110.0, flight_phase=int(FlightPhase.APPROACH_ABOVE_30M)))
    assert eng.state is EngagementState.IDLE


def test_explicit_rollout_entry_is_not_marked_adopted():
    eng = _engine()
    eng.request_rollout()
    assert eng.state is EngagementState.COMMAND_ROLLOUT
    assert eng.control_mode is ControlModeState.Rollout
    assert eng.adopted is False           # режим установили мы, а не внешний модуль


# --------------------------------------------------------------------------- #
# Передача пробег → руление: 3 → 4
# --------------------------------------------------------------------------- #

def test_rollout_does_not_collapse_into_taxi_on_its_own():
    """Обжатие стоек на пробеге истинно всегда — если переходить по нему, пробег был бы пропущен.

    Это разрешающее условие, а не триггер.
    """
    eng = _engine()
    eng.request_rollout()
    for _ in range(50):
        eng.step(_ready(groundspeed_kts=100.0))
    assert eng.state is EngagementState.COMMAND_ROLLOUT
    assert eng.control_mode is ControlModeState.Rollout


def test_taxi_handover_needs_an_explicit_request():
    eng = _engine()
    eng.request_rollout()
    assert eng.request_taxi(_ready(groundspeed_kts=25.0)) is True
    assert eng.state is EngagementState.COMMAND_TAXI
    assert eng.control_mode is ControlModeState.Taxi


def test_taxi_handover_is_idempotent_once_in_taxi():
    eng = _engine()
    eng.request_rollout()
    eng.request_taxi(_ready(groundspeed_kts=25.0))
    assert eng.request_taxi(_ready(groundspeed_kts=10.0)) is True   # уже руление — не ошибка
    assert eng.state is EngagementState.COMMAND_TAXI


def test_taxi_handover_is_refused_without_gear_on_ground():
    eng = _engine()
    eng.request_rollout()
    assert eng.request_taxi(_ready(all_gear_on_ground=False)) is False
    assert eng.state is EngagementState.COMMAND_ROLLOUT


def test_taxi_handover_is_refused_when_not_commanding_rollout():
    eng = _engine()
    assert eng.request_taxi(_ready()) is False
    assert eng.state is EngagementState.IDLE


# --------------------------------------------------------------------------- #
# Сброс и диагностика
# --------------------------------------------------------------------------- #

def test_reset_returns_to_disengaged():
    eng = _engine()
    eng.request_rollout()
    eng.step(_ready(agent_is_active=1))
    assert eng.engaged is True
    eng.reset()
    assert eng.state is EngagementState.IDLE
    assert eng.engaged is False
    assert eng.adopted is False


def test_snapshot_exposes_the_handshake_for_reports():
    clock = _Clock()
    eng = _engine(clock)
    eng.step(_ready())
    clock.advance(0.5)
    snap = eng.as_dict()
    assert snap["state"] == "ready_dwell"
    assert snap["engaged"] is False
    assert snap["confirmed"] is False
    assert snap["mode_ai_ready"] == 1
    assert snap["control_mode"] == int(ControlModeState.Off)
    assert snap["dwell_elapsed_s"] == pytest.approx(0.5)
