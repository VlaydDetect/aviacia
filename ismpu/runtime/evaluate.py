"""Приёмка по ТЗ (разд. 5) + обязательное сравнение с baseline'ами (Этап 5).

Схема заимствована из `roman_repo/docs/tz_compliance_audit.md` — у второго участника это
самая проработанная часть, и три её правила перенесены сюда как есть:

1. **Вердикт по каждому пункту ТЗ отдельно**, таблицей «критерий → предел → измерено → вердикт».
   Единая сводная оценка скрывает, какое именно требование не выполнено.
2. **Отсутствие данных = FAIL**, а не «условно прошло». Но применимость критерия задаётся
   **явно**: если фазы в эпизоде физически не было (напр. руления при аварийном завершении),
   критерий помечается `SKIP` с причиной и виден в отчёте. Молча пропущенных критериев нет —
   иначе «нет данных» превращается в «прошло».
3. **Обязательный набор baseline'ов.** Сеть сравнивается не с нулём, а с классикой:
   DEFAULT-коэффициенты, пресет сценария («оракул»), SFT-чекпоинт, PPO-чекпоинт. Если PPO не
   бьёт пресет сценария — он не окупается, и это должно быть видно числом, а не на глаз.

Плюс `admit_checkpoint` — гейт допуска (аналог `stable_controller_library.admit_candidate`):
чекпоинт не «выпускается», пока не прошёл ТЗ и пороги устойчивости; отсутствующая или
нечисловая метрика = отказ.

Метрики берутся из `envs/reward.EpisodeObjective` — то же определение, что и у reward PPO
(единый objective, см. докстринг там).

Офлайн-проверка без X-Plane: `smoke_evaluate(env, scenarios)` (ср. `smoke_train`/`smoke_pretrain`).
"""

from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass, field, asdict

import numpy as np

from ismpu.config.requirements import (
    XTE_ROLLOUT_MAX_M, XTE_TAXI_MAX_M, XTE_NWS_FAIL_MAX_M,
    HEADING_FAULT_MAX_DEG, HEADING_HOLD_UNTIL_KTS,
)
from ismpu.control.failures import FailureMode
from ismpu.envs.action import preset_action, REFERENCE_ACTION
from ismpu.envs.reward import TAXI_PHASE_KTS
from ismpu.envs.reproducibility import contract_for, worst_replica
from ismpu.envs.splits import split_scenarios, assert_no_leakage
from ismpu.agent.shield import base_gains_from_pids

PASS, FAIL, SKIP = "PASS", "FAIL", "SKIP"

# Пороги гейта допуска чекпоинта — не из ТЗ, инженерные (ср. admit_candidate у Романа).
MAX_SATURATION_RATIO = 0.60   # доля тактов с упёршейся командой
MAX_SHIELD_FALLBACKS = 0      # откат на классику = сеть выдала недопустимое → не выпускаем
MAX_RATE_P95 = 0.35           # p95 приращения любой команды за такт


# --------------------------------------------------------------------------- #
# Политики: единый интерфейс для классики и сети
# --------------------------------------------------------------------------- #

class Policy:
    """Базовая политика. `begin_episode` вызывается после `env.reset` (пресет уже применён)."""

    name = "policy"

    def begin_episode(self, env) -> None:  # noqa: D401 - хук
        pass

    def __call__(self, obs) -> np.ndarray:
        raise NotImplementedError


class DefaultGainsPolicy(Policy):
    """Baseline 1: DEFAULT-коэффициенты во всех сценариях (что выдаёт «холодная» сеть)."""

    name = "default_gains"

    def __call__(self, obs):
        return REFERENCE_ACTION


class PresetPolicy(Policy):
    """Baseline 2 («оракул»): коэффициенты пресета сценария = классика, под которую он тюнен.

    Это та планка, которую нейросеть обязана побить, чтобы окупить своё существование.
    """

    name = "scenario_preset"

    def __init__(self):
        self._action = None

    def begin_episode(self, env):
        # `env.reset` уже применил пресет сценария к контуру — снимаем его коэффициенты.
        self._action = preset_action(base_gains_from_pids(env.controller.pids))

    def __call__(self, obs):
        return self._action


class NPGSPolicy(Policy):
    """Политика на основе обученной сети. Детерминированная (greedy) — режим поставки."""

    def __init__(self, net, name: str = "npgs", deterministic: bool = True):
        self.net = net
        self.name = name
        self.deterministic = deterministic

    def __call__(self, obs):
        action, _raw, _logp, _value = self.net.act_numpy(obs, deterministic=self.deterministic)
        return action


def load_npgs_policy(path: str, *, name: str | None = None) -> NPGSPolicy:
    """Загружает чекпоинт NPGS (веса + конфиг + слепок нормировки) в политику."""
    from ismpu.agent.gain_scheduler import NPGS   # локальный импорт: torch опционален
    net = NPGS.load(path, map_location="cpu")
    return NPGSPolicy(net, name=name or os.path.splitext(os.path.basename(path))[0])


# --------------------------------------------------------------------------- #
# Критерии ТЗ
# --------------------------------------------------------------------------- #

@dataclass
class Criterion:
    """Один пункт ТЗ: предел, измеренное значение, вердикт и его причина."""
    name: str
    tz_ref: str
    limit: float
    measured: float | None
    verdict: str
    reason: str = ""
    evaluation_basis: str = ""
    """Относительно чего измерена величина. Для курса это принципиально: отклонение от направления
    ВПП и ошибка команды руления — разные числа, и при смещении от оси они расходятся на градусы."""

    def as_dict(self) -> dict:
        return asdict(self)


def _check(name: str, tz_ref: str, limit: float, measured, *,
           applicable: bool, na_reason: str = "") -> Criterion:
    """Строит вердикт. Неприменимо → SKIP; применимо, но данных нет → FAIL."""
    if not applicable:
        return Criterion(name, tz_ref, limit, None, SKIP, na_reason)
    if measured is None or not math.isfinite(float(measured)):
        # Правило Романа: отсутствие измерения не может считаться прохождением.
        return Criterion(name, tz_ref, limit, None, FAIL, "нет измерения")
    ok = abs(float(measured)) <= limit
    return Criterion(name, tz_ref, limit, float(measured), PASS if ok else FAIL,
                     "" if ok else f"превышение допуска на {abs(float(measured)) - limit:.2f}")


HEADING_CRITERION_FAILURES = frozenset({
    FailureMode.REVERSE_LEFT_FAIL, FailureMode.REVERSE_RIGHT_FAIL,
    FailureMode.ENGINE_OUT_LEFT, FailureMode.ENGINE_OUT_RIGHT,
    FailureMode.THRUST_LEFT_DEGRADED, FailureMode.THRUST_RIGHT_DEGRADED,
})
"""Отказы, при которых ТЗ нормирует удержание курса (5.1.3.3 — «при нарушении тяги или реверса
на пробеге»). В 5.1.3.1 (штатная работа) требования по курсу **нет вообще** — там только осевая
линия. Применять гейт ±5° к штатному сценарию и ссылаться при этом на 5.1.3.3 значит цитировать
заказчику пункт, который к сценарию не относится."""


def evaluate_tz(diagnostics: dict, scenario) -> list[Criterion]:
    """Диагностика эпизода + сценарий → список вердиктов по пунктам ТЗ разд. 5."""
    d = diagnostics
    failures = set(getattr(scenario, "failures", ()) or ())
    nws_failed = FailureMode.NWS_FAIL in failures
    thrust_failed = bool(failures & HEADING_CRITERION_FAILURES)

    # 5.1.3.1 — удержание оси на пробеге. При отказе NWS действует послабление до ±5 м
    # (5.1.3.2), т.к. руль направления мёртв и ось держится дифференциальным торможением.
    rollout_limit = XTE_NWS_FAIL_MAX_M if nws_failed else XTE_ROLLOUT_MAX_M
    rollout_ref = "5.1.3.2 (отказ NWS)" if nws_failed else "5.1.3.1"

    # 5.1.3.2 разрешает ±5 м «на пробеге ДО ПОЛНОЙ ОСТАНОВКИ», то есть послабление действует и на
    # малой скорости. Применять поверх него допуск руления ±1 м значит требовать строже ТЗ.
    reached_taxi = (d.get("final_speed_kts") is not None
                    and d["final_speed_kts"] < TAXI_PHASE_KTS)
    taxi_applicable = reached_taxi and not nws_failed
    taxi_na_reason = ("отказ NWS: 5.1.3.2 разрешает ±5 м до полной остановки, "
                      "допуск руления не применяется" if nws_failed
                      else "эпизод не дошёл до скорости руления — фазы не было")

    # Требование по курсу действует только выше 30 узлов (5.1.3.3): эпизод целиком ниже —
    # критерий неприменим. Но если отсчётов нет вовсе — это FAIL, а не пропуск.
    no_samples = d.get("samples", 0) == 0
    heading_measured = no_samples or d.get("heading_max_deg") is not None
    heading_applicable = thrust_failed and heading_measured
    if not thrust_failed:
        heading_na_reason = ("штатная работа (5.1.3.1) — требования по курсу ТЗ не задаёт; "
                             "±5° относится к 5.1.3.3 (нарушение тяги/реверса)")
    else:
        heading_na_reason = (f"эпизод целиком ниже {HEADING_HOLD_UNTIL_KTS:.0f} узлов — "
                             f"требование удержания курса не применяется")

    heading = _check("heading_max", "5.1.3.3", HEADING_FAULT_MAX_DEG, d.get("heading_max_deg"),
                     applicable=heading_applicable, na_reason=heading_na_reason)
    # Что именно измерялось: отклонение курса ВС от направления ВПП, а не ошибка команды руления.
    heading.evaluation_basis = "runway_relative_true_heading"

    return [
        _check("xte_rollout_max", rollout_ref, rollout_limit, d.get("xte_rollout_max_m"),
               applicable=True),
        _check("xte_taxi_max", "5.1.3.1 (руление)", XTE_TAXI_MAX_M, d.get("xte_taxi_max_m"),
               applicable=taxi_applicable, na_reason=taxi_na_reason),
        heading,
    ]


def verdict_of(criteria: list[Criterion]) -> str:
    """Итог эпизода: FAIL, если провален хоть один применимый критерий."""
    if any(c.verdict == FAIL for c in criteria):
        return FAIL
    return PASS


# --------------------------------------------------------------------------- #
# Прогон
# --------------------------------------------------------------------------- #

def run_episode(env, scenario, policy: Policy, *, max_steps: int = 4000) -> dict:
    """Один эпизод под заданной политикой → objective + вердикты ТЗ."""
    obs, _ = env.reset(scenario)
    policy.begin_episode(env)

    steps = 0
    for _ in range(max_steps):
        obs, _reward, terminated, truncated, info = env.step(policy(obs))
        steps += 1
        if terminated or truncated:
            break

    summary = env.objective.summary()
    criteria = evaluate_tz(summary["diagnostics"], scenario)
    return {
        "scenario_id": getattr(scenario, "scenario_id", "?"),
        "policy": policy.name,
        "steps": steps,
        "total_loss": summary["total_loss"],
        "reward": summary["reward"],
        "components": summary["components"],
        "diagnostics": summary["diagnostics"],
        "criteria": [c.as_dict() for c in criteria],
        "verdict": verdict_of(criteria),
    }


def run_scenario(env, scenario, policy: Policy, *, max_steps: int = 4000,
                 replicas: int | None = None) -> dict:
    """Прогон сценария нужным числом реплик → **худшая** из них.

    При стохастической погоде (турбулентность/порывы/изменчивость) X-Plane разыгрывает процесс
    своим генератором, которым мы не управляем, поэтому один прогон ничего не доказывает:
    отклонение может быть свойством регулятора, а может — одной удачной реализацией. Берётся
    худшая реплика, а не средняя: ТЗ задаёт пределы как границы (см. `envs/reproducibility`).
    """
    contract = contract_for(scenario)
    count = replicas if replicas is not None else contract.min_replicas

    results = [run_episode(env, scenario, policy, max_steps=max_steps) for _ in range(count)]
    worst = worst_replica(results) or results[0]
    worst = dict(worst)
    worst["replicas"] = count
    worst["reproducibility"] = contract.as_dict()
    if count > 1:
        worst["replica_losses"] = [r["total_loss"] for r in results]
        # Провал хотя бы одной реплики — провал сценария.
        worst["verdict"] = FAIL if any(r["verdict"] == FAIL for r in results) else worst["verdict"]
    return worst


def run_battery(env, scenarios, policy: Policy, *, max_steps: int = 4000, log=print,
                replicas: int | None = None) -> dict:
    """Прогон набора сценариев под одной политикой → сводка по политике."""
    episodes = [run_scenario(env, s, policy, max_steps=max_steps, replicas=replicas)
                for s in scenarios]
    passed = sum(1 for e in episodes if e["verdict"] == PASS)
    losses = [e["total_loss"] for e in episodes]
    if log:
        log(f"{policy.name}: {passed}/{len(episodes)} PASS, "
            f"mean loss {sum(losses) / max(len(losses), 1):.3f}")
    return {
        "policy": policy.name,
        "episodes": episodes,
        "pass_count": passed,
        "episode_count": len(episodes),
        "pass_rate": passed / len(episodes) if episodes else 0.0,
        "mean_total_loss": sum(losses) / len(losses) if losses else None,
        "worst_total_loss": max(losses) if losses else None,
    }


def compare_policies(env, scenarios, policies: list[Policy], *,
                     max_steps: int = 4000, log=print, replicas: int | None = None) -> dict:
    """Сравнение политик на одном наборе сценариев (обязательный шаг приёмки).

    Возвращает сводку + явные флаги `beats_default` / `beats_preset` для каждой политики:
    без них «модель работает» невозможно отличить от «модель не хуже нуля».
    """
    results = {p.name: run_battery(env, scenarios, p, max_steps=max_steps, log=log,
                                   replicas=replicas)
               for p in policies}

    def _loss(name):
        r = results.get(name)
        return None if r is None else r["mean_total_loss"]

    default_loss, preset_loss = _loss(DefaultGainsPolicy.name), _loss(PresetPolicy.name)
    for name, r in results.items():
        mine = r["mean_total_loss"]
        r["beats_default"] = (None if (mine is None or default_loss is None)
                              else mine < default_loss)
        r["beats_preset"] = (None if (mine is None or preset_loss is None)
                             else mine < preset_loss)

    return {
        "scenario_count": len(scenarios),
        "scenarios": [getattr(s, "scenario_id", "?") for s in scenarios],
        "policies": results,
        "baselines": {"default": default_loss, "preset": preset_loss},
    }


# --------------------------------------------------------------------------- #
# Гейт допуска чекпоинта
# --------------------------------------------------------------------------- #

@dataclass
class AdmissionResult:
    admitted: bool
    reasons: list = field(default_factory=list)

    def as_dict(self) -> dict:
        return asdict(self)


def admit_checkpoint(battery: dict, *, require_beats_preset: bool = True) -> AdmissionResult:
    """Пропускать ли чекпоинт дальше. Отсутствующая/нечисловая метрика = отказ.

    Проверяется не только соответствие ТЗ, но и «как» оно достигнуто: постоянное насыщение
    команд или резкие приращения означают, что запас управляемости исчерпан и режим держится
    на грани, даже если формальные пределы соблюдены.
    """
    reasons: list[str] = []

    if battery.get("episode_count", 0) == 0:
        return AdmissionResult(False, ["пустой приёмочный набор"])

    if battery["pass_count"] != battery["episode_count"]:
        failed = [e["scenario_id"] for e in battery["episodes"] if e["verdict"] == FAIL]
        reasons.append(f"провалены сценарии ТЗ: {', '.join(failed)}")

    for ep in battery["episodes"]:
        d = ep["diagnostics"]
        sid = ep["scenario_id"]

        sat = d.get("saturation_ratio")
        if sat is None or not math.isfinite(sat):
            reasons.append(f"{sid}: нет метрики saturation_ratio")
        elif sat > MAX_SATURATION_RATIO:
            reasons.append(f"{sid}: насыщение команд {sat:.2f} > {MAX_SATURATION_RATIO}")

        fallbacks = d.get("shield_fallbacks")
        if fallbacks is None:
            reasons.append(f"{sid}: нет метрики shield_fallbacks")
        elif fallbacks > MAX_SHIELD_FALLBACKS:
            reasons.append(f"{sid}: откатов Shield на классику {fallbacks}")

        for channel, p95 in (d.get("rate_p95") or {}).items():
            if p95 is None:
                continue      # канал не двигался за эпизод — не повод для отказа
            if not math.isfinite(p95):
                reasons.append(f"{sid}: нечисловой rate_p95[{channel}]")
            elif p95 > MAX_RATE_P95:
                reasons.append(f"{sid}: резкие приращения {channel} p95={p95:.3f} > {MAX_RATE_P95}")

    if require_beats_preset and battery.get("beats_preset") is not True:
        reasons.append("не превосходит пресет сценария (классику) — не окупается")

    return AdmissionResult(not reasons, reasons)


# --------------------------------------------------------------------------- #
# Отчёт
# --------------------------------------------------------------------------- #

def render_report(comparison: dict, admission: dict | None = None) -> str:
    """Markdown-отчёт приёмки. Отрицательные результаты не скрываются — они и есть смысл."""
    lines = ["# Приёмка ИСМПУ по ТЗ (разд. 5)", ""]
    lines.append(f"Сценариев в наборе: **{comparison['scenario_count']}**")
    lines.append("")

    lines.append("## Сводка по политикам")
    lines.append("")
    lines.append("| Политика | PASS | Средний loss | Лучше DEFAULT | Лучше пресета |")
    lines.append("|---|---|---|---|---|")
    for name, r in comparison["policies"].items():
        def _flag(v):
            return "—" if v is None else ("да" if v else "**нет**")
        mean = "—" if r["mean_total_loss"] is None else f"{r['mean_total_loss']:.3f}"
        lines.append(f"| `{name}` | {r['pass_count']}/{r['episode_count']} | {mean} "
                     f"| {_flag(r.get('beats_default'))} | {_flag(r.get('beats_preset'))} |")
    lines.append("")

    for name, r in comparison["policies"].items():
        lines.append(f"## `{name}` — по сценариям")
        lines.append("")
        lines.append("| Сценарий | Вердикт | Критерий | Пункт ТЗ | Предел | Измерено |")
        lines.append("|---|---|---|---|---|---|")
        for ep in r["episodes"]:
            for c in ep["criteria"]:
                measured = "—" if c["measured"] is None else f"{c['measured']:.2f}"
                note = f" ({c['reason']})" if c["reason"] else ""
                lines.append(f"| {ep['scenario_id']} | {ep['verdict']} | {c['name']}{note} "
                             f"| {c['tz_ref']} | {c['limit']:.1f} | {measured} |")
        lines.append("")

    if admission is not None:
        lines.append("## Гейт допуска чекпоинта")
        lines.append("")
        lines.append("**ДОПУЩЕН**" if admission["admitted"] else "**НЕ ДОПУЩЕН**")
        for reason in admission["reasons"]:
            lines.append(f"- {reason}")
        lines.append("")
    return "\n".join(lines)


def write_report(comparison: dict, out_dir: str, *, admission: dict | None = None) -> dict:
    """Пишет `evaluation.json` + `report.md`. → пути записанных файлов."""
    os.makedirs(out_dir, exist_ok=True)
    payload = {"comparison": comparison, "admission": admission}
    json_path = os.path.join(out_dir, "evaluation.json")
    md_path = os.path.join(out_dir, "report.md")
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2, default=str)
    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write(render_report(comparison, admission))
    return {"json": json_path, "markdown": md_path}


# --------------------------------------------------------------------------- #
# Точки входа
# --------------------------------------------------------------------------- #

def smoke_evaluate(env, scenarios, *, policies: list[Policy] | None = None,
                   max_steps: int = 200, log=None) -> dict:
    """Офлайн-приёмка на поданной среде (без X-Plane) — для тестов/отладки."""
    policies = policies or [DefaultGainsPolicy(), PresetPolicy()]
    return compare_policies(env, scenarios, policies, max_steps=max_steps, log=log)


def main(*, sft_checkpoint: str | None = "checkpoints/npgs_sft.pt",
         ppo_checkpoint: str | None = "checkpoints/npgs_final.pt",
         out_dir: str = "runs/evaluation") -> dict:
    """Полная приёмка на X-Plane: приёмочный набор × 4 политики → отчёт + гейт допуска."""
    from ismpu.control.system import ControllingSystem
    from ismpu.io.xplane_connector import XPlaneConnectX
    from ismpu.envs.sim_interface import XPlaneBackend
    from ismpu.envs.rollout_env import RolloutEnv
    from ismpu.envs.scenario_generator import ScenarioGenerator
    from ismpu.agent.shield import Shield
    from ismpu.runtime.train import silence_control_console

    silence_control_console()

    # Телеметрия и команды идут через SimInterface; контуру коннектор нужен только для прямой
    # отправки в классическом цикле, здесь он работает через среду (send=False).
    xpc = XPlaneConnectX()
    sim = XPlaneBackend(xpc=xpc)
    controller = ControllingSystem(sim)
    env = RolloutEnv(sim, controller, shield=Shield())

    scenarios = ScenarioGenerator(seed=0).battery()
    # Holdout считается ОТДЕЛЬНО: смешанный с обучающим он мерил бы запоминание, а не перенос.
    split = split_scenarios(scenarios)
    assert_no_leakage(split)
    print(f"Приёмочный набор: {split.summary()}")

    policies: list[Policy] = [DefaultGainsPolicy(), PresetPolicy()]
    if sft_checkpoint and os.path.exists(sft_checkpoint):
        policies.append(load_npgs_policy(sft_checkpoint, name="sft"))
    if ppo_checkpoint and os.path.exists(ppo_checkpoint):
        policies.append(load_npgs_policy(ppo_checkpoint, name="ppo"))

    try:
        comparison = compare_policies(env, scenarios, policies)
        holdout = (compare_policies(env, split.holdout, policies, log=None)
                   if split.holdout else None)
    finally:
        env.close()

    # Гейт применяется к последней (самой обученной) политике — и по holdout, если он есть:
    # соответствие на знакомых условиях само по себе ничего не гарантирует.
    target = policies[-1].name
    gate_source = holdout["policies"][target] if holdout else comparison["policies"][target]
    admission = admit_checkpoint(gate_source).as_dict()
    comparison["split"] = split.summary()
    comparison["holdout"] = holdout
    paths = write_report(comparison, out_dir, admission=admission)
    print(f"Отчёт: {paths['markdown']}")
    return {"comparison": comparison, "holdout": holdout,
            "admission": admission, "paths": paths}


if __name__ == "__main__":
    main()
