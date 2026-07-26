"""Строгий JSON schema v1 для переносимых конфигураций сценария."""

from __future__ import annotations

import json
import math
from dataclasses import asdict
from pathlib import Path
from typing import Any, Mapping

from ismpu.config.scenarios import ScenarioConfig
from ismpu.control.failures import FailureMode
from ismpu.control.trajectory import VelocityLaw
from ismpu.envs.scenario import (
    ApproachSetup, Scenario, SensorNoise, TouchdownSetup,
)
from ismpu.envs.weather import WeatherState

SCHEMA_VERSION = 1
_ROOT_KEYS = {
    "schema_version", "scenario_id", "seed", "control", "weather",
    "failures", "approach", "touchdown", "sensor_noise",
}
_CONTROL_KEYS = {
    "name", "failure", "pids", "guidance", "mixing", "trajectory",
    "draft", "approach", "matrix_code",
}
_PID_NAMES = ("runway_center", "brake_l", "brake_r", "rev_l", "rev_r")
_PID_KEYS = {
    "kp", "ki", "kd", "min_out", "max_out", "anti_windup",
    "integral_decay", "der_filter_tf", "name", "derivative_on_measurement",
    "conditional_anti_windup", "exact_discretization", "tracking_tau_s",
}


def _reject_unknown(data: Mapping[str, Any], allowed: set[str], where: str) -> None:
    unknown = set(data) - allowed
    if unknown:
        raise ValueError(f"{where}: неизвестные поля: {sorted(unknown)}")


def _finite_tree(value: Any, where: str = "config") -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError(f"{where}: число должно быть конечным")
    if isinstance(value, Mapping):
        for key, item in value.items():
            _finite_tree(item, f"{where}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _finite_tree(item, f"{where}[{index}]")


def control_to_dict(config: ScenarioConfig) -> dict[str, Any]:
    return {
        "name": config.name,
        "failure": config.failure.name,
        "pids": {name: dict(getattr(config, name)) for name in _PID_NAMES},
        "guidance": {
            "lookahead_min": config.lookahead_min,
            "lookahead_gain": config.lookahead_gain,
            "xte_gain": config.xte_gain,
        },
        "mixing": {
            "steering_brake_gain": config.steering_brake_gain,
            "steering_rev_gain": config.steering_rev_gain,
        },
        "trajectory": {"law": config.law.name},
        "draft": config.draft,
        "approach": config.approach,
        "matrix_code": config.matrix_code,
    }


def control_from_dict(data: Mapping[str, Any]) -> ScenarioConfig:
    _reject_unknown(data, _CONTROL_KEYS, "control")
    missing = {"name", "failure", "pids"} - set(data)
    if missing:
        raise ValueError(f"control: отсутствуют поля: {sorted(missing)}")
    pids = data["pids"]
    if not isinstance(pids, Mapping) or set(pids) != set(_PID_NAMES):
        raise ValueError(f"control.pids: требуются ровно {_PID_NAMES}")
    clean_pids: dict[str, dict[str, Any]] = {}
    for name in _PID_NAMES:
        spec = pids[name]
        if not isinstance(spec, Mapping):
            raise ValueError(f"control.pids.{name}: ожидается объект")
        _reject_unknown(spec, _PID_KEYS, f"control.pids.{name}")
        if not {"kp", "ki", "kd"} <= set(spec):
            raise ValueError(f"control.pids.{name}: обязательны kp/ki/kd")
        clean_pids[name] = dict(spec)
    guidance = dict(data.get("guidance", {}))
    mixing = dict(data.get("mixing", {}))
    trajectory = dict(data.get("trajectory", {}))
    result = ScenarioConfig(
        name=str(data["name"]),
        failure=FailureMode[str(data["failure"])],
        runway_center=clean_pids["runway_center"],
        brake_l=clean_pids["brake_l"],
        brake_r=clean_pids["brake_r"],
        rev_l=clean_pids["rev_l"],
        rev_r=clean_pids["rev_r"],
        lookahead_min=float(guidance.get("lookahead_min", 10.0)),
        lookahead_gain=float(guidance.get("lookahead_gain", 1.8)),
        xte_gain=float(guidance.get("xte_gain", 2.0)),
        steering_brake_gain=float(mixing.get("steering_brake_gain", 0.4)),
        steering_rev_gain=float(mixing.get("steering_rev_gain", 0.0)),
        law=VelocityLaw[str(trajectory.get("law", "GAUSS_BELL"))],
        draft=bool(data.get("draft", False)),
        approach=str(data.get("approach", "default")),
        matrix_code=str(data.get("matrix_code", "")),
    )
    _finite_tree(control_to_dict(result), "control")
    return result


def scenario_to_document(scenario: Scenario) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "scenario_id": scenario.scenario_id,
        "seed": scenario.seed,
        "control": control_to_dict(scenario.control),
        "weather": scenario.weather.to_dict(),
        "failures": [failure.name for failure in scenario.failures],
        "approach": asdict(scenario.approach),
        "touchdown": asdict(scenario.touchdown),
        "sensor_noise": asdict(scenario.sensor_noise),
    }


def scenario_from_document(data: Mapping[str, Any]) -> Scenario:
    _reject_unknown(data, _ROOT_KEYS, "root")
    if data.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(
            f"schema_version должен быть {SCHEMA_VERSION}, получено "
            f"{data.get('schema_version')!r}")
    missing = {"scenario_id", "seed", "control", "weather"} - set(data)
    if missing:
        raise ValueError(f"root: отсутствуют поля: {sorted(missing)}")
    _finite_tree(data)
    return Scenario(
        scenario_id=str(data["scenario_id"]),
        seed=int(data["seed"]),
        control=control_from_dict(data["control"]),
        weather=WeatherState.from_dict(dict(data["weather"])),
        failures=tuple(
            FailureMode[str(name)] for name in data.get("failures", ())),
        approach=ApproachSetup(**dict(data.get("approach", {}))),
        touchdown=TouchdownSetup(**dict(data.get("touchdown", {}))),
        sensor_noise=SensorNoise(**dict(data.get("sensor_noise", {}))),
    )


def load_scenario(path: str | Path) -> Scenario:
    with Path(path).open("r", encoding="utf-8") as stream:
        return scenario_from_document(json.load(stream))


def dump_scenario(scenario: Scenario, path: str | Path) -> Path:
    target = Path(path)
    target.write_text(
        json.dumps(
            scenario_to_document(scenario),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        ) + "\n",
        encoding="utf-8",
    )
    return target
