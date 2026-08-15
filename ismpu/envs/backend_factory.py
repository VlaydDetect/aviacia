"""Единая фабрика backend: ICS по умолчанию, X-Plane явно."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ismpu.config.aircraft_profiles import get_aircraft_profile
from ismpu.config.runway_profiles import get_runway_profile
from ismpu.io.ics_connector import LISTEN_IP_ANY
from ismpu.envs.sim_interface import SimInterface


def build_sim(
    backend: str = "ics",
    *,
    ip: str | None = None,
    port: int | None = None,
    xplane_root: str | Path | None = None,
    aircraft_profile: str | None = None,
    runway_profile: str | None = None,
    **kwargs: Any,
) -> SimInterface:
    """Создать backend; для ICS геодезия включается только явным ``runway_profile``."""
    kind = backend.lower()
    if kind == "ics":
        from ismpu.envs.ics_sim import ICSSim
        if aircraft_profile is None:
            raise ValueError("для backend='ics' требуется aircraft_profile")
        return ICSSim(
            listen_ip=ip or LISTEN_IP_ANY,
            listen_port=port or 3030,
            aircraft_profile=get_aircraft_profile(aircraft_profile),
            runway_profile=(
                get_runway_profile(runway_profile) if runway_profile is not None else None),
            **kwargs,
        )
    if kind == "xplane":
        from ismpu.envs.xplane_sim import XPlaneSim
        return XPlaneSim(
            ip=ip or "127.0.0.1",
            port=port or 49000,
            xplane_root=xplane_root,
            aircraft_profile=get_aircraft_profile(aircraft_profile or "a330-300"),
            runway_profile=get_runway_profile(runway_profile or "uuee-06r"),
            **kwargs,
        )
    raise ValueError("backend должен быть 'ics' или 'xplane'")
