"""Оркестратор классического контура управления.

`ControllingSystem` на каждом такте вызывает продольный и латеральный каналы, применяет
деградацию отказов и отправляет команды.

**Транспорта здесь нет.** Контур получает объект стенда (`envs.ics_sim.ICSSim`) и общается с ним
только через `read_telemetry`/`step`; ни JSON, ни UDP, ни единиц ICD он не знает — их переводит
`ICSSim`.
"""

from typing import Optional

from ismpu.control.pid import PIDController
from ismpu.control.trajectory import ReferenceTrajectory, VelocityLaw
from ismpu.control.runway_tracker import RunwayTracker
from ismpu.control.channels import ControlsState, LongitudinalChannel, LateralChannel
from ismpu.control.failures import FailureManager, FailureMode
from ismpu.config.constants import INITIAL_SPEED_KTS, TARGET_SPEED_KTS
from ismpu.config.runway import RWY_START_LAT, RWY_START_LON, RWY_END_LAT, RWY_END_LON


class ControllingSystem:
    """Оркестратор классического контура поверх стенда (`envs.ics_sim.ICSSim`).

    Простейший цикл:

        sim = ICSSim(listen_port=3030)
        controller = ControllingSystem(sim)
        scenario.apply_control(controller)
        while not controller.control_step(DT):
            pass

    `control_step` сам читает телеметрию и сам отправляет команды через `sim`. Среда обучения
    (`RolloutEnv`) вместо этого подаёт кадр параметром и ставит `send=False`, чтобы вклинить
    Shield между расчётом и отправкой.
    """

    def __init__(self, sim=None):
        self.sim = sim

        self.failures = FailureManager()

        self.pids = dict()
        self.state = ControlsState()
        self.last_telemetry = None

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

    def control_step(self, dt: float, telemetry=None, send: bool = True) -> bool:
        """Такт управления. → True, если пробег окончен (или телеметрия невалидна).

        `telemetry=None` — кадр берётся сам: сначала результат прошлого `sim.step` (он уже свежий),
        и только на первом такте делается отдельный `sim.read_telemetry()`. Так на стенде выходит
        ровно один приём UDP на такт, а не два.

        `send=False` — команды считаются в `self.state`, но не отправляются: между расчётом и
        отправкой вклинивается Shield (`RolloutEnv`), а отправляет уже вызывающий.
        """
        if telemetry is None:
            telemetry = self.last_telemetry if self.last_telemetry is not None else self._read()
        self.last_telemetry = telemetry
        self.sync_failures(telemetry)

        self.longitudinal_channel.calc_commands(dt, self.state, telemetry)
        self.lateral_channel.calc_commands(dt, self.state, telemetry)
        self.state.clamp_all(self.pids)

        if self.state.break_control:
            return True

        self.state.apply_failures(self.failures.state)
        self._track_applied(dt)
        if send:
            self.last_telemetry = self._require_sim().step(self.state)

        return False

    def hand_over_to_taxi(self) -> bool:
        """Передать управление в руление (`ControlMode 3 → 4`) — пробег окончен.

        Вызывается, когда контур объявил достижение скорости руления. Без этого стенд остаётся
        в режиме пробега, хотя ВС уже рулит. Разрешающее условие (обжатие стоек) проверяет сам
        автомат включения (`io/ics_engagement.py`).
        """
        return self._require_sim().request_taxi()

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
        """Аварийная остановка: обнулить органы, отправить нейтральную команду, встать.

        Именно отправить, а не замолчать: молчание оставит последнее отклонение приложенным до
        срабатывания сторожа на стороне симулятора/стенда.
        """
        print("\n[MultiChannelAutoBrake] Остановка. Сброс всех управляющих органов.")
        self.state.neutralize()
        if self.sim is not None:
            self.sim.step(self.state)
        self.state.break_control = True
