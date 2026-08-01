"""Профильное пространство абсолютных PID-коэффициентов NPGS."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

import numpy as np
from numpy.typing import ArrayLike, NDArray

from ismpu.config.aircraft_profiles import AircraftProfile
from ismpu.config.regulators import (
    GAIN_KEYS,
    N_GAINS,
    REGULATOR_ORDER,
    GainKey,
    GainMap,
    RegulatorKey,
)
from ismpu.config.scenarios import GroundControlConfig, SCENARIOS, Scenario
from ismpu.config.segments import FlightSegment

EXPAND = 2.0
_EPS = 1e-6
_REG_TO_FIELD: Mapping[RegulatorKey, str] = {
    "runway_center_pid": "runway_center",
    "pid_brake_l": "brake_l",
    "pid_brake_r": "brake_r",
    "pid_rev_l": "rev_l",
    "pid_rev_r": "rev_r",
}


def _profile_name(profile: AircraftProfile | str) -> str:
    return profile.name if isinstance(profile, AircraftProfile) else str(profile).lower()


def _regulator_config(
    config: GroundControlConfig, regulator: RegulatorKey,
) -> dict[str, Any]:
    try:
        return getattr(config, _REG_TO_FIELD[regulator])
    except KeyError as exc:
        raise ValueError(f"неизвестный регулятор: {regulator}") from exc


@dataclass(frozen=True)
class GainSpace:
    """Замороженная таблица gain'ов одного AircraftProfile."""

    aircraft_profile: str
    slots: tuple[tuple[RegulatorKey, GainKey], ...]
    ref: NDArray[np.float64]
    s: NDArray[np.float64]
    lo: NDArray[np.float64]
    hi: NDArray[np.float64]
    default: NDArray[np.float64]

    @classmethod
    def build(
        cls,
        aircraft_profile: AircraftProfile | str,
        scenarios: Mapping[str, Scenario] = SCENARIOS,
    ) -> "GainSpace":
        profile = _profile_name(aircraft_profile)
        configs = [
            scenario.control_for(profile, FlightSegment.ROLLOUT)
            for scenario in scenarios.values()
            if profile in scenario.aircraft_controls
        ]
        if not configs:
            raise ValueError(f"нет rollout PID для профиля {profile!r}")
        default_cfg = scenarios["default"].control_for(profile, FlightSegment.ROLLOUT)
        slots = tuple((reg, key) for reg in REGULATOR_ORDER for key in GAIN_KEYS)
        ref = np.empty(N_GAINS, dtype=np.float64)
        width = np.empty(N_GAINS, dtype=np.float64)
        lo = np.empty(N_GAINS, dtype=np.float64)
        hi = np.empty(N_GAINS, dtype=np.float64)
        default = np.empty(N_GAINS, dtype=np.float64)
        for index, (regulator, key) in enumerate(slots):
            values = [
                float(_regulator_config(config, regulator)[key])
                for config in configs
                if float(_regulator_config(config, regulator).get(key, 0.0)) > 0.0
            ]
            if not values:
                raise ValueError(f"нет положительных значений {regulator}:{key}")
            vmin, vmax = min(values), max(values)
            lo[index] = vmin / EXPAND
            hi[index] = vmax * EXPAND
            ref[index] = math.sqrt(vmin * vmax)
            width[index] = math.log(EXPAND * math.sqrt(vmax / vmin))
            default[index] = float(_regulator_config(default_cfg, regulator)[key])
        return cls(profile, slots, ref, width, lo, hi, default)

    def _by_reg(self, values: Sequence[float]) -> GainMap:
        return {
            regulator: {
                key: float(values[self.slots.index((regulator, key))])
                for key in GAIN_KEYS
            }
            for regulator in REGULATOR_ORDER
        }

    @property
    def ref_map(self) -> GainMap:
        return self._by_reg(self.ref)

    @property
    def s_map(self) -> GainMap:
        return self._by_reg(self.s)

    @property
    def lo_map(self) -> GainMap:
        return self._by_reg(self.lo)

    @property
    def hi_map(self) -> GainMap:
        return self._by_reg(self.hi)

    @property
    def default_map(self) -> GainMap:
        return self._by_reg(self.default)

    def gain_norm_scalar(self, value: float, reg: RegulatorKey, key: GainKey) -> float:
        ratio = math.log(max(float(value), 1e-12) / self.ref_map[reg][key]) / self.s_map[reg][key]
        return -1.0 if ratio < -1.0 else 1.0 if ratio > 1.0 else ratio

    def to_gain(self, z: ArrayLike) -> NDArray[np.float64]:
        return self.ref * np.exp(self.s * np.tanh(np.asarray(z, dtype=np.float64)))

    def inv_gain(self, gain: ArrayLike) -> NDArray[np.float64]:
        values = np.maximum(np.asarray(gain, dtype=np.float64), 1e-12)
        ratio = np.log(values / self.ref) / self.s
        return np.arctanh(np.clip(ratio, -1.0 + _EPS, 1.0 - _EPS))

    def gain_norm(self, gain: ArrayLike) -> NDArray[np.float64]:
        values = np.asarray(gain, dtype=np.float64)
        ratio = np.log(np.maximum(values, 1e-12) / self.ref) / self.s
        return np.clip(ratio, -1.0, 1.0)

    def default_bias(self) -> NDArray[np.float64]:
        return self.inv_gain(self.default)

    def slot_index(self, reg: RegulatorKey, key: GainKey) -> int:
        return self.slots.index((reg, key))

    def snapshot(self) -> dict[str, Any]:
        return {
            "aircraft_profile": self.aircraft_profile,
            "slots": [f"{reg}:{key}" for reg, key in self.slots],
            "ref": self.ref.tolist(), "s": self.s.tolist(),
            "lo": self.lo.tolist(), "hi": self.hi.tolist(),
            "default": self.default.tolist(), "expand": EXPAND,
        }

    def compatible_with(self, snapshot: Mapping[str, Any]) -> bool:
        if snapshot.get("aircraft_profile") != self.aircraft_profile:
            return False
        current = self.snapshot()
        return all(
            current[key] == snapshot.get(key)
            for key in ("slots", "ref", "s", "lo", "hi", "default", "expand")
        )


@lru_cache(maxsize=None)
def gain_space_for(aircraft_profile: str) -> GainSpace:
    return GainSpace.build(aircraft_profile)
