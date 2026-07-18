"""Тесты NPGS (абсолютные коэффициенты): формы forward, старт ≈ DEFAULT, ограничение
выхода к физической полосе, детерминизм greedy, сборка действия, save/load.

torch — опционален (extra `rl`); при его отсутствии тесты пропускаются (venv с CUDA).
"""

import numpy as np
import pytest

torch = pytest.importorskip("torch")

from ismpu.agent.gain_scheduler import (
    NPGS, NPGSConfig, build_npgs, POLICY_DIM, N_GAIN_OUT, phase_labels_from_groundspeed_kts,
    PHASE_TOUCHDOWN, PHASE_HIGH, PHASE_MID, PHASE_TAXI, PHASE_STOP,
)
from ismpu.agent import gain_space as gs
from ismpu.config.regulators import ACTION_DIM, REGULATOR_ORDER
from ismpu.envs.action import decode, REFERENCE_ACTION, ACTION_LOW, ACTION_HIGH
from ismpu.envs.observation import OBS_DIM


@pytest.fixture
def net():
    torch.manual_seed(0)
    return build_npgs(NPGSConfig(window=8))


def test_forward_shapes(net):
    B, T = 4, 8
    obs = torch.randn(B, T, OBS_DIM)
    mean, value, phase = net(obs)
    assert mean.shape == (B, POLICY_DIM) == (B, 17)
    assert value.shape == (B,)
    assert phase.shape == (B, 5)


def test_param_count_is_compact(net):
    n = sum(p.numel() for p in net.parameters())
    assert 0.5e6 < n < 3e6


def test_z_zero_maps_to_ref_gains_and_unit_weights(net):
    g = net.to_gains(torch.zeros(3, POLICY_DIM)).detach().numpy()
    assert np.allclose(g[:, :15], gs.GAIN_REF, rtol=1e-5)
    assert np.allclose(g[:, 15:], 1.0)


def test_init_greedy_near_default(net):
    # bias-инициализация gain-голов → старт ≈ классический DEFAULT (безопасный старт).
    obs = torch.randn(6, 8, OBS_DIM)
    a = net.get_action(obs, deterministic=True)["action"].detach().numpy()
    rel = np.abs(a[:, :15] / gs.GAIN_DEFAULT - 1.0).max()
    assert rel < 0.25, rel
    assert np.allclose(a[:, 15:], 1.0, atol=0.2)   # веса ≈ 1


def test_output_bounded_to_physical_band(net):
    g = net.to_gains(torch.randn(64, POLICY_DIM) * 10).detach().numpy()
    assert np.all(g[:, :15] >= gs.GAIN_LO - 1e-6) and np.all(g[:, :15] <= gs.GAIN_HI + 1e-6)
    assert np.all(g[:, 15:] >= -1e-6) and np.all(g[:, 15:] <= 2.0 + 1e-6)
    # действие всегда в границах пространства
    a = net.get_action(torch.randn(8, 8, OBS_DIM))["action"].detach().numpy()
    assert np.all(a >= ACTION_LOW - 1e-5) and np.all(a <= ACTION_HIGH + 1e-5)


def test_greedy_is_deterministic(net):
    obs = torch.randn(2, 8, OBS_DIM)
    a1 = net.get_action(obs, deterministic=True)["action"]
    a2 = net.get_action(obs, deterministic=True)["action"]
    assert torch.allclose(a1, a2)


def test_action_maps_to_all_five_regulators_independently(net):
    a = net.get_action(torch.randn(1, 8, OBS_DIM), deterministic=True)["action"][0].detach().numpy()
    cmd = decode(a)
    assert set(cmd.gains) == set(REGULATOR_ORDER)
    # L/R больше НЕ форсированы равными (независимые головы) — асимметрия возможна.
    assert cmd.gains["pid_brake_l"]["kp"] != cmd.gains["pid_brake_r"]["kp"]
    assert len(a) == ACTION_DIM == 17


def test_evaluate_actions_matches_get_action(net):
    obs = torch.randn(5, 8, OBS_DIM)
    out = net.get_action(obs, deterministic=False)
    logp, ent, val, mean, phase = net.evaluate_actions(obs, out["raw"])
    assert torch.allclose(out["logp"], logp, atol=1e-5)
    assert torch.allclose(out["value"], val, atol=1e-5)
    assert torch.allclose(out["mean"], mean, atol=1e-5)


def test_per_output_log_std_uniform_multiplicative_step(net):
    ls = net.log_std.detach().numpy()
    step = gs.GAIN_S * np.exp(ls[:N_GAIN_OUT])   # s_i · std_z_i
    assert np.allclose(step, 0.15, atol=1e-6)      # exploration_frac


def test_act_numpy_single_window(net):
    obs = np.random.randn(8, OBS_DIM).astype(np.float32)
    action, raw, logp, value = net.act_numpy(obs, deterministic=True)
    assert action.shape == (ACTION_DIM,) and raw.shape == (POLICY_DIM,)
    assert isinstance(logp, float) and isinstance(value, float)


def test_save_load_roundtrip(net, tmp_path):
    path = str(tmp_path / "npgs.pt")
    net.save(path)
    loaded = NPGS.load(path)
    obs = np.random.randn(8, OBS_DIM).astype(np.float32)
    a0 = net.act_numpy(obs, deterministic=True)[0]
    a1 = loaded.act_numpy(obs, deterministic=True)[0]
    assert np.allclose(a0, a1, atol=1e-6)


def test_reference_action_is_default_gains():
    assert np.allclose(REFERENCE_ACTION[:15], gs.GAIN_DEFAULT)
    assert np.allclose(REFERENCE_ACTION[15:], 1.0)


def test_phase_labels_from_groundspeed():
    labels = phase_labels_from_groundspeed_kts([200, 100, 50, 10, 1])
    assert list(labels) == [PHASE_TOUCHDOWN, PHASE_HIGH, PHASE_MID, PHASE_TAXI, PHASE_STOP]
