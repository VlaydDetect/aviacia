"""Тесты стенда (`ICSSim`) и подбора сценария — без реального стенда."""

import math
from dataclasses import fields

import pytest

from ismpu.control.channels import ControlsState
from ismpu.control.failures import FailureMode
from ismpu.control.system import ControllingSystem
from ismpu.envs.ics_sim import ICSSim, Telemetry
from ismpu.io.ics_connector import ControlModeState, ReverseEngineType, ICSOutputs
from ismpu.config.ics import (
    FlightPhase, ControlValid, ROLLOUT_CONTROL_MASK, TAXI_CONTROL_MASK, AIRBORNE_CONTROL_MASK,
    BRAKE_CMD_MAX_MM, THROTTLE_ANGLE_MIN_DEG, THROTTLE_RATE_MAX_DEG_S,
    TILLER_MAX_MM, RUDDER_MAX_DEG, RUDDER_PEDAL_MAX_MM,
)
from ismpu.config.scenarios import (
    Scenario, SCENARIOS, select_scenario, select_for_telemetry, weather_distance,
)
from ismpu.config.scenarios import DEFAULT, NWS_FAIL
from ismpu.config.segments import FlightSegment
from ismpu.envs.weather import WeatherState, RunwayCondition, WEATHER_PRESETS

from fakes import (
    make_ics_inputs, on_ground, FakeConnector, HandshakeBench, engaged_sim, telemetry,
)


# --------------------------------------------------------------------------- #
# Телеметрия: единицы и стенд-специфичные сигналы
# --------------------------------------------------------------------------- #

def test_read_telemetry_converts_icd_units_to_si():
    """Стенд отдаёт узлы, футы, футы/мин и градусы/с — граница пересчёта проходит здесь.

    Пропущенный перевод путевой скорости давал бы ошибку в 1.94 раза, и продольный канал
    прочитал бы 140 узлов как 272, немедленно дав полное торможение.
    """
    from ismpu.utils.converts import Converts

    inp = make_ics_inputs(LatitudeValid=1, Latitude=55.9,
                          LongitudeValid=1, Longitude=37.4,
                          TrueHeadingValid=1, TrueHeading=75.0,
                          GroundSpeedValid=1, GroundSpeed=140.0,       # узлы
                          IndicatedAirspeedValid=1, IndicatedAirspeed=145.0,
                          WindSpeed=8.0,              # узлы
                          RadioAltitudeValid=1, RadioAltitude=100.0,   # футы
                          BaroAltitudeValid=1, BaroAltitude=600.0,     # футы
                          VerticalSpeedValid=1, VerticalSpeed=-120.0, # футы/мин
                          BodyYawRateValid=1, BodyYawRate=6.0,         # градусы/с
                          BodyLongAccelValid=1, BodyLongAccel=-0.25)
    telem = ICSSim(connector=FakeConnector(inp), aircraft_profile="mc21").read_telemetry()

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


def test_invalid_ics_signals_are_not_exposed_as_numeric_telemetry():
    telem = Telemetry.from_ics(make_ics_inputs(
        Latitude=55.9,
        Longitude=37.4,
        GroundSpeed=140.0,
        TrueHeading=75.0,
        RadioAltitude=100.0,
        BaroAltitude=600.0,
        IndicatedAirspeed=145.0,
    ))

    assert telem.lat is None and telem.lon is None
    assert telem.groundspeed_ms is None
    assert telem.heading_true_deg is None
    assert telem.agl_m is None and telem.elevation_m is None
    assert telem.radio_altitude_ft is None and telem.ias_ms is None


def test_read_telemetry_maps_bench_only_signals():
    inp = make_ics_inputs(
        FlightPhaseValid=1, FlightPhase=int(FlightPhase.LAND_RUN),
        RunwayHeadingValid=1, RunwayHeading=75.08, RunwayLength=3700.0, RunwayWidth=60.0,
        LateralDeviation=1.4, RunwayCondition=4,                # 4 = ICE по фактическому пакету
        NoseGearWeightOnWheels=1, LeftGearWeightOnWheels=1, RightGearWeightOnWheels=1,
        FaultNWS=1, FaultLeftEngineReverse=1)
    telem = ICSSim(connector=FakeConnector(inp), aircraft_profile="mc21").read_telemetry()

    assert telem.runway_heading_deg == pytest.approx(75.08)
    assert telem.runway_length_m == pytest.approx(3700.0)
    assert telem.lateral_deviation_m == pytest.approx(1.4)
    assert telem.weight_on_wheels is True
    assert telem.flight_phase == int(FlightPhase.LAND_RUN)
    assert telem.faults == frozenset({FailureMode.NWS_FAIL, FailureMode.REVERSE_LEFT_FAIL})
    assert telem.runway_condition == pytest.approx(RunwayCondition.ICY.value)


def test_weight_on_wheels_requires_all_three_gear():
    inp = make_ics_inputs(NoseGearWeightOnWheels=1, LeftGearWeightOnWheels=1,
                          RightGearWeightOnWheels=0)
    assert ICSSim(connector=FakeConnector(inp), aircraft_profile="mc21").read_telemetry().weight_on_wheels is False


def test_unknown_runway_condition_is_treated_as_slippery():
    """Неизвестный код — не повод предполагать сухую полосу."""
    inp = make_ics_inputs(RunwayCondition=99)
    telem = ICSSim(connector=FakeConnector(inp), aircraft_profile="mc21").read_telemetry()
    assert telem.runway_condition == pytest.approx(RunwayCondition.ICY.value)


def test_read_telemetry_invalid_on_timeout():
    sim = ICSSim(connector=FakeConnector(None), aircraft_profile="mc21")
    assert sim.read_telemetry().valid is False


# --------------------------------------------------------------------------- #
# Погода — из телеметрии стенда, а не из сценария
# --------------------------------------------------------------------------- #

def test_weather_comes_from_the_bench_packet():
    """Погоду задаёт Заказчик; наш `WeatherState` — это прочитанный кадр, а не задание."""
    from ismpu.utils.converts import Converts

    inp = make_ics_inputs(WindSpeed=12.0, WindDirectionTrue=165.0, RunwayCondition=2,
                          PrecipitationRatio=0.6, Visibility=16000.0, AirfieldTemp=-4.0)
    weather = ICSSim(connector=FakeConnector(inp), aircraft_profile="mc21").read_telemetry().weather

    assert weather.wind_speed_kts == pytest.approx(12.0)        # узлы остаются узлами
    assert weather.wind_dir_from_degt == pytest.approx(165.0)
    assert weather.runway_friction == pytest.approx(RunwayCondition.WET.value)
    assert weather.rain_pct == pytest.approx(0.6)
    # Видимость приходит в ФУТАХ: без перевода 16000 футов выглядели бы как «ясно» вместо 4.9 км.
    assert weather.visibility_m == pytest.approx(16000.0 * Converts.FT_TO_M)
    assert weather.visibility_m < 5000.0
    assert weather.temperature_c == pytest.approx(-4.0)


def test_weather_is_none_without_a_bench_packet():
    assert ICSSim(connector=FakeConnector(None), aircraft_profile="mc21").read_telemetry().weather is None


# --------------------------------------------------------------------------- #
# Команды: единицы ICD и рукопожатие
# --------------------------------------------------------------------------- #

def test_commands_are_withheld_until_engaged():
    """До рукопожатия заявлять каналы нельзя: стенд ещё не разрешил нам ими управлять."""
    conn = FakeConnector(make_ics_inputs(GroundSpeed=30.0))
    sim = ICSSim(connector=conn, aircraft_profile="mc21")
    cmd = ControlsState()
    cmd.cmd_brake_l = 1.0
    sim.step(cmd)

    out = conn.sent_outputs[-1]
    assert sim.engaged is False
    assert out.ControlValidMask == 0
    assert out.ControlMode == ControlModeState.Off
    assert out.BrakeLeftCmd == 0.0        # команда не выдана, а не «выдана нулём случайно»


def test_step_converts_commands_to_icd_units():
    sim, conn = engaged_sim()
    cmd = ControlsState()
    cmd.cmd_brake_l, cmd.cmd_brake_r = 1.0, 0.5
    cmd.cmd_rudder = 1.0
    cmd.cmd_pedal = 1.0
    cmd.cmd_rev_l, cmd.cmd_rev_r = -1.0, 0.0
    sim.step(cmd)
    out = conn.sent_outputs[-1]

    assert out.ControlMode == ControlModeState.Rollout
    assert out.ControlValidMask == int(ROLLOUT_CONTROL_MASK)
    assert out.ControlValidMask != 0

    # Тормоза — ход КОМАНДЫ педали в мм (45 мм), а не нормированные [0, 1] и не 36.73 мм
    # обратной связи.
    assert out.BrakeLeftCmd == pytest.approx(BRAKE_CMD_MAX_MM)
    assert out.BrakeRightCmd == pytest.approx(BRAKE_CMD_MAX_MM * 0.5)

    # Путевое управление на пробеге: руль направления (град) + педальный пост (мм).
    # Тиллер — орган руления, на пробеге не выдаётся.
    assert out.RudderCmd == pytest.approx(RUDDER_MAX_DEG)
    assert out.RudderPedalCmd == pytest.approx(RUDDER_PEDAL_MAX_MM)
    assert out.NoseWheelTillerCmd == 0.0

    # Реверс: величина — СКОРОСТЬЮ перемещения РУД (единственный документированный канал
    # управления тягой), створки — отдельным сигналом. Абсолютное положение не выдаётся.
    assert out.ThrottleLeftRate == pytest.approx(-THROTTLE_RATE_MAX_DEG_S)   # выпуск реверса
    assert out.ThrottleRightRate == pytest.approx(0.0)                        # уже на малом газу
    assert out.ThrottleLeft == 0.0 and out.ThrottleRight == 0.0
    assert out.ReverseLeftCmd == ReverseEngineType.Deploy
    assert out.ReverseRightCmd == ReverseEngineType.Off


def test_taxi_steers_with_the_tiller_not_the_rudder():
    """Разделение органов из таблицы Заказчика: тиллер — на рулении, педальный пост — на пробеге.

    На скорости пробега отклонять тиллер нельзя, а в Taxi allocator выдаёт отдельную
    `cmd_tiller`; руль направления и педальный пост остаются нулевыми.
    """
    sim, conn = engaged_sim()
    sim.request_taxi()
    cmd = ControlsState()
    cmd.cmd_tiller = 1.0
    sim.step(cmd)
    out = conn.sent_outputs[-1]

    assert out.ControlMode is ControlModeState.Taxi
    assert out.ControlValidMask == int(TAXI_CONTROL_MASK)
    assert out.NoseWheelTillerCmd == pytest.approx(TILLER_MAX_MM)
    assert out.RudderCmd == 0.0 and out.RudderPedalCmd == 0.0


def test_declared_mask_covers_only_channels_we_actually_drive():
    """Заявить канал, который не формируешь, — взять ответственность за неуправляемый орган."""
    assert ControlValid.RUDDER in ROLLOUT_CONTROL_MASK
    assert ControlValid.RUDDER_PEDAL in ROLLOUT_CONTROL_MASK
    assert ControlValid.BRAKE_LEFT in ROLLOUT_CONTROL_MASK
    assert ControlValid.BRAKE_RIGHT in ROLLOUT_CONTROL_MASK
    assert ControlValid.THROTTLE_LEFT_RATE in ROLLOUT_CONTROL_MASK
    assert ControlValid.REVERSE_LEFT in ROLLOUT_CONTROL_MASK
    assert ControlValid.REVERSE_RIGHT in ROLLOUT_CONTROL_MASK
    # Тиллер — орган руления, на пробеге его не заявляем и не выдаём.
    assert ControlValid.NOSE_WHEEL_TILLER not in ROLLOUT_CONTROL_MASK
    assert ControlValid.NOSE_WHEEL_TILLER in TAXI_CONTROL_MASK
    assert ControlValid.RUDDER_PEDAL not in TAXI_CONTROL_MASK
    # Абсолютного положения РУД в перечне управляющих сигналов Заказчика нет вовсе.
    assert ControlValid.THROTTLE_LEFT not in ROLLOUT_CONTROL_MASK
    assert ControlValid.THROTTLE_LEFT not in TAXI_CONTROL_MASK
    assert ControlValid.ELEVATOR not in ROLLOUT_CONTROL_MASK   # продольные органы не наши
    assert ControlValid.AILERON not in ROLLOUT_CONTROL_MASK
    assert ControlValid.AIRBRAKE not in ROLLOUT_CONTROL_MASK


def test_airborne_mask_is_the_value_confirmed_on_the_bench():
    """31 — единственная маска, с которой заход реально прошёл на стенде.

    Проверяется само число, а не набор имён: имена — наша интерпретация раскладки, а стендом
    подтверждено именно значение.
    """
    assert int(AIRBORNE_CONTROL_MASK) == 31
    assert ControlValid.ELEVATOR in AIRBORNE_CONTROL_MASK
    assert ControlValid.AILERON in AIRBORNE_CONTROL_MASK
    assert ControlValid.RUDDER in AIRBORNE_CONTROL_MASK
    assert ControlValid.THROTTLE_LEFT_RATE in AIRBORNE_CONTROL_MASK
    assert ControlValid.THROTTLE_RIGHT_RATE in AIRBORNE_CONTROL_MASK
    # Колёсные органы в воздухе не заявляются, даже если структура их несёт.
    assert ControlValid.BRAKE_LEFT not in AIRBORNE_CONTROL_MASK
    assert ControlValid.NOSE_WHEEL_TILLER not in AIRBORNE_CONTROL_MASK


def test_mask_layout_matches_the_command_field_count():
    """Один бит на одно командное поле `ICSOutputs` — иначе заявка попадает не в тот канал.

    Раскладка выведена из двух наблюдений стенда (бит 0 = руль высоты, маска 31 = первые пять
    полей) плюс совпадения числа полей с `CONTROL_COMMAND_COUNT = 14` у второго участника НИР.
    """
    from ismpu.config.ics import CONTROL_COMMAND_COUNT, ALL_CONTROL_MASK

    assert len(ControlValid) == CONTROL_COMMAND_COUNT == 14
    assert ALL_CONTROL_MASK == 16383
    # Порядок битов = порядок командных полей в структуре, до флагов режимов.
    command_fields = [f.name for f in fields(ICSOutputs)][2:2 + CONTROL_COMMAND_COUNT]
    assert command_fields == [
        "ElevatorCmd", "AileronCmd", "RudderCmd", "ThrottleLeftRate", "ThrottleRightRate",
        "ThrottleLeft", "ThrottleRight", "NoseWheelTillerCmd", "RudderPedalCmd",
        "BrakeLeftCmd", "BrakeRightCmd", "AirbrakeCmd", "ReverseLeftCmd", "ReverseRightCmd",
    ]


def test_active_failures_come_from_telemetry():
    sim, _ = engaged_sim(FaultNWS=1)
    assert FailureMode.NWS_FAIL in sim.active_failures
    assert FailureMode.ENGINE_OUT_LEFT not in sim.active_failures


def test_ics_requires_profile_and_records_nonfatal_transition_mismatch():
    with pytest.raises(ValueError, match="aircraft_profile"):
        ICSSim(connector=FakeConnector())

    scenario = SCENARIOS["b_4_2_through_engine_out"]
    connector = FakeConnector(on_ground(
        FaultLeftEngine=1,
        Visibility=16000.0 / 0.3048,
    ))
    sim = ICSSim(connector=connector, aircraft_profile="mc21")
    first = sim.reset(scenario)
    controller = ControllingSystem(sim)
    controller.bind_scenario(scenario, "mc21")
    controller.activate_segment(FlightSegment.APPROACH, first)
    approach = sim.condition_match
    assert approach.matrix_run_id == "Б.4.2/1"
    assert approach.matrix_code == "Б.4.2"
    assert not approach.weather_matches
    assert approach.acceptance_valid
    assert sim.conditions_valid
    assert controller.failures.state.thrust_left_eff == 0.0

    # The bench still reports only the engine failure at touchdown.  This is
    # unsafe to "fix" by dropping authority, so the transition continues but
    # the run is invalid and the exact mismatch remains auditable.
    controller.activate_segment(FlightSegment.ROLLOUT, first)
    rollout = sim.condition_match
    assert rollout.matrix_run_id == "Б.4.2/1"
    assert rollout.missing_failures == frozenset({FailureMode.REVERSE_LEFT_FAIL})
    assert not sim.conditions_valid
    assert sim.condition_matches == [approach, rollout]
    # The first rollout calculation must use what the bench actually reports,
    # not the expected-but-missing reverser failure from the composed scenario.
    assert controller.failures.state.thrust_left_eff == 0.0
    assert controller.failures.state.reverse_left_eff == 1.0


# --------------------------------------------------------------------------- #
# Отказы: источник истины — борт, а не пресет сценария
# --------------------------------------------------------------------------- #

def test_controller_takes_failures_from_the_bench_not_from_the_preset():
    """Пресет — стартовое предположение; фактическую конфигурацию сообщает борт."""
    from ismpu.config.constants import DT

    controller = ControllingSystem()
    SCENARIOS["default"].apply_control(controller, "mc21")
    assert controller.failures.state.steering_eff == 1.0

    failed = telemetry(ics_inputs=on_ground(FaultNWS=1))
    controller.control_step(DT, failed, send=False)
    assert controller.failures.state.steering_eff == 0.0      # борт сообщил отказ NWS


def test_failures_are_cleared_when_the_bench_stops_reporting_them():
    """Отказ может быть снят — накапливающий учёт держал бы орган мёртвым до конца эпизода."""
    from ismpu.config.constants import DT

    controller = ControllingSystem()
    SCENARIOS["nws_fail"].apply_control(controller, "mc21")
    assert controller.failures.state.steering_eff == 0.0

    healthy = telemetry(ics_inputs=on_ground())
    controller.control_step(DT, healthy, send=False)
    assert controller.failures.state.steering_eff == 1.0


def test_synthetic_telemetry_does_not_silently_clear_the_preset_failure():
    """Кадр без пакета стенда: пустой `faults` значит «сообщать некому», а не «всё исправно».

    Приравняв одно к другому, офлайн-прогон (тесты, разбор логов) молча снимал бы отказ пресета
    и мерил бы совсем не тот режим.
    """
    from ismpu.config.constants import DT

    controller = ControllingSystem()
    SCENARIOS["nws_fail"].apply_control(controller, "mc21")
    controller.control_step(DT, telemetry(50.0), send=False)     # ics_inputs=None
    assert controller.failures.state.steering_eff == 0.0


def test_lost_packet_does_not_repair_a_failed_actuator():
    """Единичный таймаут — не повод вернуть рулю авторитет, которого у него нет."""
    from ismpu.config.constants import DT

    controller = ControllingSystem()
    SCENARIOS["default"].apply_control(controller, "mc21")
    controller.control_step(DT, telemetry(ics_inputs=on_ground(FaultNWS=1)), send=False)
    assert controller.failures.state.steering_eff == 0.0

    controller.control_step(DT, Telemetry.invalid(), send=False)
    assert controller.failures.state.steering_eff == 0.0


# --------------------------------------------------------------------------- #
# Контур против стенда
# --------------------------------------------------------------------------- #

def test_controller_runs_the_plain_loop_against_the_bench():
    """Базовый контур на стенде: `control_step` сам читает телеметрию и сам отправляет."""
    from ismpu.config.constants import DT

    sim, conn = engaged_sim(GroundSpeed=100.0)
    controller = ControllingSystem(sim)
    assert not hasattr(controller, "xpc")
    SCENARIOS["default"].apply_control(controller, "mc21")

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

    sim, conn = engaged_sim(GroundSpeed=100.0)
    reads = {"n": 0}
    original = sim.read_telemetry

    def counting_read():
        reads["n"] += 1
        return original()

    sim.read_telemetry = counting_read
    controller = ControllingSystem(sim)
    SCENARIOS["default"].apply_control(controller, "mc21")

    ticks = 4
    for _ in range(ticks):
        controller.control_step(DT)

    assert len(conn.sent_outputs) == ticks
    # По одному чтению на такт (внутри `sim.step`) плюс одно холодное на первом такте.
    # Наивная реализация читала бы дважды за такт — вдвое больше приёмов UDP.
    assert reads["n"] == ticks + 1
    assert reads["n"] < 2 * ticks


def test_control_exception_sends_a_neutral_command_then_releases_the_channels(monkeypatch):
    """Замолчать нельзя: последнее отклонение осталось бы приложенным до сторожа на той стороне.

    Но и одной нейтрали мало: нулевая команда с заявленной маской — это по-прежнему команда
    (в воздухе нулевой РУД означает «малый газ»). Поэтому за нейтралью идёт снятие заявки
    каналов, и последним, что видит стенд, оказывается `ControlValidMask = 0` + `Off`.
    """
    from ismpu.config.constants import DT

    monkeypatch.setattr("ismpu.envs.ics_sim.time.sleep", lambda _s: None)
    sim, conn = engaged_sim(GroundSpeed=100.0)
    controller = ControllingSystem(sim)
    SCENARIOS["default"].apply_control(controller, "mc21")
    controller.control_step(DT)

    sent_before = len(conn.sent_outputs)
    controller.control_exception()

    assert len(conn.sent_outputs) > sent_before          # молчания нет
    neutral = conn.sent_outputs[sent_before]
    assert neutral.BrakeLeftCmd == 0.0 and neutral.BrakeRightCmd == 0.0
    assert neutral.RudderCmd == 0.0 and neutral.NoseWheelTillerCmd == 0.0

    released = conn.sent_outputs[-1]
    assert released.ControlValidMask == 0
    assert released.ControlMode is ControlModeState.Off
    assert released.ModeAIReady == 0
    assert controller.state.break_control is True
    assert sim.engaged is False


def test_lateral_channel_uses_runway_geometry_from_telemetry():
    """Иначе поставленная система на любой ВПП поедет по осевой Шереметьево из конфига."""
    from ismpu.config.constants import DT

    def rudder_for(runway_heading, lateral_deviation):
        controller = ControllingSystem()
        SCENARIOS["default"].apply_control(controller, "mc21")
        telem = Telemetry.from_ics(make_ics_inputs(
            GroundSpeedValid=1, GroundSpeed=100.0,
            TrueHeadingValid=1, TrueHeading=runway_heading,
            MagneticHeadingValid=1, MagneticHeading=runway_heading,
            TrkAngleMagneticValid=1, TrkAngleMagnetic=runway_heading,
            RunwayHeadingValid=1, RunwayHeading=runway_heading,
            LateralDeviation=lateral_deviation,
        ))
        controller.control_step(DT, telem, send=False)
        return controller.state.rudder_cmd

    # ВПП с курсом, не имеющим ничего общего с UUEE 06R: смещение вправо парируется влево.
    assert rudder_for(200.0, +3.0) < 0.0
    assert rudder_for(200.0, -3.0) > 0.0
    assert rudder_for(200.0, 0.0) == pytest.approx(0.0, abs=1e-9)

    # Значение отклонения берётся из телеметрии, а не пересчитывается по конфигу.
    assert rudder_for(200.0, +5.0) < rudder_for(200.0, +1.0)


def test_geodetic_path_is_kept_when_the_bench_gives_no_runway_geometry():
    """Fallback работает лишь когда профиль ВПП явно приложен к кадру."""
    from ismpu.config.constants import DT

    controller = ControllingSystem()
    SCENARIOS["default"].apply_control(controller, "mc21")
    telem = telemetry(50.0)
    assert telem.runway_heading_deg is None and telem.lateral_deviation_m is None
    controller.control_step(DT, telem, send=False)   # геодезический путь, без исключений
    assert controller.lateral_channel.last_diagnostics.source == "geodetic"


def test_missing_direct_and_explicit_geodetic_sources_is_neutral_and_diagnostic():
    from ismpu.config.constants import DT

    controller = ControllingSystem()
    SCENARIOS["default"].apply_control(controller, "mc21")
    telem = telemetry(50.0, runway_profile=None)

    controller.control_step(DT, telem, send=False)

    assert controller.state.rudder_cmd == 0.0
    diag = controller.lateral_channel.last_diagnostics
    assert diag.xte is None
    assert diag.course_error is None
    assert diag.heading_error is None
    assert diag.guidance_error is None
    assert diag.along_track is None
    assert diag.source == "unavailable"
    assert diag.event == "guidance_unavailable"


def test_real_bench_heading_64_frame_ignores_uuee_coordinates():
    """Характеризация стендового кадра: direct-пара имеет приоритет над UUEE fallback."""
    from ismpu.config.constants import DT
    from ismpu.config.runway_profiles import UUEE_06R

    def result_for(lat, lon):
        controller = ControllingSystem()
        SCENARIOS["default"].apply_control(controller, "mc21")
        frame = Telemetry.from_ics(make_ics_inputs(
            LatitudeValid=1, Latitude=lat, LongitudeValid=1, Longitude=lon,
            GroundSpeedValid=1, GroundSpeed=100.0,
            # Намеренно несовместимые true-направления: direct-пара магнитная и не должна
            # смешиваться ни с ними, ни с геометрией профиля UUEE.
            TrueHeadingValid=1, TrueHeading=123.0,
            TrkAngleTrueValid=1, TrkAngleTrue=123.0,
            MagneticHeadingValid=1, MagneticHeading=66.0,
            TrkAngleMagneticValid=1, TrkAngleMagnetic=64.0,
            RunwayHeadingValid=1, RunwayHeading=64.0,
            LateralDeviation=0.0,
        ), runway_profile=UUEE_06R)
        controller.control_step(DT, frame, send=False)
        return controller.state.rudder_cmd, controller.lateral_channel.last_diagnostics

    for lat, lon in ((55.96715, 37.3865417), (0.0, 0.0)):
        rudder, diag = result_for(lat, lon)
        assert rudder == pytest.approx(0.0, abs=1e-12)
        assert diag.xte == 0.0
        assert diag.course_error == 0.0
        assert diag.heading_error == -2.0
        assert diag.guidance_error == 0.0
        assert diag.source == "ics_direct"


def test_lateral_deviation_sign_is_an_aircraft_profile_calibration():
    from ismpu.config.constants import DT
    from ismpu.config.aircraft_profiles import AircraftProfile

    inp = make_ics_inputs(
        GroundSpeedValid=1, GroundSpeed=100.0,
        MagneticHeadingValid=1, MagneticHeading=64.0,
        TrkAngleMagneticValid=1, TrkAngleMagnetic=64.0,
        RunwayHeadingValid=1, RunwayHeading=64.0,
        LateralDeviation=3.0,
    )
    normal = ICSSim(connector=FakeConnector(inp), aircraft_profile="mc21").read_telemetry()
    flipped = ICSSim(
        connector=FakeConnector(inp),
        aircraft_profile=AircraftProfile(
            "test-flipped", "test", ics_lateral_deviation_sign=-1.0),
    ).read_telemetry()

    assert normal.lateral_deviation_m == 3.0
    assert flipped.lateral_deviation_m == -3.0
    commands = []
    for frame in (normal, flipped):
        controller = ControllingSystem()
        SCENARIOS["default"].apply_control(controller, "mc21")
        controller.control_step(DT, frame, send=False)
        commands.append(controller.state.rudder_cmd)
    assert commands[0] == pytest.approx(-commands[1])
    with pytest.raises(ValueError, match=r"\+1 или -1"):
        AircraftProfile("bad", "bad", ics_lateral_deviation_sign=0.0)


# --------------------------------------------------------------------------- #
# Рукопожатие: сквозной холодный старт на земле
# --------------------------------------------------------------------------- #

def _cold_sim(**overrides):
    conn = HandshakeBench(on_ground(GroundSpeed=0.0, **overrides))
    return ICSSim(connector=conn, aircraft_profile="mc21"), conn


def test_cold_ground_start_engages_only_after_the_bench_confirms(monkeypatch):
    """Сквозной прогрев: маска нулевая, пока стенд не подтвердил `AgentIsActive = 1`."""
    from ismpu.config.ics import ENGAGE_MIN_READY_FRAMES

    monkeypatch.setattr("ismpu.envs.ics_sim.time.sleep", lambda _s: None)
    sim, conn = _cold_sim()
    sim.reset(SCENARIOS["default"])
    assert sim.engaged is False

    assert sim.warm_up(timeout_s=30.0) is True
    assert sim.engaged is True

    # Всё, что ушло за прогрев, — только заявка готовности: каналы не заявлялись ни разу.
    warmup = list(conn.sent_outputs)
    assert all(o.ControlValidMask == 0 for o in warmup)
    # Две секунды готовности реально передавались кадрами с ControlMode = Off.
    ready_off = [o for o in warmup
                 if o.ControlMode == ControlModeState.Off and o.ModeAIReady == 1]
    assert len(ready_off) >= ENGAGE_MIN_READY_FRAMES
    # И состоялся переход 0 → 4 — тот самый стимул, по которому стенд нас включил.
    assert any(o.ControlMode == ControlModeState.Taxi for o in warmup)

    # После подтверждения реальная команда несёт маску руления (наземное включение с нуля ведёт
    # именно в Taxi) и ControlMode = Taxi.
    cmd = ControlsState()
    cmd.cmd_brake_l = 0.5
    sim.step(cmd)
    last = conn.sent_outputs[-1]
    assert last.ControlMode == ControlModeState.Taxi
    assert last.ControlValidMask == int(TAXI_CONTROL_MASK)


def test_warm_up_paces_itself_and_does_not_flood_the_bench(monkeypatch):
    """Темп задаётся часами, а не sleep.

    Со сломанным (или подменённым) sleep наивный цикл выпаливал 139 тысяч пакетов за две
    секунды — стенд рассчитан на 20 Гц.
    """
    monkeypatch.setattr("ismpu.envs.ics_sim.time.sleep", lambda _s: None)
    sim, conn = _cold_sim()
    sim.reset(SCENARIOS["default"])
    sim.warm_up(timeout_s=30.0)

    assert sim.engaged is True
    # ~2 секунды на 20 Гц = ~40 кадров. Даём щедрый запас на дрожание, но ловим порядок величины.
    assert len(conn.sent_outputs) < 200


def test_warm_up_timeout_raises_with_a_diagnosis(monkeypatch):
    """Молча продолжить нельзя: дальше мы бы «управляли» в пустоту."""
    monkeypatch.setattr("ismpu.envs.ics_sim.time.sleep", lambda _s: None)
    sim, _ = _cold_sim(NoseGearWeightOnWheels=0)     # стойка не обжата → включения не будет

    with pytest.raises(TimeoutError) as exc:
        sim.warm_up(timeout_s=0.3)
    assert "стойки" in str(exc.value)                # причина названа, а не «не получилось»
    assert sim.engaged is False


def test_reset_does_not_touch_the_bench_environment():
    """Средой распоряжается Заказчик: `reset` ничего не выставляет, только сбрасывает автомат."""
    sim, conn = engaged_sim()
    assert sim.engaged is True
    sim.reset(SCENARIOS["icy_rwy"])
    assert conn.sent_outputs == []        # ни одной команды на конфигурацию среды


def test_cold_ground_start_does_not_end_the_run_on_the_first_tick():
    """Раньше неподвижное ВС завершало пробег на первом такте — до рукопожатия.

    «Скорость руления достигнута» тривиально истинна при 0 м/с (порог ≈5.14 м/с), поэтому цикл
    умирал за ~50 мс при потребных 2000 мс выдержки.
    """
    from ismpu.config.constants import DT

    controller = ControllingSystem()
    SCENARIOS["default"].apply_control(controller, "mc21")
    stationary = telemetry(0.0)

    for _ in range(50):
        assert controller.control_step(DT, stationary, send=False) is False
    assert controller.longitudinal_channel.rollout_started is False


def test_rollout_completion_still_fires_once_the_run_actually_started():
    """Защёлка не должна помешать нормальному завершению пробега."""
    from ismpu.config.constants import DT

    controller = ControllingSystem()
    SCENARIOS["default"].apply_control(controller, "mc21")

    controller.control_step(DT, telemetry(70.0), send=False)
    assert controller.longitudinal_channel.rollout_started is True

    assert controller.control_step(DT, telemetry(1.0), send=False) is True    # пробег окончен


def test_controller_without_a_bench_fails_loudly():
    """Без стенда контур не может ни прочитать, ни отправить — молчать об этом нельзя."""
    from ismpu.config.constants import DT

    controller = ControllingSystem()
    SCENARIOS["default"].apply_control(controller, "mc21")
    with pytest.raises(RuntimeError, match="стенд"):
        controller.control_step(DT, telemetry(), send=True)

    # Чистый расчёт без отправки нужен replay-тестам и диагностике алгоритма.
    assert controller.control_step(DT, telemetry(), send=False) is False


# --------------------------------------------------------------------------- #
# Scenario: сериализация и подбор под фактические условия
# --------------------------------------------------------------------------- #

def test_scenario_roundtrip_with_weather_and_failures():
    scenario = Scenario.from_preset(
        "nws_fail", scenario_id="s1", seed=7,
        weather=WeatherState.from_crosswind(15.0, 5.0, runway_friction=RunwayCondition.ICY.value),
        failures=(FailureMode.NWS_FAIL, FailureMode.REVERSE_LEFT_FAIL),
    )
    restored = Scenario.from_dict(scenario.to_dict())
    assert restored.to_dict() == scenario.to_dict()
    assert restored.failures == scenario.failures
    assert restored.weather.runway_friction == pytest.approx(RunwayCondition.ICY.value)


def test_select_scenario_matches_the_reported_failure():
    """Старые gains теперь draft; для настройки их надо запросить явно."""
    with pytest.raises(ValueError, match="нет допущенных сценариев"):
        select_scenario((FailureMode.NWS_FAIL,))
    assert select_scenario((FailureMode.NWS_FAIL,), include_draft=True) is NWS_FAIL
    assert select_scenario((), include_draft=True) is DEFAULT


def test_failure_match_outweighs_any_weather_similarity():
    """Пресет под отказ NWS в штатной конфигурации ведёт себя не так, как нужно, — и никакая
    близость по погоде этого не компенсирует."""
    chosen = select_scenario((), WEATHER_PRESETS["icy"], include_draft=True)
    assert chosen.failures == ()


def test_select_scenario_prefers_closer_weather_within_the_same_failure_set():
    chosen = select_scenario((), WEATHER_PRESETS["icy"], include_draft=True)
    calm = select_scenario((), WEATHER_PRESETS["clear_dry"], include_draft=True)
    assert chosen.scenario_id != calm.scenario_id
    assert weather_distance(chosen.weather, WEATHER_PRESETS["icy"]) < \
           weather_distance(calm.weather, WEATHER_PRESETS["icy"])


def test_select_scenario_skips_draft_presets_by_default():
    """Молча выбрать невыверенный пресет — вести пробег на непроверенных коэффициентах."""
    assert all(
        scenario.is_draft("mc21", FlightSegment.ROLLOUT)
        for scenario in SCENARIOS.values()
    )
    with pytest.raises(ValueError, match="нет допущенных сценариев"):
        select_scenario(())


def test_select_for_telemetry_reads_conditions_off_the_bench():
    inp = on_ground(FaultNWS=1, RunwayCondition=4)      # отказ NWS на льду
    telem = ICSSim(connector=FakeConnector(inp), aircraft_profile="mc21").read_telemetry()
    assert select_for_telemetry(telem, include_draft=True) is NWS_FAIL


def test_select_for_telemetry_falls_back_to_default_without_telemetry():
    """Без кадра о конфигурации борта неизвестно ничего — безопасен только штатный пресет."""
    assert select_for_telemetry(Telemetry.invalid(), include_draft=True) is DEFAULT
    assert select_for_telemetry(None, include_draft=True) is DEFAULT


# --------------------------------------------------------------------------- #
# Единые пресеты сценариев (управление + условия калибровки)
# --------------------------------------------------------------------------- #

def test_scenarios_is_the_only_registry():
    assert SCENARIOS["default"] is DEFAULT
    assert SCENARIOS["nws_fail"] is NWS_FAIL


def test_calm_presets_carry_standard_weather():
    # Спокойные пресеты (default + отказные) — ясно/штиль/сухо. Погодные пресеты
    # (RIGHT_WIND/WET/...) несут СВОИ условия (SegmentConditions.weather) и здесь не проверяются.
    for name in ("default", "nws_fail", "left_reverse_fail", "right_reverse_fail"):
        w = SCENARIOS[name].weather
        assert w.wind_speed_kts == 0.0          # штиль
        assert w.runway_friction == 0.0         # сухо (Dry)
        assert w.rain_pct == 0.0                # ясно


def test_preset_failures_match_control_preset():
    assert SCENARIOS["default"].failures == ()
    assert SCENARIOS["nws_fail"].failures == (FailureMode.NWS_FAIL,)
    assert SCENARIOS["left_reverse_fail"].failures == (FailureMode.REVERSE_LEFT_FAIL,)


def test_preset_apply_control_matches_direct_config_apply():
    # apply_control пересобирает PID выбранной профильной ветки → NWS активируется.
    controller = ControllingSystem()
    SCENARIOS["nws_fail"].apply_control(controller, "mc21")
    assert controller.failures.state.steering_eff == 0.0


def test_preset_roundtrips_through_dict():
    for name in SCENARIOS:
        s = SCENARIOS[name]
        restored = Scenario.from_dict(s.to_dict())
        assert restored.to_dict() == s.to_dict()
