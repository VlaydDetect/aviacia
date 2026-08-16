"""Этап 8: два минимальных SFT-регрессора, offline data и fail-safe runtime."""

import csv
import json
from pathlib import Path

import numpy as np
import pytest

torch = pytest.importorskip("torch")

from fakes import FakeConnector, airborne_inputs
from ismpu.agent.pid_gain_regressor import (
    GainGuard, Normalization, PidGainRegressor, feature_schema_hash,
)
from ismpu.config.run_matrix import SOURCE_SHA256
from ismpu.config.scenarios import SCENARIOS
from ismpu.control.system import ControllingSystem
from ismpu.envs.ics_sim import ICSSim
from ismpu.runtime.pretrain import (
    RunSequence, SftTrainConfig, WindowDataset, load_offline_dataset, split_runs,
    train_segment,
)
from ismpu.runtime.sft import (
    AIR_FEATURES, FEATURES, GAIN_LAYOUT, PID_NAMES, SftRuntime, apply_gain_vector,
    controller_gain_vector,
)


def _checkpoint(path: Path, segment: str, preset: np.ndarray, *, activation=False) -> Path:
    model = PidGainRegressor(len(FEATURES[segment]), len(preset), hidden_size=8)
    for parameter in model.parameters():
        torch.nn.init.zeros_(parameter)
    feature_norm = Normalization(
        np.zeros(len(FEATURES[segment])), np.full(len(FEATURES[segment]), 1e9),
        np.full(len(FEATURES[segment]), -1e12), np.full(len(FEATURES[segment]), 1e12),
    )
    target_norm = Normalization(
        preset.copy(), np.ones(len(preset)), preset.copy(), preset.copy())
    lower = np.minimum(preset * 0.3, preset * 2.5)
    upper = np.maximum(preset * 0.3, preset * 2.5)
    model.save_checkpoint(path, {
        "segment": segment, "window_frames": 40, "frequency_hz": 20.0,
        "feature_schema": list(FEATURES[segment]),
        "feature_schema_hash": feature_schema_hash(FEATURES[segment]),
        "gain_layout": list(GAIN_LAYOUT[segment]),
        "normalization": {
            "features": feature_norm.snapshot(), "targets": target_norm.snapshot()},
        "physical_bounds": {"low": lower.tolist(), "high": upper.tolist()},
        "matrix_hash": SOURCE_SHA256, "aircraft_profile": "mc21",
        "run_ids": ["accepted-1"],
        "split_run_ids": {
            "train": ["accepted-1"], "validation": ["accepted-2"],
            "test": ["accepted-3"]},
        "metrics": {"gate_passed": True},
        "activation": {name: activation for name in (
            "replay", "xplane", "shadow", "no_degradation")},
    })
    return path


def test_regressor_is_exact_minimal_architecture_and_has_separate_dimensions():
    air = PidGainRegressor(11, 9, hidden_size=7)
    ground = PidGainRegressor(13, 15, hidden_size=7)

    assert [type(layer) for layer in air.children()] == [
        torch.nn.LayerNorm, torch.nn.GRU, torch.nn.Linear]
    assert air.gru.num_layers == ground.gru.num_layers == 1
    assert air(torch.zeros(2, 40, 11)).shape == (2, 9)
    assert ground(torch.zeros(2, 40, 13)).shape == (2, 15)
    assert not any(hasattr(model, name) for model in (air, ground)
                   for name in ("critic", "log_std", "channel_weights"))


def test_feature_schemas_exclude_current_gains_and_cover_both_segments():
    assert len(GAIN_LAYOUT["air"]) == 9
    assert len(GAIN_LAYOUT["ground"]) == 15
    assert "approach_input_LocDeviation" in AIR_FEATURES
    for names in FEATURES.values():
        assert not any(name.endswith(("_kp", "_ki", "_kd")) for name in names)


def _write_run(root: Path, run_id: str, *, eligible=True, policy="classical") -> Path:
    directory = root / run_id
    directory.mkdir()
    (directory / "manifest.json").write_text(json.dumps({
        "execution_id": run_id, "control_policy": policy, "aircraft_profile": "mc21",
        "matrix_source_sha256": SOURCE_SHA256,
        "scenario": {"conditions": {"approach": {"wind": int(run_id[-1]) % 2}}},
    }), encoding="utf-8")
    (directory / "report.json").write_text(
        json.dumps({"sft_eligible": eligible}), encoding="utf-8")
    fields = ["tick_id", "valid", "radio_altitude_ft"] + [
        f"pid_{pid}_{gain}" for pid in PID_NAMES["air"] for gain in ("kp", "ki", "kd")]
    with (directory / "approach.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for tick in range(1, 7):
            row = {"tick_id": tick, "valid": 1, "radio_altitude_ft": 500 - tick}
            for index, name in enumerate(fields[3:], 1):
                row[name] = index + int(run_id[-1]) * 0.1
            writer.writerow(row)
    return directory


def test_offline_loader_uses_only_accepted_classical_segment_csv(tmp_path):
    accepted = _write_run(tmp_path, "run1")
    _write_run(tmp_path, "run2", eligible=False)
    _write_run(tmp_path, "run3", policy="sft-shadow")

    runs = load_offline_dataset(tmp_path, "air")

    assert [run.directory for run in runs] == [accepted]
    assert runs[0].features.shape == (6, len(FEATURES["air"]))
    assert runs[0].targets.shape == (6, 9)


def test_run_split_has_no_window_leakage_and_windows_are_continuous():
    runs = [RunSequence(
        f"run-{index}", f"condition-{index % 2}",
        np.arange(30, dtype=float).reshape(10, 3) + index,
        np.full((10, 2), index, dtype=float), Path(str(index)),
    ) for index in range(6)]
    split = split_runs(runs, seed=7)
    ids = split.run_ids()
    assert set(ids["train"]).isdisjoint(ids["validation"])
    assert set(ids["train"]).isdisjoint(ids["test"])
    all_features = np.concatenate([run.features for run in split.train])
    all_targets = np.concatenate([run.targets for run in split.train])
    feature_norm, target_norm = Normalization.fit(all_features), Normalization.fit(all_targets)
    dataset = WindowDataset(split.train, 4, feature_norm, target_norm)
    assert len(dataset) == sum(len(run.features) - 3 for run in split.train)
    first_window, _ = dataset[0]
    assert first_window.shape == (4, 3)

    interrupted = RunSequence(
        "dropout", "condition", np.arange(16, dtype=float).reshape(8, 2),
        np.ones((8, 1)), Path("dropout"),
        np.array([1, 1, 1, 0, 1, 1, 1, 1], dtype=bool))
    interrupted_features = Normalization.fit(interrupted.features)
    interrupted_targets = Normalization.fit(interrupted.targets)
    assert len(WindowDataset(
        [interrupted], 3, interrupted_features, interrupted_targets)) == 3


def test_offline_training_is_reproducible_and_checkpoint_lists_run_splits(tmp_path):
    runs = tmp_path / "runs"
    runs.mkdir()
    for index in range(1, 7):
        _write_run(runs, f"run{index}")
    cfg = SftTrainConfig(
        window_frames=4, hidden_size=4, epochs=2, batch_size=8, seed=19)

    first = train_segment(runs, "air", tmp_path / "first.pt", cfg)
    second = train_segment(runs, "air", tmp_path / "second.pt", cfg)
    model_a, checkpoint = PidGainRegressor.load_checkpoint(
        first.checkpoint, require_gate=False)
    model_b = PidGainRegressor.load(second.checkpoint, require_gate=False)

    assert checkpoint["target_source"].startswith("applied_pid_gains")
    assert set(checkpoint["run_ids"]) == {f"run{i}" for i in range(1, 7)}
    assert all(torch.equal(model_a.state_dict()[key], model_b.state_dict()[key])
               for key in model_a.state_dict())


def test_gain_guard_falls_back_and_limits_by_actual_dt():
    preset = np.array([-4.0, 2.0, 0.0])
    guard = GainGuard([-10.0, 0.0, 0.0], [-1.0, 8.0, 0.0])

    incomplete = guard.guard(None, preset, preset, 0.05, window_ready=False)
    nonfinite = guard.guard([np.nan, 2.0, 0.0], preset, preset, 0.05)
    limited = guard.guard([-6.0, 3.0, 0.0], preset, preset, 0.1)

    assert incomplete.fallback and incomplete.reason == "window_incomplete"
    assert nonfinite.fallback and np.array_equal(nonfinite.gains, preset)
    assert limited.rate_limited and not limited.fallback
    assert np.allclose(limited.gains, [-4.1, 2.05, 0.0])


def test_sft_application_changes_only_pid_coefficients():
    controller = ControllingSystem()
    SCENARIOS["default"].apply_control(controller, "mc21")
    before_state = dict(vars(controller.state))
    before_limits = {
        name: (pid.min_out, pid.max_out, pid.anti_windup)
        for name, pid in controller.pids.items()}
    gains = controller_gain_vector(controller, "ground") * 1.01

    apply_gain_vector(controller, "ground", gains)

    assert dict(vars(controller.state)) == before_state
    assert before_limits == {
        name: (pid.min_out, pid.max_out, pid.anti_windup)
        for name, pid in controller.pids.items()}
    assert np.allclose(controller_gain_vector(controller, "ground"), gains)


def test_checkpoint_contract_and_ics_activation_gate(tmp_path):
    preset = np.arange(1.0, 10.0)
    path = _checkpoint(tmp_path / "sft_air.pt", "air", preset)
    model, payload = PidGainRegressor.load_checkpoint(
        path, expected_segment="air", expected_features=FEATURES["air"],
        expected_gain_layout=GAIN_LAYOUT["air"], expected_matrix_hash=SOURCE_SHA256)
    assert model.output_dim == 9 and payload["run_ids"] == ["accepted-1"]
    with pytest.raises(PermissionError, match="ICS sft-active"):
        SftRuntime.from_checkpoints(mode="sft-active", air_path=path, backend="ics")
    admitted = _checkpoint(tmp_path / "admitted.pt", "air", preset, activation=True)
    assert SftRuntime.from_checkpoints(
        mode="sft-active", air_path=admitted, backend="ics").models["air"] is not None


def test_runtime_predicts_each_tick_after_40_frames_and_falls_back_before_it(tmp_path):
    sim = ICSSim(
        connector=FakeConnector(airborne_inputs()), aircraft_profile="mc21",
        validate_conditions=False)
    telemetry = sim.read_telemetry()
    controller = ControllingSystem(sim)
    controller.bind_scenario(SCENARIOS["default"], "mc21")
    controller.begin_flight(telemetry)
    preset = controller_gain_vector(controller, "air")
    runtime = SftRuntime.from_checkpoints(
        mode="sft-active", air_path=_checkpoint(tmp_path / "sft_air.pt", "air", preset),
        backend="xplane")

    first = runtime.before_step(controller, telemetry, 0.05)
    assert first.fallback and first.reason == "window_incomplete"
    for _ in range(42):
        runtime.before_step(controller, telemetry, 0.05)
        controller.control_step(0.05, telemetry, send=False)
        runtime.after_step(controller, telemetry, 0.05)

    assert controller.sft_diagnostics["prediction_count"] == 3
    assert controller.sft_diagnostics["window_ready"] is True
    assert np.allclose(controller_gain_vector(controller, "air"), preset)
