"""Единый описатель сценария эпизода — управление + среда в одном объекте.

`Scenario` собирает ВСЕ настройки эпизода посадки/пробега в одном месте:
- `control` — классические коэффициенты (`ScenarioConfig` из `config.scenarios`,
  PID/guidance/закон скорости + связанный отказ); значения пресетов не меняются;
- `weather` — погода (`WeatherState`); по умолчанию — стандарт: ясно, штиль, сухо;
- `failures` — активные отказы эпизода;
- `touchdown` / `sensor_noise` — начальные условия касания и шум датчиков.

Так устраняется прежний разрыв: и генератор, и цикл управления оперируют одним
типом `Scenario`. Готовые пресеты — `SCENARIO_PRESETS` (те же имена, что и в
`config.scenarios.SCENARIOS`, но уже с погодой и НУ) — выбираются циклом по имени.

Сериализация (`to_dict`/`from_dict`) хранит `control` по имени пресета (канонический
ключ `config.scenarios.SCENARIOS`), погоду — как словарь; нужна для воспроизводимой
приёмочной батареи (Этап 5).
"""

from dataclasses import dataclass, asdict, field

from ismpu.control.failures import FailureMode
from ismpu.config.scenarios import ScenarioConfig, SCENARIOS
from ismpu.config.aircraft import A330_SETUP
from ismpu.envs.weather import WeatherState


@dataclass(frozen=True)
class TouchdownSetup:
    """Начальные условия касания (для рандомизации НУ, ось §8)."""
    speed_knots: float = 140.0
    descent_rate_fpm: float = 120.0
    pitch_deg: float = 0.0
    lateral_offset_m: float = 0.0      # смещение от оси ВПП; > 0 — правее
    heading_offset_deg: float = 0.0    # отклонение курса от курса ВПП


@dataclass(frozen=True)
class SensorNoise:
    """Параметры шума телеметрии (применяется при сборке Observation, Этап 2)."""
    pos_sigma_m: float = 0.0           # СКО позиционного шума (→ cross-track), м
    heading_sigma_deg: float = 0.0     # СКО шума курса, °
    speed_sigma_ms: float = 0.0        # СКО шума путевой скорости, м/с
    dropout_prob: float = 0.0          # вероятность выпадения отсчёта [0..1]


# Стандартная погода пресетов: ясно, штиль, ВПП сухая (WeatherState() по умолчанию).
STANDARD_WEATHER = WeatherState()
# НУ касания как в текущем цикле (A330: 200 узлов), чтобы поведение не менялось.
_STANDARD_TOUCHDOWN = TouchdownSetup(**A330_SETUP)


@dataclass(frozen=True)
class Scenario:
    """Полное описание эпизода: управление + среда. Неизменяемое и сериализуемое."""
    scenario_id: str
    seed: int
    control: ScenarioConfig                                    # классические коэффициенты (config.scenarios)
    weather: WeatherState = field(default_factory=lambda: STANDARD_WEATHER)
    failures: tuple[FailureMode, ...] = ()
    touchdown: TouchdownSetup = field(default_factory=lambda: _STANDARD_TOUCHDOWN)
    sensor_noise: SensorNoise = field(default_factory=SensorNoise)

    @property
    def primary_failure(self) -> FailureMode:
        return self.failures[0] if self.failures else FailureMode.NONE

    def apply_control(self, controller):
        """Настраивает контур классическими коэффициентами (PID + активация отказа пресета)."""
        return self.control.apply(controller)

    @classmethod
    def from_preset(cls, name: str, *, weather: WeatherState | None = None,
                    failures: tuple | None = None, touchdown: TouchdownSetup | None = None,
                    sensor_noise: SensorNoise | None = None,
                    scenario_id: str | None = None, seed: int = 0) -> "Scenario":
        """Готовый сценарий из пресета `config.scenarios.SCENARIOS[name]` + стандартная погода."""
        control = SCENARIOS[name]
        if failures is None:
            failures = (control.failure,) if control.failure is not FailureMode.NONE else ()

        if weather is None:
            weather = control.weather if control.weather is not None else STANDARD_WEATHER

        return cls(
            scenario_id=scenario_id or name, seed=seed, control=control,
            weather=weather,
            failures=tuple(failures),
            touchdown=touchdown if touchdown is not None else _STANDARD_TOUCHDOWN,
            sensor_noise=sensor_noise if sensor_noise is not None else SensorNoise(),
        )

    def to_dict(self) -> dict:
        return {
            "scenario_id": self.scenario_id,
            "seed": self.seed,
            "control": self.control.name,   # канонический ключ SCENARIOS
            "weather": self.weather.to_dict(),
            "failures": [f.name for f in self.failures],
            "touchdown": asdict(self.touchdown),
            "sensor_noise": asdict(self.sensor_noise),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Scenario":
        return cls(
            scenario_id=d["scenario_id"],
            seed=d["seed"],
            control=SCENARIOS[d["control"]],
            weather=WeatherState.from_dict(d["weather"]),
            failures=tuple(FailureMode[name] for name in d.get("failures", [])),
            touchdown=TouchdownSetup(**d.get("touchdown", {})),
            sensor_noise=SensorNoise(**d.get("sensor_noise", {})),
        )


# Готовые к запуску пресеты: те же имена, что в config.scenarios.SCENARIOS,
# но уже с полной средой (стандартная погода: ясно/штиль/сухо).
SCENARIO_PRESETS: dict[str, Scenario] = {name: Scenario.from_preset(name) for name in SCENARIOS}
