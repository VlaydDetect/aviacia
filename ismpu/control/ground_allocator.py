"""Детерминированное распределение наземного yaw-запроса по органам управления."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ismpu.config.segments import FlightSegment
from ismpu.control.failures import FailureState

if TYPE_CHECKING:
    from ismpu.control.channels import ControlsState, LateralDiagnostics, LongitudinalDiagnostics
    from ismpu.envs.ics_sim import Telemetry


@dataclass(frozen=True)
class ActuatorVector:
    """Нормированные наземные команды в явных физических каналах."""

    rudder: float = 0.0
    pedal: float = 0.0
    tiller: float = 0.0
    brake_left: float = 0.0
    brake_right: float = 0.0
    reverse_left: float = 0.0
    reverse_right: float = 0.0


@dataclass(frozen=True)
class ActuatorFeedback:
    """Измеренные положения/усилия стенда в исходных единицах ICS."""

    rudder_deg: float | None = None
    nose_wheel_deg: float | None = None
    brake_left_mm: float | None = None
    brake_right_mm: float | None = None
    throttle_left_deg: float | None = None
    throttle_right_deg: float | None = None
    thrust_left: float | None = None
    thrust_right: float | None = None
    longitudinal_accel_g: float | None = None
    lateral_accel_g: float | None = None
    yaw_rate_rad_s: float | None = None


@dataclass(frozen=True)
class AllocationDiagnostics:
    """Полная трасса allocator: база + добавка → запрос → ограниченная команда."""

    base: ActuatorVector
    lateral: ActuatorVector
    requested: ActuatorVector
    limited: ActuatorVector
    feedback: ActuatorFeedback
    steering_request: float
    steering_applied: float
    failure_compensation: float
    saturated: tuple[str, ...]


def _clamp(value: float, lower: float, upper: float) -> float:
    return min(upper, max(lower, value))


class GroundControlAllocator:
    """Единственное место, где смешиваются каналы и учитывается доступность органов."""

    def __init__(
        self,
        *,
        steering_brake_gain: float,
        steering_rev_gain: float,
        steering_rate_per_s: float = 1.0,
        brake_rate_per_s: float = 1.0,
        reverse_rate_per_s: float = 1.0,
        failure_yaw_compensation_gain: float = 1.0,
    ) -> None:
        self.steering_brake_gain = steering_brake_gain
        self.steering_rev_gain = steering_rev_gain
        self.steering_rate_per_s = steering_rate_per_s
        self.brake_rate_per_s = brake_rate_per_s
        self.reverse_rate_per_s = reverse_rate_per_s
        self.failure_yaw_compensation_gain = failure_yaw_compensation_gain
        self.last_diagnostics: AllocationDiagnostics | None = None

    def allocate(
        self,
        segment: FlightSegment,
        longitudinal: "LongitudinalDiagnostics",
        lateral: "LateralDiagnostics",
        failures: FailureState,
        previous: "ControlsState",
        telemetry: "Telemetry",
        dt: float,
        *,
        ground_contact_available: bool = True,
    ) -> AllocationDiagnostics:
        rollout = segment is FlightSegment.ROLLOUT
        control_available = longitudinal.valid and telemetry.valid and ground_contact_available
        guidance_available = lateral.valid
        reverse_available = rollout and longitudinal.reverse_allowed
        steering = lateral.steering_limited if lateral.valid else 0.0

        base = ActuatorVector(
            brake_left=longitudinal.base_brake_left,
            brake_right=longitudinal.base_brake_right,
            reverse_left=longitudinal.base_reverse_left if reverse_available else 0.0,
            reverse_right=longitudinal.base_reverse_right if reverse_available else 0.0,
        )

        nominal_lateral = self._lateral_vector(
            steering, rollout=rollout, reverse_available=reverse_available)

        # После исключения неисправного реверса симметричная продольная база становится yaw-
        # возмущением. Переводим его в противоположный запрос и отдаём доступным рулю/тормозам.
        effective_base_reverse_left = (
            base.reverse_left * failures.reverse_left_eff * failures.thrust_left_eff)
        effective_base_reverse_right = (
            base.reverse_right * failures.reverse_right_eff * failures.thrust_right_eff)
        failure_compensation = (
            -self.failure_yaw_compensation_gain * (
                effective_base_reverse_left - effective_base_reverse_right)
        )
        compensation = self._lateral_vector(
            failure_compensation, rollout=rollout, reverse_available=False)
        lateral_vector = self._add(nominal_lateral, compensation)
        combined = self._add(base, lateral_vector)

        requested = ActuatorVector(
            rudder=combined.rudder if rollout else 0.0,
            pedal=(combined.pedal * failures.steering_eff if rollout else 0.0),
            tiller=(combined.tiller * failures.steering_eff if not rollout else 0.0),
            brake_left=combined.brake_left * failures.brake_left_eff,
            brake_right=combined.brake_right * failures.brake_right_eff,
            reverse_left=(
                combined.reverse_left * failures.reverse_left_eff * failures.thrust_left_eff
                if reverse_available else 0.0),
            reverse_right=(
                combined.reverse_right * failures.reverse_right_eff * failures.thrust_right_eff
                if reverse_available else 0.0),
        )

        dt_limited = _clamp(dt, 0.001, 0.25)
        # Потеря guidance означает немедленно убрать асимметричную добавку, а не продолжать
        # несколько кадров прошлый поворот из-за slew limiter. Симметричная speed-база остаётся.
        steering_rate = self.steering_rate_per_s if guidance_available else float("inf")
        brake_rate = self.brake_rate_per_s if guidance_available else float("inf")
        reverse_rate = self.reverse_rate_per_s if guidance_available else float("inf")
        limited = ActuatorVector(
            rudder=self._limit(requested.rudder, previous.cmd_rudder,
                               steering_rate, dt_limited,
                               control_available and guidance_available and rollout),
            pedal=self._limit(requested.pedal, previous.cmd_pedal,
                              steering_rate, dt_limited,
                              control_available and guidance_available and rollout
                              and failures.steering_eff > 0.0),
            tiller=self._limit(requested.tiller, previous.cmd_tiller,
                              steering_rate, dt_limited,
                              control_available and guidance_available and not rollout
                              and failures.steering_eff > 0.0),
            brake_left=self._limit(requested.brake_left, previous.cmd_brake_l,
                                   brake_rate, dt_limited,
                                   control_available and failures.brake_left_eff > 0.0,
                                   0.0, 1.0),
            brake_right=self._limit(requested.brake_right, previous.cmd_brake_r,
                                    brake_rate, dt_limited,
                                    control_available and failures.brake_right_eff > 0.0,
                                    0.0, 1.0),
            reverse_left=self._limit(requested.reverse_left, previous.cmd_rev_l,
                                     reverse_rate, dt_limited,
                                     control_available and reverse_available
                                     and failures.reverse_left_eff > 0.0
                                     and failures.thrust_left_eff > 0.0, -1.0, 0.0),
            reverse_right=self._limit(requested.reverse_right, previous.cmd_rev_r,
                                      reverse_rate, dt_limited,
                                      control_available and reverse_available
                                      and failures.reverse_right_eff > 0.0
                                      and failures.thrust_right_eff > 0.0, -1.0, 0.0),
        )
        saturated = tuple(
            name for name in ActuatorVector.__dataclass_fields__
            if abs(getattr(requested, name) - getattr(limited, name)) > 1e-12
        )
        if rollout:
            steering_applied = limited.rudder
        elif failures.steering_eff > 0.0:
            steering_applied = limited.tiller
        elif self.steering_brake_gain != 0.0:
            base_difference = (
                base.brake_right * failures.brake_right_eff
                - base.brake_left * failures.brake_left_eff
            )
            steering_applied = (
                limited.brake_right - limited.brake_left - base_difference
            ) / (2.0 * self.steering_brake_gain)
        else:
            steering_applied = 0.0
        diagnostics = AllocationDiagnostics(
            base=base,
            lateral=lateral_vector,
            requested=requested,
            limited=limited,
            feedback=self._feedback(telemetry),
            steering_request=steering,
            steering_applied=steering_applied,
            failure_compensation=failure_compensation,
            saturated=saturated,
        )
        self.last_diagnostics = diagnostics
        return diagnostics

    def _lateral_vector(
        self, steering: float, *, rollout: bool, reverse_available: bool,
    ) -> ActuatorVector:
        brake = steering * self.steering_brake_gain
        reverse = steering * self.steering_rev_gain if reverse_available else 0.0
        return ActuatorVector(
            rudder=steering if rollout else 0.0,
            pedal=steering if rollout else 0.0,
            tiller=steering if not rollout else 0.0,
            brake_left=-brake,
            brake_right=brake,
            reverse_left=reverse,
            reverse_right=-reverse,
        )

    @staticmethod
    def _add(left: ActuatorVector, right: ActuatorVector) -> ActuatorVector:
        return ActuatorVector(**{
            name: getattr(left, name) + getattr(right, name)
            for name in ActuatorVector.__dataclass_fields__
        })

    @staticmethod
    def _limit(
        requested: float,
        previous: float,
        rate_per_s: float,
        dt: float,
        available: bool,
        lower: float = -1.0,
        upper: float = 1.0,
    ) -> float:
        if not available:
            return 0.0
        delta = max(0.0, rate_per_s) * dt
        return _clamp(_clamp(requested, previous - delta, previous + delta), lower, upper)

    @staticmethod
    def _feedback(telemetry: "Telemetry") -> ActuatorFeedback:
        raw = telemetry.ics_inputs
        return ActuatorFeedback(
            rudder_deg=getattr(raw, "RudderAngle", None),
            nose_wheel_deg=getattr(raw, "NoseWheelAngle", None),
            brake_left_mm=getattr(raw, "LeftBrakePedal", None),
            brake_right_mm=getattr(raw, "RightBrakePedal", None),
            throttle_left_deg=getattr(raw, "LeftThrottleAngle", None),
            throttle_right_deg=getattr(raw, "RightThrottleAngle", None),
            thrust_left=getattr(raw, "EngLeftThrust", None),
            thrust_right=getattr(raw, "EngRigntThrust", None),
            longitudinal_accel_g=telemetry.accel_long_g,
            lateral_accel_g=telemetry.accel_side_g,
            yaw_rate_rad_s=telemetry.r_rad,
        )
