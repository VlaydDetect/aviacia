"""Стенд заказчика как источник телеметрии и приёмник команд.

Единственный «симулятор» проекта: контур, среда обучения и актор работают против стенда по
ПИВ (JSON/UDP, `io/ics_connector.py`). Абстракции «выбери бэкенд» здесь нет и не нужно —
поставка идёт на стенд, и второго транспорта не существует.

Два класса:

* `Telemetry` — телеметрия в **СИ**. Стенд шлёт узлы, футы, футы/мин и градусы/с (см.
  `docs/ICSInterface.cs`), контур и наблюдение работают в СИ; граница пересчёта проходит ровно
  здесь и больше нигде.
* `ICSSim` — обмен со стендом: `read_telemetry` / `step(ControlsState)` плюс рукопожатие
  (`io/ics_engagement.py`), без которого стенд команды не исполняет.

**Средой распоряжается Заказчик.** Погоду, отказы и начальные условия задаёт стенд, а нам они
приходят телеметрией (`WeatherState.from_ics`, `Telemetry.faults`). Ни телепорта, ни инъекции
отказов, ни паузы у нас нет — сценарий (`envs/scenario.py`) описывает условия, чтобы под них
**подобрать** пресет, а не чтобы их установить.
"""

import math
import time
import logging
from dataclasses import dataclass, field, replace
from typing import Optional

from ismpu.io.ics_connector import (
    ICSBenchConnector, ICSInputs, ICSOutputs, ControlModeState, ReverseEngineType, LISTEN_IP_ANY,
)
from ismpu.io.ics_engagement import IcsEngagement, EngagementInputs
from ismpu.config.ics import (
    BRAKE_CMD_MAX_MM, THROTTLE_ANGLE_MIN_DEG, THROTTLE_RATE_MAX_DEG_S,
    REVERSE_THROTTLE_GAIN_PER_S, TILLER_MAX_MM, RUDDER_MAX_DEG, RUDDER_PEDAL_MAX_MM,
    AILERON_MAX_DEG, ROLLOUT_CONTROL_MASK, TAXI_CONTROL_MASK, AIRBORNE_CONTROL_MASK, FlightPhase,
    FLARE_MODE_RADIO_ALTITUDE_FT, FLARE_MODE_END_RADIO_ALTITUDE_FT,
)
from ismpu.utils.converts import Converts
from ismpu.config.constants import DT
from ismpu.config.envelope import LandingFlapConfiguration
from ismpu.config.aircraft_profiles import AircraftProfile, get_aircraft_profile
from ismpu.config.runway_profiles import RunwayProfile, get_runway_profile
from ismpu.config.segments import FlightSegment
from ismpu.config.scenarios import ConditionMatch, Scenario, match_conditions
from ismpu.control.channels import ControlsState
from ismpu.control.failures import FailureMode
from ismpu.envs.weather import WeatherState
from ismpu.envs.sim_interface import ApproachData, ShutdownReport, SimInterface, StartMode

logger = logging.getLogger(__name__)


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _signal_valid(flag: int, value: object) -> bool:
    """Validity-флаг стенда плюс конечное числовое значение."""
    try:
        return bool(flag) and math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _throttle_rate(reverse_level: float, actual_angle_deg: float) -> float:
    """Желаемый уровень реверса [-1, 0] → скорость перемещения РУД (°/с).

    Тягой (в том числе обратной) командуют **скоростью**: абсолютного положения в перечне
    управляющих сигналов Заказчика нет. Поэтому уровень превращается в целевой угол, а на стенд
    уходит скорость, которой фактический угол к этой цели ведут.
    """
    target = -reverse_level * THROTTLE_ANGLE_MIN_DEG        # [-1,0] → [−26.5°, 0°]
    rate = REVERSE_THROTTLE_GAIN_PER_S * (target - actual_angle_deg)
    return _clamp(rate, -THROTTLE_RATE_MAX_DEG_S, THROTTLE_RATE_MAX_DEG_S)


@dataclass(frozen=True)
class TelemetryExtensions:
    """Типизированные backend-расширения общего SI-кадра."""

    ias_ms: Optional[float] = None
    radio_altitude_ft: Optional[float] = None
    ils_valid: Optional[bool] = None
    landing_flaps: Optional[LandingFlapConfiguration] = None
    main_gear_contact: Optional[bool] = None
    runway_heading_true_deg: Optional[float] = None
    runway_heading_magnetic_deg: Optional[float] = None
    runway_length_m: Optional[float] = None
    runway_width_m: Optional[float] = None
    lateral_deviation_m: Optional[float] = None
    weight_on_wheels: Optional[bool] = None
    flight_phase: Optional[FlightPhase] = None
    faults: frozenset[FailureMode] = frozenset()
    weather: Optional[WeatherState] = None
    agent_is_active: Optional[bool] = None


@dataclass
class Telemetry:
    """Телеметрия стенда, приведённая к **СИ**.

    Проверять надо `valid` **до** полей: при таймауте приёма бэкенд отдаёт нули, а не `None`,
    и `groundspeed_ms = 0.0` неотличимо от «достигнута скорость руления».

    **Стенд-специфичные сигналы не дублируются.** Обжатие стоек, фаза полёта, геометрия ВПП,
    погода, отказы и `AgentIsActive` — это разные поля одного «сырого» пакета `ICSInputs`.
    Пересказывать их в отдельные поля значило бы завести второй источник истины и рисковать
    рассинхроном (именно так раньше обжатие стоек считалось нашей, а не стендовой, логикой).
    Поэтому пакет прикладывается целиком (`ics_inputs`), а сигналы выводятся из него через
    property. Хранимые поля — только те, что нужны контуру и наблюдению в СИ.
    """
    lat: Optional[float]
    lon: Optional[float]
    groundspeed_ms: Optional[float]
    heading_true_deg: Optional[float]
    heading_magnetic_deg: Optional[float] = None
    track_magnetic_deg: Optional[float] = None
    track_true_deg: Optional[float] = None
    runway_heading_true_deg: Optional[float] = None
    runway_heading_magnetic_deg: Optional[float] = None
    pitch_deg: Optional[float] = None
    roll_deg: Optional[float] = None
    elevation_m: Optional[float] = None
    agl_m: Optional[float] = None
    vy_ms: Optional[float] = None
    p_rad: Optional[float] = None
    q_rad: Optional[float] = None
    r_rad: Optional[float] = None
    accel_long_g: Optional[float] = None
    accel_norm_g: Optional[float] = None
    accel_side_g: Optional[float] = None
    wind_speed_ms: Optional[float] = None
    wind_dir_from_deg: Optional[float] = None
    runway_profile: Optional[RunwayProfile] = None
    lateral_deviation_sign: float = 1.0

    # Общий воздушный срез. Для ICS это сам ICSInputs (он имеет тот же набор полей),
    # для X-Plane — ApproachData. Сырой пакет ICS остаётся только для аудита.
    approach_inputs: Optional[ApproachData | ICSInputs] = None
    ics_inputs: Optional[ICSInputs] = None
    extensions: TelemetryExtensions = field(default_factory=TelemetryExtensions)

    # Значения, которые backend может задать без ICSInputs. Суффикс ``_direct``
    # отличает хранимое поле dataclass от публичного property.
    ias_ms_direct: Optional[float] = None
    radio_altitude_ft_direct: Optional[float] = None
    ils_valid_direct: Optional[bool] = None
    landing_flaps_direct: Optional[object] = None
    main_gear_contact_direct: Optional[bool] = None
    runway_heading_deg_direct: Optional[float] = None
    runway_length_m_direct: Optional[float] = None
    runway_width_m_direct: Optional[float] = None
    lateral_deviation_m_direct: Optional[float] = None
    weight_on_wheels_direct: Optional[bool] = None
    flight_phase_direct: Optional[int] = None
    faults_direct: Optional[frozenset] = None
    weather_direct: Optional[WeatherState] = None
    agent_is_active_direct: Optional[bool] = None

    valid: bool = True   # False — телеметрии нет (таймаут приёма)

    @classmethod
    def from_ics(
        cls,
        inp: ICSInputs,
        *,
        runway_profile: RunwayProfile | None = None,
        lateral_deviation_sign: float = 1.0,
    ) -> "Telemetry":
        """`ICSInputs` → `Telemetry`: поля в СИ + «сырой» пакет для property.

        Стенд отдаёт узлы, футы, футы/мин и градусы/с. Пропущенный здесь перевод — не косметика:
        путевая скорость в узлах, положенная в поле м/с, даёт ошибку в 1.94 раза, и продольный
        канал прочитает 140 узлов как 272 и немедленно даст полное торможение.
        """
        if lateral_deviation_sign not in (-1.0, 1.0):
            raise ValueError("lateral_deviation_sign должен быть +1 или -1")
        return cls(
            lat=inp.Latitude if _signal_valid(inp.LatitudeValid, inp.Latitude) else None,
            lon=inp.Longitude if _signal_valid(inp.LongitudeValid, inp.Longitude) else None,
            groundspeed_ms=(
                inp.GroundSpeed * Converts.KTS_TO_MS
                if _signal_valid(inp.GroundSpeedValid, inp.GroundSpeed) else None),
            heading_true_deg=(
                inp.TrueHeading if _signal_valid(inp.TrueHeadingValid, inp.TrueHeading) else None),
            heading_magnetic_deg=(
                inp.MagneticHeading
                if _signal_valid(inp.MagneticHeadingValid, inp.MagneticHeading) else None),
            track_magnetic_deg=(
                inp.TrkAngleMagnetic
                if _signal_valid(inp.TrkAngleMagneticValid, inp.TrkAngleMagnetic) else None),
            track_true_deg=(
                inp.TrkAngleTrue
                if _signal_valid(inp.TrkAngleTrueValid, inp.TrkAngleTrue) else None),
            runway_heading_magnetic_deg=(
                inp.RunwayHeading
                if _signal_valid(inp.RunwayHeadingValid, inp.RunwayHeading) else None),
            pitch_deg=(
                inp.PitchAngle if _signal_valid(inp.PitchAngleValid, inp.PitchAngle) else None),
            roll_deg=(
                inp.RollAngle if _signal_valid(inp.RollAngleValid, inp.RollAngle) else None),
            elevation_m=(
                inp.BaroAltitude * Converts.FT_TO_M
                if _signal_valid(inp.BaroAltitudeValid, inp.BaroAltitude) else None),
            agl_m=(
                inp.RadioAltitude * Converts.FT_TO_M
                if _signal_valid(inp.RadioAltitudeValid, inp.RadioAltitude) else None),
            vy_ms=(
                inp.VerticalSpeed * Converts.FTM_TO_MS
                if _signal_valid(inp.VerticalSpeedValid, inp.VerticalSpeed) else None),
            p_rad=(math.radians(inp.BodyRollRate)
                   if _signal_valid(inp.BodyRollRateValid, inp.BodyRollRate) else None),
            q_rad=(math.radians(inp.BodyPitchRate)
                   if _signal_valid(inp.BodyPitchRateValid, inp.BodyPitchRate) else None),
            r_rad=(math.radians(inp.BodyYawRate)
                   if _signal_valid(inp.BodyYawRateValid, inp.BodyYawRate) else None),
            accel_long_g=(inp.BodyLongAccel
                          if _signal_valid(inp.BodyLongAccelValid, inp.BodyLongAccel) else None),
            accel_norm_g=(inp.BodyNormAccel
                          if _signal_valid(inp.BodyNormAccelValid, inp.BodyNormAccel) else None),
            accel_side_g=(inp.BodyLatAccel
                          if _signal_valid(inp.BodyLatAccelValid, inp.BodyLatAccel) else None),
            wind_speed_ms=inp.WindSpeed * Converts.KTS_TO_MS,           # kt → м/с
            wind_dir_from_deg=inp.WindDirectionTrue,
            runway_profile=runway_profile,
            lateral_deviation_sign=lateral_deviation_sign,
            approach_inputs=inp,
            ics_inputs=inp,
        )

    @classmethod
    def invalid(cls) -> "Telemetry":
        """Кадр «связи со стендом нет». Нули, а не None: контур проверяет `valid` первым."""
        return cls(lat=0.0, lon=0.0, groundspeed_ms=0.0, heading_true_deg=0.0, valid=False)

    # --- сигналы стенда: выводятся из ics_inputs, отдельно не хранятся --- #

    @property
    def airborne_data_available(self) -> bool:
        return bool(self.valid and self.approach_inputs is not None)

    @property
    def invalid_approach_signals(self) -> tuple[str, ...]:
        """Невалидные ICS-сигналы, которые воздушный закон читает безусловно."""
        i = self.ics_inputs
        if i is None:
            return ()
        required = {
            "RadioAltitude": _signal_valid(i.RadioAltitudeValid, i.RadioAltitude),
            "IndicatedAirspeed": _signal_valid(
                i.IndicatedAirspeedValid, i.IndicatedAirspeed),
            "TrueAirspeed": _signal_valid(i.TrueAirspeedValid, i.TrueAirspeed),
            "GroundSpeed": _signal_valid(i.GroundSpeedValid, i.GroundSpeed),
            "VerticalSpeed": _signal_valid(i.VerticalSpeedValid, i.VerticalSpeed),
            "PitchAngle": _signal_valid(i.PitchAngleValid, i.PitchAngle),
            "RollAngle": _signal_valid(i.RollAngleValid, i.RollAngle),
            "TrkAngleMagnetic": _signal_valid(
                i.TrkAngleMagneticValid, i.TrkAngleMagnetic),
            "RunwayHeading": _signal_valid(i.RunwayHeadingValid, i.RunwayHeading),
            "BodyPitchRate": _signal_valid(i.BodyPitchRateValid, i.BodyPitchRate),
            "BodyNormAccel": _signal_valid(i.BodyNormAccelValid, i.BodyNormAccel),
        }
        return tuple(name for name, valid in required.items() if not valid)

    @property
    def faults_available(self) -> bool:
        return bool(self.valid and (self.faults_direct is not None or self.ics_inputs is not None))

    @property
    def ias_ms(self) -> Optional[float]:
        """Приборная скорость (kt → м/с). Отсечки реверса заданы по ней, а не по путевой."""
        if self.ias_ms_direct is not None:
            return self.ias_ms_direct
        source = self.approach_inputs
        if source is None:
            return None
        if self.ics_inputs is not None and not _signal_valid(
            self.ics_inputs.IndicatedAirspeedValid,
            self.ics_inputs.IndicatedAirspeed,
        ):
            return None
        return source.IndicatedAirspeed * Converts.KTS_TO_MS

    @property
    def radio_altitude_ft(self) -> Optional[float]:
        """Радиовысота **в футах** — единицы стенда.

        Порог воздушного включения (400 футов) и терминальное окно (80 футов) заданы в футах,
        и сверять их с пересчитанным `agl_m` значило бы гонять величину туда-обратно ради
        сравнения с константой, которая всё равно записана в футах.
        """
        if self.radio_altitude_ft_direct is not None:
            return self.radio_altitude_ft_direct
        i = self.ics_inputs
        return (
            i.RadioAltitude
            if i is not None and _signal_valid(i.RadioAltitudeValid, i.RadioAltitude)
            else None)

    @property
    def ils_valid(self) -> Optional[bool]:
        """Объявлены ли валидными **оба** канала ILS (курсовой и глиссадный).

        `None` — пакета стенда нет, судить не по чему. Проверять обязательно: сам закон захода
        читает `LocDeviation`/`GSDeviation` безусловно, и при снятой валидности нулевое отклонение
        неотличимо от «идеально на оси» — контур будет уверенно вести ВС по несуществующей
        глиссаде.
        """
        if self.ils_valid_direct is not None:
            return self.ils_valid_direct
        i = self.ics_inputs
        if i is None:
            return None
        return bool(
            _signal_valid(i.LocDeviationValid, i.LocDeviation)
            and _signal_valid(i.GSDeviationValid, i.GSDeviation))

    @property
    def landing_flaps(self):
        """Посадочная конфигурация механизации; `None` — положение не посадочное.

        `None` здесь — это запрет на воздушное управление, а не повод подставить предположение:
        весь воздушный закон (уставка скорости к VAPP, пределы угла атаки, мониторинг огибающей)
        считается по таблицам посадочной конфигурации и на чистом крыле неприменим.
        """
        from ismpu.config.envelope import measured_landing_flaps
        if self.landing_flaps_direct is not None:
            return self.landing_flaps_direct
        source = self.approach_inputs
        return measured_landing_flaps(source.FlapsAngle) if source is not None else None

    @property
    def main_gear_contact(self) -> bool:
        """Касание: обжата **любая основная** стойка.

        Носовая не участвует — она обжимается позже основных, и ждать её значило бы пропустить
        начало пробега. Признак подтверждён на стенде коллегой как точка окончания воздушного
        участка.
        """
        if self.main_gear_contact_direct is not None:
            return self.main_gear_contact_direct
        i = self.ics_inputs
        return bool(i is not None and (i.LeftGearWeightOnWheels or i.RightGearWeightOnWheels))

    @property
    def runway_heading_deg(self) -> Optional[float]:
        if self.runway_heading_deg_direct is not None:
            return self.runway_heading_deg_direct
        i = self.ics_inputs
        return (
            i.RunwayHeading
            if i is not None and _signal_valid(i.RunwayHeadingValid, i.RunwayHeading)
            else None)

    @property
    def runway_length_m(self) -> Optional[float]:
        if self.runway_length_m_direct is not None:
            return self.runway_length_m_direct
        i = self.ics_inputs
        return (
            i.RunwayLength
            if i is not None
            and _signal_valid(i.RunwayHeadingValid, i.RunwayHeading)
            and math.isfinite(i.RunwayLength)
            else None)

    @property
    def runway_width_m(self) -> Optional[float]:
        if self.runway_width_m_direct is not None:
            return self.runway_width_m_direct
        i = self.ics_inputs
        return (
            i.RunwayWidth
            if i is not None
            and _signal_valid(i.RunwayHeadingValid, i.RunwayHeading)
            and math.isfinite(i.RunwayWidth)
            else None)

    @property
    def lateral_deviation_m(self) -> Optional[float]:
        """Боковое отклонение от оси, измеренное стендом. Позволяет не считать геодезию самим."""
        if self.lateral_deviation_m_direct is not None:
            return self.lateral_deviation_m_direct
        i = self.ics_inputs
        if (
            i is None
            or not _signal_valid(i.RunwayHeadingValid, i.RunwayHeading)
            or not math.isfinite(i.LateralDeviation)
        ):
            return None
        return self.lateral_deviation_sign * i.LateralDeviation

    @property
    def weight_on_wheels(self) -> Optional[bool]:
        """Обжатие ВСЕХ стоек. Диагностический сигнал; условие включения проверяет сам стенд."""
        if self.weight_on_wheels_direct is not None:
            return self.weight_on_wheels_direct
        i = self.ics_inputs
        if i is None:
            return None
        return bool(i.NoseGearWeightOnWheels and i.LeftGearWeightOnWheels and i.RightGearWeightOnWheels)

    @property
    def flight_phase(self) -> Optional[int]:
        """Фаза полёта по `config.ics.FlightPhase` — по ней распознаётся уже идущий пробег."""
        if self.flight_phase_direct is not None:
            return self.flight_phase_direct
        i = self.ics_inputs
        return i.FlightPhase if (i is not None and i.FlightPhaseValid) else None

    @property
    def faults(self) -> frozenset:
        """Отказы, о которых сообщает борт — **единственный** источник истины об отказах.

        Раньше отказы задавались сценарием и моделировались нами; на стенде они приходят
        телеметрией, и выдумывать их на своей стороне значит управлять по несуществующей
        конфигурации.
        """
        if self.faults_direct is not None:
            return self.faults_direct
        return _faults_from_inputs(self.ics_inputs) if self.ics_inputs else frozenset()

    @property
    def weather(self) -> Optional[WeatherState]:
        """Фактические погодные условия со стенда (ветер, сцепление, осадки, видимость)."""
        if self.weather_direct is not None:
            return self.weather_direct
        return WeatherState.from_ics(self.ics_inputs) if self.ics_inputs else None

    @property
    def runway_condition(self) -> Optional[float]:
        """Состояние ВПП в нашей шкале скользкости (`envs.weather.RunwayCondition`)."""
        w = self.weather
        return w.runway_friction if w is not None else None

    @property
    def agent_is_active(self) -> bool:
        """Подтверждение стенда, что он **принял** наше управление к исполнению. Единственный
        авторитет по факту включения: наша сторона его не вычисляет, а читает (см.
        `io/ics_engagement.py`)."""
        if self.agent_is_active_direct is not None:
            return self.agent_is_active_direct
        return bool(self.ics_inputs.AgentIsActive) if self.ics_inputs else False


def _faults_from_inputs(inp: ICSInputs) -> frozenset:
    """Сигналы отказов со стенда → наши `FailureMode`.

    Отказы шасси (`FaultLeftLandingGear` и др.) приходят кодом 0…6 с разными причинами; для нас
    существенен сам факт неисправной конфигурации, поэтому любой ненулевой код → `GEAR_CONFIG`.
    """
    active = set()
    if inp.FaultLeftEngine:
        active.add(FailureMode.ENGINE_OUT_LEFT)
    if inp.FaultRightEngine:
        active.add(FailureMode.ENGINE_OUT_RIGHT)
    if inp.FaultLeftEngineReverse:
        active.add(FailureMode.REVERSE_LEFT_FAIL)
    if inp.FaultRightEngineReverse:
        active.add(FailureMode.REVERSE_RIGHT_FAIL)
    if inp.FaultNWS:
        active.add(FailureMode.NWS_FAIL)
    if inp.FaultLeftLandingGear or inp.FaultRightLandingGear or inp.FaultNoseLandingGear:
        active.add(FailureMode.GEAR_CONFIG)
    return frozenset(active)


class ICSSim(SimInterface):
    """Обмен со стендом заказчика: телеметрия внутрь, команды наружу.

    Управление включается **только** после рукопожатия (`io/ics_engagement.py`). Факт включения
    определяет **стенд**, а не мы: он подтверждает приём управления полем `AgentIsActive = 1` во
    входной телеметрии. Наша задача в прогреве — гнать корректный стимул (`ModeAIReady = 1`
    непрерывно и переход `ControlMode`), а `engaged` лишь читает подтверждение стенда. Пока его
    нет, `ControlValidMask = 0` и органы не выдаются.
    """

    backend_name = "ics"

    def __init__(self, connector: Optional[ICSBenchConnector] = None,
                 listen_ip: str = LISTEN_IP_ANY, listen_port: int = 3030, timeout: float = 1.0,
                 engagement: Optional[IcsEngagement] = None,
                 aircraft_profile: AircraftProfile | str | None = None,
                 runway_profile: RunwayProfile | str | None = None,
                 validate_conditions: bool = True):
        if aircraft_profile is None:
            raise ValueError("для ICS требуется явный aircraft_profile")
        self.aircraft_profile = (
            get_aircraft_profile(aircraft_profile)
            if isinstance(aircraft_profile, str) else aircraft_profile)
        self.runway_profile = (
            get_runway_profile(runway_profile)
            if isinstance(runway_profile, str) else runway_profile)
        self.connector = connector if connector is not None else ICSBenchConnector(listen_ip, listen_port)
        self.timeout = timeout
        self.engagement = engagement if engagement is not None else IcsEngagement()
        self._last_telemetry: Optional[Telemetry] = None
        self._shutdown_report: Optional[ShutdownReport] = None
        self._scenario: Scenario | None = None
        self._entered_segment: FlightSegment | None = None
        self.condition_match: ConditionMatch | None = None
        self.condition_matches: list[ConditionMatch] = []
        self.conditions_valid = True
        self.validate_conditions = validate_conditions

    @property
    def aircraft_profile_name(self) -> str:
        return self.aircraft_profile.name

    @property
    def engaged(self) -> bool:
        """Принимает ли стенд наши команды. До включения любой `step` уходит вхолостую."""
        return self.engagement.engaged

    # --- жизненный цикл эпизода ---

    def reset(
            self,
            scenario: "Scenario | None" = None,
            *,
            start: StartMode | None = None,
    ) -> "Telemetry":
        """Начало эпизода: сброс рукопожатия и первый кадр со стенда.

        Средой распоряжается Заказчик, поэтому сбрасывать здесь нечего — ни телепорта, ни
        погоды, ни отказов мы не задаём. `scenario` принимается только ради единообразия вызова
        из `RolloutEnv` и на состояние стенда не влияет.
        """
        self.engagement.reset()
        self._scenario = scenario
        self._entered_segment = None
        self.condition_match = None
        self.condition_matches.clear()
        self.conditions_valid = True
        frame = self.read_telemetry()
        if start == "taxi":
            self.engagement.arm_taxi_start()
        return frame

    def enter_segment(
        self,
        scenario: Scenario,
        segment: FlightSegment,
        telemetry: Telemetry | None = None,
    ) -> ConditionMatch:
        """Сверить ожидаемые условия; стендовые условия никогда не изменяются кодом."""
        frame = telemetry or self._last_telemetry or self.read_telemetry()
        report = replace(
            match_conditions(
                scenario.conditions_for(segment), frame.faults, frame.weather, segment),
            matrix_run_id=scenario.matrix_runs.get(segment),
            matrix_code=scenario.matrix_codes.get(segment),
        )
        initial = self._entered_segment is None
        self._scenario = scenario
        self._entered_segment = segment
        self.condition_match = report
        self.condition_matches.append(report)
        self.conditions_valid = self.conditions_valid and report.exact
        if self.validate_conditions and initial and not report.failures_match:
            missing = ", ".join(sorted(f.name for f in report.missing_failures)) or "—"
            unexpected = ", ".join(sorted(f.name for f in report.unexpected_failures)) or "—"
            raise RuntimeError(
                f"условия ICS не соответствуют сценарию {scenario.scenario_id!r}: "
                f"нет отказов [{missing}], лишние [{unexpected}]")
        if not report.failures_match or not report.weather_matches:
            logger.warning(
                "Условия участка %s отличаются от сценария %s: missing=%s unexpected=%s "
                "weather_distance=%.6f",
                segment.value, scenario.scenario_id,
                sorted(f.name for f in report.missing_failures),
                sorted(f.name for f in report.unexpected_failures), report.weather_distance,
            )
        return report

    def step(self, command: ControlsState) -> Telemetry:
        outputs = self._to_outputs(command)
        if self.connector.send_outputs(outputs):
            # Автомат узнаёт о ФАКТЕ передачи: выдержка по ICD — это время, в течение которого
            # стенд получает готовность, а не время, которое мы считаем у себя.
            self.engagement.on_frame_sent(outputs.ModeAIReady)
        return self.read_telemetry()

    def read_telemetry(self) -> Telemetry:
        inputs = self.connector.receive_inputs(timeout=self.timeout)
        telemetry = Telemetry.invalid() if inputs is None else Telemetry.from_ics(
            inputs,
            runway_profile=self.runway_profile,
            lateral_deviation_sign=self.aircraft_profile.ics_lateral_deviation_sign,
        )

        self._last_telemetry = telemetry
        self.engagement.step(self._engagement_inputs(telemetry))
        return telemetry

    def warm_up(self, timeout_s: float = 10.0, dt: float = DT) -> bool:
        """Гонит стимул рукопожатия, пока стенд не подтвердит включение (`AgentIsActive = 1`).

        Команда — нейтральная: до включения мы не управляем ВС, а лишь заявляем готовность.
        Стимул несёт `_to_outputs` из состояния автомата (`io/ics_engagement.py`):
        `ModeAIReady = 1` непрерывно и переход `ControlMode` (`Off` во время двухсекундной
        выдержки → `Taxi`, то есть `0 → 4`). Именно этот стимул стенд ждёт, чтобы выставить
        `AgentIsActive = 1`; до тех пор `ControlValidMask = 0`.

        Возврат — по факту подтверждения стендом (`self.engaged`), а не по нашей внутренней
        выдержке: иначе мы объявляли бы включение сами и могли «управлять» в пустоту. Исчерпание
        таймаута — исключение с диагностикой, а не молчаливый выход: приёмка иначе засчитала бы
        прогон, которого стенд не принял.
        """
        if self.engaged:
            return True

        neutral = ControlsState()
        start = time.monotonic()
        deadline = start + timeout_s
        next_send = start
        while time.monotonic() < deadline:
            now = time.monotonic()
            if now < next_send:
                # Темп отправки задаётся часами, а не тем, отработал ли sleep. Иначе при
                # неточном или подменённом sleep прогрев выпаливает десятки тысяч пакетов в
                # секунду — стенд рассчитан на 20 Гц.
                time.sleep(min(dt, max(0.0, next_send - now)))
                continue
            next_send = now + dt

            self.step(neutral)
            if self.engaged:
                logger.info("[ICS] управление включено: %s", self.engagement.as_dict())
                return True

        reason = self.engagement.blocking_reason(self._engagement_inputs(self._last_telemetry))
        raise TimeoutError(
            f"[ICS] стенд не включил управление за {timeout_s:.1f} с: {reason}. "
            f"Состояние автомата: {self.engagement.as_dict()}")

    def request_rollout(self) -> None:
        """Войти в пробег самостоятельно (`ControlMode 0 → 3`)."""
        self.engagement.request_rollout()

    def request_landing(self) -> bool:
        """Перейти `Approach → Landing`; сессия и воздушные каналы сохраняются."""
        return self.engagement.request_landing()

    def request_taxi(self) -> bool:
        """Передать управление в руление (`3 → 4`) — по решению вызывающего, что пробег окончен."""
        return self.engagement.request_taxi(self._engagement_inputs(self._last_telemetry))

    def __enter__(self) -> "ICSSim":
        return self

    def __exit__(self, exc_type, exc, traceback) -> bool:
        self.shutdown()
        return False

    def shutdown(self, frames: int = 10, dt: float = DT) -> ShutdownReport:
        if self._shutdown_report is not None:
            return self._shutdown_report
        actions: list[str] = []
        errors: list[str] = []
        try:
            self.deactivate(frames=frames, dt=dt)
            actions.append("controls_released")
        except Exception as exc:
            errors.append(f"deactivate: {type(exc).__name__}: {exc}")
            logger.exception("[ICS] ошибка снятия управления")
        try:
            self.engagement.reset()
            actions.append("engagement_reset")
        except Exception as exc:
            errors.append(f"engagement_reset: {type(exc).__name__}: {exc}")
        try:
            self.connector.close()
            actions.append("transport_closed")
        except Exception as exc:
            errors.append(f"transport_close: {type(exc).__name__}: {exc}")
            logger.exception("[ICS] ошибка закрытия транспорта")
        self._shutdown_report = ShutdownReport(
            backend=self.backend_name, actions=tuple(actions), errors=tuple(errors))
        return self._shutdown_report

    def close(self) -> None:
        self.shutdown()

    # --- внутреннее ---

    @staticmethod
    def _engagement_inputs(telemetry: Optional[Telemetry]) -> EngagementInputs:
        """Признаки для автомата включения.

        `agent_is_active` — подтверждение стенда: именно оно, а не наша выдержка, определяет факт
        включения. Путевая скорость — обратно в узлы (порог включения задан в узлах), но она и
        обжатие стоек здесь нужны лишь чтобы решить, **когда гнать стимул** (готовность + переход
        режима), а не чтобы объявлять себя включёнными.
        """
        if telemetry is None:
            return EngagementInputs(all_gear_on_ground=False, groundspeed_kts=0.0,
                                    telemetry_valid=False)
        return EngagementInputs(
            all_gear_on_ground=bool(telemetry.weight_on_wheels),
            groundspeed_kts=(telemetry.groundspeed_ms or 0.0) * Converts.MS_TO_KTS,
            flight_phase=telemetry.flight_phase,
            agent_is_active=1 if telemetry.agent_is_active else 0,
            telemetry_valid=telemetry.valid,
            radio_altitude_ft=telemetry.radio_altitude_ft,
        )

    @property
    def active_failures(self) -> frozenset[FailureMode]:
        """На стенде отказы приходят телеметрией, а не инжектируются нами."""
        return (frozenset(self._last_telemetry.faults)
                if self._last_telemetry else frozenset())

    def deactivate(self, frames: int = 10, dt: float = DT) -> None:
        """Снять управление: пустая маска и `ControlMode = Off` несколько кадров подряд.

        Не «замолчать» и не «выдать нули»: молчание оставляет последнее отклонение приложенным
        до сторожа стенда, а нули с заявленной маской — это по-прежнему команда (нулевое
        положение РУД в воздухе означает «малый газ», а не «управляй сам»). Пустая маска —
        единственный способ сказать «мы больше не отвечаем ни за один орган».

        Повтор нужен потому, что транспорт — UDP: одиночный пакет деактивации может потеряться,
        и тогда стенд останется ждать команд от того, кто уже вышел.
        """
        self.engagement.reset()
        packet = ICSOutputs(ControlValidMask=0, ControlMode=ControlModeState.Off, ModeAIReady=0)
        for i in range(max(1, frames)):
            self.connector.send_outputs(packet)
            if i + 1 < frames:
                time.sleep(dt)

    def _to_outputs(self, command: ControlsState) -> ICSOutputs:
        """`ControlsState` → `ICSOutputs` (единицы ICD), **по текущему участку полёта**.

        Три вещи, без которых стенд команду не исполнит:

        * `ControlValidMask` — какие каналы мы заявляем. Маска **зависит от режима**: в воздухе
          мы ведём руль высоты, элероны и РУД, на пробеге — тормоза, реверс и тиллер. Одна маска
          на весь полёт означала бы либо заявку колёсных тормозов в воздухе, либо руля высоты на
          пробеге — в обоих случаях ответственность за орган, который мы не формируем.
        * `ControlMode` и `ModeAIReady` — состояние рукопожатия, а не константы (см.
          `io/ics_engagement.py`). До включения команды органов не выдаются вовсе.
        * Единицы: тормоза в миллиметрах хода педали, руль и тиллер в градусах, реверс — углом
          РУД. Нормированные значения здесь дали бы ~1/37 от задуманного торможения.
        """
        out = ICSOutputs()
        mode = self.engagement.control_mode
        out.ControlMode = mode
        out.ModeAIReady = self.engagement.mode_ai_ready

        if not self.engagement.engaged:
            # Рукопожатие не завершено: заявлять каналы нельзя, иначе мы возьмём на себя
            # ответственность за органы, которыми стенд нам управлять ещё не разрешил.
            out.ControlValidMask = 0
            return out

        if mode in (ControlModeState.Approach, ControlModeState.Landing):
            self._fill_airborne(out, command)
        else:
            self._fill_ground(out, command)   # выбирает маску пробега или руления по режиму

        # Показатели качества выдерживания (ТЗ 5.1.5) — это отчёт, а не команда, и заявления
        # каналов не требуют.
        out.QualityLateralError = command.quality_lateral
        out.QualityHeadingError = command.quality_heading
        out.QualitySpeedError = command.quality_speed
        return out

    def _fill_airborne(self, out: ICSOutputs, command: ControlsState) -> None:
        """Воздушный участок: перегрузка, элероны и скорости РУД.

        `ModeFlare` повторяет подтверждённое окно 100–20 ft. Остальные фазовые флаги остаются
        нулевыми; `ModeSpeed`/`ModeThrust` держатся единицами — ими мы и управляем.
        """
        out.ControlValidMask = int(AIRBORNE_CONTROL_MASK)
        out.ElevatorCmd = command.cmd_elevator                      # g
        out.AileronCmd = _clamp(command.cmd_aileron, -AILERON_MAX_DEG, AILERON_MAX_DEG)
        out.RudderCmd = command.cmd_rudder * RUDDER_MAX_DEG
        out.ThrottleLeftRate = _clamp(command.cmd_throttle_l_rate,
                                      -THROTTLE_RATE_MAX_DEG_S, THROTTLE_RATE_MAX_DEG_S)
        out.ThrottleRightRate = _clamp(command.cmd_throttle_r_rate,
                                       -THROTTLE_RATE_MAX_DEG_S, THROTTLE_RATE_MAX_DEG_S)
        # Абсолютное положение маской не заявлено и в перечне команд Заказчика отсутствует —
        # но передаётся, потому что часть сборок стенда маску игнорирует, и тогда положение
        # должно совпадать с тем, куда ведёт скорость, а не спорить с ней. На таком прогоне
        # заход коллеги и был подтверждён.
        out.ThrottleLeft = command.cmd_throttle_norm
        out.ThrottleRight = command.cmd_throttle_norm
        ra = getattr(self._last_telemetry, "radio_altitude_ft", None)
        out.ModeFlare = int(
            ra is not None
            and FLARE_MODE_END_RADIO_ALTITUDE_FT < ra <= FLARE_MODE_RADIO_ALTITUDE_FT
        )
        out.ModeSpeed = 1
        out.ModeThrust = 1

    def _fill_ground(self, out: ICSOutputs, command: ControlsState) -> None:
        """Пробег и руление: тормоза, путевое управление, реверс.

        Путевой орган **зависит от режима**: на пробеге это педальный пост (±75 мм) вместе с
        аэродинамическим рулём, на рулении — тиллер (±65 мм). Так их и разделяет таблица
        управляющих сигналов Заказчика, и это не формальность: на скорости пробега тиллер
        отклонять нельзя, а на скорости руления руль направления бесполезен.
        """
        taxi = out.ControlMode is ControlModeState.Taxi
        out.ControlValidMask = int(TAXI_CONTROL_MASK if taxi else ROLLOUT_CONTROL_MASK)
        out.ModeRollout = 1 if out.ControlMode is ControlModeState.Rollout else 0
        out.ModeTaxi = 1 if taxi else 0

        # Тормоза: [0, 1] → ход КОМАНДЫ педали в мм (45 мм, не 36.73 — то шкала обратной связи).
        out.BrakeLeftCmd = command.cmd_brake_l * BRAKE_CMD_MAX_MM
        out.BrakeRightCmd = command.cmd_brake_r * BRAKE_CMD_MAX_MM

        if taxi:
            out.NoseWheelTillerCmd = command.cmd_tiller * TILLER_MAX_MM
        else:
            out.RudderCmd = command.cmd_rudder * RUDDER_MAX_DEG
            out.RudderPedalCmd = command.cmd_pedal * RUDDER_PEDAL_MAX_MM

        # Реверс: команда [-1, 0] — это желаемый уровень обратной тяги. Задаётся он **скоростью**
        # перемещения РУД (единственный документированный канал управления тягой), а не записью
        # абсолютного угла: позиционный контур ведёт фактический РУД к цели, `ReverseXCmd`
        # открывает створки.
        angle_l = self._throttle_angle(left=True)
        angle_r = self._throttle_angle(left=False)
        out.ThrottleLeftRate = _throttle_rate(command.cmd_rev_l, angle_l)
        out.ThrottleRightRate = _throttle_rate(command.cmd_rev_r, angle_r)
        out.ReverseLeftCmd = (ReverseEngineType.Deploy if command.cmd_rev_l < 0
                              else ReverseEngineType.Off)
        out.ReverseRightCmd = (ReverseEngineType.Deploy if command.cmd_rev_r < 0
                               else ReverseEngineType.Off)

    def _throttle_angle(self, *, left: bool) -> float:
        """Фактический угол РУД из последнего кадра стенда; 0 при отсутствии кадра.

        Обратная связь позиционного контура. Без кадра нулевой угол означает «малый газ» — это
        безопасное предположение: контур в худшем случае даст полную скорость на выпуск реверса,
        которую стенд всё равно отработает физически.
        """
        i = getattr(self._last_telemetry, "ics_inputs", None)
        if i is None:
            return 0.0
        return i.LeftThrottleAngle if left else i.RightThrottleAngle
