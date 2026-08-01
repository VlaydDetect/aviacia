"""Профильные пространства абсолютных PID-коэффициентов NPGS."""

import json

import numpy as np

from ismpu.agent.gain_space import GainSpace, gain_space_for
from ismpu.config.regulators import GAIN_KEYS, REGULATOR_ORDER
from ismpu.config.scenarios import SCENARIOS
from ismpu.config.segments import FlightSegment


def _vector(space, config):
    pids = config.build_pids()
    return np.array([
        getattr(pids[regulator], key)
        for regulator, key in space.slots
    ])


def test_profile_spaces_have_stable_17_action_contract_and_independent_identity():
    mc21 = gain_space_for("mc21")
    a330 = gain_space_for("a330-300")
    assert len(mc21.slots) == len(a330.slots) == 15
    assert mc21.slots == tuple(
        (regulator, key) for regulator in REGULATOR_ORDER for key in GAIN_KEYS
    )
    assert mc21.aircraft_profile == "mc21"
    assert a330.aircraft_profile == "a330-300"
    assert mc21 is not a330


def test_every_profile_preset_gain_is_inside_its_band():
    for profile in ("mc21", "a330-300"):
        space = gain_space_for(profile)
        for name, scenario in SCENARIOS.items():
            config = scenario.control_for(profile, FlightSegment.ROLLOUT)
            values = _vector(space, config)
            assert np.all(space.lo <= values) and np.all(values <= space.hi), name


def test_transform_roundtrip_and_default_bias():
    space = gain_space_for("mc21")
    assert np.allclose(space.to_gain(np.zeros(15)), space.ref)
    assert np.allclose(space.to_gain(space.inv_gain(space.default)), space.default, rtol=1e-6)
    for scenario in SCENARIOS.values():
        values = _vector(space, scenario.control_for("mc21", FlightSegment.ROLLOUT))
        assert np.allclose(space.to_gain(space.inv_gain(values)), values, rtol=1e-9)


def test_normalization_endpoints_and_nonpositive_guard():
    space = gain_space_for("mc21")
    assert np.allclose(space.gain_norm(space.ref), 0.0)
    assert np.allclose(space.gain_norm(space.hi), 1.0)
    assert np.allclose(space.gain_norm(space.lo), -1.0)
    assert np.all(np.isfinite(space.inv_gain(np.zeros(15))))


def test_snapshot_is_serializable_profile_bound_and_exactly_checked():
    space = gain_space_for("mc21")
    snapshot = space.snapshot()
    json.dumps(snapshot)
    assert snapshot["aircraft_profile"] == "mc21"
    assert len(snapshot["ref"]) == len(snapshot["slots"]) == 15
    assert space.compatible_with(snapshot)
    assert not gain_space_for("a330-300").compatible_with(snapshot)


def test_gain_space_can_be_built_from_external_scenario_registry():
    external = {"default": SCENARIOS["default"]}
    space = GainSpace.build("mc21", external)
    assert space.default.shape == (15,)
