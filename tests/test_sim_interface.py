"""Тесты SimInterface, бэкендов и генератора сценариев (без реального симулятора)."""

import math
from dataclasses import fields

import pytest

from ismpu.control.channels import ControlsState
from ismpu.control.failures import FailureMode
from ismpu.control.system import ControllingSystem
from ismpu.envs.sim_interface import XPlaneBackend, ICSBackend, Telemetry
from ismpu.io.ics_connector import ControlModeState, ReverseEngineType
from ismpu.config.ics import (
    FlightPhase, ControlValid, ROLLOUT_CONTROL_MASK,
    BRAKE_PEDAL_MAX_MM, THROTTLE_ANGLE_MIN_DEG, TILLER_MAX_DEG, RUDDER_MAX_DEG,
)
from ismpu.envs.scenario import Scenario, TouchdownSetup, SensorNoise, SCENARIO_PRESETS
from ismpu.envs.scenario_generator import ScenarioGenerator
from ismpu.config.scenarios import SCENARIOS, DEFAULT, NWS_FAIL
from ismpu.envs.weather import WeatherState, RunwayCondition, FrictionProfile, WEATHER_PRESETS
from ismpu.io.datarefs import (
    LATITUDE, LONGITUDE, GROUNDSPEED, TRUE_PSI, G_AXIL,
    FAIL_ENGINE, FAIL_REVERSER, FAILURE_ENUM_INOP, FAILURE_ENUM_OK,
    LEFT_BRAKE_RATIO, YOKE_HEADING_RATIO,
)


class FakeXPC:
    """Мок XPlaneConnectX: пишет всё в списки, subscribe эмулирует получение значений."""

    def __init__(self):
        self.sent = []
        self.ctrl = []
        self.posi = []
        self.paused = []
        self.current_dref_values = {}

    def sendDREF(self, dref, value):
        self.sent.append((dref, value))

    def sendCTRL(self, **kw):
        self.ctrl.append(kw)

    def sendPOSI(self, **kw):
        self.posi.append(kw)

    def sendCMND(self, cmd):
        self.sent.append((cmd, None))

    def pauseSIM(self, flag):
        self.paused.append(flag)

    def fix_all_systems(self):
        self.sendCMND("sim/operation/fix_all_systems")

    def subscribeDREFs(self, subs, timeout=5.0):
        for dref, _freq in subs:
            self.current_dref_values.setdefault(dref, {"value": 0.0})

    def getDREF(self, dref):
        return 0.0

    def last(self, dref):
        for d, v in reversed(self.sent):
            if d == dref:
                return v
        raise KeyError(dref)


# --------------------------------------------------------------------------- #
# XPlaneBackend
# --------------------------------------------------------------------------- #

def test_xplane_reset_sequence_and_failure_injection():
    fake = FakeXPC()
    be = XPlaneBackend(xpc=fake, settle_s=0.0, reload_each_reset=False)  # мок: без reload
    scenario = Scenario(
        scenario_id="t", seed=1, control=SCENARIOS["default"],
        weather=WeatherState(runway_friction=RunwayCondition.WET.value),
        failures=(FailureMode.ENGINE_OUT_LEFT,),
        touchdown=TouchdownSetup(lateral_offset_m=3.0, heading_offset_deg=2.0),
    )
    telem = be.reset(scenario)

    assert fake.paused == [True, False]        # пауза на конфигурацию, затем снятие
    assert fake.posi, "должен быть телепорт (sendPOSI)"
    assert fake.ctrl, "должна быть конфигурация органов (sendCTRL)"
    assert fake.last(f"{FAIL_ENGINE}0") == pytest.approx(FAILURE_ENUM_INOP)  # левый двигатель отказал
    assert FailureMode.ENGINE_OUT_LEFT in be.active_failures
    assert telem.valid


def test_xplane_nws_failure_has_no_sim_dataref_but_is_tracked():
    fake = FakeXPC()
    be = XPlaneBackend(xpc=fake, settle_s=0.0)
    be.inject_failure(FailureMode.NWS_FAIL)
    assert FailureMode.NWS_FAIL in be.active_failures
    # У NWS нет failure-датарефа → в sent не должно быть failure-строк
    assert not any(str(d).startswith("sim/operation/failures") for d, _ in fake.sent)


def test_xplane_clear_failures_resets_injected_drefs():
    fake = FakeXPC()
    be = XPlaneBackend(xpc=fake, settle_s=0.0)
    be.inject_failure(FailureMode.REVERSE_RIGHT_FAIL)
    assert fake.last(f"{FAIL_REVERSER}1") == pytest.approx(FAILURE_ENUM_INOP)
    be.clear_failures()
    assert fake.last(f"{FAIL_REVERSER}1") == pytest.approx(FAILURE_ENUM_OK)
    assert be.active_failures == set()


def test_xplane_read_telemetry_maps_drefs():
    fake = FakeXPC()
    fake.current_dref_values = {
        LATITUDE: {"value": 55.97}, LONGITUDE: {"value": 37.39},
        GROUNDSPEED: {"value": 50.0}, TRUE_PSI: {"value": 75.0},
        G_AXIL: {"value": -0.3},
    }
    be = XPlaneBackend(xpc=fake, settle_s=0.0)
    telem = be.read_telemetry()
    assert telem.lat == pytest.approx(55.97)
    assert telem.groundspeed_ms == pytest.approx(50.0)
    assert telem.heading_true_deg == pytest.approx(75.0)
    assert telem.accel_long_g == pytest.approx(-0.3)
    assert telem.valid


def test_xplane_read_telemetry_invalid_when_missing():
    be = XPlaneBackend(xpc=FakeXPC(), settle_s=0.0)
    telem = be.read_telemetry()  # ничего не подписано → значения None
    assert telem.valid is False


def test_xplane_step_sends_control_commands():
    fake = FakeXPC()
    be = XPlaneBackend(xpc=fake, settle_s=0.0)
    cmd = ControlsState()
    cmd.cmd_brake_l = 0.5
    cmd.rudder_cmd = -0.2
    be.step(cmd)
    assert fake.last(LEFT_BRAKE_RATIO) == pytest.approx(0.5)
    assert fake.last(YOKE_HEADING_RATIO) == pytest.approx(-0.2)


def test_xplane_update_forwards_variable_friction():
    fake = FakeXPC()
    be = XPlaneBackend(xpc=fake, settle_s=0.0)
    be.apply_weather(WeatherState(friction_profile=FrictionProfile([(0.0, 0.0), (600.0, 11.0)])))
    n_before = sum(1 for d, _ in fake.sent if d == "sim/weather/region/runway_friction")
    be.update(700.0)  # перешли на лёд → одна дозапись сцепления
    n_after = sum(1 for d, _ in fake.sent if d == "sim/weather/region/runway_friction")
    assert n_after == n_before + 1


# --------------------------------------------------------------------------- #
# Перезагрузка планера между эпизодами + детектор готовности
# --------------------------------------------------------------------------- #

from ismpu.io.datarefs import TOTAL_FLIGHT_TIME

RELOAD_CMD = "sim/operation/reload_aircraft_no_art"


class _AdvancingFlightTime:
    """Запись current_dref_values, где каждое чтение ['value'] растёт — физика идёт."""

    def __init__(self, start=0.0, step=0.1):
        self._t, self._step = start, step

    def __getitem__(self, key):
        if key == "value":
            self._t += self._step
            return self._t
        raise KeyError(key)


class ReloadFakeXPC(FakeXPC):
    """Мок с reload_aircraft и телеметрией (flight_time растёт → готовность детектируется)."""

    def __init__(self, flight_time_entry=None):
        super().__init__()
        self._flight_entry = flight_time_entry if flight_time_entry is not None else _AdvancingFlightTime()

    def reload_aircraft(self):
        self.sendCMND(RELOAD_CMD)

    def subscribeDREFs(self, subs, timeout=5.0):
        self.current_dref_values[TOTAL_FLIGHT_TIME] = self._flight_entry
        self.current_dref_values[LATITUDE] = {"value": 55.97}
        self.current_dref_values[LONGITUDE] = {"value": 37.39}
        self.current_dref_values[GROUNDSPEED] = {"value": 70.0}
        self.current_dref_values[TRUE_PSI] = {"value": 63.0}


def test_reload_each_reset_reloads_and_waits_ready():
    fake = ReloadFakeXPC()
    be = XPlaneBackend(xpc=fake, settle_s=0.0, reload_each_reset=True, ready_timeout=5.0)
    scenario = SCENARIO_PRESETS["nws_fail"]

    telem = be.reset(scenario)

    assert (RELOAD_CMD, None) in fake.sent          # планер перезагружен перед эпизодом
    assert fake.posi, "после готовности выполнен телепорт (sendPOSI)"
    assert False in fake.paused and True in fake.paused
    assert telem.valid


def test_wait_until_ready_times_out_gracefully(caplog):
    import logging
    # flight_time не растёт (константа) → детектор упирается в таймаут, но НЕ виснет.
    frozen = {"value": 5.0}
    fake = ReloadFakeXPC(flight_time_entry=frozen)
    be = XPlaneBackend(xpc=fake, settle_s=0.0, reload_each_reset=True, ready_timeout=0.3)

    with caplog.at_level(logging.WARNING):
        telem = be.reset(SCENARIO_PRESETS["default"])

    assert telem.valid                               # reset завершился, а не завис
    assert any("readiness timeout" in r.message for r in caplog.records)


# --------------------------------------------------------------------------- #
# ICSBackend
# --------------------------------------------------------------------------- #

def _make_ics_inputs(**overrides):
    from ismpu.io.ics_connector import ICSInputs
    data = {f.name: 0 for f in fields(ICSInputs)}
    data.update(overrides)
    return ICSInputs.from_dict(data)


class FakeConnector:
    def __init__(self, inputs=None):
        self.inputs = inputs
        self.sent_outputs = []
        self.closed = False

    def receive_inputs(self, timeout=1.0):
        return self.inputs

    def send_outputs(self, outputs):
        self.sent_outputs.append(outputs)

    def close(self):
        self.closed = True


def test_ics_read_telemetry_converts_icd_units_to_si():
    """Стенд отдаёт узлы, футы, футы/мин и градусы/с — граница пересчёта проходит здесь.

    Пропущенный перевод путевой скорости давал бы ошибку в 1.94 раза, и продольный канал
    прочитал бы 140 узлов как 272, немедленно дав полное торможение.
    """
    from ismpu.utils.converts import Converts

    inp = _make_ics_inputs(Latitude=55.9, Longitude=37.4, TrueHeading=75.0,
                           GroundSpeed=140.0,          # узлы
                           IndicatedAirspeed=145.0,    # узлы
                           WindSpeed=8.0,              # узлы
                           RadioAltitude=100.0,        # футы
                           BaroAltitude=600.0,         # футы
                           VerticalSpeed=-120.0,       # футы/мин
                           BodyYawRate=6.0,            # градусы/с
                           BodyLongAccel=-0.25)
    telem = ICSBackend(connector=FakeConnector(inp)).read_telemetry()

    assert telem.lat == pytest.approx(55.9)
    assert telem.groundspeed_ms == pytest.approx(140.0 * Converts.KTS_TO_MS)   # ≈72 м/с
    assert telem.groundspeed_ms < 100.0                 # узлы не просочились в поле м/с
    assert telem.ias_ms == pytest.approx(145.0 * Converts.KTS_TO_MS)
    assert telem.wind_speed_ms == pytest.approx(8.0 * Converts.KTS_TO_MS)
    assert telem.agl_m == pytest.approx(100.0 * Converts.FT_TO_M)              # ≈30.5 м
    assert telem.elevation_m == pytest.approx(600.0 * Converts.FT_TO_M)
    assert telem.vy_ms == pytest.approx(-120.0 * Converts.FTM_TO_MS)
    assert telem.r_rad == pytest.approx(math.radians(6.0))                     # ≈0.105 рад/с
    assert telem.accel_long_g == pytest.approx(-0.25)   # g остаётся g
    assert telem.valid


def test_ics_read_telemetry_maps_bench_only_signals():
    inp = _make_ics_inputs(
        FlightPhaseValid=1, FlightPhase=int(FlightPhase.LAND_RUN),
        RunwayHeadingValid=1, RunwayHeading=75.08, RunwayLength=3700.0, RunwayWidth=60.0,
        LateralDeviation=1.4, RunwayCondition=2,                # 2 = ICE по шкале стенда
        NoseGearWeightOnWheels=1, LeftGearWeightOnWheels=1, RightGearWeightOnWheels=1,
        FaultNWS=1, FaultLeftEngineReverse=1)
    telem = ICSBackend(connector=FakeConnector(inp)).read_telemetry()

    assert telem.runway_heading_deg == pytest.approx(75.08)
    assert telem.runway_length_m == pytest.approx(3700.0)
    assert telem.lateral_deviation_m == pytest.approx(1.4)
    assert telem.weight_on_wheels is True
    assert telem.flight_phase == int(FlightPhase.LAND_RUN)
    assert telem.faults == frozenset({FailureMode.NWS_FAIL, FailureMode.REVERSE_LEFT_FAIL})
    assert telem.runway_condition == pytest.approx(RunwayCondition.ICY.value)


def test_ics_weight_on_wheels_requires_all_three_gear():
    inp = _make_ics_inputs(NoseGearWeightOnWheels=1, LeftGearWeightOnWheels=1,
                           RightGearWeightOnWheels=0)
    assert ICSBackend(connector=FakeConnector(inp)).read_telemetry().weight_on_wheels is False


def test_ics_unknown_runway_condition_is_treated_as_slippery():
    """Неизвестный код — не повод предполагать сухую полосу."""
    inp = _make_ics_inputs(RunwayCondition=99)
    telem = ICSBackend(connector=FakeConnector(inp)).read_telemetry()
    assert telem.runway_condition == pytest.approx(RunwayCondition.ICY.value)


def test_ics_read_telemetry_invalid_on_timeout():
    be = ICSBackend(connector=FakeConnector(None))
    assert be.read_telemetry().valid is False


# --------------------------------------------------------------------------- #
# Команды: единицы ICD и рукопожатие
# --------------------------------------------------------------------------- #

def _engaged_backend(**input_overrides):
    """Бэкенд с завершённым рукопожатием (подхват пробега по фазе полёта)."""
    inp = _make_ics_inputs(FlightPhaseValid=1, FlightPhase=int(FlightPhase.LAND_RUN),
                           NoseGearWeightOnWheels=1, LeftGearWeightOnWheels=1,
                           RightGearWeightOnWheels=1, **input_overrides)
    conn = FakeConnector(inp)
    be = ICSBackend(connector=conn)
    be.read_telemetry()          # автомат подхватывает пробег
    assert be.engaged
    return be, conn


def test_ics_commands_are_withheld_until_engaged():
    """До рукопожатия заявлять каналы нельзя: стенд ещё не разрешил нам ими управлять."""
    conn = FakeConnector(_make_ics_inputs(GroundSpeed=30.0))
    be = ICSBackend(connector=conn)
    cmd = ControlsState()
    cmd.cmd_brake_l = 1.0
    be.step(cmd)

    out = conn.sent_outputs[-1]
    assert be.engaged is False
    assert out.ControlValidMask == 0
    assert out.ControlMode == ControlModeState.Off
    assert out.BrakeLeftCmd == 0.0        # команда не выдана, а не «выдана нулём случайно»


def test_ics_step_converts_commands_to_icd_units():
    be, conn = _engaged_backend()
    cmd = ControlsState()
    cmd.cmd_brake_l, cmd.cmd_brake_r = 1.0, 0.5
    cmd.rudder_cmd = 1.0
    cmd.cmd_rev_l, cmd.cmd_rev_r = -1.0, 0.0
    be.step(cmd)
    out = conn.sent_outputs[-1]

    assert out.ControlMode == ControlModeState.Rollout
    assert out.ControlValidMask == int(ROLLOUT_CONTROL_MASK)
    assert out.ControlValidMask != 0

    # Тормоза — ход педали в мм, а не нормированные [0, 1].
    assert out.BrakeLeftCmd == pytest.approx(BRAKE_PEDAL_MAX_MM)
    assert out.BrakeRightCmd == pytest.approx(BRAKE_PEDAL_MAX_MM * 0.5)

    # Путевое управление — в градусах, и передняя стойка задействована.
    assert out.RudderCmd == pytest.approx(RUDDER_MAX_DEG)
    assert out.NoseWheelTillerCmd == pytest.approx(TILLER_MAX_DEG)

    # Реверс: величина — отрицательным углом РУД, створки — отдельным сигналом.
    assert out.ThrottleLeft == pytest.approx(THROTTLE_ANGLE_MIN_DEG)
    assert out.ThrottleRight == pytest.approx(0.0)
    assert out.ReverseLeftCmd == ReverseEngineType.Deploy
    assert out.ReverseRightCmd == ReverseEngineType.Off


def test_ics_declared_mask_covers_only_channels_we_actually_drive():
    """Заявить канал, который не формируешь, — взять ответственность за неуправляемый орган."""
    assert ControlValid.RUDDER in ROLLOUT_CONTROL_MASK
    assert ControlValid.WHEEL_BRAKES in ROLLOUT_CONTROL_MASK
    assert ControlValid.NOSE_WHEEL_TILLER in ROLLOUT_CONTROL_MASK
    assert ControlValid.REVERSE in ROLLOUT_CONTROL_MASK
    assert ControlValid.ELEVATOR not in ROLLOUT_CONTROL_MASK   # продольные органы не наши
    assert ControlValid.AILERON not in ROLLOUT_CONTROL_MASK
    assert ControlValid.AIRBRAKE not in ROLLOUT_CONTROL_MASK


def test_ics_active_failures_come_from_telemetry_not_injection():
    be, _ = _engaged_backend(FaultNWS=1)
    assert FailureMode.NWS_FAIL in be.active_failures
    be.inject_failure(FailureMode.ENGINE_OUT_LEFT)      # на стенде это no-op
    assert FailureMode.ENGINE_OUT_LEFT not in be.active_failures


# --------------------------------------------------------------------------- #
# Контур работает против стенда: то, ради чего делалась развязка от xpc
# --------------------------------------------------------------------------- #

def test_controller_runs_the_plain_loop_against_the_bench():
    """Базовый контур на стенде — то, ради чего делалась развязка.

    Раньше это было невозможно дважды: каналы индексировали `xpc.current_dref_values`
    (`AttributeError` на первом такте), а `ControlsState.send_commands` писал DataRef'ы X-Plane.
    Теперь единственная зависимость — `SimInterface`, и цикл выглядит одинаково для обоих
    бэкендов: `control_step` сам читает телеметрию и сам отправляет команды.
    """
    from ismpu.config.constants import DT
    from ismpu.envs.scenario import SCENARIO_PRESETS

    be, conn = _engaged_backend(Latitude=55.96715, Longitude=37.3865417,
                                TrueHeading=75.079, GroundSpeed=100.0)
    controller = ControllingSystem(be)             # единственная зависимость — SimInterface
    assert not hasattr(controller, "xpc")
    SCENARIO_PRESETS["default"].apply_control(controller)

    for _ in range(5):
        assert controller.control_step(DT) is False   # ни телеметрии, ни отправки вручную

    out = conn.sent_outputs[-1]
    assert len(conn.sent_outputs) == 5
    assert out.ControlValidMask != 0
    assert out.ControlMode == ControlModeState.Rollout
    assert out.BrakeLeftCmd >= 0.0                  # команды дошли до структуры стенда


def test_plain_loop_reads_telemetry_once_per_tick():
    """На стенде каждый лишний `read_telemetry` — лишний приём UDP.

    Кадр, вернувшийся из `sim.step`, уже свежий, поэтому отдельное чтение делается только на
    первом такте.
    """
    from ismpu.config.constants import DT
    from ismpu.envs.scenario import SCENARIO_PRESETS

    be, conn = _engaged_backend(Latitude=55.96715, Longitude=37.3865417,
                                TrueHeading=75.079, GroundSpeed=100.0)
    reads = {"n": 0}
    original = be.read_telemetry

    def counting_read():
        reads["n"] += 1
        return original()

    be.read_telemetry = counting_read
    controller = ControllingSystem(be)
    SCENARIO_PRESETS["default"].apply_control(controller)

    ticks = 4
    for _ in range(ticks):
        controller.control_step(DT)

    assert len(conn.sent_outputs) == ticks
    # По одному чтению на такт (внутри `sim.step`) плюс одно холодное на первом такте.
    # Наивная реализация читала бы дважды за такт — вдвое больше приёмов UDP.
    assert reads["n"] == ticks + 1
    assert reads["n"] < 2 * ticks


def test_control_exception_sends_a_neutral_command_not_silence():
    """Замолчать нельзя: последнее отклонение осталось бы приложенным до сторожа на той стороне."""
    from ismpu.config.constants import DT
    from ismpu.envs.scenario import SCENARIO_PRESETS

    be, conn = _engaged_backend(GroundSpeed=100.0)
    controller = ControllingSystem(be)
    SCENARIO_PRESETS["default"].apply_control(controller)
    controller.control_step(DT)

    sent_before = len(conn.sent_outputs)
    controller.control_exception()

    assert len(conn.sent_outputs) == sent_before + 1     # нейтральная команда отправлена
    out = conn.sent_outputs[-1]
    assert out.BrakeLeftCmd == 0.0 and out.BrakeRightCmd == 0.0
    assert out.RudderCmd == 0.0 and out.NoseWheelTillerCmd == 0.0
    assert controller.state.break_control is True


def test_lateral_channel_uses_runway_geometry_from_telemetry():
    """Иначе поставленная система на любой ВПП поедет по осевой Шереметьево из конфига."""
    from ismpu.config.constants import DT
    from ismpu.config.runway import RWY_HEADING_TRUE
    from ismpu.envs.scenario import SCENARIO_PRESETS

    def rudder_for(runway_heading, lateral_deviation):
        controller = ControllingSystem()
        SCENARIO_PRESETS["default"].apply_control(controller)
        telem = Telemetry(lat=55.96715, lon=37.3865417, groundspeed_ms=50.0,
                          heading_true_deg=runway_heading,   # ВС точно по курсу ВПП
                          runway_heading_deg=runway_heading,
                          lateral_deviation_m=lateral_deviation)
        controller.control_step(DT, telem, send=False)
        return controller.state.rudder_cmd

    # ВПП с курсом, не имеющим ничего общего с UUEE 06R: смещение вправо парируется влево.
    assert rudder_for(200.0, +3.0) < 0.0
    assert rudder_for(200.0, -3.0) > 0.0
    assert rudder_for(200.0, 0.0) == pytest.approx(0.0, abs=1e-9)

    # Значение отклонения берётся из телеметрии, а не пересчитывается по конфигу.
    assert rudder_for(200.0, +5.0) < rudder_for(200.0, +1.0)


def test_geodetic_path_is_kept_when_the_backend_gives_no_runway_geometry():
    """X-Plane этих полей не даёт — прежний путь обязан остаться нетронутым."""
    from ismpu.config.constants import DT
    from ismpu.config.runway import RWY_START_LAT, RWY_START_LON, RWY_HEADING_TRUE
    from ismpu.envs.scenario import SCENARIO_PRESETS

    controller = ControllingSystem()
    SCENARIO_PRESETS["default"].apply_control(controller)
    telem = Telemetry(lat=RWY_START_LAT, lon=RWY_START_LON, groundspeed_ms=50.0,
                      heading_true_deg=float(RWY_HEADING_TRUE))
    assert telem.runway_heading_deg is None and telem.lateral_deviation_m is None
    controller.control_step(DT, telem, send=False)   # геодезический путь, без исключений


def test_controller_without_a_backend_fails_loudly():
    """Без `SimInterface` контур не может ни прочитать, ни отправить — молчать об этом нельзя."""
    from ismpu.config.constants import DT
    from ismpu.envs.scenario import SCENARIO_PRESETS

    controller = ControllingSystem()
    SCENARIO_PRESETS["default"].apply_control(controller)
    telemetry = Telemetry(lat=55.96715, lon=37.3865417, groundspeed_ms=50.0,
                          heading_true_deg=75.079)
    with pytest.raises(RuntimeError, match="SimInterface"):
        controller.control_step(DT, telemetry, send=True)

    # ...но чистый расчёт без отправки работает и без бэкенда — это путь RL-среды.
    assert controller.control_step(DT, telemetry, send=False) is False


def test_ics_environment_methods_are_noop():
    conn = FakeConnector(_make_ics_inputs())
    be = ICSBackend(connector=conn)
    be.apply_weather(WEATHER_PRESETS["icy"])
    be.inject_failure(FailureMode.NWS_FAIL)
    be.teleport_touchdown(TouchdownSetup())
    be.pause(True)
    assert conn.sent_outputs == []  # стенд владеет средой — ничего не отправили


# --------------------------------------------------------------------------- #
# Scenario сериализация
# --------------------------------------------------------------------------- #

def test_scenario_roundtrip_with_profile_and_failures():
    scenario = Scenario(
        scenario_id="s1", seed=7, control=SCENARIOS["nws_fail"],
        weather=WeatherState.from_crosswind(
            15.0, 5.0, gust_kts=8.0,
            friction_profile=FrictionProfile([(0.0, 0.0), (600.0, 11.0)]),
        ),
        failures=(FailureMode.NWS_FAIL, FailureMode.REVERSE_LEFT_FAIL),
        touchdown=TouchdownSetup(lateral_offset_m=2.0, heading_offset_deg=1.5),
        sensor_noise=SensorNoise(pos_sigma_m=0.3),
    )
    restored = Scenario.from_dict(scenario.to_dict())
    assert restored.to_dict() == scenario.to_dict()
    assert restored.failures == scenario.failures
    assert restored.weather.friction_profile.at(700.0) == pytest.approx(11.0)


# --------------------------------------------------------------------------- #
# ScenarioGenerator
# --------------------------------------------------------------------------- #

def test_generator_is_deterministic_for_same_seed():
    g1, g2 = ScenarioGenerator(seed=42), ScenarioGenerator(seed=42)
    a = [g1.sample().to_dict() for _ in range(5)]
    b = [g2.sample().to_dict() for _ in range(5)]
    assert a == b


def test_generator_zero_difficulty_has_no_failures():
    gen = ScenarioGenerator(seed=1)
    for _ in range(5):
        assert gen.sample(difficulty=0.0).failures == ()


def test_generator_high_difficulty_produces_failures():
    gen = ScenarioGenerator(seed=1)
    any_failure = any(gen.sample(difficulty=1.0).failures for _ in range(15))
    assert any_failure


def test_generator_samples_are_valid_and_serializable():
    gen = ScenarioGenerator(seed=3)
    for _ in range(10):
        s = gen.sample()
        assert 300.0 <= s.weather.visibility_m <= 16000.0
        assert Scenario.from_dict(s.to_dict()).to_dict() == s.to_dict()


def test_battery_covers_key_cases_and_roundtrips():
    battery = ScenarioGenerator(seed=0).battery()
    ids = {s.scenario_id for s in battery}
    assert {"nominal", "nws_fail", "icy", "crosswind"} <= ids
    for s in battery:
        assert Scenario.from_dict(s.to_dict()).to_dict() == s.to_dict()


def test_generator_embeds_control_config():
    s = ScenarioGenerator(seed=1).sample(difficulty=0.0)
    # control — это ScenarioConfig из общего реестра (не строка-ключ)
    assert s.control is SCENARIOS[s.control.name]
    assert s.control is DEFAULT  # без отказов → базовый пресет


# --------------------------------------------------------------------------- #
# Единые пресеты сценариев (управление + стандартная погода)
# --------------------------------------------------------------------------- #

def test_presets_mirror_control_registry_with_same_pids():
    assert set(SCENARIO_PRESETS) == set(SCENARIOS)
    # инвариант: PID-настройки не менялись — control это тот же самый объект
    assert SCENARIO_PRESETS["default"].control is DEFAULT
    assert SCENARIO_PRESETS["nws_fail"].control is NWS_FAIL


def test_calm_presets_carry_standard_weather():
    # Спокойные пресеты (default + отказные) — ясно/штиль/сухо. Погодные пресеты
    # (RIGHT_WIND/WET/...) несут СВОЮ погоду (ScenarioConfig.weather) и здесь не проверяются.
    for name in ("default", "nws_fail", "left_reverse_fail", "right_reverse_fail"):
        w = SCENARIO_PRESETS[name].weather
        assert w.wind_speed_kts == 0.0          # штиль
        assert w.gust_kts == 0.0
        assert w.runway_friction == 0.0         # сухо (Dry)
        assert w.rain_pct == 0.0                # ясно


def test_preset_failures_match_control_preset():
    assert SCENARIO_PRESETS["default"].failures == ()
    assert SCENARIO_PRESETS["nws_fail"].failures == (FailureMode.NWS_FAIL,)
    assert SCENARIO_PRESETS["left_reverse_fail"].failures == (FailureMode.REVERSE_LEFT_FAIL,)


def test_preset_apply_control_matches_direct_config_apply():
    # apply_control делегирует в ScenarioConfig.apply → поведение прежнее (NWS активируется)
    controller = ControllingSystem(XPlaneBackend(xpc=FakeXPC(), settle_s=0.0, reload_each_reset=False))
    SCENARIO_PRESETS["nws_fail"].apply_control(controller)
    assert controller.failures.state.steering_eff == 0.0


def test_preset_roundtrips_through_dict():
    for name in SCENARIO_PRESETS:
        s = SCENARIO_PRESETS[name]
        restored = Scenario.from_dict(s.to_dict())
        assert restored.control is s.control      # разрешается по имени в общий реестр
        assert restored.to_dict() == s.to_dict()
