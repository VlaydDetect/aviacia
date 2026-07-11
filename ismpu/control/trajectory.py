"""Генератор эталонной кривой скорости пробега.

Два закона замедления: колокол Гаусса (по умолчанию) и равнозамедленное движение.
Перенесено из main.ipynb без изменений.
"""

from enum import Enum

import numpy as np

from ismpu.utils.converts import Converts


class VelocityLaw(Enum):
    EQUALLY_SLOW = 1
    GAUSS_BELL = 2


class ReferenceTrajectory:
    """Генератор эталонной кривой скорости (Колокол Гаусса)."""

    def __init__(self, v_start_kts: float, v_target_kts: float, braking_distance_m: float,
                 law: VelocityLaw = VelocityLaw.GAUSS_BELL):
        self.v_start_ms = v_start_kts * Converts.KTS_TO_MS
        self.v_target_ms = v_target_kts * Converts.KTS_TO_MS
        self.distance = braking_distance_m

        self.law = law

        match law:
            case VelocityLaw.GAUSS_BELL:
                # f(x) = v_start * exp(-x^2 / (2 * b^2))
                # Математический расчет коэффициента 2*b^2 для точного прохождения через точку v_target на дистанции distance
                self.two_b_squared = (self.distance ** 2) / np.log(self.v_start_ms / self.v_target_ms)

            case VelocityLaw.EQUALLY_SLOW:
                # Вычисление требуемого постоянного отрицательного ускорения (модуль)
                # Формула: a = (v_start^2 - v_tgt^2) / (2 * S)
                self.a_req = (self.v_start_ms ** 2 - self.v_target_ms ** 2) / (2.0 * self.distance)

    def get_reference_speed(self, current_distance_m: float) -> float:
        """Возвращает идеальную скорость (м/с) для текущей точки пути."""
        if current_distance_m >= self.distance:
            return self.v_target_ms

        match self.law:
            case VelocityLaw.GAUSS_BELL:
                return self.v_start_ms * np.exp(-(current_distance_m ** 2) / self.two_b_squared)

            case VelocityLaw.EQUALLY_SLOW:
                # v(s) = sqrt(v_0^2 - 2 * a * s)
                val_under_sqrt = self.v_start_ms ** 2 - 2.0 * self.a_req * current_distance_m
                if val_under_sqrt <= 0:
                    return self.v_target_ms

                return np.sqrt(val_under_sqrt)
