"""PPO-тренер + многокомпонентный loss для NPGS (план §11).

`L = L_ppo + λ_s·L_smooth + λ_p·L_phys + λ_sh·L_shield` (+ опц. вспом. фаза).

- **L_ppo** — clipped surrogate + GAE(λ)-advantage от критика + value-clipping.
- **L_smooth** — дифференцируемый штраф **временной гладкости коэффициентов**: расхождение
  выхода сети с ПРОШЛЫМИ gain'ами (закодированы в obs как лог-норма = `tanh(z)`),
  `Σ(tanh(mean)−prev_gain_norm)²`. Опц. + SFT-prior-anchor `‖mean − mean_SFT‖²` (не забывать
  пресеты). Рывки управления и активация Shield входят также через **reward**
  (`envs/reward.py`) — так недифференцируемые штрафы корректно попадают в advantage.
- **L_phys** — хук обсервера (§12); `λ_p = 0` до его включения, слагаемое уже в сумме.
- **L_shield** — хук штрафа за вмешательство Shield; `λ_sh = 0` по умолчанию (основной
  сигнал Shield идёт через reward), барьерный терм подключается тем же швом.
- Вспом. задача фазы движения (§10) — опц. cross-entropy, `λ_phase = 0` по умолчанию.

Собственный компактный PPO (стиль CleanRL): один env (X-Plane — один экземпляр),
rollout-буфер, GAE, минибатчи × эпохи, AdamW, grad-clip, нормировка advantage,
annealing LR, KL-early-stop. Логирование по каждому терму — в `history`.

Тонкость bootstrap: усечение по `max_steps` в пределах одного rollout маловероятно
(эпизод длиннее буфера), поэтому используется маска `nextnonterminal` без хранения
терминального obs (обычная упрощённая схема CleanRL для одиночного env).
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from ismpu.agent.gain_scheduler import NPGS, POLICY_DIM, N_GAIN_OUT, phase_labels_from_groundspeed_kts
from ismpu.agent.normalization import SPEED_SCALE
from ismpu.envs.observation import FEATURE_NAMES, GAIN_FEATURE_INDICES
from ismpu.utils.converts import Converts

_GS_IDX = FEATURE_NAMES.index("ground_speed")   # индекс путевой скорости в кадре obs
_GAIN_FEAT_IDX = GAIN_FEATURE_INDICES           # gain-признаки (лог-норма прошлых коэффициентов)


@dataclass
class PPOConfig:
    rollout_len: int = 2048
    gamma: float = 0.99
    gae_lambda: float = 0.95
    clip_coef: float = 0.2
    vf_coef: float = 0.5
    ent_coef: float = 0.0
    max_grad_norm: float = 0.5
    lr: float = 3e-4
    update_epochs: int = 10
    num_minibatches: int = 32
    target_kl: float | None = 0.03
    norm_adv: bool = True
    clip_vloss: bool = True
    anneal_lr: bool = True
    # Многокомпонентный loss
    lambda_smooth: float = 1e-3
    lambda_anchor: float = 0.0      # SFT-prior-anchor к замороженной SFT-копии (Stage C)
    lambda_phys: float = 0.0        # хук обсервера (§12), включается позже
    lambda_shield: float = 0.0      # хук штрафа Shield (основной сигнал — через reward)
    lambda_phase: float = 0.0       # вспом. задача фазы движения (§10)
    device: str = "cuda"

    def to_dict(self) -> dict:
        return asdict(self)


class RolloutBuffer:
    """Плоский буфер одного env: obs-окна, сырые действия, logp/value/reward/done."""

    def __init__(self, size: int, window: int, obs_dim: int, act_dim: int, device):
        self.device = device
        self.obs = torch.zeros((size, window, obs_dim), device=device)
        self.actions = torch.zeros((size, act_dim), device=device)     # сырые u (до ограничения)
        self.logp = torch.zeros(size, device=device)
        self.values = torch.zeros(size, device=device)
        self.rewards = torch.zeros(size, device=device)
        self.dones = torch.zeros(size, device=device)
        self.advantages = torch.zeros(size, device=device)
        self.returns = torch.zeros(size, device=device)
        self.size = size

    def compute_gae(self, next_value: float, next_done: float, gamma: float, lam: float):
        adv, lastgaelam = self.advantages, 0.0
        for t in reversed(range(self.size)):
            if t == self.size - 1:
                nextnonterminal = 1.0 - next_done
                nextvalue = next_value
            else:
                nextnonterminal = 1.0 - self.dones[t + 1]
                nextvalue = self.values[t + 1]
            delta = self.rewards[t] + gamma * nextvalue * nextnonterminal - self.values[t]
            adv[t] = lastgaelam = delta + gamma * lam * nextnonterminal * lastgaelam
        self.returns = self.advantages + self.values


class PPOTrainer:
    """Собирает rollout из среды и обновляет NPGS многокомпонентным PPO-loss."""

    def __init__(self, net: NPGS, config: PPOConfig | None = None, total_updates: int | None = None):
        self.cfg = config or PPOConfig()
        if self.cfg.device == "cuda" and not torch.cuda.is_available():
            self.cfg.device = "cpu"
        self.device = torch.device(self.cfg.device)
        self.net = net.to(self.device)
        self.optimizer = torch.optim.AdamW(self.net.parameters(), lr=self.cfg.lr, eps=1e-5)
        self.total_updates = total_updates
        self.window = net.cfg.window
        self.obs_dim = net.cfg.obs_dim
        self.global_step = 0
        self.update_idx = 0
        self.history: list[dict] = []
        self.sft_reference: NPGS | None = None   # замороженная SFT-копия для L_anchor (Stage C)
        # Состояние потоковой среды (между rollout'ами не теряем эпизод).
        self._next_obs: np.ndarray | None = None
        self._next_done: float = 1.0

    # ------------------------------------------------------------------ #
    # Сбор rollout
    # ------------------------------------------------------------------ #

    def collect(self, env, scenario_provider) -> dict:
        """Шагает средой `rollout_len` тактов (сброс по завершению эпизода). → статистика."""
        cfg = self.cfg
        buf = RolloutBuffer(cfg.rollout_len, self.window, self.obs_dim, POLICY_DIM, self.device)
        self.net.eval()

        if self._next_obs is None:
            self._next_obs, _ = env.reset(scenario_provider())
            self._next_done = 1.0

        ep_returns, ep_lens, cur_ret, cur_len = [], [], 0.0, 0
        shield_hits, comp_sums = 0, {}

        for step in range(cfg.rollout_len):
            buf.obs[step] = torch.as_tensor(self._next_obs, dtype=torch.float32, device=self.device)
            buf.dones[step] = self._next_done

            action, raw, logp, value = self.net.act_numpy(self._next_obs, deterministic=False)
            buf.actions[step] = torch.as_tensor(raw, dtype=torch.float32, device=self.device)
            buf.logp[step] = logp
            buf.values[step] = value

            nobs, reward, terminated, truncated, info = env.step(action)
            buf.rewards[step] = reward
            cur_ret += reward
            cur_len += 1
            self.global_step += 1

            rep = info.get("shield")
            if rep is not None and getattr(rep, "active", False):
                shield_hits += 1
            comp = info.get("reward_components")
            if comp is not None:
                for k, v in comp.as_dict().items():
                    comp_sums[k] = comp_sums.get(k, 0.0) + v

            done = bool(terminated or truncated)
            self._next_done = 1.0 if done else 0.0
            if done:
                ep_returns.append(cur_ret)
                ep_lens.append(cur_len)
                cur_ret, cur_len = 0.0, 0
                nobs, _ = env.reset(scenario_provider())
            self._next_obs = nobs

        with torch.no_grad():
            obs_t = torch.as_tensor(self._next_obs, dtype=torch.float32, device=self.device)
            _, next_value, _ = self.net(obs_t.unsqueeze(0))
        buf.compute_gae(float(next_value.item()), self._next_done, cfg.gamma, cfg.gae_lambda)
        self._buffer = buf

        n = max(1, len(ep_returns))
        denom = max(1, cfg.rollout_len)
        return {
            "ep_return_mean": float(np.mean(ep_returns)) if ep_returns else float("nan"),
            "ep_len_mean": float(np.mean(ep_lens)) if ep_lens else float("nan"),
            "episodes": len(ep_returns),
            "shield_rate": shield_hits / denom,
            **{f"reward/{k}": v / denom for k, v in comp_sums.items()},
        }

    # ------------------------------------------------------------------ #
    # Обновление политики
    # ------------------------------------------------------------------ #

    def update(self) -> dict:
        cfg, buf = self.cfg, self._buffer
        self.net.train()

        if cfg.anneal_lr and self.total_updates:
            frac = 1.0 - self.update_idx / float(self.total_updates)
            self.optimizer.param_groups[0]["lr"] = max(0.0, frac) * cfg.lr

        b_obs, b_actions = buf.obs, buf.actions
        b_logp, b_adv, b_ret, b_val = buf.logp, buf.advantages, buf.returns, buf.values

        # Метки фазы движения для вспом. задачи (из путевой скорости последнего кадра).
        gs_kts = (b_obs[:, -1, _GS_IDX].cpu().numpy() * SPEED_SCALE) * Converts.MS_TO_KTS
        b_phase = torch.as_tensor(phase_labels_from_groundspeed_kts(gs_kts), device=self.device)

        idx = np.arange(cfg.rollout_len)
        mb_size = max(1, cfg.rollout_len // cfg.num_minibatches)
        rng = np.random.default_rng(self.update_idx)

        metrics = {k: 0.0 for k in ("pg_loss", "v_loss", "entropy", "l_smooth",
                                    "l_shield", "l_phys", "phase_loss", "approx_kl", "clipfrac")}
        n_mb = 0
        early_stop = False
        for _ in range(cfg.update_epochs):
            rng.shuffle(idx)
            for start in range(0, cfg.rollout_len, mb_size):
                mb = idx[start:start + mb_size]
                mb_t = torch.as_tensor(mb, device=self.device)

                new_logp, entropy, new_value, mean, phase_logits = self.net.evaluate_actions(
                    b_obs[mb_t], b_actions[mb_t])

                logratio = new_logp - b_logp[mb_t]
                ratio = logratio.exp()
                with torch.no_grad():
                    approx_kl = ((ratio - 1.0) - logratio).mean()
                    clipfrac = ((ratio - 1.0).abs() > cfg.clip_coef).float().mean()

                adv = b_adv[mb_t]
                if cfg.norm_adv and adv.numel() > 1:
                    adv = (adv - adv.mean()) / (adv.std() + 1e-8)

                # Clipped surrogate (минимизируем − суррогат).
                pg1 = -adv * ratio
                pg2 = -adv * torch.clamp(ratio, 1 - cfg.clip_coef, 1 + cfg.clip_coef)
                pg_loss = torch.max(pg1, pg2).mean()

                # Value loss (+ клиппинг значения).
                new_value = new_value.view(-1)
                if cfg.clip_vloss:
                    v_unclipped = (new_value - b_ret[mb_t]) ** 2
                    v_clipped = b_val[mb_t] + torch.clamp(
                        new_value - b_val[mb_t], -cfg.clip_coef, cfg.clip_coef)
                    v_clipped = (v_clipped - b_ret[mb_t]) ** 2
                    v_loss = 0.5 * torch.max(v_unclipped, v_clipped).mean()
                else:
                    v_loss = 0.5 * ((new_value - b_ret[mb_t]) ** 2).mean()

                ent = entropy.mean()

                # L_smooth: временная гладкость коэффициентов — штраф за расхождение выхода сети
                # с ПРОШЛЫМИ gain'ами (закодированы в obs как лог-норма = tanh(z)). Дифференцируемо.
                cur_gain_norm = torch.tanh(mean[:, :N_GAIN_OUT])
                prev_gain_norm = b_obs[mb_t][:, -1, _GAIN_FEAT_IDX]
                l_smooth = (cur_gain_norm - prev_gain_norm).pow(2).sum(-1).mean()
                # + опц. SFT-prior-anchor: не забывать пресеты (замороженная SFT-копия, Stage C).
                if self.sft_reference is not None and cfg.lambda_anchor > 0:
                    with torch.no_grad():
                        ref_mean, _, _ = self.sft_reference(b_obs[mb_t])
                    l_smooth = l_smooth + cfg.lambda_anchor * (mean - ref_mean).pow(2).sum(-1).mean()

                # Хуки §11 (по умолчанию нулевой вклад).
                l_shield = self._shield_barrier(mean)
                l_phys = torch.zeros((), device=self.device)
                phase_loss = (F.cross_entropy(phase_logits, b_phase[mb_t])
                              if cfg.lambda_phase > 0 else torch.zeros((), device=self.device))

                loss = (pg_loss + cfg.vf_coef * v_loss - cfg.ent_coef * ent
                        + cfg.lambda_smooth * l_smooth + cfg.lambda_shield * l_shield
                        + cfg.lambda_phys * l_phys + cfg.lambda_phase * phase_loss)

                self.optimizer.zero_grad()
                loss.backward()
                nn.utils.clip_grad_norm_(self.net.parameters(), cfg.max_grad_norm)
                self.optimizer.step()

                for k, v in (("pg_loss", pg_loss), ("v_loss", v_loss), ("entropy", ent),
                             ("l_smooth", l_smooth), ("l_shield", l_shield), ("l_phys", l_phys),
                             ("phase_loss", phase_loss), ("approx_kl", approx_kl), ("clipfrac", clipfrac)):
                    metrics[k] += float(v.item())
                n_mb += 1

            if cfg.target_kl is not None and float(approx_kl.item()) > cfg.target_kl:
                early_stop = True
                break

        for k in metrics:
            metrics[k] /= max(1, n_mb)
        metrics["lr"] = self.optimizer.param_groups[0]["lr"]
        metrics["early_stop"] = early_stop
        self.update_idx += 1
        return metrics

    def _shield_barrier(self, mean: torch.Tensor) -> torch.Tensor:
        """Хук L_shield (§11): барьер, отталкивающий выход от края уровня-1 Shield.

        По умолчанию `λ_shield = 0` (основной сигнал Shield — через reward). Терм
        дифференцируем и подключается тем же швом, что L_phys обсервера.
        """
        # мягкий барьер: ≈0 в центре, круто растёт, когда |tanh(z)|→1 (α/w у края band).
        return torch.tanh(mean).pow(4).mean()

    # ------------------------------------------------------------------ #
    # Одна итерация PPO (сбор + апдейт) и цикл обучения
    # ------------------------------------------------------------------ #

    def step(self, env, scenario_provider) -> dict:
        roll = self.collect(env, scenario_provider)
        upd = self.update()
        metrics = {"update": self.update_idx, "global_step": self.global_step, **roll, **upd}
        self.history.append(metrics)
        return metrics

    def train(self, env, scenario_provider, total_updates: int, callback=None) -> list[dict]:
        self.total_updates = total_updates
        for _ in range(total_updates):
            metrics = self.step(env, scenario_provider)
            if callback is not None:
                callback(metrics)
        return self.history
