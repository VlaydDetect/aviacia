"""Фейковый стенд для тестов: `ICSInputs` вместо реального UDP.

Единственный источник телеметрии в проекте — стенд, поэтому и в тестах подменяется он, а не
транспорт. Три уровня «стендовости», по возрастанию:

* `FakeConnector` — статический кадр, всё отправленное складывается в `sent_outputs`;
* `HandshakeBench` — включает управление только после корректного рукопожатия (проверка того,
  что включает нас стенд по нашему стимулу, а не наша внутренняя выдержка);
* `KinematicBench` — мини-модель пробега: замедление по команде, ход вдоль осевой ВПП.
"""

import math
from dataclasses import fields, replace

from ismpu.config.constants import DT
from ismpu.config.ics import (
    BRAKE_PEDAL_MAX_MM, THROTTLE_ANGLE_MIN_DEG, RUDDER_MAX_DEG, FlightPhase,
)
from ismpu.config.runway import RWY_START_LAT, RWY_START_LON, RWY_HEADING_TRUE
from ismpu.control.runway_tracker import RunwayTracker
from ismpu.io.ics_connector import ICSInputs, ControlModeState
from ismpu.envs.ics_sim import ICSSim, Telemetry


def make_ics_inputs(**overrides) -> ICSInputs:
    """Полный пакет стенда: нули по умолчанию + заданные поля."""
    data = {f.name: 0 for f in fields(ICSInputs)}
    data.update(overrides)
    return ICSInputs.from_dict(data)


def on_ground(**overrides) -> ICSInputs:
    """Кадр «ВС на полосе»: обжаты все стойки, курс/координаты у порога UUEE 06R."""
    base = dict(Latitude=55.96715, Longitude=37.3865417, TrueHeading=75.079,
                NoseGearWeightOnWheels=1, LeftGearWeightOnWheels=1, RightGearWeightOnWheels=1)
    base.update(overrides)
    return make_ics_inputs(**base)


def engaged_inputs(**overrides) -> ICSInputs:
    """Кадр стенда, который уже принял управление: `AgentIsActive = 1`, идёт пробег."""
    base = dict(AgentIsActive=1, FlightPhaseValid=1, FlightPhase=int(FlightPhase.LAND_RUN))
    base.update(overrides)
    return on_ground(**base)


def telemetry(groundspeed_ms=50.0, *, lat=RWY_START_LAT, lon=RWY_START_LON,
              heading=float(RWY_HEADING_TRUE), **kwargs) -> Telemetry:
    """Готовый кадр `Telemetry` для прямых вызовов `control_step(dt, telemetry, send=False)`."""
    return Telemetry(lat=lat, lon=lon, groundspeed_ms=groundspeed_ms,
                     heading_true_deg=heading, **kwargs)


class FakeConnector:
    """Статический стенд: всегда один и тот же кадр, отправленное — в `sent_outputs`."""

    def __init__(self, inputs=None):
        self.inputs = inputs
        self.sent_outputs = []
        self.closed = False

    def receive_inputs(self, timeout=1.0):
        return self.inputs

    def send_outputs(self, outputs):
        self.sent_outputs.append(outputs)
        return True

    def close(self):
        self.closed = True

    # --- разбор отправленного (единицы ICD → нормированные команды контура) --- #

    def commands(self):
        """Отправленные команды в нормированном виде — для сравнения траекторий.

        Сравнивать сырые `ICSOutputs` неудобно: они в миллиметрах и градусах, а паритет
        проверяется по тому, что посчитал контур.
        """
        return [decode_outputs(o) for o in self.sent_outputs]


def decode_outputs(outputs) -> tuple:
    """`ICSOutputs` → (brake_l, brake_r, rev_l, rev_r, rudder) в нормированных единицах."""
    return (
        outputs.BrakeLeftCmd / BRAKE_PEDAL_MAX_MM,
        outputs.BrakeRightCmd / BRAKE_PEDAL_MAX_MM,
        -outputs.ThrottleLeft / THROTTLE_ANGLE_MIN_DEG,
        -outputs.ThrottleRight / THROTTLE_ANGLE_MIN_DEG,
        outputs.RudderCmd / RUDDER_MAX_DEG,
    )


def engaged_sim(**overrides):
    """(sim, connector) с завершённым рукопожатием: стенд подтвердил `AgentIsActive = 1`."""
    conn = FakeConnector(engaged_inputs(**overrides))
    sim = ICSSim(connector=conn)
    sim.read_telemetry()          # снимаем подтверждение стенда + подхват пробега
    assert sim.engaged
    return sim, conn


def static_sim(groundspeed_ms=50.0, *, lat=RWY_START_LAT, lon=RWY_START_LON, **overrides):
    """(sim, connector) с неизменным кадром у порога ВПП. Скорость задаётся в **м/с**.

    Стенд шлёт узлы, поэтому перевод делается здесь: тесты контура рассуждают в СИ, и указать
    «50» в узлах вместо м/с сместило бы всю траекторию почти вдвое.
    """
    return engaged_sim(Latitude=lat, Longitude=lon, TrueHeading=float(RWY_HEADING_TRUE),
                       GroundSpeed=groundspeed_ms * 1.94384449244, **overrides)


class HandshakeBench(FakeConnector):
    """Стенд, включающий управление только после корректного рукопожатия.

    Ждёт непрерывной готовности при `ControlMode = Off`, затем перехода `0 → 4`. До этого
    `AgentIsActive = 0`, сколько бы кадров ни ушло, — так проверяется, что включает нас именно
    стенд по нашему стимулу, а не наша внутренняя выдержка.
    """

    def __init__(self, base_inputs=None):
        super().__init__(base_inputs if base_inputs is not None else on_ground())
        self._active = False
        self._saw_off_ready = False

    def send_outputs(self, outputs):
        self.sent_outputs.append(outputs)
        if outputs.ModeAIReady == 1 and outputs.ControlMode == ControlModeState.Off:
            self._saw_off_ready = True          # видели заявку готовности при ControlMode = 0
        if (self._saw_off_ready and outputs.ModeAIReady == 1
                and outputs.ControlMode == ControlModeState.Taxi):
            self._active = True                 # переход 0 → 4 после готовности → включаем
        return True                             # успешная отправка продвигает выдержку

    def receive_inputs(self, timeout=1.0):
        if self.inputs is None:
            return None
        return replace(self.inputs, AgentIsActive=1 if self._active else 0)


class KinematicBench(FakeConnector):
    """Мини-модель стенда: замедление ~ команде тормоза/реверса, ход вдоль осевой ВПП.

    Интегрирование идёт на **отправке** команды, а не на приёме: среда читает телеметрию по
    нескольку раз за такт (кадр «до» для Shield, кадр «после» для reward), и интегрируй мы на
    приёме — один такт управления двигал бы модель дважды.
    """

    def __init__(self, speed=60.0, lateral=0.0, **input_overrides):
        super().__init__(None)
        self.tracker = RunwayTracker()
        self._overrides = input_overrides
        self.reset_state(speed, lateral)

    def reset_state(self, speed=60.0, lateral=0.0):
        self.speed, self.along, self.xte = float(speed), 0.0, float(lateral)

    def receive_inputs(self, timeout=1.0):
        brg = math.radians(RWY_HEADING_TRUE)
        lat, lon = self.tracker.destination(RWY_START_LAT, RWY_START_LON, brg, self.along)
        if self.xte:
            side = math.radians(RWY_HEADING_TRUE + (90.0 if self.xte > 0 else -90.0))
            lat, lon = self.tracker.destination(lat, lon, side, abs(self.xte))
        return engaged_inputs(Latitude=lat, Longitude=lon,
                              TrueHeading=float(RWY_HEADING_TRUE),
                              GroundSpeed=self.speed * 1.94384449244,   # м/с → узлы (ICD)
                              **self._overrides)

    def send_outputs(self, outputs):
        self.sent_outputs.append(outputs)
        brake_l, brake_r, rev_l, rev_r, rudder = decode_outputs(outputs)
        brake = 0.5 * (brake_l + brake_r)
        rev = -0.5 * (rev_l + rev_r)
        decel = 1.0 + 6.0 * brake + 4.0 * rev
        self.speed = max(0.0, self.speed - decel * DT)
        self.along += self.speed * DT
        self.xte += -rudder * 0.05
        return True


def kinematic_sim(speed=60.0, lateral=0.0, **input_overrides):
    """(sim, bench) на кинематической модели — стенд уже принял управление."""
    bench = KinematicBench(speed=speed, lateral=lateral, **input_overrides)
    sim = ICSSim(connector=bench)
    sim.read_telemetry()
    return sim, bench
