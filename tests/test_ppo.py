"""Тесты PPO-тренера (Этап 4, §11): GAE, компоненты loss, сквозной прогон обучения
на скриптованной среде (без стенда), обновление параметров, детерминизм.

torch — опционален; без него тесты пропускаются.
"""

import math

import numpy as np
import pytest

torch = pytest.importorskip("torch")

from ismpu.control.system import ControllingSystem
from ismpu.envs.rollout_env import RolloutEnv
from ismpu.envs.scenario import SCENARIO_PRESETS
from ismpu.agent.shield import Shield
from ismpu.agent.gain_scheduler import NPGS, NPGSConfig, POLICY_DIM
from ismpu.agent.ppo import PPOTrainer, PPOConfig, RolloutBuffer
from ismpu.runtime.train import smoke_train

from fakes import kinematic_sim


# --------------------------------------------------------------------------- #
# Скриптованный стенд: кинематический пробег по оси (см. fakes.KinematicBench)
# --------------------------------------------------------------------------- #

def scripted_env(window=6, shield=True, lateral=0.0):
    """Среда на кинематической модели стенда — общая фикстура для PPO и SFT-тестов."""
    sim, _bench = kinematic_sim(lateral=lateral)
    ctrl = ControllingSystem(sim)
    return RolloutEnv(sim, ctrl, history_len=window, shield=Shield() if shield else None)


def _make_env(window=6, shield=True):
    return scripted_env(window=window, shield=shield)


def _provider():
    return SCENARIO_PRESETS["default"]


# --------------------------------------------------------------------------- #
# GAE
# --------------------------------------------------------------------------- #

def test_gae_matches_manual_computation():
    buf = RolloutBuffer(3, window=2, obs_dim=4, act_dim=POLICY_DIM, device=torch.device("cpu"))
    buf.rewards[:] = torch.tensor([1.0, 1.0, 1.0])
    buf.values[:] = torch.zeros(3)
    buf.dones[:] = torch.zeros(3)
    buf.compute_gae(next_value=0.0, next_done=0.0, gamma=1.0, lam=1.0)
    assert torch.allclose(buf.advantages, torch.tensor([3.0, 2.0, 1.0]))
    assert torch.allclose(buf.returns, torch.tensor([3.0, 2.0, 1.0]))


def test_gae_zeroes_bootstrap_after_done():
    buf = RolloutBuffer(3, window=2, obs_dim=4, act_dim=POLICY_DIM, device=torch.device("cpu"))
    buf.rewards[:] = torch.tensor([1.0, 1.0, 1.0])
    buf.values[:] = torch.zeros(3)
    buf.dones[:] = torch.tensor([0.0, 0.0, 1.0])   # obs[2] — начало нового эпизода
    buf.compute_gae(next_value=5.0, next_done=0.0, gamma=1.0, lam=1.0)
    # t=2 бутстрапит next_value=5 → adv[2]=6; t=1 не бутстрапит через done[2] → adv[1]=1
    assert torch.allclose(buf.advantages, torch.tensor([2.0, 1.0, 6.0]))


# --------------------------------------------------------------------------- #
# Среда отдаёт последовательность (T, 56)
# --------------------------------------------------------------------------- #

def test_env_returns_sequence_window():
    from ismpu.envs.observation import OBS_DIM
    from ismpu.envs.action import REFERENCE_ACTION
    env = _make_env(window=6)
    obs, _ = env.reset(_provider())
    assert obs.shape == (6, OBS_DIM)
    obs2, reward, term, trunc, info = env.step(REFERENCE_ACTION)
    assert obs2.shape == (6, OBS_DIM)
    assert np.isfinite(reward)


# --------------------------------------------------------------------------- #
# Сквозной PPO
# --------------------------------------------------------------------------- #

def test_ppo_smoke_runs_and_updates_params():
    torch.manual_seed(0)
    window = 6
    env = _make_env(window=window)
    net = NPGS(NPGSConfig(window=window))
    before = [p.detach().clone() for p in net.parameters()]

    cfg = PPOConfig(rollout_len=48, num_minibatches=4, update_epochs=2, device="cpu")
    trainer = PPOTrainer(net, cfg, total_updates=2)
    trainer.train(env, _provider, total_updates=2)

    after = list(net.parameters())
    changed = any(not torch.allclose(b, a) for b, a in zip(before, after))
    assert changed, "PPO не обновил параметры"
    assert len(trainer.history) == 2


def test_ppo_metrics_present_and_finite():
    torch.manual_seed(0)
    env = _make_env(window=6)
    net = NPGS(NPGSConfig(window=6))
    cfg = PPOConfig(rollout_len=32, num_minibatches=4, update_epochs=1, device="cpu")
    trainer = PPOTrainer(net, cfg, total_updates=1)
    m = trainer.step(env, _provider)
    for key in ("pg_loss", "v_loss", "entropy", "l_smooth", "l_shield", "l_phys",
                "approx_kl", "clipfrac", "lr", "global_step"):
        assert key in m
    for key in ("pg_loss", "v_loss", "entropy", "l_smooth", "approx_kl"):
        assert math.isfinite(m[key]), f"{key} не конечно"


def test_smoke_train_helper_runs():
    torch.manual_seed(0)
    env = _make_env(window=6)
    trainer = smoke_train(env, _provider, updates=1)
    assert len(trainer.history) == 1


def test_lambda_smooth_temporal_term_finite_and_trains():
    # L_smooth теперь — временная гладкость коэффициентов (выход ≈ прошлые gain'ы из obs).
    # Проверяем, что сильный вес не ломает обучение и терм конечен/неотрицателен.
    torch.manual_seed(0)
    env = _make_env(window=6, shield=False)
    net = NPGS(NPGSConfig(window=6))
    cfg = PPOConfig(rollout_len=32, num_minibatches=2, update_epochs=3,
                    lambda_smooth=5.0, lr=1e-3, device="cpu")
    trainer = PPOTrainer(net, cfg, total_updates=3)
    trainer.train(env, _provider, total_updates=3)
    m = trainer.history[-1]
    assert math.isfinite(m["l_smooth"]) and m["l_smooth"] >= 0.0
    assert all(math.isfinite(h["pg_loss"]) for h in trainer.history)
