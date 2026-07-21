"""Слежение за осью ВПП: геодезия, cross-track error, guidance с look-ahead.

Сферическая модель Земли (haversine, bearing, прямая геодезическая задача).
Guidance формирует Stanley-подобную ошибку курса по точке упреждения
(look-ahead), масштабируемой скоростью. Перенесено из main.ipynb без изменений;
константы ВПП импортируются из config.runway (ранее — модульные глобали ноутбука).
"""

import numpy as np

from ismpu.config.runway import (
    RWY_START_LAT, RWY_START_LON, RWY_END_LAT, RWY_END_LON, RWY_HEADING_TRUE,
)


class RunwayTracker:
    def __init__(self, lookahead_min=15.0, lookahead_gain=1.5, xte_gain=1.0):
        self.R = 6371008.7714  # Средний радиус Земли в метрах

        self.theta_rwy = self.bearing(RWY_START_LAT, RWY_START_LON, RWY_END_LAT, RWY_END_LON)

        self.lookahead_min = lookahead_min
        self.lookahead_gain = lookahead_gain
        self.xte_gain = xte_gain

        self.rwy_heading = np.radians(RWY_HEADING_TRUE)

    @staticmethod
    def wrap_pi(angle):
        return (angle + np.pi) % (2 * np.pi) - np.pi

    @staticmethod
    def wrap_deg(angle):
        return (angle + 180.0) % 360.0 - 180.0

    @staticmethod
    def bearing(lat1: float, lon1: float, lat2: float, lon2: float):
        phi1 = np.radians(lat1)
        phi2 = np.radians(lat2)

        dlon = np.radians(lon2 - lon1)

        y = np.sin(dlon) * np.cos(phi2)
        x = (np.cos(phi1) * np.sin(phi2) - np.sin(phi1) * np.cos(phi2) * np.cos(dlon))

        return np.arctan2(y, x)

    def haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float):
        phi1 = np.radians(lat1)
        phi2 = np.radians(lat2)

        dphi = phi2 - phi1
        dlon = np.radians(lon2 - lon1)

        a = np.sin(dphi / 2.0) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlon / 2.0) ** 2

        return self.R * 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    def destination(self, lat, lon, bearing, distance):
        """
        Решение прямой геодезической задачи.
        """

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

        return np.degrees(phi2), np.degrees(lam2)

    def guidance(self,
                 aircraft_lat,
                 aircraft_lon,
                 aircraft_heading_deg,
                 ground_speed):
        d13 = self.haversine_distance(
            RWY_START_LAT,
            RWY_START_LON,
            aircraft_lat,
            aircraft_lon
        ) / self.R

        theta13 = self.bearing(
            RWY_START_LAT,
            RWY_START_LON,
            aircraft_lat,
            aircraft_lon
        )

        theta12 = self.rwy_heading

        # Cross-track
        xte = np.arcsin(
            np.sin(d13) *
            np.sin(theta13 - theta12)
        ) * self.R

        # Along-track
        along = np.arctan2(
            np.sin(d13) * np.cos(theta13 - theta12),
            np.cos(d13)
        ) * self.R

        # LookAhead
        lookahead = self.lookahead_min + self.lookahead_gain * ground_speed

        target_distance = along + lookahead

        target_lat, target_lon = self.destination(
            RWY_START_LAT,
            RWY_START_LON,
            theta12,
            target_distance
        )

        desired_heading = self.bearing(
            aircraft_lat,
            aircraft_lon,
            target_lat,
            target_lon
        )

        aircraft_heading = np.radians(aircraft_heading_deg)

        heading_error = self.wrap_pi(
            desired_heading - aircraft_heading
        )

        # Stanley-подобная коррекция
        heading_error += np.arctan2(
            -self.xte_gain * xte,
            max(lookahead, 1.0)
        )

        heading_error = self.wrap_pi(heading_error)

        return {
            "xte": xte,
            "along": along,
            "lookahead": lookahead,
            "heading_error_deg": np.degrees(heading_error),
            "desired_heading_deg": np.degrees(desired_heading),
        }

    def guidance_from_deviation(self, aircraft_heading_deg, runway_heading_deg, xte_m, ground_speed):
        """Guidance по курсу ВПП и измеренному отклонению — без собственной геодезии.

        Нужна для стенда заказчика: он сообщает `RunwayHeading` и `LateralDeviation`, но **не**
        координаты торцов ВПП, поэтому геодезическую задачу решать не из чего. Зато и не надо:
        то же самое выражается через курс ВПП и отклонение.

        Эквивалентна `guidance()`: пеленг на точку упреждения отличается от оси ВПП на
        `atan2(-e, L)`, к чему добавляется Stanley-коррекция `atan2(-k·e, L)`. Сверено численно —
        совпадает с геодезической формой с точностью до расхождения между `RWY_HEADING_TRUE` и
        фактическим пеленгом между торцами (≈0.01°, артефакт конфигурации).
        """
        lookahead = self.lookahead_min + self.lookahead_gain * ground_speed
        L = max(lookahead, 1.0)

        heading_error = np.radians(self.wrap_deg(runway_heading_deg - aircraft_heading_deg))
        heading_error += np.arctan2(-xte_m, L)                      # геометрия точки упреждения
        heading_error += np.arctan2(-self.xte_gain * xte_m, L)      # Stanley-подобная коррекция
        heading_error = self.wrap_pi(heading_error)

        return {
            "xte": xte_m,
            "along": None,          # вдоль-трековая координата на стенде не восстанавливается
            "lookahead": lookahead,
            "heading_error_deg": np.degrees(heading_error),
            "desired_heading_deg": float(runway_heading_deg),
        }

    def get_cross_track_error(self, lat_ac: float, lon_ac: float):
        """Возвращает отклонение от осевой линии в метрах. >0 - правее оси, <0 - левее."""
        d_ac = self.haversine_distance(RWY_START_LAT, RWY_START_LON, lat_ac, lon_ac) / self.R
        theta_ac = self.bearing(RWY_START_LAT, RWY_START_LON, lat_ac, lon_ac)

        xte = np.asin(np.sin(d_ac) * np.sin(theta_ac - self.theta_rwy)) * self.R
        return xte
