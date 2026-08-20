"""Единая профильная модель сценариев всего интервала полёта.

`Scenario` — единственный публичный описатель сценария. Он связывает условия участков с
независимыми настройками управления МС-21 и A330; отдельного `ScenarioConfig` и производного
реестра готовых пресетов больше нет.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field, replace
from enum import Enum
from typing import TYPE_CHECKING, Any

from ismpu.control.trajectory import CompletionRule, VelocityLaw
from ismpu.control.failures import FailureMode
from ismpu.config.aircraft_profiles import A330_300, MC21, AircraftProfile
from ismpu.config.approach import (
    ApproachConfig,
    ICS_CLEAR_WEATHER_APPROACH,
)
from ismpu.config.constants import INITIAL_SPEED_KTS
from ismpu.config.runway import RWY_HEADING_TRUE
from ismpu.config.runway_profiles import UUEE_06R
from ismpu.config.segments import FlightSegment
from ismpu.envs.weather import WeatherState, WEATHER_PRESETS
from ismpu.envs.weather import decompose_wind

if TYPE_CHECKING:
    from ismpu.config.run_matrix import MatrixCase, MatrixRun
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
    target_speed_kts: float = 7.5
    braking_distance_m: float = UUEE_06R.length_m
    completion_rule: CompletionRule = CompletionRule.HANDOVER_TAXI
    steering_rate_per_s: float = 1.0
    brake_rate_per_s: float = 1.0
    reverse_rate_per_s: float = 1.0
    failure_yaw_compensation_gain: float = 1.0

    def build_pids(self) -> dict[str, "PIDController"]:
        """Создать новые stateful PID из immutable словарей конфигурации."""
        from ismpu.factories.control import build_pids
        return build_pids(self)

    def apply(self, controller: "ControllingSystem") -> "ControllingSystem":
        """Полностью пересобрать наземные каналы controller этой конфигурацией."""
        from ismpu.factories.control import apply_ground_control
        return apply_ground_control(self, controller)


@dataclass(frozen=True)
class _GroundPresetSpec:
    """Компактный внутренний шаблон наземной ветки; наружу выдаётся только `Scenario`."""

    name: str
    runway_center: PidConfig
    brake_l: PidConfig
    brake_r: PidConfig
    rev_l: PidConfig
    rev_r: PidConfig
    failures: frozenset[FailureMode] = field(default_factory=frozenset)
    weather: WeatherState = field(default_factory=lambda: WEATHER_PRESETS["clear_dry"])
    lookahead_min: float = 10.0
    lookahead_gain: float = 1.8
    xte_gain: float = 2.0
    steering_brake_gain: float = 0.4
    steering_rev_gain: float = 0.0
    law: VelocityLaw = VelocityLaw.GAUSS_BELL
    target_speed_kts: float = 7.5
    braking_distance_m: float = UUEE_06R.length_m
    completion_rule: CompletionRule = CompletionRule.HANDOVER_TAXI
    steering_rate_per_s: float = 1.0
    brake_rate_per_s: float = 1.0
    reverse_rate_per_s: float = 1.0
    failure_yaw_compensation_gain: float = 1.0
    matrix_code: str = ""
    """Шифр матрицы прогонов (`config.run_matrix`), если пресет заведён под неё."""

    def ground(self) -> GroundControlConfig:
        """Материализовать публичную immutable конфигурацию из внутреннего preset spec."""
        return GroundControlConfig(
            runway_center=dict(self.runway_center), brake_l=dict(self.brake_l),
            brake_r=dict(self.brake_r), rev_l=dict(self.rev_l), rev_r=dict(self.rev_r),
            lookahead_min=self.lookahead_min, lookahead_gain=self.lookahead_gain,
            xte_gain=self.xte_gain, steering_brake_gain=self.steering_brake_gain,
            steering_rev_gain=self.steering_rev_gain, law=self.law,
            target_speed_kts=self.target_speed_kts,
            braking_distance_m=self.braking_distance_m,
            completion_rule=self.completion_rule,
            steering_rate_per_s=self.steering_rate_per_s,
            brake_rate_per_s=self.brake_rate_per_s,
            reverse_rate_per_s=self.reverse_rate_per_s,
            failure_yaw_compensation_gain=self.failure_yaw_compensation_gain,
        )


_DEFAULT_SPEC = _GroundPresetSpec(
    name="default",
    runway_center=dict(kp=0.0015, ki=0.0001, kd=0.065, min_out=-1, max_out=1, name="Runway_Center"),
    brake_l=dict(kp=0.1, ki=0.01, kd=0.05, min_out=0.0, max_out=1.0, name="Brake_L"),
    brake_r=dict(kp=0.1, ki=0.01, kd=0.05, min_out=0.0, max_out=1.0, name="Brake_R"),
    rev_l=dict(kp=0.03, ki=0.002, kd=0.01, min_out=-1.0, max_out=0.0, name="Rev_L"),
    rev_r=dict(kp=0.03, ki=0.002, kd=0.01, min_out=-1.0, max_out=0.0, name="Rev_R"),
    lookahead_min=10.0, lookahead_gain=1.8, xte_gain=2.0, steering_brake_gain=0.4,
)

_LEFT_REVERSE_FAIL_SPEC = _GroundPresetSpec(
    name="left_reverse_fail",
    failures=frozenset({FailureMode.REVERSE_LEFT_FAIL}),
    runway_center=dict(kp=0.0004, ki=0.0006, kd=0.07, min_out=-1, max_out=1, name="Runway_Center"),
    brake_l=dict(kp=0.1, ki=0.01, kd=0.05, min_out=0.0, max_out=1.0, name="Brake_L"),
    brake_r=dict(kp=0.08, ki=0.015, kd=0.06, min_out=0.0, max_out=1.0, name="Brake_R"),
    rev_l=dict(kp=0.03, ki=0.0025, kd=0.02, min_out=-1.0, max_out=0.0, name="Rev_L"),
    rev_r=dict(kp=0.03, ki=0.0025, kd=0.02, min_out=-1.0, max_out=0.0, name="Rev_R"),
    lookahead_min=10.0, lookahead_gain=1.6, xte_gain=2.0, steering_brake_gain=0.4,
)

_RIGHT_REVERSE_FAIL_SPEC = _GroundPresetSpec(
    name="right_reverse_fail",
    failures=frozenset({FailureMode.REVERSE_RIGHT_FAIL}),
    runway_center=dict(kp=0.0004, ki=0.0006, kd=0.07, min_out=-1, max_out=1, name="Runway_Center"),
    brake_l=dict(kp=0.08, ki=0.015, kd=0.06, min_out=0.0, max_out=1.0, name="Brake_L"),
    brake_r=dict(kp=0.1, ki=0.01, kd=0.05, min_out=0.0, max_out=1.0, name="Brake_R"),
    rev_l=dict(kp=0.03, ki=0.0025, kd=0.02, min_out=-1.0, max_out=0.0, name="Rev_L"),
    rev_r=dict(kp=0.03, ki=0.0025, kd=0.02, min_out=-1.0, max_out=0.0, name="Rev_R"),
    lookahead_min=10.0, lookahead_gain=1.6, xte_gain=2.0, steering_brake_gain=0.4,
)

# right wind (90 deg) 20 kts
_RIGHT_WIND_SPEC = _GroundPresetSpec(
    name="right_wind",
    weather=WeatherState.from_crosswind(20.0, 0.0),
    runway_center=dict(kp=0.1, ki=0.1, kd=0.3, min_out=-1, max_out=1, anti_windup=10, der_filter_tf=0.2, name="Runway_Center"),
    brake_l=dict(kp=0.1, ki=0.01, kd=0.05, min_out=0.0, max_out=1.0, name="Brake_L"),
    brake_r=dict(kp=0.1, ki=0.01, kd=0.05, min_out=0.0, max_out=1.0, name="Brake_R"),
    rev_l=dict(kp=0.03, ki=0.002, kd=0.01, min_out=-1.0, max_out=0.0, name="Rev_L"),
    rev_r=dict(kp=0.03, ki=0.002, kd=0.01, min_out=-1.0, max_out=0.0, name="Rev_R"),
    lookahead_min=10.0, lookahead_gain=1.7, xte_gain=1.3, steering_brake_gain=0.35, steering_rev_gain=0.53
)

_WET_RWY_SPEC = _GroundPresetSpec(
    name="wet_rwy",
    weather=WEATHER_PRESETS["wet"],
    runway_center=dict(kp=0.12, ki=0.006, kd=0.08, min_out=-1, max_out=1, anti_windup=10, der_filter_tf=0.2, name="Runway_Center"),
    brake_l=dict(kp=0.1, ki=0.01, kd=0.05, min_out=0.0, max_out=1.0, name="Brake_L"),
    brake_r=dict(kp=0.1, ki=0.01, kd=0.05, min_out=0.0, max_out=1.0, name="Brake_R"),
    rev_l=dict(kp=0.03, ki=0.002, kd=0.01, min_out=-1.0, max_out=0.0, name="Rev_L"),
    rev_r=dict(kp=0.03, ki=0.002, kd=0.01, min_out=-1.0, max_out=0.0, name="Rev_R"),
    lookahead_min=10.0, lookahead_gain=1.7, xte_gain=1.9, steering_brake_gain=0.0,
)

_PUDDLY_RWY_SPEC = _GroundPresetSpec(
    name="puddly_rwy",
    weather=WEATHER_PRESETS["puddly"],
    runway_center=dict(kp=0.0015, ki=0.0001, kd=0.065, min_out=-1, max_out=1, name="Runway_Center"),
    brake_l=dict(kp=0.1, ki=0.01, kd=0.05, min_out=0.0, max_out=1.0, name="Brake_L"),
    brake_r=dict(kp=0.1, ki=0.01, kd=0.05, min_out=0.0, max_out=1.0, name="Brake_R"),
    rev_l=dict(kp=0.03, ki=0.002, kd=0.01, min_out=-1.0, max_out=0.0, name="Rev_L"),
    rev_r=dict(kp=0.03, ki=0.002, kd=0.01, min_out=-1.0, max_out=0.0, name="Rev_R"),
    lookahead_min=10.0, lookahead_gain=1.8, xte_gain=2.0, steering_brake_gain=0.4,
)

_ICY_RWY_SPEC = _GroundPresetSpec(
    name="icy_rwy",
    weather=WEATHER_PRESETS["icy"],
    runway_center=dict(kp=0.0015, ki=0.0001, kd=0.065, min_out=-1, max_out=1, name="Runway_Center"),
    brake_l=dict(kp=0.1, ki=0.01, kd=0.05, min_out=0.0, max_out=1.0, name="Brake_L"),
    brake_r=dict(kp=0.1, ki=0.01, kd=0.05, min_out=0.0, max_out=1.0, name="Brake_R"),
    rev_l=dict(kp=0.03, ki=0.002, kd=0.01, min_out=-1.0, max_out=0.0, name="Rev_L"),
    rev_r=dict(kp=0.03, ki=0.002, kd=0.01, min_out=-1.0, max_out=0.0, name="Rev_R"),
    lookahead_min=10.0, lookahead_gain=1.8, xte_gain=2.0, steering_brake_gain=0.4,
)

def _matrix_draft(
    base: _GroundPresetSpec,
    name: str,
    code: str,
    *,
    failures: frozenset[FailureMode],
    **overrides,
) -> _GroundPresetSpec:
    """Скопировать ближайший рабочий набор PID для одного шифра листа Б.

    Матрица определяет имена, отказы и число строк. Здесь остаются только инженерно
    значимые стартовые исключения для руления и постоянного увода NWS. Словари PID
    обязательно копируются, чтобы настройка одного шифра не меняла соседний.
    """
    spec = dict(
        name=name, matrix_code=code,
        failures=failures,
        runway_center=dict(base.runway_center), brake_l=dict(base.brake_l),
        brake_r=dict(base.brake_r), rev_l=dict(base.rev_l), rev_r=dict(base.rev_r),
    )
    if code == "Б.1.2":
        spec.update(target_speed_kts=15.0, completion_rule=CompletionRule.OPERATOR)
    else:
        spec.update(target_speed_kts=0.0, completion_rule=CompletionRule.FULL_STOP)
    spec.update(overrides)
    return replace(base, **spec)


def _ground_matrix_drafts() -> tuple[_GroundPresetSpec, ...]:
    """Построить десять черновиков непосредственно из versioned JSON-каталога."""
    from ismpu.config.run_matrix import GROUND_CASES

    exceptions = {
        "Б.1.2": {"lookahead_min": 5.0, "lookahead_gain": 1.2, "xte_gain": 3.0},
        "Б.2.2": {"steering_brake_gain": 0.9, "steering_rev_gain": 0.6},
    }
    drafts = []
    for case in GROUND_CASES:
        failures = frozenset(case.bench_faults)
        if FailureMode.NWS_FAIL in failures:
            # normal working with NWS fail
            base = _DEFAULT_SPEC
        elif failures:
            # Все текущие не-NWS строки Б возмущают левый канал тяги/реверса.
            base = _LEFT_REVERSE_FAIL_SPEC
        else:
            base = _DEFAULT_SPEC
        drafts.append(_matrix_draft(
            base,
            case.preset,
            case.code,
            failures=failures,
            **exceptions.get(case.code, {}),
        ))
    return tuple(drafts)


GROUND_MATRIX_DRAFTS = _ground_matrix_drafts()


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
    """Детерминированно seeded шум/пропуски, применяемые только resettable backend."""

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
    matrix_run_id: str | None = None
    matrix_code: str | None = None

    @property
    def failures_match(self) -> bool:
        """Истина, если набор фактических отказов совпал ровно."""
        return not self.missing_failures and not self.unexpected_failures

    @property
    def weather_matches(self) -> bool:
        """Истина при практически нулевой нормированной дистанции погоды."""
        return self.weather_distance <= 1e-3

    @property
    def acceptance_valid(self) -> bool:
        """Погода остаётся отчётной; неверный отказ делает прогон недопустимым."""
        return self.failures_match

class ProfileStatus(str, Enum):
    """Admission status одной aircraft/segment конфигурации."""

    DRAFT = "draft"
    TUNED = "tuned"
    ACCEPTED = "accepted"


def _materialize_override(config, patch: Mapping[str, Any]):
    """Применить одноуровневый sparse patch и вернуть полный неизменяемый config."""
    changes = {
        name: dict(value)
        for name, value in vars(config).items()
        if isinstance(value, Mapping)
    }
    for name, value in patch.items():
        if not hasattr(config, name):
            raise ValueError(f"неизвестное поле override {name!r}")
        current = getattr(config, name)
        if isinstance(current, Mapping) and isinstance(value, Mapping):
            changes[name] = {**current, **value}
        elif isinstance(current, Enum) and not isinstance(value, type(current)):
            changes[name] = (
                type(current)[value] if isinstance(value, str) and value in type(current).__members__
                else type(current)(value)
            )
        else:
            changes[name] = value
    return replace(config, **changes)


@dataclass(frozen=True)
class ControlProfile:
    """Базовые законы одного профиля ЛА и sparse override конкретных строк матрицы."""

    approach: ApproachConfig
    rollout: GroundControlConfig
    taxi: GroundControlConfig
    statuses: Mapping[FlightSegment, ProfileStatus] = field(default_factory=lambda: {
        segment: ProfileStatus.ACCEPTED for segment in FlightSegment
    })
    run_overrides: Mapping[
        str, Mapping[FlightSegment, Mapping[str, Any]]
    ] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if set(self.statuses) != set(FlightSegment):
            raise ValueError("ControlProfile требует статус approach/rollout/taxi")
        if not self.run_overrides:
            return
        from ismpu.config.run_matrix import resolve_matrix_run
        for run_id, per_segment in self.run_overrides.items():
            run = resolve_matrix_run(run_id)
            for segment, patch in per_segment.items():
                if run.segment not in (segment.value, "through"):
                    raise ValueError(
                        f"override {run_id} нельзя применить к {segment.value}")
                base = (
                    self.approach if segment is FlightSegment.APPROACH
                    else self.rollout if segment is FlightSegment.ROLLOUT
                    else self.taxi
                )
                _materialize_override(base, patch)

    def for_segment(
        self, segment: FlightSegment, matrix_run_id: str | None = None,
    ) -> ApproachConfig | GroundControlConfig:
        """Материализовать базовую ветку и sparse override выбранной строки."""
        if segment is FlightSegment.APPROACH:
            base = self.approach
        elif segment is FlightSegment.ROLLOUT:
            base = self.rollout
        elif segment is FlightSegment.TAXI:
            base = self.taxi
        else:
            raise ValueError(f"неподдерживаемый участок {segment!r}")
        patch = self.run_overrides.get(matrix_run_id or "", {}).get(segment, {})
        return _materialize_override(base, patch)

    def status_for(self, segment: FlightSegment) -> ProfileStatus:
        """Вернуть admission status участка; отсутствующий status безопасно означает draft."""
        return ProfileStatus(self.statuses.get(segment, ProfileStatus.DRAFT))

def _profile_name(profile: AircraftProfile | str) -> str:
    return profile.name if isinstance(profile, AircraftProfile) else str(profile).lower()


@dataclass(frozen=True)
class Scenario:
    """Полный профильный сценарий APPROACH → ROLLOUT → TAXI."""

    scenario_id: str
    seed: int
    aircraft_controls: Mapping[str, ControlProfile]
    conditions: Mapping[FlightSegment, SegmentConditions]
    approach: ApproachSetup = field(default_factory=ApproachSetup)
    touchdown: TouchdownSetup = field(default_factory=TouchdownSetup)
    sensor_noise: SensorNoise = field(default_factory=SensorNoise)
    matrix_runs: Mapping[FlightSegment, str] = field(default_factory=dict)
    matrix_codes: Mapping[FlightSegment, str] = field(default_factory=dict)
    provenance: Mapping[FlightSegment, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.matrix_runs:
            return
        from ismpu.config.run_matrix import resolve_matrix_run
        for segment, run_id in self.matrix_runs.items():
            run = resolve_matrix_run(run_id)
            if self.matrix_codes.get(segment) != run.code:
                raise ValueError(
                    f"{segment.value}: run_id {run_id!r} не совпадает с выбранным шифром")
            if run.segment not in (segment.value, "through"):
                raise ValueError(
                    f"{run_id}: строка {run.segment} не относится к {segment.value}")

    def control_for(
        self, profile: AircraftProfile | str, segment: FlightSegment,
    ) -> ApproachConfig | GroundControlConfig:
        """Вернуть effective control с override конкретного ``matrix_run_id``."""
        name = _profile_name(profile)
        try:
            controls = self.aircraft_controls[name]
        except KeyError as exc:
            known = ", ".join(sorted(self.aircraft_controls))
            raise KeyError(
                f"сценарий {self.scenario_id!r} не содержит профиль {name!r}; доступны: {known}"
            ) from exc
        return controls.for_segment(segment, self.matrix_runs.get(segment))

    def conditions_for(self, segment: FlightSegment) -> SegmentConditions:
        """Вернуть ожидаемую погоду и отказы одного участка без наследования на лету."""
        try:
            return self.conditions[segment]
        except KeyError as exc:
            raise KeyError(
                f"сценарий {self.scenario_id!r} не содержит участок {segment.value!r}"
            ) from exc

    def is_draft(self, profile: AircraftProfile | str, segment: FlightSegment) -> bool:
        """Проверить, запрещена ли автоматическая эксплуатация ветки."""
        return self.control_status(profile, segment) is ProfileStatus.DRAFT

    def control_status(
        self, profile: AircraftProfile | str, segment: FlightSegment,
    ) -> ProfileStatus:
        """Получить status конфигурации для точной пары aircraft/segment."""
        name = _profile_name(profile)
        try:
            return self.aircraft_controls[name].status_for(segment)
        except KeyError as exc:
            raise KeyError(f"в сценарии нет профиля {name!r}") from exc

    def is_accepted(self, profile: AircraftProfile | str, segment: FlightSegment) -> bool:
        """Проверить, допускается ли ветка в SFT expert dataset и auto-selection."""
        return self.control_status(profile, segment) is ProfileStatus.ACCEPTED

    def matrix_run_for(self, segment: FlightSegment) -> "MatrixRun | None":
        """Разрешить закреплённый run_id участка в неизменяемую строку каталога."""
        run_id = self.matrix_runs.get(segment)
        if run_id is None:
            return None
        from ismpu.config.run_matrix import resolve_matrix_run
        return resolve_matrix_run(run_id)

    def apply_control(
        self,
        controller: "ControllingSystem",
        profile: AircraftProfile | str,
        segment: FlightSegment = FlightSegment.ROLLOUT,
    ) -> "ControllingSystem":
        """Пересобрать stateful PID выбранного участка и синхронизировать ожидаемые отказы."""
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
        """Совместимый наземный срез отказов для подбора сценария и отчёта."""
        return tuple(sorted(
            self.conditions_for(FlightSegment.ROLLOUT).failures, key=lambda f: f.value))

    def to_dict(self) -> dict[str, Any]:
        """Serialize only the canonical profile- and matrix-aware schema v3."""
        from ismpu.config.json_config import scenario_to_document

        return scenario_to_document(self)

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
        *,
        legacy_aircraft_profile: str = "mc21",
    ) -> "Scenario":
        """Прочитать schema v3 либо явно мигрируемую v1/v2 конфигурацию."""
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
        """Скопировать канонический preset и заменить только запрошенные условия запуска."""
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

    # Численность PID и allocator изменены на этапе 2: все прежние наземные gains требуют
    # повторной настройки, даже если до рефакторинга считались рабочими.
    mc21_statuses = {
        FlightSegment.APPROACH: ProfileStatus.ACCEPTED,
        FlightSegment.ROLLOUT: ProfileStatus.DRAFT,
        FlightSegment.TAXI: ProfileStatus.DRAFT,
    }
    a330_statuses = {segment: ProfileStatus.DRAFT for segment in FlightSegment}
    controls = {
        MC21.name: ControlProfile(
            approach=_copy_approach(
                ICS_CLEAR_WEATHER_APPROACH,
                name=ICS_CLEAR_WEATHER_APPROACH.name,
                draft=False,
            ),
            rollout=_copy_ground(rollout_ground), taxi=_copy_ground(taxi_ground),
            statuses=mc21_statuses,
        ),
        A330_300.name: ControlProfile(
            approach=_copy_approach(
                _A330_APPROACH_DRAFT,
                name=_A330_APPROACH_DRAFT.name,
                draft=True,
            ),
            rollout=_copy_ground(rollout_ground), taxi=_copy_ground(taxi_ground),
            statuses=a330_statuses,
        ),
    }

    standard = SegmentConditions(weather=spec.weather)
    conditions = {segment: standard for segment in FlightSegment}
    for segment in affected:
        conditions[segment] = SegmentConditions(
            weather=spec.weather, failures=spec.failures
        )
    matrix_codes = {segment: spec.matrix_code for segment in affected if spec.matrix_code}
    return Scenario(
        scenario_id=spec.name,
        seed=0,
        aircraft_controls=controls,
        conditions=conditions,
        touchdown=(
            TouchdownSetup(speed_knots=15.0)
            if spec.name == "b_1_2_taxi" else TouchdownSetup()
        ),
        matrix_codes=matrix_codes,
        provenance={segment: spec.name for segment in FlightSegment},
    )


_SPECS = (
    _DEFAULT_SPEC, _LEFT_REVERSE_FAIL_SPEC, _RIGHT_REVERSE_FAIL_SPEC,
    _RIGHT_WIND_SPEC, _WET_RWY_SPEC, _PUDDLY_RWY_SPEC, _ICY_RWY_SPEC,
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
            profile: ControlProfile(
                approach=_copy_approach(
                    control.approach,
                    name=control.approach.name,
                    draft=control.approach.draft,
                ),
                rollout=_copy_ground(control.rollout),
                taxi=_copy_ground(control.taxi),
                statuses=dict(control.statuses),
                run_overrides=dict(control.run_overrides),
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
    controls: dict[str, ControlProfile] = {}
    for profile in sorted(profiles):
        by_segment = {
            segment: source.aircraft_controls[profile] for segment, source in sources.items()
        }
        statuses = {
            segment: source_controls.status_for(segment)
            for segment, source_controls in by_segment.items()
        }
        overrides: dict[str, dict[FlightSegment, Mapping[str, Any]]] = {}
        for segment, source_controls in by_segment.items():
            for run_id, per_segment in source_controls.run_overrides.items():
                if segment in per_segment:
                    overrides.setdefault(run_id, {})[segment] = per_segment[segment]
        controls[profile] = ControlProfile(
            approach=by_segment[FlightSegment.APPROACH].approach,
            rollout=by_segment[FlightSegment.ROLLOUT].rollout,
            taxi=by_segment[FlightSegment.TAXI].taxi,
            statuses=statuses,
            run_overrides=overrides,
        )
    return Scenario(
        scenario_id=scenario_id,
        seed=seed,
        aircraft_controls=controls,
        conditions={segment: source.conditions_for(segment) for segment, source in sources.items()},
        approach=sources[FlightSegment.APPROACH].approach,
        touchdown=sources[FlightSegment.ROLLOUT].touchdown,
        sensor_noise=sources[FlightSegment.APPROACH].sensor_noise,
        matrix_runs={
            segment: source.matrix_runs[segment]
            for segment, source in sources.items() if segment in source.matrix_runs
        },
        matrix_codes={
            segment: source.matrix_codes[segment]
            for segment, source in sources.items() if segment in source.matrix_codes
        },
        provenance={segment: source.scenario_id for segment, source in sources.items()},
    )


def compose_matrix_scenario(
    scenario_id: str,
    *,
    approach_run: "str | MatrixRun | None" = None,
    rollout_run: "str | MatrixRun | None" = None,
    taxi_run: "str | MatrixRun | None" = None,
    approach_case: "str | MatrixCase | None" = None,
    ground_case: "str | MatrixCase | None" = None,
    seed: int = 0,
) -> Scenario:
    """Собрать сценарий из конкретных строк APPROACH/ROLLOUT/TAXI.

    ``approach_case``/``ground_case`` оставлены только для эталонного ``working_ics`` и
    детерминированно означают первую строку шифра. Production CLI принимает только run_id.
    """
    from ismpu.config.run_matrix import (
        CASE_BY_CODE,
        CASE_BY_PRESET,
        MatrixRun,
        resolve_matrix_run,
    )

    if (approach_case is not None or ground_case is not None) and any(
        value is not None for value in (approach_run, rollout_run, taxi_run)
    ):
        raise ValueError("нельзя смешивать конкретные run_id и legacy шифры")

    def _first_run(value: "str | MatrixCase", expected: str) -> MatrixRun:
        if not isinstance(value, str):
            case = value
        else:
            case = CASE_BY_PRESET.get(value) or CASE_BY_CODE.get(
                value.strip().upper().replace("A", "А").replace("B", "Б"))
        if case is None or (expected == "approach") != (case.segment == "approach"):
            raise KeyError(f"шифр {value!r} не относится к части {expected}")
        return case.rows[0]

    if approach_case is not None or ground_case is not None:
        if approach_case is None or ground_case is None:
            raise ValueError("legacy-композиции нужны оба шифра")
        approach_run = _first_run(approach_case, "approach")
        legacy_ground = _first_run(ground_case, "ground")
        if legacy_ground.segment == "taxi":
            taxi_run = legacy_ground
        elif legacy_ground.segment == "through":
            return scenario_for_matrix_run(legacy_ground, scenario_id=scenario_id, seed=seed)
        else:
            rollout_run = legacy_ground

    selected: dict[FlightSegment, MatrixRun] = {}
    for segment, value, expected in (
        (FlightSegment.APPROACH, approach_run, "approach"),
        (FlightSegment.ROLLOUT, rollout_run, "rollout"),
        (FlightSegment.TAXI, taxi_run, "taxi"),
    ):
        if value is None:
            continue
        run = resolve_matrix_run(value)
        if run.segment == "through":
            if len([item for item in (approach_run, rollout_run, taxi_run) if item is not None]) != 1:
                raise ValueError("сквозной run_id нельзя смешивать с другими строками")
            return scenario_for_matrix_run(run, scenario_id=scenario_id, seed=seed)
        if run.segment != expected:
            raise ValueError(
                f"{run.matrix_run_id} относится к {run.segment}, а не к {expected}")
        selected[segment] = run

    if not selected:
        raise ValueError("нужен хотя бы один конкретный run_id")

    approach_source = selected.get(FlightSegment.APPROACH)
    rollout_source = selected.get(FlightSegment.ROLLOUT)
    taxi_source = selected.get(FlightSegment.TAXI)
    scenario = compose_scenario(
        scenario_id,
        approach=approach_source.preset if approach_source else "default",
        rollout=rollout_source.preset if rollout_source else "default",
        taxi=taxi_source.preset if taxi_source else None,
        seed=seed,
    )
    conditions = dict(scenario.conditions)
    for segment, run in selected.items():
        conditions[segment] = SegmentConditions(
            weather=run.condition.weather,
            failures=run.failures_for(segment),
        )
    if rollout_source is not None and taxi_source is None:
        conditions[FlightSegment.TAXI] = SegmentConditions(
            weather=rollout_source.condition.weather,
            failures=rollout_source.failures_for(FlightSegment.TAXI),
        )

    # Введённые в воздухе отказы явно сохраняются на последующих сегментах.
    persistent = conditions[FlightSegment.APPROACH].failures
    for segment in (FlightSegment.ROLLOUT, FlightSegment.TAXI):
        current = conditions[segment]
        conditions[segment] = replace(current, failures=current.failures | persistent)
    return replace(
        scenario,
        conditions=conditions,
        touchdown=(SCENARIOS[taxi_source.preset].touchdown
                   if taxi_source is not None else scenario.touchdown),
        matrix_runs={segment: run.matrix_run_id for segment, run in selected.items()},
        matrix_codes={segment: run.code for segment, run in selected.items()},
    )


def scenario_for_matrix_run(
    matrix_run: "str | MatrixRun", *, scenario_id: str | None = None, seed: int = 0,
) -> Scenario:
    """Одна строка каталога → минимальный сценарий нужного участка или сквозной пары."""
    from ismpu.config.run_matrix import (
        CASE_BY_CODE,
        THROUGH_PROFILE_CODES,
        resolve_matrix_run,
    )

    run = resolve_matrix_run(matrix_run)
    name = scenario_id or run.matrix_run_id
    if run.segment == "approach":
        return compose_matrix_scenario(name, approach_run=run, seed=seed)
    if run.segment == "rollout":
        return compose_matrix_scenario(name, rollout_run=run, seed=seed)
    if run.segment == "taxi":
        return compose_matrix_scenario(name, taxi_run=run, seed=seed)

    pair = THROUGH_PROFILE_CODES[run.code]
    approach = CASE_BY_CODE[pair[FlightSegment.APPROACH]].preset
    rollout = CASE_BY_CODE[pair[FlightSegment.ROLLOUT]].preset
    scenario = compose_scenario(name, approach=approach, rollout=rollout, seed=seed)
    conditions = {
        segment: SegmentConditions(
            weather=run.condition.weather,
            failures=run.failures_for(segment),
        )
        for segment in FlightSegment
    }
    return replace(
        scenario,
        conditions=conditions,
        matrix_runs={
            FlightSegment.APPROACH: run.matrix_run_id,
            FlightSegment.ROLLOUT: run.matrix_run_id,
        },
        matrix_codes={
            FlightSegment.APPROACH: run.code,
            FlightSegment.ROLLOUT: run.code,
        },
    )


def rebind_matrix_run(scenario: Scenario, matrix_run: "str | MatrixRun") -> Scenario:
    """Перенести накопленные overrides одного шифра на следующее условие этого же шифра."""
    from ismpu.config.run_matrix import resolve_matrix_run

    run = resolve_matrix_run(matrix_run)
    source_codes = set(scenario.matrix_codes.values())
    if source_codes != {run.code}:
        raise ValueError(
            f"scenario JSON относится к {sorted(source_codes) or ['без матрицы']}, "
            f"а выбран {run.code}")
    target = scenario_for_matrix_run(run, seed=scenario.seed)
    if set(target.aircraft_controls) != set(scenario.aircraft_controls):
        raise ValueError("набор AircraftProfile в scenario JSON не совпадает с матрицей")
    return replace(
        target,
        aircraft_controls=scenario.aircraft_controls,
        sensor_noise=scenario.sensor_noise,
    )


def _install_through_scenarios() -> None:
    """Собрать Б.4 из первой строки и заранее определённой пары законов."""
    from ismpu.config.run_matrix import CASE_BY_CODE

    for code in ("Б.4.1", "Б.4.2"):
        case = CASE_BY_CODE[code]
        SCENARIOS[case.preset] = scenario_for_matrix_run(
            case.rows[0], scenario_id=case.preset)


_install_through_scenarios()

FAILURE_MISMATCH_PENALTY = 100.0
_FRICTION_SCALE = 15.0
_WIND_SCALE = 20.0
_VISIBILITY_SCALE = 30100.0


def weather_distance(
    a: WeatherState, b: WeatherState, runway_heading_degt: float = RWY_HEADING_TRUE,
) -> float:
    """Нормированная дистанция сцепления, ветра, осадков и видимости двух условий."""
    cross_a, head_a = decompose_wind(
        a.wind_speed_kts, a.wind_dir_from_degt, runway_heading_degt)
    cross_b, head_b = decompose_wind(
        b.wind_speed_kts, b.wind_dir_from_degt, runway_heading_degt)

    runway_friction_dist = abs(a.runway_friction - b.runway_friction) / _FRICTION_SCALE
    cross_wind_dist = abs(cross_a - cross_b) / _WIND_SCALE
    head_wind_dist = 0.5 * abs(head_a - head_b) / _WIND_SCALE
    rain_pct_dist = abs(a.rain_pct - b.rain_pct)
    # visibility_dist = 0.5 * abs(a.visibility_m - b.visibility_m) / _VISIBILITY_SCALE

    return (
        runway_friction_dist
        + cross_wind_dist
        + head_wind_dist
        + rain_pct_dist
        # + visibility_dist
    )


def match_conditions(
    expected: SegmentConditions,
    failures: Iterable[FailureMode],
    weather: WeatherState,
    segment: FlightSegment,
) -> ConditionMatch:
    """Сравнить ожидаемые условия участка с одним фактическим кадром backend."""
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
    """Оценить близость telemetry к preset; несовпадение отказа доминирует над погодой."""
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
    """Выбрать ближайший нематричный preset, не допуская draft без явного флага."""
    pool = list(scenarios if scenarios is not None else SCENARIOS.values())
    profile = _profile_name(aircraft_profile)
    # Строка матрицы требует явного run_id; телеметрия не выбирает даже принятый шифр.
    pool = [scenario for scenario in pool if not scenario.matrix_codes]
    pool = [scenario for scenario in pool if profile in scenario.aircraft_controls]
    if not include_draft:
        pool = [scenario for scenario in pool if scenario.is_accepted(profile, segment)]
    if not pool:
        admission = "допущенных " if not include_draft else ""
        raise ValueError(
            f"нет {admission}сценариев для профиля {profile!r} "
            f"и участка {segment.value!r}")
    return min(pool, key=lambda scenario: (
        scenario_distance(scenario, failures, weather, segment=segment),
        bool(scenario.matrix_codes),
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
    """Подобрать нематричный preset по валидной telemetry или безопасным defaults."""
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
