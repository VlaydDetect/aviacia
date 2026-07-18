"""Цикл обучения NPGS через PPO с domain randomization (план §11, Этап 4).

Собирает тренировочный стек: **один** коннектор X-Plane, разделяемый бэкендом
`XPlaneBackend` и классическим контуром `ControllingSystem` (среда шлёт команды через
`SimInterface.step`, а контур читает телеметрию из того же `xpc.current_dref_values`,
поэтому коннектор обязан быть общим), `RolloutEnv` со Shield в inference-пути и NPGS.
Учебный план (curriculum) поднимает `difficulty` от 0 к 1 по ходу обучения через
`ScenarioGenerator`. Чекпоинты и CSV-лог по каждому терму — в `checkpoint_dir`.

Запуск реального обучения (нужен X-Plane 12 на 127.0.0.1:49000):
    python -m ismpu.runtime.train

Оффлайн-валидация цикла PPO без X-Plane — `smoke_train(env, provider, ...)`
(среду подаёт вызывающий; используется в тестах).
"""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass, field

from ismpu.agent.gain_scheduler import NPGS, NPGSConfig
from ismpu.agent.ppo import PPOTrainer, PPOConfig
from ismpu.agent.shield import Shield


@dataclass
class TrainConfig:
    total_updates: int = 400
    seed: int = 0
    curriculum_ramp: float = 0.6      # доля обучения, за которую difficulty 0→1
    checkpoint_dir: str = "checkpoints"
    checkpoint_every: int = 20
    silence_console: bool = True      # заглушить cprint контура (иначе флуд на 20 Гц×5)
    init_from: str | None = None      # SFT-чекпоинт (npgs_sft.pt) — тёплый старт перед PPO
    npgs: NPGSConfig = field(default_factory=NPGSConfig)
    ppo: PPOConfig = field(default_factory=PPOConfig)


def silence_control_console() -> None:
    """Гасит потактовый `cprint` контура (PID/каналы) — критично для скорости обучения.

    Не трогает исходники: заменяет импортированную ссылку `cprint` на no-op в модулях
    контура. Реальный лог доступен через `logging` (`ismpu.control.pid`).
    """
    noop = lambda *a, **k: None
    for modname in ("ismpu.control.pid", "ismpu.control.channels"):
        try:
            import importlib
            mod = importlib.import_module(modname)
            if hasattr(mod, "cprint"):
                mod.cprint = noop
        except Exception:
            pass


def make_curriculum_provider(generator, trainer: PPOTrainer, total_updates: int, ramp: float):
    """Возвращает `scenario_provider()`: difficulty растёт с номером апдейта PPO."""
    ramp_updates = max(1, int(total_updates * ramp))

    def provider():
        difficulty = min(1.0, trainer.update_idx / ramp_updates)
        return generator.sample(difficulty)

    return provider


class CSVLogger:
    """Пишет метрики каждого апдейта в CSV (по каждому терму loss/reward)."""

    def __init__(self, path: str):
        self.path = path
        self._writer = None
        self._file = None

    def __call__(self, metrics: dict) -> None:
        if self._writer is None:
            os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
            self._file = open(self.path, "w", newline="", encoding="utf-8")
            self._writer = csv.DictWriter(self._file, fieldnames=list(metrics.keys()))
            self._writer.writeheader()
        self._writer.writerow(metrics)
        self._file.flush()

    def close(self):
        if self._file:
            self._file.close()


# --------------------------------------------------------------------------- #
# X-Plane training stack
# --------------------------------------------------------------------------- #

def build_xplane_stack(cfg: TrainConfig, ip: str = "127.0.0.1", port: int = 49000):
    """Строит (env, npgs, trainer) на общем коннекторе X-Plane. Требует запущенный X-Plane.

    С `cfg.init_from` — грузит SFT-подогретые веса (тёплый старт; конфиг/нормировка берутся
    из чекпоинта). При `ppo.lambda_anchor > 0` замороженная SFT-копия ставится как
    `trainer.sft_reference` (L_anchor — не забывать пресеты)."""
    from ismpu.io.xplane_connector import XPlaneConnectX
    from ismpu.control.system import ControllingSystem
    from ismpu.envs.sim_interface import XPlaneBackend
    from ismpu.envs.rollout_env import RolloutEnv

    net = NPGS.load(cfg.init_from) if cfg.init_from else NPGS(cfg.npgs)

    xpc = XPlaneConnectX(ip=ip, port=port)
    sim = XPlaneBackend(xpc=xpc)               # общий коннектор — обязательное условие обучения
    controller = ControllingSystem(xpc=xpc)
    env = RolloutEnv(sim, controller, history_len=net.cfg.window, shield=Shield())

    trainer = PPOTrainer(net, cfg.ppo, total_updates=cfg.total_updates)
    if cfg.init_from and cfg.ppo.lambda_anchor > 0:
        ref = NPGS.load(cfg.init_from, map_location=trainer.device)
        for p in ref.parameters():
            p.requires_grad_(False)
        trainer.sft_reference = ref.to(trainer.device)
    return env, net, trainer


def train(cfg: TrainConfig | None = None, ip: str = "127.0.0.1", port: int = 49000) -> PPOTrainer:
    """Полный цикл обучения на X-Plane с curriculum, логом и чекпоинтами."""
    from ismpu.envs.scenario_generator import ScenarioGenerator

    cfg = cfg or TrainConfig()
    if cfg.silence_console:
        silence_control_console()

    env, net, trainer = build_xplane_stack(cfg, ip=ip, port=port)
    generator = ScenarioGenerator(seed=cfg.seed)
    provider = make_curriculum_provider(generator, trainer, cfg.total_updates, cfg.curriculum_ramp)

    os.makedirs(cfg.checkpoint_dir, exist_ok=True)
    logger = CSVLogger(os.path.join(cfg.checkpoint_dir, "train_log.csv"))

    def on_update(metrics: dict):
        logger(metrics)
        print(f"upd {metrics['update']:>4} | step {metrics['global_step']:>8} | "
              f"R {metrics.get('ep_return_mean', float('nan')):+8.2f} | "
              f"pg {metrics['pg_loss']:+.3f} v {metrics['v_loss']:.3f} "
              f"ent {metrics['entropy']:.3f} kl {metrics['approx_kl']:.4f} "
              f"smooth {metrics['l_smooth']:.4f} shield% {metrics.get('shield_rate', 0):.2f}")
        if metrics["update"] % cfg.checkpoint_every == 0:
            net.save(os.path.join(cfg.checkpoint_dir, f"npgs_upd{metrics['update']}.pt"))

    try:
        trainer.train(env, provider, cfg.total_updates, callback=on_update)
    finally:
        net.save(os.path.join(cfg.checkpoint_dir, "npgs_final.pt"))
        logger.close()
        env.close()
    return trainer


def smoke_train(env, scenario_provider, *, npgs: NPGS | None = None,
                ppo: PPOConfig | None = None, updates: int = 2) -> PPOTrainer:
    """Оффлайн-прогон цикла PPO на поданной среде (без X-Plane) — для тестов/отладки."""
    net = npgs or NPGS(NPGSConfig(window=env.history_len))
    trainer = PPOTrainer(net, ppo or PPOConfig(rollout_len=64, num_minibatches=4,
                                               update_epochs=2, device="cpu"),
                         total_updates=updates)
    trainer.train(env, scenario_provider, updates)
    return trainer


if __name__ == "__main__":
    cfg = TrainConfig()
    # cfg.silence_console = False
    train(cfg=cfg)
