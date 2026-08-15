"""Оркестрация SFT-подогрева NPGS (план Stage B): захват классических прогонов на стенде →
behavioral cloning на эталонных коэффициентах пресетов → чекпоинт для `train.py init_from`.

Запуск (нужен работающий стенд):  python -m ismpu.runtime.pretrain
Оффлайн-валидация без стенда — `smoke_pretrain(env, scenarios, ...)` (среду подаёт вызывающий).

Разметка (каноническая): каждая ветка со статусом **accepted** для выбранного профиля = отдельный режим/метка,
цель = его собственные коэффициенты. Каждый пресет прогоняется по нескольку раз: разнообразие
наблюдений даёт сам стенд (расстановка, ветер, шум датчиков от прогона к прогону не повторяются),
а метка при этом не меняется. Отсев ещё-не-выверенных пресетов — через флаг
`Scenario.is_accepted(profile, FlightSegment.ROLLOUT)`, НЕ по названию.

**Условия задаёт оператор стенда.** `build_scenarios` перечисляет, какие режимы надо снять; в
каких именно условиях стенд их выдаст, мы не выбираем — сверяться с фактическими условиями
эпизода нужно по телеметрии (`Telemetry.weather` / `Telemetry.faults`), а прогоны, не
соответствующие своему пресету, отсеивает оценка качества в `capture.py`.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field, replace

from ismpu.agent.gain_scheduler import NPGS, NPGSConfig
from ismpu.io.ics_connector import LISTEN_IP_ANY
from ismpu.agent.pretrain import pretrain_sft, PretrainConfig, SFTDataset
from ismpu.runtime.capture import capture_dataset
from ismpu.config.scenarios import SCENARIOS
from ismpu.config.segments import FlightSegment


@dataclass
class PretrainRunConfig:
    variants_per_preset: int = 20      # прогонов на пресет (разнообразие obs)
    max_steps: int = 3000              # макс. тактов на прогон
    seed: int = 0
    checkpoint_dir: str = "checkpoints"
    checkpoint_name: str = "npgs_sft.pt"
    legacy_checkpoint_profile: str | None = None
    silence_console: bool = True
    npgs: NPGSConfig = field(default_factory=NPGSConfig)
    pretrain: PretrainConfig = field(default_factory=PretrainConfig)

    presets: tuple[str, ...] | None = None
    """Явный список имён пресетов для захвата. `None` — все откалиброванные.

    Нужен, чтобы снимать матрицу прогонов частями: шифры настраиваются не все сразу, и
    доснять один режим должно быть дешевле, чем перезапустить весь SFT."""
    include_drafts: bool = False
    """Устаревший флаг совместимости. SFT никогда не принимает draft/tuned профили."""
    backend: str = "xplane"
    start: str = "rollout"
    xplane_root: str | None = None
    aircraft_profile: str = "a330-300"
    runway_profile: str = "uuee-06r"


def build_scenarios(cfg: PretrainRunConfig) -> list:
    """Список сценариев для захвата: отобранные пресеты × повторные прогоны."""
    selected = _selected_presets(cfg)
    return [replace(base, scenario_id=f"{base.scenario_id}-v{v:02d}")
            for base in selected for v in range(cfg.variants_per_preset)]


def _selected_presets(cfg: PretrainRunConfig) -> list:
    """Пресеты для захвата по конфигурации, с явным отчётом о том, что отброшено."""
    if cfg.include_drafts:
        raise ValueError("SFT допускает только ControlProfile со статусом accepted")
    if cfg.presets is not None:
        unknown = [n for n in cfg.presets if n not in SCENARIOS]
        if unknown:
            raise KeyError(f"неизвестные пресеты для SFT: {unknown}")
        chosen = [SCENARIOS[n] for n in cfg.presets]
    else:
        chosen = list(SCENARIOS.values())

    # NPGS controls the ground rollout only.  Approach-only and taxi-only
    # matrix cases have no rollout expert label and must not enter SFT.
    chosen = [
        scenario for scenario in chosen
        if not scenario.matrix_codes or FlightSegment.ROLLOUT in scenario.matrix_codes
    ]

    rejected = [
        s for s in chosen
        if not s.is_accepted(cfg.aircraft_profile, FlightSegment.ROLLOUT)
    ]
    if rejected:
        names = ", ".join(s.scenario_id for s in rejected)
        print(f"[SFT] пропущены не-accepted пресеты ({len(rejected)}): {names}")
        chosen = [
            s for s in chosen
            if s.is_accepted(cfg.aircraft_profile, FlightSegment.ROLLOUT)
        ]
    if not chosen:
        raise ValueError("для SFT не осталось ни одного пресета")
    return chosen


def matrix_preset_names(
    *,
    only_calibrated: bool = True,
    aircraft_profile: str = "mc21",
) -> tuple[str, ...]:
    """Имена наземных пресетов матрицы прогонов (пригодных для SFT) в порядке матрицы.

    Заход сюда не входит: его коэффициенты статические и в пространство действий NPGS не входят
    (см. `config/run_matrix.ground_cases`).
    """
    from ismpu.config.run_matrix import ground_cases

    cases = [c for c in ground_cases() if c.preset in SCENARIOS]
    if only_calibrated:
        cases = [
            case for case in cases
            if SCENARIOS[case.preset].is_accepted(
                aircraft_profile,
                FlightSegment.TAXI if case.segment == "taxi" else FlightSegment.ROLLOUT,
            )
        ]
    return tuple(case.preset for case in cases)


def build_capture_stack(cfg: PretrainRunConfig, ip: str | None = None,
                        port: int | None = None, *, backend: str | None = None):
    """(env, net) поверх выбранного backend; env без Shield (чистая классика)."""
    from ismpu.control.system import ControllingSystem
    from ismpu.envs.backend_factory import build_sim
    from ismpu.envs.rollout_env import RolloutEnv
    from ismpu.config.regulators import validate_action_contract

    validate_action_contract()   # контракт обучаемого слоя — до захвата, а не после

    sim = build_sim(
        backend or cfg.backend,
        ip=ip,
        port=port,
        xplane_root=cfg.xplane_root,
        aircraft_profile=cfg.aircraft_profile,
        runway_profile=cfg.runway_profile,
    )
    controller = ControllingSystem(sim)
    env = RolloutEnv(sim, controller, history_len=cfg.npgs.window, shield=None)
    net_cfg = replace(cfg.npgs, aircraft_profile=cfg.aircraft_profile)
    net = NPGS(net_cfg, gain_space=env.gain_space)
    return env, net


def run_pretrain(cfg: PretrainRunConfig | None = None, ip: str | None = None,
                 port: int | None = None):
    """Полный SFT: захват на стенде → BC → чекпоинт. → (net, dataset, history)."""
    from ismpu.runtime.train import silence_control_console

    cfg = cfg or PretrainRunConfig()
    if cfg.silence_console:
        silence_control_console()

    env, net = build_capture_stack(cfg, ip=ip, port=port)
    try:
        scenarios = build_scenarios(cfg)
        dataset, reports = capture_dataset(env, scenarios, max_steps=cfg.max_steps)
        kept = [r for r in reports if r["weight"] > 0.0]
        caveated = [r for r in kept if r["reasons"]]
        print(f"SFT dataset: {len(dataset)} окон из {len(kept)}/{len(scenarios)} прогонов "
              f"(отброшено {len(reports) - len(kept)}, с оговорками {len(caveated)})")
        history = pretrain_sft(net, dataset, cfg.pretrain)
        profile_checkpoint_dir = os.path.join(cfg.checkpoint_dir, cfg.aircraft_profile)
        os.makedirs(profile_checkpoint_dir, exist_ok=True)
        path = os.path.join(profile_checkpoint_dir, cfg.checkpoint_name)
        net.source_scenarios = tuple(dict.fromkeys(s.scenario_id.split("-v", 1)[0] for s in scenarios))
        net.save(path)
        print(f"SFT готово: mse {history[-1]['mse']:.5f} → {path}")
    finally:
        env.close()
    return net, dataset, history


def smoke_pretrain(env, scenarios, *, npgs: NPGS | None = None,
                   pretrain: PretrainConfig | None = None, max_steps: int = 200):
    """Оффлайн SFT на поданной среде (без стенда) — для тестов/отладки. → (net, dataset, history)."""
    net = npgs or NPGS(
        NPGSConfig(window=env.history_len, aircraft_profile=env.sim.aircraft_profile_name),
        gain_space=env.gain_space,
    )
    dataset, _reports = capture_dataset(env, scenarios, max_steps=max_steps, log=None)
    history = pretrain_sft(net, dataset, pretrain or PretrainConfig(epochs=3, batch_size=64, device="cpu"))
    return net, dataset, history


if __name__ == "__main__":
    run_pretrain()
