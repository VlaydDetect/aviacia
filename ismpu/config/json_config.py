"""Строгая переносимая JSON-схема профильного сценария (v2) и чтение legacy v1."""

from __future__ import annotations

import json
import math
from dataclasses import asdict, fields, replace
from pathlib import Path
from typing import Any, Mapping

from ismpu.config.approach import (
    APPROACH_CONFIGS,
    ICS_CLEAR_WEATHER_APPROACH,
    ApproachConfig,
)
from ismpu.config.scenarios import (
    AircraftControlSet,
    ApproachSetup,
    GroundControlConfig,
    SCENARIOS,
    Scenario,
    SegmentConditions,
    SensorNoise,
    TouchdownSetup,
)
from ismpu.config.segments import FlightSegment
from ismpu.control.failures import FailureMode
from ismpu.control.trajectory import VelocityLaw
from ismpu.envs.weather import WeatherState

SCHEMA_VERSION = 2
_ROOT_KEYS_V2 = {
    "schema_version", "scenario_id", "seed", "aircraft_controls", "conditions",
    "approach", "touchdown", "sensor_noise", "matrix_codes", "provenance",
}
_ROOT_KEYS_V1 = {
    "schema_version", "scenario_id", "seed", "control", "weather",
    "failures", "approach", "touchdown", "sensor_noise",
}
_PID_NAMES = ("runway_center", "brake_l", "brake_r", "rev_l", "rev_r")


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


def ground_control_to_dict(config: GroundControlConfig) -> dict[str, Any]:
    return {
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
    }


def ground_control_from_dict(data: Mapping[str, Any]) -> GroundControlConfig:
    pids = data.get("pids")
    if not isinstance(pids, Mapping) or set(pids) != set(_PID_NAMES):
        raise ValueError(f"ground.pids: требуются ровно {_PID_NAMES}")
    guidance = dict(data.get("guidance", {}))
    mixing = dict(data.get("mixing", {}))
    trajectory = dict(data.get("trajectory", {}))
    return GroundControlConfig(
        **{name: dict(pids[name]) for name in _PID_NAMES},
        lookahead_min=float(guidance.get("lookahead_min", 10.0)),
        lookahead_gain=float(guidance.get("lookahead_gain", 1.8)),
        xte_gain=float(guidance.get("xte_gain", 2.0)),
        steering_brake_gain=float(mixing.get("steering_brake_gain", 0.4)),
        steering_rev_gain=float(mixing.get("steering_rev_gain", 0.0)),
        law=VelocityLaw[str(trajectory.get("law", "GAUSS_BELL"))],
    )


def approach_control_to_dict(config: ApproachConfig) -> dict[str, Any]:
    return asdict(config)


def approach_control_from_dict(data: Mapping[str, Any]) -> ApproachConfig:
    allowed = {field.name for field in fields(ApproachConfig)}
    _reject_unknown(data, allowed, "approach_control")
    return ApproachConfig(**dict(data))


def scenario_to_document(scenario: Scenario) -> dict[str, Any]:
    document = {
        "schema_version": SCHEMA_VERSION,
        "scenario_id": scenario.scenario_id,
        "seed": scenario.seed,
        "aircraft_controls": {
            profile: {
                "approach": approach_control_to_dict(controls.approach),
                "rollout": ground_control_to_dict(controls.rollout),
                "taxi": ground_control_to_dict(controls.taxi),
                "draft_segments": sorted(segment.value for segment in controls.draft_segments),
            }
            for profile, controls in scenario.aircraft_controls.items()
        },
        "conditions": {
            segment.value: {
                "weather": conditions.weather.to_dict(),
                "failures": [failure.name for failure in sorted(
                    conditions.failures, key=lambda item: item.value)],
            }
            for segment, conditions in scenario.conditions.items()
        },
        "approach": asdict(scenario.approach),
        "touchdown": asdict(scenario.touchdown),
        "sensor_noise": asdict(scenario.sensor_noise),
        "matrix_codes": {segment.value: code for segment, code in scenario.matrix_codes.items()},
        "provenance": {segment.value: source for segment, source in scenario.provenance.items()},
    }
    _finite_tree(document)
    return document


def _scenario_from_v2(data: Mapping[str, Any]) -> Scenario:
    _reject_unknown(data, _ROOT_KEYS_V2, "root")
    missing = {"scenario_id", "seed", "aircraft_controls", "conditions"} - set(data)
    if missing:
        raise ValueError(f"root: отсутствуют поля: {sorted(missing)}")
    controls: dict[str, AircraftControlSet] = {}
    for profile, raw in dict(data["aircraft_controls"]).items():
        raw = dict(raw)
        controls[str(profile).lower()] = AircraftControlSet(
            approach=approach_control_from_dict(dict(raw["approach"])),
            rollout=ground_control_from_dict(dict(raw["rollout"])),
            taxi=ground_control_from_dict(dict(raw["taxi"])),
            draft_segments=frozenset(
                FlightSegment(value) for value in raw.get("draft_segments", ())),
        )
    raw_conditions = dict(data["conditions"])
    conditions = {
        segment: SegmentConditions(
            weather=WeatherState.from_dict(dict(raw_conditions[segment.value]["weather"])),
            failures=frozenset(
                FailureMode[name] for name in raw_conditions[segment.value].get("failures", ())),
        )
        for segment in FlightSegment
    }
    return Scenario(
        scenario_id=str(data["scenario_id"]),
        seed=int(data["seed"]),
        aircraft_controls=controls,
        conditions=conditions,
        approach=ApproachSetup(**dict(data.get("approach", {}))),
        touchdown=TouchdownSetup(**dict(data.get("touchdown", {}))),
        sensor_noise=SensorNoise(**dict(data.get("sensor_noise", {}))),
        matrix_codes={
            FlightSegment(key): str(value)
            for key, value in dict(data.get("matrix_codes", {})).items()
        },
        provenance={
            FlightSegment(key): str(value)
            for key, value in dict(data.get("provenance", {})).items()
        },
    )


def _legacy_ground(
    data: Mapping[str, Any],
) -> tuple[str, GroundControlConfig, bool, str, str]:
    """Старый `control` v1 → имя, ground, draft, approach key и матричный шифр."""
    pids = data["pids"]
    ground = ground_control_from_dict({
        "pids": pids,
        "guidance": data.get("guidance", {}),
        "mixing": data.get("mixing", {}),
        "trajectory": data.get("trajectory", {}),
    })
    return (
        str(data.get("name", "legacy")), ground, bool(data.get("draft", False)),
        str(data.get("approach", "default")),
        str(data.get("matrix_code", "")),
    )


def _copy_approach(config: ApproachConfig, *, name: str | None = None) -> ApproachConfig:
    return replace(
        config,
        name=name or config.name,
        roll_pid=dict(config.roll_pid),
        pitch_pid=dict(config.pitch_pid),
        speed_pid=dict(config.speed_pid),
    )


def _legacy_matrix_segments(code: str) -> tuple[FlightSegment, ...]:
    normalized = code.strip().upper().replace("A", "А").replace("B", "Б")
    if normalized.startswith("А."):
        return (FlightSegment.APPROACH,)
    if normalized == "Б.1.2":
        return (FlightSegment.TAXI,)
    if normalized.startswith("Б.4."):
        return (FlightSegment.APPROACH, FlightSegment.ROLLOUT)
    return (FlightSegment.ROLLOUT,)


def _scenario_from_v1(
    data: Mapping[str, Any], legacy_aircraft_profile: str,
) -> Scenario:
    _reject_unknown(data, _ROOT_KEYS_V1, "root")
    missing = {"scenario_id", "seed", "control", "weather"} - set(data)
    if missing:
        raise ValueError(f"root: отсутствуют поля: {sorted(missing)}")
    raw_control = dict(data["control"])
    name, ground, draft, approach_key, matrix_code = _legacy_ground(raw_control)
    profile = legacy_aircraft_profile.lower()
    try:
        profile_default = SCENARIOS["default"].aircraft_controls[profile]
    except KeyError as exc:
        raise ValueError(f"неизвестный legacy_aircraft_profile {profile!r}") from exc
    if profile == "mc21":
        configured = (
            ICS_CLEAR_WEATHER_APPROACH
            if approach_key == "default"
            else APPROACH_CONFIGS.get(approach_key)
        )
        approach = _copy_approach(
            configured or profile_default.approach,
            name=approach_key if configured is None else configured.name,
        )
        if configured is None:
            approach = replace(approach, draft=True)
    else:
        # v1 never serialized the A330 airborne coefficients; retain the existing
        # profile draft instead of pretending the MC-21 law is calibrated for it.
        approach = _copy_approach(profile_default.approach)
    affected = _legacy_matrix_segments(matrix_code) if matrix_code else (
        FlightSegment.ROLLOUT, FlightSegment.TAXI)
    draft_segments = set(affected if draft else ())
    if approach.draft:
        draft_segments.add(FlightSegment.APPROACH)
    controls = AircraftControlSet(
        approach=approach,
        rollout=ground,
        taxi=replace(ground),
        draft_segments=frozenset(draft_segments),
    )
    weather = WeatherState.from_dict(dict(data["weather"]))
    raw_failures = data.get("failures")
    if raw_failures is None:
        legacy_failure = str(raw_control.get("failure", "NONE"))
        raw_failures = () if legacy_failure == "NONE" else (legacy_failure,)
    failures = frozenset(FailureMode[item] for item in raw_failures)
    conditions = {
        segment: SegmentConditions(weather=weather, failures=failures)
        for segment in FlightSegment
    }
    return Scenario(
        scenario_id=str(data["scenario_id"]),
        seed=int(data["seed"]),
        aircraft_controls={profile: controls},
        conditions=conditions,
        approach=ApproachSetup(**dict(data.get("approach", {}))),
        touchdown=TouchdownSetup(**dict(data.get("touchdown", {}))),
        sensor_noise=SensorNoise(**dict(data.get("sensor_noise", {}))),
        matrix_codes={segment: matrix_code for segment in affected if matrix_code},
        provenance={segment: name for segment in FlightSegment},
    )


def scenario_from_document(
    data: Mapping[str, Any], *, legacy_aircraft_profile: str = "mc21",
) -> Scenario:
    _finite_tree(data)
    version = data.get("schema_version")
    if version == SCHEMA_VERSION:
        return _scenario_from_v2(data)
    if version == 1:
        return _scenario_from_v1(data, legacy_aircraft_profile)
    raise ValueError(f"schema_version должна быть 1 или {SCHEMA_VERSION}, получено {version!r}")


def load_scenario(
    path: str | Path, *, legacy_aircraft_profile: str = "mc21",
) -> Scenario:
    with Path(path).open("r", encoding="utf-8") as stream:
        return scenario_from_document(
            json.load(stream), legacy_aircraft_profile=legacy_aircraft_profile)


def dump_scenario(scenario: Scenario, path: str | Path) -> Path:
    target = Path(path)
    target.write_text(
        json.dumps(
            scenario_to_document(scenario), ensure_ascii=False, indent=2,
            sort_keys=True, allow_nan=False,
        ) + "\n",
        encoding="utf-8",
    )
    return target
