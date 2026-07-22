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
    BRAKE_CMD_MAX_MM, THROTTLE_ANGLE_MIN_DEG, THROTTLE_ANGLE_MAX_DEG,
    THROTTLE_RATE_MAX_DEG_S, RUDDER_MAX_DEG, RUDDER_PEDAL_MAX_MM, TILLER_MAX_MM, FlightPhase,
)
from ismpu.io.ics_connector import ControlModeState as _Mode
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


def airborne_inputs(radio_altitude_ft=1000.0, **overrides) -> ICSInputs:
    """Кадр «ВС на глиссаде»: стойки не обжаты, ILS валиден, скорость и высота осмысленные.

    Все поля валидности выставлены явно: воздушный закон читает `LocDeviationValid`,
    `PitchAngleValid` и прочие, и кадр с нулями там вёл бы себя как «датчик молчит», а не как
    «на глиссаде».
    """
    base = dict(
        AgentIsActive=1,
        FlightPhaseValid=1, FlightPhase=int(FlightPhase.APPROACH_ABOVE_30M),
        LatitudeValid=1, Latitude=55.96715, LongitudeValid=1, Longitude=37.3865417,
        RadioAltitudeValid=1, RadioAltitude=radio_altitude_ft,
        BaroAltitudeValid=1, BaroAltitude=radio_altitude_ft + 630.0,
        IndicatedAirspeedValid=1, IndicatedAirspeed=140.0,
        TrueAirspeedValid=1, TrueAirspeed=145.0,
        GroundSpeedValid=1, GroundSpeed=140.0,
        VerticalSpeedValid=1, VerticalSpeed=-750.0,          # фут/мин
        PitchAngleValid=1, PitchAngle=2.5,
        RollAngleValid=1, RollAngle=0.0,
        MagneticHeadingValid=1, MagneticHeading=float(RWY_HEADING_TRUE),
        TrueHeadingValid=1, TrueHeading=float(RWY_HEADING_TRUE),
        BodyPitchRateValid=1, BodyPitchRate=0.0,
        BodyRollRateValid=1, BodyRollRate=0.0,
        BodyYawRateValid=1, BodyYawRate=0.0,
        BodyNormAccelValid=1, BodyNormAccel=0.0,
        RunwayHeadingValid=1, RunwayHeading=float(RWY_HEADING_TRUE),
        LocDeviationValid=1, LocDeviation=0.0,
        GSDeviationValid=1, GSDeviation=0.0,
        FlapsAngle=27.0,                                      # посадочная конфигурация FLAPS 3
        SlatsAngle=20.0,
        LeftThrottleAngle=20.0, RightThrottleAngle=20.0,
        AirfieldTemp=15.0,
        NoseGearWeightOnWheels=0, LeftGearWeightOnWheels=0, RightGearWeightOnWheels=0,
    )
    base.update(overrides)
    return make_ics_inputs(**base)


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
    """`ICSOutputs` → (brake_l, brake_r, thr_l_rate, thr_r_rate, steer), всё нормировано.

    Только наземные каналы; воздушные команды идут в единицах ICD и сравниваются напрямую
    (`decode_airborne`).

    Тяга декодируется как **скорость** перемещения РУД, а не как уровень реверса: абсолютного
    положения в перечне управляющих сигналов Заказчика нет, уровень задаётся именно скоростью, и
    восстанавливать его из пакета в отрыве от фактического угла было бы обратной подгонкой.
    Путевой орган берётся по режиму: на рулении это тиллер, иначе — руль направления.
    """
    steer = (outputs.NoseWheelTillerCmd / TILLER_MAX_MM
             if outputs.ControlMode is _Mode.Taxi
             else outputs.RudderCmd / RUDDER_MAX_DEG)
    return (
        outputs.BrakeLeftCmd / BRAKE_CMD_MAX_MM,
        outputs.BrakeRightCmd / BRAKE_CMD_MAX_MM,
        outputs.ThrottleLeftRate / THROTTLE_RATE_MAX_DEG_S,
        outputs.ThrottleRightRate / THROTTLE_RATE_MAX_DEG_S,
        steer,
    )


def _integrate_throttle(angle_deg: float, rate_deg_s: float) -> float:
    """Ход рычага РУД за такт: интеграл команды-скорости, зажатый физическим диапазоном."""
    rate = max(-THROTTLE_RATE_MAX_DEG_S, min(THROTTLE_RATE_MAX_DEG_S, rate_deg_s))
    return max(THROTTLE_ANGLE_MIN_DEG,
               min(THROTTLE_ANGLE_MAX_DEG, angle_deg + rate * DT))


def _reverse_fraction(angle_deg: float) -> float:
    """Доля обратной тяги по фактическому углу РУД: 0 в положительном секторе, 1 на упоре."""
    return max(0.0, -angle_deg) / abs(THROTTLE_ANGLE_MIN_DEG)


def decode_airborne(outputs) -> tuple:
    """`ICSOutputs` → (elevator_g, aileron_deg, thr_l_rate, thr_r_rate, thr_norm)."""
    return (
        outputs.ElevatorCmd,
        outputs.AileronCmd,
        outputs.ThrottleLeftRate,
        outputs.ThrottleRightRate,
        outputs.ThrottleLeft,
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

    Ждёт непрерывной готовности при `ControlMode = Off`, затем перехода в целевой режим (`0 → 4`
    для руления, `0 → 1` для захода). До этого `AgentIsActive = 0`, сколько бы кадров ни ушло, —
    так проверяется, что включает нас именно стенд по нашему стимулу, а не наша внутренняя
    выдержка.
    """

    def __init__(self, base_inputs=None, *, target_mode=ControlModeState.Taxi):
        super().__init__(base_inputs if base_inputs is not None else on_ground())
        self.target_mode = target_mode
        self._active = False
        self._saw_off_ready = False

    def send_outputs(self, outputs):
        self.sent_outputs.append(outputs)
        if outputs.ModeAIReady == 1 and outputs.ControlMode == ControlModeState.Off:
            self._saw_off_ready = True          # видели заявку готовности при ControlMode = 0
        if (self._saw_off_ready and outputs.ModeAIReady == 1
                and outputs.ControlMode == self.target_mode):
            self._active = True                 # фронт Off → режим после готовности → включаем
        return True                             # успешная отправка продвигает выдержку

    def receive_inputs(self, timeout=1.0):
        if self.inputs is None:
            return None
        return replace(self.inputs, AgentIsActive=1 if self._active else 0)


class ScriptedFlightBench(FakeConnector):
    """Стенд, проигрывающий заход и касание **по сценарию**, а не по нашим командам.

    Радиовысота убывает с постоянным темпом, на нуле обжимаются основные стойки и фаза
    переключается на пробег; дальше скорость гасится как у `KinematicBench`. Модель **не
    реагирует на управление** — и это осознанно: проверяется стыковка участков (рукопожатие,
    маски, момент передачи захода на пробег), а не аэродинамика. Изображать реакцию планера на
    руль высоты пришлось бы выдуманными коэффициентами, и тест начал бы проверять выдумку.
    """

    def __init__(self, radio_altitude_ft=1000.0, descent_fps=25.0, groundspeed_kts=140.0,
                 **input_overrides):
        super().__init__(None)
        self.tracker = RunwayTracker()
        self._overrides = input_overrides
        self.descent_fps = descent_fps
        self.ra_ft = float(radio_altitude_ft)
        self.speed_kts = float(groundspeed_kts)
        self.along_m = 0.0
        self.touched = False
        self.thr_l = self.thr_r = 20.0    # заход идёт с ненулевым РУД

    @property
    def airborne(self) -> bool:
        return not self.touched

    def receive_inputs(self, timeout=1.0):
        lat, lon = self.tracker.destination(
            RWY_START_LAT, RWY_START_LON, math.radians(RWY_HEADING_TRUE), self.along_m)
        if self.touched:
            return engaged_inputs(Latitude=lat, Longitude=lon,
                                  TrueHeading=float(RWY_HEADING_TRUE),
                                  GroundSpeed=self.speed_kts,
                                  RadioAltitudeValid=1, RadioAltitude=0.0,
                                  LeftThrottleAngle=self.thr_l, RightThrottleAngle=self.thr_r,
                                  **self._overrides)
        return airborne_inputs(radio_altitude_ft=self.ra_ft, Latitude=lat, Longitude=lon,
                               GroundSpeed=self.speed_kts, IndicatedAirspeed=self.speed_kts,
                               VerticalSpeed=-self.descent_fps * 60.0,
                               LeftThrottleAngle=self.thr_l, RightThrottleAngle=self.thr_r,
                               **self._overrides)

    def send_outputs(self, outputs):
        self.sent_outputs.append(outputs)
        self.thr_l = _integrate_throttle(self.thr_l, outputs.ThrottleLeftRate)
        self.thr_r = _integrate_throttle(self.thr_r, outputs.ThrottleRightRate)
        if self.touched:
            brake_l, brake_r, _rl, _rr, _rudder = decode_outputs(outputs)
            rev = 0.5 * (_reverse_fraction(self.thr_l) + _reverse_fraction(self.thr_r))
            decel_kts = (1.0 + 6.0 * 0.5 * (brake_l + brake_r) + 4.0 * rev) * 1.94384449244
            self.speed_kts = max(0.0, self.speed_kts - decel_kts * DT)
        else:
            self.ra_ft = max(0.0, self.ra_ft - self.descent_fps * DT)
            if self.ra_ft <= 0.0:
                self.touched = True
        self.along_m += self.speed_kts * 0.51444444444 * DT
        return True


def flight_sim(radio_altitude_ft=1000.0, **kwargs):
    """(sim, bench) на сценарном заходе. Рукопожатие ещё не выполнено."""
    bench = ScriptedFlightBench(radio_altitude_ft=radio_altitude_ft, **kwargs)
    sim = ICSSim(connector=bench)
    return sim, bench


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
        self.thr_l = self.thr_r = 0.0     # фактические углы РУД, град (0 = малый газ)

    def receive_inputs(self, timeout=1.0):
        brg = math.radians(RWY_HEADING_TRUE)
        lat, lon = self.tracker.destination(RWY_START_LAT, RWY_START_LON, brg, self.along)
        if self.xte:
            side = math.radians(RWY_HEADING_TRUE + (90.0 if self.xte > 0 else -90.0))
            lat, lon = self.tracker.destination(lat, lon, side, abs(self.xte))
        return engaged_inputs(Latitude=lat, Longitude=lon,
                              TrueHeading=float(RWY_HEADING_TRUE),
                              GroundSpeed=self.speed * 1.94384449244,   # м/с → узлы (ICD)
                              LeftThrottleAngle=self.thr_l,
                              RightThrottleAngle=self.thr_r,
                              **self._overrides)

    def send_outputs(self, outputs):
        """Замедление считается по **фактическому** углу РУД, а не по команде.

        Тягой командуют скоростью перемещения (см. `config/ics.py`), поэтому модель обязана
        держать положение рычага сама и отдавать его обратно телеметрией — иначе позиционный
        контур в `ICSSim` замкнётся сам на себя и реверс никогда не «доедет» до уставки.
        """
        self.sent_outputs.append(outputs)
        brake_l, brake_r, rate_l, rate_r, rudder = decode_outputs(outputs)
        self.thr_l = _integrate_throttle(self.thr_l, outputs.ThrottleLeftRate)
        self.thr_r = _integrate_throttle(self.thr_r, outputs.ThrottleRightRate)

        brake = 0.5 * (brake_l + brake_r)
        rev = 0.5 * (_reverse_fraction(self.thr_l) + _reverse_fraction(self.thr_r))
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
