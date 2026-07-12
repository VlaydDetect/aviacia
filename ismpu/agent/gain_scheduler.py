"""Neural PID Gain Scheduler (NPGS) — актор + критик (план §10).

Планировщик коэффициентов: PID остаётся классическим plant'ом, сеть лишь
**предсказывает мультипликативные поправки** к его коэффициентам (+ веса каналов).
Это НЕ классический PIDNN (передаточная функция PID в сеть не встраивается — запрет ТЗ).

Поток (общий энкодер, актор и критик делят его):
    obs (B, T, 56)
      → LayerNorm по признакам кадра
      → Feature Encoder  Linear(56→256)→GELU→Linear(256→256)→GELU (+residual), time-distributed
      → GRU(256, 2 слоя)
      → MultiHeadAttention(256, 4 heads) + residual → attention-пулинг → (B, 256)
      → Shared trunk  Linear(256→256)→GELU→Linear(256→128)→GELU (+skip) → z_shared (B, 128)
      → Context Fusion  Linear(128→128)→GELU → c (B, 128)   (+ опц. голова фазы движения)
    Головы (вход [z_shared ⊕ c], 256):
      Heading→α(runway_center,3) · Brake→α(3, дубль L/R) · Reverse→α(3, дубль L/R) · Weights→(w_lon,w_lat)
      = 11 выходов политики → детерминированно разворачиваются в 17-мерный `Corrections`.
    Критик — голова от z_shared: Linear(128→64)→GELU→Linear(64→1) → V(s).

Ограничение выхода (гладко, = уровень 1 Shield):
    α = 1 + Δα_max·tanh(z) → [0.5, 1.5]   (Δα_max = 0.5)
    w = 1 + tanh(z)        → [0, 2]
Голова mean инициализируется малым orthogonal-gain → на старте z≈0 ⇒ α≈1, w≈1
(инвариант identity, §1: старт обучения ≈ классика).

Политика — tanh-squashed Gaussian: `mean` из голов, `log_std` обучаемый вектор
(state-independent, init ≈ −0.5). Greedy (поставка) = mean, без сэмплинга.

Для PPO наружу отдаётся сэмпл `u` (11-мерный, ДО ограничения) — по нему пересчитывается
log-prob на апдейте; в среду уходит развёрнутый ограниченный 17-мерный вектор.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, asdict

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from ismpu.envs.observation import OBS_DIM
from ismpu.agent.shield import ACTION_DIM, REGULATOR_ORDER
from ismpu.agent import normalization as norm

# Разбивка 11 выходов политики: 3 heading + 3 brake + 3 reverse + 2 weights.
N_HEADING, N_BRAKE, N_REVERSE, N_WEIGHTS = 3, 3, 3, 2
N_ALPHA_OUT = N_HEADING + N_BRAKE + N_REVERSE   # 9 множителей α (до дублирования L/R)
POLICY_DIM = N_ALPHA_OUT + N_WEIGHTS            # 11 выходов политики
N_PHASES = 5                                    # касание / скоростной / средний / руление / стоп

# Фазы движения (метки для опц. вспомогательной задачи, метки из groundspeed).
PHASE_TOUCHDOWN, PHASE_HIGH, PHASE_MID, PHASE_TAXI, PHASE_STOP = range(N_PHASES)
_PHASE_BOUNDS_KTS = (150.0, 90.0, 30.0, 5.0)    # верхние границы фаз (убыв.) → метка


@dataclass
class NPGSConfig:
    """Гиперпараметры архитектуры NPGS (замораживаются вместе с весами при поставке)."""
    obs_dim: int = OBS_DIM
    window: int = 16              # T кадров истории (≈0.8 с при 20 Гц)
    d_model: int = 256
    gru_layers: int = 2
    attn_heads: int = 4
    trunk_dim: int = 128
    context_dim: int = 128
    head_hidden: tuple = (64, 32)
    n_phases: int = N_PHASES
    dropout: float = 0.0          # в RL dropout вредит политике; по умолчанию нет
    log_std_init: float = -0.5
    delta_alpha_max: float = 0.5  # α ∈ [1−Δ, 1+Δ] = [0.5, 1.5] (уровень 1 Shield)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "NPGSConfig":
        d = dict(d)
        if "head_hidden" in d:
            d["head_hidden"] = tuple(d["head_hidden"])
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


def layer_init(layer: nn.Linear, gain: float = math.sqrt(2.0), bias: float = 0.0) -> nn.Linear:
    """Orthogonal-инициализация (лучшая практика PPO): скрытые √2, mean-голова 0.01, value 1.0."""
    nn.init.orthogonal_(layer.weight, gain)
    nn.init.constant_(layer.bias, bias)
    return layer


def _mlp_head(in_dim: int, hidden: tuple, out_dim: int, out_gain: float) -> nn.Sequential:
    layers, d = [], in_dim
    for h in hidden:
        layers += [layer_init(nn.Linear(d, h)), nn.GELU()]
        d = h
    layers.append(layer_init(nn.Linear(d, out_dim), gain=out_gain))
    return nn.Sequential(*layers)


def phase_labels_from_groundspeed_kts(gs_kts) -> np.ndarray:
    """Метка фазы движения по путевой скорости (для вспомогательной задачи, §10)."""
    gs = np.asarray(gs_kts, dtype=np.float32)
    label = np.full(gs.shape, PHASE_STOP, dtype=np.int64)
    hi, mid, taxi, stop = _PHASE_BOUNDS_KTS
    label = np.where(gs >= hi, PHASE_TOUCHDOWN, label)
    label = np.where((gs < hi) & (gs >= mid), PHASE_HIGH, label)
    label = np.where((gs < mid) & (gs >= taxi), PHASE_MID, label)
    label = np.where((gs < taxi) & (gs >= stop), PHASE_TAXI, label)
    return label


class NPGS(nn.Module):
    """Neural PID Gain Scheduler: общий энкодер + головы актора + голова критика."""

    def __init__(self, config: NPGSConfig | None = None):
        super().__init__()
        cfg = config or NPGSConfig()
        self.cfg = cfg
        d = cfg.d_model

        # --- Общий энкодер ---
        self.input_norm = nn.LayerNorm(cfg.obs_dim)
        self.enc1 = layer_init(nn.Linear(cfg.obs_dim, d))
        self.enc2 = layer_init(nn.Linear(d, d))
        self.gru = nn.GRU(d, d, num_layers=cfg.gru_layers, batch_first=True)
        self.attn = nn.MultiheadAttention(d, cfg.attn_heads, batch_first=True)
        self.attn_norm = nn.LayerNorm(d)
        self.pool_query = nn.Parameter(torch.randn(d) * 0.02)   # обучаемый запрос attention-пулинга
        self.trunk1 = layer_init(nn.Linear(d, d))
        self.trunk2 = layer_init(nn.Linear(d, cfg.trunk_dim))
        self.trunk_skip = layer_init(nn.Linear(d, cfg.trunk_dim))
        self.dropout = nn.Dropout(cfg.dropout) if cfg.dropout > 0 else nn.Identity()

        # --- Context Fusion (фаза движения) ---
        self.context = layer_init(nn.Linear(cfg.trunk_dim, cfg.context_dim))
        self.phase_head = _mlp_head(cfg.context_dim, (64,), cfg.n_phases, out_gain=0.01)

        # --- Головы актора (вход [z_shared ⊕ c]) ---
        head_in = cfg.trunk_dim + cfg.context_dim
        self.head_heading = _mlp_head(head_in, cfg.head_hidden, N_HEADING, out_gain=0.01)
        self.head_brake = _mlp_head(head_in, cfg.head_hidden, N_BRAKE, out_gain=0.01)
        self.head_reverse = _mlp_head(head_in, cfg.head_hidden, N_REVERSE, out_gain=0.01)
        self.head_weights = _mlp_head(head_in, cfg.head_hidden, N_WEIGHTS, out_gain=0.01)
        self.log_std = nn.Parameter(torch.full((POLICY_DIM,), float(cfg.log_std_init)))

        # --- Критик (голова от z_shared) ---
        self.critic = _mlp_head(cfg.trunk_dim, (64,), 1, out_gain=1.0)

    # ------------------------------------------------------------------ #
    # Энкодер
    # ------------------------------------------------------------------ #

    def encode(self, obs: torch.Tensor):
        """obs (B, T, 56) → (z_shared (B,128), c (B,128), phase_logits (B,n_phases))."""
        if obs.dim() == 2:               # (T, 56) → (1, T, 56)
            obs = obs.unsqueeze(0)
        x = self.input_norm(obs)
        h = F.gelu(self.enc1(x))
        h = F.gelu(self.enc2(h)) + h     # residual, time-distributed
        h = self.dropout(h)

        seq, _ = self.gru(h)             # (B, T, d)
        a, _ = self.attn(seq, seq, seq)  # self-attention по времени
        a = self.attn_norm(a + seq)      # residual + norm

        scores = torch.einsum("btd,d->bt", a, self.pool_query) / math.sqrt(self.cfg.d_model)
        w = torch.softmax(scores, dim=1)
        pooled = torch.einsum("bt,btd->bd", w, a)   # attention-пулинг → (B, d)

        t = F.gelu(self.trunk1(pooled))
        t = F.gelu(self.trunk2(t))
        z_shared = t + self.trunk_skip(pooled)      # (B, trunk_dim)

        c = F.gelu(self.context(z_shared))          # контекст фазы (B, context_dim)
        phase_logits = self.phase_head(c)
        return z_shared, c, phase_logits

    def forward(self, obs: torch.Tensor):
        """→ (mean (B,11), value (B,), phase_logits (B,n_phases))."""
        z_shared, c, phase_logits = self.encode(obs)
        head_in = torch.cat([z_shared, c], dim=-1)
        mean = torch.cat([
            self.head_heading(head_in),
            self.head_brake(head_in),
            self.head_reverse(head_in),
            self.head_weights(head_in),
        ], dim=-1)                                  # (B, 11)
        value = self.critic(z_shared).squeeze(-1)   # (B,)
        return mean, value, phase_logits

    # ------------------------------------------------------------------ #
    # Ограничение выхода и разворот в 17-мерное действие
    # ------------------------------------------------------------------ #

    def bound(self, u: torch.Tensor) -> torch.Tensor:
        """11 сырых выходов → ограниченные поправки: α=1+Δ·tanh, w=1+tanh."""
        alpha = 1.0 + self.cfg.delta_alpha_max * torch.tanh(u[..., :N_ALPHA_OUT])
        weight = 1.0 + torch.tanh(u[..., N_ALPHA_OUT:])
        return torch.cat([alpha, weight], dim=-1)

    @staticmethod
    def expand_to_action(bounded: torch.Tensor) -> torch.Tensor:
        """11 ограниченных поправок → 17-мерный вектор (layout `Corrections`/`REGULATOR_ORDER`).

        Тормоза и реверс симметричны (§1 принцип 2): один набор α дублируется на L/R.
        Порядок: runway_center(3) · brake_l(3) · brake_r(3) · rev_l(3) · rev_r(3) · w_lon · w_lat.
        """
        heading = bounded[..., 0:3]
        brake = bounded[..., 3:6]
        reverse = bounded[..., 6:9]
        weights = bounded[..., 9:11]
        return torch.cat([heading, brake, brake, reverse, reverse, weights], dim=-1)

    # ------------------------------------------------------------------ #
    # Политика: сэмплирование, оценка, log-prob (tanh-squashed Gaussian)
    # ------------------------------------------------------------------ #

    def _dist(self, mean: torch.Tensor):
        std = torch.exp(self.log_std).expand_as(mean)
        return torch.distributions.Normal(mean, std)

    @staticmethod
    def _logprob(dist, u: torch.Tensor) -> torch.Tensor:
        """log π(u) с tanh-поправкой −Σ log(1 − tanh²(u)) (изменение переменных)."""
        logp = dist.log_prob(u).sum(-1)
        logp = logp - torch.log(1.0 - torch.tanh(u) ** 2 + 1e-6).sum(-1)
        return logp

    def get_action(self, obs: torch.Tensor, deterministic: bool = False):
        """Один шаг актора. Возвращает dict с 17-мерным действием и величинами для PPO.

        - `action` (…, 17) — ограниченное действие для среды (`decode`/`Shield`);
        - `raw` (…, 11)    — сэмпл `u` ДО ограничения (хранится в буфере PPO);
        - `logp`, `value`, `entropy`, `phase_logits`.
        """
        mean, value, phase_logits = self.forward(obs)
        dist = self._dist(mean)
        u = mean if deterministic else dist.rsample()
        action = self.expand_to_action(self.bound(u))
        logp = self._logprob(dist, u)
        entropy = dist.entropy().sum(-1)   # базовая Gaussian-энтропия (бонус)
        return {"action": action, "raw": u, "logp": logp, "value": value,
                "entropy": entropy, "phase_logits": phase_logits, "mean": mean}

    def evaluate_actions(self, obs: torch.Tensor, u: torch.Tensor):
        """Пересчёт на апдейте PPO для сохранённых `u`. → (logp, entropy, value, mean, phase_logits)."""
        mean, value, phase_logits = self.forward(obs)
        dist = self._dist(mean)
        logp = self._logprob(dist, u)
        entropy = dist.entropy().sum(-1)
        return logp, entropy, value, mean, phase_logits

    # ------------------------------------------------------------------ #
    # Инференс из numpy (среда/поставка) и сериализация
    # ------------------------------------------------------------------ #

    @torch.no_grad()
    def act_numpy(self, obs_window: np.ndarray, deterministic: bool = False):
        """obs (T,56) np → (action_17 np, raw_11 np, logp float, value float)."""
        device = self.log_std.device
        obs = torch.as_tensor(obs_window, dtype=torch.float32, device=device)
        out = self.get_action(obs, deterministic=deterministic)
        return (out["action"].squeeze(0).cpu().numpy(),
                out["raw"].squeeze(0).cpu().numpy(),
                float(out["logp"].item()), float(out["value"].item()))

    def save(self, path: str) -> None:
        """Веса + конфиг + слепок нормировки одним артефактом (детерминизм поставки, §14)."""
        torch.save({"state_dict": self.state_dict(), "config": self.cfg.to_dict(),
                    "normalization": norm.snapshot()}, path)

    @classmethod
    def load(cls, path: str, map_location=None) -> "NPGS":
        ckpt = torch.load(path, map_location=map_location, weights_only=False)
        model = cls(NPGSConfig.from_dict(ckpt["config"]))
        model.load_state_dict(ckpt["state_dict"])
        model.eval()
        return model


def build_npgs(config: NPGSConfig | None = None, device: str = "cpu") -> NPGS:
    model = NPGS(config).to(device)
    assert POLICY_DIM == 11 and len(REGULATOR_ORDER) * 3 + 2 == ACTION_DIM == 17
    return model
