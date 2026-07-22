"""Каналы управления и общий вектор команд.

`ControlsState` — разделяемая по тактам структура команд (тормоза, реверс, руль).
`LongitudinalChannel` — управление скоростью (тормоза + реверс) по эталонной кривой.
`LateralChannel` — удержание оси (руление + дифференциальное торможение).

**Транспорта здесь нет.** Каналы получают телеметрию параметром и складывают команды в
`ControlsState`; отправкой и переводом в единицы ПИВ занимается стенд (`ICSSim.step`).
Команды здесь **нормированные** ([0,1] тормоза, [-1,0] реверс, [-1,1] руль) — миллиметры хода
педали и градусы РУД появляются только на границе транспорта.
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
    """Разделяемая по тактам структура команд — и наземных, и воздушных.

    Аннотации типов обязательны: без них `@dataclass` не видит ни одного поля, и тогда
    (а) `__eq__` сравнивает пустой набор — любые два экземпляра равны независимо от команд,
    (б) значения живут как атрибуты класса до первой записи в экземпляр.

    Структура одна на весь полёт, а заполняется по участкам: на заходе пишет
    `control/approach.py`, на пробеге — каналы ниже. Разделять её на две значило бы дублировать
    и `rudder_cmd`, и всю обвязку отправки; вместо этого какие поля **заявлены** стенду решает
    маска (`ICSSim._to_outputs` по текущему `ControlMode`).
    """
    break_control: bool = False

    # --- пробег: нормированные команды ([0,1] тормоза, [-1,0] реверс, [-1,1] руль) --- #
    rudder_cmd: float = 0.0

    cmd_brake_l: float = 0.0
    cmd_brake_r: float = 0.0

    cmd_rev_l: float = 0.0
    cmd_rev_r: float = 0.0

    # --- воздушный участок: единицы ICD --- #
    # Префикс `cmd_` не косметика: по нему `config/regulators.py` собирает
    # `FORBIDDEN_DIRECT_OUTPUTS` — список команд, которые обучаемый слой не выдаёт никогда.
    # Поле, названное иначе, молча выпало бы из контракта ТЗ.
    cmd_elevator: float = 0.0
    """`ElevatorCmd` — продольная команда в **g** (нормальная перегрузка), а не в градусах руля:
    так поле задокументировано в датапуле стенда."""
    cmd_aileron: float = 0.0
    """`AileronCmd` — градусы."""
    cmd_throttle_l_rate: float = 0.0
    cmd_throttle_r_rate: float = 0.0
    """Темп перекладки РУД, град/с (типичный диапазон -8…+8)."""
    cmd_throttle_norm: float = 0.0
    """Абсолютное положение РУД, 0…1. Дублирует темп намеренно: некоторые сборки стенда
    игнорируют маску валидности, и оба канала должны вести к одной уставке, а не спорить."""

    # --- поля качества (`ICSOutputs.Quality*`, ТЗ 5.1.5) --- #
    quality_lateral: float = 0.0
    quality_heading: float = 0.0
    quality_speed: float = 0.0

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
        self.neutralize_airborne()
        self.quality_lateral = self.quality_heading = self.quality_speed = 0.0

    def neutralize_airborne(self):
        """Обнулить только воздушные команды.

        Нужно, когда воздушный канал не может считать закон (нет пакета стенда): оставить
        прошлое отклонение элеронов приложенным нельзя, а придумывать новое — не по чему.
        """
        self.cmd_elevator = 0.0
        self.cmd_aileron = 0.0
        self.cmd_throttle_l_rate = self.cmd_throttle_r_rate = 0.0
        self.cmd_throttle_norm = 0.0

    def apply_failures(self, failures_state: FailureState):
        """Деградация команд по эффективности актуаторов — **только наземные органы**.

        Воздушные команды не трогаются: модель отказов описывает потерю авторитета органов
        пробега (руление носовой стойкой, тормоза, реверс), а поведение планера при отказе на
        заходе моделирует сам стенд. Домножать здесь ещё и элероны значило бы моделировать
        аэродинамику второй раз, поверх стендовой.
        """
        self.rudder_cmd *= failures_state.steering_eff

        self.cmd_brake_l *= failures_state.brake_left_eff
        self.cmd_brake_r *= failures_state.brake_right_eff

        self.cmd_rev_l *= failures_state.reverse_left_eff
        self.cmd_rev_l *= failures_state.thrust_left_eff
        self.cmd_rev_r *= failures_state.reverse_right_eff
        self.cmd_rev_r *= failures_state.thrust_right_eff

    def clamp_all(self, pids: dict[str, PIDController]):
        """Финальные пределы наземных команд — после дифференциального микса.

        Воздушные команды сюда не входят: их зажимают собственные регуляторы захода
        (`control/approach.py`), которых нет в `pids`, и второго микса поверх них нет.
        """
        self.rudder_cmd = pids['runway_center_pid'].clamp(self.rudder_cmd)

        self.cmd_brake_l = pids['pid_brake_l'].clamp(self.cmd_brake_l)
        self.cmd_brake_r = pids['pid_brake_r'].clamp(self.cmd_brake_r)

        self.cmd_rev_l = pids['pid_rev_l'].clamp(self.cmd_rev_l)
        self.cmd_rev_r = pids['pid_rev_r'].clamp(self.cmd_rev_r)

    def neutralize(self):
        """Обнуляет все органы управления. Отправку делает вызывающий через `ICSSim.step`.

        Нейтральная команда, а не молчание: если просто перестать слать, последнее отклонение
        останется приложенным до срабатывания сторожа на той стороне. В воздухе одной нейтрали
        мало — там вместе с ней снимается заявка каналов (`ICSSim.deactivate`), иначе нулевое
        положение РУД было бы командой «малый газ», а не отказом от управления.
        """
        self.cmd_brake_l = self.cmd_brake_r = 0.0
        self.cmd_rev_l = self.cmd_rev_r = 0.0
        self.rudder_cmd = 0.0
        self.neutralize_airborne()


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
            # PID реверса ограничен [-1, 0], поэтому его выход — уже готовая обратная тяга.
            state.cmd_rev_l = self.w_lon * self.pid_rev_l.compute(error, dt)
            state.cmd_rev_r = self.w_lon * self.pid_rev_r.compute(error, dt)
        else:
            # Скорость ниже 60 узлов - принудительное отключение реверса.
            state.cmd_rev_l = 0.0
            state.cmd_rev_r = 0.0
            # Сбрасываем интеграторы, чтобы PID не копил ошибку, пока отключен.
            self.pid_rev_l.reset()
            self.pid_rev_r.reset()

        # Показатель выдерживания скорости (ТЗ 5.1.5) — в узлах, как его ждёт стенд.
        state.quality_speed = abs(current_speed_kts - ref_speed_kts)

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
        """Guidance по тому, что даёт стенд. → словарь guidance или None, если данных нет.

        Стенд сообщает курс ВПП и боковое отклонение напрямую — тогда собственная геодезия не
        нужна и, главное, не применима: координат торцов ВПП стенд не передаёт, и считать от
        захардкоженного Шереметьево значило бы вести ВС по чужой осевой линии.

        Запасной геодезический путь (`config/runway.py`) остаётся на случай, когда стенд не
        объявляет `RunwayHeadingValid`: тогда ось считается по конфигурации.
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
        # Показатели выдерживания (ТЗ 5.1.5): боковое уклонение в **метрах** от осевой и ошибка
        # курса в градусах. На пробеге их обязан заполнять именно этот канал — иначе на стенд
        # уходили бы замороженные величины момента касания (в точках курсового маяка!), а при
        # старте с полосы — постоянные нули, то есть «идеальное выдерживание» при любом сносе.
        state.quality_lateral = abs(guidance["xte"])
        state.quality_heading = abs(error)

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
