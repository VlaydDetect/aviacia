"""Описатель сценария эпизода — сериализуемое, воспроизводимое состояние среды.

`Scenario` собирает всё, что определяет один эпизод посадки/пробега: начальные
условия касания, погоду (`WeatherState`), набор отказов и параметры шума датчиков,
плюс ключ пресета классических коэффициентов (`control_preset`). Генерируется
`ScenarioGenerator` (domain randomization) и применяется к среде через
`SimInterface.reset(scenario)`.

Сериализация (`to_dict`/`from_dict`) нужна для приёмочной батареи (Этап 5): каждый
прогон логируется и точно воспроизводится.
"""

from dataclasses import dataclass, asdict, field

from ismpu.control.failures import FailureMode
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


@dataclass(frozen=True)
class Scenario:
    """Полное описание эпизода. Неизменяемое и сериализуемое."""
    scenario_id: str
    seed: int
    control_preset: str                       # ключ в config.scenarios.SCENARIOS (базовые PID)
    weather: WeatherState = field(default_factory=WeatherState)
    failures: tuple[FailureMode, ...] = ()
    touchdown: TouchdownSetup = field(default_factory=TouchdownSetup)
    sensor_noise: SensorNoise = field(default_factory=SensorNoise)

    @property
    def primary_failure(self) -> FailureMode:
        return self.failures[0] if self.failures else FailureMode.NONE

    def to_dict(self) -> dict:
        return {
            "scenario_id": self.scenario_id,
            "seed": self.seed,
            "control_preset": self.control_preset,
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
            control_preset=d["control_preset"],
            weather=WeatherState.from_dict(d["weather"]),
            failures=tuple(FailureMode[name] for name in d.get("failures", [])),
            touchdown=TouchdownSetup(**d.get("touchdown", {})),
            sensor_noise=SensorNoise(**d.get("sensor_noise", {})),
        )
