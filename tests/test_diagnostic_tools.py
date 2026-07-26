from dataclasses import replace

import pytest

from ismpu.envs.ics_sim import Telemetry
from ismpu.tools.authority_sweep import (
    SweepPulse,
    build_altitude_sweep,
    command_for_pulse,
    safety_reason,
    validate_pulse,
)
from ismpu.tools.prepare_stabilizer import (
    StabilizerPreparer,
    pulse_command,
    resolve_case,
)

from tests.fakes import airborne_inputs


def test_a31_a34_stabilizer_matrix_mapping():
    assert resolve_case("A.3.1").offset_deg == -2.0
    assert resolve_case("А.3.2").target_height_m == 300.0
    assert resolve_case("A.3.3").target_height_m == 60.0
    assert resolve_case("А.3.4").offset_deg == 2.0
    with pytest.raises(ValueError):
        resolve_case("A.3.5")


def test_stabilizer_pulse_is_bounded_and_has_expected_direction():
    assert pulse_command(0.0, 2.0) == 0.25
    assert pulse_command(0.0, -2.0) == -0.25
    assert pulse_command(1.95, 2.0) == 0.0
    with pytest.raises(ValueError):
        pulse_command(0.0, 2.0, magnitude_g=0.51)


def test_stabilizer_preparer_is_dry_run_by_default():
    class Sim:
        def read_telemetry(self):
            return Telemetry.from_ics(
                airborne_inputs(1000.0, StabilizerAngle=1.5))

        def step(self, command):
            raise AssertionError("dry-run must not send a command")

    plan = StabilizerPreparer(Sim()).prepare("A.3.1")
    assert plan["dry_run"] is True
    assert plan["baseline_deg"] == 1.5
    assert plan["target_deg"] == -0.5


def test_authority_sweep_is_safe_and_dry_run_friendly():
    pulses = build_altitude_sweep()
    assert len(pulses) == 8
    assert all(pulse.duration_s <= 0.25 for pulse in pulses)

    elevator = command_for_pulse(SweepPulse(450.0, "elevator", -0.5))
    aileron = command_for_pulse(SweepPulse(450.0, "aileron", 5.0))
    assert elevator.cmd_elevator == -0.5
    assert aileron.cmd_aileron == 5.0

    with pytest.raises(ValueError):
        validate_pulse(SweepPulse(450.0, "elevator", 0.6))
    with pytest.raises(ValueError):
        validate_pulse(SweepPulse(450.0, "elevator", 0.25, duration_s=0.3))


def test_authority_safety_gate_uses_finite_airborne_telemetry():
    safe = Telemetry.from_ics(airborne_inputs(600.0))
    assert safety_reason(safe) is None

    low = Telemetry.from_ics(airborne_inputs(99.0))
    assert safety_reason(low) == "below abort radio altitude"

    fast_raw = replace(airborne_inputs(600.0), IndicatedAirspeed=200.0)
    assert safety_reason(Telemetry.from_ics(fast_raw)) == "IAS outside safety interval"
