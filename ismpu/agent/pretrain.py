"""SFT (behavioral cloning) — предобучение NPGS предсказывать эталонные коэффициенты PID.

Цель = абсолютные коэффициенты пресета сценария (эксперт), инвертированные в pre-squash `z`
через `gain_space.inv_gain`; сеть регрессирует `mean → target_z` (MSE). Так PPO стартует не с
DEFAULT, а уже у экспертных gain'ов под внешнее воздействие → быстрее сходится.

**Анти-копирование (ключевой риск).** obs содержит «прошлые коэффициенты» (лог-норма gain'ов),
а цель постоянна на прогон → сеть может свести loss к нулю, копируя вход. Поэтому в SFT
gain-признаки obs **заменяются свежим шумом** `U(−1,1)` на каждом батче (`mask_prev_gains`):
шум некоррелирован с целью, и сеть вынуждена предсказывать её из внешнего воздействия
(отказы/погода) и динамики. Важно: шум, а НЕ ноль — реальные значения на инференсе тоже лежат
в `[−1,1]`, поэтому нет сдвига распределения train↔inference (сеть просто игнорирует эти входы).

`log_std` при SFT заморожен (регрессия трогает только `mean`/критика/фазу). Артефакт —
`net.save` (несёт config + слепок gain-пространства), его затем грузит PPO (`init_from`).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import torch
import torch.nn.functional as F

from ismpu.agent.gain_scheduler import NPGS, POLICY_DIM, N_GAIN_OUT, phase_labels_from_groundspeed_kts
from ismpu.agent import gain_space
from ismpu.agent.normalization import SPEED_SCALE
from ismpu.envs.observation import GAIN_FEATURE_INDICES, FEATURE_NAMES
from ismpu.config.regulators import REGULATOR_ORDER, GAIN_KEYS
from ismpu.utils.converts import Converts

_GS_IDX = FEATURE_NAMES.index("ground_speed")


def target_z_from_gains(gains: dict) -> np.ndarray:
    """Абсолютные коэффициенты пресета → `target_z` (17,): gains через `inv_gain`, веса → 0 (w=1)."""
    vec = np.array([gains[reg][k] for reg in REGULATOR_ORDER for k in GAIN_KEYS], dtype=np.float64)
    z = np.zeros(POLICY_DIM, dtype=np.float32)
    z[:N_GAIN_OUT] = gain_space.inv_gain(vec).astype(np.float32)   # веса остаются 0 → w=1
    return z


@dataclass
class SFTDataset:
    """Датасет BC: окна наблюдений, постоянные (на прогон) целевые `target_z` и вес качества.

    `weight` — доверие к метке (1.0 чистый прогон / 0.5 с оговорками); прогоны, нарушившие
    гейт ТЗ, отбрасываются ещё на захвате (`runtime.capture`). Без этого BC клонирует и
    плохие траектории тоже: пресет вне своего режима даёт метку, которую воспроизводить не надо.
    """
    obs: np.ndarray        # (N, T, 56) float32
    target_z: np.ndarray   # (N, 17)   float32
    weight: np.ndarray | None = None   # (N,) float32; None ≡ все единицы

    def __post_init__(self):
        if self.weight is None:
            self.weight = np.ones(len(self.obs), dtype=np.float32)
        self.weight = np.asarray(self.weight, dtype=np.float32).reshape(-1)
        if len(self.weight) != len(self.obs):
            raise ValueError(f"weight ({len(self.weight)}) не совпадает с obs ({len(self.obs)})")

    def __len__(self) -> int:
        return len(self.obs)

    @classmethod
    def concat(cls, parts: list["SFTDataset"]) -> "SFTDataset":
        parts = [p for p in parts if len(p)]
        if not parts:
            return cls(np.zeros((0, 0, 0), dtype=np.float32),
                       np.zeros((0, POLICY_DIM), dtype=np.float32))
        return cls(np.concatenate([p.obs for p in parts]),
                   np.concatenate([p.target_z for p in parts]),
                   np.concatenate([p.weight for p in parts]))


@dataclass
class PretrainConfig:
    epochs: int = 30
    batch_size: int = 256
    lr: float = 1e-3
    mask_prev_gains: bool = True    # анти-копирование: глушить gain-признаки obs нулём
    lambda_phase: float = 0.0       # опц. вспом. задача фазы (метки из groundspeed)
    seed: int = 0
    device: str = "cuda"


def _phase_labels(obs: torch.Tensor) -> torch.Tensor:
    gs_kts = (obs[:, -1, _GS_IDX].cpu().numpy() * SPEED_SCALE) * Converts.MS_TO_KTS
    return torch.as_tensor(phase_labels_from_groundspeed_kts(gs_kts), device=obs.device)


def pretrain_sft(net: NPGS, dataset: SFTDataset, config: PretrainConfig | None = None) -> list[dict]:
    """BC-обучение `net` на `dataset` (регрессия mean → target_z). → история по эпохам."""
    cfg = config or PretrainConfig()
    if cfg.device == "cuda" and not torch.cuda.is_available():
        cfg.device = "cpu"
    device = torch.device(cfg.device)
    net.to(device).train()

    # log_std не участвует в регрессии.
    net.log_std.requires_grad_(False)
    params = [p for n, p in net.named_parameters() if "log_std" not in n]
    opt = torch.optim.AdamW(params, lr=cfg.lr, eps=1e-5)

    obs = torch.as_tensor(dataset.obs, dtype=torch.float32, device=device)
    tz = torch.as_tensor(dataset.target_z, dtype=torch.float32, device=device)
    wq = torch.as_tensor(dataset.weight, dtype=torch.float32, device=device)
    gain_idx = torch.as_tensor(GAIN_FEATURE_INDICES, device=device)
    phase_lab = _phase_labels(obs) if cfg.lambda_phase > 0 else None

    n = len(obs)
    rng = np.random.default_rng(cfg.seed)
    history: list[dict] = []
    for epoch in range(cfg.epochs):
        idx = rng.permutation(n)
        mse_sum, ph_sum, nb = 0.0, 0.0, 0
        for start in range(0, n, cfg.batch_size):
            mb = torch.as_tensor(idx[start:start + cfg.batch_size], device=device)
            x = obs[mb]
            if cfg.mask_prev_gains:               # анти-копирование: gain-признаки → свежий шум U(−1,1)
                x = x.clone()
                noise = torch.empty((x.shape[0], x.shape[1], len(GAIN_FEATURE_INDICES)),
                                    device=device).uniform_(-1.0, 1.0)
                x[..., gain_idx] = noise
            mean, _, phase_logits = net(x)
            # Взвешенный MSE: метка с оговорками (0.5) тянет градиент вдвое слабее чистой.
            # Нормировка на сумму весов, а не на размер батча, — иначе эффективный LR
            # плавал бы вместе с долей «сомнительных» строк в батче.
            w = wq[mb].unsqueeze(1)
            mse = (w * (mean - tz[mb]) ** 2).sum() / (w.sum() * mean.shape[1] + 1e-8)
            loss = mse
            ph = torch.zeros((), device=device)
            if phase_lab is not None:
                ph = F.cross_entropy(phase_logits, phase_lab[mb])
                loss = loss + cfg.lambda_phase * ph
            opt.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(params, 1.0)
            opt.step()
            mse_sum += float(mse.item()); ph_sum += float(ph.item()); nb += 1
        history.append({"epoch": epoch, "mse": mse_sum / max(1, nb), "phase": ph_sum / max(1, nb)})

    net.log_std.requires_grad_(True)
    net.eval()
    return history
