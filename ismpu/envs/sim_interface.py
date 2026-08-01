"""Общий контракт симулятора и воздушных сигналов.

ICS и X-Plane различаются транспортом и возможностями reset, но контур управления
не должен знать, откуда пришёл кадр. ``ApproachData`` сохраняет размерные единицы
воздушного закона (узлы, футы, фут/мин, градусы), потому что его коэффициенты
идентифицированы именно в этих единицах.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Literal, Mapping, Protocol, runtime_checkable

if TYPE_CHECKING:
    from ismpu.control.channels import ControlsState
    from ismpu.control.failures import FailureMode
    from ismpu.envs.ics_sim import Telemetry
    from ismpu.envs.scenario import Scenario

StartMode = Literal["approach", "rollout"]


@dataclass(frozen=True)
class ShutdownReport:
    """Результат безусловного best-effort отключения backend."""

    backend: str
    actions: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()

    @property
    def successful(self) -> bool:
        return not self.errors


class RunStopReason(str, Enum):
    COMPLETED = "completed"
    GO_AROUND = "go_around"
    ENGAGEMENT_LOST = "engagement_lost"
    INTERRUPTED = "interrupted"
    ERROR = "error"


@dataclass(frozen=True)
class RunResult:
    reason: RunStopReason
    shutdown: ShutdownReport | None = None
    details: str | None = None


@dataclass(frozen=True)
class XPlaneDiagnostics:
    ready: bool = False
    ignored_failures: tuple[str, ...] = ()
    missing_or_stale_datarefs: tuple[str, ...] = ()
    last_flight_time: float | None = None


@dataclass(frozen=True)
class ControlDiagnostics:
    segment: str
    guidance: Mapping[str, float | None] | None = None
    values: Mapping[str, Any] = field(default_factory=dict)


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
    # X-Plane does not model these bench flags yet; zero means "fault absent".
    FaultLeftStab: int = 0
    FaultRightStab: int = 0


@runtime_checkable
class SimInterface(Protocol):
    """Минимальный lifecycle, одинаковый для стенда и X-Plane."""

    backend_name: str
    aircraft_profile_name: str

    @property
    def engaged(self) -> bool: ...

    @property
    def active_failures(self) -> frozenset["FailureMode"]: ...

    def reset(
        self,
        scenario: "Scenario | None" = None,
        *,
        start: StartMode | None = None,
    ) -> "Telemetry": ...

    def warm_up(self, timeout_s: float = 10.0, dt: float = 0.05) -> bool: ...

    def read_telemetry(self) -> "Telemetry": ...

    def step(self, command: "ControlsState") -> "Telemetry": ...

    def request_rollout(self) -> None: ...

    def request_taxi(self) -> bool: ...

    def deactivate(self, frames: int = 10, dt: float = 0.05) -> None: ...

    def shutdown(self, frames: int = 10, dt: float = 0.05) -> ShutdownReport: ...

    def close(self) -> None: ...

    def __enter__(self) -> "SimInterface": ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: object | None,
    ) -> bool: ...
