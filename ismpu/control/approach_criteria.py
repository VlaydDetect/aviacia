"""Отдельный монитор критерия А.1.1 (не участвует в go-around)."""

from __future__ import annotations

import math
from dataclasses import dataclass


def angular_error_deg(reference_deg: float, actual_deg: float) -> float:
    return (actual_deg - reference_deg + 180.0) % 360.0 - 180.0


@dataclass(frozen=True)
class ApproachCriteriaConfig:
    cutoff_radio_altitude_ft: float = 300.0
    max_course_error_deg: float = 0.7
    max_glideslope_error_deg: float = 0.5
    target_glideslope_deg: float = 3.0


@dataclass(frozen=True)
class ApproachCriteriaSample:
    course_error_deg: float | None
    glideslope_error_deg: float | None
    status: str


@dataclass(frozen=True)
class ApproachCriteriaVerdict:
    status: str
    sample_count: int
    start_radio_altitude_ft: float | None
    end_radio_altitude_ft: float | None
    max_course_error_deg: float | None
    max_glideslope_error_deg: float | None
    reasons: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return self.status == "PASS"


class ApproachCriteriaMonitor:
    """Захватывает А.1.1 после входа в допуск и завершает оценку на 300 ft."""

    def __init__(self, config: ApproachCriteriaConfig | None = None) -> None:
        self.config = config or ApproachCriteriaConfig()
        self.sample_count = 0
        self.start_radio_altitude_ft = None
        self.end_radio_altitude_ft = None
        self.max_course_error_deg = 0.0
        self.max_glideslope_error_deg = 0.0
        self.invalid_reasons: set[str] = set()
        self.cutoff_reached = False

    def observe(self, telemetry, flight_path_angle_deg: float) -> ApproachCriteriaSample:
        if self.cutoff_reached:
            return ApproachCriteriaSample(None, None, "COMPLETE")
        state = getattr(telemetry, "approach_inputs", None)
        if state is None or not getattr(telemetry, "valid", False):
            self.invalid_reasons.add("airborne telemetry unavailable")
            return ApproachCriteriaSample(None, None, "INVALID")
        ra = state.RadioAltitude
        if not math.isfinite(ra):
            self.invalid_reasons.add("radio altitude is non-finite")
            return ApproachCriteriaSample(None, None, "INVALID")
        if ra <= self.config.cutoff_radio_altitude_ft:
            self.cutoff_reached = True
            self.end_radio_altitude_ft = ra
            return ApproachCriteriaSample(None, None, "COMPLETE")
        if self.start_radio_altitude_ft is None:
            self.start_radio_altitude_ft = ra
        self.end_radio_altitude_ft = ra

        values = {
            "runway heading non-finite": state.RunwayHeading,
            "magnetic track non-finite": state.TrkAngleMagnetic,
            "flight-path angle non-finite": flight_path_angle_deg,
        }
        missing = [name for name, value in values.items() if not math.isfinite(value)]
        if missing:
            self.invalid_reasons.update(missing)
            return ApproachCriteriaSample(None, None, "INVALID")

        course = abs(angular_error_deg(state.RunwayHeading, state.TrkAngleMagnetic))
        glide = abs(flight_path_angle_deg + self.config.target_glideslope_deg)
        if self.sample_count == 0 and (
            course > self.config.max_course_error_deg
            or glide > self.config.max_glideslope_error_deg
        ):
            return ApproachCriteriaSample(course, glide, "WAITING_CAPTURE")

        self.sample_count += 1
        self.max_course_error_deg = max(self.max_course_error_deg, course)
        self.max_glideslope_error_deg = max(self.max_glideslope_error_deg, glide)
        status = "OK" if (
            course <= self.config.max_course_error_deg
            and glide <= self.config.max_glideslope_error_deg
        ) else "LIMIT"
        return ApproachCriteriaSample(course, glide, status)

    def verdict(self) -> ApproachCriteriaVerdict:
        reasons = sorted(self.invalid_reasons)
        if not self.cutoff_reached:
            status = "INCOMPLETE"
            reasons.append(f"{self.config.cutoff_radio_altitude_ft:g}-ft cutoff was not reached")
        elif self.sample_count == 0:
            status = "FAIL"
            reasons.append("criteria were not captured above the cutoff")
        else:
            if self.max_course_error_deg > self.config.max_course_error_deg:
                reasons.append("course limit exceeded")
            if self.max_glideslope_error_deg > self.config.max_glideslope_error_deg:
                reasons.append("glideslope limit exceeded")
            status = "PASS" if not reasons else "FAIL"
        return ApproachCriteriaVerdict(
            status=status,
            sample_count=self.sample_count,
            start_radio_altitude_ft=self.start_radio_altitude_ft,
            end_radio_altitude_ft=self.end_radio_altitude_ft,
            max_course_error_deg=self.max_course_error_deg if self.sample_count else None,
            max_glideslope_error_deg=(
                self.max_glideslope_error_deg if self.sample_count else None),
            reasons=tuple(reasons),
        )
