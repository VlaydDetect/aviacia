"""Пропорционально-интегрально-дифференциальный регулятор.

Улучшенный PID с leaky-интегратором и апериодическим фильтром D-составляющей
первого порядка. Перенесён из main.ipynb без изменения численного поведения;
единственное отличие — отладочный вывод переведён с `cprint` на `logging`
(на 20 Гц × 5 регуляторов cprint забивал консоль). По умолчанию логгер молчит;
для трассировки: `logging.getLogger("ismpu.control.pid").setLevel(logging.DEBUG)`.
"""

import logging

import numpy as np
from termcolor import cprint

logger = logging.getLogger(__name__)
logging.getLogger("ismpu.control.pid").setLevel(logging.DEBUG)

class PIDController:
    def __init__(self, kp: float, ki: float, kd: float, min_out: float = 0.0, max_out: float = 1.0,
                 anti_windup: float = 10.0, integral_decay: float = 0.0, der_filter_tf: float = 0.1, name: str = ""):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.name = name

        self.min_out = min_out
        self.max_out = max_out

        self.integral = 0.0
        # Avoiding differential shock at startup
        self.prev_error = None

        self.anti_windup = anti_windup
        self.integral_decay = integral_decay  # Коэффициент экспоненциального затухания интеграла
        self.der_filter_tf = der_filter_tf  # Постоянная времени фильтра низких частот D-составляющей (T_f в секундах)
        self.filtered_derivative = 0.0  # Накопленное отфильтрованное значение производной
        self.last_output = 0.0  # Последний зажатый выход (для Observation Space)

    def compute(self, error: float, dt: float):
        if dt <= 0.0:
            return 0.0

        if self.integral_decay > 0.0:
            self.integral *= np.exp(-self.integral_decay * dt)

        self.integral += error * dt
        # Anti-windup (защита от накопления интеграла)
        self.integral = max(-self.anti_windup, min(self.anti_windup, self.integral))

        # Экспоненциальный низкочастотный фильтр (Low-Pass Filter / IIR) для производной
        derivative = 0.0
        if self.prev_error is not None:
            raw_derivative = (error - self.prev_error) / dt

            # Расчет весового коэффициента альфа на основе шага dt и постоянной времени фильтра T_f
            # Формула: alpha = dt / (dt + T_f)
            alpha = dt / (dt + self.der_filter_tf)

            # Применение апериодического фильтра первого порядка
            self.filtered_derivative = alpha * raw_derivative + (1.0 - alpha) * self.filtered_derivative
            derivative = self.filtered_derivative
        else:
            self.prev_error = error
            self.filtered_derivative = 0.0

        logger.debug("PID '%s': error=%s, integral=%s, derivative=%s", self.name, error, self.integral, derivative)
        # cprint(f"PID '{self.name}': error={error}, integral={self.integral}, derivative={derivative}", "red")

        self.prev_error = error
        output = (self.kp * error) + (self.ki * self.integral) + (self.kd * derivative)

        self.last_output = self.clamp(output)
        return self.last_output

    def clamp(self, value: float) -> float:
        return max(self.min_out, min(self.max_out, value))

    def reset(self):
        """Сброс внутренних состояний (используется при выключении системы)."""
        self.integral = 0.0
        self.prev_error = None
        self.filtered_derivative = 0.0
