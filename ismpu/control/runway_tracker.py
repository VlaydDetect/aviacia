"""Слежение за осью ВПП: геодезия, cross-track error, guidance с look-ahead.

Сферическая модель Земли (haversine, bearing, прямая геодезическая задача).
Guidance формирует Stanley-подобную ошибку курса по точке упреждения
(look-ahead), масштабируемой скоростью. Прямое стендовое и геодезическое наведение возвращают
одинаковое разложение ошибок; геометрия по умолчанию импортируется из config.runway.
"""

from dataclasses import dataclass
from collections.abc import Iterator, Mapping
from typing import TYPE_CHECKING
import numpy as np

from ismpu.config.runway import (
    RWY_START_LAT, RWY_START_LON, RWY_END_LAT, RWY_END_LON, RWY_HEADING_TRUE,
)

if TYPE_CHECKING:
    from ismpu.config.runway_profiles import RunwayProfile


@dataclass(frozen=True)
class GuidanceState(Mapping[str, float | str | None]):
    xte: float
    along_track: float | None
    lookahead: float
    course_error_deg: float
    heading_error_deg: float
    guidance_error_deg: float
    desired_heading_deg: float
    source: str

    @property
    def along(self) -> float | None:
        """Совместимость с прежним атрибутом; новый термин явно указывает ось."""
        return self.along_track

    def __getitem__(self, key: str) -> float | str | None:
        """Совместимость со старым словарным API."""
        values = {
            "xte": self.xte,
            "along": self.along_track,
            "along_track": self.along_track,
            "lookahead": self.lookahead,
            "course_error_deg": self.course_error_deg,
            "heading_error_deg": self.heading_error_deg,
            "guidance_error_deg": self.guidance_error_deg,
            "desired_heading_deg": self.desired_heading_deg,
            "source": self.source,
        }
        return values[key]

    def __iter__(self) -> Iterator[str]:
        return iter((
            "xte", "along_track", "lookahead", "course_error_deg",
            "heading_error_deg", "guidance_error_deg", "desired_heading_deg", "source",
        ))

    def __len__(self) -> int:
        return 8


class RunwayTracker:
    """Геодезическое наведение на ось ВПП с упреждением по скорости."""

    def __init__(
        self,
        lookahead_min: float = 15.0,
        lookahead_gain: float = 1.5,
        xte_gain: float = 1.0,
        runway_profile: "RunwayProfile | None" = None,
    ) -> None:
        self.R: float = 6371008.7714  # средний радиус Земли, м

        self.start_lat = runway_profile.threshold_lat if runway_profile else RWY_START_LAT
        self.start_lon = runway_profile.threshold_lon if runway_profile else RWY_START_LON
        self.end_lat = runway_profile.end_lat if runway_profile else RWY_END_LAT
        self.end_lon = runway_profile.end_lon if runway_profile else RWY_END_LON
        self.runway_heading_deg = float(
            runway_profile.heading_true_deg if runway_profile else RWY_HEADING_TRUE)

        self.theta_rwy: float = self.bearing(
            self.start_lat, self.start_lon, self.end_lat, self.end_lon)

        self.lookahead_min: float = lookahead_min
        self.lookahead_gain: float = lookahead_gain
        self.xte_gain: float = xte_gain

        self.rwy_heading: float = float(np.radians(self.runway_heading_deg))

    @staticmethod
    def wrap_pi(angle: float) -> float:
        return float((angle + np.pi) % (2 * np.pi) - np.pi)

    @staticmethod
    def wrap_deg(angle: float) -> float:
        return float((angle + 180.0) % 360.0 - 180.0)

    @staticmethod
    def bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        phi1 = np.radians(lat1)
        phi2 = np.radians(lat2)

        dlon = np.radians(lon2 - lon1)

        y = np.sin(dlon) * np.cos(phi2)
        x = (np.cos(phi1) * np.sin(phi2) - np.sin(phi1) * np.cos(phi2) * np.cos(dlon))

        return float(np.arctan2(y, x))

    def haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        phi1 = np.radians(lat1)
        phi2 = np.radians(lat2)

        dphi = phi2 - phi1
        dlon = np.radians(lon2 - lon1)

        a = np.sin(dphi / 2.0) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlon / 2.0) ** 2

        return float(self.R * 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a)))

    def destination(
        self,
        lat: float,
        lon: float,
        bearing: float,
        distance: float,
    ) -> tuple[float, float]:
        """Решить прямую геодезическую задачу на сферической Земле."""

        phi1 = np.radians(lat)
        lam1 = np.radians(lon)

        delta = distance / self.R

        phi2 = np.arcsin(
            np.sin(phi1) * np.cos(delta)
            + np.cos(phi1) * np.sin(delta) * np.cos(bearing)
        )

        lam2 = lam1 + np.arctan2(
            np.sin(bearing) * np.sin(delta) * np.cos(phi1),
            np.cos(delta) - np.sin(phi1) * np.sin(phi2)
        )

        return float(np.degrees(phi2)), float(np.degrees(lam2))

    def guidance(
        self,
        aircraft_lat: float,
        aircraft_lon: float,
        aircraft_track_deg: float,
        ground_speed: float,
        *,
        aircraft_heading_deg: float | None = None,
        runway_profile: "RunwayProfile | None" = None,
        source: str = "geodetic",
    ) -> GuidanceState:
        """Геодезическое guidance в истинной системе направлений."""
        start_lat = runway_profile.threshold_lat if runway_profile else self.start_lat
        start_lon = runway_profile.threshold_lon if runway_profile else self.start_lon
        end_lat = runway_profile.end_lat if runway_profile else self.end_lat
        end_lon = runway_profile.end_lon if runway_profile else self.end_lon
        runway_heading_deg = float(
            runway_profile.heading_true_deg if runway_profile else self.runway_heading_deg)
        theta12 = self.bearing(start_lat, start_lon, end_lat, end_lon)
        aircraft_heading_deg = (
            aircraft_track_deg if aircraft_heading_deg is None else aircraft_heading_deg)

        d13 = self.haversine_distance(
            start_lat, start_lon, aircraft_lat, aircraft_lon) / self.R
        theta13 = self.bearing(start_lat, start_lon, aircraft_lat, aircraft_lon)

        xte = np.arcsin(np.sin(d13) * np.sin(theta13 - theta12)) * self.R
        along = np.arctan2(
            np.sin(d13) * np.cos(theta13 - theta12), np.cos(d13)) * self.R
        lookahead = self.lookahead_min + self.lookahead_gain * ground_speed

        target_lat, target_lon = self.destination(
            start_lat, start_lon, theta12, along + lookahead)
        desired_heading = self.bearing(
            aircraft_lat, aircraft_lon, target_lat, target_lon)

        guidance_error = self.wrap_pi(
            desired_heading - np.radians(aircraft_track_deg))
        guidance_error += np.arctan2(
            -self.xte_gain * xte, max(lookahead, 1.0))
        guidance_error = self.wrap_pi(guidance_error)
        course_error = self.wrap_deg(runway_heading_deg - aircraft_track_deg)
        heading_error = self.wrap_deg(runway_heading_deg - aircraft_heading_deg)

        return GuidanceState(
            xte=float(xte),
            along_track=float(along),
            lookahead=float(lookahead),
            course_error_deg=float(course_error),
            heading_error_deg=float(heading_error),
            guidance_error_deg=float(np.degrees(guidance_error)),
            desired_heading_deg=float(
                (aircraft_track_deg + np.degrees(guidance_error)) % 360.0),
            source=source,
        )

    def guidance_from_deviation(
        self,
        aircraft_track_deg: float,
        runway_heading_deg: float,
        xte_m: float,
        ground_speed: float,
        *,
        aircraft_heading_deg: float | None = None,
        source: str = "direct",
    ) -> GuidanceState:
        """Guidance по курсу ВПП и измеренному отклонению — без собственной геодезии.

        Нужна для стенда заказчика: он сообщает `RunwayHeading` и `LateralDeviation`, но **не**
        координаты торцов ВПП, поэтому геодезическую задачу решать не из чего. Зато и не надо:
        то же самое выражается через курс ВПП и отклонение.

        Эквивалентна `guidance()`: пеленг на точку упреждения отличается от оси ВПП на
        `atan2(-e, L)`, к чему добавляется Stanley-коррекция `atan2(-k·e, L)`. Сверено численно —
        совпадает с геодезической формой с точностью до расхождения между `RWY_HEADING_TRUE` и
        фактическим пеленгом между торцами (≈0.01°, артефакт конфигурации).
        """
        aircraft_heading_deg = (
            aircraft_track_deg if aircraft_heading_deg is None else aircraft_heading_deg)
        lookahead = self.lookahead_min + self.lookahead_gain * ground_speed
        L = max(lookahead, 1.0)

        course_error = self.wrap_deg(runway_heading_deg - aircraft_track_deg)
        heading_error = self.wrap_deg(runway_heading_deg - aircraft_heading_deg)
        guidance_error = np.radians(course_error)
        guidance_error += np.arctan2(-xte_m, L)                     # геометрия точки упреждения
        guidance_error += np.arctan2(-self.xte_gain * xte_m, L)     # Stanley-подобная коррекция
        guidance_error = self.wrap_pi(guidance_error)

        return GuidanceState(
            xte=float(xte_m),
            along_track=None,
            lookahead=float(lookahead),
            course_error_deg=float(course_error),
            heading_error_deg=float(heading_error),
            guidance_error_deg=float(np.degrees(guidance_error)),
            desired_heading_deg=float(
                (aircraft_track_deg + np.degrees(guidance_error)) % 360.0),
            source=source,
        )

    def get_cross_track_error(self, lat_ac: float, lon_ac: float) -> float:
        """Возвращает отклонение от осевой линии в метрах. >0 - правее оси, <0 - левее."""
        d_ac = self.haversine_distance(self.start_lat, self.start_lon, lat_ac, lon_ac) / self.R
        theta_ac = self.bearing(self.start_lat, self.start_lon, lat_ac, lon_ac)

        xte = np.asin(np.sin(d_ac) * np.sin(theta_ac - self.theta_rwy)) * self.R
        return float(xte)

    def runway_length_m(self) -> float:
        return float(self.haversine_distance(
            self.start_lat, self.start_lon, self.end_lat, self.end_lon))

    def point_on_centerline(self, distance_before_threshold_m: float) -> tuple[float, float]:
        return self.destination(
            self.start_lat,
            self.start_lon,
            self.rwy_heading + np.pi,
            distance_before_threshold_m,
        )
