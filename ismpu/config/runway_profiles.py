"""Профили ВПП и разрешение ILS из установленной базы X-Plane."""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

from ismpu.config.runway import (
    ELEVATION_MSL, RWY_END_LAT, RWY_END_LON, RWY_HEADING_TRUE,
    RWY_START_LAT, RWY_START_LON,
)


@dataclass(frozen=True)
class ILSStation:
    airport: str
    runway: str
    frequency_hz: int
    ident: str
    latitude: float
    longitude: float


@dataclass(frozen=True)
class RunwayProfile:
    name: str
    airport: str
    runway: str
    threshold_lat: float
    threshold_lon: float
    end_lat: float
    end_lon: float
    heading_true_deg: float
    elevation_m: float
    width_m: float = 60.0

    @property
    def length_m(self) -> float:
        return _distance_m(
            self.threshold_lat, self.threshold_lon, self.end_lat, self.end_lon)

    def point_on_centerline(self, distance_before_threshold_m: float) -> tuple[float, float]:
        """Точка на продолжении оси; положительное расстояние — до порога."""
        return _destination(
            self.threshold_lat, self.threshold_lon,
            (self.heading_true_deg + 180.0) % 360.0,
            distance_before_threshold_m,
        )

    def discover_ils(self, xplane_root: str | Path) -> ILSStation:
        nav_path = find_earth_nav_dat(xplane_root)
        return parse_ils_station(nav_path, self.airport, self.runway)


UUEE_06R = RunwayProfile(
    name="uuee-06r",
    airport="UUEE",
    runway="06R",
    threshold_lat=RWY_START_LAT,
    threshold_lon=RWY_START_LON,
    end_lat=RWY_END_LAT,
    end_lon=RWY_END_LON,
    heading_true_deg=float(RWY_HEADING_TRUE),
    elevation_m=ELEVATION_MSL,
)

RUNWAY_PROFILES = {UUEE_06R.name: UUEE_06R}


def get_runway_profile(name: str) -> RunwayProfile:
    try:
        return RUNWAY_PROFILES[name.lower()]
    except KeyError as exc:
        known = ", ".join(sorted(RUNWAY_PROFILES))
        raise ValueError(f"неизвестный профиль ВПП {name!r}; доступен: {known}") from exc


def find_earth_nav_dat(xplane_root: str | Path) -> Path:
    root = Path(xplane_root)
    candidates = (
        root / "Custom Data" / "earth_nav.dat",
        root / "Resources" / "default data" / "earth_nav.dat",
    )
    for path in candidates:
        if path.is_file():
            return path
    raise FileNotFoundError(
        "earth_nav.dat не найден; проверены: " + ", ".join(str(p) for p in candidates))


def parse_ils_station(path: str | Path, airport: str, runway: str) -> ILSStation:
    """Найти LOC (тип 4) без хардкода частоты."""
    airport = airport.upper()
    runway = runway.upper()
    with Path(path).open("r", encoding="utf-8", errors="replace") as stream:
        for raw in stream:
            fields = raw.split()
            if len(fields) < 9 or fields[0] != "4":
                continue
            upper = [field.upper() for field in fields]
            if airport not in upper or runway not in upper:
                continue
            try:
                frequency_hz = int(fields[4]) * 10_000
                return ILSStation(
                    airport=airport,
                    runway=runway,
                    frequency_hz=frequency_hz,
                    ident=fields[7],
                    latitude=float(fields[1]),
                    longitude=float(fields[2]),
                )
            except (ValueError, IndexError) as exc:
                raise ValueError(f"повреждённая строка ILS в {path}: {raw.rstrip()}") from exc
    raise LookupError(f"ILS {airport} {runway} не найден в {path}")


def _distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6_371_000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * radius * math.asin(math.sqrt(a))


def _destination(lat: float, lon: float, bearing_deg: float, distance_m: float) -> tuple[float, float]:
    radius = 6_371_000.0
    angular = distance_m / radius
    bearing = math.radians(bearing_deg)
    p1 = math.radians(lat)
    l1 = math.radians(lon)
    p2 = math.asin(
        math.sin(p1) * math.cos(angular)
        + math.cos(p1) * math.sin(angular) * math.cos(bearing))
    l2 = l1 + math.atan2(
        math.sin(bearing) * math.sin(angular) * math.cos(p1),
        math.cos(angular) - math.sin(p1) * math.sin(p2))
    return math.degrees(p2), (math.degrees(l2) + 540.0) % 360.0 - 180.0
