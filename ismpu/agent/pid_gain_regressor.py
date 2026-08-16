"""Минимальная SFT-модель абсолютных коэффициентов PID и общий runtime guard."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from os import PathLike
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
from numpy.typing import ArrayLike, NDArray
import torch
import torch.nn as nn


CHECKPOINT_VERSION = 1
DEFAULT_WINDOW_FRAMES = 40
DEFAULT_FREQUENCY_HZ = 20.0


def feature_schema_hash(names: Sequence[str]) -> str:
    """Стабильный hash порядка признаков; перестановка является сменой контракта."""
    payload = json.dumps(
        list(names), ensure_ascii=False, separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True)
class Normalization:
    """Покомпонентная standardization и границы обучающей выборки."""

    mean: NDArray[np.float64]
    scale: NDArray[np.float64]
    minimum: NDArray[np.float64]
    maximum: NDArray[np.float64]

    @classmethod
    def fit(cls, values: ArrayLike) -> "Normalization":
        data = np.asarray(values, dtype=np.float64)
        if data.ndim != 2 or not len(data):
            raise ValueError("normalization requires a non-empty 2-D array")
        if not np.isfinite(data).all():
            raise ValueError("normalization data must be finite")
        scale = data.std(axis=0)
        scale[scale < 1e-12] = 1.0
        return cls(data.mean(axis=0), scale, data.min(axis=0), data.max(axis=0))

    @classmethod
    def from_snapshot(cls, value: Mapping[str, Any]) -> "Normalization":
        result = cls(*(np.asarray(value[key], dtype=np.float64)
                       for key in ("mean", "scale", "minimum", "maximum")))
        size = len(result.mean)
        if not size or any(item.shape != (size,) for item in (
            result.scale, result.minimum, result.maximum,
        )):
            raise ValueError("invalid normalization dimensions")
        if (not all(np.isfinite(item).all() for item in (
                result.mean, result.scale, result.minimum, result.maximum))
                or np.any(result.scale <= 0.0)):
            raise ValueError("invalid normalization values")
        return result

    def transform(
        self, values: ArrayLike, *, ood_z: float = 8.0,
    ) -> tuple[NDArray[np.float32], bool]:
        data = np.asarray(values, dtype=np.float64)
        if data.shape[-1:] != self.mean.shape:
            raise ValueError(
                f"normalization expects {len(self.mean)} values, got {data.shape}")
        if not np.isfinite(data).all():
            raise ValueError("features must be finite")
        normalized = (data - self.mean) / self.scale
        return normalized.astype(np.float32), bool(np.any(np.abs(normalized) > ood_z))

    def inverse(self, values: ArrayLike) -> NDArray[np.float64]:
        data = np.asarray(values, dtype=np.float64)
        if data.shape[-1:] != self.mean.shape:
            raise ValueError(
                f"normalization expects {len(self.mean)} values, got {data.shape}")
        return data * self.scale + self.mean

    def snapshot(self) -> dict[str, list[float]]:
        return {
            "mean": self.mean.tolist(), "scale": self.scale.tolist(),
            "minimum": self.minimum.tolist(), "maximum": self.maximum.tolist(),
        }


class PidGainRegressor(nn.Module):
    """``LayerNorm → GRU(1) → Linear``; выход — только абсолютные PID gains."""

    def __init__(self, input_dim: int, output_dim: int, hidden_size: int = 64) -> None:
        super().__init__()
        if input_dim <= 0 or output_dim <= 0 or hidden_size <= 0:
            raise ValueError("model dimensions must be positive")
        self.input_dim = int(input_dim)
        self.output_dim = int(output_dim)
        self.hidden_size = int(hidden_size)
        self.input_norm = nn.LayerNorm(self.input_dim)
        self.gru = nn.GRU(
            self.input_dim, self.hidden_size, num_layers=1, batch_first=True)
        self.output = nn.Linear(self.hidden_size, self.output_dim)
        self.checkpoint: dict[str, Any] | None = None

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        single = features.ndim == 2
        if single:
            features = features.unsqueeze(0)
        if features.ndim != 3 or features.shape[-1] != self.input_dim:
            raise ValueError(
                f"expected (B,T,{self.input_dim}) or (T,{self.input_dim}), "
                f"got {tuple(features.shape)}")
        sequence, _ = self.gru(self.input_norm(features))
        result = self.output(sequence[:, -1])
        return result.squeeze(0) if single else result

    @torch.no_grad()
    def predict(
        self,
        window: ArrayLike,
        feature_normalization: Normalization,
        target_normalization: Normalization,
    ) -> tuple[NDArray[np.float64], bool]:
        normalized, ood = feature_normalization.transform(window)
        device = next(self.parameters()).device
        output = self(torch.as_tensor(normalized, dtype=torch.float32, device=device))
        gains = target_normalization.inverse(output.detach().cpu().numpy())
        return gains.reshape(-1), ood

    def save_checkpoint(
        self, path: str | PathLike[str], metadata: Mapping[str, Any],
    ) -> None:
        """Сохранить веса вместе с полным train↔runtime контрактом."""
        payload = dict(metadata)
        payload.update({
            "checkpoint_version": CHECKPOINT_VERSION,
            "model_type": type(self).__name__,
            "model": {
                "input_dim": self.input_dim, "output_dim": self.output_dim,
                "hidden_size": self.hidden_size,
            },
            "state_dict": self.state_dict(),
        })
        _validate_checkpoint(payload)
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        torch.save(payload, target)

    @classmethod
    def load_checkpoint(
        cls,
        path: str | PathLike[str],
        *,
        map_location: str | torch.device = "cpu",
        expected_segment: str | None = None,
        expected_features: Sequence[str] | None = None,
        expected_gain_layout: Sequence[str] | None = None,
        expected_matrix_hash: str | None = None,
        expected_aircraft_profile: str | None = None,
        require_gate: bool = True,
        require_ics_activation: bool = False,
    ) -> tuple["PidGainRegressor", dict[str, Any]]:
        payload = torch.load(path, map_location=map_location, weights_only=False)
        _validate_checkpoint(payload)
        if expected_segment is not None and payload["segment"] != expected_segment:
            raise ValueError(
                f"checkpoint segment {payload['segment']!r} != {expected_segment!r}")
        if expected_features is not None and tuple(payload["feature_schema"]) != tuple(expected_features):
            raise ValueError("checkpoint feature schema does not match runtime")
        if expected_gain_layout is not None and tuple(payload["gain_layout"]) != tuple(expected_gain_layout):
            raise ValueError("checkpoint gain layout does not match runtime")
        if expected_matrix_hash is not None and payload["matrix_hash"] != expected_matrix_hash:
            raise ValueError("checkpoint run-matrix hash does not match runtime")
        if (expected_aircraft_profile is not None
                and payload["aircraft_profile"] != expected_aircraft_profile):
            raise ValueError("checkpoint aircraft profile does not match runtime")
        if require_gate and payload["metrics"].get("gate_passed") is not True:
            raise ValueError("checkpoint did not pass the SFT regression gate")
        if require_ics_activation:
            evidence = payload.get("activation", {})
            missing = [name for name in ("replay", "xplane", "shadow", "no_degradation")
                       if evidence.get(name) is not True]
            if missing:
                raise PermissionError(
                    "ICS sft-active requires replay/X-Plane/shadow evidence: "
                    + ", ".join(missing))
        config = payload["model"]
        model = cls(**config)
        model.load_state_dict(payload["state_dict"])
        model.checkpoint = payload
        model.eval()
        return model, payload

    @classmethod
    def load(cls, path: str | PathLike[str], **kwargs) -> "PidGainRegressor":
        return cls.load_checkpoint(path, **kwargs)[0]


def _validate_checkpoint(payload: Mapping[str, Any]) -> None:
    required = {
        "checkpoint_version", "model_type", "model", "state_dict", "segment",
        "window_frames", "frequency_hz", "feature_schema", "feature_schema_hash",
        "gain_layout", "normalization", "physical_bounds", "matrix_hash",
        "aircraft_profile", "run_ids", "split_run_ids", "metrics",
    }
    missing = sorted(required - set(payload))
    if missing:
        raise ValueError(f"checkpoint misses fields: {', '.join(missing)}")
    if payload["checkpoint_version"] != CHECKPOINT_VERSION:
        raise ValueError("unsupported SFT checkpoint version")
    if payload["model_type"] != "PidGainRegressor":
        raise ValueError("checkpoint contains another model type")
    features = tuple(payload["feature_schema"])
    gains = tuple(payload["gain_layout"])
    config = payload["model"]
    if payload["feature_schema_hash"] != feature_schema_hash(features):
        raise ValueError("checkpoint feature schema hash is invalid")
    if config.get("input_dim") != len(features) or config.get("output_dim") != len(gains):
        raise ValueError("checkpoint model dimensions violate schema/layout")
    if payload["segment"] not in {"air", "ground"}:
        raise ValueError("checkpoint segment must be 'air' or 'ground'")
    if len(gains) != {"air": 9, "ground": 15}[payload["segment"]]:
        raise ValueError("checkpoint has the wrong number of PID gains")
    if any(name.rpartition(":")[2] not in {"kp", "ki", "kd"} for name in gains):
        raise ValueError("checkpoint gain layout contains a non-PID output")
    if any(name.endswith(("_kp", "_ki", "_kd")) for name in features):
        raise ValueError("checkpoint leaks current gains into model features")
    if int(payload["window_frames"]) <= 0 or not math.isfinite(float(payload["frequency_hz"])):
        raise ValueError("invalid inference timing contract")
    Normalization.from_snapshot(payload["normalization"]["features"])
    Normalization.from_snapshot(payload["normalization"]["targets"])
    bounds = payload["physical_bounds"]
    low = np.asarray(bounds["low"], dtype=np.float64)
    high = np.asarray(bounds["high"], dtype=np.float64)
    if low.shape != (len(gains),) or high.shape != low.shape:
        raise ValueError("invalid physical gain bounds")
    if not np.isfinite(low).all() or not np.isfinite(high).all() or np.any(low > high):
        raise ValueError("invalid physical gain bounds")
    if not payload["matrix_hash"] or not payload["aircraft_profile"] or not payload["run_ids"]:
        raise ValueError("checkpoint must identify its matrix and source runs")


@dataclass(frozen=True)
class GuardResult:
    gains: NDArray[np.float64]
    fallback: bool
    rate_limited: bool
    reason: str | None = None


class GainGuard:
    """Проверяет prediction и ограничивает скорость изменения до записи в PID."""

    def __init__(
        self,
        physical_low: ArrayLike,
        physical_high: ArrayLike,
        *,
        relative_low: float = 0.3,
        relative_high: float = 2.5,
        rate_fraction_per_s: float = 0.25,
    ) -> None:
        self.physical_low = np.asarray(physical_low, dtype=np.float64).reshape(-1)
        self.physical_high = np.asarray(physical_high, dtype=np.float64).reshape(-1)
        if (self.physical_low.shape != self.physical_high.shape
                or not np.isfinite(self.physical_low).all()
                or not np.isfinite(self.physical_high).all()
                or np.any(self.physical_low > self.physical_high)):
            raise ValueError("invalid physical gain bounds")
        if not (0.0 <= relative_low <= relative_high) or rate_fraction_per_s < 0.0:
            raise ValueError("invalid GainGuard limits")
        self.relative_low = float(relative_low)
        self.relative_high = float(relative_high)
        self.rate_fraction_per_s = float(rate_fraction_per_s)

    def guard(
        self,
        prediction: ArrayLike | None,
        preset: ArrayLike,
        previous: ArrayLike,
        dt: float,
        *,
        window_ready: bool = True,
        telemetry_valid: bool = True,
        ood: bool = False,
        model_error: str | None = None,
    ) -> GuardResult:
        preset_vec = np.asarray(preset, dtype=np.float64).reshape(-1)
        previous_vec = np.asarray(previous, dtype=np.float64).reshape(-1)
        shape = self.physical_low.shape
        if preset_vec.shape != shape or not np.isfinite(preset_vec).all():
            raise ValueError("accepted preset violates GainGuard contract")

        def fallback(reason: str) -> GuardResult:
            return GuardResult(preset_vec.copy(), True, False, reason)

        if not telemetry_valid:
            return fallback("telemetry_dropout")
        if not window_ready:
            return fallback("window_incomplete")
        if model_error is not None:
            return fallback(f"model_error:{model_error}")
        if ood:
            return fallback("feature_ood")
        if prediction is None:
            return fallback("prediction_missing")
        candidate = np.asarray(prediction, dtype=np.float64).reshape(-1)
        if candidate.shape != shape or not np.isfinite(candidate).all():
            return fallback("prediction_nonfinite_or_wrong_shape")
        if previous_vec.shape != shape or not np.isfinite(previous_vec).all():
            return fallback("previous_gains_invalid")
        if not math.isfinite(dt) or dt <= 0.0:
            return fallback("invalid_dt")

        relative_a = preset_vec * self.relative_low
        relative_b = preset_vec * self.relative_high
        low = np.maximum(self.physical_low, np.minimum(relative_a, relative_b))
        high = np.minimum(self.physical_high, np.maximum(relative_a, relative_b))
        if np.any(low > high) or np.any(candidate < low) or np.any(candidate > high):
            return fallback("gain_bounds")

        max_step = np.abs(preset_vec) * self.rate_fraction_per_s * dt
        limited = np.clip(candidate, previous_vec - max_step, previous_vec + max_step)
        limited = np.clip(limited, low, high)
        was_limited = not np.array_equal(limited, candidate)
        return GuardResult(limited, False, was_limited, "rate_limited" if was_limited else None)

    apply = guard
