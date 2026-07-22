"""Каналы управления и общий вектор команд.

`ControlsState` — разделяемая по тактам структура команд (тормоза, реверс, руль).
`LongitudinalChannel` — управление скоростью (тормоза + реверс) по эталонной кривой.
`LateralChannel` — удержание оси (руление + дифференциальное торможение).

**Транспорта здесь нет.** Каналы получают телеметрию параметром и складывают команды в
`ControlsState`; отправкой занимается бэкенд (`SimInterface.step`). Раньше `ControlsState`
сам писал DataRef'ы X-Plane, из-за чего контур нельзя было запустить на стенде заказчика.
"""

from dataclasses import dataclass

from termcolor import cprint

from ismpu.utils.converts import Converts
from ismpu.control.pid import PIDController
from ismpu.control.trajectory import ReferenceTrajectory
from ismpu.control.runway_tracker import RunwayTracker
from ismpu.control.failures import FailureState
from ismpu.config.requirements import HEADING_HOLD_UNTIL_KTS

ROLLOUT_STARTED_KTS = HEADING_HOLD_UNTIL_KTS
"""Порог, выше которого считаем, что пробег начался. Та же граница (30 узлов), на которой ТЗ
5.1.3.3 снимает требование по удержанию курса, — ниже неё режим уже руление, а не пробег."""


@dataclass
class ControlsState:
    """Разделяемая по тактам структура команд.

    Аннотации типов обязательны: без них `@dataclass` не видит ни одного поля, и тогда
    (а) `__eq__` сравнивает пустой набор — любые два экземпляра равны независимо от команд,
    (б) значения живут как атрибуты класса до первой записи в экземпляр.
    """
    break_control: bool = False

    # commands
    rudder_cmd: float = 0.0

    cmd_brake_l: float = 0.0
    cmd_brake_r: float = 0.0

    cmd_rev_l: float = 0.0
    cmd_rev_r: float = 0.0

    def reset(self):
        """Сброс к нейтральным командам — новый эпизод начинается с чистого состояния.

        Критично для `break_control`: он выставляется в конце КАЖДОГО нормального пробега
        (достигнута скорость руления), и без сброса следующий эпизод завершался бы на первом
        же такте.
        """
        self.break_control = False
        self.rudder_cmd = 0.0
        self.cmd_brake_l = self.cmd_brake_r = 0.0
        self.cmd_rev_l = self.cmd_rev_r = 0.0

    def apply_failures(self, failures_state: FailureState):
        self.rudder_cmd *= failures_state.steering_eff

        self.cmd_brake_l *= failures_state.brake_left_eff
        self.cmd_brake_r *= failures_state.brake_right_eff

        self.cmd_rev_l *= failures_state.reverse_left_eff
        self.cmd_rev_l *= failures_state.thrust_left_eff
        self.cmd_rev_r *= failures_state.reverse_right_eff
        self.cmd_rev_r *= failures_state.thrust_left_eff

    def clamp_all(self, pids: dict[str, PIDController]):
        self.rudder_cmd = pids['runway_center_pid'].clamp(self.rudder_cmd)

        self.cmd_brake_l = pids['pid_brake_l'].clamp(self.cmd_brake_l)
        self.cmd_brake_r = pids['pid_brake_r'].clamp(self.cmd_brake_r)

        self.cmd_rev_l = pids['pid_rev_l'].clamp(self.cmd_rev_l)
        self.cmd_rev_r = pids['pid_rev_r'].clamp(self.cmd_rev_r)

    def neutralize(self):
        """Обнуляет все органы управления. Отправку делает вызывающий через `SimInterface.step`.

        Нейтральная команда, а не молчание: если просто перестать слать, последнее отклонение
        останется приложенным до срабатывания сторожа на той стороне.
        """
        self.cmd_brake_l = self.cmd_brake_r = 0.0
        self.cmd_rev_l = self.cmd_rev_r = 0.0
        self.rudder_cmd = 0.0


class LongitudinalChannel:
    """Управление скоростью по эталонной кривой. Телеметрию получает параметром, не читает сам."""

    def __init__(self, pid_brake_l: PIDController, pid_brake_r: PIDController,
                 pid_rev_l: PIDController, pid_rev_r: PIDController, trajectory: ReferenceTrajectory):
        self.trajectory = trajectory

        self.pid_brake_l = pid_brake_l
        self.pid_brake_r = pid_brake_r
        self.pid_rev_l = pid_rev_l
        self.pid_rev_r = pid_rev_r

        self.traveled_distance_m = 0.0
        self.w_lon = 1.0  # вес влияния канала (актор, §6); 1.0 = классика
        self.rollout_started = False
        """Защёлка «пробег действительно начался».

        Без неё условие «скорость руления достигнута» тривиально истинно у неподвижного ВС
        (0 м/с ≤ 5.14 м/с), и контур завершался бы на первом же такте — в частности, до того как
        успевает пройти двухсекундное рукопожатие со стендом. При касании на 140 узлах защёлка
        ставится на первом такте, поэтому поведение классики не меняется."""

        print("[LongitudinalChannel] Запуск продольного канала.")

    def calc_commands(self, dt: float, state: ControlsState, telemetry):
        # `valid` проверяется ПЕРВЫМ и отдельно от полей: бэкенд стенда при обрыве связи отдаёт
        # нули, а не None, и проверка «поле is None» пропустила бы groundspeed = 0.0 дальше —
        # где оно тут же выглядело бы как «достигнута скорость руления».
        if not telemetry.valid or telemetry.groundspeed_ms is None:
            state.cmd_brake_l = state.cmd_brake_r = state.cmd_rev_l = state.cmd_rev_r = 0.0
            state.break_control = True
            return

        current_speed_ms = telemetry.groundspeed_ms

        self.traveled_distance_m += current_speed_ms * dt
        ref_speed_ms = self.trajectory.get_reference_speed(self.traveled_distance_m)
        current_speed_kts = current_speed_ms * Converts.MS_TO_KTS
        ref_speed_kts = ref_speed_ms * Converts.MS_TO_KTS

        # Глобальная ошибка по скорости. >0 означает, что мы едем слишком быстро
        error = current_speed_ms - ref_speed_ms

        # 1. Расчет тормозов (Hydraulic Brakes). w_lon — вес влияния канала (=1 у классики).
        state.cmd_brake_l = self.w_lon * self.pid_brake_l.compute(error, dt)
        state.cmd_brake_r = self.w_lon * self.pid_brake_r.compute(error, dt)

        # 2. Расчет реверса (Thrust Reversers) с учетом эксплуатационного лимита
        if current_speed_kts > 60.0:
            # Скорость безопасна для реверса
            state.cmd_rev_l = self.w_lon * self.pid_rev_l.compute(error, dt)  # Инверсия знака для X-Plane
            state.cmd_rev_r = self.w_lon * self.pid_rev_r.compute(error, dt)
        else:
            # Скорость ниже 60 узлов - принудительное отключение реверса.
            state.cmd_rev_l = 0.0
            state.cmd_rev_r = 0.0
            # Сбрасываем интеграторы, чтобы PID не копил ошибку, пока отключен.
            self.pid_rev_l.reset()
            self.pid_rev_r.reset()

        cprint(
            f"[LongitudinalChannel] Dist: {self.traveled_distance_m:4.0f}m | V_cur: {current_speed_kts:3.0f}; V_ref: {ref_speed_kts:3.0f} | "
            f"Brk_L: {state.cmd_brake_l:.2f}; Brk_R: {state.cmd_brake_r:.2f} | "
            f"Rev_L: {state.cmd_rev_l:.2f}; Rev_R: {state.cmd_rev_r:.2f}", "green")

        if current_speed_kts >= ROLLOUT_STARTED_KTS:
            self.rollout_started = True

        # Пробег нельзя объявить оконченным, пока он не начался: иначе неподвижное ВС на земле
        # завершает эпизод на первом такте (см. `rollout_started`).
        if self.rollout_started and current_speed_ms <= self.trajectory.v_target_ms:
            print("[LongitudinalChannel] Посадочная дистанция пройдена. Скорость руления достигнута.")
            state.cmd_brake_l = state.cmd_brake_r = 0.1
            state.cmd_rev_l = state.cmd_rev_r = 0.0
            state.break_control = True


class LateralChannel:
    """Удержание оси ВПП. Телеметрию получает параметром, не читает сам."""

    def __init__(self, pid: PIDController, tracker: RunwayTracker, steering_brake_gain=0.4,
                 steering_rev_gain=0.0):
        self.pid = pid

        self.tracker = tracker
        self.steering_brake_gain = steering_brake_gain
        self.steering_rev_gain = steering_rev_gain
        self.w_lat = 1.0  # вес влияния канала (актор, §6); 1.0 = классика

        print("[LateralChannel] Запуск латерального канала.")

    def _guidance(self, telemetry, heading, groundspeed_ms):
        """Guidance по тому, что даёт бэкенд. → словарь guidance или None, если данных нет.

        Стенд заказчика сообщает курс ВПП и боковое отклонение напрямую — тогда собственная
        геодезия не нужна и, главное, не применима: координат торцов ВПП стенд не передаёт, и
        считать от захардкоженного Шереметьево значило бы вести ВС по чужой осевой линии.

        X-Plane этих полей не даёт → работает прежний геодезический путь, бит-в-бит как раньше.
        """
        runway_heading = getattr(telemetry, "runway_heading_deg", None)
        lateral_deviation = getattr(telemetry, "lateral_deviation_m", None)
        if runway_heading is not None and lateral_deviation is not None:
            return self.tracker.guidance_from_deviation(
                heading, runway_heading, lateral_deviation, groundspeed_ms)

        if None in (telemetry.lat, telemetry.lon):
            return None
        return self.tracker.guidance(telemetry.lat, telemetry.lon, heading, groundspeed_ms)

    def calc_commands(self, dt: float, state: ControlsState, telemetry):
        heading = telemetry.heading_true_deg
        groundspeed_ms = telemetry.groundspeed_ms
        # `valid` — первым: см. комментарий в LongitudinalChannel.calc_commands.
        if not telemetry.valid or None in (heading, groundspeed_ms):
            cprint(f"[RunwayCenteringSystem] Error: telemetry is invalid", "red")
            state.rudder_cmd = 0.0
            return

        guidance = self._guidance(telemetry, heading, groundspeed_ms)
        if guidance is None:
            cprint(f"[RunwayCenteringSystem] Error: telemetry is invalid", "red")
            state.rudder_cmd = 0.0
            return

        error = guidance["heading_error_deg"]
        # w_lat — вес влияния латерального канала (=1 у классики); масштабирует руль и дифф. микс.
        state.rudder_cmd = self.w_lat * self.pid.compute(error, dt)

        diff_brake = state.rudder_cmd * self.steering_brake_gain  # Коэффициент микширования
        state.cmd_brake_l -= diff_brake
        state.cmd_brake_r += diff_brake

        if groundspeed_ms * Converts.MS_TO_KTS > 60.0:
            diff_rev = state.rudder_cmd * self.steering_rev_gain
            state.cmd_rev_l += diff_rev
            state.cmd_rev_r -= diff_rev

        cprint(
            f"[LateralChannel] XTE={guidance['xte']:+6.2f} м | "
            f"Herr={error:+6.2f}° | "
            f"L={guidance['lookahead']:5.1f} м | "
            f"Rudder={state.rudder_cmd:+.3f}",
            "yellow"
        )
