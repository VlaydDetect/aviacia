"""Тесты NPGS (Этап 4, §10): формы forward, identity при z=0, ограничение выхода,
детерминизм greedy, соответствие сборки действия `Corrections`/`Shield`, save/load.

torch — опционален (extra `rl`); при его отсутствии тесты пропускаются (venv с CUDA).
"""

import numpy as np
import pytest

torch = pytest.importorskip("torch")

from ismpu.agent.gain_scheduler import (
    NPGS, NPGSConfig, build_npgs, POLICY_DIM, N_ALPHA_OUT, phase_labels_from_groundspeed_kts,
    PHASE_TOUCHDOWN, PHASE_HIGH, PHASE_MID, PHASE_TAXI, PHASE_STOP,
)
from ismpu.agent.shield import ACTION_DIM, REGULATOR_ORDER
from ismpu.envs.action import decode, IDENTITY_ACTION, ACTION_LOW, ACTION_HIGH
from ismpu.envs.observation import OBS_DIM


@pytest.fixture
def net():
    torch.manual_seed(0)
    return build_npgs(NPGSConfig(window=8))


def test_forward_shapes(net):
    B, T = 4, 8
    obs = torch.randn(B, T, OBS_DIM)
    mean, value, phase = net(obs)
    assert mean.shape == (B, POLICY_DIM)
    assert value.shape == (B,)
    assert phase.shape == (B, 5)


def test_param_count_is_compact(net):
    n = sum(p.numel() for p in net.parameters())
    assert 0.5e6 < n < 3e6   # ~1–2 M (§10): реалтайм < 50 мс


def test_identity_at_zero_matches_identity_action(net):
    u0 = torch.zeros(3, POLICY_DIM)
    action = net.expand_to_action(net.bound(u0))
    assert action.shape == (3, ACTION_DIM)
    assert torch.allclose(action, torch.tensor(IDENTITY_ACTION), atol=1e-6)


def test_output_bounded_for_extreme_inputs(net):
    for val, exp_a, exp_w in [(50.0, 1.5, 2.0), (-50.0, 0.5, 0.0)]:
        a = net.expand_to_action(net.bound(torch.full((2, POLICY_DIM), val))).numpy()
        assert np.allclose(a[:, :15].max() if val > 0 else a[:, :15].min(), exp_a, atol=1e-4)
        assert np.allclose(a[:, 15:].max() if val > 0 else a[:, 15:].min(), exp_w, atol=1e-4)
    # никогда не выходит за band действия
    a = net.expand_to_action(net.bound(torch.randn(32, POLICY_DIM) * 10)).numpy()
    assert np.all(a >= ACTION_LOW - 1e-5) and np.all(a <= ACTION_HIGH + 1e-5)


def test_greedy_near_identity_at_init(net):
    # mean-головы инициализированы малым gain → старт ≈ классика (инвариант §1).
    obs = torch.randn(4, 8, OBS_DIM)
    a = net.get_action(obs, deterministic=True)["action"].detach().numpy()
    assert np.abs(a - IDENTITY_ACTION).max() < 0.15


def test_greedy_is_deterministic(net):
    obs = torch.randn(2, 8, OBS_DIM)
    a1 = net.get_action(obs, deterministic=True)["action"]
    a2 = net.get_action(obs, deterministic=True)["action"]
    assert torch.allclose(a1, a2)


def test_action_expansion_duplicates_brake_and_reverse(net):
    a = net.get_action(torch.randn(1, 8, OBS_DIM), deterministic=True)["action"][0].detach().numpy()
    corr = decode(a)
    assert corr.alpha["pid_brake_l"] == corr.alpha["pid_brake_r"]   # симметричное торможение
    assert corr.alpha["pid_rev_l"] == corr.alpha["pid_rev_r"]        # симметричный реверс
    assert len(a) == ACTION_DIM == len(REGULATOR_ORDER) * 3 + 2


def test_evaluate_actions_matches_get_action(net):
    obs = torch.randn(5, 8, OBS_DIM)
    out = net.get_action(obs, deterministic=False)
    logp, ent, val, mean, phase = net.evaluate_actions(obs, out["raw"])
    assert torch.allclose(out["logp"], logp, atol=1e-5)
    assert torch.allclose(out["value"], val, atol=1e-5)
    assert torch.allclose(out["mean"], mean, atol=1e-5)


def test_act_numpy_single_window(net):
    obs = np.random.randn(8, OBS_DIM).astype(np.float32)
    action, raw, logp, value = net.act_numpy(obs, deterministic=True)
    assert action.shape == (ACTION_DIM,)
    assert raw.shape == (POLICY_DIM,)
    assert isinstance(logp, float) and isinstance(value, float)


def test_save_load_roundtrip(net, tmp_path):
    path = str(tmp_path / "npgs.pt")
    net.save(path)
    loaded = NPGS.load(path)
    obs = np.random.randn(8, OBS_DIM).astype(np.float32)
    a0 = net.act_numpy(obs, deterministic=True)[0]
    a1 = loaded.act_numpy(obs, deterministic=True)[0]
    assert np.allclose(a0, a1, atol=1e-6)


def test_phase_labels_from_groundspeed():
    labels = phase_labels_from_groundspeed_kts([200, 100, 50, 10, 1])
    assert list(labels) == [PHASE_TOUCHDOWN, PHASE_HIGH, PHASE_MID, PHASE_TAXI, PHASE_STOP]
