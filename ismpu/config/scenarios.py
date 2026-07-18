"""Пресеты классических PID-коэффициентов по сценариям.

Перенесены из ячеек main.ipynb (`# default`, `# left reverse fail`,
`# right reverse fail`, `# NWS fault`). Данные отделены от построения: каждый
`ScenarioConfig` хранит коэффициенты, а `build_pids()`/`apply()` создают свежие
(stateful!) экземпляры `PIDController` — общий экземпляр между запусками
недопустим.

`apply()` настраивает контур И активирует связанный с пресетом `FailureMode`
(если он не NONE). `NWS_FAIL` откалиброван под реальный отказ руления носовой
стойкой (`steering_eff→0`): удержание оси обеспечивается дифференциальным
торможением и асимметричной тягой (`steering_brake_gain` / `steering_rev_gain`).
Сценарии реверса (`LEFT_REVERSE_FAIL` / `RIGHT_REVERSE_FAIL`) перенесены из
черновых ячеек ноутбука и требуют калибровки/валидации.
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ismpu.control.pid import PIDController
from ismpu.control.trajectory import VelocityLaw
from ismpu.control.failures import FailureMode
from ismpu.envs.weather import WeatherState, WEATHER_PRESETS

if TYPE_CHECKING:
    from ismpu.control.system import ControllingSystem


@dataclass(frozen=True)
class ScenarioConfig:
    name: str
    failure: FailureMode
    runway_center: dict
    brake_l: dict
    brake_r: dict
    rev_l: dict
    rev_r: dict
    weather: WeatherState = field(default_factory=lambda: WEATHER_PRESETS["clear_dry"])
    lookahead_min: float = 10.0
    lookahead_gain: float = 1.8
    xte_gain: float = 2.0
    steering_brake_gain: float = 0.4
    steering_rev_gain: float = 0.0
    law: VelocityLaw = VelocityLaw.GAUSS_BELL
    draft: bool = False  # True = черновой пресет, требует калибровки

    def build_pids(self) -> dict[str, PIDController]:
        """Создаёт свежий набор из 5 регуляторов (по имени аргументов setup())."""
        return dict(
            runway_center_pid=PIDController(**self.runway_center),
            pid_brake_l=PIDController(**self.brake_l),
            pid_brake_r=PIDController(**self.brake_r),
            pid_rev_l=PIDController(**self.rev_l),
            pid_rev_r=PIDController(**self.rev_r),
        )

    def apply(self, controller: "ControllingSystem") -> "ControllingSystem":
        """Настраивает контур под сценарий и активирует связанный отказ (если задан)."""
        controller.setup(
            self.build_pids(),
            lookahead_min=self.lookahead_min,
            lookahead_gain=self.lookahead_gain,
            xte_gain=self.xte_gain,
            steering_brake_gain=self.steering_brake_gain,
            steering_rev_gain=self.steering_rev_gain,
            law=self.law,
        )
        if self.failure is not FailureMode.NONE:
            controller.apply_failure(self.failure)
        return controller


DEFAULT = ScenarioConfig(
    name="default",
    failure=FailureMode.NONE,
    runway_center=dict(kp=0.0015, ki=0.0001, kd=0.065, min_out=-1, max_out=1, integral_decay=0.5, name="Runway_Center"),
    brake_l=dict(kp=0.1, ki=0.01, kd=0.05, min_out=0.0, max_out=1.0, name="Brake_L"),
    brake_r=dict(kp=0.1, ki=0.01, kd=0.05, min_out=0.0, max_out=1.0, name="Brake_R"),
    rev_l=dict(kp=0.03, ki=0.002, kd=0.01, min_out=-1.0, max_out=0.0, name="Rev_L"),
    rev_r=dict(kp=0.03, ki=0.002, kd=0.01, min_out=-1.0, max_out=0.0, name="Rev_R"),
    lookahead_min=10.0, lookahead_gain=1.8, xte_gain=2.0, steering_brake_gain=0.4,
)

# Активный сценарий ноутбука.
NWS_FAIL = ScenarioConfig(
    name="nws_fail",
    failure=FailureMode.NWS_FAIL,
    runway_center=dict(kp=0.0015, ki=0.0001, kd=0.065, min_out=-1, max_out=1, integral_decay=0.5, name="Runway_Center"),
    brake_l=dict(kp=0.12, ki=0.002, kd=0.11, min_out=0.0, max_out=1.0, integral_decay=0.5, der_filter_tf=0.1, anti_windup=5, name="Brake_L"),
    brake_r=dict(kp=0.12, ki=0.002, kd=0.11, min_out=0.0, max_out=1.0, integral_decay=0.5, der_filter_tf=0.1, anti_windup=5, name="Brake_R"),
    rev_l=dict(kp=0.12, ki=0.0065, kd=0.1, min_out=-1.0, max_out=0.0, integral_decay=0.7, name="Rev_L"),
    rev_r=dict(kp=0.12, ki=0.0065, kd=0.1, min_out=-1.0, max_out=0.0, integral_decay=0.7, name="Rev_R"),
    lookahead_min=10.0, lookahead_gain=1.2, xte_gain=0.8, steering_brake_gain=0.75, steering_rev_gain=0.5,
)

LEFT_REVERSE_FAIL = ScenarioConfig(
    name="left_reverse_fail",
    failure=FailureMode.REVERSE_LEFT_FAIL,
    runway_center=dict(kp=0.0004, ki=0.0006, kd=0.07, min_out=-1, max_out=1, integral_decay=0.15, name="Runway_Center"),
    brake_l=dict(kp=0.1, ki=0.01, kd=0.05, min_out=0.0, max_out=1.0, name="Brake_L"),
    brake_r=dict(kp=0.08, ki=0.015, kd=0.06, min_out=0.0, max_out=1.0, name="Brake_R"),
    rev_l=dict(kp=0.03, ki=0.0025, kd=0.02, min_out=-1.0, max_out=0.0, name="Rev_L"),
    rev_r=dict(kp=0.03, ki=0.0025, kd=0.02, min_out=-1.0, max_out=0.0, name="Rev_R"),
    lookahead_min=10.0, lookahead_gain=1.6, xte_gain=2.0, steering_brake_gain=0.4,
)

RIGHT_REVERSE_FAIL = ScenarioConfig(
    name="right_reverse_fail",
    failure=FailureMode.REVERSE_RIGHT_FAIL,
    runway_center=dict(kp=0.0004, ki=0.0006, kd=0.07, min_out=-1, max_out=1, integral_decay=0.15, name="Runway_Center"),
    brake_l=dict(kp=0.08, ki=0.015, kd=0.06, min_out=0.0, max_out=1.0, name="Brake_L"),
    brake_r=dict(kp=0.1, ki=0.01, kd=0.05, min_out=0.0, max_out=1.0, name="Brake_R"),
    rev_l=dict(kp=0.03, ki=0.0025, kd=0.02, min_out=-1.0, max_out=0.0, name="Rev_L"),
    rev_r=dict(kp=0.03, ki=0.0025, kd=0.02, min_out=-1.0, max_out=0.0, name="Rev_R"),
    lookahead_min=10.0, lookahead_gain=1.6, xte_gain=2.0, steering_brake_gain=0.4,
)

RIGHT_WIND = ScenarioConfig(
    name="right_wind",
    failure=FailureMode.NONE,
    weather=WeatherState.from_crosswind(10.0, 0.0),
    # runway_center=dict(kp=0.009, ki=0.0075, kd=0.09, min_out=-1, max_out=1, anti_windup=2, integral_decay=0.65, name="Runway_Center"),
    # brake_l=dict(kp=0.1, ki=0.01, kd=0.05, min_out=0.0, max_out=1.0, name="Brake_L"),
    # brake_r=dict(kp=0.1, ki=0.01, kd=0.05, min_out=0.0, max_out=1.0, name="Brake_R"),
    # rev_l=dict(kp=0.03, ki=0.002, kd=0.01, min_out=-1.0, max_out=0.0, name="Rev_L"),
    # rev_r=dict(kp=0.03, ki=0.002, kd=0.01, min_out=-1.0, max_out=0.0, name="Rev_R"),
    # lookahead_min=5.0, lookahead_gain=1.4, xte_gain=1.7, steering_brake_gain=0.3, steering_rev_gain=0.5
    runway_center=dict(kp=0.001, ki=0.0073, kd=0.09, min_out=-1, max_out=1, anti_windup=2.13, integral_decay=0.63, name="Runway_Center"),
    brake_l=dict(kp=0.1, ki=0.01, kd=0.05, min_out=0.0, max_out=1.0, name="Brake_L"),
    brake_r=dict(kp=0.1, ki=0.01, kd=0.05, min_out=0.0, max_out=1.0, name="Brake_R"),
    rev_l=dict(kp=0.03, ki=0.002, kd=0.01, min_out=-1.0, max_out=0.0, name="Rev_L"),
    rev_r=dict(kp=0.03, ki=0.002, kd=0.01, min_out=-1.0, max_out=0.0, name="Rev_R"),
    lookahead_min=5.2, lookahead_gain=1.39, xte_gain=1.72, steering_brake_gain=0.35, steering_rev_gain=0.53
)

FWD_WIND = ScenarioConfig(
    name="fwd_wind",
    failure=FailureMode.NONE,
    weather=WeatherState.from_crosswind(0.0, 10.0),
    runway_center=dict(kp=0.0015, ki=0.0005, kd=0.065, min_out=-1, max_out=1, anti_windup=2.5, integral_decay=0.5, name="Runway_Center"),
    brake_l=dict(kp=0.1, ki=0.01, kd=0.05, min_out=0.0, max_out=1.0, name="Brake_L"),
    brake_r=dict(kp=0.1, ki=0.01, kd=0.05, min_out=0.0, max_out=1.0, name="Brake_R"),
    rev_l=dict(kp=0.03, ki=0.002, kd=0.01, min_out=-1.0, max_out=0.0, name="Rev_L"),
    rev_r=dict(kp=0.03, ki=0.002, kd=0.01, min_out=-1.0, max_out=0.0, name="Rev_R"),
    lookahead_min=15.0, lookahead_gain=1.8, xte_gain=2.0, steering_brake_gain=0.4,
)

WET_RWY = ScenarioConfig(
    name="wet_rwy",
    failure=FailureMode.NONE,
    weather=WEATHER_PRESETS["wet"],
    runway_center=dict(kp=0.0015, ki=0.0001, kd=0.065, min_out=-1, max_out=1, integral_decay=0.5, name="Runway_Center"),
    brake_l=dict(kp=0.1, ki=0.01, kd=0.05, min_out=0.0, max_out=1.0, name="Brake_L"),
    brake_r=dict(kp=0.1, ki=0.01, kd=0.05, min_out=0.0, max_out=1.0, name="Brake_R"),
    rev_l=dict(kp=0.03, ki=0.002, kd=0.01, min_out=-1.0, max_out=0.0, name="Rev_L"),
    rev_r=dict(kp=0.03, ki=0.002, kd=0.01, min_out=-1.0, max_out=0.0, name="Rev_R"),
    lookahead_min=10.0, lookahead_gain=1.8, xte_gain=2.0, steering_brake_gain=0.4,
)

PUDDLY_RWY = ScenarioConfig(
    name="puddly_rwy",
    failure=FailureMode.NONE,
    weather=WEATHER_PRESETS["puddly"],
    runway_center=dict(kp=0.0015, ki=0.0001, kd=0.065, min_out=-1, max_out=1, integral_decay=0.5, name="Runway_Center"),
    brake_l=dict(kp=0.1, ki=0.01, kd=0.05, min_out=0.0, max_out=1.0, name="Brake_L"),
    brake_r=dict(kp=0.1, ki=0.01, kd=0.05, min_out=0.0, max_out=1.0, name="Brake_R"),
    rev_l=dict(kp=0.03, ki=0.002, kd=0.01, min_out=-1.0, max_out=0.0, name="Rev_L"),
    rev_r=dict(kp=0.03, ki=0.002, kd=0.01, min_out=-1.0, max_out=0.0, name="Rev_R"),
    lookahead_min=10.0, lookahead_gain=1.8, xte_gain=2.0, steering_brake_gain=0.4,
)

ICY_RWY = ScenarioConfig(
    name="icy_rwy",
    failure=FailureMode.NONE,
    weather=WEATHER_PRESETS["icy"],
    runway_center=dict(kp=0.0015, ki=0.0001, kd=0.065, min_out=-1, max_out=1, integral_decay=0.5, name="Runway_Center"),
    brake_l=dict(kp=0.1, ki=0.01, kd=0.05, min_out=0.0, max_out=1.0, name="Brake_L"),
    brake_r=dict(kp=0.1, ki=0.01, kd=0.05, min_out=0.0, max_out=1.0, name="Brake_R"),
    rev_l=dict(kp=0.03, ki=0.002, kd=0.01, min_out=-1.0, max_out=0.0, name="Rev_L"),
    rev_r=dict(kp=0.03, ki=0.002, kd=0.01, min_out=-1.0, max_out=0.0, name="Rev_R"),
    lookahead_min=10.0, lookahead_gain=1.8, xte_gain=2.0, steering_brake_gain=0.4,
)

SCENARIOS = {
    s.name: s for s in (DEFAULT, NWS_FAIL, LEFT_REVERSE_FAIL, RIGHT_REVERSE_FAIL, RIGHT_WIND, FWD_WIND, WET_RWY, PUDDLY_RWY, ICY_RWY)
}
