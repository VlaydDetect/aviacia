"""Параметры установки ЛА в сценарий касания."""

from ismpu.config.constants import INITIAL_SPEED_KTS

A330_SETUP = dict(
    speed_knots=INITIAL_SPEED_KTS,
    descent_rate_fpm=200.0,
    pitch_deg=0.0,
)
