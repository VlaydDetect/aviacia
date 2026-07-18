"""Neural PID Gain Scheduler (NPGS) — актор + критик (план §10; выход — АБСОЛЮТНЫЕ коэффициенты).

Планировщик коэффициентов: PID остаётся классическим plant'ом, а сеть **предсказывает
абсолютные коэффициенты** его регуляторов (kp/ki/kd × 5) + веса каналов. Это НЕ классический
PIDNN (передаточная функция PID в сеть не встраивается — её считает `PIDController`).

Параметризация выхода (лог-tanh вокруг референса, см. `agent.gain_space`):
    gain_i   = ref_i · exp(s_i · tanh(z_i))   → внутри физической полосы [lo_i, hi_i]
    weight_j = 1 + tanh(z_j)                   → [0, 2]
`ref/s` — из семейства пресетов (геом. середина + лог-полуширина). Головы gain'ов
инициализируются **bias'ом на DEFAULT** (`gain_space.default_bias()`) → при старте выход ≈
классический DEFAULT (безопасный старт; точная классика — через Shield-fallback на пресет).

Поток энкодера без изменений: obs (B,T,56) → LayerNorm → FeatureEncoder → GRU×2 →
MultiheadAttention → attention-пулинг → trunk → z_shared(128) → Context Fusion c(128).
Головы (вход [z_shared⊕c]): Heading→runway_center(3), Brake→L/R(6), Reverse→L/R(6),
Weights→(w_lon,w_lat) = **17 выходов** (= ACTION_DIM; L/R больше НЕ дублируются — асимметрия
тормоза/реверса нужна для reverse-fail пресетов, а симметрию восстанавливает SFT-prior).

Политика (PPO) — Gaussian над сырым `u` (pre-squash); в среду уходит `to_gains(u)`.
`log_std` — обучаемый вектор, инициализируется по слотам так, чтобы шаг исследования был
равномерно-мультипликативным (`s_i·std_z_i ≈ exploration_frac`). Greedy (поставка) = mean.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, asdict

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from ismpu.envs.observation import OBS_DIM
from ismpu.config.regulators import REGULATOR_ORDER, N_GAINS, ACTION_DIM
from ismpu.agent import gain_space
from ismpu.agent import normalization as norm

# Разбивка 17 выходов: runway_center(3) + brake_l/r(6) + reverse_l/r(6) + weights(2).
N_HEADING, N_BRAKE, N_REVERSE, N_WEIGHTS = 3, 6, 6, 2
POLICY_DIM = N_GAINS + N_WEIGHTS          # 17 = ACTION_DIM
N_GAIN_OUT = N_GAINS                       # 15 gain-выходов (первые в 17-мерном действии)
N_PHASES = 5                               # касание / скоростной / средний / руление / стоп

PHASE_TOUCHDOWN, PHASE_HIGH, PHASE_MID, PHASE_TAXI, PHASE_STOP = range(N_PHASES)
_PHASE_BOUNDS_KTS = (150.0, 90.0, 30.0, 5.0)


@dataclass
class NPGSConfig:
    """Гиперпараметры архитектуры NPGS (замораживаются вместе с весами при поставке)."""
    obs_dim: int = OBS_DIM
    window: int = 16
    d_model: int = 256
    gru_layers: int = 2
    attn_heads: int = 4
    trunk_dim: int = 128
    context_dim: int = 128
    head_hidden: tuple = (64, 32)
    n_phases: int = N_PHASES
    dropout: float = 0.0
    exploration_frac: float = 0.15   # целевой мультипликативный шаг исследования gain'ов (±15%)
    weight_std: float = 0.3          # std исследования весов каналов

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "NPGSConfig":
        d = dict(d)
        if "head_hidden" in d:
            d["head_hidden"] = tuple(d["head_hidden"])
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


def layer_init(layer: nn.Linear, gain: float = math.sqrt(2.0), bias=0.0) -> nn.Linear:
    nn.init.orthogonal_(layer.weight, gain)
    if isinstance(bias, (int, float)):
        nn.init.constant_(layer.bias, float(bias))
    else:  # вектор bias (для gain-голов → старт ≈ DEFAULT)
        with torch.no_grad():
            layer.bias.copy_(torch.as_tensor(bias, dtype=layer.bias.dtype))
    return layer


def _mlp_head(in_dim: int, hidden: tuple, out_dim: int, out_gain: float, out_bias=0.0) -> nn.Sequential:
    layers, d = [], in_dim
    for h in hidden:
        layers += [layer_init(nn.Linear(d, h)), nn.GELU()]
        d = h
    layers.append(layer_init(nn.Linear(d, out_dim), gain=out_gain, bias=out_bias))
    return nn.Sequential(*layers)


def phase_labels_from_groundspeed_kts(gs_kts) -> np.ndarray:
    gs = np.asarray(gs_kts, dtype=np.float32)
    label = np.full(gs.shape, PHASE_STOP, dtype=np.int64)
    hi, mid, taxi, stop = _PHASE_BOUNDS_KTS
    label = np.where(gs >= hi, PHASE_TOUCHDOWN, label)
    label = np.where((gs < hi) & (gs >= mid), PHASE_HIGH, label)
    label = np.where((gs < mid) & (gs >= taxi), PHASE_MID, label)
    label = np.where((gs < taxi) & (gs >= stop), PHASE_TAXI, label)
    return label


def _init_log_std() -> torch.Tensor:
    """Per-output log_std: gain-слоты `log(frac)−log(s_i)` (равномерный мульт. шаг), веса `log(σ_w)`."""
    cfg = NPGSConfig()
    log_std = np.empty(POLICY_DIM, dtype=np.float32)
    log_std[:N_GAINS] = np.log(cfg.exploration_frac) - np.log(gain_space.GAIN_S)
    log_std[N_GAINS:] = math.log(cfg.weight_std)
    return torch.tensor(log_std)


class NPGS(nn.Module):
    """Neural PID Gain Scheduler: общий энкодер + головы актора (абс. gain'ы) + голова критика."""

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
        self.pool_query = nn.Parameter(torch.randn(d) * 0.02)
        self.trunk1 = layer_init(nn.Linear(d, d))
        self.trunk2 = layer_init(nn.Linear(d, cfg.trunk_dim))
        self.trunk_skip = layer_init(nn.Linear(d, cfg.trunk_dim))
        self.dropout = nn.Dropout(cfg.dropout) if cfg.dropout > 0 else nn.Identity()

        # --- Context Fusion (фаза движения) ---
        self.context = layer_init(nn.Linear(cfg.trunk_dim, cfg.context_dim))
        self.phase_head = _mlp_head(cfg.context_dim, (64,), cfg.n_phases, out_gain=0.01)

        # --- Головы актора (вход [z_shared ⊕ c]); gain-головы стартуют ≈ DEFAULT ---
        head_in = cfg.trunk_dim + cfg.context_dim
        bias = gain_space.default_bias()                      # (15,) в порядке REGULATOR_ORDER×(kp,ki,kd)
        self.head_heading = _mlp_head(head_in, cfg.head_hidden, N_HEADING, 0.01, out_bias=bias[0:3])
        self.head_brake = _mlp_head(head_in, cfg.head_hidden, N_BRAKE, 0.01, out_bias=bias[3:9])
        self.head_reverse = _mlp_head(head_in, cfg.head_hidden, N_REVERSE, 0.01, out_bias=bias[9:15])
        self.head_weights = _mlp_head(head_in, cfg.head_hidden, N_WEIGHTS, 0.01, out_bias=0.0)
        self.log_std = nn.Parameter(_init_log_std())

        # --- Критик (голова от z_shared) ---
        self.critic = _mlp_head(cfg.trunk_dim, (64,), 1, out_gain=1.0)

        # Референс/полуширина gain-пространства (буферы: едут с моделью, входят в state_dict).
        self.register_buffer("gain_ref", torch.tensor(gain_space.GAIN_REF, dtype=torch.float32))
        self.register_buffer("gain_s", torch.tensor(gain_space.GAIN_S, dtype=torch.float32))

    # ------------------------------------------------------------------ #
    # Энкодер
    # ------------------------------------------------------------------ #

    def encode(self, obs: torch.Tensor):
        if obs.dim() == 2:
            obs = obs.unsqueeze(0)
        x = self.input_norm(obs)
        h = F.gelu(self.enc1(x))
        h = F.gelu(self.enc2(h)) + h
        h = self.dropout(h)

        seq, _ = self.gru(h)
        a, _ = self.attn(seq, seq, seq)
        a = self.attn_norm(a + seq)

        scores = torch.einsum("btd,d->bt", a, self.pool_query) / math.sqrt(self.cfg.d_model)
        w = torch.softmax(scores, dim=1)
        pooled = torch.einsum("bt,btd->bd", w, a)

        t = F.gelu(self.trunk1(pooled))
        t = F.gelu(self.trunk2(t))
        z_shared = t + self.trunk_skip(pooled)

        c = F.gelu(self.context(z_shared))
        phase_logits = self.phase_head(c)
        return z_shared, c, phase_logits

    def forward(self, obs: torch.Tensor):
        """→ (mean (B,17), value (B,), phase_logits (B,n_phases))."""
        z_shared, c, phase_logits = self.encode(obs)
        head_in = torch.cat([z_shared, c], dim=-1)
        mean = torch.cat([
            self.head_heading(head_in),   # runway_center (3)
            self.head_brake(head_in),     # brake_l, brake_r (6)
            self.head_reverse(head_in),   # rev_l, rev_r (6)
            self.head_weights(head_in),   # w_lon, w_lat (2)
        ], dim=-1)                        # (B, 17) в layout REGULATOR_ORDER + веса
        value = self.critic(z_shared).squeeze(-1)
        return mean, value, phase_logits

    # ------------------------------------------------------------------ #
    # Отображение сырого выхода → абсолютные gain'ы + веса (= 17-мерное действие)
    # ------------------------------------------------------------------ #

    def to_gains(self, u: torch.Tensor) -> torch.Tensor:
        """17 сырых выходов → [абс. gains×15, w_lon, w_lat] (layout `REGULATOR_ORDER` + веса)."""
        gains = self.gain_ref * torch.exp(self.gain_s * torch.tanh(u[..., :N_GAINS]))
        weights = 1.0 + torch.tanh(u[..., N_GAINS:])
        return torch.cat([gains, weights], dim=-1)

    # ------------------------------------------------------------------ #
    # Политика (Gaussian над сырым u; squash — детерминированный `to_gains`)
    # ------------------------------------------------------------------ #

    def _dist(self, mean: torch.Tensor):
        std = torch.exp(self.log_std).expand_as(mean)
        return torch.distributions.Normal(mean, std)

    def get_action(self, obs: torch.Tensor, deterministic: bool = False):
        """Один шаг актора. `action` (…,17) — абс. gain'ы для среды; `raw` (…,17) — сэмпл u для PPO."""
        mean, value, phase_logits = self.forward(obs)
        dist = self._dist(mean)
        u = mean if deterministic else dist.rsample()
        action = self.to_gains(u)
        logp = dist.log_prob(u).sum(-1)
        entropy = dist.entropy().sum(-1)
        return {"action": action, "raw": u, "logp": logp, "value": value,
                "entropy": entropy, "phase_logits": phase_logits, "mean": mean}

    def evaluate_actions(self, obs: torch.Tensor, u: torch.Tensor):
        """Пересчёт на апдейте PPO. → (logp, entropy, value, mean, phase_logits)."""
        mean, value, phase_logits = self.forward(obs)
        dist = self._dist(mean)
        logp = dist.log_prob(u).sum(-1)
        entropy = dist.entropy().sum(-1)
        return logp, entropy, value, mean, phase_logits

    # ------------------------------------------------------------------ #
    # Инференс из numpy и сериализация
    # ------------------------------------------------------------------ #

    @torch.no_grad()
    def act_numpy(self, obs_window: np.ndarray, deterministic: bool = False):
        """obs (T,56) np → (action_17 np, raw_17 np, logp float, value float)."""
        device = self.log_std.device
        obs = torch.as_tensor(obs_window, dtype=torch.float32, device=device)
        out = self.get_action(obs, deterministic=deterministic)
        return (out["action"].squeeze(0).cpu().numpy(),
                out["raw"].squeeze(0).cpu().numpy(),
                float(out["logp"].item()), float(out["value"].item()))

    def save(self, path: str) -> None:
        """Веса + конфиг + слепок нормировки (включая gain-пространство) одним артефактом."""
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
    assert POLICY_DIM == ACTION_DIM == 17
    return model
