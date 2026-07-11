"""Каналы управления и общий вектор команд.

`ControlsState` — разделяемая по тактам структура команд (тормоза, реверс, руль).
`LongitudinalChannel` — управление скоростью (тормоза + реверс) по эталонной кривой.
`LateralChannel` — удержание оси (руление + дифференциальное торможение).
Перенесено из main.ipynb без изменения логики; строковые DREF заменены на
именованные константы из io.datarefs (эквивалентно).
"""

from dataclasses import dataclass

from termcolor import cprint

from ismpu.utils.converts import Converts
from ismpu.control.pid import PIDController
from ismpu.control.trajectory import ReferenceTrajectory
from ismpu.control.runway_tracker import RunwayTracker
from ismpu.control.failures import FailureState
from ismpu.io.xplane_connector import XPlaneConnectX
from ismpu.io.datarefs import (
    GROUNDSPEED, LATITUDE, LONGITUDE, TRUE_PSI,
    LEFT_BRAKE_RATIO, RIGHT_BRAKE_RATIO, THROTTLE_RATIO_L, THROTTLE_RATIO_R,
    YOKE_HEADING_RATIO,
)


@dataclass
class ControlsState:
    break_control = False

    # commands
    rudder_cmd = 0.0

    cmd_brake_l = 0.0
    cmd_brake_r = 0.0

    cmd_rev_l = 0.0
    cmd_rev_r = 0.0

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

    def send_commands(self, xpc: XPlaneConnectX) -> bool:
        if self.break_control:
            return True

        xpc.sendDREF(LEFT_BRAKE_RATIO, self.cmd_brake_l)
        xpc.sendDREF(RIGHT_BRAKE_RATIO, self.cmd_brake_r)
        xpc.sendDREF(THROTTLE_RATIO_L, self.cmd_rev_l)
        xpc.sendDREF(THROTTLE_RATIO_R, self.cmd_rev_r)
        xpc.sendDREF(YOKE_HEADING_RATIO, self.rudder_cmd)

        return False

    def control_exception(self, xpc: XPlaneConnectX):
        print("\n[MultiChannelAutoBrake] Остановка. Сброс всех управляющих органов.")
        self.cmd_brake_l = self.cmd_brake_r = self.cmd_rev_l = self.cmd_rev_r = self.rudder_cmd = 0.0
        self.send_commands(xpc)


class LongitudinalChannel:
    def __init__(self, xpc: XPlaneConnectX, pid_brake_l: PIDController, pid_brake_r: PIDController,
                 pid_rev_l: PIDController, pid_rev_r: PIDController, trajectory: ReferenceTrajectory):
        self.xpc = xpc

        self.trajectory = trajectory

        self.pid_brake_l = pid_brake_l
        self.pid_brake_r = pid_brake_r
        self.pid_rev_l = pid_rev_l
        self.pid_rev_r = pid_rev_r

        self.traveled_distance_m = 0.0

        print("[LongitudinalChannel] Запуск продольного канала.")

    def calc_commands(self, dt: float, state: ControlsState):
        current_speed_ms = self.xpc.current_dref_values[GROUNDSPEED]['value']
        if current_speed_ms is None:
            state.cmd_brake_l = state.cmd_brake_r = state.cmd_rev_l = state.cmd_rev_r = 0.0
            state.break_control = True
            return

        self.traveled_distance_m += current_speed_ms * dt
        ref_speed_ms = self.trajectory.get_reference_speed(self.traveled_distance_m)
        current_speed_kts = current_speed_ms * Converts.MS_TO_KTS
        ref_speed_kts = ref_speed_ms * Converts.MS_TO_KTS

        # Глобальная ошибка по скорости. >0 означает, что мы едем слишком быстро
        error = current_speed_ms - ref_speed_ms

        # 1. Расчет тормозов (Hydraulic Brakes)
        state.cmd_brake_l = self.pid_brake_l.compute(error, dt)
        state.cmd_brake_r = self.pid_brake_r.compute(error, dt)

        # 2. Расчет реверса (Thrust Reversers) с учетом эксплуатационного лимита
        if current_speed_kts > 60.0:
            # Скорость безопасна для реверса
            state.cmd_rev_l = self.pid_rev_l.compute(error, dt)  # Инверсия знака для X-Plane
            state.cmd_rev_r = self.pid_rev_r.compute(error, dt)
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

        if current_speed_ms <= self.trajectory.v_target_ms:
            print("[LongitudinalChannel] Посадочная дистанция пройдена. Скорость руления достигнута.")
            state.cmd_brake_l = state.cmd_brake_r = 0.1
            state.cmd_rev_l = state.cmd_rev_r = 0.0
            state.break_control = True


class LateralChannel:
    def __init__(self, xpc: XPlaneConnectX, pid: PIDController, tracker: RunwayTracker, steering_brake_gain=0.4,
                 steering_rev_gain=0.0):
        self.xpc = xpc

        self.pid = pid

        self.tracker = tracker
        self.steering_brake_gain = steering_brake_gain
        self.steering_rev_gain = steering_rev_gain

        print("[LateralChannel] Запуск латерального канала.")

    def calc_commands(self, dt: float, state: ControlsState):
        lat = self.xpc.current_dref_values[LATITUDE]['value']
        lon = self.xpc.current_dref_values[LONGITUDE]['value']
        heading = self.xpc.current_dref_values[TRUE_PSI]["value"]
        groundspeed_ms = self.xpc.current_dref_values[GROUNDSPEED]["value"]
        if None in (lat, lon, heading, groundspeed_ms):
            cprint(f"[RunwayCenteringSystem] Error: drefs values is None", "red")
            state.rudder_cmd = 0.0
            return

        guidance = self.tracker.guidance(lat, lon, heading, groundspeed_ms)

        error = guidance["heading_error_deg"]
        state.rudder_cmd = self.pid.compute(error, dt)

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
