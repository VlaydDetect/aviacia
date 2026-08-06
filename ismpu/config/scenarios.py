"""Единая профильная модель сценариев всего интервала полёта.

`Scenario` — единственный публичный описатель сценария. Он связывает условия участков с
независимыми настройками управления МС-21 и A330; отдельного `ScenarioConfig` и производного
реестра готовых пресетов больше нет.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING, Any

from ismpu.control.trajectory import VelocityLaw
from ismpu.control.failures import FailureMode
from ismpu.config.aircraft_profiles import A330_300, MC21, AircraftProfile
from ismpu.config.approach import (
    ApproachConfig,
    ICS_CLEAR_WEATHER_APPROACH,
)
from ismpu.config.constants import INITIAL_SPEED_KTS
from ismpu.config.runway import RWY_HEADING_TRUE
from ismpu.config.segments import FlightSegment
from ismpu.envs.weather import WeatherState, WEATHER_PRESETS
from ismpu.envs.weather import decompose_wind

if TYPE_CHECKING:
    from ismpu.config.run_matrix import MatrixCase
    from ismpu.control.pid import PIDController
    from ismpu.control.system import ControllingSystem
    from ismpu.envs.ics_sim import Telemetry

PidConfig = dict[str, Any]


@dataclass(frozen=True)
class GroundControlConfig:
    """Пять PID пробега/руления и статические параметры наземного закона."""

    runway_center: PidConfig
    brake_l: PidConfig
    brake_r: PidConfig
    rev_l: PidConfig
    rev_r: PidConfig
    lookahead_min: float = 10.0
    lookahead_gain: float = 1.8
    xte_gain: float = 2.0
    steering_brake_gain: float = 0.4
    steering_rev_gain: float = 0.0
    law: VelocityLaw = VelocityLaw.GAUSS_BELL

    def build_pids(self) -> dict[str, "PIDController"]:
        from ismpu.factories.control import build_pids
        return build_pids(self)

    def apply(self, controller: "ControllingSystem") -> "ControllingSystem":
        from ismpu.factories.control import apply_ground_control
        return apply_ground_control(self, controller)


@dataclass(frozen=True)
class _GroundPresetSpec:
    """Внутренняя форма переноса прежних литералов; наружу выдаётся только `Scenario`."""

    name: str
    failure: FailureMode
    runway_center: PidConfig
    brake_l: PidConfig
    brake_r: PidConfig
    rev_l: PidConfig
    rev_r: PidConfig
    weather: WeatherState = field(default_factory=lambda: WEATHER_PRESETS["clear_dry"])
    lookahead_min: float = 10.0
    lookahead_gain: float = 1.8
    xte_gain: float = 2.0
    steering_brake_gain: float = 0.4
    steering_rev_gain: float = 0.0
    law: VelocityLaw = VelocityLaw.GAUSS_BELL
    draft: bool = False  # True = черновой наземный пресет, требует калибровки
    matrix_code: str = ""
    """Шифр матрицы прогонов (`config.run_matrix`), если пресет заведён под неё."""

    def ground(self) -> GroundControlConfig:
        return GroundControlConfig(
            runway_center=dict(self.runway_center), brake_l=dict(self.brake_l),
            brake_r=dict(self.brake_r), rev_l=dict(self.rev_l), rev_r=dict(self.rev_r),
            lookahead_min=self.lookahead_min, lookahead_gain=self.lookahead_gain,
            xte_gain=self.xte_gain, steering_brake_gain=self.steering_brake_gain,
            steering_rev_gain=self.steering_rev_gain, law=self.law,
        )


_DEFAULT_SPEC = _GroundPresetSpec(
    name="default",
    failure=FailureMode.NONE,
    runway_center=dict(kp=0.0015, ki=0.0001, kd=0.065, min_out=-1, max_out=1, integral_decay=0.5, name="Runway_Center"),
    brake_l=dict(kp=0.1, ki=0.01, kd=0.05, min_out=0.0, max_out=1.0, name="Brake_L"),
    brake_r=dict(kp=0.1, ki=0.01, kd=0.05, min_out=0.0, max_out=1.0, name="Brake_R"),
    rev_l=dict(kp=0.03, ki=0.002, kd=0.01, min_out=-1.0, max_out=0.0, name="Rev_L"),
    rev_r=dict(kp=0.03, ki=0.002, kd=0.01, min_out=-1.0, max_out=0.0, name="Rev_R"),
    lookahead_min=10.0, lookahead_gain=1.8, xte_gain=2.0, steering_brake_gain=0.4,
)

_NWS_FAIL_SPEC = _GroundPresetSpec(
    name="nws_fail",
    failure=FailureMode.NWS_FAIL,
    runway_center=dict(kp=0.0015, ki=0.0001, kd=0.065, min_out=-1, max_out=1, integral_decay=0.5, name="Runway_Center"),
    brake_l=dict(kp=0.12, ki=0.002, kd=0.11, min_out=0.0, max_out=1.0, integral_decay=0.5, der_filter_tf=0.1, anti_windup=5, name="Brake_L"),
    brake_r=dict(kp=0.12, ki=0.002, kd=0.11, min_out=0.0, max_out=1.0, integral_decay=0.5, der_filter_tf=0.1, anti_windup=5, name="Brake_R"),
    rev_l=dict(kp=0.12, ki=0.0065, kd=0.1, min_out=-1.0, max_out=0.0, integral_decay=0.7, name="Rev_L"),
    rev_r=dict(kp=0.12, ki=0.0065, kd=0.1, min_out=-1.0, max_out=0.0, integral_decay=0.7, name="Rev_R"),
    lookahead_min=10.0, lookahead_gain=1.2, xte_gain=0.8, steering_brake_gain=0.75, steering_rev_gain=0.5,
)

_LEFT_REVERSE_FAIL_SPEC = _GroundPresetSpec(
    name="left_reverse_fail",
    failure=FailureMode.REVERSE_LEFT_FAIL,
    runway_center=dict(kp=0.0004, ki=0.0006, kd=0.07, min_out=-1, max_out=1, integral_decay=0.15, name="Runway_Center"),
    brake_l=dict(kp=0.1, ki=0.01, kd=0.05, min_out=0.0, max_out=1.0, name="Brake_L"),
    brake_r=dict(kp=0.08, ki=0.015, kd=0.06, min_out=0.0, max_out=1.0, name="Brake_R"),
    rev_l=dict(kp=0.03, ki=0.0025, kd=0.02, min_out=-1.0, max_out=0.0, name="Rev_L"),
    rev_r=dict(kp=0.03, ki=0.0025, kd=0.02, min_out=-1.0, max_out=0.0, name="Rev_R"),
    lookahead_min=10.0, lookahead_gain=1.6, xte_gain=2.0, steering_brake_gain=0.4,
)

_RIGHT_REVERSE_FAIL_SPEC = _GroundPresetSpec(
    name="right_reverse_fail",
    failure=FailureMode.REVERSE_RIGHT_FAIL,
    runway_center=dict(kp=0.0004, ki=0.0006, kd=0.07, min_out=-1, max_out=1, integral_decay=0.15, name="Runway_Center"),
    brake_l=dict(kp=0.08, ki=0.015, kd=0.06, min_out=0.0, max_out=1.0, name="Brake_L"),
    brake_r=dict(kp=0.1, ki=0.01, kd=0.05, min_out=0.0, max_out=1.0, name="Brake_R"),
    rev_l=dict(kp=0.03, ki=0.0025, kd=0.02, min_out=-1.0, max_out=0.0, name="Rev_L"),
    rev_r=dict(kp=0.03, ki=0.0025, kd=0.02, min_out=-1.0, max_out=0.0, name="Rev_R"),
    lookahead_min=10.0, lookahead_gain=1.6, xte_gain=2.0, steering_brake_gain=0.4,
)

_RIGHT_WIND_SPEC = _GroundPresetSpec(
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

_FWD_WIND_SPEC = _GroundPresetSpec(
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

_WET_RWY_SPEC = _GroundPresetSpec(
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

_PUDDLY_RWY_SPEC = _GroundPresetSpec(
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

_ICY_RWY_SPEC = _GroundPresetSpec(
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

def _matrix_draft(base: _GroundPresetSpec, name: str, code: str, *,
                  failure: FailureMode | None = None,
                  **overrides) -> _GroundPresetSpec:
    """Черновик под шифр матрицы на базе откалиброванного пресета.

    Словари коэффициентов копируются: spec заморожен, но сами словари — нет, и
    общий словарь на два пресета означал бы, что настройка одного молча меняет другой.
    """
    spec = dict(
        name=name, matrix_code=code, draft=True,
        failure=base.failure if failure is None else failure,
        runway_center=dict(base.runway_center), brake_l=dict(base.brake_l),
        brake_r=dict(base.brake_r), rev_l=dict(base.rev_l), rev_r=dict(base.rev_r),
    )
    spec.update(overrides)
    return replace(base, **spec)


B_1_1_ROLLOUT = _matrix_draft(_DEFAULT_SPEC, "b_1_1_rollout", "Б.1.1")
"""Штатный пробег от касания до полной остановки. Критерий — ось ВПП ± 3 м (ТЗ 5.1.3.1)."""

B_1_2_TAXI = _matrix_draft(
    _DEFAULT_SPEC, "b_1_2_taxi", "Б.1.2",
    lookahead_min=5.0, lookahead_gain=1.2, xte_gain=3.0)
"""Руление по прямому участку. Допуск втрое жёстче пробега (± 1 м), а скорости втрое ниже,
поэтому упреждение укорочено, а реакция на боковое смещение усилена — это отправная точка
настройки, а не результат."""

B_2_1_NWS_STUCK_NEUTRAL = _matrix_draft(_NWS_FAIL_SPEC, "b_2_1_nws_stuck_neutral", "Б.2.1")
"""Заедание носовой стойки в нейтрали. Ближайший откалиброванный родитель — `nws_fail`:
у него удержание оси уже перенесено на дифференциальное торможение и асимметричную тягу."""

B_2_2_NWS_STUCK_OFFSET = _matrix_draft(
    _NWS_FAIL_SPEC, "b_2_2_nws_stuck_offset", "Б.2.2",
    steering_brake_gain=0.9, steering_rev_gain=0.6)
"""Заедание с уводом (+5°). Хуже нейтрали: стойка не просто бездействует, а постоянно тянет с
полосы, и парировать это приходится тормозами и тягой непрерывно, а не эпизодически."""

B_2_3_NWS_LIMITED = _matrix_draft(_NWS_FAIL_SPEC, "b_2_3_nws_limited", "Б.2.3")
"""Ограничение диапазона до ± 3°. Смешанное управление: стойка ещё живая, но её авторитета не
хватает. Заводится от `nws_fail`, хотя по смыслу лежит между ним и штатным пробегом."""

B_3_1_REVERSE_LEFT_FAIL = _matrix_draft(_LEFT_REVERSE_FAIL_SPEC, "b_3_1_reverse_left_fail", "Б.3.1")
"""Отказ реверса левого двигателя."""

B_3_2_REVERSE_ASYMMETRIC = _matrix_draft(_LEFT_REVERSE_FAIL_SPEC, "b_3_2_reverse_asymmetric", "Б.3.2")
"""Несимметричное включение реверса (левый с задержкой 3 с). По телеметрии неотличим от Б.3.1 —
выбирается только по имени."""

B_3_3_RESIDUAL_THRUST = _matrix_draft(
    _LEFT_REVERSE_FAIL_SPEC, "b_3_3_residual_thrust", "Б.3.3",
    failure=FailureMode.THRUST_LEFT_DEGRADED)
"""Остаточная прямая тяга ~30 % на левом. Отличается от отказа реверса знаком возмущения: не
«нечем тормозить слева», а «слева подталкивает вперёд»."""

B_4_1_THROUGH = _matrix_draft(_DEFAULT_SPEC, "b_4_1_through", "Б.4.1")
"""Сквозной прогон без отказов: глиссада → касание → пробег. Критерий добавляет то, чего нет ни
у одного участка по отдельности — отсутствие скачка управляющих воздействий на стыке."""

B_4_2_THROUGH_ENGINE_OUT = _matrix_draft(
    _LEFT_REVERSE_FAIL_SPEC, "b_4_2_through_engine_out", "Б.4.2")
"""Сквозной, худший случай: отказ левого двигателя на глиссаде + отказ его реверса на пробеге."""


GROUND_MATRIX_DRAFTS = (
    B_1_1_ROLLOUT, B_1_2_TAXI,
    B_2_1_NWS_STUCK_NEUTRAL, B_2_2_NWS_STUCK_OFFSET, B_2_3_NWS_LIMITED,
    B_3_1_REVERSE_LEFT_FAIL, B_3_2_REVERSE_ASYMMETRIC, B_3_3_RESIDUAL_THRUST,
    B_4_1_THROUGH, B_4_2_THROUGH_ENGINE_OUT,
)


@dataclass(frozen=True)
class ApproachSetup:
    """Начальные условия захода X-Plane на продолжении оси и глиссады."""

    radio_altitude_ft: float = 2800.0
    ias_knots: float = 150.0
    vertical_speed_fpm: float = -750.0
    glideslope_deg: float = 3.0
    flap_ratio: float = 0.75
    lateral_offset_m: float = 0.0
    heading_offset_deg: float = 0.0
    loc_offset_dots: float = 0.0
    gs_offset_dots: float = 0.0


@dataclass(frozen=True)
class TouchdownSetup:
    """Начальные условия быстрого старта непосредственно с пробега."""

    speed_knots: float = INITIAL_SPEED_KTS
    descent_rate_fpm: float = 0.0
    pitch_deg: float = 0.0
    lateral_offset_m: float = 0.0
    heading_offset_deg: float = 0.0
    elevation_m: float = 1.5


@dataclass(frozen=True)
class SensorNoise:
    pos_sigma_m: float = 0.0
    heading_sigma_deg: float = 0.0
    speed_sigma_ms: float = 0.0
    dropout_prob: float = 0.0


@dataclass(frozen=True)
class SegmentConditions:
    """Ожидаемые физические условия одного участка."""

    weather: WeatherState = field(default_factory=lambda: WEATHER_PRESETS["clear_dry"])
    failures: frozenset[FailureMode] = frozenset()


@dataclass(frozen=True)
class ConditionMatch:
    """Сверка ожидаемых условий с фактической телеметрией backend."""

    segment: FlightSegment
    missing_failures: frozenset[FailureMode]
    unexpected_failures: frozenset[FailureMode]
    weather_distance: float

    @property
    def failures_match(self) -> bool:
        return not self.missing_failures and not self.unexpected_failures

    @property
    def exact(self) -> bool:
        return self.failures_match and self.weather_distance <= 1e-3


@dataclass(frozen=True)
class AircraftControlSet:
    """Настройки всех участков одного профиля ЛА."""

    approach: ApproachConfig
    rollout: GroundControlConfig
    taxi: GroundControlConfig
    draft_segments: frozenset[FlightSegment] = frozenset()

    def for_segment(self, segment: FlightSegment) -> ApproachConfig | GroundControlConfig:
        if segment is FlightSegment.APPROACH:
            return self.approach
        if segment is FlightSegment.ROLLOUT:
            return self.rollout
        if segment is FlightSegment.TAXI:
            return self.taxi
        raise ValueError(f"неподдерживаемый участок {segment!r}")


def _profile_name(profile: AircraftProfile | str) -> str:
    return profile.name if isinstance(profile, AircraftProfile) else str(profile).lower()


@dataclass(frozen=True)
class Scenario:
    """Полный профильный сценарий APPROACH → ROLLOUT → TAXI."""

    scenario_id: str
    seed: int
    aircraft_controls: Mapping[str, AircraftControlSet]
    conditions: Mapping[FlightSegment, SegmentConditions]
    approach: ApproachSetup = field(default_factory=ApproachSetup)
    touchdown: TouchdownSetup = field(default_factory=TouchdownSetup)
    sensor_noise: SensorNoise = field(default_factory=SensorNoise)
    matrix_codes: Mapping[FlightSegment, str] = field(default_factory=dict)
    provenance: Mapping[FlightSegment, str] = field(default_factory=dict)

    @property
    def name(self) -> str:
        return self.scenario_id

    def control_for(
        self, profile: AircraftProfile | str, segment: FlightSegment,
    ) -> ApproachConfig | GroundControlConfig:
        name = _profile_name(profile)
        try:
            controls = self.aircraft_controls[name]
        except KeyError as exc:
            known = ", ".join(sorted(self.aircraft_controls))
            raise KeyError(
                f"сценарий {self.scenario_id!r} не содержит профиль {name!r}; доступны: {known}"
            ) from exc
        return controls.for_segment(segment)

    def conditions_for(self, segment: FlightSegment) -> SegmentConditions:
        try:
            return self.conditions[segment]
        except KeyError as exc:
            raise KeyError(
                f"сценарий {self.scenario_id!r} не содержит участок {segment.value!r}"
            ) from exc

    def is_draft(self, profile: AircraftProfile | str, segment: FlightSegment) -> bool:
        name = _profile_name(profile)
        try:
            return segment in self.aircraft_controls[name].draft_segments
        except KeyError as exc:
            raise KeyError(f"в сценарии нет профиля {name!r}") from exc

    def apply_control(
        self,
        controller: "ControllingSystem",
        profile: AircraftProfile | str,
        segment: FlightSegment = FlightSegment.ROLLOUT,
    ) -> "ControllingSystem":
        control = self.control_for(profile, segment)
        if segment is FlightSegment.APPROACH:
            controller.setup_approach(control)
        else:
            control.apply(controller)
        controller.failures.sync(self.conditions_for(segment).failures)
        return controller

    @property
    def weather(self) -> WeatherState:
        """Условия пробега для report/eval-кода, работающего только на земле."""
        return self.conditions_for(FlightSegment.ROLLOUT).weather

    @property
    def failures(self) -> tuple[FailureMode, ...]:
        return tuple(sorted(
            self.conditions_for(FlightSegment.ROLLOUT).failures, key=lambda f: f.value))

    @property
    def primary_failure(self) -> FailureMode:
        return self.failures[0] if self.failures else FailureMode.NONE

    @property
    def matrix_code(self) -> str:
        codes = tuple(dict.fromkeys(c for c in self.matrix_codes.values() if c))
        return codes[0] if len(codes) == 1 else "+".join(codes)

    def to_dict(self) -> dict[str, Any]:
        """Serialize only the canonical profile-aware schema v2."""
        from ismpu.config.json_config import scenario_to_document

        return scenario_to_document(self)

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
        *,
        legacy_aircraft_profile: str = "mc21",
    ) -> "Scenario":
        from ismpu.config.json_config import scenario_from_document

        return scenario_from_document(
            data, legacy_aircraft_profile=legacy_aircraft_profile)

    @classmethod
    def from_preset(
        cls,
        name: str,
        *,
        weather: WeatherState | None = None,
        failures: Iterable[FailureMode] | None = None,
        approach: ApproachSetup | None = None,
        touchdown: TouchdownSetup | None = None,
        sensor_noise: SensorNoise | None = None,
        scenario_id: str | None = None,
        seed: int = 0,
    ) -> "Scenario":
        base = SCENARIOS[name]
        conditions = dict(base.conditions)
        if weather is not None or failures is not None:
            for segment in FlightSegment:
                current = conditions[segment]
                conditions[segment] = SegmentConditions(
                    weather=weather or current.weather,
                    failures=(frozenset(failures) if failures is not None else current.failures),
                )
        return replace(
            base,
            scenario_id=scenario_id or name,
            seed=seed,
            conditions=conditions,
            approach=approach or base.approach,
            touchdown=touchdown or base.touchdown,
            sensor_noise=sensor_noise or base.sensor_noise,
        )


def _copy_ground(config: GroundControlConfig) -> GroundControlConfig:
    return replace(
        config,
        runway_center=dict(config.runway_center), brake_l=dict(config.brake_l),
        brake_r=dict(config.brake_r), rev_l=dict(config.rev_l), rev_r=dict(config.rev_r),
    )


def _copy_approach(config: ApproachConfig, *, name: str, draft: bool) -> ApproachConfig:
    return replace(
        config, name=name, draft=draft,
        roll_pid=dict(config.roll_pid), pitch_pid=dict(config.pitch_pid),
        speed_pid=dict(config.speed_pid),
    )


_A330_APPROACH_DRAFT = _copy_approach(
    ICS_CLEAR_WEATHER_APPROACH, name="xplane_a330_approach", draft=True)
"""The existing X-Plane A330 airborne law, deliberately draft until live acceptance."""


def _ground_segments_for_spec(spec: _GroundPresetSpec) -> tuple[FlightSegment, ...]:
    if spec.name == "b_1_2_taxi":
        return (FlightSegment.TAXI,)
    if spec.name.startswith("b_"):
        return (FlightSegment.ROLLOUT,)
    return (FlightSegment.ROLLOUT, FlightSegment.TAXI)


def _scenario_from_ground_spec(spec: _GroundPresetSpec) -> Scenario:
    """Полный сценарий с наземной веткой `spec` и рабочим воздушным законом ICS."""
    affected = _ground_segments_for_spec(spec)
    default_ground = _DEFAULT_SPEC.ground()
    own_ground = spec.ground()
    rollout_ground = own_ground if FlightSegment.ROLLOUT in affected else default_ground
    taxi_ground = own_ground if FlightSegment.TAXI in affected else _copy_ground(rollout_ground)

    mc21_drafts = frozenset(affected if spec.draft else ())
    a330_drafts = mc21_drafts | {FlightSegment.APPROACH}
    controls = {
        MC21.name: AircraftControlSet(
            approach=_copy_approach(
                ICS_CLEAR_WEATHER_APPROACH,
                name=ICS_CLEAR_WEATHER_APPROACH.name,
                draft=False,
            ),
            rollout=_copy_ground(rollout_ground), taxi=_copy_ground(taxi_ground),
            draft_segments=frozenset(mc21_drafts),
        ),
        A330_300.name: AircraftControlSet(
            approach=_copy_approach(
                _A330_APPROACH_DRAFT,
                name=_A330_APPROACH_DRAFT.name,
                draft=True,
            ),
            rollout=_copy_ground(rollout_ground), taxi=_copy_ground(taxi_ground),
            draft_segments=frozenset(a330_drafts),
        ),
    }

    standard = SegmentConditions(weather=spec.weather)
    conditions = {segment: standard for segment in FlightSegment}
    failure_set = frozenset(() if spec.failure is FailureMode.NONE else (spec.failure,))
    for segment in affected:
        conditions[segment] = SegmentConditions(weather=spec.weather, failures=failure_set)
    if spec.name == "b_4_2_through_engine_out":
        conditions[FlightSegment.ROLLOUT] = SegmentConditions(
            weather=spec.weather,
            failures=frozenset({FailureMode.ENGINE_OUT_LEFT, FailureMode.REVERSE_LEFT_FAIL}),
        )
    matrix_codes = {segment: spec.matrix_code for segment in affected if spec.matrix_code}
    return Scenario(
        scenario_id=spec.name,
        seed=0,
        aircraft_controls=controls,
        conditions=conditions,
        matrix_codes=matrix_codes,
        provenance={segment: spec.name for segment in FlightSegment},
    )


_SPECS = (
    _DEFAULT_SPEC, _NWS_FAIL_SPEC, _LEFT_REVERSE_FAIL_SPEC, _RIGHT_REVERSE_FAIL_SPEC,
    _RIGHT_WIND_SPEC, _FWD_WIND_SPEC, _WET_RWY_SPEC, _PUDDLY_RWY_SPEC, _ICY_RWY_SPEC,
    *GROUND_MATRIX_DRAFTS,
)

SCENARIOS: dict[str, Scenario] = {
    spec.name: _scenario_from_ground_spec(spec) for spec in _SPECS
}


def _install_approach_scenarios() -> None:
    """Лист А: один рабочий ICS-пресет, разные условия и матричные шифры."""
    from ismpu.config.run_matrix import APPROACH_CASES

    base = SCENARIOS["default"]
    for case in APPROACH_CASES:
        controls = {
            profile: AircraftControlSet(
                approach=_copy_approach(
                    control.approach,
                    name=control.approach.name,
                    draft=control.approach.draft,
                ),
                rollout=_copy_ground(control.rollout),
                taxi=_copy_ground(control.taxi),
                draft_segments=control.draft_segments,
            )
            for profile, control in base.aircraft_controls.items()
        }
        conditions_for_case = SegmentConditions(
            weather=WEATHER_PRESETS["clear_dry"],
            failures=frozenset(case.bench_faults),
        )
        # Отказ, введённый на заходе, физически сохраняется после касания.
        conditions = {segment: conditions_for_case for segment in FlightSegment}
        provenance = dict(base.provenance)
        provenance[FlightSegment.APPROACH] = case.preset
        SCENARIOS[case.preset] = replace(
            base,
            scenario_id=case.preset,
            aircraft_controls=controls,
            conditions=conditions,
            matrix_codes={FlightSegment.APPROACH: case.code},
            provenance=provenance,
        )


_install_approach_scenarios()

DEFAULT = SCENARIOS["default"]
NWS_FAIL = SCENARIOS["nws_fail"]
LEFT_REVERSE_FAIL = SCENARIOS["left_reverse_fail"]
RIGHT_REVERSE_FAIL = SCENARIOS["right_reverse_fail"]


def resolve_scenario(key: str) -> Scenario:
    """Сценарий по имени либо шифру матрицы, без различия раскладки А/B."""
    if key in SCENARIOS:
        return SCENARIOS[key]
    normalized = key.strip().upper().replace("A", "А").replace("B", "Б")
    for scenario in SCENARIOS.values():
        if any(code.upper() == normalized for code in scenario.matrix_codes.values()):
            return scenario
    raise KeyError(
        f"неизвестный сценарий или шифр матрицы: {key!r}. Известны: "
        f"{', '.join(sorted(SCENARIOS))}")


def compose_scenario(
    scenario_id: str,
    *,
    approach: str | Scenario,
    rollout: str | Scenario,
    taxi: str | Scenario | None = None,
    seed: int = 0,
) -> Scenario:
    """Собрать сценарий из независимых источников участков."""
    sources = {
        FlightSegment.APPROACH: resolve_scenario(approach) if isinstance(approach, str) else approach,
        FlightSegment.ROLLOUT: resolve_scenario(rollout) if isinstance(rollout, str) else rollout,
    }
    sources[FlightSegment.TAXI] = (
        sources[FlightSegment.ROLLOUT]
        if taxi is None else resolve_scenario(taxi) if isinstance(taxi, str) else taxi)
    profiles = set.intersection(*(set(source.aircraft_controls) for source in sources.values()))
    if not profiles:
        raise ValueError("у частей составного сценария нет общего AircraftProfile")
    controls: dict[str, AircraftControlSet] = {}
    for profile in sorted(profiles):
        by_segment = {
            segment: source.aircraft_controls[profile] for segment, source in sources.items()
        }
        drafts = frozenset(
            segment for segment, source_controls in by_segment.items()
            if segment in source_controls.draft_segments)
        controls[profile] = AircraftControlSet(
            approach=by_segment[FlightSegment.APPROACH].approach,
            rollout=by_segment[FlightSegment.ROLLOUT].rollout,
            taxi=by_segment[FlightSegment.TAXI].taxi,
            draft_segments=drafts,
        )
    return Scenario(
        scenario_id=scenario_id,
        seed=seed,
        aircraft_controls=controls,
        conditions={segment: source.conditions_for(segment) for segment, source in sources.items()},
        approach=sources[FlightSegment.APPROACH].approach,
        touchdown=sources[FlightSegment.ROLLOUT].touchdown,
        sensor_noise=sources[FlightSegment.APPROACH].sensor_noise,
        matrix_codes={
            segment: source.matrix_codes[segment]
            for segment, source in sources.items() if segment in source.matrix_codes
        },
        provenance={segment: source.scenario_id for segment, source in sources.items()},
    )


def compose_matrix_scenario(
    scenario_id: str,
    *,
    approach_case: "str | MatrixCase",
    ground_case: "str | MatrixCase",
    seed: int = 0,
) -> Scenario:
    """Объединить случай листа А и случай листа Б в один полный сценарий.

    Аргументы принимают как шифры (`А.1.2`, `Б.1.1`), так и имена из поля
    `MatrixCase.preset`. Все варианты листа А используют единственный рабочий
    `ICS_CLEAR_WEATHER_APPROACH`; матрица задаёт условия, а не копии PID.
    """
    from ismpu.config.run_matrix import APPROACH_CASES, GROUND_CASES

    def find_case(key: "str | MatrixCase", cases, sheet: str):
        if not isinstance(key, str):
            if key in cases:
                return key
            raise KeyError(f"случай {key!r} не относится к листу {sheet}")
        normalized = key.strip().upper().replace("A", "А").replace("B", "Б")
        for case in cases:
            if case.preset == key or case.code.upper() == normalized:
                return case
        raise KeyError(f"в листе {sheet} нет случая {key!r}")

    approach = find_case(approach_case, APPROACH_CASES, "А")
    ground = find_case(ground_case, GROUND_CASES, "Б")
    if ground.segment == "taxi":
        rollout_source: str | Scenario = "default"
        taxi_source: str | Scenario | None = ground.preset
    else:
        rollout_source = ground.preset
        taxi_source = None
    scenario = compose_scenario(
        scenario_id,
        approach=approach.preset,
        rollout=rollout_source,
        taxi=taxi_source,
        seed=seed,
    )
    # Отказы листа А не чинятся сами в момент касания. Переносим их на землю;
    # frozenset одновременно убирает повтор, если лист Б содержит тот же отказ.
    persistent = scenario.conditions_for(FlightSegment.APPROACH).failures
    conditions = dict(scenario.conditions)
    for segment in (FlightSegment.ROLLOUT, FlightSegment.TAXI):
        current = conditions[segment]
        conditions[segment] = replace(
            current, failures=current.failures | persistent)
    return replace(scenario, conditions=conditions)


def _install_through_scenarios() -> None:
    """Собрать штатные сквозные случаи Б.4 из реальных источников листов А и Б."""
    sources = {
        "b_4_1_through": "А.1.2",
        "b_4_2_through_engine_out": "А.4.1",
    }
    for scenario_id, approach_code in sources.items():
        rollout_source = SCENARIOS[scenario_id]
        scenario = compose_matrix_scenario(
            scenario_id,
            approach_case=approach_code,
            ground_case=rollout_source.matrix_code,
            seed=rollout_source.seed,
        )
        code = rollout_source.matrix_code
        SCENARIOS[scenario_id] = replace(scenario, matrix_codes={
            FlightSegment.APPROACH: code,
            FlightSegment.ROLLOUT: code,
        })


_install_through_scenarios()


FAILURE_MISMATCH_PENALTY = 100.0
_FRICTION_SCALE = 15.0
_WIND_SCALE = 20.0
_VISIBILITY_SCALE = 30100.0


def weather_distance(
    a: WeatherState, b: WeatherState, runway_heading_degt: float = RWY_HEADING_TRUE,
) -> float:
    cross_a, head_a = decompose_wind(
        a.wind_speed_kts, a.wind_dir_from_degt, runway_heading_degt)
    cross_b, head_b = decompose_wind(
        b.wind_speed_kts, b.wind_dir_from_degt, runway_heading_degt)

    runway_friction_dist = abs(a.runway_friction - b.runway_friction) / _FRICTION_SCALE
    cross_wind_dist = abs(cross_a - cross_b) / _WIND_SCALE
    head_wind_dist = 0.5 * abs(head_a - head_b) / _WIND_SCALE
    rain_pct_dist = abs(a.rain_pct - b.rain_pct)
    visibility_dist = 0.5 * abs(a.visibility_m - b.visibility_m) / _VISIBILITY_SCALE

    return (
        runway_friction_dist
        + cross_wind_dist
        + head_wind_dist
        + rain_pct_dist
        + visibility_dist
    )


def match_conditions(
    expected: SegmentConditions,
    failures: Iterable[FailureMode],
    weather: WeatherState,
    segment: FlightSegment,
) -> ConditionMatch:
    actual = frozenset(failures)
    return ConditionMatch(
        segment=segment,
        missing_failures=expected.failures - actual,
        unexpected_failures=actual - expected.failures,
        weather_distance=weather_distance(expected.weather, weather),
    )


def scenario_distance(
    scenario: Scenario,
    failures: Iterable[FailureMode],
    weather: WeatherState | None = None,
    *,
    segment: FlightSegment = FlightSegment.ROLLOUT,
) -> float:
    expected = scenario.conditions_for(segment)
    mismatch = frozenset(failures).symmetric_difference(expected.failures)
    score = FAILURE_MISMATCH_PENALTY * len(mismatch)
    if weather is not None:
        score += weather_distance(expected.weather, weather)
    return score


def select_scenario(
    failures: Iterable[FailureMode] = (),
    weather: WeatherState | None = None,
    *,
    aircraft_profile: AircraftProfile | str = MC21,
    segment: FlightSegment = FlightSegment.ROLLOUT,
    scenarios: Sequence[Scenario] | None = None,
    include_draft: bool = False,
) -> Scenario:
    pool = list(scenarios if scenarios is not None else SCENARIOS.values())
    profile = _profile_name(aircraft_profile)
    pool = [scenario for scenario in pool if profile in scenario.aircraft_controls]
    if not include_draft:
        pool = [scenario for scenario in pool if not scenario.is_draft(profile, segment)]
    if not pool:
        admission = "допущенных " if not include_draft else ""
        raise ValueError(
            f"нет {admission}сценариев для профиля {profile!r} "
            f"и участка {segment.value!r}")
    return min(pool, key=lambda scenario: (
        scenario_distance(scenario, failures, weather, segment=segment),
        scenario.scenario_id != "default",
        scenario.scenario_id,
    ))


def select_for_telemetry(
    telemetry: "Telemetry | None",
    *,
    aircraft_profile: AircraftProfile | str = MC21,
    segment: FlightSegment = FlightSegment.ROLLOUT,
    scenarios: Sequence[Scenario] | None = None,
    include_draft: bool = False,
) -> Scenario:
    if telemetry is None or not telemetry.valid:
        return select_scenario(
            aircraft_profile=aircraft_profile,
            segment=segment,
            scenarios=scenarios,
            include_draft=include_draft,
        )
    return select_scenario(
        telemetry.faults, telemetry.weather,
        aircraft_profile=aircraft_profile, segment=segment,
        scenarios=scenarios, include_draft=include_draft,
    )


def matrix_battery(segment: str | None = None) -> tuple[Scenario, ...]:
    from ismpu.config.run_matrix import RUN_MATRIX
    return tuple(
        SCENARIOS[case.preset] for case in RUN_MATRIX
        if case.preset in SCENARIOS and (segment is None or case.segment == segment)
    )
