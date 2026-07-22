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

BENCH_WIND = "bench_wind_realization"
BENCH_PRECIPITATION = "bench_precipitation"
BENCH_LOW_FRICTION = "bench_low_friction"

WIND_STOCHASTIC_KTS = 1.0
"""Ветер слабее узла считаем штилем: он не порождает разброса, за которым стоило бы гнать реплики."""

DEFAULT_MIN_REPLICAS = 3
"""Сколько реплик требовать при неспокойных условиях. Три — минимум, на котором «худшая из
реплик» отличается от «единственной попытки»; это порог отчётности, а не статистика."""


def stochastic_sources(weather) -> tuple[str, ...]:
    """Источники случайности на стороне стенда, активные при данных условиях.

    Мы задаём (точнее — просим Заказчика выставить) их **интенсивность**, но не реализацию:
    сам процесс разыгрывает модель стенда.
    """
    sources: list[str] = []
    if abs(getattr(weather, "wind_speed_kts", 0.0)) >= WIND_STOCHASTIC_KTS:
        sources.append(BENCH_WIND)
    if getattr(weather, "rain_pct", 0.0) > 0.0:
        sources.append(BENCH_PRECIPITATION)
    if getattr(weather, "runway_friction", 0.0) > 0.0:
        # Скользкая полоса — срыв сцепления, а он по своей природе разыгрывается, а не считается.
        sources.append(BENCH_LOW_FRICTION)
    return tuple(sources)


@dataclass(frozen=True)
class ReproducibilityContract:
    """Что в эпизоде детерминировано, что нет, и сколько реплик из-за этого нужно."""
    scenario_id: str
    deterministic_inputs: dict = field(default_factory=dict)
    external_stochastic_sources: tuple = ()
    replica_validation_required: bool = False
    min_replicas: int = 1

    @property
    def bit_reproducible(self) -> bool:
        """Даст ли повторный прогон с тем же сидом ту же траекторию."""
        return not self.external_stochastic_sources

    def as_dict(self) -> dict:
        return asdict(self)


def contract_for(scenario, *, min_replicas: int = DEFAULT_MIN_REPLICAS) -> ReproducibilityContract:
    """Строит контракт воспроизводимости для сценария."""
    weather = getattr(scenario, "weather", None)
    sources = stochastic_sources(weather) if weather is not None else ()

    deterministic = {
        "scenario_seed": getattr(scenario, "seed", None),
        "expected_weather": _as_dict(weather),
        "failures": [f.name for f in (getattr(scenario, "failures", ()) or ())],
        "control_preset": getattr(getattr(scenario, "control", None), "name", None),
    }

    return ReproducibilityContract(
        scenario_id=getattr(scenario, "scenario_id", "?"),
        deterministic_inputs=deterministic,
        external_stochastic_sources=sources,
        replica_validation_required=bool(sources),
        min_replicas=min_replicas if sources else 1,
    )


def required_replicas(scenario, *, min_replicas: int = DEFAULT_MIN_REPLICAS) -> int:
    """Сколько раз прогнать сценарий, чтобы результат приёмки что-то значил."""
    return contract_for(scenario, min_replicas=min_replicas).min_replicas


def worst_replica(results: list[dict], *, key: str = "total_loss") -> dict | None:
    """Худшая реплика по заданной метрике.

    Приёмка смотрит именно на худшую, а не на среднюю: ТЗ задаёт пределы как границы, и
    усреднение по репликам прятало бы единичный выход за допуск.
    """
    finite = [r for r in results if isinstance(r.get(key), (int, float))]
    if not finite:
        return None
    return max(finite, key=lambda r: r[key])


def _as_dict(value):
    if value is None:
        return None
    try:
        return asdict(value)
    except TypeError:
        return str(value)
