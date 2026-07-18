"""Тесты gain-пространства NPGS (абсолютные коэффициенты): покрытие пресетов,
обратимость z↔gain, валидность DEFAULT-bias, нормировка признаков."""

import json

import numpy as np

from ismpu.agent import gain_space as gs
from ismpu.config.scenarios import SCENARIOS
from ismpu.agent.shield import REGULATOR_ORDER


def _preset_vector(cfg):
    return np.array([getattr(cfg, gs._REG_TO_FIELD[reg])[key] for reg, key in gs.SLOTS])


def test_table_shape_and_order():
    assert gs.N_GAINS == 15 == len(gs.SLOTS)
    assert gs.SLOTS == [(reg, k) for reg in REGULATOR_ORDER for k in ("kp", "ki", "kd")]
    for arr in (gs.GAIN_REF, gs.GAIN_S, gs.GAIN_LO, gs.GAIN_HI, gs.GAIN_DEFAULT):
        assert arr.shape == (15,)


def test_every_preset_gain_inside_physical_band():
    for name, cfg in SCENARIOS.items():
        v = _preset_vector(cfg)
        assert np.all(gs.GAIN_LO <= v) and np.all(v <= gs.GAIN_HI), name


def test_z_zero_maps_to_ref():
    assert np.allclose(gs.to_gain(np.zeros(15)), gs.GAIN_REF)


def test_preset_round_trip_is_exact():
    for cfg in SCENARIOS.values():
        v = _preset_vector(cfg)
        rt = gs.to_gain(gs.inv_gain(v))
        assert np.allclose(rt, v, rtol=1e-9)


def test_default_bias_reproduces_default():
    b = gs.default_bias()
    assert np.all(np.isfinite(b))
    assert np.allclose(gs.to_gain(b), gs.GAIN_DEFAULT, rtol=1e-6)


def test_s_covers_default_offset_from_ref():
    # bias-инициализация корректна только если s_i ≥ |log(DEFAULT_i/ref_i)|.
    assert np.all(gs.GAIN_S >= np.abs(np.log(gs.GAIN_DEFAULT / gs.GAIN_REF)) - 1e-9)


def test_gain_norm_endpoints():
    assert np.allclose(gs.gain_norm(gs.GAIN_REF), 0.0, atol=1e-9)
    assert np.allclose(gs.gain_norm(gs.GAIN_HI), 1.0)
    assert np.allclose(gs.gain_norm(gs.GAIN_LO), -1.0)


def test_inv_gain_handles_nonpositive_without_error():
    z = gs.inv_gain(np.zeros(15))       # gain=0 → guard, конечный z
    assert np.all(np.isfinite(z))


def test_snapshot_serializable_and_complete():
    snap = gs.snapshot()
    json.dumps(snap)
    assert len(snap["ref"]) == len(snap["s"]) == len(snap["slots"]) == 15
    assert snap["expand"] == gs.EXPAND
