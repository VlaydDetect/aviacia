"""Пропорционально-интегрально-дифференциальный регулятор.

Класс сохраняет прежнюю численность по умолчанию для совместимости воздушного контура.
Наземная фабрика включает вариант из `working_ics`: derivative-on-measurement, точный ZOH-фильтр,
`dt` 0,001–0,25 с, conditional anti-windup и отдельные пределы интегратора. Опциональный
`track(applied)` возвращает интегратор к фактически распределённой allocator-ом команде.
"""

import logging
import math
from dataclasses import dataclass

import numpy as np

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PIDDiagnostics:
    """Типизированный снимок последнего такта регулятора."""

    error: float
    measurement: float | None
    p: float
    i: float
    d: float
    unconstrained: float
    output: float
    integral: float
    derivative: float
    saturated: bool


class PIDController:
    def __init__(self, kp: float, ki: float, kd: float, min_out: float = 0.0, max_out: float = 1.0,
                 anti_windup: float = 10.0, integral_decay: float = 0.0, der_filter_tf: float = 0.1,
                 name: str = "", *,
                 derivative_on_measurement: bool = False,
                 conditional_anti_windup: bool = False,
                 exact_discretization: bool = False,
                 tracking_tau_s: float | None = None,
                 integral_min: float | None = None,
                 integral_max: float | None = None,
                 clamp_dt: bool = False,
                 dt_min_s: float = 0.001,
                 dt_max_s: float = 0.25) -> None:
        self.kp: float = kp
        self.ki: float = ki
        self.kd: float = kd
        self.name: str = name

        self.min_out: float = min_out
        self.max_out: float = max_out

        self.integral: float = 0.0
        # Первый такт не имеет предыдущего отсчёта для производной.
        self.prev_error: float | None = None

        self.anti_windup: float = anti_windup
        self.integral_min: float = -anti_windup if integral_min is None else integral_min
        self.integral_max: float = anti_windup if integral_max is None else integral_max
        if self.integral_min > self.integral_max:
            raise ValueError("integral_min must not exceed integral_max")
        # Коэффициент экспоненциального затухания интеграла
        self.integral_decay: float = integral_decay
        # Постоянная времени фильтра низких частот D-составляющей (T_f в секундах)
        self.der_filter_tf: float = der_filter_tf
        # Накопленное отфильтрованное значение производной
        self.filtered_derivative: float = 0.0
        # Последний зажатый выход (для Observation Space)
        self.last_output: float = 0.0
        self.last_error: float = 0.0
        self.last_measurement: float | None = None
        self.last_unconstrained: float = 0.0
        self.last_p_term: float = 0.0
        self.last_i_term: float = 0.0
        self.last_d_term: float = 0.0

        # --- опциональная численность (по умолчанию = прежнее поведение) ---
        self.derivative_on_measurement: bool = derivative_on_measurement
        self.conditional_anti_windup: bool = conditional_anti_windup
        self.exact_discretization: bool = exact_discretization
        self.tracking_tau_s: float | None = tracking_tau_s
        self.clamp_dt: bool = clamp_dt
        self.dt_min_s: float = dt_min_s
        self.dt_max_s: float = dt_max_s
        if self.dt_min_s <= 0.0 or self.dt_min_s > self.dt_max_s:
            raise ValueError("dt limits must satisfy 0 < dt_min_s <= dt_max_s")
        # вход D-составляющей прошлого такта (ошибка или измерение)
        self._prev_deriv_input: float | None = None

    # ------------------------------------------------------------------ #
    # Внутренние составляющие
    # ------------------------------------------------------------------ #

    def _filter_alpha(self, dt: float) -> float:
        """Вес апериодического фильтра D-составляющей за такт `dt`."""
        if self.der_filter_tf <= 0.0:
            return 1.0
        if self.exact_discretization:
            # Точное решение звена первого порядка (ZOH), устойчиво при любом dt.
            return -math.expm1(-dt / self.der_filter_tf)
        # Прежняя аппроксимация — сохраняется по умолчанию ради парити.
        return dt / (dt + self.der_filter_tf)

    def _integral_candidates(self, error: float, dt: float) -> tuple[float, float]:
        """→ (интеграл только с утечкой, интеграл с утечкой и приращением). Оба уже зажаты."""
        if self.integral_decay > 0.0:
            decay = np.exp(-self.integral_decay * dt)
            leaked = self.integral * decay
            if self.exact_discretization:
                # Точное решение при постоянной ошибке на такте: τ = 1/decay.
                increment = error * (1.0 / self.integral_decay) * (1.0 - decay)
            else:
                increment = error * dt
        else:
            leaked = self.integral
            increment = error * dt

        candidate = self._clip_integral(leaked + increment)
        # Прежний путь зажимал только итог; при conditional AW нужен и зажатый «только утечка».
        return (self._clip_integral(leaked) if self.conditional_anti_windup else leaked), candidate

    def _clip_integral(self, value: float) -> float:
        return max(self.integral_min, min(self.integral_max, value))

    # ------------------------------------------------------------------ #
    # Такт
    # ------------------------------------------------------------------ #

    def compute(self, error: float, dt: float, measurement: float | None = None) -> float:
        """Такт регулятора. `measurement` обязателен при `derivative_on_measurement=True`."""
        if not self.clamp_dt and dt <= 0.0:
            return 0.0
        if self.clamp_dt:
            dt = max(self.dt_min_s, min(self.dt_max_s, dt))

        if self.derivative_on_measurement and measurement is None:
            raise ValueError(
                f"PID '{self.name}': derivative_on_measurement=True требует measurement")

        leaked, candidate_integral = self._integral_candidates(error, dt)

        # --- D-составляющая ---
        # По измерению производная берётся со знаком минус: рост измерения = убывание ошибки,
        # но при этом движение уставки в неё уже не попадает.
        deriv_input = -measurement if self.derivative_on_measurement else error

        derivative = 0.0
        if self._prev_deriv_input is not None:
            raw_derivative = (deriv_input - self._prev_deriv_input) / dt
            alpha = self._filter_alpha(dt)
            # Инкрементная форма, а не `alpha*raw + (1-alpha)*filtered`. Алгебраически это одно
            # и то же, но в плавающей точке формы расходятся на ~1e-16, и на 400 тактах прогона
            # 118 из них давали разные биты с реализацией второго участника НИР. Воздушный
            # контур перенесён от него вместе с коэффициентами — совпадение должно быть точным,
            # иначе «тот же PID» превращается в «почти тот же».
            self.filtered_derivative += alpha * (raw_derivative - self.filtered_derivative)
            derivative = self.filtered_derivative
        else:
            self.filtered_derivative = 0.0

        # --- выход и решение об интегрировании ---
        unconstrained = (self.kp * error) + (self.ki * candidate_integral) + (self.kd * derivative)

        if self.conditional_anti_windup:
            # Интегрируем, если выход не в насыщении ИЛИ приращение уводит ИЗ насыщения.
            integral_delta = self.ki * (candidate_integral - self.integral)
            may_integrate = (
                self.min_out <= unconstrained <= self.max_out
                or (unconstrained > self.max_out and integral_delta < 0.0)
                or (unconstrained < self.min_out and integral_delta > 0.0)
            )
            self.integral = candidate_integral if may_integrate else leaked
        else:
            self.integral = candidate_integral

        logger.debug("PID '%s': error=%s, integral=%s, derivative=%s",
                     self.name, error, self.integral, derivative)

        self.prev_error = error
        self._prev_deriv_input = deriv_input

        self.last_error = error
        self.last_measurement = measurement
        self.last_p_term = self.kp * error
        # Компоненты описывают именно рассчитанный выход этого такта. При conditional
        # anti-windup сохранённое состояние интегратора может отклонить candidate уже после
        # расчёта команды; оно отдельно доступно как `integral` в диагностике.
        self.last_i_term = self.ki * candidate_integral
        self.last_d_term = self.kd * derivative
        self.last_unconstrained = unconstrained
        self.last_output = self.clamp(unconstrained)
        return self.last_output

    def track(self, applied_output: float, dt: float, commanded_output: float | None = None) -> None:
        """Back-calculation: подтянуть интегратор к фактически применённой команде.

        No-op пока не задан `tracking_tau_s` — поэтому вызывать можно безусловно, поведение
        классики по умолчанию не меняется. `commanded_output` по умолчанию — последний выход
        `compute`; передавать явно нужно, если между PID и актуатором есть свой пересчёт.
        """
        if self.tracking_tau_s is None or self.ki == 0.0 or dt <= 0.0:
            return

        if self.clamp_dt:
            dt = max(self.dt_min_s, min(self.dt_max_s, dt))

        reference = self.last_output if commanded_output is None else commanded_output
        alpha = -math.expm1(-dt / self.tracking_tau_s)
        correction = (applied_output - reference) * alpha / self.ki
        self.integral = self._clip_integral(self.integral + correction)

    def clamp(self, value: float) -> float:
        return max(self.min_out, min(self.max_out, value))

    def diagnostics(self) -> PIDDiagnostics:
        return PIDDiagnostics(
            error=self.last_error,
            measurement=self.last_measurement,
            p=self.last_p_term,
            i=self.last_i_term,
            d=self.last_d_term,
            unconstrained=self.last_unconstrained,
            output=self.last_output,
            integral=self.integral,
            derivative=self.filtered_derivative,
            saturated=(
                self.last_unconstrained < self.min_out
                or self.last_unconstrained > self.max_out
            ),
        )

    def set_gains_bumpless(self, *, kp: float, ki: float, kd: float) -> None:
        """Сменить коэффициенты без сброса D-history и с компенсацией интегратором.

        Текущий ограниченный выход используется как цель. Если новый ``ki`` равен нулю или
        требуемый интеграл выходит за его физические пределы, сохраняется ближайшее достижимое
        состояние — искусственный bias в классический PID не добавляется.
        """
        values = (float(kp), float(ki), float(kd))
        if not all(math.isfinite(value) for value in values):
            raise ValueError("PID gains must be finite")
        target = self.last_output
        self.kp, self.ki, self.kd = values
        if abs(self.ki) > 1e-15:
            self.integral = self._clip_integral(
                (target - self.kp * self.last_error
                 - self.kd * self.filtered_derivative) / self.ki)
        self.last_p_term = self.kp * self.last_error
        self.last_i_term = self.ki * self.integral
        self.last_d_term = self.kd * self.filtered_derivative
        self.last_unconstrained = (
            self.last_p_term + self.last_i_term + self.last_d_term)
        self.last_output = self.clamp(self.last_unconstrained)

    def reset(self) -> None:
        """Сброс внутренних состояний (используется при выключении системы)."""
        self.integral = 0.0
        self.prev_error = None
        self.filtered_derivative = 0.0
        self._prev_deriv_input = None
        self.last_error = 0.0
        self.last_measurement = None
        self.last_unconstrained = 0.0
        self.last_p_term = self.last_i_term = self.last_d_term = 0.0
        self.last_output = 0.0
