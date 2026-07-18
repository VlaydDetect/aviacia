"""Оркестрация SFT-подогрева NPGS (план Stage B): захват классических прогонов в X-Plane →
behavioral cloning на эталонных коэффициентах пресетов → чекпоинт для `train.py init_from`.

Запуск (нужен X-Plane 12):  python -m ismpu.runtime.pretrain
Оффлайн-валидация без X-Plane — `smoke_pretrain(env, scenarios, ...)` (среду подаёт вызывающий).

Разметка (канонная): каждый **не-draft** пресет `SCENARIO_PRESETS` = отдельный режим/метка,
цель = его собственные коэффициенты. Каждый пресет прогоняется в СВОИХ условиях с лёгкой
рандомизацией касания (разнообразие obs, метку не меняет). Отсев ещё-не-выверенных пресетов —
через флаг `ScenarioConfig.draft`, НЕ по названию.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field, replace

import numpy as np

from ismpu.agent.gain_scheduler import NPGS, NPGSConfig
from ismpu.agent.pretrain import pretrain_sft, PretrainConfig, SFTDataset
from ismpu.runtime.capture import capture_dataset
from ismpu.envs.scenario import SCENARIO_PRESETS, TouchdownSetup


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
    """Список сценариев для захвата: не-draft пресеты × варианты со случайным касанием."""
    presets = [s for s in SCENARIO_PRESETS.values() if not s.control.draft]
    rng = np.random.default_rng(cfg.seed)
    scenarios = []
    for base in presets:
        for v in range(cfg.variants_per_preset):
            td = TouchdownSetup(
                lateral_offset_m=float(rng.uniform(-2.0, 2.0)),
                heading_offset_deg=float(rng.uniform(-2.0, 2.0)),
            )
            scenarios.append(replace(base, scenario_id=f"{base.scenario_id}-v{v:02d}", touchdown=td))
    return scenarios


def build_capture_stack(cfg: PretrainRunConfig, ip: str = "127.0.0.1", port: int = 49000):
    """(env, net) на общем коннекторе X-Plane; env без Shield (чистая классика). Требует X-Plane."""
    from ismpu.io.xplane_connector import XPlaneConnectX
    from ismpu.control.system import ControllingSystem
    from ismpu.envs.sim_interface import XPlaneBackend
    from ismpu.envs.rollout_env import RolloutEnv

    xpc = XPlaneConnectX(ip=ip, port=port)
    sim = XPlaneBackend(xpc=xpc)
    controller = ControllingSystem(xpc=xpc)
    env = RolloutEnv(sim, controller, history_len=cfg.npgs.window, shield=None)
    net = NPGS(cfg.npgs)
    return env, net


def run_pretrain(cfg: PretrainRunConfig | None = None, ip: str = "127.0.0.1", port: int = 49000):
    """Полный SFT: захват в X-Plane → BC → чекпоинт. → (net, dataset, history)."""
    from ismpu.runtime.train import silence_control_console

    cfg = cfg or PretrainRunConfig()
    if cfg.silence_console:
        silence_control_console()

    env, net = build_capture_stack(cfg, ip=ip, port=port)
    try:
        scenarios = build_scenarios(cfg)
        dataset = capture_dataset(env, scenarios, max_steps=cfg.max_steps)
        print(f"SFT dataset: {len(dataset)} окон из {len(scenarios)} прогонов")
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
    """Оффлайн SFT на поданной среде (без X-Plane) — для тестов/отладки. → (net, dataset, history)."""
    net = npgs or NPGS(NPGSConfig(window=env.history_len))
    dataset = capture_dataset(env, scenarios, max_steps=max_steps, log=None)
    history = pretrain_sft(net, dataset, pretrain or PretrainConfig(epochs=3, batch_size=64, device="cpu"))
    return net, dataset, history


if __name__ == "__main__":
    run_pretrain()
