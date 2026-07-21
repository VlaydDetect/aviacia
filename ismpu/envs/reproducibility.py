"""Контракт воспроизводимости эпизода (шаг 6).

Заимствовано из `roman_repo/scripts/scenario_reproducibility.py`. Его идея: явно разделить
входы, которые мы контролируем сидом, и источники случайности, которые нам **не принадлежат** —
и назвать вторые поимённо, вместо того чтобы считать прогон воспроизводимым по умолчанию.

Наш случай ровно такой. `ScenarioGenerator` детерминирован по сиду, но **X-Plane — нет**:
собственные турбулентность, порывы (shear) и пространственная изменчивость ветра симулятор
разыгрывает сам, своим генератором, которым мы не управляем. Значит, при ненулевой болтанке
одинаковый сид **не даёт** одинаковую траекторию, и приёмочный прогон такого сценария в одну
реплику ничего не доказывает: измеренное отклонение может быть как свойством регулятора, так и
одной удачной или неудачной реализацией турбулентности.

Отсюда правило: `replica_validation_required = True`, когда в погоде есть стохастика, и
приёмка обязана прогнать сценарий `min_replicas` раз и смотреть на худшую реплику, а не на
среднюю (ТЗ формулирует пределы как границы, а не как средние).
"""

from __future__ import annotations

from dataclasses import dataclass, asdict, field

XPLANE_NATIVE_TURBULENCE = "xplane_native_turbulence"
XPLANE_NATIVE_GUST = "xplane_native_wind_shear"
XPLANE_WIND_VARIABILITY = "xplane_wind_variability"

DEFAULT_MIN_REPLICAS = 3
"""Сколько реплик требовать при стохастической погоде. Три — минимум, на котором «худшая из
реплик» отличается от «единственной попытки»; это порог отчётности, а не статистика."""


def stochastic_sources(weather) -> tuple[str, ...]:
    """Источники случайности на стороне X-Plane, активные при данной погоде.

    Мы задаём их **интенсивность**, но не реализацию: сам процесс разыгрывает симулятор.
    """
    sources: list[str] = []
    if getattr(weather, "turbulence", 0.0) > 0.0:
        sources.append(XPLANE_NATIVE_TURBULENCE)
    if getattr(weather, "gust_kts", 0.0) > 0.0:
        sources.append(XPLANE_NATIVE_GUST)
    if getattr(weather, "variability_pct", 0.0) > 0.0:
        sources.append(XPLANE_WIND_VARIABILITY)
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
        "touchdown": _as_dict(getattr(scenario, "touchdown", None)),
        "sensor_noise": _as_dict(getattr(scenario, "sensor_noise", None)),
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
