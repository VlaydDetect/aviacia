"""Профили преобразования команд ИСМПУ в органы управления X-Plane."""

from __future__ import annotations

from dataclasses import dataclass

from ismpu.io import datarefs as dr


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


@dataclass(frozen=True)
class AircraftProfile:
    """DataRef, индексы и знаки конкретного планера."""

    name: str
    description: str
    engine_indices: tuple[int, int]
    gear_indices: tuple[int, int, int]  # nose, left main, right main
    flap_full_deg: float
    aileron_full_scale_deg: float
    elevator_full_scale_g: float
    roll_sign: float = 1.0
    pitch_sign: float = 1.0
    yaw_sign: float = 1.0

    @property
    def subscriptions(self) -> tuple[str, ...]:
        engine_refs = self.throttle_feedback_refs
        gear_refs = tuple(f"{dr.GEAR_ON_GROUND}[{i}]" for i in self.gear_indices)
        return (*dr.COMMON_SUBSCRIPTIONS, *engine_refs, *gear_refs)

    @property
    def throttle_refs(self) -> tuple[str, str]:
        """Command refs retained under the historical public name."""
        return self.throttle_command_refs

    @property
    def throttle_command_refs(self) -> tuple[str, str]:
        return tuple(f"{dr.THROTTLE_COMMAND}[{i}]" for i in self.engine_indices)

    @property
    def throttle_feedback_refs(self) -> tuple[str, str]:
        return tuple(f"{dr.THROTTLE_RATIO}[{i}]" for i in self.engine_indices)

    @property
    def gear_refs(self) -> tuple[str, str, str]:
        return tuple(f"{dr.GEAR_ON_GROUND}[{i}]" for i in self.gear_indices)

    def airborne_commands(self, command) -> dict[str, float]:
        left, right = self.throttle_command_refs
        return {
            dr.YOKE_ROLL_RATIO: clamp(
                self.roll_sign * command.cmd_aileron / self.aileron_full_scale_deg, -1.0, 1.0),
            dr.YOKE_PITCH_RATIO: clamp(
                self.pitch_sign * command.cmd_elevator / self.elevator_full_scale_g, -1.0, 1.0),
            dr.YOKE_HEADING_RATIO: clamp(self.yaw_sign * command.rudder_cmd, -1.0, 1.0),
            left: clamp(command.cmd_throttle_norm, 0.0, 1.0),
            right: clamp(command.cmd_throttle_norm, 0.0, 1.0),
        }

    def ground_commands(self, command) -> dict[str, float]:
        left, right = self.throttle_command_refs
        return {
            dr.LEFT_BRAKE_RATIO: clamp(command.cmd_brake_l, 0.0, 1.0),
            dr.RIGHT_BRAKE_RATIO: clamp(command.cmd_brake_r, 0.0, 1.0),
            left: clamp(command.cmd_rev_l, -1.0, 0.0),
            right: clamp(command.cmd_rev_r, -1.0, 0.0),
            dr.YOKE_HEADING_RATIO: clamp(self.yaw_sign * command.rudder_cmd, -1.0, 1.0),
        }


A330_300 = AircraftProfile(
    name="a330-300",
    description="Штатный Airbus A330-300 X-Plane 12",
    engine_indices=(0, 1),
    gear_indices=(0, 1, 2),
    flap_full_deg=40.0,
    aileron_full_scale_deg=25.0,
    elevator_full_scale_g=0.5,
    # Профиль намеренно помечается калибровочным на уровне пресета захода:
    # знаки здесь описывают только проводку штатного планера.
)

AIRCRAFT_PROFILES = {A330_300.name: A330_300}


def get_aircraft_profile(name: str) -> AircraftProfile:
    try:
        return AIRCRAFT_PROFILES[name.lower()]
    except KeyError as exc:
        known = ", ".join(sorted(AIRCRAFT_PROFILES))
        raise ValueError(f"неизвестный профиль ЛА {name!r}; доступен: {known}") from exc


def register_aircraft_profile(profile: AircraftProfile) -> None:
    """Расширение реестра будущим профилем МС-21 без правки XPlaneSim."""
    if profile.name in AIRCRAFT_PROFILES:
        raise ValueError(f"профиль {profile.name!r} уже зарегистрирован")
    AIRCRAFT_PROFILES[profile.name] = profile
