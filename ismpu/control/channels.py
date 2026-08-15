"""Каналы управления и общий вектор команд.

`ControlsState` — разделяемая по тактам структура физических команд.
`LongitudinalChannel` — speed controller, выдающий симметричную базу тормозов/реверса.
`LateralChannel` — guidance, выдающий единый yaw-запрос. Смешивание выполняет allocator.

**Транспорта здесь нет.** Каналы получают телеметрию параметром и складывают команды в
`ControlsState`; отправкой и переводом в единицы ПИВ занимается стенд (`ICSSim.step`).
Команды здесь **нормированные** ([0,1] тормоза, [-1,0] реверс, [-1,1] руль) — миллиметры хода
педали и градусы РУД появляются только на границе транспорта.
"""

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from ismpu.utils.converts import Converts
from ismpu.control.pid import PIDController
from ismpu.control.trajectory import CompletionRule, ReferenceTrajectory
from ismpu.control.runway_tracker import GuidanceState, RunwayTracker
from ismpu.config.requirements import HEADING_HOLD_UNTIL_KTS

if TYPE_CHECKING:
    from ismpu.envs.ics_sim import Telemetry

logger = logging.getLogger(__name__)

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
    `control/approach.py`, на земле — `GroundControlAllocator`. Какие поля **заявлены** стенду,
    решает маска (`ICSSim._to_outputs` по текущему `ControlMode`).
    """
    break_control: bool = False

    # --- земля: каждый физический орган имеет отдельную нормированную команду --- #
    cmd_rudder: float = 0.0
    cmd_pedal: float = 0.0
    cmd_tiller: float = 0.0

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

    def reset(self) -> None:
        """Сброс к нейтральным командам — новый эпизод начинается с чистого состояния.

        Критично для `break_control`: он выставляется в конце КАЖДОГО нормального пробега
        (достигнута скорость руления), и без сброса следующий эпизод завершался бы на первом
        же такте.
        """
        self.break_control = False
        self.cmd_rudder = self.cmd_pedal = self.cmd_tiller = 0.0
        self.cmd_brake_l = self.cmd_brake_r = 0.0
        self.cmd_rev_l = self.cmd_rev_r = 0.0
        self.neutralize_airborne()
        self.quality_lateral = self.quality_heading = self.quality_speed = 0.0

    def neutralize_airborne(self) -> None:
        """Обнулить только воздушные команды.

        Нужно, когда воздушный канал не может считать закон (нет пакета стенда): оставить
        прошлое отклонение элеронов приложенным нельзя, а придумывать новое — не по чему.
        """
        self.cmd_elevator = 0.0
        self.cmd_aileron = 0.0
        self.cmd_throttle_l_rate = self.cmd_throttle_r_rate = 0.0
        self.cmd_throttle_norm = 0.0
        self.cmd_rudder = 0.0

    def neutralize(self) -> None:
        """Обнуляет все органы управления. Отправку делает вызывающий через `ICSSim.step`.

        Нейтральная команда, а не молчание: если просто перестать слать, последнее отклонение
        останется приложенным до срабатывания сторожа на той стороне. В воздухе одной нейтрали
        мало — там вместе с ней снимается заявка каналов (`ICSSim.deactivate`), иначе нулевое
        положение РУД было бы командой «малый газ», а не отказом от управления.
        """
        self.cmd_brake_l = self.cmd_brake_r = 0.0
        self.cmd_rev_l = self.cmd_rev_r = 0.0
        self.cmd_rudder = self.cmd_pedal = self.cmd_tiller = 0.0
        self.neutralize_airborne()

    @property
    def rudder_cmd(self) -> float:
        """Совместимое имя старого API; колёсные органы оно больше не обозначает."""
        return self.cmd_rudder

    @rudder_cmd.setter
    def rudder_cmd(self, value: float) -> None:
        self.cmd_rudder = value


@dataclass(frozen=True)
class LongitudinalDiagnostics:
    valid: bool
    value: float | None
    setpoint: float | None
    error: float | None
    acceleration_ms2: float | None
    distance_m: float
    base_brake_left: float
    base_brake_right: float
    base_reverse_left: float
    base_reverse_right: float
    reverse_allowed: bool
    completion_rule: CompletionRule
    completion_reached: bool
    stop_requested: bool


class LongitudinalChannel:
    """Блок 1: скорость → симметричная база тормозов и реверса."""

    STOP_THRESHOLD_KTS = 0.5

    def __init__(self, pid_brake_l: PIDController, pid_brake_r: PIDController,
                 pid_rev_l: PIDController, pid_rev_r: PIDController,
                 trajectory: ReferenceTrajectory) -> None:
        self.trajectory = trajectory
        self.pid_brake_l = pid_brake_l
        self.pid_brake_r = pid_brake_r
        self.pid_rev_l = pid_rev_l
        self.pid_rev_r = pid_rev_r
        self.traveled_distance_m = 0.0
        self.last_diagnostics: LongitudinalDiagnostics | None = None
        self.w_lon = 1.0
        self.rollout_started = False
        self.initialized = False
        self._previous_speed_ms: float | None = None

    def begin(self, groundspeed_ms: float) -> None:
        """Сбросить PID и привязать начало профиля к фактической скорости касания/старта."""
        for pid in (self.pid_brake_l, self.pid_brake_r, self.pid_rev_l, self.pid_rev_r):
            pid.reset()
        self.trajectory.reset_ms(max(0.0, groundspeed_ms))
        self.traveled_distance_m = 0.0
        self.rollout_started = groundspeed_ms * Converts.MS_TO_KTS >= ROLLOUT_STARTED_KTS
        self._previous_speed_ms = groundspeed_ms
        self.initialized = True

    def compute(self, dt: float, telemetry: "Telemetry") -> LongitudinalDiagnostics:
        if not telemetry.valid or telemetry.groundspeed_ms is None:
            result = LongitudinalDiagnostics(
                False, None, None, None, None, self.traveled_distance_m,
                0.0, 0.0, 0.0, 0.0, False,
                self.trajectory.completion_rule, False, True,
            )
            self.last_diagnostics = result
            return result

        speed = telemetry.groundspeed_ms
        if not self.initialized:
            self.begin(speed)
        dt_distance = max(0.0, min(0.25, dt))
        reference = self.trajectory.get_reference_speed(self.traveled_distance_m)
        error = speed - reference
        acceleration = (
            telemetry.accel_long_g * 9.80665
            if telemetry.accel_long_g is not None
            else ((speed - self._previous_speed_ms) / dt_distance
                  if self._previous_speed_ms is not None and dt_distance > 0.0 else 0.0)
        )

        brake_left = self.w_lon * self.pid_brake_l.compute(error, dt, measurement=speed)
        brake_right = self.w_lon * self.pid_brake_r.compute(error, dt, measurement=speed)
        speed_kts = speed * Converts.MS_TO_KTS
        reverse_allowed = speed_kts > 60.0
        if reverse_allowed:
            # Реверс имеет диапазон [-1, 0], поэтому его ошибка должна быть отрицательной,
            # когда ВС быстрее профиля. Прежний положительный знак всегда зажимал выход в 0.
            reverse_error = -error
            reverse_left = self.w_lon * self.pid_rev_l.compute(
                reverse_error, dt, measurement=speed)
            reverse_right = self.w_lon * self.pid_rev_r.compute(
                reverse_error, dt, measurement=speed)
        else:
            reverse_left = reverse_right = 0.0
            self.pid_rev_l.reset()
            self.pid_rev_r.reset()

        if speed_kts >= ROLLOUT_STARTED_KTS:
            self.rollout_started = True
        rule = self.trajectory.completion_rule
        completion_reached = False
        if self.rollout_started:
            if rule is CompletionRule.FULL_STOP:
                completion_reached = speed_kts <= self.STOP_THRESHOLD_KTS
            elif rule is CompletionRule.HANDOVER_TAXI:
                completion_reached = speed <= self.trajectory.v_target_ms

        result = LongitudinalDiagnostics(
            valid=True,
            value=speed,
            setpoint=reference,
            error=error,
            acceleration_ms2=acceleration,
            distance_m=self.traveled_distance_m,
            base_brake_left=brake_left,
            base_brake_right=brake_right,
            base_reverse_left=reverse_left,
            base_reverse_right=reverse_right,
            reverse_allowed=reverse_allowed,
            completion_rule=rule,
            completion_reached=completion_reached,
            stop_requested=completion_reached,
        )
        self.traveled_distance_m += speed * dt_distance
        self._previous_speed_ms = speed
        self.last_diagnostics = result
        logger.debug("ground longitudinal: %s", result)
        return result

@dataclass(frozen=True)
class LateralDiagnostics:
    valid: bool
    value: float | None
    setpoint: float | None
    error: float | None
    xte: float | None
    course_error: float | None
    heading_error: float | None
    guidance_error: float | None
    along_track: float | None
    lookahead: float | None
    source: str
    event: str | None
    steering_requested: float
    steering_limited: float
    saturated: bool


class LateralChannel:
    """Блок 2: runway guidance → единый нормированный yaw-запрос."""

    def __init__(self, pid: PIDController, tracker: RunwayTracker) -> None:
        self.pid = pid
        self.tracker = tracker
        self.w_lat = 1.0
        self.last_diagnostics: LateralDiagnostics | None = None
        self.last_guidance: GuidanceState | None = None
        self._last_guidance_telemetry: "Telemetry | None" = None
        self._previous_track_deg: float | None = None
        self._unwrapped_track_deg: float | None = None

    def _guidance(
        self,
        telemetry: "Telemetry",
        groundspeed_ms: float,
    ) -> GuidanceState | None:
        """Guidance по тому, что даёт стенд. → словарь guidance или None, если данных нет.

        Стенд сообщает курс ВПП и боковое отклонение напрямую — тогда собственная геодезия не
        нужна и, главное, не применима: координат торцов ВПП стенд не передаёт, и считать от
        захардкоженного Шереметьево значило бы вести ВС по чужой осевой линии.

        Геодезический путь разрешён только с явно приложенным профилем ВПП и полностью
        валидными истинными координатами/направлениями. Поэтому два источника не смешиваются.
        """
        if self._last_guidance_telemetry is telemetry:
            return self.last_guidance

        runway_heading = telemetry.runway_heading_magnetic_deg
        if runway_heading is None:
            runway_heading = telemetry.runway_heading_deg
        lateral_deviation = telemetry.lateral_deviation_m
        if None not in (
            runway_heading,
            lateral_deviation,
            telemetry.track_magnetic_deg,
            telemetry.heading_magnetic_deg,
        ):
            result = self.tracker.guidance_from_deviation(
                telemetry.track_magnetic_deg,
                runway_heading,
                lateral_deviation,
                groundspeed_ms,
                aircraft_heading_deg=telemetry.heading_magnetic_deg,
                source="ics_direct" if telemetry.ics_inputs is not None else "direct",
            )
            self.last_guidance = result
            self._last_guidance_telemetry = telemetry
            return result

        # В синтетических backend-независимых кадрах явно заданный true heading одновременно
        # служит true track. Для ICS это запрещено: там есть отдельный validity-флаг track.
        true_track = telemetry.track_true_deg
        if true_track is None and telemetry.ics_inputs is None:
            true_track = telemetry.heading_true_deg
        profile = telemetry.runway_profile
        if profile is None or None in (
            telemetry.lat,
            telemetry.lon,
            true_track,
            telemetry.heading_true_deg,
        ):
            result = None
        else:
            result = self.tracker.guidance(
                telemetry.lat,
                telemetry.lon,
                true_track,
                groundspeed_ms,
                aircraft_heading_deg=telemetry.heading_true_deg,
                runway_profile=profile,
                source="geodetic",
            )
        self.last_guidance = result
        self._last_guidance_telemetry = telemetry
        return result

    def guidance_for(self, telemetry: "Telemetry") -> GuidanceState | None:
        """Единый GuidanceState текущего кадра для control/observation/reward."""
        if not telemetry.valid or telemetry.groundspeed_ms is None:
            return None
        return self._guidance(telemetry, telemetry.groundspeed_ms)

    def _guidance_unavailable(self) -> LateralDiagnostics:
        result = LateralDiagnostics(
            valid=False,
            value=None,
            setpoint=None,
            error=None,
            xte=None,
            course_error=None,
            heading_error=None,
            guidance_error=None,
            along_track=None,
            lookahead=None,
            source="unavailable",
            event="guidance_unavailable",
            steering_requested=0.0,
            steering_limited=0.0,
            saturated=False,
        )
        self.last_diagnostics = result
        return result

    def compute(self, dt: float, telemetry: "Telemetry") -> LateralDiagnostics:
        groundspeed_ms = telemetry.groundspeed_ms
        if not telemetry.valid or groundspeed_ms is None:
            return self._guidance_unavailable()

        guidance = self._guidance(telemetry, groundspeed_ms)
        if guidance is None:
            return self._guidance_unavailable()

        error = guidance.guidance_error_deg
        measured_track = telemetry.track_magnetic_deg
        if guidance.source == "geodetic":
            measured_track = (
                telemetry.track_true_deg
                if telemetry.track_true_deg is not None else telemetry.heading_true_deg)
        measurement = self._unwrap_track(measured_track)
        limited = self.w_lat * self.pid.compute(error, dt, measurement=measurement)
        requested = self.w_lat * self.pid.last_unconstrained
        result = LateralDiagnostics(
            valid=True,
            value=measured_track,
            setpoint=guidance.desired_heading_deg,
            error=error,
            xte=guidance.xte,
            course_error=guidance.course_error_deg,
            heading_error=guidance.heading_error_deg,
            guidance_error=guidance.guidance_error_deg,
            along_track=guidance.along_track,
            lookahead=guidance.lookahead,
            source=guidance.source,
            event=None,
            steering_requested=requested,
            steering_limited=limited,
            saturated=abs(requested - limited) > 1e-12,
        )
        self.last_diagnostics = result
        logger.debug("ground lateral: %s", result)
        return result

    def _unwrap_track(self, track_deg: float | None) -> float:
        if track_deg is None:
            return 0.0
        if self._previous_track_deg is None or self._unwrapped_track_deg is None:
            self._unwrapped_track_deg = track_deg
        else:
            delta = (track_deg - self._previous_track_deg + 180.0) % 360.0 - 180.0
            self._unwrapped_track_deg += delta
        self._previous_track_deg = track_deg
        return self._unwrapped_track_deg
