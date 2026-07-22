"""Тесты погоды: разбор ветра, шкала скользкости и чтение условий из пакета стенда."""

import pytest

from ismpu.envs.weather import (
    WeatherState, RunwayCondition, decompose_wind, compose_wind,
    runway_condition_from_bench, BENCH_RUNWAY_CONDITION, WEATHER_PRESETS,
)
from ismpu.config.runway import RWY_HEADING_TRUE
from ismpu.utils.converts import Converts

from fakes import make_ics_inputs


# --------------------------------------------------------------------------- #
# Разложение/сборка ветра
# --------------------------------------------------------------------------- #

def test_crosswind_from_right_is_perpendicular():
    # Чистый боковой ветер справа: дует «откуда» = курс ВПП + 90°.
    speed, direction = compose_wind(crosswind=15.0, headwind=0.0, runway_heading_degt=RWY_HEADING_TRUE)
    assert speed == pytest.approx(15.0)
    assert direction == pytest.approx((RWY_HEADING_TRUE + 90.0) % 360.0)


def test_pure_headwind_is_along_runway():
    speed, direction = compose_wind(crosswind=0.0, headwind=12.0, runway_heading_degt=RWY_HEADING_TRUE)
    assert speed == pytest.approx(12.0)
    assert direction == pytest.approx(RWY_HEADING_TRUE % 360.0)


def test_decompose_is_inverse_of_compose():
    for cross, head in [(15.0, 5.0), (-8.0, 10.0), (20.0, -3.0)]:
        speed, direction = compose_wind(cross, head, RWY_HEADING_TRUE)
        c2, h2 = decompose_wind(speed, direction, RWY_HEADING_TRUE)
        assert c2 == pytest.approx(cross, abs=1e-6)
        assert h2 == pytest.approx(head, abs=1e-6)


def test_weatherstate_from_crosswind():
    ws = WeatherState.from_crosswind(crosswind_kts=10.0, headwind_kts=0.0)
    assert ws.wind_speed_kts == pytest.approx(10.0)
    assert ws.wind_dir_from_degt == pytest.approx((RWY_HEADING_TRUE + 90.0) % 360.0)


# --------------------------------------------------------------------------- #
# Погода приходит из пакета стенда
# --------------------------------------------------------------------------- #

def test_from_ics_converts_units():
    """Стенд шлёт узлы и **футы**; в WeatherState видимость — в метрах."""
    inp = make_ics_inputs(WindSpeed=18.0, WindDirectionTrue=100.0, RunwayCondition=5,
                          PrecipitationRatio=0.25, Visibility=3000.0, AirfieldTemp=-6.5)
    ws = WeatherState.from_ics(inp)

    assert ws.wind_speed_kts == pytest.approx(18.0)          # узлы остаются узлами
    assert ws.wind_dir_from_degt == pytest.approx(100.0)
    assert ws.runway_friction == pytest.approx(RunwayCondition.SNOWY.value)
    assert ws.rain_pct == pytest.approx(0.25)
    assert ws.visibility_m == pytest.approx(3000.0 * Converts.FT_TO_M)
    assert ws.temperature_c == pytest.approx(-6.5)


def test_from_ics_wind_decomposes_relative_to_the_runway():
    """Для пробега существенна боковая составляющая, а не «скорость ветра» сама по себе."""
    inp = make_ics_inputs(WindSpeed=15.0, WindDirectionTrue=(RWY_HEADING_TRUE + 90.0) % 360.0)
    ws = WeatherState.from_ics(inp)
    cross, head = decompose_wind(ws.wind_speed_kts, ws.wind_dir_from_degt, RWY_HEADING_TRUE)
    assert cross == pytest.approx(15.0, abs=1e-6)
    assert head == pytest.approx(0.0, abs=1e-6)


# --------------------------------------------------------------------------- #
# Шкала состояния ВПП
# --------------------------------------------------------------------------- #

def test_bench_codes_map_to_a_monotone_slipperiness_scale():
    """Коды стенда не упорядочены по скользкости: ICE=2 стоит между WET=1 и FLOODED=3.

    Подать код в сеть как число значило бы сообщить ей неверное отношение порядка — лёд
    оказался бы «менее скользким», чем лужи.
    """
    dry = runway_condition_from_bench(0).value
    wet = runway_condition_from_bench(1).value
    ice = runway_condition_from_bench(2).value
    flooded = runway_condition_from_bench(3).value

    assert dry < wet < flooded < ice          # порядок по скользкости, а не по коду
    assert ice > flooded                      # ...в отличие от порядка кодов (2 < 3)


def test_every_documented_bench_code_is_mapped():
    """ICD перечисляет ровно семь состояний — незакрытый код молча стал бы «льдом»."""
    assert set(BENCH_RUNWAY_CONDITION) == set(range(7))


def test_unknown_bench_code_is_treated_as_slippery():
    """Предположить сухую полосу — разрешить максимальное торможение там, где оно сорвёт ВС."""
    assert runway_condition_from_bench(99) is RunwayCondition.ICY
    assert runway_condition_from_bench(-1) is RunwayCondition.ICY


# --------------------------------------------------------------------------- #
# Сериализация и пресеты условий
# --------------------------------------------------------------------------- #

def test_weather_roundtrips_through_dict():
    for ws in WEATHER_PRESETS.values():
        assert WeatherState.from_dict(ws.to_dict()) == ws


def test_presets_cover_the_tz_conditions():
    # Аквапланирование и низкое сцепление — отдельные пункты ТЗ 5.1.3.1.
    assert WEATHER_PRESETS["puddly"].runway_friction == RunwayCondition.PUDDLY.value
    assert WEATHER_PRESETS["icy"].runway_friction == RunwayCondition.ICY.value
    assert WEATHER_PRESETS["crosswind"].wind_speed_kts > 0.0
    assert WEATHER_PRESETS["clear_dry"].runway_friction == RunwayCondition.DRY.value
