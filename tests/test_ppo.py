"""Тесты PPO-тренера (Этап 4, §11): GAE, компоненты loss, сквозной прогон обучения
на скриптованной среде (без X-Plane), обновление параметров, детерминизм.

torch — опционален; без него тесты пропускаются.
"""

import math

import numpy as np
import pytest

torch = pytest.importorskip("torch")

from ismpu.config.constants import DT
from ismpu.config.runway import RWY_START_LAT, RWY_START_LON, RWY_HEADING_TRUE
from ismpu.control.runway_tracker import RunwayTracker
from ismpu.control.system import ControllingSystem
from ismpu.io.datarefs import LATITUDE, LONGITUDE, GROUNDSPEED, TRUE_PSI
from ismpu.envs.sim_interface import XPlaneBackend
from ismpu.envs.rollout_env import RolloutEnv
from ismpu.envs.scenario import SCENARIO_PRESETS
from ismpu.agent.shield import Shield
from ismpu.agent.gain_scheduler import NPGS, NPGSConfig, POLICY_DIM
from ismpu.agent.ppo import PPOTrainer, PPOConfig, RolloutBuffer
from ismpu.runtime.train import smoke_train


# --------------------------------------------------------------------------- #
# Скриптованный бэкенд: кинематический пробег по оси, без X-Plane
# --------------------------------------------------------------------------- #

class FakeXPC:
    def __init__(self):
        self.current_dref_values = {}

    def sendDREF(self, dref, value): pass
    def sendCTRL(self, **kw): pass
    def sendPOSI(self, **kw): pass
    def sendCMND(self, *a): pass
    def pauseSIM(self, *a): pass

    def subscribeDREFs(self, subs, timeout=5.0):
        for dref, _ in subs:
            self.current_dref_values.setdefault(dref, {"value": 0.0})

    def getDREF(self, dref):
        v = self.current_dref_values.get(dref)
        return v["value"] if v else 0.0


class ScriptedBackend(XPlaneBackend):
    """Мини-симулятор: замедление ~ команде тормоза/реверса, ход вдоль осевой ВПП."""

    def __init__(self):
        super().__init__(xpc=FakeXPC(), settle_s=0.0)
        self.tracker = RunwayTracker()
        self._reset_state(0.0)

    def _reset_state(self, lateral):
        self.speed, self.along, self.xte = 60.0, 0.0, float(lateral)
        self._write()

    def _write(self):
        brg = math.radians(RWY_HEADING_TRUE)
        lat, lon = self.tracker.destination(RWY_START_LAT, RWY_START_LON, brg, self.along)
        if self.xte:
            side = math.radians(RWY_HEADING_TRUE + (90.0 if self.xte > 0 else -90.0))
            lat, lon = self.tracker.destination(lat, lon, side, abs(self.xte))
        cur = self.xpc.current_dref_values
        cur[LATITUDE] = {"value": lat}
        cur[LONGITUDE] = {"value": lon}
        cur[GROUNDSPEED] = {"value": self.speed}
        cur[TRUE_PSI] = {"value": float(RWY_HEADING_TRUE)}

    def reset(self, scenario):
        lateral = scenario.touchdown.lateral_offset_m if scenario.touchdown else 0.0
        self._reset_state(lateral)
        self._ensure_subscribed()
        return self.read_telemetry()

    def step(self, command):
        brake = 0.5 * (command.cmd_brake_l + command.cmd_brake_r)
        rev = -0.5 * (command.cmd_rev_l + command.cmd_rev_r)
        decel = 1.0 + 6.0 * brake + 4.0 * rev
        self.speed = max(0.0, self.speed - decel * DT)
        self.along += self.speed * DT
        self.xte += -command.rudder_cmd * 0.05
        self._write()
        return self.read_telemetry()


def _make_env(window=6, shield=True):
    sim = ScriptedBackend()
    ctrl = ControllingSystem(xpc=sim.xpc)   # общий коннектор (обязательное условие обучения)
    return RolloutEnv(sim, ctrl, history_len=window, shield=Shield() if shield else None)


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
    from ismpu.envs.action import IDENTITY_ACTION
    env = _make_env(window=6)
    obs, _ = env.reset(_provider())
    assert obs.shape == (6, OBS_DIM)
    obs2, reward, term, trunc, info = env.step(IDENTITY_ACTION)
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


def test_lambda_smooth_pulls_toward_identity():
    # При сильном L_smooth и нулевом reward-градиенте политика тянется к identity.
    torch.manual_seed(0)
    env = _make_env(window=6, shield=False)
    net = NPGS(NPGSConfig(window=6))
    cfg = PPOConfig(rollout_len=32, num_minibatches=2, update_epochs=3,
                    lambda_smooth=5.0, lr=1e-3, device="cpu")
    trainer = PPOTrainer(net, cfg, total_updates=3)
    trainer.train(env, _provider, total_updates=3)
    # средний выход близок к identity (α≈1): |tanh(mean)| мал
    obs = torch.randn(8, 6, 56)
    with torch.no_grad():
        mean, _, _ = net(obs)
    assert float(torch.tanh(mean).abs().mean()) < 0.2
