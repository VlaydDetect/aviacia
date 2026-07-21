"""Автомат включения управления на стенде.

Главное, что проверяется: `ControlMode` — состояние, а не константа. Пока мы шлём одно и то же
значение каждый такт, перехода не происходит и стенд не включит управление никогда.

Часы инжектируются, поэтому выдержка 2 с проверяется мгновенно.
"""

import pytest

from ismpu.config.ics import ENGAGE_MAX_GROUNDSPEED_KTS, ENGAGE_READY_DWELL_S, FlightPhase
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
    """Признаки, удовлетворяющие наземным предусловиям включения."""
    base = dict(all_gear_on_ground=True, groundspeed_kts=0.5,
                flight_phase=None, telemetry_valid=True)
    base.update(overrides)
    return EngagementInputs(**base)


def _engine(clock=None):
    return IcsEngagement(clock=clock or _Clock())


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
# Наземное включение с нуля: 0 → 4
# --------------------------------------------------------------------------- #

def test_ground_engagement_requires_the_full_dwell():
    clock = _Clock()
    eng = _engine(clock)

    eng.step(_ready())
    assert eng.state is EngagementState.READY_DWELL
    assert eng.mode_ai_ready == 1          # держим готовность, пока идёт выдержка
    assert eng.engaged is False

    clock.advance(ENGAGE_READY_DWELL_S * 0.9)
    eng.step(_ready())
    assert eng.engaged is False            # выдержка ещё не набрана

    clock.advance(ENGAGE_READY_DWELL_S * 0.2)
    eng.step(_ready())
    assert eng.state is EngagementState.ENGAGED_TAXI
    assert eng.control_mode is ControlModeState.Taxi


def test_dwell_restarts_when_a_precondition_drops_midway():
    """Срыв предусловия обнуляет отсчёт, а не приостанавливает его."""
    clock = _Clock()
    eng = _engine(clock)

    eng.step(_ready())
    clock.advance(ENGAGE_READY_DWELL_S * 0.9)
    eng.step(_ready(all_gear_on_ground=False))    # срыв
    assert eng.state is EngagementState.IDLE
    assert eng.mode_ai_ready == 0

    eng.step(_ready())                            # предусловия вернулись
    clock.advance(ENGAGE_READY_DWELL_S * 0.9)     # 0.9 + 0.9 > 2с, но отсчёт начат заново
    eng.step(_ready())
    assert eng.engaged is False


def test_no_engagement_without_all_gear_compressed():
    clock = _Clock()
    eng = _engine(clock)
    for _ in range(5):
        clock.advance(ENGAGE_READY_DWELL_S)
        eng.step(_ready(all_gear_on_ground=False))
    assert eng.engaged is False
    assert eng.state is EngagementState.IDLE


def test_no_engagement_above_the_speed_threshold():
    clock = _Clock()
    eng = _engine(clock)
    for _ in range(5):
        clock.advance(ENGAGE_READY_DWELL_S)
        eng.step(_ready(groundspeed_kts=ENGAGE_MAX_GROUNDSPEED_KTS + 0.1))
    assert eng.engaged is False


def test_speed_threshold_is_interpreted_in_knots():
    """Порог задан в узлах. 1.5 узла — это включение; 1.5 м/с (≈2.9 узла) — нет.

    Пересчёт телеметрии в м/с перед этой проверкой дал бы ошибку в 1.94 раза и включал бы
    управление на скорости почти вдвое выше разрешённой.
    """
    clock = _Clock()
    eng = _engine(clock)
    eng.step(_ready(groundspeed_kts=1.5))
    clock.advance(ENGAGE_READY_DWELL_S)
    eng.step(_ready(groundspeed_kts=1.5))
    assert eng.engaged is True

    clock2 = _Clock()
    eng2 = _engine(clock2)
    eng2.step(_ready(groundspeed_kts=2.9))
    clock2.advance(ENGAGE_READY_DWELL_S)
    eng2.step(_ready(groundspeed_kts=2.9))
    assert eng2.engaged is False


def test_invalid_telemetry_does_not_accumulate_dwell():
    clock = _Clock()
    eng = _engine(clock)
    eng.step(_ready())
    clock.advance(ENGAGE_READY_DWELL_S * 0.9)
    eng.step(_ready(telemetry_valid=False))
    assert eng.state is EngagementState.IDLE
    clock.advance(ENGAGE_READY_DWELL_S)
    eng.step(_ready(telemetry_valid=False))
    assert eng.engaged is False


# --------------------------------------------------------------------------- #
# Подхват уже включённого пробега
# --------------------------------------------------------------------------- #

def test_adopts_rollout_from_the_flight_phase():
    """`ControlMode` нет во входной структуре, поэтому подхват опирается на фазу полёта."""
    eng = _engine()
    eng.step(_ready(all_gear_on_ground=True, groundspeed_kts=110.0,
                    flight_phase=int(FlightPhase.LAND_RUN)))
    assert eng.state is EngagementState.ENGAGED_ROLLOUT
    assert eng.control_mode is ControlModeState.Rollout
    assert eng.engaged is True
    assert eng.adopted is True


def test_other_flight_phases_do_not_trigger_adoption():
    eng = _engine()
    eng.step(_ready(groundspeed_kts=110.0, flight_phase=int(FlightPhase.APPROACH_ABOVE_30M)))
    assert eng.engaged is False


def test_explicit_rollout_entry_is_not_marked_adopted():
    eng = _engine()
    eng.request_rollout()
    assert eng.state is EngagementState.ENGAGED_ROLLOUT
    assert eng.engaged is True
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
    assert eng.state is EngagementState.ENGAGED_ROLLOUT
    assert eng.control_mode is ControlModeState.Rollout


def test_taxi_handover_needs_an_explicit_request():
    eng = _engine()
    eng.request_rollout()
    assert eng.request_taxi(_ready(groundspeed_kts=25.0)) is True
    assert eng.state is EngagementState.ENGAGED_TAXI
    assert eng.control_mode is ControlModeState.Taxi


def test_taxi_handover_is_refused_without_gear_on_ground():
    eng = _engine()
    eng.request_rollout()
    assert eng.request_taxi(_ready(all_gear_on_ground=False)) is False
    assert eng.state is EngagementState.ENGAGED_ROLLOUT


def test_taxi_handover_is_refused_when_not_in_rollout():
    eng = _engine()
    assert eng.request_taxi(_ready()) is False
    assert eng.state is EngagementState.IDLE


# --------------------------------------------------------------------------- #
# Сброс и диагностика
# --------------------------------------------------------------------------- #

def test_reset_returns_to_disengaged():
    eng = _engine()
    eng.request_rollout()
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
    assert snap["mode_ai_ready"] == 1
    assert snap["control_mode"] == int(ControlModeState.Off)
    assert snap["dwell_elapsed_s"] == pytest.approx(0.5)
