"""Генератор эталонной кривой скорости пробега.

Два закона замедления: колокол Гаусса (по умолчанию) и равнозамедленное движение.
Перенесено из main.ipynb без изменений.
"""

from dataclasses import dataclass
from enum import Enum

import numpy as np

from ismpu.utils.converts import Converts


class VelocityLaw(Enum):
    EQUALLY_SLOW = 1
    GAUSS_BELL = 2


class CompletionRule(str, Enum):
    """Как активный наземный сценарий заканчивает управление."""

    FULL_STOP = "full_stop"
    HANDOVER_TAXI = "handover_taxi"
    OPERATOR = "operator"


@dataclass(frozen=True)
class TrajectoryState:
    distance_m: float
    reference_speed_ms: float
    finished: bool


class ReferenceTrajectory:
    """Генератор эталонной кривой скорости (Колокол Гаусса)."""

    def __init__(self, v_start_kts: float, v_target_kts: float, braking_distance_m: float,
                 law: VelocityLaw = VelocityLaw.GAUSS_BELL,
                 completion_rule: CompletionRule = CompletionRule.HANDOVER_TAXI) -> None:
        self.v_target_ms: float = v_target_kts * Converts.KTS_TO_MS
        self.distance: float = braking_distance_m
        self.law: VelocityLaw = law
        self.completion_rule: CompletionRule = completion_rule
        self.v_start_ms: float = 0.0
        self.two_b_squared: float = 0.0
        self.a_req: float = 0.0
        self.reset(v_start_kts)

    def reset(self, v_start_kts: float) -> None:
        """Начать профиль с фактической скорости текущего участка."""
        if not np.isfinite(v_start_kts) or v_start_kts < 0.0:
            raise ValueError("v_start_kts must be finite and non-negative")
        self.reset_ms(v_start_kts * Converts.KTS_TO_MS)

    def reset_ms(self, v_start_ms: float) -> None:
        """То же без лишнего round-trip м/с → узлы → м/с на касании."""
        if not np.isfinite(v_start_ms) or v_start_ms < 0.0:
            raise ValueError("v_start_ms must be finite and non-negative")
        if not np.isfinite(self.distance) or self.distance <= 0.0:
            raise ValueError("braking_distance_m must be finite and positive")
        if not np.isfinite(self.v_target_ms) or self.v_target_ms < 0.0:
            raise ValueError("v_target_kts must be non-negative")
        self.v_start_ms = v_start_ms

        if self.v_start_ms <= self.v_target_ms:
            self.two_b_squared = float("inf")
            self.a_req = 0.0
            return

        match self.law:
            case VelocityLaw.GAUSS_BELL:
                # Параметр выбран так, чтобы кривая прошла через v_target на distance.
                # f(x) = v_start * exp(-x^2 / (2 * b^2))
                # Для полной остановки логарифм от деления на ноль не определён; до конца
                # дистанции ведём профиль к 0,5 уз, а в самой конечной точке возвращаем 0.
                endpoint = max(self.v_target_ms, 0.5 * Converts.KTS_TO_MS)
                self.two_b_squared = (self.distance ** 2) / np.log(
                    self.v_start_ms / min(endpoint, self.v_start_ms * 0.999999))

            case VelocityLaw.EQUALLY_SLOW:
                # Постоянное замедление из v² = v₀² - 2as.
                # Формула: a = (v_start^2 - v_tgt^2) / (2 * S)
                self.a_req = (self.v_start_ms ** 2 - self.v_target_ms ** 2) / (2.0 * self.distance)

    def set_law(self, law: VelocityLaw) -> None:
        self.law = law
        self.reset_ms(self.v_start_ms)

    def get_reference_speed(self, current_distance_m: float) -> float:
        """Возвращает идеальную скорость (м/с) для текущей точки пути."""
        if self.v_start_ms <= self.v_target_ms:
            return self.v_target_ms
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

    def state_at(self, current_distance_m: float) -> TrajectoryState:
        distance = float(current_distance_m)
        return TrajectoryState(
            distance_m=distance,
            reference_speed_ms=float(self.get_reference_speed(distance)),
            finished=distance >= self.distance,
        )
