"""Оркестратор классического контура управления — на всём интервале полёта.

`ControllingSystem` на каждом такте выбирает участок (`control/flight.py`) и вызывает его закон:
в воздухе — `ApproachChannel` (заход по ILS и выравнивание), на земле — продольный и латеральный
каналы, деградация отказов и отправка команд.

**Транспорта здесь нет.** Контур получает объект стенда (`envs.ics_sim.ICSSim`) и общается с ним
только через `read_telemetry`/`step`; ни JSON, ни UDP, ни единиц ICD он не знает — их переводит
`ICSSim`.

**Воздушные регуляторы живут отдельно от `self.pids`.** Словарь `pids` — это ровно пять
регуляторов пробега из `config/regulators.py`, и из него собраны `ACTION_DIM`, пространство
коэффициентов и все сохранённые чекпоинты NPGS. Положить туда регуляторы захода значило бы молча
переопределить пространство действий; они лежат в самом канале
(`approach_channel.pids`) и настраиваются статически.
"""

from typing import Optional

from ismpu.control.pid import PIDController
from ismpu.control.trajectory import ReferenceTrajectory, VelocityLaw
from ismpu.control.runway_tracker import RunwayTracker
from ismpu.control.channels import ControlsState, LongitudinalChannel, LateralChannel
from ismpu.control.approach import ApproachChannel
from ismpu.control.failures import FailureManager, FailureMode
from ismpu.control.flight import (
    FlightSegment, ApproachRefused, initial_segment, segment_is_decidable, touched_down,
    approach_blocker, ils_blocker,
)
from ismpu.config.approach import ApproachConfig
from ismpu.config.constants import INITIAL_SPEED_KTS, TARGET_SPEED_KTS
from ismpu.config.runway import RWY_START_LAT, RWY_START_LON, RWY_END_LAT, RWY_END_LON


class ControllingSystem:
    """Оркестратор классического контура поверх стенда (`envs.ics_sim.ICSSim`).

    Простейший цикл:

        sim = ICSSim(listen_port=3030)
        controller = ControllingSystem(sim)
        scenario.apply_control(controller)
        controller.begin_flight(sim.read_telemetry())   # с какого участка начинаем
        while not controller.control_step(DT):
            pass

    `control_step` сам читает телеметрию и сам отправляет команды через `sim`. Среда обучения
    (`RolloutEnv`) вместо этого подаёт кадр параметром и ставит `send=False`, чтобы вклинить
    Shield между расчётом и отправкой.

    Без `begin_flight` участок остаётся пробегом. Это осознанное умолчание: среда обучения и все
    офлайн-разборы работают именно с пробегом, и «угадывать» для них воздушный заход по кадру без
    пакета стенда нельзя.
    """

    def __init__(self, sim=None, approach_config: Optional[ApproachConfig] = None):
        self.sim = sim

        self.failures = FailureManager()

        self.pids = dict()
        self.state = ControlsState()
        self.last_telemetry = None

        self.segment = FlightSegment.ROLLOUT
        self._segment_decided = True
        """Определён ли участок окончательно. `False` только между `begin_flight` по
        непригодному кадру и первым пригодным — см. `begin_flight`."""
        self.approach_channel = ApproachChannel(approach_config)
        self.abort_reason: Optional[str] = None

    def setup(self, pids: dict[str, PIDController],
              lookahead_min=15.0, lookahead_gain=1.5, xte_gain=1.0,
              steering_brake_gain=0.4, steering_rev_gain=0.0, law: VelocityLaw = VelocityLaw.GAUSS_BELL):
        self.pids = pids

        # Настройка сценария = начало эпизода: команды сбрасываются вместе с PID и каналами.
        # Иначе `break_control`, выставленный в конце прошлого пробега, оставался бы взведён
        # и следующий эпизод завершался бы на первом такте.
        self.state.reset()

        tracker = RunwayTracker(lookahead_min, lookahead_gain, xte_gain)
        self.lateral_channel = LateralChannel(pids["runway_center_pid"], tracker,
                                              steering_brake_gain, steering_rev_gain)

        trajectory = ReferenceTrajectory(
            INITIAL_SPEED_KTS,
            TARGET_SPEED_KTS,
            tracker.haversine_distance(RWY_START_LAT, RWY_START_LON, RWY_END_LAT, RWY_END_LON),
            law)
        self.longitudinal_channel = LongitudinalChannel(
            pids["pid_brake_l"], pids["pid_brake_r"], pids["pid_rev_l"], pids["pid_rev_r"],
            trajectory)

    def setup_approach(self, config: Optional[ApproachConfig] = None) -> ApproachChannel:
        """Пересобрать воздушный канал под заданные настройки. → новый канал.

        Именно пересобрать, а не переписать коэффициенты: регуляторы захода **stateful**
        (интеграл, фильтр производной, память профиля выравнивания), и перенос состояния прошлого
        захода в новый — это ступень команды руля высоты на первом же такте.
        """
        self.approach_channel = ApproachChannel(config)
        return self.approach_channel

    def set_longitudinal_params(self, lookahead_min: float, lookahead_gain: float, xte_gain: float):
        self.longitudinal_channel.lookahead_min = lookahead_min
        self.longitudinal_channel.lookahead_gain = lookahead_gain
        self.longitudinal_channel.xte_gain = xte_gain

    def set_lateral_params(self, steering_brake_gain: float, steering_rev_gain: float):
        self.lateral_channel.steering_brake_gain = steering_brake_gain
        self.lateral_channel.steering_rev_gain = steering_rev_gain

    def set_channel_weights(self, w_lon: float, w_lat: float):
        """Веса влияния каналов (актор, §6): множители к выходам каналов. 1.0 = классика."""
        self.longitudinal_channel.w_lon = w_lon
        self.lateral_channel.w_lat = w_lat

    def set_velocity_law(self, law: VelocityLaw):
        self.longitudinal_channel.trajectory.law = law

    def apply_failure(self, mode: FailureMode):
        self.failures.activate(mode)

    def sync_failures(self, telemetry) -> None:
        """Привести модель отказов к тому, что сообщает борт (`ICSInputs.Fault*`).

        Отказы читаются, а не задаются: их источник — стенд. Пресет сценария выставляет лишь
        стартовое предположение, а фактическая конфигурация может отличаться и меняться посреди
        пробега, поэтому состояние пересобирается каждый такт.

        При невалидной телеметрии состояние **сохраняется**: единичный потерянный пакет не
        означает, что отказавший орган починился, а «починка» на такт вернула бы рулю авторитет,
        которого у него нет.

        Кадр без пакета стенда (синтетическая телеметрия в тестах и офлайн-разборах) не трогает
        отказы вовсе: пустой `faults` там означает «сообщать некому», а не «всё исправно», и
        приравнять одно к другому значило бы молча снимать отказ пресета.
        """
        if telemetry is None or not telemetry.valid:
            return
        if getattr(telemetry, "ics_inputs", None) is None:
            return
        self.failures.sync(telemetry.faults)

    def begin_flight(self, telemetry) -> FlightSegment:
        """Определить стартовый участок по кадру стенда. → выбранный участок.

        Вызывается в начале прогона. Если стенд сообщает, что ВС в воздухе и выше порога приёма
        захода, начинаем с захода; во всех остальных случаях — с пробега.

        **Непригодный кадр решением не считается.** Первый `read_telemetry` может вернуться по
        таймауту (стенд ещё не шлёт, оператор не нажал ICS) — тогда участок остаётся пробегом
        лишь *предварительно*, и решение принимается заново на первом кадре с пакетом стенда.
        Иначе получалась бы необратимая ошибка: автомат включения решает по **более поздним**
        кадрам и уходит в `Approach`, маска и содержимое команды берутся из его режима, а закон
        считают наземные каналы — на стенд ушли бы нулевой руль высоты (это команда нулевой
        перегрузки, а не нейтраль) и «пройденная дистанция», интегрируемая в полёте.

        Заход, который вести нельзя (`approach_blocker`), — это `ApproachRefused`, а не тихий
        откат на наземный закон: ВС в воздухе, и молча поехать по земле хуже, чем отказаться.
        """
        self._segment_decided = segment_is_decidable(telemetry)
        self.segment = initial_segment(telemetry) if self._segment_decided else FlightSegment.ROLLOUT
        if self.segment is FlightSegment.APPROACH:
            blocker = approach_blocker(telemetry)
            if blocker is not None:
                raise ApproachRefused(f"заход невозможен: {blocker}")
            self.approach_channel.reset()
        return self.segment

    def _settle_segment(self, telemetry) -> None:
        """Досчитать отложенное решение об участке на первом пригодном кадре."""
        if self._segment_decided or not segment_is_decidable(telemetry):
            return
        self._segment_decided = True
        if initial_segment(telemetry) is not FlightSegment.APPROACH:
            return
        blocker = approach_blocker(telemetry)
        if blocker is not None:
            raise ApproachRefused(f"заход невозможен: {blocker}")
        self.segment = FlightSegment.APPROACH
        self.approach_channel.reset()

    def control_step(self, dt: float, telemetry=None, send: bool = True) -> bool:
        """Такт управления. → True, если управление окончено (или телеметрия невалидна).

        `telemetry=None` — кадр берётся сам: сначала результат прошлого `sim.step` (он уже свежий),
        и только на первом такте делается отдельный `sim.read_telemetry()`. Так на стенде выходит
        ровно один приём UDP на такт, а не два.

        `send=False` — команды считаются в `self.state`, но не отправляются: между расчётом и
        отправкой вклинивается Shield (`RolloutEnv`), а отправляет уже вызывающий.
        """
        if telemetry is None:
            telemetry = self.last_telemetry if self.last_telemetry is not None else self._read()
        self.last_telemetry = telemetry
        self._settle_segment(telemetry)
        self.sync_failures(telemetry)

        if self.segment is FlightSegment.APPROACH:
            finished = self._approach_step(dt, telemetry)
        else:
            finished = self._ground_step(dt)
        if finished:
            return True

        if send:
            self.last_telemetry = self._require_sim().step(self.state)

        return False

    def _approach_step(self, dt: float, telemetry) -> bool:
        """Такт воздушного участка. → True, если управлять больше нечем.

        Касание проверяется **до** расчёта закона: после обжатия основных стоек воздушный закон
        неприменим (глиссады уже нет, а РУД пора отдавать реверсу), и такт нужно считать уже
        наземными каналами. Иначе первый такт пробега уходил бы с командой захода.
        """
        if touched_down(telemetry):
            self.hand_over_to_rollout()
            return self._ground_step(dt)

        if not telemetry.valid:
            # Без кадра стенда воздушный закон считать не по чему: размерный расчёт по нулям
            # выдал бы правдоподобное отклонение по несуществующим данным.
            return self._abort_approach("нет валидной телеметрии со стенда")

        # Прерывание по потере наведения живёт здесь, а не в законе: закон читает отклонения
        # безусловно (как и эталон), и решение «дальше вести нечем» принимает контур над ним.
        blocker = ils_blocker(telemetry)
        if blocker is not None:
            return self._abort_approach(blocker)

        self.approach_channel.calc_commands(dt, self.state, telemetry)
        return False

    def _abort_approach(self, reason: str) -> bool:
        """Прервать заход с названной причиной. → True (управлять больше нечем)."""
        self.abort_reason = reason
        print(f"[ControllingSystem] Заход прерван: {reason}")
        self.state.neutralize_airborne()
        self.state.break_control = True
        return True

    def _ground_step(self, dt: float) -> bool:
        """Такт пробега/руления: два канала, финальные пределы, деградация отказов."""
        telemetry = self.last_telemetry
        self.longitudinal_channel.calc_commands(dt, self.state, telemetry)
        self.lateral_channel.calc_commands(dt, self.state, telemetry)
        self.state.clamp_all(self.pids)

        if self.state.break_control:
            return True

        self.state.apply_failures(self.failures.state)
        # Обратная связь по фактически применённой команде — только для наземных регуляторов:
        # на заходе они вообще не считались, и подтягивать их интеграторы к чужим полям значит
        # копить в них мусор к моменту касания.
        self._track_applied(dt)
        return False

    def hand_over_to_rollout(self) -> None:
        """Передать управление с захода на пробег (`ControlMode 1 → 3`).

        Момент — первое обжатие основной стойки. Раньше нельзя: смена `ControlMode` до касания
        сбрасывает автопилот стенда, поэтому весь заход, включая выравнивание, идёт в одном
        режиме `Approach`.
        """
        if self.segment is not FlightSegment.APPROACH:
            return
        self.segment = FlightSegment.ROLLOUT
        # Воздушные команды больше не выдаются — маска пробега их не заявляет, но оставлять в
        # структуре последнее отклонение элеронов значит хранить мусор в логах и в отчёте.
        self.state.neutralize_airborne()
        if self.sim is not None:
            self.sim.request_rollout()

    TAXI_HANDOVER_FRAMES = 4
    """Сколько кадров передать после перехода `3 → 4`. Транспорт — UDP: одиночный кадр с новым
    режимом может потеряться, и стенд не увидит фронта, по которому только и переключается."""

    def hand_over_to_taxi(self, frames: int = TAXI_HANDOVER_FRAMES) -> bool:
        """Передать управление в руление (`ControlMode 3 → 4`) — пробег окончен.

        Вызывается, когда контур объявил достижение скорости руления. Без этого стенд остаётся
        в режиме пробега, хотя ВС уже рулит. Разрешающее условие (обжатие стоек) проверяет сам
        автомат включения (`io/ics_engagement.py`).

        Переход **действительно передаётся**, а не только записывается у нас: `request_taxi`
        меняет лишь состояние автомата, а стенд переключается по фронту `ControlMode` в
        полученном кадре. Раньше после этого вызова управление уходило в остановку цикла, и
        режим `Taxi` не попадал на провод ни разу — стенд так и оставался в пробеге.
        """
        sim = self._require_sim()
        accepted = sim.request_taxi()
        if not accepted:
            return False
        self.segment = FlightSegment.TAXI
        for _ in range(max(1, frames)):
            sim.step(self.state)
        return True

    def _read(self):
        return self._require_sim().read_telemetry()

    def _require_sim(self):
        if self.sim is None:
            raise RuntimeError(
                "контуру не задан стенд: без него он не может ни прочитать телеметрию, ни "
                "отправить команды. Передайте ICSSim в ControllingSystem(sim=...) либо подавайте "
                "кадр параметром и используйте send=False.")
        return self.sim

    # Фактически применённая команда ≠ выходу PID: её меняют вес канала, дифференциальный микс,
    # `clamp_all` и деградация отказов. Без обратной связи интегратор копит на отказавший
    # актуатор (при `steering_eff = 0` — классический windup).
    _TRACKED = (("runway_center_pid", "rudder_cmd"),
                ("pid_brake_l", "cmd_brake_l"), ("pid_brake_r", "cmd_brake_r"),
                ("pid_rev_l", "cmd_rev_l"), ("pid_rev_r", "cmd_rev_r"))

    def _track_applied(self, dt: float) -> None:
        """Back-calculation по итоговым командам. No-op, пока у PID не задан `tracking_tau_s`."""
        for regulator, command_field in self._TRACKED:
            pid = self.pids.get(regulator)
            if pid is not None:
                pid.track(getattr(self.state, command_field), dt)

    def control_exception(self):
        """Аварийная остановка: обнулить органы и **снять заявку каналов**.

        Именно отправить, а не замолчать: молчание оставит последнее отклонение приложенным до
        срабатывания сторожа на стороне стенда. Но и нулевой команды с заявленной маской мало —
        в воздухе нулевое положение РУД это команда «малый газ», а не отказ от управления.
        Поэтому уходим пакетом деактивации (`ControlValidMask = 0`, `ControlMode = Off`), и стенд
        забирает ВС себе.
        """
        print("\n[ControllingSystem] Остановка. Сброс органов и снятие заявки каналов.")
        self.state.neutralize()
        if self.sim is not None:
            self.sim.step(self.state)      # нейтраль в уже заявленных каналах
            self.sim.deactivate()          # затем снятие заявки
        self.state.break_control = True
