"""Безопасные elevator/altitude authority sweep без дублирования ICS runner."""

from __future__ import annotations

import math
from dataclasses import dataclass

from ismpu.control.channels import ControlsState

MAX_ELEVATOR_STEP_G = 0.5
MAX_AILERON_STEP_DEG = 5.0
MAX_PULSE_SECONDS = 0.25
MIN_ACTIVATION_RA_FT = 500.0
MIN_ABORT_RA_FT = 100.0


@dataclass(frozen=True)
class SweepPulse:
    target_radio_altitude_ft: float
    axis: str
    command: float
    duration_s: float = 0.25
    recovery_s: float = 0.75


@dataclass(frozen=True)
class SweepLimits:
    abort_radio_altitude_ft: float = MIN_ABORT_RA_FT
    min_ias_kt: float = 120.0
    max_ias_kt: float = 190.0
    max_abs_pitch_deg: float = 15.0
    max_abs_roll_deg: float = 15.0
    min_vertical_speed_fpm: float = -2000.0


def validate_pulse(pulse: SweepPulse, limits: SweepLimits = SweepLimits()) -> None:
    if pulse.axis not in {"elevator", "aileron"}:
        raise ValueError("axis должен быть elevator или aileron")
    if not math.isfinite(pulse.command):
        raise ValueError("команда должна быть конечной")
    maximum = MAX_ELEVATOR_STEP_G if pulse.axis == "elevator" else MAX_AILERON_STEP_DEG
    if not 0.0 < abs(pulse.command) <= maximum:
        raise ValueError(f"|{pulse.axis}| должен быть в (0, {maximum:g}]")
    if not 0.0 < pulse.duration_s <= MAX_PULSE_SECONDS:
        raise ValueError(f"pulse duration должен быть <= {MAX_PULSE_SECONDS:g} с")
    if pulse.target_radio_altitude_ft <= limits.abort_radio_altitude_ft:
        raise ValueError("высота импульса должна быть выше abort height")


def safety_reason(telemetry, limits: SweepLimits = SweepLimits()) -> str | None:
    source = getattr(telemetry, "approach_inputs", None)
    if source is None or not telemetry.valid:
        return "airborne telemetry unavailable"
    checks = (
        source.RadioAltitude, source.IndicatedAirspeed, source.PitchAngle,
        source.RollAngle, source.VerticalSpeed,
    )
    if not all(math.isfinite(value) for value in checks):
        return "non-finite telemetry"
    if source.RadioAltitude <= limits.abort_radio_altitude_ft:
        return "below abort radio altitude"
    if not limits.min_ias_kt <= source.IndicatedAirspeed <= limits.max_ias_kt:
        return "IAS outside safety interval"
    if abs(source.PitchAngle) > limits.max_abs_pitch_deg:
        return "pitch outside safety interval"
    if abs(source.RollAngle) > limits.max_abs_roll_deg:
        return "roll outside safety interval"
    if source.VerticalSpeed < limits.min_vertical_speed_fpm:
        return "vertical speed below safety limit"
    return None


def build_altitude_sweep(
    altitudes_ft=(450.0, 350.0, 250.0, 150.0),
    *,
    elevator_step_g: float = 0.5,
    aileron_step_deg: float = 5.0,
    duration_s: float = 0.25,
) -> tuple[SweepPulse, ...]:
    pulses = []
    for index, altitude in enumerate(altitudes_ft):
        pulses.extend((
            SweepPulse(altitude, "elevator", elevator_step_g, duration_s),
            SweepPulse(altitude, "aileron",
                       aileron_step_deg if index % 2 == 0 else -aileron_step_deg,
                       duration_s),
        ))
    for pulse in pulses:
        validate_pulse(pulse)
    return tuple(pulses)


def command_for_pulse(pulse: SweepPulse) -> ControlsState:
    """Чистое преобразование, пригодное и для dry-run, и для ICSSim."""
    validate_pulse(pulse)
    state = ControlsState()
    if pulse.axis == "elevator":
        state.cmd_elevator = pulse.command
    else:
        state.cmd_aileron = pulse.command
    return state
