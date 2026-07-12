"""Тесты системы управления погодой (симулятор-независимые, через MockXPC)."""

import math

import pytest

from ismpu.envs.weather import (
    WeatherManager, WeatherState, RunwayCondition, ChangeMode, FrictionProfile,
    decompose_wind, compose_wind, WEATHER_PRESETS,
)
from ismpu.config.runway import RWY_HEADING_TRUE
from ismpu.io.datarefs import (
    WX_CHANGE_MODE, WX_UPDATE_IMMEDIATELY, WX_RUNWAY_FRICTION, WX_RAIN_PERCENT,
    WX_VISIBILITY_SM, WX_VARIABILITY_PCT, WX_SEALEVEL_TEMP_C, WX_N_LAYERS,
    WX_WIND_SPEED_MSC, WX_WIND_DIR_DEGT, WX_SHEAR_SPEED_MSC, WX_TURBULENCE,
    WX_AC_WIND_SPEED_MSC, WX_AC_WIND_DIR_DEGT,
)
from ismpu.utils.converts import Converts


class MockXPC:
    def __init__(self, dref_values: dict | None = None):
        self.sent: list[tuple[str, float]] = []
        self._dref_values = dref_values or {}

    def sendDREF(self, dref, value):
        self.sent.append((dref, value))

    def getDREF(self, dref):
        return self._dref_values.get(dref, 0.0)

    def last(self, dref):
        """Последнее записанное значение датарефа."""
        for d, v in reversed(self.sent):
            if d == dref:
                return v
        raise KeyError(dref)


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
    ws = WeatherState.from_crosswind(crosswind_kts=10.0, headwind_kts=0.0, gust_kts=5.0)
    assert ws.wind_speed_kts == pytest.approx(10.0)
    assert ws.wind_dir_from_degt == pytest.approx((RWY_HEADING_TRUE + 90.0) % 360.0)
    assert ws.gust_kts == 5.0


# --------------------------------------------------------------------------- #
# Применение погоды в симулятор
# --------------------------------------------------------------------------- #

def test_apply_writes_mode_and_scalars():
    mock = MockXPC()
    ws = WeatherState(runway_friction=RunwayCondition.WET.value, rain_pct=0.4,
                      visibility_m=8000.0, variability_pct=0.5, temperature_c=3.0)
    WeatherManager(mock).apply(ws)

    assert mock.last(WX_CHANGE_MODE) == pytest.approx(ChangeMode.STATIC.value)
    assert mock.last(WX_UPDATE_IMMEDIATELY) == 1.0  # применить немедленно
    assert mock.last(WX_RUNWAY_FRICTION) == pytest.approx(RunwayCondition.WET.value)
    assert mock.last(WX_RAIN_PERCENT) == pytest.approx(0.4)
    assert mock.last(WX_VARIABILITY_PCT) == pytest.approx(0.5)
    assert mock.last(WX_SEALEVEL_TEMP_C) == pytest.approx(3.0)
    # видимость: метры → статутные мили
    assert mock.last(WX_VISIBILITY_SM) == pytest.approx(8000.0 * Converts.M_TO_SM)


def test_apply_writes_all_wind_layers_in_ms():
    mock = MockXPC()
    ws = WeatherState.from_crosswind(crosswind_kts=20.0, headwind_kts=0.0, gust_kts=10.0, turbulence=4.0)
    WeatherManager(mock).apply(ws)

    expected_speed_ms = ws.wind_speed_kts * Converts.KTS_TO_MS
    expected_gust_ms = ws.gust_kts * Converts.KTS_TO_MS
    for i in range(WX_N_LAYERS):
        assert mock.last(f"{WX_WIND_SPEED_MSC}[{i}]") == pytest.approx(expected_speed_ms)
        assert mock.last(f"{WX_WIND_DIR_DEGT}[{i}]") == pytest.approx(ws.wind_dir_from_degt)
        assert mock.last(f"{WX_SHEAR_SPEED_MSC}[{i}]") == pytest.approx(expected_gust_ms)
        assert mock.last(f"{WX_TURBULENCE}[{i}]") == pytest.approx(4.0)


def test_reset_restores_clear_dry():
    mock = MockXPC()
    wm = WeatherManager(mock)
    wm.apply(WEATHER_PRESETS["icy"])
    wm.reset()
    assert mock.last(WX_RUNWAY_FRICTION) == pytest.approx(RunwayCondition.DRY.value)
    assert mock.last(WX_RAIN_PERCENT) == pytest.approx(0.0)
    assert mock.last(f"{WX_WIND_SPEED_MSC}[0]") == pytest.approx(0.0)


# --------------------------------------------------------------------------- #
# Переменное сцепление по дистанции
# --------------------------------------------------------------------------- #

def test_friction_profile_step_lookup():
    prof = FrictionProfile([(0.0, 0.0), (600.0, 11.0), (1200.0, 8.0)])
    assert prof.at(0.0) == 0.0
    assert prof.at(500.0) == 0.0
    assert prof.at(600.0) == 11.0
    assert prof.at(1000.0) == 11.0
    assert prof.at(1500.0) == 8.0


def test_friction_profile_sorts_unordered_segments():
    prof = FrictionProfile([(1200.0, 8.0), (0.0, 0.0), (600.0, 11.0)])
    assert prof.at(700.0) == 11.0


def test_update_resends_friction_only_on_change():
    mock = MockXPC()
    ws = WeatherState(friction_profile=FrictionProfile([(0.0, 0.0), (600.0, 11.0)]))
    wm = WeatherManager(mock)
    wm.apply(ws)  # стартовое сцепление = 0 (профиль в точке 0)

    def friction_writes():
        return [v for d, v in mock.sent if d == WX_RUNWAY_FRICTION]

    n_after_apply = len(friction_writes())
    wm.update(100.0)   # ещё сухо → без записи
    wm.update(500.0)   # ещё сухо → без записи
    assert len(friction_writes()) == n_after_apply
    wm.update(650.0)   # перешли на лёд → одна запись
    assert friction_writes()[-1] == pytest.approx(11.0)
    assert len(friction_writes()) == n_after_apply + 1
    wm.update(800.0)   # тот же уровень → без записи
    assert len(friction_writes()) == n_after_apply + 1


def test_update_noop_without_profile():
    mock = MockXPC()
    wm = WeatherManager(mock)
    wm.apply(WeatherState(runway_friction=RunwayCondition.WET.value))
    before = len(mock.sent)
    wm.update(500.0)
    assert len(mock.sent) == before  # профиля нет → ничего не дослали


# --------------------------------------------------------------------------- #
# Чтение фактического ветра
# --------------------------------------------------------------------------- #

def test_read_crosswind_from_effective_wind():
    # Ветер 10 м/с «откуда» = курс+90° → чистый боковой справа, ~19.4 узла.
    mock = MockXPC({
        WX_AC_WIND_SPEED_MSC: 10.0,
        WX_AC_WIND_DIR_DEGT: (RWY_HEADING_TRUE + 90.0) % 360.0,
    })
    cross, head = WeatherManager(mock).read_crosswind()
    assert cross == pytest.approx(10.0 * Converts.MS_TO_KTS, abs=1e-3)
    assert head == pytest.approx(0.0, abs=1e-6)
