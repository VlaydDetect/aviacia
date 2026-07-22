"""Оркестрация SFT-подогрева NPGS (план Stage B): захват классических прогонов на стенде →
behavioral cloning на эталонных коэффициентах пресетов → чекпоинт для `train.py init_from`.

Запуск (нужен работающий стенд):  python -m ismpu.runtime.pretrain
Оффлайн-валидация без стенда — `smoke_pretrain(env, scenarios, ...)` (среду подаёт вызывающий).

Разметка (канонная): каждый **не-draft** пресет `SCENARIO_PRESETS` = отдельный режим/метка,
цель = его собственные коэффициенты. Каждый пресет прогоняется по нескольку раз: разнообразие
наблюдений даёт сам стенд (расстановка, ветер, шум датчиков от прогона к прогону не повторяются),
а метка при этом не меняется. Отсев ещё-не-выверенных пресетов — через флаг
`ScenarioConfig.draft`, НЕ по названию.

**Условия задаёт оператор стенда.** `build_scenarios` перечисляет, какие режимы надо снять; в
каких именно условиях стенд их выдаст, мы не выбираем — сверяться с фактическими условиями
эпизода нужно по телеметрии (`Telemetry.weather` / `Telemetry.faults`), а прогоны, не
соответствующие своему пресету, отсеивает оценка качества в `capture.py`.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field, replace

from ismpu.agent.gain_scheduler import NPGS, NPGSConfig
from ismpu.agent.pretrain import pretrain_sft, PretrainConfig, SFTDataset
from ismpu.runtime.capture import capture_dataset
from ismpu.envs.scenario import SCENARIO_PRESETS


@dataclass
class PretrainRunConfig:
    variants_per_preset: int = 20      # прогонов на пресет (разнообразие obs)
    max_steps: int = 3000              # макс. тактов на прогон
    seed: int = 0
    checkpoint_dir: str = "checkpoints"
    checkpoint_name: str = "npgs_sft.pt"
    silence_console: bool = True
    npgs: NPGSConfig = field(default_factory=NPGSConfig)
    pretrain: PretrainConfig = field(default_factory=PretrainConfig)


def build_scenarios(cfg: PretrainRunConfig) -> list:
    """Список сценариев для захвата: не-draft пресеты × повторные прогоны."""
    presets = [s for s in SCENARIO_PRESETS.values() if not s.control.draft]
    return [replace(base, scenario_id=f"{base.scenario_id}-v{v:02d}")
            for base in presets for v in range(cfg.variants_per_preset)]


def build_capture_stack(cfg: PretrainRunConfig, ip: str = "127.0.0.1", port: int = 3030):
    """(env, net) поверх стенда; env без Shield (чистая классика). Требует работающий стенд."""
    from ismpu.control.system import ControllingSystem
    from ismpu.envs.ics_sim import ICSSim
    from ismpu.envs.rollout_env import RolloutEnv
    from ismpu.config.regulators import validate_action_contract

    validate_action_contract()   # контракт обучаемого слоя — до захвата, а не после

    sim = ICSSim(listen_ip=ip, listen_port=port)
    controller = ControllingSystem(sim)
    env = RolloutEnv(sim, controller, history_len=cfg.npgs.window, shield=None)
    net = NPGS(cfg.npgs)
    return env, net


def run_pretrain(cfg: PretrainRunConfig | None = None, ip: str = "127.0.0.1", port: int = 3030):
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
        os.makedirs(cfg.checkpoint_dir, exist_ok=True)
        path = os.path.join(cfg.checkpoint_dir, cfg.checkpoint_name)
        net.save(path)
        print(f"SFT готово: mse {history[-1]['mse']:.5f} → {path}")
    finally:
        env.close()
    return net, dataset, history


def smoke_pretrain(env, scenarios, *, npgs: NPGS | None = None,
                   pretrain: PretrainConfig | None = None, max_steps: int = 200):
    """Оффлайн SFT на поданной среде (без стенда) — для тестов/отладки. → (net, dataset, history)."""
    net = npgs or NPGS(NPGSConfig(window=env.history_len))
    dataset, _reports = capture_dataset(env, scenarios, max_steps=max_steps, log=None)
    history = pretrain_sft(net, dataset, pretrain or PretrainConfig(epochs=3, batch_size=64, device="cpu"))
    return net, dataset, history


if __name__ == "__main__":
    run_pretrain()
