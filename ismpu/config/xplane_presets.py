"""Отдельные пресеты A330 для X-Plane.

Они намеренно не являются псевдонимами стендовых объектов: настройка одного ЛА
не должна незаметно менять коэффициенты другого. Воздушный набор остаётся
черновым до живого приёмочного прогона X-Plane.
"""

from dataclasses import replace

from ismpu.config.approach import APPROACH_DEFAULT
from ismpu.config.scenarios import SCENARIOS, ScenarioConfig


def _copy_ground(config: ScenarioConfig) -> ScenarioConfig:
    return replace(
        config,
        runway_center=dict(config.runway_center),
        brake_l=dict(config.brake_l),
        brake_r=dict(config.brake_r),
        rev_l=dict(config.rev_l),
        rev_r=dict(config.rev_r),
    )


XPLANE_A330_GROUND_PRESETS = {
    name: _copy_ground(config) for name, config in SCENARIOS.items()
}

XPLANE_A330_APPROACH = replace(
    APPROACH_DEFAULT,
    name="xplane_a330_approach",
    draft=True,
    roll_pid=dict(APPROACH_DEFAULT.roll_pid),
    pitch_pid=dict(APPROACH_DEFAULT.pitch_pid),
    speed_pid=dict(APPROACH_DEFAULT.speed_pid),
)


def xplane_ground_preset(name: str) -> ScenarioConfig:
    try:
        return XPLANE_A330_GROUND_PRESETS[name]
    except KeyError as exc:
        raise KeyError(f"нет X-Plane A330-пресета {name!r}") from exc
