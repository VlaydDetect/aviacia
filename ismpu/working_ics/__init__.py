"""Exact package port of the ICS approach contour validated in ``aviacia_v2``.

The numerical controller and wire protocol intentionally live together here so
future refactors of the generic simulator backend cannot silently change the
known-good live flight path.
"""

from .pid_controller import ClearWeatherILSController, ControllerConfig, ControlResult
from .protocol import ICSInputs, ICSOutputs

__all__ = [
    "ClearWeatherILSController",
    "ControllerConfig",
    "ControlResult",
    "ICSInputs",
    "ICSOutputs",
]
