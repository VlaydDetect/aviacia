"""Единый описатель сценария эпизода и подбор сценария под фактические условия.

`Scenario` собирает всё, что отличает один пробег от другого:

- `control` — классические коэффициенты (`ScenarioConfig` из `config.scenarios`: PID/guidance/
  закон скорости); значения пресетов не меняются;
- `failures` — отказы, под которые пресет откалиброван;
- `weather` — условия, под которые пресет откалиброван (`WeatherState`).

**Сценарий ничего не устанавливает.** Средой на стенде распоряжается Заказчик: и погода, и
отказы приходят телеметрией (`ICSInputs`). Поэтому `weather`/`failures` здесь — не задание, а
**признаки для подбора**: `select_scenario(...)` берёт фактические условия со стенда и выбирает
пресет, который под них калибровался. Настраивает контур только `apply_control`.

Сериализация (`to_dict`/`from_dict`) хранит `control` по имени пресета (канонический ключ
`config.scenarios.SCENARIOS`), погоду — как словарь; нужна для воспроизводимой приёмочной
батареи.
"""

from dataclasses import dataclass, field

from ismpu.control.failures import FailureMode
from ismpu.config.scenarios import ScenarioConfig, SCENARIOS
from ismpu.envs.weather import WeatherState, decompose_wind
from ismpu.config.runway import RWY_HEADING_TRUE

# Стандартные условия пресетов: ясно, штиль, ВПП сухая (WeatherState() по умолчанию).
STANDARD_WEATHER = WeatherState()


@dataclass(frozen=True)
class Scenario:
    """Полное описание эпизода: коэффициенты + условия, под которые они калиброваны."""
    scenario_id: str
    seed: int
    control: ScenarioConfig                                    # классические коэффициенты (config.scenarios)
    weather: WeatherState = field(default_factory=lambda: STANDARD_WEATHER)
    failures: tuple[FailureMode, ...] = ()

    @property
    def primary_failure(self) -> FailureMode:
        return self.failures[0] if self.failures else FailureMode.NONE

    def apply_control(self, controller):
        """Настраивает контур классическими коэффициентами (PID + отказ пресета).

        Отказ пресета — лишь стартовое предположение: на стенде фактическую конфигурацию
        сообщает борт, и контур переопределяет её по телеметрии на каждом такте
        (`ControllingSystem.sync_failures`).
        """
        return self.control.apply(controller)

    @classmethod
    def from_preset(cls, name: str, *, weather: WeatherState | None = None,
                    failures: tuple | None = None,
                    scenario_id: str | None = None, seed: int = 0) -> "Scenario":
        """Готовый сценарий из пресета `config.scenarios.SCENARIOS[name]`."""
        control = SCENARIOS[name]
        if failures is None:
            failures = (control.failure,) if control.failure is not FailureMode.NONE else ()

        if weather is None:
            weather = control.weather if control.weather is not None else STANDARD_WEATHER

        return cls(scenario_id=scenario_id or name, seed=seed, control=control,
                   weather=weather, failures=tuple(failures))

    def to_dict(self) -> dict:
        return {
            "scenario_id": self.scenario_id,
            "seed": self.seed,
            "control": self.control.name,   # канонический ключ SCENARIOS
            "weather": self.weather.to_dict(),
            "failures": [f.name for f in self.failures],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Scenario":
        return cls(
            scenario_id=d["scenario_id"],
            seed=d["seed"],
            control=SCENARIOS[d["control"]],
            weather=WeatherState.from_dict(d["weather"]),
            failures=tuple(FailureMode[name] for name in d.get("failures", [])),
        )


# Готовые к запуску пресеты: те же имена, что в config.scenarios.SCENARIOS,
# но уже с условиями, под которые пресет калибровался.
SCENARIO_PRESETS: dict[str, Scenario] = {name: Scenario.from_preset(name) for name in SCENARIOS}


# --------------------------------------------------------------------------- #
# Подбор сценария под фактические условия стенда
# --------------------------------------------------------------------------- #

FAILURE_MISMATCH_PENALTY = 100.0
"""Штраф за каждый несовпавший отказ. На порядок больше любого погодного расхождения: пресет,
откалиброванный под отказ NWS, в штатной конфигурации ведёт себя иначе, чем нужно, и никакая
близость по погоде этого не компенсирует."""

_FRICTION_SCALE = 15.0      # шкала RunwayCondition (0…15)
_WIND_SCALE = 20.0          # узлы; типичный предел бокового ветра
_VISIBILITY_SCALE = 16000.0  # метры


def weather_distance(a: WeatherState, b: WeatherState,
                     runway_heading_degt: float = RWY_HEADING_TRUE) -> float:
    """Насколько условия `a` далеки от `b` (0 — совпадают). Безразмерная сумма.

    Ветер сравнивается **по составляющим относительно ВПП**, а не по скорости с направлением:
    для пробега существенна боковая составляющая, и 10 узлов сбоку — это совсем не то же, что
    10 узлов в лоб, хотя «скорость ветра» у них одинаковая.
    """
    cross_a, head_a = decompose_wind(a.wind_speed_kts, a.wind_dir_from_degt, runway_heading_degt)
    cross_b, head_b = decompose_wind(b.wind_speed_kts, b.wind_dir_from_degt, runway_heading_degt)
    return (
        abs(a.runway_friction - b.runway_friction) / _FRICTION_SCALE
        + abs(cross_a - cross_b) / _WIND_SCALE
        + 0.5 * abs(head_a - head_b) / _WIND_SCALE
        + abs(a.rain_pct - b.rain_pct)
        + 0.5 * abs(a.visibility_m - b.visibility_m) / _VISIBILITY_SCALE
    )


def scenario_distance(scenario: Scenario, failures, weather: WeatherState | None = None) -> float:
    """Насколько сценарий не подходит под фактические условия (0 — точное совпадение).

    Отказы сравниваются симметрической разностью: одинаково плохо и тюнинговать под отказ,
    которого нет, и не учесть отказ, который есть.
    """
    observed = frozenset(failures or ())
    mismatch = observed.symmetric_difference(scenario.failures)
    score = FAILURE_MISMATCH_PENALTY * len(mismatch)
    if weather is not None:
        score += weather_distance(scenario.weather, weather)
    return score


def select_scenario(failures=(), weather: WeatherState | None = None, *,
                    scenarios=None, include_draft: bool = False) -> Scenario:
    """Подобрать сценарий под фактические условия стенда.

    Черновые пресеты (`ScenarioConfig.draft`) по умолчанию не рассматриваются: они не выверены,
    и молча выбрать такой значило бы вести пробег на непроверенных коэффициентах.
    """
    pool = list(scenarios if scenarios is not None else SCENARIO_PRESETS.values())
    if not include_draft:
        pool = [s for s in pool if not s.control.draft] or pool
    if not pool:
        raise ValueError("нет сценариев для подбора")
    return min(pool, key=lambda s: (scenario_distance(s, failures, weather), s.scenario_id))


def select_for_telemetry(telemetry, *, scenarios=None, include_draft: bool = False) -> Scenario:
    """Подбор по кадру телеметрии стенда (отказы и погода берутся из `ICSInputs`).

    При невалидном кадре подбирать не по чему — возвращается штатный пресет: он единственный
    безопасен, когда о конфигурации борта ничего не известно.
    """
    if telemetry is None or not telemetry.valid:
        return SCENARIO_PRESETS["default"]
    return select_scenario(telemetry.faults, telemetry.weather,
                           scenarios=scenarios, include_draft=include_draft)
