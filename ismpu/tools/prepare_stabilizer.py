"""Подготовка случаев А.3.1–А.3.4 через текущий ICSSim."""

from __future__ import annotations

import math
import time
from dataclasses import dataclass

from ismpu.config.constants import DT
from ismpu.control.channels import ControlsState
from ismpu.tools.authority_sweep import SweepLimits, safety_reason


@dataclass(frozen=True)
class StabilizerCase:
    matrix_code: str
    offset_deg: float
    target_height_m: float


STABILIZER_CASES = {
    "А.3.1": StabilizerCase("А.3.1", -2.0, 300.0),
    "А.3.2": StabilizerCase("А.3.2", +2.0, 300.0),
    "А.3.3": StabilizerCase("А.3.3", -2.0, 60.0),
    "А.3.4": StabilizerCase("А.3.4", +2.0, 60.0),
}


def resolve_case(code: str) -> StabilizerCase:
    normalized = code.strip().upper().replace("A", "А")
    try:
        return STABILIZER_CASES[normalized]
    except KeyError as exc:
        raise ValueError(f"неизвестный случай стабилизатора {code!r}") from exc


def pulse_command(current_deg: float, target_deg: float, *,
                  tolerance_deg: float = 0.1, magnitude_g: float = 0.25) -> float:
    if not all(math.isfinite(value) for value in (current_deg, target_deg)):
        raise ValueError("углы стабилизатора должны быть конечными")
    if not 0.0 < magnitude_g <= 0.5:
        raise ValueError("импульс руля высоты должен быть в (0, 0.5] g")
    error = target_deg - current_deg
    return 0.0 if abs(error) <= tolerance_deg else math.copysign(magnitude_g, error)


class StabilizerPreparer:
    """Dry-run по умолчанию; реальная выдача требует ``send=True``."""

    def __init__(self, sim, *, send: bool = False, pulse_g: float = 0.25,
                 pulse_seconds: float = 0.25, settle_seconds: float = 0.75,
                 tolerance_deg: float = 0.1, limits: SweepLimits = SweepLimits()) -> None:
        if pulse_seconds > 0.25:
            raise ValueError("pulse_seconds не должен превышать 0.25 с")
        self.sim = sim
        self.send = send
        self.pulse_g = pulse_g
        self.pulse_seconds = pulse_seconds
        self.settle_seconds = settle_seconds
        self.tolerance_deg = tolerance_deg
        self.limits = limits

    def prepare(self, code: str, *, max_pulses: int = 30) -> dict:
        case = resolve_case(code)
        telemetry = self.sim.read_telemetry()
        raw = getattr(telemetry, "ics_inputs", None)
        if raw is None:
            raise RuntimeError("подготовка стабилизатора доступна только на ICS")
        violation = safety_reason(telemetry, self.limits)
        if violation:
            raise RuntimeError(f"safety check: {violation}")
        baseline = float(raw.StabilizerAngle)
        target = baseline + case.offset_deg
        plan = {
            "matrix_code": case.matrix_code,
            "baseline_deg": baseline,
            "target_deg": target,
            "offset_deg": case.offset_deg,
            "target_height_m": case.target_height_m,
            "dry_run": not self.send,
        }
        if not self.send:
            return plan

        self.sim.warm_up()
        for _ in range(max_pulses):
            telemetry = self.sim.read_telemetry()
            violation = safety_reason(telemetry, self.limits)
            if violation:
                raise RuntimeError(f"safety abort: {violation}")
            current = float(telemetry.ics_inputs.StabilizerAngle)
            elevator = pulse_command(
                current, target, tolerance_deg=self.tolerance_deg,
                magnitude_g=self.pulse_g)
            if elevator == 0.0:
                plan["final_deg"] = current
                return plan
            command = ControlsState(cmd_elevator=elevator)
            frames = max(1, math.ceil(self.pulse_seconds / DT))
            for frame in range(frames):
                self.sim.step(command)
                if frame + 1 < frames:
                    time.sleep(DT)
            self.sim.step(ControlsState())
            time.sleep(self.settle_seconds)
        raise TimeoutError("стабилизатор не достиг целевого положения")
