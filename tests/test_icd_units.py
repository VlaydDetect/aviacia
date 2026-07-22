"""Сверка каждого сигнала стенда с документами Заказчика.

Два независимых первоисточника, и они описывают **разные** стороны обмена:

* `docs/ICSInterface.cs` — входная телеметрия: единицы указаны в doc-комментариях к каждому полю
  `ICSInputs`. У полей `ICSOutputs` комментариев нет вовсе;
* `docs/Входы_САУ.xlsx`, лист «Управляющие сигналы» — единицы и пределы **команд**.

Именно из-за этого разделения раньше и разъехались шкалы: пределы выходов выводились из единиц
входной телеметрии, то есть из шкалы, по которой орган **отчитывается**, а не по которой им
командуют. Тест фиксирует обе таблицы как данные, чтобы расхождение всплывало здесь, а не на
стенде.
"""

import math

import pytest

from ismpu.config.ics import (
    AILERON_MAX_DEG, RUDDER_MAX_DEG, THROTTLE_RATE_MAX_DEG_S, TILLER_MAX_MM,
    RUDDER_PEDAL_MAX_MM, BRAKE_CMD_MAX_MM, BRAKE_FEEDBACK_MAX_MM, AIRBRAKE_CMD_MAX_MM,
    THROTTLE_ANGLE_MIN_DEG, THROTTLE_ANGLE_MAX_DEG, ControlValid,
    ROLLOUT_CONTROL_MASK, TAXI_CONTROL_MASK, AIRBORNE_CONTROL_MASK, FlightPhase,
)
from ismpu.envs.ics_sim import Telemetry
from ismpu.envs.weather import WeatherState, RunwayCondition, runway_condition_from_bench
from ismpu.utils.converts import Converts

from fakes import make_ics_inputs


# --------------------------------------------------------------------------- #
# Команды: docs/Входы_САУ.xlsx, лист «Управляющие сигналы»
# --------------------------------------------------------------------------- #

COMMAND_TABLE = {
    # поле ICSOutputs          (размерность, предел «от», предел «до»)
    "ElevatorCmd":          ("g",     None, None),   # заданная перегрузка, +TED
    "AileronCmd":           ("deg",  -25.0,  25.0),  # +LWD
    "RudderCmd":            ("deg",  -30.0,  30.0),  # +TER
    "ThrottleLeftRate":     ("deg/s", -8.0,   8.0),
    "ThrottleRightRate":    ("deg/s", -8.0,   8.0),
    "NoseWheelTillerCmd":   ("mm",   -65.0,  65.0),  # используется на рулении
    "RudderPedalCmd":       ("mm",   -75.0,  75.0),  # используется на пробеге
    "BrakeLeftCmd":         ("mm",     0.0,  45.0),
    "BrakeRightCmd":        ("mm",     0.0,  45.0),
    "AirbrakeCmd":          ("mm",     0.0,  55.0),
}


def test_command_limits_match_the_customer_table():
    """Наши константы обязаны совпадать с таблицей управляющих сигналов Заказчика."""
    assert COMMAND_TABLE["AileronCmd"][2] == AILERON_MAX_DEG
    assert COMMAND_TABLE["RudderCmd"][2] == RUDDER_MAX_DEG
    assert COMMAND_TABLE["ThrottleLeftRate"][2] == THROTTLE_RATE_MAX_DEG_S
    assert COMMAND_TABLE["ThrottleRightRate"][2] == THROTTLE_RATE_MAX_DEG_S
    assert COMMAND_TABLE["NoseWheelTillerCmd"][2] == TILLER_MAX_MM
    assert COMMAND_TABLE["RudderPedalCmd"][2] == RUDDER_PEDAL_MAX_MM
    assert COMMAND_TABLE["BrakeLeftCmd"][2] == BRAKE_CMD_MAX_MM
    assert COMMAND_TABLE["BrakeRightCmd"][2] == BRAKE_CMD_MAX_MM
    assert COMMAND_TABLE["AirbrakeCmd"][2] == AIRBRAKE_CMD_MAX_MM


def test_tiller_is_a_travel_not_an_angle():
    """Тиллер задаётся ходом в миллиметрах.

    Отдельным тестом, потому что ошибка была именно в размерности: стояли 70 «градусов» —
    справочный предел поворота стойки A330, попавший на место хода органа управления. Число,
    похожее на правду, но не та величина.
    """
    assert COMMAND_TABLE["NoseWheelTillerCmd"][0] == "mm"
    assert TILLER_MAX_MM == 65.0


def test_the_command_and_feedback_brake_scales_are_different():
    """0–45 мм командует, 0–36.73 мм отчитывается. Подмена недодаёт ~18 % хода."""
    assert BRAKE_CMD_MAX_MM == 45.0
    assert BRAKE_FEEDBACK_MAX_MM == 36.73
    assert BRAKE_FEEDBACK_MAX_MM / BRAKE_CMD_MAX_MM == pytest.approx(0.816, abs=1e-3)


def test_absolute_throttle_position_is_not_a_customer_command():
    """В перечне управляющих сигналов абсолютного положения РУД нет — только скорость.

    Отсюда и ответ про реверс: его величину задаёт скорость перемещения, а `ReverseXCmd` —
    только створки. Ни один наземный режим не заявляет `ThrottleLeft`/`ThrottleRight`.
    """
    assert "ThrottleLeft" not in COMMAND_TABLE and "ThrottleRight" not in COMMAND_TABLE
    for mask in (ROLLOUT_CONTROL_MASK, TAXI_CONTROL_MASK, AIRBORNE_CONTROL_MASK):
        assert ControlValid.THROTTLE_LEFT not in mask
        assert ControlValid.THROTTLE_RIGHT not in mask


def test_every_declared_channel_has_a_documented_scale():
    """Заявляем только то, для чего у нас есть подтверждённая шкала."""
    name_by_bit = {
        ControlValid.ELEVATOR: "ElevatorCmd",
        ControlValid.AILERON: "AileronCmd",
        ControlValid.RUDDER: "RudderCmd",
        ControlValid.THROTTLE_LEFT_RATE: "ThrottleLeftRate",
        ControlValid.THROTTLE_RIGHT_RATE: "ThrottleRightRate",
        ControlValid.NOSE_WHEEL_TILLER: "NoseWheelTillerCmd",
        ControlValid.RUDDER_PEDAL: "RudderPedalCmd",
        ControlValid.BRAKE_LEFT: "BrakeLeftCmd",
        ControlValid.BRAKE_RIGHT: "BrakeRightCmd",
        ControlValid.AIRBRAKE: "AirbrakeCmd",
    }
    for mask in (ROLLOUT_CONTROL_MASK, TAXI_CONTROL_MASK, AIRBORNE_CONTROL_MASK):
        for bit in ControlValid:
            if bit in mask:
                # Створки реверса — перечисление Off/Arm/Deploy, шкалы у них нет.
                if bit in (ControlValid.REVERSE_LEFT, ControlValid.REVERSE_RIGHT):
                    continue
                assert name_by_bit[bit] in COMMAND_TABLE, f"{bit!r} заявлен без описанной шкалы"


# --------------------------------------------------------------------------- #
# Телеметрия: docs/ICSInterface.cs
# --------------------------------------------------------------------------- #

def test_telemetry_conversions_match_the_documented_input_units():
    """Стенд шлёт узлы, футы, фут/мин и град/с — граница пересчёта в СИ проходит в `Telemetry`."""
    inp = make_ics_inputs(
        Latitude=55.9, Longitude=37.4,
        GroundSpeed=140.0, IndicatedAirspeed=145.0, TrueAirspeed=150.0,   # kt
        RadioAltitude=1000.0, BaroAltitude=1630.0,                        # ft
        VerticalSpeed=-750.0,                                             # ft/min
        BodyRollRate=3.0, BodyPitchRate=-2.0, BodyYawRate=1.0,            # deg/s
        BodyLongAccel=0.1, BodyNormAccel=0.2, BodyLatAccel=-0.05,         # g
        TrueHeading=75.0, PitchAngle=2.5, RollAngle=-1.0,                 # deg
        WindSpeed=20.0, WindDirectionTrue=180.0,                          # kt / deg
        RadioAltitudeValid=1,
    )
    t = Telemetry.from_ics(inp)

    assert t.groundspeed_ms == pytest.approx(140.0 * 0.514444, abs=1e-3)
    assert t.ias_ms == pytest.approx(145.0 * 0.514444, abs=1e-3)
    assert t.elevation_m == pytest.approx(1630.0 * 0.3048, abs=1e-6)
    assert t.agl_m == pytest.approx(1000.0 * 0.3048, abs=1e-6)
    assert t.vy_ms == pytest.approx(-750.0 * 0.3048 / 60.0, abs=1e-9)
    assert t.p_rad == pytest.approx(math.radians(3.0))
    assert t.q_rad == pytest.approx(math.radians(-2.0))
    assert t.r_rad == pytest.approx(math.radians(1.0))
    # Ускорения остаются в g — так они и задокументированы, пересчитывать нечего.
    assert (t.accel_long_g, t.accel_norm_g, t.accel_side_g) == (0.1, 0.2, -0.05)
    # Радиовысота отдаётся и в футах — пороги включения заданы в футах.
    assert t.radio_altitude_ft == 1000.0
    assert t.wind_speed_ms == pytest.approx(20.0 * 0.514444, abs=1e-3)


def test_vertical_speed_conversion_is_exact():
    """1 фут/мин = 0.3048/60 м/с. Приближение здесь копится на всём заходе."""
    assert Converts.FTM_TO_MS == Converts.FT_TO_M / 60.0


def test_visibility_is_converted_from_feet():
    """`Visibility` в футах. Без пересчёта 16000 футов читались бы как «ясно» вместо 4.9 км."""
    w = WeatherState.from_ics(make_ics_inputs(Visibility=16000.0))
    assert w.visibility_m == pytest.approx(16000.0 * 0.3048, abs=1e-6)
    # RVR 300 м из матрицы прогонов — это ~984 фута.
    low = WeatherState.from_ics(make_ics_inputs(Visibility=984.0))
    assert low.visibility_m == pytest.approx(300.0, abs=1.0)


def test_runway_condition_codes_are_remapped_not_passed_through():
    """Коды стенда не упорядочены по скользкости, поэтому есть своя монотонная шкала."""
    assert runway_condition_from_bench(0) is RunwayCondition.DRY
    assert runway_condition_from_bench(1) is RunwayCondition.WET          # WET=1
    assert runway_condition_from_bench(2) is RunwayCondition.ICY          # ICE=2 у стенда
    assert runway_condition_from_bench(3) is RunwayCondition.PUDDLY       # FLOODED=3
    # В шкале стенда 2 < 3, а по скользкости лёд хуже залитой полосы — порядок обратный.
    assert (runway_condition_from_bench(2).value
            > runway_condition_from_bench(3).value)
    # Неизвестный код — самый скользкий вариант, а не «сухо».
    assert runway_condition_from_bench(99) is RunwayCondition.ICY


def test_flight_phase_codes_match_the_icd_enumeration():
    """Нумерация фаз из doc-комментария `FlightPhase` в ICSInterface.cs."""
    assert int(FlightPhase.APPROACH_ABOVE_30M) == 9
    assert int(FlightPhase.APPROACH_ABOVE_15M) == 10
    assert int(FlightPhase.LAND_FLARE_AND_TOUCHDOWN) == 11
    assert int(FlightPhase.LAND_RUN) == 12
    assert int(FlightPhase.TAXI_IN) == 13


def test_throttle_feedback_range_is_the_input_scale():
    """−26.5…55.0° — фактическое положение РУД во входной телеметрии, не команда."""
    assert (THROTTLE_ANGLE_MIN_DEG, THROTTLE_ANGLE_MAX_DEG) == (-26.5, 55.0)
