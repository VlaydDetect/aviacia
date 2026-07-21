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


def holdout_reason(scenario, *, fraction: float = DEFAULT_HOLDOUT_FRACTION) -> str | None:
    """Почему сценарий в holdout, или `None` если он обучающий. Причина всегда именованная."""
    scenario_id = getattr(scenario, "scenario_id", str(scenario))
    if is_marked_holdout(scenario_id):
        return "marker"
    if has_holdout_failure(scenario):
        return "reserved_failure_family"
    if _hash_unit(scenario_id) < fraction:
        return "hash_topup"
    return None


@dataclass
class SplitResult:
    train: list = field(default_factory=list)
    holdout: list = field(default_factory=list)
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
        }


def split_scenarios(scenarios, *, fraction: float = DEFAULT_HOLDOUT_FRACTION) -> SplitResult:
    """Разбивает набор сценариев. Детерминировано и устойчиво к добавлению новых элементов."""
    if not 0.0 <= fraction <= 1.0:
        raise ValueError(f"fraction должна быть в [0, 1], получено {fraction}")

    result = SplitResult()
    for scenario in scenarios:
        reason = holdout_reason(scenario, fraction=fraction)
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
