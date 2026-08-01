"""Детерминированное разбиение сценариев на обучение и holdout (шаг 6).

Схема заимствована из `roman_repo/scripts/train_neural_pid_tuner.py::make_split`. Разбиение
**не случайное**, а семантическое плюс хеш-добор:

1. **Семантика.** Сценарий уходит в holdout, если его имя помечено (`holdout`/`unseen`) или его
   отказ входит в `HOLDOUT_FAILURE_FAMILIES` — семейства, которые PPO не видит на обучении
   вообще. Без этого «обобщение на незнакомый отказ» проверить нечем: сеть встречала все
   режимы, и приёмка мерила бы запоминание, а не перенос.
2. **Хеш-добор** до нужной доли — по SHA-256 от идентификатора сценария, а не по
   `shuffle(seed)`. Свойство, ради которого это делается: **добавление новых сценариев не
   перетасовывает уже назначенные**. С seeded-перемешиванием любой новый сценарий менял бы
   разбиение целиком, и результаты приёмки переставали бы сравниваться между прогонами.

Разбиение — чистая функция от идентификаторов и отказов: ни RNG, ни глобального состояния.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

from ismpu.control.failures import FailureMode

HOLDOUT_MARKERS = ("holdout", "unseen")
DEFAULT_HOLDOUT_FRACTION = 0.2


@dataclass(frozen=True)
class ScenarioSignature:
    """Устойчивая комбинация условий, а не имя или целое семейство отказов."""

    failures: tuple[str, ...]
    runway_friction_bin: int
    crosswind_bin: int
    headwind_bin: int
    lateral_offset_bin: int
    heading_offset_bin: int
    speed_bin: int
    aircraft_profile: str = ""

    def key(self) -> str:
        values = (
            ",".join(self.failures) or "NONE",
            str(self.runway_friction_bin),
            str(self.crosswind_bin),
            str(self.headwind_bin),
            str(self.lateral_offset_bin),
            str(self.heading_offset_bin),
            str(self.speed_bin),
        )
        return "|".join(((self.aircraft_profile,) if self.aircraft_profile else ()) + values)


def scenario_signature(scenario, *, aircraft_profile: str | None = None) -> ScenarioSignature:
    """Каноническая дискретизация условий для train/eval split."""
    from ismpu.config.runway import RWY_HEADING_TRUE
    from ismpu.envs.weather import decompose_wind

    weather = scenario.weather
    cross, head = decompose_wind(
        weather.wind_speed_kts,
        weather.wind_dir_from_degt,
        RWY_HEADING_TRUE,
    )
    touchdown = scenario.touchdown
    return ScenarioSignature(
        failures=tuple(sorted(f.name for f in scenario.failures)),
        runway_friction_bin=int(round(float(weather.runway_friction))),
        crosswind_bin=int(round(cross / 5.0)),
        headwind_bin=int(round(head / 5.0)),
        lateral_offset_bin=int(round(touchdown.lateral_offset_m / 2.0)),
        heading_offset_bin=int(round(touchdown.heading_offset_deg / 2.0)),
        speed_bin=int(round(touchdown.speed_knots / 10.0)),
        aircraft_profile=(aircraft_profile or "").lower(),
    )


def is_signature_holdout(
    scenario,
    *,
    fraction: float = DEFAULT_HOLDOUT_FRACTION,
    aircraft_profile: str | None = None,
) -> bool:
    if not 0.0 <= fraction <= 1.0:
        raise ValueError("holdout fraction должна быть в [0, 1]")
    return _hash_unit(
        "signature-v1:" + scenario_signature(
            scenario, aircraft_profile=aircraft_profile).key()
    ) < fraction


class PartitionedScenarioProvider:
    """Фильтр над единым sampler с непересекающимися train/eval signatures."""

    def __init__(
        self,
        generator,
        *,
        partition: str,
        fraction: float = DEFAULT_HOLDOUT_FRACTION,
        difficulty=None,
        max_attempts: int = 10_000,
    ):
        if partition not in {"train", "eval"}:
            raise ValueError("partition должен быть 'train' или 'eval'")
        self.generator = generator
        self.partition = partition
        self.fraction = fraction
        self.difficulty = difficulty
        self.max_attempts = max_attempts

    def __call__(self):
        difficulty = self.difficulty() if callable(self.difficulty) else self.difficulty
        want_holdout = self.partition == "eval"
        for _ in range(self.max_attempts):
            scenario = self.generator.sample(difficulty)
            if is_signature_holdout(
                scenario,
                fraction=self.fraction,
                aircraft_profile=getattr(self.generator, "aircraft_profile", None),
            ) is want_holdout:
                return scenario
        raise RuntimeError(
            f"не удалось получить scenario partition={self.partition!r} "
            f"за {self.max_attempts} попыток")

HOLDOUT_FAILURE_FAMILIES = frozenset({
    FailureMode.ENGINE_OUT_LEFT,
    FailureMode.ENGINE_OUT_RIGHT,
    FailureMode.GEAR_CONFIG,
})
"""Семейства отказов, зарезервированные под holdout: на обучении не встречаются никогда.

Выбраны отказы, для которых **нет своего откалиброванного пресета** (`_PRESET_BY_FAILURE`
покрывает только NWS и реверсы). Значит, классика на них работает своим `default`-пресетом, и
именно здесь у сети есть шанс показать перенос, а у приёмки — его измерить.
"""


def _hash_unit(key: str) -> float:
    """SHA-256 от идентификатора → число в [0, 1). Стабильно между запусками и версиями Python.

    Встроенный `hash()` здесь не годится: он рандомизирован по соли процесса (PYTHONHASHSEED),
    поэтому разбиение менялось бы от запуска к запуску.
    """
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") / float(1 << 64)


def is_marked_holdout(scenario_id: str) -> bool:
    """Помечен ли сценарий как holdout своим именем."""
    lowered = str(scenario_id).lower()
    return any(marker in lowered for marker in HOLDOUT_MARKERS)


def has_holdout_failure(scenario) -> bool:
    """Затрагивает ли сценарий зарезервированное семейство отказов."""
    failures = set(getattr(scenario, "failures", ()) or ())
    return bool(failures & HOLDOUT_FAILURE_FAMILIES)


def holdout_reason(
    scenario,
    *,
    fraction: float = DEFAULT_HOLDOUT_FRACTION,
    aircraft_profile: str | None = None,
) -> str | None:
    """Почему сценарий в holdout, или `None` если он обучающий. Причина всегда именованная."""
    scenario_id = getattr(scenario, "scenario_id", str(scenario))
    if is_marked_holdout(scenario_id):
        return "marker"
    if has_holdout_failure(scenario):
        return "reserved_failure_family"
    profile_prefix = f"{aircraft_profile.lower()}:" if aircraft_profile else ""
    if _hash_unit(profile_prefix + scenario_id) < fraction:
        return "hash_topup"
    return None


@dataclass
class SplitResult:
    train: list = field(default_factory=list)
    holdout: list = field(default_factory=list)
    aircraft_profile: str | None = None
    reasons: dict = field(default_factory=dict)   # scenario_id → причина попадания в holdout

    @property
    def holdout_fraction(self) -> float:
        total = len(self.train) + len(self.holdout)
        return len(self.holdout) / total if total else 0.0

    def summary(self) -> dict:
        counts: dict[str, int] = {}
        for reason in self.reasons.values():
            counts[reason] = counts.get(reason, 0) + 1
        return {
            "train": len(self.train),
            "holdout": len(self.holdout),
            "holdout_fraction": self.holdout_fraction,
            "holdout_by_reason": counts,
            "aircraft_profile": self.aircraft_profile,
        }


def split_scenarios(
    scenarios,
    *,
    fraction: float = DEFAULT_HOLDOUT_FRACTION,
    aircraft_profile: str | None = None,
) -> SplitResult:
    """Разбивает набор сценариев. Детерминировано и устойчиво к добавлению новых элементов."""
    if not 0.0 <= fraction <= 1.0:
        raise ValueError(f"fraction должна быть в [0, 1], получено {fraction}")

    profile = aircraft_profile.lower() if aircraft_profile else None
    result = SplitResult(aircraft_profile=profile)
    for scenario in scenarios:
        if profile and profile not in scenario.aircraft_controls:
            raise ValueError(
                f"scenario {scenario.scenario_id!r} has no aircraft profile {profile!r}")
        reason = holdout_reason(
            scenario, fraction=fraction, aircraft_profile=profile)
        if reason is None:
            result.train.append(scenario)
        else:
            result.holdout.append(scenario)
            result.reasons[getattr(scenario, "scenario_id", str(scenario))] = reason
    return result


def assert_no_leakage(split: SplitResult) -> None:
    """Проверяет, что holdout не пересекается с обучением по идентификаторам.

    Дешёвая страховка от самой дорогой ошибки приёмки: если сценарий попал в обе части,
    «результат на незнакомых условиях» измеряет запоминание.
    """
    train_ids = {getattr(s, "scenario_id", str(s)) for s in split.train}
    holdout_ids = {getattr(s, "scenario_id", str(s)) for s in split.holdout}
    overlap = train_ids & holdout_ids
    if overlap:
        raise ValueError(f"утечка holdout в обучение: {sorted(overlap)}")

    leaked_families = [
        getattr(s, "scenario_id", "?") for s in split.train if has_holdout_failure(s)
    ]
    if leaked_families:
        raise ValueError(
            f"зарезервированное семейство отказов попало в обучение: {sorted(leaked_families)}")
