"""In-process захват классических траекторий для SFT-датасета (план Stage B).

Гоняет **классический** контур внутри `RolloutEnv` (действие = коэффициенты пресета →
`env.step` воспроизводит классику) и на каждом такте сохраняет `(obs_окно, target_z)`,
где target = коэффициенты пресета этого прогона. Это единственный корректный путь: obs
включает внутреннее состояние PID (integral/deriv/last_output, traveled) — его НЕТ в пакете
телеметрии стенда, поэтому obs берём из того же `ObservationBuilder`, что и на инференсе
(гарантия контракта train↔deploy).

**Качество меток (заимствовано из `roman_repo`, `build_step3_pid_corrections_dataset.py`).**
Не все классические прогоны стоит клонировать: пресет вне своего режима — или в погоде, на
которую он не калиброван, — даёт траекторию, которую воспроизводить не надо. Поэтому каждый
прогон оценивается тем же objective, что и reward, и получает вес доверия:

* `1.0` — чистый прогон;
* `0.5` — с оговорками (насыщение команд, вмешательства Shield) — тянет градиент вдвое слабее;
* `0.0` — нарушен гейт ТЗ → прогон **отбрасывается**, а не размывает обучение.

Причины понижения именованные (а не «плохой прогон»), чтобы отчёт захвата был читаемым.

Реальный захват — на стенде (`RolloutEnv` с `ICSSim`); в тестах — на скриптованном стенде.
"""

from __future__ import annotations

import numpy as np

from ismpu.envs.action import preset_action
from ismpu.agent.shield import base_gains_from_pids
from ismpu.agent.pretrain import SFTDataset, target_z_from_gains
from ismpu.runtime.evaluate import evaluate_tz, FAIL

QUALITY_CLEAN = 1.0
QUALITY_CAVEAT = 0.5
QUALITY_REJECT = 0.0

# Пороги понижения — инженерные, не из ТЗ.
CAVEAT_SATURATION_RATIO = 0.50   # доля тактов с упёршейся командой
CAVEAT_RATE_P95 = 0.35           # p95 приращения команды за такт


def episode_quality(summary: dict, scenario) -> tuple[float, list[str]]:
    """Сводка эпизода + сценарий → (вес доверия к метке, именованные причины понижения)."""
    d = summary["diagnostics"]

    failed = [c.name for c in evaluate_tz(d, scenario) if c.verdict == FAIL]
    if failed:
        # Прогон не соответствует ТЗ — такую траекторию клонировать нельзя.
        return QUALITY_REJECT, [f"tz_fail:{name}" for name in failed]

    reasons: list[str] = []
    sat = d.get("saturation_ratio")
    if sat is not None and sat > CAVEAT_SATURATION_RATIO:
        reasons.append(f"saturation:{sat:.2f}")
    if d.get("shield_fallbacks"):
        reasons.append(f"shield_fallback:{d['shield_fallbacks']}")
    if d.get("shield_activations"):
        reasons.append(f"shield_active:{d['shield_activations']}")
    for channel, p95 in (d.get("rate_p95") or {}).items():
        if p95 is not None and p95 > CAVEAT_RATE_P95:
            reasons.append(f"rate:{channel}:{p95:.2f}")

    return (QUALITY_CAVEAT if reasons else QUALITY_CLEAN), reasons


def capture_scenario(env, scenario, max_steps: int = 2000,
                     *, score: bool = True) -> tuple[SFTDataset, dict]:
    """Один классический прогон сценария → (`SFTDataset` с весом, отчёт о качестве)."""
    obs, _ = env.reset(scenario)
    preset = base_gains_from_pids(env.controller.pids)   # коэффициенты пресета сценария
    action = preset_action(preset)                       # точная запись → классика
    tz = target_z_from_gains(preset)

    windows = [np.asarray(obs, dtype=np.float32)]
    for _ in range(max_steps):
        obs, _reward, terminated, truncated, _info = env.step(action)
        windows.append(np.asarray(obs, dtype=np.float32))
        if terminated or truncated:
            break

    if score:
        summary = env.objective.summary()
        weight, reasons = episode_quality(summary, scenario)
        report = {"scenario_id": getattr(scenario, "scenario_id", "?"),
                  "weight": weight, "reasons": reasons,
                  "total_loss": summary["total_loss"], "windows": len(windows)}
    else:
        weight, report = QUALITY_CLEAN, {"scenario_id": getattr(scenario, "scenario_id", "?"),
                                         "weight": QUALITY_CLEAN, "reasons": [],
                                         "total_loss": None, "windows": len(windows)}

    obs_arr = np.stack(windows).astype(np.float32)
    tz_arr = np.repeat(tz[None, :], len(windows), axis=0).astype(np.float32)
    weights = np.full(len(windows), weight, dtype=np.float32)
    return SFTDataset(obs=obs_arr, target_z=tz_arr, weight=weights), report


def capture_dataset(env, scenarios, max_steps: int = 2000, log=print,
                    *, score: bool = True) -> tuple[SFTDataset, list[dict]]:
    """Захват набора сценариев → (объединённый `SFTDataset`, отчёты по каждому прогону).

    Прогоны с нулевым весом (нарушен гейт ТЗ) в датасет не попадают. Если отброшены все —
    поднимается ошибка: молча вернуть пустой датасет значит превратить «нечего учить» в
    «обучение прошло».
    """
    parts, reports = [], []
    for i, scenario in enumerate(scenarios):
        ds, report = capture_scenario(env, scenario, max_steps=max_steps, score=score)
        reports.append(report)
        sid = report["scenario_id"] if report["scenario_id"] != "?" else f"#{i}"

        if report["weight"] <= QUALITY_REJECT:
            if log:
                log(f"ОТБРОШЕН {sid}: {', '.join(report['reasons'])}")
            continue

        parts.append(ds)
        if log:
            note = f" (оговорки: {', '.join(report['reasons'])})" if report["reasons"] else ""
            log(f"captured {sid}: {len(ds)} windows, вес {report['weight']}{note}")

    if not parts:
        raise RuntimeError(
            "все прогоны отброшены по гейту ТЗ — обучать SFT не на чем. "
            f"Причины: {[r['reasons'] for r in reports]}")
    return SFTDataset.concat(parts), reports
