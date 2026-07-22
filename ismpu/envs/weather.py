"""Погодные условия эпизода: описание, шкала сцепления и разбор ветра.

Модуль **не задаёт** погоду — на стенде заказчика её задаёт Заказчик, а нам она приходит
телеметрией (`ICSInputs`: `WindSpeed`, `WindDirectionTrue`, `RunwayCondition`,
`PrecipitationRatio`, `Visibility`, `AirfieldTemp`). Поэтому здесь остались только:

* `WeatherState` — описание условий. Два применения: (1) `WeatherState.from_ics` строит его из
  пакета стенда для признаков наблюдения и диагностики; (2) в `Scenario` он описывает условия,
  под которые откалиброван пресет, — по нему сценарий и подбирается под фактическую погоду.
* `RunwayCondition` — наша **монотонная шкала скользкости** ВПП и перевод в неё кода стенда.
* `decompose_wind` / `compose_wind` — ветер ↔ (боковая, встречная) составляющие относительно ВПП.

Единицы `WeatherState`: ветер в узлах (как в ТЗ и как шлёт стенд), направление «откуда дует»
в ° от истинного севера, видимость в метрах, температура в °C.
"""

import math
from enum import Enum
from dataclasses import dataclass

from ismpu.utils.converts import Converts
from ismpu.config.runway import RWY_HEADING_TRUE


class RunwayCondition(Enum):
    """Состояние ВПП как **монотонная шкала скользкости** 0…15 (0 — сухо, 15 — лёд со снегом).

    Стенд сообщает состояние ВПП перечислением из семи значений (`ICSInputs.RunwayCondition`,
    коды 0…6), и порядок этих кодов **не** отражает скользкость: ICE=2 стоит между WET=1 и
    FLOODED=3, хотя лёд — худший случай из всех. Подать такой код в сеть как число значило бы
    сообщить ей неверное отношение порядка. Поэтому код переводится в эту шкалу
    (`runway_condition_from_bench`), а нормируется уже она (`normalization.FRICTION_SCALE`).

    Значения — середины диапазонов: сухо 0, мокро 1–3, лужи/аквапланирование 4–6, снег 7–9,
    лёд 10–12, снег со льдом 13–15.
    """
    DRY = 0.0
    WET = 2.0
    PUDDLY = 5.0       # риск аквапланирования (ТЗ 5.1.3.1)
    SNOWY = 8.0
    ICY = 11.0
    SNOWY_ICY = 14.0


BENCH_RUNWAY_CONDITION = {
    0: RunwayCondition.DRY,        # DRY
    1: RunwayCondition.WET,        # WET
    2: RunwayCondition.ICY,        # ICE
    3: RunwayCondition.PUDDLY,     # FLOODED
    4: RunwayCondition.WET,        # WET RUBBER
    5: RunwayCondition.SNOWY,      # SNOW
    6: RunwayCondition.PUDDLY,     # SLUSH
}
"""Код `ICSInputs.RunwayCondition` (0…6) → наша шкала скользкости.

FLOODED и SLUSH сведены к PUDDLY: обе означают слой воды/шуги, то есть риск аквапланирования;
WET RUBBER — мокрое покрытие с резиновым загрязнением, по сцеплению ближе к WET."""


def runway_condition_from_bench(code: int) -> RunwayCondition:
    """Код состояния ВПП со стенда → наша шкала.

    Неизвестный код трактуется как `ICY`, а не `DRY`: при неизвестном сцеплении вести себя надо
    консервативно. Предположить сухую полосу — значит разрешить максимальное торможение там, где
    оно может сорвать ВС с оси.
    """
    return BENCH_RUNWAY_CONDITION.get(int(code), RunwayCondition.ICY)


@dataclass(frozen=True)
class WeatherState:
    """Погодные условия. Поля — ровно то, что сообщает стенд (см. `from_ics`).

    Неизменяемое: это описание условий, а не рычаг управления средой. Менять погоду на стенде
    мы не можем — только читать её и подбирать под неё пресет.
    """
    wind_speed_kts: float = 0.0
    wind_dir_from_degt: float = 0.0     # откуда дует, ° от истинного севера

    runway_friction: float = RunwayCondition.DRY.value  # 0..15, см. RunwayCondition

    rain_pct: float = 0.0               # 0..1, интенсивность осадков
    visibility_m: float = 16000.0       # ~10 миль (ясно)
    temperature_c: float = 15.0

    @classmethod
    def from_ics(cls, inp) -> "WeatherState":
        """`ICSInputs` → `WeatherState`. Единственный источник фактической погоды.

        Стенд шлёт ветер в узлах, видимость — в **футах**; перевод видимости здесь не косметика:
        16000 футов, положенные в поле метров, дали бы «ясно» там, где видимость 4.9 км.
        """
        return cls(
            wind_speed_kts=inp.WindSpeed,
            wind_dir_from_degt=inp.WindDirectionTrue,
            runway_friction=float(runway_condition_from_bench(inp.RunwayCondition).value),
            rain_pct=inp.PrecipitationRatio,
            visibility_m=inp.Visibility * Converts.FT_TO_M,   # ft → м
            temperature_c=inp.AirfieldTemp,
        )

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
            "runway_friction": self.runway_friction,
            "rain_pct": self.rain_pct,
            "visibility_m": self.visibility_m,
            "temperature_c": self.temperature_c,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "WeatherState":
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


# --------------------------------------------------------------------------- #
# Пресеты условий — «под что откалиброван сценарий» (см. envs/scenario.py)
# --------------------------------------------------------------------------- #

CLEAR_DRY = WeatherState()

WET = WeatherState(runway_friction=RunwayCondition.WET.value, rain_pct=0.4, visibility_m=8000.0)

PUDDLY_AQUAPLANING = WeatherState(runway_friction=RunwayCondition.PUDDLY.value, rain_pct=0.8,
                                  visibility_m=4000.0)

ICY = WeatherState(runway_friction=RunwayCondition.ICY.value, temperature_c=-8.0, visibility_m=6000.0)

SNOWY = WeatherState(runway_friction=RunwayCondition.SNOWY.value, temperature_c=-3.0,
                     visibility_m=3000.0)

STRONG_CROSSWIND = WeatherState.from_crosswind(crosswind_kts=10.0, headwind_kts=5.0)

LOW_VISIBILITY = WeatherState(visibility_m=800.0, rain_pct=0.3)

WEATHER_PRESETS: dict[str, WeatherState] = {
    "clear_dry": CLEAR_DRY,
    "wet": WET,
    "puddly": PUDDLY_AQUAPLANING,
    "icy": ICY,
    "snowy": SNOWY,
    "crosswind": STRONG_CROSSWIND,
    "low_visibility": LOW_VISIBILITY,
}
