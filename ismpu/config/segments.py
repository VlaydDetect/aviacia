"""Канонические участки управляемого интервала полёта."""

from enum import Enum


class FlightSegment(str, Enum):
    """Участок, для которого выбираются закон управления и условия сценария."""

    APPROACH = "approach"
    ROLLOUT = "rollout"
    TAXI = "taxi"
