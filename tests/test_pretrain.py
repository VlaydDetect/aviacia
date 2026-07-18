"""Тесты SFT-конвейера (Stage B): инверсия цели, захват датасета, overfit-до-нуля,
анти-копирование (сеть учится по внешнему воздействию, а не копирует прошлый gain)."""

import numpy as np
import pytest

torch = pytest.importorskip("torch")

from ismpu.agent.gain_scheduler import NPGS, NPGSConfig
from ismpu.agent import gain_space as gs
from ismpu.agent.pretrain import target_z_from_gains, pretrain_sft, PretrainConfig, SFTDataset
from ismpu.runtime.capture import capture_scenario, capture_dataset
from ismpu.runtime.pretrain import smoke_pretrain
from ismpu.envs.scenario import SCENARIO_PRESETS
from ismpu.agent.shield import base_gains_from_pids
from ismpu.control.system import ControllingSystem

from test_ppo import ScriptedBackend, FakeXPC   # переиспользуем скриптованный бэкенд
from ismpu.envs.rollout_env import RolloutEnv


def _make_env(window=6):
    sim = ScriptedBackend()
    ctrl = ControllingSystem(xpc=sim.xpc)
    return RolloutEnv(sim, ctrl, history_len=window, shield=None)


# --------------------------------------------------------------------------- #
# Инверсия цели
# --------------------------------------------------------------------------- #

def test_target_z_inverts_to_preset_gains():
    ctrl = ControllingSystem(xpc=FakeXPC())
    SCENARIO_PRESETS["nws_fail"].apply_control(ctrl)
    preset = base_gains_from_pids(ctrl.pids)

    tz = target_z_from_gains(preset)
    assert tz.shape == (17,)
    assert np.allclose(tz[15:], 0.0)                       # веса: z=0 → w=1
    # to_gains(target_z) воспроизводит пресет
    net = NPGS(NPGSConfig(window=4))
    g = net.to_gains(torch.tensor(tz)).detach().numpy()
    from ismpu.config.regulators import REGULATOR_ORDER, GAIN_KEYS
    expected = np.array([preset[r][k] for r in REGULATOR_ORDER for k in GAIN_KEYS])
    assert np.allclose(g[:15], expected, rtol=1e-5)
    assert np.allclose(g[15:], 1.0)


# --------------------------------------------------------------------------- #
# Захват
# --------------------------------------------------------------------------- #

def test_capture_scenario_produces_constant_target():
    env = _make_env(window=6)
    ds = capture_scenario(env, SCENARIO_PRESETS["nws_fail"], max_steps=30)
    assert ds.obs.ndim == 3 and ds.obs.shape[1:] == (6, 56)
    assert ds.target_z.shape == (len(ds), 17)
    # цель постоянна на прогон
    assert np.allclose(ds.target_z, ds.target_z[0])
    # и равна NWS-пресету
    ctrl = ControllingSystem(xpc=FakeXPC()); SCENARIO_PRESETS["nws_fail"].apply_control(ctrl)
    assert np.allclose(ds.target_z[0], target_z_from_gains(base_gains_from_pids(ctrl.pids)))


# --------------------------------------------------------------------------- #
# Overfit до ~0 (сеть способна выучить цель)
# --------------------------------------------------------------------------- #

def test_sft_overfits_small_dataset():
    torch.manual_seed(0)
    env = _make_env(window=6)
    ds = capture_dataset(env, [SCENARIO_PRESETS["nws_fail"]], max_steps=40, log=None)
    net = NPGS(NPGSConfig(window=6))
    hist = pretrain_sft(net, ds, PretrainConfig(epochs=60, batch_size=64, lr=2e-3, device="cpu"))
    assert hist[-1]["mse"] < 0.3 * hist[0]["mse"]     # loss заметно падает


# --------------------------------------------------------------------------- #
# Анти-копирование: сеть различает режимы по внешнему воздействию, не копирует прошлый gain
# --------------------------------------------------------------------------- #

def test_sft_learns_to_distinguish_scenarios_not_copy_input():
    torch.manual_seed(0)
    env = _make_env(window=6)
    ds = capture_dataset(env, [SCENARIO_PRESETS["default"], SCENARIO_PRESETS["nws_fail"]],
                         max_steps=60, log=None)
    net = NPGS(NPGSConfig(window=6))
    pretrain_sft(net, ds, PretrainConfig(epochs=80, batch_size=128, lr=2e-3,
                                         mask_prev_gains=True, device="cpu"))

    # greedy-выход на DEFAULT-окне ≈ DEFAULT-пресет, на NWS-окне ≈ NWS-пресет — и они РАЗНЫЕ.
    def greedy_gains(preset_name):
        e = _make_env(window=6)
        obs, _ = e.reset(SCENARIO_PRESETS[preset_name])
        return net.act_numpy(obs, deterministic=True)[0][:15]

    from ismpu.config.regulators import REGULATOR_ORDER, GAIN_KEYS
    def preset_vec(name):
        c = ControllingSystem(xpc=FakeXPC()); SCENARIO_PRESETS[name].apply_control(c)
        p = base_gains_from_pids(c.pids)
        return np.array([p[r][k] for r in REGULATOR_ORDER for k in GAIN_KEYS])

    g_def, g_nws = greedy_gains("default"), greedy_gains("nws_fail")
    p_def, p_nws = preset_vec("default"), preset_vec("nws_fail")

    # выходы для разных режимов различаются (не копия одного и того же входа)
    assert np.abs(g_def - g_nws).max() > 1e-3
    # каждый ближе к своему пресету, чем к чужому (в лог-норме)
    def lognorm(v):
        return np.array([gs.gain_norm_scalar(v[i], r, k)
                         for i, (r, k) in enumerate([(r, k) for r in REGULATOR_ORDER for k in GAIN_KEYS])])
    d_own = np.abs(lognorm(g_nws) - lognorm(p_nws)).mean()
    d_other = np.abs(lognorm(g_nws) - lognorm(p_def)).mean()
    assert d_own < d_other


# --------------------------------------------------------------------------- #
# Оффлайн smoke оркестрации
# --------------------------------------------------------------------------- #

def test_smoke_pretrain_runs():
    torch.manual_seed(0)
    env = _make_env(window=6)
    scenarios = [SCENARIO_PRESETS["default"], SCENARIO_PRESETS["nws_fail"]]
    net, dataset, history = smoke_pretrain(env, scenarios, max_steps=30)
    assert len(dataset) > 0 and len(history) == 3
    assert all(np.isfinite(h["mse"]) for h in history)
