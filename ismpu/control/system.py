"""Оркестратор классического контура управления.

`ControllingSystem` на каждом такте вызывает продольный и латеральный каналы,
затем применяет деградацию отказов и отправляет команды. Перенесено из main.ipynb.

Отличие от ноутбука: в `setup()` каналы получают `self.xpc` вместо модульной
глобали `xpc` (в ноутбуке это был один и тот же объект, поведение не меняется;
устранена зависимость от глобального состояния).
"""

from ismpu.control.pid import PIDController
from ismpu.control.trajectory import ReferenceTrajectory, VelocityLaw
from ismpu.control.runway_tracker import RunwayTracker
from ismpu.control.channels import ControlsState, LongitudinalChannel, LateralChannel
from ismpu.control.failures import FailureManager, FailureMode
from ismpu.io.xplane_connector import XPlaneConnectX
from ismpu.config.constants import INITIAL_SPEED_KTS, TARGET_SPEED_KTS
from ismpu.config.runway import RWY_START_LAT, RWY_START_LON, RWY_END_LAT, RWY_END_LON


class ControllingSystem:
    def __init__(self, xpc: XPlaneConnectX):
        self.xpc = xpc

        self.failures = FailureManager()

        self.pids = dict()
        self.state = ControlsState()

    def setup(self, pids: dict[str, PIDController],
              lookahead_min=15.0, lookahead_gain=1.5, xte_gain=1.0,
              steering_brake_gain=0.4, steering_rev_gain=0.0, law: VelocityLaw = VelocityLaw.GAUSS_BELL):
        self.pids = pids

        tracker = RunwayTracker(lookahead_min, lookahead_gain, xte_gain)
        self.lateral_channel = LateralChannel(self.xpc, pids["runway_center_pid"], tracker, steering_brake_gain, steering_rev_gain)

        trajectory = ReferenceTrajectory(
            INITIAL_SPEED_KTS,
            TARGET_SPEED_KTS,
            tracker.haversine_distance(RWY_START_LAT, RWY_START_LON, RWY_END_LAT, RWY_END_LON),
            law)
        self.longitudinal_channel = LongitudinalChannel(self.xpc, pids["pid_brake_l"], pids["pid_brake_r"], pids["pid_rev_l"], pids["pid_rev_r"], trajectory)

    def set_longitudinal_params(self, lookahead_min: float, lookahead_gain: float, xte_gain: float):
        self.longitudinal_channel.lookahead_min = lookahead_min
        self.longitudinal_channel.lookahead_gain = lookahead_gain
        self.longitudinal_channel.xte_gain = xte_gain

    def set_lateral_params(self, steering_brake_gain: float, steering_rev_gain: float):
        self.lateral_channel.steering_brake_gain = steering_brake_gain
        self.lateral_channel.steering_rev_gain = steering_rev_gain

    def set_velocity_law(self, law: VelocityLaw):
        self.longitudinal_channel.trajectory.law = law

    def apply_failure(self, mode: FailureMode):
        self.failures.activate(mode)

    def control_step(self, dt: float) -> bool:
        self.longitudinal_channel.calc_commands(dt, self.state)
        self.lateral_channel.calc_commands(dt, self.state)
        self.state.clamp_all(self.pids)

        if self.state.break_control:
            return True

        self.state.apply_failures(self.failures.state)
        self.state.send_commands(self.xpc)

        return False

    def control_exception(self):
        self.state.control_exception(self.xpc)
