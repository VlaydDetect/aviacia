"""Система управления погодой в X-Plane 12.

Автономный модуль (по образцу `FailureManager`): описывает состояние окружающей
среды `WeatherState` и применяет его в симулятор через `WeatherManager`, записывая
writable-DataRef'ы семейства `sim/weather/region/*` (см. `io/datarefs.py`). Служит
подводкой к системе сценариев (Этап 1): `scenario_generator` будет сэмплировать
`WeatherState` и передавать его сюда (ср. `SimInterface.apply_weather`).

Единицы: ветер/порывы задаём в узлах (как в ТЗ), в симулятор пишем в м/с.
Направление ветра — «откуда дует», ° от истинного севера по часовой стрелке
(как в X-Plane).

Ограничение X-Plane: сцепление задаётся ЕДИНСТВЕННЫМ глобальным `runway_friction`
(0..15), покрытие всей ВПП разом. Отдельного датарефа μ по координате нет. Поэтому
«переменное сцепление по длине ВПП» реализовано как профиль по дистанции
(`FrictionProfile`), который `WeatherManager.update(distance_m)` дописывает в
`runway_friction` по мере пробега.
"""

import math
from enum import Enum
from dataclasses import dataclass
from typing import Optional

from ismpu.io.xplane_connector import XPlaneConnectX
from ismpu.utils.converts import Converts
from ismpu.config.runway import RWY_HEADING_TRUE
from ismpu.io.datarefs import (
    WX_CHANGE_MODE, WX_UPDATE_IMMEDIATELY, WX_RUNWAY_FRICTION, WX_VARIABILITY_PCT,
    WX_RAIN_PERCENT, WX_VISIBILITY_SM, WX_SEALEVEL_TEMP_C,
    WX_WIND_SPEED_MSC, WX_WIND_DIR_DEGT, WX_SHEAR_SPEED_MSC, WX_SHEAR_DIR_DEGT,
    WX_TURBULENCE, WX_N_LAYERS, WX_AC_WIND_SPEED_MSC, WX_AC_WIND_DIR_DEGT,
)


class RunwayCondition(Enum):
    """Состояние ВПП как репрезентативный уровень `runway_friction` (0..15).

    Диапазоны X-Plane: Dry=0, wet 1-3, puddly 4-6 (аквапланирование), snowy 7-9,
    icy 10-12, snowy/icy 13-15. Значения — середины диапазонов; при желании можно
    задавать дробный `runway_friction` напрямую.
    """
    DRY = 0.0
    WET = 2.0
    PUDDLY = 5.0       # риск аквапланирования (ТЗ 5.1.3.1)
    SNOWY = 8.0
    ICY = 11.0
    SNOWY_ICY = 14.0


class ChangeMode(Enum):
    """`sim/weather/region/change_mode` — временной тренд погоды."""
    RAPIDLY_IMPROVING = 0
    IMPROVING = 1
    GRADUALLY_IMPROVING = 2
    STATIC = 3                 # по умолчанию: ручная статичная погода
    GRADUALLY_DETERIORATING = 4
    DETERIORATING = 5
    RAPIDLY_DETERIORATING = 6
    REAL_WEATHER = 7


@dataclass
class FrictionProfile:
    """Переменное сцепление по дистанции вдоль ВПП: ступенчатая функция.

    `segments` — список `(start_distance_m, friction)` от начала пробега; уровень
    держится до начала следующего сегмента. Первый сегмент задаёт стартовое
    сцепление (обычно `start=0`).
    """
    segments: list[tuple[float, float]]

    def __post_init__(self):
        # Сортируем по дистанции начала, чтобы `at()` был корректен при любом вводе.
        object.__setattr__(self, "segments", sorted(self.segments, key=lambda s: s[0]))

    def at(self, distance_m: float) -> float:
        value = self.segments[0][1]
        for start, friction in self.segments:
            if distance_m >= start:
                value = friction
            else:
                break
        return value

    def to_list(self) -> list[list[float]]:
        return [[float(s), float(f)] for s, f in self.segments]

    @classmethod
    def from_list(cls, data) -> "FrictionProfile":
        return cls([(float(s), float(f)) for s, f in data])


@dataclass
class WeatherState:
    """Полное описание погодных условий сценария (единицы: узлы, метры, °C)."""
    wind_speed_kts: float = 0.0
    wind_dir_from_degt: float = 0.0     # откуда дует, ° от истинного севера
    gust_kts: float = 0.0               # прирост порывов (shear), узлы
    turbulence: float = 0.0             # 0..10 — болтанка
    variability_pct: float = 0.0        # 0..1 — пространственная изменчивость

    runway_friction: float = RunwayCondition.DRY.value  # 0..15, база (см. RunwayCondition)
    friction_profile: Optional[FrictionProfile] = None  # переменное сцепление по дистанции

    rain_pct: float = 0.0               # 0..1
    visibility_m: float = 16000.0       # ~10 миль (ясно)
    temperature_c: float = 15.0
    change_mode: ChangeMode = ChangeMode.STATIC

    @classmethod
    def from_crosswind(cls, crosswind_kts: float, headwind_kts: float = 0.0,
                       runway_heading_degt: float = RWY_HEADING_TRUE, **kwargs) -> "WeatherState":
        """Собирает ветер из компонент относительно курса ВПП.

        `crosswind_kts` > 0 — ветер справа; `headwind_kts` > 0 — встречный.
        """
        speed, direction = compose_wind(crosswind_kts, headwind_kts, runway_heading_degt)
        return cls(wind_speed_kts=speed, wind_dir_from_degt=direction, **kwargs)

    def to_dict(self) -> dict:
        """Сериализация в примитивы (для логирования/воспроизводимости сценариев)."""
        return {
            "wind_speed_kts": self.wind_speed_kts,
            "wind_dir_from_degt": self.wind_dir_from_degt,
            "gust_kts": self.gust_kts,
            "turbulence": self.turbulence,
            "variability_pct": self.variability_pct,
            "runway_friction": self.runway_friction,
            "friction_profile": self.friction_profile.to_list() if self.friction_profile else None,
            "rain_pct": self.rain_pct,
            "visibility_m": self.visibility_m,
            "temperature_c": self.temperature_c,
            "change_mode": self.change_mode.value,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "WeatherState":
        d = dict(d)
        profile = d.get("friction_profile")
        d["friction_profile"] = FrictionProfile.from_list(profile) if profile else None
        d["change_mode"] = ChangeMode(d.get("change_mode", ChangeMode.STATIC.value))
        return cls(**d)


# --------------------------------------------------------------------------- #
# Разложение/сборка ветра относительно курса ВПП
# --------------------------------------------------------------------------- #

def decompose_wind(speed: float, dir_from_degt: float, runway_heading_degt: float) -> tuple[float, float]:
    """(скорость, откуда) → (crosswind, headwind) относительно курса ВПП.

    crosswind > 0 — справа; headwind > 0 — встречный. Единицы crosswind/headwind
    совпадают с единицами `speed`.
    """
    delta = math.radians(dir_from_degt - runway_heading_degt)
    headwind = speed * math.cos(delta)
    crosswind = speed * math.sin(delta)
    return crosswind, headwind


def compose_wind(crosswind: float, headwind: float, runway_heading_degt: float) -> tuple[float, float]:
    """(crosswind, headwind) → (скорость, откуда, °). Обратна `decompose_wind`."""
    speed = math.hypot(crosswind, headwind)
    direction = (runway_heading_degt + math.degrees(math.atan2(crosswind, headwind))) % 360.0
    return speed, direction


class WeatherManager:
    """Записывает `WeatherState` в X-Plane и ведёт переменное сцепление.

    Аналог `FailureManager`: создаётся с `xpc`, хранит текущее состояние,
    `apply()` конфигурирует симулятор разом, `update()` дописывает сцепление по
    дистанции, `reset()` возвращает ясную сухую погоду.
    """

    FRICTION_EPS = 1e-3  # порог, чтобы не спамить одинаковым сцеплением каждый такт

    def __init__(self, xpc: XPlaneConnectX):
        self.xpc = xpc
        self.state: Optional[WeatherState] = None
        self._last_friction: Optional[float] = None

    def apply(self, state: WeatherState) -> "WeatherManager":
        """Полностью конфигурирует погоду региона под `state` (немедленно)."""
        x = self.xpc

        # Режим: ручная (не real-weather) и применить сразу, а не через 60 с.
        x.sendDREF(WX_CHANGE_MODE, float(state.change_mode.value))
        x.sendDREF(WX_UPDATE_IMMEDIATELY, 1.0)

        # Ветер/сдвиг/турбулентность — одинаково по всем 13 слоям (нам важен приземный).
        speed_ms = state.wind_speed_kts * Converts.KTS_TO_MS
        gust_ms = state.gust_kts * Converts.KTS_TO_MS
        for i in range(WX_N_LAYERS):
            x.sendDREF(f"{WX_WIND_SPEED_MSC}[{i}]", speed_ms)
            x.sendDREF(f"{WX_WIND_DIR_DEGT}[{i}]", state.wind_dir_from_degt)
            x.sendDREF(f"{WX_SHEAR_SPEED_MSC}[{i}]", gust_ms)
            x.sendDREF(f"{WX_SHEAR_DIR_DEGT}[{i}]", state.wind_dir_from_degt)
            x.sendDREF(f"{WX_TURBULENCE}[{i}]", state.turbulence)

        # Сцепление: база или стартовая точка профиля.
        base_friction = state.friction_profile.at(0.0) if state.friction_profile else state.runway_friction
        x.sendDREF(WX_RUNWAY_FRICTION, float(base_friction))
        self._last_friction = base_friction

        # Прочее окружение.
        x.sendDREF(WX_VARIABILITY_PCT, state.variability_pct)
        x.sendDREF(WX_RAIN_PERCENT, state.rain_pct)
        x.sendDREF(WX_VISIBILITY_SM, state.visibility_m * Converts.M_TO_SM)
        x.sendDREF(WX_SEALEVEL_TEMP_C, state.temperature_c)

        self.state = state
        return self

    def update(self, distance_m: float) -> None:
        """Переменное сцепление: дописывает `runway_friction` по профилю (по дистанции).

        No-op, если профиль не задан или уровень не изменился. Вызывать из
        управляющего цикла с накопленной дистанцией пробега.
        """
        if self.state is None or self.state.friction_profile is None:
            return
        friction = self.state.friction_profile.at(distance_m)
        if self._last_friction is None or abs(friction - self._last_friction) > self.FRICTION_EPS:
            self.xpc.sendDREF(WX_RUNWAY_FRICTION, float(friction))
            self._last_friction = friction

    def reset(self) -> "WeatherManager":
        """Возвращает ясную сухую штилевую погоду."""
        return self.apply(WeatherState())

    def read_effective_wind(self) -> tuple[float, float]:
        """Фактический ветер у ЛА: (скорость, м/с; направление «откуда», °)."""
        speed = self.xpc.getDREF(WX_AC_WIND_SPEED_MSC)
        direction = self.xpc.getDREF(WX_AC_WIND_DIR_DEGT)
        return speed, direction

    def read_crosswind(self, runway_heading_degt: float = RWY_HEADING_TRUE) -> tuple[float, float]:
        """Фактические (crosswind, headwind) в узлах относительно курса ВПП."""
        speed_ms, direction = self.read_effective_wind()
        return decompose_wind(speed_ms * Converts.MS_TO_KTS, direction, runway_heading_degt)


# --------------------------------------------------------------------------- #
# Пресеты погоды (аналог config.scenarios.SCENARIOS) — сырьё для генератора
# --------------------------------------------------------------------------- #

CLEAR_DRY = WeatherState()

WET = WeatherState(runway_friction=RunwayCondition.WET.value, rain_pct=0.4, visibility_m=8000.0)

PUDDLY_AQUAPLANING = WeatherState(runway_friction=RunwayCondition.PUDDLY.value, rain_pct=0.8,
                                  visibility_m=4000.0)

ICY = WeatherState(runway_friction=RunwayCondition.ICY.value, temperature_c=-8.0, visibility_m=6000.0)

STRONG_CROSSWIND = WeatherState.from_crosswind(crosswind_kts=10.0, headwind_kts=5.0)

GUSTY_CROSSWIND = WeatherState.from_crosswind(crosswind_kts=10.0, headwind_kts=4.0,
                                              gust_kts=12.0, turbulence=5.0, variability_pct=0.6)

LOW_VISIBILITY = WeatherState(visibility_m=800.0, rain_pct=0.3)

# Переменное сцепление: сухо → лёд на середине → снег к концу пробега.
VARIABLE_FRICTION = WeatherState(
    friction_profile=FrictionProfile([
        (0.0, RunwayCondition.DRY.value),
        (600.0, RunwayCondition.ICY.value),
        (1200.0, RunwayCondition.SNOWY.value),
    ]),
    temperature_c=-3.0,
)

WEATHER_PRESETS: dict[str, WeatherState] = {
    "clear_dry": CLEAR_DRY,
    "wet": WET,
    "puddly": PUDDLY_AQUAPLANING,
    "icy": ICY,
    "crosswind": STRONG_CROSSWIND,
    "gusty_crosswind": GUSTY_CROSSWIND,
    "low_visibility": LOW_VISIBILITY,
    "variable_friction": VARIABLE_FRICTION,
}
