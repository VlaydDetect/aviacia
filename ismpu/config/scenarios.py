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

from dataclasses import dataclass, field, replace
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
    approach: str = "default"
    """Имя пресета воздушного участка (`config.approach.APPROACH_PRESETS`). Отдельным полем, а не
    частью этого набора: воздушные коэффициенты статические и в пространство коэффициентов NPGS
    не входят, поэтому смешивать их с пятью регуляторами пробега нельзя."""
    matrix_code: str = ""
    """Шифр матрицы прогонов (`config.run_matrix`), если пресет заведён под неё."""

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
        """Настраивает контур под сценарий и активирует связанный отказ (если задан).

        Настраиваются **оба** участка: пять регуляторов пробега из этого набора и воздушный
        пресет по имени. Иначе сценарий, заведённый под сквозной прогон с отказом двигателя на
        глиссаде, менял бы только пробег — то есть ровно не тот участок, где отказ вводится.
        """
        from ismpu.config.approach import APPROACH_PRESETS

        controller.setup(
            self.build_pids(),
            lookahead_min=self.lookahead_min,
            lookahead_gain=self.lookahead_gain,
            xte_gain=self.xte_gain,
            steering_brake_gain=self.steering_brake_gain,
            steering_rev_gain=self.steering_rev_gain,
            law=self.law,
        )
        controller.setup_approach(APPROACH_PRESETS[self.approach])
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

# --------------------------------------------------------------------------- #
# Черновые пресеты под матрицу прогонов (лист Б: ВПП и руление)
# --------------------------------------------------------------------------- #
#
# Один шифр матрицы = один набор коэффициентов: внутри шифра прогоны идут от простого к сложному,
# и настройка переносится с предыдущего на следующий (см. `config/run_matrix.py`). Поэтому пресет
# заводится на шифр, а не на строку таблицы.
#
# Каждый черновик наследуется от **ближайшего откалиброванного** пресета, а не от нулей: начинать
# настройку от работающего набора — ровно то, что предписывает методика матрицы. Пометка
# `draft=True` при этом говорит правду: под конкретный отказ коэффициенты ещё не считались, и
# автоматический подбор по телеметрии такие пресеты не берёт.

def _matrix_draft(base: ScenarioConfig, name: str, code: str, *,
                  failure: FailureMode | None = None,
                  approach: str = "default", **overrides) -> ScenarioConfig:
    """Черновик под шифр матрицы на базе откалиброванного пресета.

    Словари коэффициентов копируются: `ScenarioConfig` заморожен, но сами словари — нет, и
    общий словарь на два пресета означал бы, что настройка одного молча меняет другой.
    """
    spec = dict(
        name=name, matrix_code=code, draft=True, approach=approach,
        failure=base.failure if failure is None else failure,
        runway_center=dict(base.runway_center), brake_l=dict(base.brake_l),
        brake_r=dict(base.brake_r), rev_l=dict(base.rev_l), rev_r=dict(base.rev_r),
    )
    spec.update(overrides)
    return replace(base, **spec)


B_1_1_ROLLOUT = _matrix_draft(DEFAULT, "b_1_1_rollout", "Б.1.1")
"""Штатный пробег от касания до полной остановки. Критерий — ось ВПП ± 3 м (ТЗ 5.1.3.1)."""

B_1_2_TAXI = _matrix_draft(
    DEFAULT, "b_1_2_taxi", "Б.1.2",
    lookahead_min=5.0, lookahead_gain=1.2, xte_gain=3.0)
"""Руление по прямому участку. Допуск втрое жёстче пробега (± 1 м), а скорости втрое ниже,
поэтому упреждение укорочено, а реакция на боковое смещение усилена — это отправная точка
настройки, а не результат."""

B_2_1_NWS_STUCK_NEUTRAL = _matrix_draft(NWS_FAIL, "b_2_1_nws_stuck_neutral", "Б.2.1")
"""Заедание носовой стойки в нейтрали. Ближайший откалиброванный родитель — `nws_fail`:
у него удержание оси уже перенесено на дифференциальное торможение и асимметричную тягу."""

B_2_2_NWS_STUCK_OFFSET = _matrix_draft(
    NWS_FAIL, "b_2_2_nws_stuck_offset", "Б.2.2",
    steering_brake_gain=0.9, steering_rev_gain=0.6)
"""Заедание с уводом (+5°). Хуже нейтрали: стойка не просто бездействует, а постоянно тянет с
полосы, и парировать это приходится тормозами и тягой непрерывно, а не эпизодически."""

B_2_3_NWS_LIMITED = _matrix_draft(NWS_FAIL, "b_2_3_nws_limited", "Б.2.3")
"""Ограничение диапазона до ± 3°. Смешанное управление: стойка ещё живая, но её авторитета не
хватает. Заводится от `nws_fail`, хотя по смыслу лежит между ним и штатным пробегом."""

B_3_1_REVERSE_LEFT_FAIL = _matrix_draft(LEFT_REVERSE_FAIL, "b_3_1_reverse_left_fail", "Б.3.1")
"""Отказ реверса левого двигателя."""

B_3_2_REVERSE_ASYMMETRIC = _matrix_draft(LEFT_REVERSE_FAIL, "b_3_2_reverse_asymmetric", "Б.3.2")
"""Несимметричное включение реверса (левый с задержкой 3 с). По телеметрии неотличим от Б.3.1 —
выбирается только по имени."""

B_3_3_RESIDUAL_THRUST = _matrix_draft(
    LEFT_REVERSE_FAIL, "b_3_3_residual_thrust", "Б.3.3",
    failure=FailureMode.THRUST_LEFT_DEGRADED)
"""Остаточная прямая тяга ~30 % на левом. Отличается от отказа реверса знаком возмущения: не
«нечем тормозить слева», а «слева подталкивает вперёд»."""

B_4_1_THROUGH = _matrix_draft(DEFAULT, "b_4_1_through", "Б.4.1", approach="a_1_2_flare")
"""Сквозной прогон без отказов: глиссада → касание → пробег. Критерий добавляет то, чего нет ни
у одного участка по отдельности — отсутствие скачка управляющих воздействий на стыке."""

B_4_2_THROUGH_ENGINE_OUT = _matrix_draft(
    LEFT_REVERSE_FAIL, "b_4_2_through_engine_out", "Б.4.2",
    approach="a_4_1_engine_out_high")
"""Сквозной, худший случай: отказ левого двигателя на глиссаде + отказ его реверса на пробеге."""


# --------------------------------------------------------------------------- #
# Черновые пресеты под лист А матрицы (заход и посадка)
# --------------------------------------------------------------------------- #
#
# Настраивается там воздушный контур (`config/approach.py`), а не пять регуляторов пробега.
# Но запускать прогон всё равно нужно чем-то целым, поэтому шифр захода получает сценарий:
# наземная часть — штатная (после касания прогон обычный), воздушная — своя.
#
# В SFT они не идут: обучаемый слой планирует коэффициенты пробега, а не захода, и метки для
# воздушного участка у него попросту нет.

_APPROACH_MATRIX = (
    ("a_1_1_track", "А.1.1", FailureMode.NONE),
    ("a_1_2_flare", "А.1.2", FailureMode.NONE),
    ("a_2_1_gear_left_up", "А.2.1", FailureMode.GEAR_CONFIG),
    ("a_2_2_gear_nose_up", "А.2.2", FailureMode.GEAR_CONFIG),
    ("a_2_3_gear_partial", "А.2.3", FailureMode.GEAR_CONFIG),
    ("a_3_1_stab_nose_down_high", "А.3.1", FailureMode.NONE),
    ("a_3_2_stab_nose_up_high", "А.3.2", FailureMode.NONE),
    ("a_3_3_stab_nose_down_low", "А.3.3", FailureMode.NONE),
    ("a_3_4_stab_nose_up_low", "А.3.4", FailureMode.NONE),
    ("a_4_1_engine_out_high", "А.4.1", FailureMode.ENGINE_OUT_LEFT),
    ("a_4_2_engine_partial", "А.4.2", FailureMode.THRUST_LEFT_DEGRADED),
    ("a_4_3_engine_out_low", "А.4.3", FailureMode.ENGINE_OUT_LEFT),
)
"""Отказ указан тот, каким он **придёт в телеметрии**. Заклинение стабилизатора (А.3.x) остаётся
`NONE`: `FaultLeftStab`/`FaultRightStab` в ICD есть, но нашей модели отказов такой режим не
описывает — он меняет балансировку планера, а не эффективность нашего органа, и парируется тем же
контуром тангажа."""

APPROACH_MATRIX_DRAFTS = tuple(
    _matrix_draft(DEFAULT, name, code, failure=failure, approach=name)
    for name, code, failure in _APPROACH_MATRIX
)

MATRIX_DRAFTS = (
    *APPROACH_MATRIX_DRAFTS,
    B_1_1_ROLLOUT, B_1_2_TAXI,
    B_2_1_NWS_STUCK_NEUTRAL, B_2_2_NWS_STUCK_OFFSET, B_2_3_NWS_LIMITED,
    B_3_1_REVERSE_LEFT_FAIL, B_3_2_REVERSE_ASYMMETRIC, B_3_3_RESIDUAL_THRUST,
    B_4_1_THROUGH, B_4_2_THROUGH_ENGINE_OUT,
)

SCENARIOS = {
    s.name: s for s in (
        DEFAULT, NWS_FAIL, LEFT_REVERSE_FAIL, RIGHT_REVERSE_FAIL,
        RIGHT_WIND, FWD_WIND, WET_RWY, PUDDLY_RWY, ICY_RWY,
        *MATRIX_DRAFTS,
    )
}
