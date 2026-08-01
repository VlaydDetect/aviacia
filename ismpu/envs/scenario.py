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

from collections.abc import Iterable, Sequence
from dataclasses import asdict, dataclass, field
from typing import TYPE_CHECKING, Any

from ismpu.control.failures import FailureMode
from ismpu.config.scenarios import ScenarioConfig, SCENARIOS
from ismpu.config.constants import INITIAL_SPEED_KTS
from ismpu.envs.weather import WeatherState, decompose_wind
from ismpu.config.runway import RWY_HEADING_TRUE

if TYPE_CHECKING:
    from ismpu.control.system import ControllingSystem
    from ismpu.envs.ics_sim import Telemetry

# Стандартные условия пресетов: ясно, штиль, ВПП сухая (WeatherState() по умолчанию).
STANDARD_WEATHER = WeatherState()


@dataclass(frozen=True)
class ApproachSetup:
    """Начальные условия захода X-Plane на продолжении оси и глиссады."""

    radio_altitude_ft: float = 2800.0
    ias_knots: float = 150.0
    vertical_speed_fpm: float = -750.0
    glideslope_deg: float = 3.0
    flap_ratio: float = 0.75
    lateral_offset_m: float = 0.0
    heading_offset_deg: float = 0.0
    loc_offset_dots: float = 0.0
    gs_offset_dots: float = 0.0


@dataclass(frozen=True)
class TouchdownSetup:
    """Начальные условия быстрого старта непосредственно с пробега."""

    speed_knots: float = INITIAL_SPEED_KTS
    descent_rate_fpm: float = 0.0
    pitch_deg: float = 0.0
    lateral_offset_m: float = 0.0
    heading_offset_deg: float = 0.0
    elevation_m: float = 1.5


@dataclass(frozen=True)
class SensorNoise:
    pos_sigma_m: float = 0.0
    heading_sigma_deg: float = 0.0
    speed_sigma_ms: float = 0.0
    dropout_prob: float = 0.0


@dataclass(frozen=True)
class Scenario:
    """Полное описание эпизода: коэффициенты + условия, под которые они калиброваны."""
    scenario_id: str
    seed: int
    control: ScenarioConfig                                    # классические коэффициенты (config.scenarios)
    weather: WeatherState = field(default_factory=lambda: STANDARD_WEATHER)
    failures: tuple[FailureMode, ...] = ()
    approach: ApproachSetup = field(default_factory=ApproachSetup)
    touchdown: TouchdownSetup = field(default_factory=TouchdownSetup)
    sensor_noise: SensorNoise = field(default_factory=SensorNoise)

    @property
    def primary_failure(self) -> FailureMode:
        return self.failures[0] if self.failures else FailureMode.NONE

    def apply_control(self, controller: "ControllingSystem") -> "ControllingSystem":
        """Настраивает контур классическими коэффициентами (PID + отказ пресета).

        Отказ пресета — лишь стартовое предположение: на стенде фактическую конфигурацию
        сообщает борт, и контур переопределяет её по телеметрии на каждом такте
        (`ControllingSystem.sync_failures`).
        """
        return self.control.apply(controller)

    @property
    def matrix_code(self) -> str:
        """Шифр матрицы прогонов, если сценарий заведён под неё («Б.3.1»), иначе пустая строка."""
        return self.control.matrix_code

    @classmethod
    def from_preset(cls, name: str, *, weather: WeatherState | None = None,
                    failures: Iterable[FailureMode] | None = None,
                    approach: ApproachSetup | None = None,
                    touchdown: TouchdownSetup | None = None,
                    sensor_noise: SensorNoise | None = None,
                    scenario_id: str | None = None, seed: int = 0) -> "Scenario":
        """Готовый сценарий из пресета `config.scenarios.SCENARIOS[name]`."""
        control = SCENARIOS[name]
        if failures is None:
            failures = (control.failure,) if control.failure is not FailureMode.NONE else ()

        if weather is None:
            weather = control.weather if control.weather is not None else STANDARD_WEATHER

        return cls(
            scenario_id=scenario_id or name,
            seed=seed,
            control=control,
            weather=weather,
            failures=tuple(failures),
            approach=approach or ApproachSetup(),
            touchdown=touchdown or TouchdownSetup(),
            sensor_noise=sensor_noise or SensorNoise(),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "seed": self.seed,
            "control": self.control.name,   # канонический ключ SCENARIOS
            "weather": self.weather.to_dict(),
            "failures": [f.name for f in self.failures],
            "approach": asdict(self.approach),
            "touchdown": asdict(self.touchdown),
            "sensor_noise": asdict(self.sensor_noise),
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Scenario":
        return cls(
            scenario_id=d["scenario_id"],
            seed=d["seed"],
            control=SCENARIOS[d["control"]],
            weather=WeatherState.from_dict(d["weather"]),
            failures=tuple(FailureMode[name] for name in d.get("failures", [])),
            approach=ApproachSetup(**d.get("approach", {})),
            touchdown=TouchdownSetup(**d.get("touchdown", {})),
            sensor_noise=SensorNoise(**d.get("sensor_noise", {})),
        )


# Готовые к запуску пресеты: те же имена, что в config.scenarios.SCENARIOS,
# но уже с условиями, под которые пресет калибровался.
SCENARIO_PRESETS: dict[str, Scenario] = {name: Scenario.from_preset(name) for name in SCENARIOS}


def resolve_preset(key: str) -> Scenario:
    """Сценарий по имени пресета **или** по шифру матрицы прогонов («Б.3.1», «б.3.1», «a_1_1»).

    Шифр — это то, чем оперирует таблица Заказчика и исполнитель за пультом стенда; требовать от
    него мысленного перевода в имя переменной значит напрашиваться на запуск не того прогона.
    Регистр и раскладка («Б» кириллическая, «A» латинская) не различаются: в шифрах матрицы
    буквы кириллические, и промах по раскладке иначе выглядел бы как несуществующий пресет.
    """
    from ismpu.config.run_matrix import CASE_BY_CODE

    if key in SCENARIO_PRESETS:
        return SCENARIO_PRESETS[key]

    normalized = key.strip().upper().replace("A", "А").replace("B", "Б")
    for code, case in CASE_BY_CODE.items():
        if code.upper() == normalized and case.preset in SCENARIO_PRESETS:
            return SCENARIO_PRESETS[case.preset]

    known = ", ".join(sorted(SCENARIO_PRESETS))
    raise KeyError(f"неизвестный пресет или шифр матрицы: {key!r}. Известны: {known}")


def matrix_battery(segment: str | None = None) -> tuple[Scenario, ...]:
    """Сценарии матрицы прогонов в порядке таблицы. → кортеж `Scenario`.

    Порядок не косметика: матрица предписывает идти сверху вниз, потому что внутри шифра условия
    усложняются, а настройка предыдущего прогона служит начальным приближением следующего.

    Шифры захода (`segment="approach"`) сюда попадают только если под них заведён наземный
    пресет: воздушные коэффициенты живут отдельно (`config/approach.py`) и сценарием пробега не
    описываются.
    """
    from ismpu.config.run_matrix import RUN_MATRIX

    return tuple(SCENARIO_PRESETS[c.preset] for c in RUN_MATRIX
                 if c.preset in SCENARIO_PRESETS
                 and (segment is None or c.segment == segment))


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


def scenario_distance(
    scenario: Scenario,
    failures: Iterable[FailureMode],
    weather: WeatherState | None = None,
) -> float:
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


def select_scenario(
    failures: Iterable[FailureMode] = (),
    weather: WeatherState | None = None,
    *,
    scenarios: Sequence[Scenario] | None = None,
    include_draft: bool = False,
) -> Scenario:
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


def select_for_telemetry(
    telemetry: "Telemetry | None",
    *,
    scenarios: Sequence[Scenario] | None = None,
    include_draft: bool = False,
) -> Scenario:
    """Подбор по кадру телеметрии стенда (отказы и погода берутся из `ICSInputs`).

    При невалидном кадре подбирать не по чему — возвращается штатный пресет: он единственный
    безопасен, когда о конфигурации борта ничего не известно.
    """
    if telemetry is None or not telemetry.valid:
        return SCENARIO_PRESETS["default"]
    return select_scenario(telemetry.faults, telemetry.weather,
                           scenarios=scenarios, include_draft=include_draft)
