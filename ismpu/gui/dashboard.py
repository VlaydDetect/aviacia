"""Canonical local PID dashboard; implementation lives beside this stable import path."""

from ismpu.gui.dashboard_core import (
    AIR_PID_KEYS,
    GROUND_PID_KEYS,
    DashboardServer,
    DashboardSnapshot,
    DashboardState,
    GainChange,
    VIEW_SPECS,
    ViewSpec,
    main,
)

__all__ = (
    "AIR_PID_KEYS",
    "GROUND_PID_KEYS",
    "DashboardServer",
    "DashboardSnapshot",
    "DashboardState",
    "GainChange",
    "VIEW_SPECS",
    "ViewSpec",
    "main",
)

if __name__ == "__main__":
    main()
