"""Пропорционально-интегрально-дифференциальный регулятор.

Улучшенный PID с leaky-интегратором и апериодическим фильтром D-составляющей первого порядка.
Перенесён из main.ipynb без изменения численного поведения; отладочный вывод переведён с
`cprint` на `logging` (на 20 Гц × 5 регуляторов cprint забивал консоль). По умолчанию логгер
молчит; для трассировки:
`logging.getLogger("ismpu.control.pid").setLevel(logging.DEBUG)`.

## Опциональные улучшения численности (заимствованы из `roman_repo/xp_pid_bridge/pid.py`)

Четыре независимых флага, **по умолчанию выключенных**: при значениях по умолчанию численное
поведение бит-в-бит совпадает с прежним, поэтому парити классики и калибровка пресетов не
затрагиваются. Каждый флаг включается отдельно и требует перетюна пресетов.

* `tracking_tau_s` — **back-calculation**. Самый важный для нашего контура: фактически
  применённая команда ≠ выходу PID, потому что `ControlsState.apply_failures()` домножает её
  на эффективность актуатора, `clamp_all()` дожимает после дифференциального микса, а
  `LateralChannel` добавляет разницу к тормозам. Интегратор об этом не знает и копит на
  отказавший актуатор — при `steering_eff = 0` (`NWS_FAIL`) это классический windup.
  `track(applied)` возвращает интегратор к тому, что реально применили.
* `derivative_on_measurement` — производная по измерению, а не по ошибке. Продольный канал ведёт
  цель по `ReferenceTrajectory` (`GAUSS_BELL`), т.е. **уставка непрерывно движется**, и
  производная по ошибке даёт паразитный вклад от движения уставки, а не от динамики объекта.
* `conditional_anti_windup` — интегрировать только если это не загоняет глубже в насыщение
  (выход из насыщения разрешён всегда). Наши тормоза зажаты в `[0,1]`, реверсы в `[-1,0]` и на
  пробеге в насыщении почти постоянно, так что жёсткий клип интеграла работает грубо.
* `exact_discretization` — точные решения вместо аппроксимаций: `alpha = -expm1(-dt/T_f)`
  вместо `dt/(dt+T_f)`, и `error·τ·(1−exp(−dt/τ))` вместо `error·dt` для утечки. На фиксированных
  20 Гц разница мала, но `control_step(dt)` принимает dt параметром, и при просадке цикла
  аппроксимация уплывает.
"""

import logging
import math

import numpy as np

logger = logging.getLogger(__name__)


class PIDController:
    def __init__(self, kp: float, ki: float, kd: float, min_out: float = 0.0, max_out: float = 1.0,
                 anti_windup: float = 10.0, integral_decay: float = 0.0, der_filter_tf: float = 0.1,
                 name: str = "", *,
                 derivative_on_measurement: bool = False,
                 conditional_anti_windup: bool = False,
                 exact_discretization: bool = False,
                 tracking_tau_s: float | None = None):
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

        # --- опциональная численность (по умолчанию = прежнее поведение) ---
        self.derivative_on_measurement = derivative_on_measurement
        self.conditional_anti_windup = conditional_anti_windup
        self.exact_discretization = exact_discretization
        self.tracking_tau_s = tracking_tau_s
        self._prev_deriv_input = None   # вход D-составляющей прошлого такта (ошибка или измерение)

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
        return max(-self.anti_windup, min(self.anti_windup, value))

    # ------------------------------------------------------------------ #
    # Такт
    # ------------------------------------------------------------------ #

    def compute(self, error: float, dt: float, measurement: float | None = None):
        """Такт регулятора. `measurement` обязателен при `derivative_on_measurement=True`."""
        if dt <= 0.0:
            return 0.0

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

        reference = self.last_output if commanded_output is None else commanded_output
        alpha = -math.expm1(-dt / self.tracking_tau_s)
        correction = (applied_output - reference) * alpha / self.ki
        self.integral = self._clip_integral(self.integral + correction)

    def clamp(self, value: float) -> float:
        return max(self.min_out, min(self.max_out, value))

    def reset(self):
        """Сброс внутренних состояний (используется при выключении системы)."""
        self.integral = 0.0
        self.prev_error = None
        self.filtered_derivative = 0.0
        self._prev_deriv_input = None
