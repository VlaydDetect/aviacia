"""Совместимый путь импорта единой модели сценариев.

Каноническая модель и реестр находятся в :mod:`ismpu.config.scenarios`. В этом модуле нет
второго класса или производного реестра.
"""

from ismpu.config.scenarios import (
    AircraftControlSet,
    ApproachSetup,
    CONTROL_PROFILES,
    ConditionMatch,
    ControlProfile,
    GroundControlConfig,
    ProfileStatus,
    Scenario,
    SegmentConditions,
    SensorNoise,
    TouchdownSetup,
    compose_scenario,
    compose_matrix_scenario,
    match_conditions,
    matrix_battery,
    resolve_scenario,
    scenario_distance,
    scenario_for_matrix_run,
    select_for_telemetry,
    select_scenario,
    weather_distance,
)

__all__ = (
    "AircraftControlSet", "ApproachSetup", "CONTROL_PROFILES", "ConditionMatch", "ControlProfile",
    "GroundControlConfig", "ProfileStatus",
    "Scenario", "SegmentConditions", "SensorNoise", "TouchdownSetup", "compose_scenario",
    "compose_matrix_scenario",
    "match_conditions", "matrix_battery", "resolve_scenario", "scenario_distance",
    "scenario_for_matrix_run",
    "select_for_telemetry", "select_scenario", "weather_distance",
)
