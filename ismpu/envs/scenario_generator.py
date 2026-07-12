"""Генератор сценариев обучения (domain randomization).

Сэмплирует `Scenario` из всего пространства признаков (§8 плана): состояние ВПП/μ,
ветер с боковой составляющей, порывы и турбулентность, дождь/видимость/температура,
отказы, шум датчиков и начальные условия касания. Параметр `difficulty ∈ [0, 1]`
задаёт учебный план (curriculum): чем выше, тем тяжелее и вероятнее возмущения.

Детерминизм: весь случайный выбор идёт через seeded `numpy.random.Generator`, поэтому
два генератора с одним seed дают идентичную последовательность (воспроизводимость,
Этап 5). `battery()` — фиксированный приёмочный набор (штат + отказы + погода).
"""

import numpy as np

from ismpu.control.failures import FailureMode
from ismpu.config.scenarios import SCENARIOS
from ismpu.envs.weather import WeatherState, RunwayCondition, FrictionProfile, WEATHER_PRESETS
from ismpu.envs.scenario import Scenario, TouchdownSetup, SensorNoise


# Пресеты классических коэффициентов под конкретный отказ (иначе — "default").
_PRESET_BY_FAILURE = {
    FailureMode.NWS_FAIL: "nws_fail",
    FailureMode.REVERSE_LEFT_FAIL: "left_reverse_fail",
    FailureMode.REVERSE_RIGHT_FAIL: "right_reverse_fail",
}

_FAILURE_POOL = [
    FailureMode.NWS_FAIL,
    FailureMode.REVERSE_LEFT_FAIL, FailureMode.REVERSE_RIGHT_FAIL,
    FailureMode.ENGINE_OUT_LEFT, FailureMode.ENGINE_OUT_RIGHT,
    FailureMode.THRUST_LEFT_DEGRADED, FailureMode.THRUST_RIGHT_DEGRADED,
    FailureMode.GEAR_CONFIG,
]

# Пары отказов, несовместимые в одном эпизоде (симметричные/бессмысленные вместе).
_CONTRADICTIONS = [
    {FailureMode.ENGINE_OUT_LEFT, FailureMode.ENGINE_OUT_RIGHT},
    {FailureMode.THRUST_LEFT_DEGRADED, FailureMode.THRUST_RIGHT_DEGRADED},
    {FailureMode.REVERSE_LEFT_FAIL, FailureMode.REVERSE_RIGHT_FAIL},
]

_CONDITIONS = [RunwayCondition.DRY, RunwayCondition.WET, RunwayCondition.PUDDLY,
               RunwayCondition.SNOWY, RunwayCondition.ICY]


class ScenarioGenerator:
    def __init__(self, seed: int = 0):
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        self._counter = 0

    # --- публичный API ---

    def sample(self, difficulty: float | None = None) -> Scenario:
        """Один случайный сценарий. `difficulty=None` → случайная сложность."""
        if difficulty is None:
            difficulty = float(self.rng.uniform(0.0, 1.0))
        d = float(np.clip(difficulty, 0.0, 1.0))

        weather = self._sample_weather(d)
        failures = self._sample_failures(d)
        touchdown = self._sample_touchdown(d)
        noise = self._sample_noise(d)
        preset = _PRESET_BY_FAILURE.get(failures[0], "default") if failures else "default"

        scenario_id = f"gen-{self.seed}-{self._counter:04d}"
        scenario_seed = int(self.rng.integers(0, 2 ** 31 - 1))
        self._counter += 1
        return Scenario(scenario_id=scenario_id, seed=scenario_seed, control=SCENARIOS[preset],
                        weather=weather, failures=failures, touchdown=touchdown, sensor_noise=noise)

    def battery(self) -> list[Scenario]:
        """Фиксированный приёмочный набор (детерминированный, без RNG)."""
        items: list[Scenario] = []

        def add(sid, preset, weather, failures=()):
            items.append(Scenario(scenario_id=sid, seed=0, control=SCENARIOS[preset],
                                  weather=weather, failures=tuple(failures)))

        # Штат + погода
        add("nominal", "default", WEATHER_PRESETS["clear_dry"])
        add("wet", "default", WEATHER_PRESETS["wet"])
        add("puddly", "default", WEATHER_PRESETS["puddly"])
        add("icy", "default", WEATHER_PRESETS["icy"])
        add("crosswind", "default", WEATHER_PRESETS["crosswind"])
        add("gusty_crosswind", "default", WEATHER_PRESETS["gusty_crosswind"])
        add("low_visibility", "default", WEATHER_PRESETS["low_visibility"])
        add("variable_friction", "default", WEATHER_PRESETS["variable_friction"])
        # Отказы
        add("nws_fail", "nws_fail", WEATHER_PRESETS["clear_dry"], (FailureMode.NWS_FAIL,))
        add("left_reverse_fail", "left_reverse_fail", WEATHER_PRESETS["wet"], (FailureMode.REVERSE_LEFT_FAIL,))
        add("right_reverse_fail", "right_reverse_fail", WEATHER_PRESETS["wet"], (FailureMode.REVERSE_RIGHT_FAIL,))
        add("engine_out_left", "default", WEATHER_PRESETS["clear_dry"], (FailureMode.ENGINE_OUT_LEFT,))
        # Комбинации отказ + тяжёлая погода
        add("nws_crosswind", "nws_fail", WEATHER_PRESETS["crosswind"], (FailureMode.NWS_FAIL,))
        add("nws_icy", "nws_fail", WEATHER_PRESETS["icy"], (FailureMode.NWS_FAIL,))
        return items

    # --- частные сэмплеры ---

    def _weighted_pick(self, items, weights):
        w = np.asarray(weights, dtype=float)
        w = w / w.sum()
        r = self.rng.random()
        cumulative = 0.0
        for item, wi in zip(items, w):
            cumulative += wi
            if r <= cumulative:
                return item
        return items[-1]

    def _sample_condition(self, d: float) -> RunwayCondition:
        # d=0 → почти всегда сухо; d=1 → чаще снег/лёд.
        weights = [
            1.0 - d,          # DRY
            0.5,              # WET
            0.3 + 0.3 * d,    # PUDDLY (аквапланирование)
            0.5 * d,          # SNOWY
            0.7 * d,          # ICY
        ]
        return self._weighted_pick(_CONDITIONS, weights)

    def _sample_weather(self, d: float) -> WeatherState:
        condition = self._sample_condition(d)

        # С ростом сложности — вероятность переменного сцепления по длине ВПП.
        if self.rng.random() < 0.2 * d:
            friction_kw = dict(friction_profile=FrictionProfile([
                (0.0, RunwayCondition.DRY.value),
                (float(self.rng.uniform(400.0, 800.0)), condition.value),
                (float(self.rng.uniform(1000.0, 1400.0)), min(15.0, condition.value + 3.0)),
            ]))
        else:
            friction_kw = dict(runway_friction=condition.value)

        crosswind = float(self.rng.uniform(-1.0, 1.0) * (3.0 + 20.0 * d))
        headwind = float(self.rng.uniform(-3.0, 10.0))
        gust = float(self.rng.uniform(0.0, 12.0 * d))
        turbulence = float(self.rng.uniform(0.0, 7.0 * d))
        variability = float(self.rng.uniform(0.0, 0.8 * d))

        wet = condition in (RunwayCondition.WET, RunwayCondition.PUDDLY)
        rain = float(self.rng.uniform(0.3, 1.0)) if wet else float(self.rng.uniform(0.0, 0.2 * d))
        visibility = float(np.clip(16000.0 * (1.0 - 0.9 * d * self.rng.random()) - 6000.0 * rain, 300.0, 16000.0))

        cold = condition in (RunwayCondition.SNOWY, RunwayCondition.ICY)
        temperature = float(self.rng.uniform(-15.0, -1.0)) if cold else float(self.rng.uniform(0.0, 25.0))

        return WeatherState.from_crosswind(
            crosswind, headwind, gust_kts=gust, turbulence=turbulence, variability_pct=variability,
            rain_pct=rain, visibility_m=visibility, temperature_c=temperature, **friction_kw,
        )

    def _sample_failures(self, d: float) -> tuple:
        failures: list[FailureMode] = []
        if self.rng.random() < d:  # хотя бы один отказ — с вероятностью d
            failures.append(_FAILURE_POOL[int(self.rng.integers(len(_FAILURE_POOL)))])
            if self.rng.random() < 0.4 * d:  # изредка — второй, без противоречий
                candidates = [
                    f for f in _FAILURE_POOL
                    if f not in failures
                    and not any({f, failures[0]} == pair for pair in _CONTRADICTIONS)
                ]
                if candidates:
                    failures.append(candidates[int(self.rng.integers(len(candidates)))])
        return tuple(failures)

    def _sample_touchdown(self, d: float) -> TouchdownSetup:
        return TouchdownSetup(
            speed_knots=float(self.rng.uniform(130.0, 160.0)),
            descent_rate_fpm=float(self.rng.uniform(100.0, 300.0)),
            pitch_deg=float(self.rng.uniform(-1.0, 3.0)),
            lateral_offset_m=float(self.rng.uniform(-1.0, 1.0) * (1.0 + 6.0 * d)),
            heading_offset_deg=float(self.rng.uniform(-1.0, 1.0) * (1.0 + 6.0 * d)),
        )

    def _sample_noise(self, d: float) -> SensorNoise:
        return SensorNoise(
            pos_sigma_m=0.05 + 0.5 * d,
            heading_sigma_deg=0.1 + 1.0 * d,
            speed_sigma_ms=0.1 + 1.0 * d,
            dropout_prob=0.02 * d,
        )
