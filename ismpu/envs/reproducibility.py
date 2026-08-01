"""Контракт воспроизводимости эпизода (шаг 6).

Заимствовано из `roman_repo/scripts/scenario_reproducibility.py`. Его идея: явно разделить
входы, которые мы контролируем сидом, и источники случайности, которые нам **не принадлежат** —
и назвать вторые поимённо, вместо того чтобы считать прогон воспроизводимым по умолчанию.

Наш случай ровно такой, и после перехода на стенд — в ещё большей степени. Пресеты и порядок
сценариев детерминированы, но **среду разыгрывает стенд**: ветер, осадки и состояние ВПП
выставляет Заказчик, реализацию порывов и сноса считает его модель, а повторить эпизод
бит-в-бит мы не можем даже теоретически — у нас нет ни телепорта, ни сида его генератора.
Значит, при неспокойных условиях один прогон ничего не доказывает: измеренное отклонение может
быть как свойством регулятора, так и одной удачной (или неудачной) реализацией.

Отсюда правило: `replica_validation_required = True`, когда условия неспокойные, и приёмка
обязана прогнать сценарий `min_replicas` раз и смотреть на худшую реплику, а не на среднюю
(ТЗ формулирует пределы как границы, а не как средние).
"""

from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Any

from ismpu.config.scenarios import Scenario
from ismpu.config.segments import FlightSegment
from ismpu.envs.weather import WeatherState

BENCH_WIND = "bench_wind_realization"
BENCH_PRECIPITATION = "bench_precipitation"
BENCH_LOW_FRICTION = "bench_low_friction"

WIND_STOCHASTIC_KTS = 1.0
"""Ветер слабее узла считаем штилем: он не порождает разброса, за которым стоило бы гнать реплики."""

DEFAULT_MIN_REPLICAS = 3
"""Сколько реплик требовать при неспокойных условиях. Три — минимум, на котором «худшая из
реплик» отличается от «единственной попытки»; это порог отчётности, а не статистика."""


def stochastic_sources(weather: WeatherState) -> tuple[str, ...]:
    """Источники случайности на стороне стенда, активные при данных условиях.

    Мы задаём (точнее — просим Заказчика выставить) их **интенсивность**, но не реализацию:
    сам процесс разыгрывает модель стенда.
    """
    sources: list[str] = []
    if abs(weather.wind_speed_kts) >= WIND_STOCHASTIC_KTS:
        sources.append(BENCH_WIND)
    if weather.rain_pct > 0.0:
        sources.append(BENCH_PRECIPITATION)
    if weather.runway_friction > 0.0:
        # Реализацию потери сцепления разыгрывает модель стенда, а не код сценария.
        sources.append(BENCH_LOW_FRICTION)
    return tuple(sources)


@dataclass(frozen=True)
class ReproducibilityContract:
    """Что в эпизоде детерминировано, что нет, и сколько реплик из-за этого нужно."""
    scenario_id: str
    deterministic_inputs: dict[str, Any] = field(default_factory=dict)
    external_stochastic_sources: tuple[str, ...] = ()
    replica_validation_required: bool = False
    min_replicas: int = 1

    @property
    def bit_reproducible(self) -> bool:
        """Даст ли повторный прогон с тем же сидом ту же траекторию."""
        return not self.external_stochastic_sources

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def contract_for(
    scenario: Scenario,
    *,
    min_replicas: int = DEFAULT_MIN_REPLICAS,
    aircraft_profile: str | None = None,
) -> ReproducibilityContract:
    """Строит контракт воспроизводимости для сценария."""
    weather = scenario.weather
    sources = tuple(dict.fromkeys(
        source
        for segment in FlightSegment
        for source in stochastic_sources(scenario.conditions_for(segment).weather)
    ))

    deterministic = {
        "scenario_seed": scenario.seed,
        "aircraft_profile": aircraft_profile,
        "expected_weather": _as_dict(weather),
        "failures": [failure.name for failure in scenario.failures],
        "control_preset": scenario.provenance.get(
            FlightSegment.ROLLOUT, scenario.scenario_id),
        "segment_sources": {
            segment.value: scenario.provenance.get(segment, scenario.scenario_id)
            for segment in FlightSegment
        },
        "segment_conditions": {
            segment.value: {
                "weather": _as_dict(scenario.conditions_for(segment).weather),
                "failures": sorted(
                    failure.name
                    for failure in scenario.conditions_for(segment).failures
                ),
            }
            for segment in FlightSegment
        },
    }

    return ReproducibilityContract(
        scenario_id=scenario.scenario_id,
        deterministic_inputs=deterministic,
        external_stochastic_sources=sources,
        replica_validation_required=bool(sources),
        min_replicas=min_replicas if sources else 1,
    )


def required_replicas(scenario: Scenario, *, min_replicas: int = DEFAULT_MIN_REPLICAS) -> int:
    """Сколько раз прогнать сценарий, чтобы результат приёмки что-то значил."""
    return contract_for(scenario, min_replicas=min_replicas).min_replicas


def worst_replica(
    results: list[dict[str, Any]],
    *,
    key: str = "total_loss",
) -> dict[str, Any] | None:
    """Худшая реплика по заданной метрике.

    Приёмка смотрит именно на худшую, а не на среднюю: ТЗ задаёт пределы как границы, и
    усреднение по репликам прятало бы единичный выход за допуск.
    """
    finite = [r for r in results if isinstance(r.get(key), (int, float))]
    if not finite:
        return None
    return max(finite, key=lambda r: r[key])


def _as_dict(value: object) -> dict[str, Any] | str | None:
    if value is None:
        return None
    try:
        return asdict(value)
    except TypeError:
        return str(value)
