"""Офлайн-SFT двух PID gain-регрессоров из принятых ``approach/ground.csv``."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Sequence

import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset

from ismpu.agent.pid_gain_regressor import (
    DEFAULT_FREQUENCY_HZ, DEFAULT_WINDOW_FRAMES, Normalization, PidGainRegressor,
    feature_schema_hash,
)
from ismpu.config.run_matrix import SOURCE_SHA256
from ismpu.config.scenarios import SCENARIOS
from ismpu.config.segments import FlightSegment
from ismpu.runtime.run_reader import RunReader
from ismpu.runtime.sft import FEATURES, GAIN_LAYOUT, feature_vector, gain_vector_from_row


@dataclass(frozen=True)
class RunSequence:
    run_id: str
    condition_key: str
    features: np.ndarray
    targets: np.ndarray
    directory: Path
    valid: np.ndarray | None = None
    aircraft_profile: str = "mc21"


@dataclass(frozen=True)
class RunSplit:
    train: tuple[RunSequence, ...]
    validation: tuple[RunSequence, ...]
    test: tuple[RunSequence, ...]

    def run_ids(self) -> dict[str, list[str]]:
        return {
            name: [run.run_id for run in getattr(self, name)]
            for name in ("train", "validation", "test")
        }


@dataclass
class SftTrainConfig:
    window_frames: int = DEFAULT_WINDOW_FRAMES
    hidden_size: int = 64
    epochs: int = 40
    batch_size: int = 256
    learning_rate: float = 1e-3
    seed: int = 0
    device: str = "cpu"
    train_fraction: float = 0.70
    validation_fraction: float = 0.15
    mae_limit: float = 0.05
    p95_limit: float = 0.10


@dataclass
class PretrainRunConfig:
    runs_root: str | Path = "runs"
    checkpoint_dir: str | Path = "checkpoints"
    segments: tuple[str, ...] = ("air", "ground")
    matrix_hash: str = SOURCE_SHA256
    train: SftTrainConfig = field(default_factory=SftTrainConfig)
    # Совместимость каталожных тестов до удаления live-capture в Этапе 9.
    variants_per_preset: int = 20
    presets: tuple[str, ...] | None = None
    include_drafts: bool = False
    aircraft_profile: str = "mc21"
    backend: str = "xplane"


@dataclass(frozen=True)
class TrainingResult:
    segment: str
    checkpoint: Path
    metrics: dict
    split_run_ids: dict[str, list[str]]


def load_offline_dataset(
    sources: str | Path | Sequence[str | Path],
    segment: str,
    *,
    matrix_hash: str = SOURCE_SHA256,
) -> list[RunSequence]:
    """Прочитать только PASS/accepted/classical run-directories; live backend не вызывается."""
    if segment not in FEATURES:
        raise ValueError("segment must be 'air' or 'ground'")
    filename = "approach.csv" if segment == "air" else "ground.csv"
    sequences: list[RunSequence] = []
    for directory in _run_directories(sources):
        report_path = directory / "report.json"
        manifest_path = directory / "manifest.json"
        csv_path = directory / filename
        if not (report_path.is_file() and manifest_path.is_file() and csv_path.is_file()):
            continue
        report = json.loads(report_path.read_text(encoding="utf-8"))
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if report.get("sft_eligible") is not True:
            continue
        if manifest.get("control_policy", "classical") != "classical":
            continue
        if manifest.get("matrix_source_sha256") != matrix_hash:
            raise ValueError(f"{directory}: run-matrix hash mismatch")
        rows = list(RunReader(csv_path).rows())
        if not rows:
            continue
        feature_rows, target_rows, valid_rows = [], [], []
        for row in rows:
            feature_rows.append(feature_vector(row, segment))
            target_rows.append(gain_vector_from_row(row, segment))
            valid_rows.append(bool(row.get("valid", True)))
        if not feature_rows:
            continue
        run_id = str(manifest.get("execution_id") or directory.name)
        sequences.append(RunSequence(
            run_id=run_id,
            condition_key=_condition_key(manifest, rows[0], segment),
            features=np.stack(feature_rows), targets=np.stack(target_rows),
            directory=directory, valid=np.asarray(valid_rows, dtype=bool),
            aircraft_profile=str(manifest.get("aircraft_profile") or "mc21"),
        ))
    if not sequences:
        raise RuntimeError(f"no accepted classical {filename} runs found")
    ids = [run.run_id for run in sequences]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate execution_id in SFT sources")
    return sorted(sequences, key=lambda run: run.run_id)


def split_runs(
    runs: Sequence[RunSequence], *, seed: int = 0,
    train_fraction: float = 0.70, validation_fraction: float = 0.15,
) -> RunSplit:
    """Стратифицировать по условиям, назначая целый run ровно одному split."""
    if not 0.0 < train_fraction < 1.0 or not 0.0 <= validation_fraction < 1.0:
        raise ValueError("invalid split fractions")
    if train_fraction + validation_fraction >= 1.0:
        raise ValueError("train + validation fractions must be below one")
    buckets: dict[str, list[RunSequence]] = {}
    for run in runs:
        buckets.setdefault(run.condition_key, []).append(run)
    result: dict[str, list[RunSequence]] = {
        "train": [], "validation": [], "test": [],
    }
    for condition, group in sorted(buckets.items()):
        ordered = sorted(group, key=lambda run: _stable_rank(seed, condition, run.run_id))
        n = len(ordered)
        n_validation = max(1, round(n * validation_fraction)) if n >= 3 else int(n == 2)
        n_test = max(1, round(n * (1.0 - train_fraction - validation_fraction))) if n >= 3 else 0
        while n_validation + n_test >= n:
            if n_validation > n_test:
                n_validation -= 1
            else:
                n_test -= 1
        result["validation"].extend(ordered[:n_validation])
        result["test"].extend(ordered[n_validation:n_validation + n_test])
        result["train"].extend(ordered[n_validation + n_test:])

    # Маленькие condition-группы всё равно делятся только целыми прогонами.
    for missing in ("validation", "test"):
        if not result[missing] and len(result["train"]) > 1:
            result[missing].append(result["train"].pop())
    split = RunSplit(*(tuple(result[name]) for name in ("train", "validation", "test")))
    memberships = [run.run_id for name in ("train", "validation", "test")
                   for run in getattr(split, name)]
    if len(memberships) != len(set(memberships)) or set(memberships) != {run.run_id for run in runs}:
        raise RuntimeError("run-level split leakage")
    return split


class WindowDataset(Dataset):
    """Ленивые непрерывные окна: один прогноз на каждый такт после заполнения истории."""

    def __init__(
        self,
        runs: Sequence[RunSequence],
        window_frames: int,
        feature_norm: Normalization,
        target_norm: Normalization,
    ) -> None:
        if window_frames <= 0:
            raise ValueError("window_frames must be positive")
        self.window_frames = int(window_frames)
        self.runs: list[tuple[np.ndarray, np.ndarray, str]] = []
        self.indices: list[tuple[int, int]] = []
        for run in runs:
            if len(run.features) < window_frames:
                continue
            features, _ = feature_norm.transform(run.features)
            targets, _ = target_norm.transform(run.targets)
            run_index = len(self.runs)
            self.runs.append((features, targets, run.run_id))
            self.indices.extend(
                (run_index, end) for end in _window_ends(run, window_frames))

    def __len__(self) -> int:
        return len(self.indices)

    def __getitem__(self, index: int):
        run_index, end = self.indices[index]
        features, targets, _ = self.runs[run_index]
        start = end + 1 - self.window_frames
        return torch.from_numpy(features[start:end + 1]), torch.from_numpy(targets[end])


def train_segment(
    sources: str | Path | Sequence[str | Path],
    segment: str,
    output: str | Path,
    config: SftTrainConfig | None = None,
    *,
    matrix_hash: str = SOURCE_SHA256,
) -> TrainingResult:
    """Обучить один регрессор, оценить gates и записать самодостаточный checkpoint."""
    cfg = config or SftTrainConfig()
    if (cfg.window_frames <= 0 or cfg.hidden_size <= 0 or cfg.epochs <= 0
            or cfg.batch_size <= 0 or cfg.learning_rate <= 0.0
            or cfg.mae_limit < 0.0 or cfg.p95_limit < 0.0):
        raise ValueError("invalid SFT training configuration")
    _seed_everything(cfg.seed)
    runs = load_offline_dataset(sources, segment, matrix_hash=matrix_hash)
    profiles = {run.aircraft_profile for run in runs}
    if len(profiles) != 1:
        raise ValueError(f"SFT sources mix aircraft profiles: {sorted(profiles)}")
    split = split_runs(
        runs, seed=cfg.seed, train_fraction=cfg.train_fraction,
        validation_fraction=cfg.validation_fraction,
    )
    if not split.train or not split.validation or not split.test:
        raise RuntimeError("SFT requires non-empty train/validation/test run splits")
    feature_norm = _fit_feature_normalization(split.train)
    target_norm = Normalization.fit(_target_rows(split.train, cfg.window_frames))
    datasets = {
        name: WindowDataset(getattr(split, name), cfg.window_frames, feature_norm, target_norm)
        for name in ("train", "validation", "test")
    }
    if any(not dataset for dataset in datasets.values()):
        raise RuntimeError("every split needs at least one complete SFT window")

    device_name = cfg.device if cfg.device != "cuda" or torch.cuda.is_available() else "cpu"
    device = torch.device(device_name)
    model = PidGainRegressor(
        len(FEATURES[segment]), len(GAIN_LAYOUT[segment]), cfg.hidden_size,
    ).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=cfg.learning_rate)
    generator = torch.Generator().manual_seed(cfg.seed)
    loader = DataLoader(
        datasets["train"], batch_size=cfg.batch_size, shuffle=True, generator=generator,
    )
    best_state, best_loss = None, math.inf
    history: list[float] = []
    for _ in range(cfg.epochs):
        model.train()
        total, count = 0.0, 0
        for features, targets in loader:
            features, targets = features.to(device), targets.to(device)
            loss = F.mse_loss(model(features), targets)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total += float(loss.item()) * len(features)
            count += len(features)
        history.append(total / max(1, count))
        validation_loss = _normalized_mse(model, datasets["validation"], device, cfg.batch_size)
        if validation_loss < best_loss:
            best_loss = validation_loss
            best_state = copy.deepcopy(model.state_dict())
    if best_state is not None:
        model.load_state_dict(best_state)
    model.eval()

    physical_low, physical_high = _physical_bounds(runs, cfg.window_frames)
    expert_targets = _target_rows(runs, cfg.window_frames)
    expert_range = expert_targets.max(axis=0) - expert_targets.min(axis=0)
    baseline = _target_rows(split.train, cfg.window_frames).mean(axis=0)
    metrics = {
        "history_mse": history,
        "best_validation_mse": best_loss,
        "splits": {},
    }
    for name in ("train", "validation", "test"):
        actual = _target_rows(getattr(split, name), cfg.window_frames)
        predicted = _predict(model, datasets[name], target_norm, device, cfg.batch_size)
        metrics["splits"][name] = _regression_metrics(
            actual, predicted, baseline, expert_range,
            GAIN_LAYOUT[segment], cfg.mae_limit, cfg.p95_limit,
        )
    metrics["gate_passed"] = bool(
        metrics["splits"]["validation"]["passed"]
        and metrics["splits"]["test"]["passed"])
    split_ids = split.run_ids()
    metadata = {
        "segment": segment,
        "window_frames": cfg.window_frames,
        "frequency_hz": DEFAULT_FREQUENCY_HZ,
        "feature_schema": list(FEATURES[segment]),
        "feature_schema_hash": feature_schema_hash(FEATURES[segment]),
        "gain_layout": list(GAIN_LAYOUT[segment]),
        "normalization": {
            "features": feature_norm.snapshot(), "targets": target_norm.snapshot(),
        },
        "physical_bounds": {"low": physical_low.tolist(), "high": physical_high.tolist()},
        "matrix_hash": matrix_hash,
        "aircraft_profile": profiles.pop(),
        "run_ids": sorted(run.run_id for run in runs),
        "split_run_ids": split_ids,
        "metrics": metrics,
        "activation": {
            "replay": False, "xplane": False, "shadow": False,
            "no_degradation": False,
        },
        "target_source": "applied_pid_gains_from_accepted_classical_runs",
    }
    checkpoint = Path(output)
    model.cpu().save_checkpoint(checkpoint, metadata)
    return TrainingResult(segment, checkpoint, metrics, split_ids)


def run_pretrain(config: PretrainRunConfig | None = None) -> dict[str, TrainingResult]:
    cfg = config or PretrainRunConfig()
    result = {}
    for segment in cfg.segments:
        path = Path(cfg.checkpoint_dir) / f"sft_{segment}.pt"
        result[segment] = train_segment(
            cfg.runs_root, segment, path, cfg.train, matrix_hash=cfg.matrix_hash)
        print(f"{segment}: gate={result[segment].metrics['gate_passed']} -> {path}")
    return result


def build_scenarios(cfg: PretrainRunConfig) -> list:
    """Legacy-каталог accepted presets; активный offline trainer его не вызывает."""
    selected = _selected_presets(cfg)
    return [replace(base, scenario_id=f"{base.scenario_id}-v{variant:02d}")
            for base in selected for variant in range(cfg.variants_per_preset)]


def _selected_presets(cfg: PretrainRunConfig) -> list:
    if cfg.include_drafts:
        raise ValueError("SFT допускает только ControlProfile со статусом accepted")
    if cfg.presets is not None:
        unknown = [name for name in cfg.presets if name not in SCENARIOS]
        if unknown:
            raise KeyError(f"неизвестные пресеты для SFT: {unknown}")
        chosen = [SCENARIOS[name] for name in cfg.presets]
    else:
        chosen = list(SCENARIOS.values())
    chosen = [scenario for scenario in chosen if (
        not scenario.matrix_codes or FlightSegment.ROLLOUT in scenario.matrix_codes)]
    rejected = [scenario for scenario in chosen if not scenario.is_accepted(
        cfg.aircraft_profile, FlightSegment.ROLLOUT)]
    if rejected:
        print(f"[SFT] пропущены не-accepted пресеты ({len(rejected)}): "
              + ", ".join(scenario.scenario_id for scenario in rejected))
    accepted = [scenario for scenario in chosen if scenario not in rejected]
    if not accepted:
        raise ValueError("для SFT не осталось ни одного accepted пресета")
    return accepted


def matrix_preset_names(
    *, only_calibrated: bool = True, aircraft_profile: str = "mc21",
) -> tuple[str, ...]:
    """Legacy-представление наземных строк; dataset строится по run-directory."""
    from ismpu.config.run_matrix import ground_cases

    cases = [case for case in ground_cases() if case.preset in SCENARIOS]
    if only_calibrated:
        cases = [case for case in cases if SCENARIOS[case.preset].is_accepted(
            aircraft_profile,
            FlightSegment.TAXI if case.segment == "taxi" else FlightSegment.ROLLOUT)]
    return tuple(case.preset for case in cases)


def _run_directories(sources: str | Path | Sequence[str | Path]) -> list[Path]:
    values = [sources] if isinstance(sources, (str, Path)) else list(sources)
    directories: list[Path] = []
    for value in values:
        path = Path(value)
        if (path / "manifest.json").is_file():
            directories.append(path)
        elif path.is_dir():
            directories.extend(child for child in path.iterdir() if child.is_dir())
    return sorted(set(directories))


def _condition_key(manifest: dict, first_row: dict, segment: str) -> str:
    scenario = manifest.get("scenario") if isinstance(manifest.get("scenario"), dict) else {}
    conditions = scenario.get("conditions", {})
    condition = conditions.get(segment) or conditions.get(
        FlightSegment.APPROACH.value if segment == "air" else FlightSegment.ROLLOUT.value)
    if condition is None:
        condition = {
            "weather": first_row.get("weather"), "faults": first_row.get("faults"),
            "runway": first_row.get("runway_profile_name"),
        }
    payload = json.dumps(condition, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _stable_rank(seed: int, condition: str, run_id: str) -> str:
    return hashlib.sha256(f"{seed}:{condition}:{run_id}".encode()).hexdigest()


def _target_rows(runs: Sequence[RunSequence], window_frames: int) -> np.ndarray:
    arrays = [run.targets[list(_window_ends(run, window_frames))] for run in runs]
    arrays = [array for array in arrays if len(array)]
    if not arrays:
        raise RuntimeError("split has no continuous complete windows")
    return np.concatenate(arrays, axis=0)


def _fit_feature_normalization(runs: Sequence[RunSequence]) -> Normalization:
    size = runs[0].features.shape[1]
    count = 0
    total = np.zeros(size, dtype=np.float64)
    squares = np.zeros(size, dtype=np.float64)
    minimum = np.full(size, np.inf)
    maximum = np.full(size, -np.inf)
    for run in runs:
        data = np.asarray(run.features[_valid_mask(run)], dtype=np.float64)
        if not len(data):
            continue
        count += len(data)
        total += data.sum(axis=0)
        squares += np.square(data).sum(axis=0)
        minimum = np.minimum(minimum, data.min(axis=0))
        maximum = np.maximum(maximum, data.max(axis=0))
    if not count:
        raise RuntimeError("training split has no valid feature frames")
    mean = total / count
    scale = np.sqrt(np.maximum(squares / count - np.square(mean), 0.0))
    scale[scale < 1e-12] = 1.0
    return Normalization(mean, scale, minimum, maximum)


def _valid_mask(run: RunSequence) -> np.ndarray:
    return (np.ones(len(run.features), dtype=bool) if run.valid is None
            else np.asarray(run.valid, dtype=bool))


def _window_ends(run: RunSequence, window_frames: int):
    valid = _valid_mask(run)
    for end in range(window_frames - 1, len(valid)):
        if valid[end + 1 - window_frames:end + 1].all():
            yield end


def _physical_bounds(runs: Sequence[RunSequence], window_frames: int) -> tuple[np.ndarray, np.ndarray]:
    targets = _target_rows(runs, window_frames)
    scaled_a, scaled_b = targets * 0.3, targets * 2.5
    return np.minimum(scaled_a, scaled_b).min(axis=0), np.maximum(scaled_a, scaled_b).max(axis=0)


def _normalized_mse(model, dataset, device, batch_size: int) -> float:
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False)
    total, count = 0.0, 0
    model.eval()
    with torch.no_grad():
        for features, targets in loader:
            loss = F.mse_loss(model(features.to(device)), targets.to(device), reduction="sum")
            total += float(loss.item())
            count += targets.numel()
    return total / max(1, count)


def _predict(model, dataset, target_norm, device, batch_size: int) -> np.ndarray:
    outputs = []
    model.eval()
    with torch.no_grad():
        for features, _ in DataLoader(dataset, batch_size=batch_size, shuffle=False):
            outputs.append(model(features.to(device)).cpu().numpy())
    return target_norm.inverse(np.concatenate(outputs, axis=0))


def _regression_metrics(
    actual: np.ndarray, predicted: np.ndarray, baseline: np.ndarray,
    gain_range: np.ndarray, layout: Sequence[str], mae_limit: float, p95_limit: float,
) -> dict:
    error = np.abs(predicted - actual)
    baseline_error = np.abs(actual - baseline)
    safe_range = np.maximum(np.abs(gain_range), 1e-12)
    mae = error.mean(axis=0)
    p95 = np.percentile(error, 95, axis=0)
    baseline_mae = baseline_error.mean(axis=0)
    mae_fraction, p95_fraction = mae / safe_range, p95 / safe_range
    model_score = float(mae_fraction.mean())
    baseline_score = float((baseline_mae / safe_range).mean())
    per_gain = {
        name: {
            "mae": float(mae[i]), "p95": float(p95[i]),
            "range": float(gain_range[i]), "mae_fraction": float(mae_fraction[i]),
            "p95_fraction": float(p95_fraction[i]),
            "baseline_mae": float(baseline_mae[i]),
            "passed": bool(mae_fraction[i] <= mae_limit and p95_fraction[i] <= p95_limit),
        }
        for i, name in enumerate(layout)
    }
    beats = model_score < baseline_score
    return {
        "samples": len(actual), "model_score": model_score,
        "constant_baseline_score": baseline_score, "beats_constant_baseline": beats,
        "passed": bool(beats and all(item["passed"] for item in per_gain.values())),
        "per_gain": per_gain,
    }


def _seed_everything(seed: int) -> None:
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def smoke_pretrain(env, scenarios, *, npgs=None, pretrain=None, max_steps: int = 200):
    """Временная совместимость PPO-тестов; production SFT этот live-capture не импортирует."""
    from ismpu.agent.gain_scheduler import NPGS, NPGSConfig
    from ismpu.agent.pretrain import PretrainConfig, pretrain_sft
    from ismpu.runtime.capture import capture_dataset

    net = npgs or NPGS(
        NPGSConfig(window=env.history_len, aircraft_profile=env.sim.aircraft_profile_name),
        gain_space=env.gain_space,
    )
    dataset, _ = capture_dataset(env, scenarios, max_steps=max_steps, log=None)
    history = pretrain_sft(
        net, dataset, pretrain or PretrainConfig(epochs=3, batch_size=64, device="cpu"))
    return net, dataset, history


def cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Offline SFT PID gain regressors")
    parser.add_argument("runs_root", nargs="?", default="runs")
    parser.add_argument("--segment", choices=("air", "ground", "both"), default="both")
    parser.add_argument("--checkpoint-dir", default="checkpoints")
    parser.add_argument("--epochs", type=int, default=40)
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args(argv)
    segments = ("air", "ground") if args.segment == "both" else (args.segment,)
    results = run_pretrain(PretrainRunConfig(
        runs_root=args.runs_root, checkpoint_dir=args.checkpoint_dir, segments=segments,
        train=SftTrainConfig(epochs=args.epochs, batch_size=args.batch_size, seed=args.seed),
    ))
    return 0 if all(result.metrics["gate_passed"] for result in results.values()) else 2


if __name__ == "__main__":
    raise SystemExit(cli())
