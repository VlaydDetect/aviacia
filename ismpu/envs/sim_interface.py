"""Общий контракт симулятора и воздушных сигналов.

ICS и X-Plane различаются транспортом и возможностями reset, но контур управления
не должен знать, откуда пришёл кадр. ``ApproachData`` сохраняет размерные единицы
воздушного закона (узлы, футы, фут/мин, градусы), потому что его коэффициенты
идентифицированы именно в этих единицах.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable


@dataclass
class ApproachData:
    """Backend-независимый срез сигналов для захода и ухода на второй круг."""

    RadioAltitude: float = 0.0
    IndicatedAirspeed: float = 0.0
    TrueAirspeed: float = 0.0
    GroundSpeed: float = 0.0
    VerticalSpeed: float = 0.0
    PitchAngle: float = 0.0
    RollAngle: float = 0.0
    TrkAngleMagnetic: float = 0.0
    MagneticHeading: float = 0.0
    RunwayHeading: float = 0.0
    LocDeviation: float = 0.0
    GSDeviation: float = 0.0
    FlapsAngle: float = 0.0
    LeftThrottleAngle: float = 0.0
    RightThrottleAngle: float = 0.0
    BodyPitchRate: float = 0.0
    BodyRollRate: float = 0.0
    BodyYawRate: float = 0.0
    BodyNormAccel: float = 0.0
    AirfieldTemp: float = 15.0


@runtime_checkable
class SimInterface(Protocol):
    """Минимальный lifecycle, одинаковый для стенда и X-Plane."""

    backend_name: str
    aircraft_profile_name: str

    @property
    def engaged(self) -> bool: ...

    @property
    def active_failures(self) -> set: ...

    def reset(self, scenario: Any = None, *, start: str | None = None): ...

    def warm_up(self, timeout_s: float = 10.0, dt: float = 0.05) -> bool: ...

    def read_telemetry(self): ...

    def step(self, command): ...

    def request_rollout(self) -> None: ...

    def request_taxi(self) -> bool: ...

    def deactivate(self, frames: int = 10, dt: float = 0.05) -> None: ...

    def close(self) -> None: ...
