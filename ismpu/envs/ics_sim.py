"""Стенд заказчика как источник телеметрии и приёмник команд.

Единственный «симулятор» проекта: контур, среда обучения и актор работают против стенда по
ПИВ (JSON/UDP, `io/ics_connector.py`). Абстракции «выбери бэкенд» здесь нет и не нужно —
поставка идёт на стенд, и второго транспорта не существует.

Два класса:

* `Telemetry` — телеметрия в **СИ**. Стенд шлёт узлы, футы, футы/мин и градусы/с (см.
  `ICSInterface.cs`), контур и наблюдение работают в СИ; граница пересчёта проходит ровно
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
from dataclasses import dataclass
from typing import Optional

from ismpu.io.ics_connector import (
    ICSBenchConnector, ICSInputs, ICSOutputs, ControlModeState, ReverseEngineType,
)
from ismpu.io.ics_engagement import IcsEngagement, EngagementInputs
from ismpu.config.ics import (
    BRAKE_PEDAL_MAX_MM, THROTTLE_ANGLE_MIN_DEG, TILLER_MAX_DEG, RUDDER_MAX_DEG,
    ROLLOUT_CONTROL_MASK,
)
from ismpu.utils.converts import Converts
from ismpu.config.constants import DT
from ismpu.control.channels import ControlsState
from ismpu.control.failures import FailureMode
from ismpu.envs.weather import WeatherState

logger = logging.getLogger(__name__)


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
    lat: float
    lon: float
    groundspeed_ms: float
    heading_true_deg: float
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

    # «Сырой» пакет стенда — единственный источник сигналов ниже (None, если связи нет).
    ics_inputs: Optional[ICSInputs] = None

    valid: bool = True   # False — телеметрии нет (таймаут приёма)

    @classmethod
    def from_ics(cls, inp: ICSInputs) -> "Telemetry":
        """`ICSInputs` → `Telemetry`: поля в СИ + «сырой» пакет для property.

        Стенд отдаёт узлы, футы, футы/мин и градусы/с. Пропущенный здесь перевод — не косметика:
        путевая скорость в узлах, положенная в поле м/с, даёт ошибку в 1.94 раза, и продольный
        канал прочитает 140 узлов как 272 и немедленно даст полное торможение.
        """
        return cls(
            lat=inp.Latitude,
            lon=inp.Longitude,
            groundspeed_ms=inp.GroundSpeed * Converts.KTS_TO_MS,        # kt → м/с
            heading_true_deg=inp.TrueHeading,
            pitch_deg=inp.PitchAngle,
            roll_deg=inp.RollAngle,
            elevation_m=inp.BaroAltitude * Converts.FT_TO_M,            # ft → м
            agl_m=inp.RadioAltitude * Converts.FT_TO_M,                 # ft → м
            vy_ms=inp.VerticalSpeed * Converts.FTM_TO_MS,               # ft/min → м/с
            p_rad=math.radians(inp.BodyRollRate),                       # deg/s → рад/с
            q_rad=math.radians(inp.BodyPitchRate),
            r_rad=math.radians(inp.BodyYawRate),
            accel_long_g=inp.BodyLongAccel,
            accel_norm_g=inp.BodyNormAccel,
            accel_side_g=inp.BodyLatAccel,
            wind_speed_ms=inp.WindSpeed * Converts.KTS_TO_MS,           # kt → м/с
            wind_dir_from_deg=inp.WindDirectionTrue,
            ics_inputs=inp,
        )

    @classmethod
    def invalid(cls) -> "Telemetry":
        """Кадр «связи со стендом нет». Нули, а не None: контур проверяет `valid` первым."""
        return cls(lat=0.0, lon=0.0, groundspeed_ms=0.0, heading_true_deg=0.0, valid=False)

    # --- сигналы стенда: выводятся из ics_inputs, отдельно не хранятся --- #

    @property
    def ias_ms(self) -> Optional[float]:
        """Приборная скорость (kt → м/с). Отсечки реверса заданы по ней, а не по путевой."""
        return self.ics_inputs.IndicatedAirspeed * Converts.KTS_TO_MS if self.ics_inputs else None

    @property
    def runway_heading_deg(self) -> Optional[float]:
        i = self.ics_inputs
        return i.RunwayHeading if (i is not None and i.RunwayHeadingValid) else None

    @property
    def runway_length_m(self) -> Optional[float]:
        return self.ics_inputs.RunwayLength if self.ics_inputs else None

    @property
    def runway_width_m(self) -> Optional[float]:
        return self.ics_inputs.RunwayWidth if self.ics_inputs else None

    @property
    def lateral_deviation_m(self) -> Optional[float]:
        """Боковое отклонение от оси, измеренное стендом. Позволяет не считать геодезию самим."""
        return self.ics_inputs.LateralDeviation if self.ics_inputs else None

    @property
    def weight_on_wheels(self) -> Optional[bool]:
        """Обжатие ВСЕХ стоек. Диагностический сигнал; условие включения проверяет сам стенд."""
        i = self.ics_inputs
        if i is None:
            return None
        return bool(i.NoseGearWeightOnWheels and i.LeftGearWeightOnWheels and i.RightGearWeightOnWheels)

    @property
    def flight_phase(self) -> Optional[int]:
        """Фаза полёта по `config.ics.FlightPhase` — по ней распознаётся уже идущий пробег."""
        i = self.ics_inputs
        return i.FlightPhase if (i is not None and i.FlightPhaseValid) else None

    @property
    def faults(self) -> frozenset:
        """Отказы, о которых сообщает борт — **единственный** источник истины об отказах.

        Раньше отказы задавались сценарием и моделировались нами; на стенде они приходят
        телеметрией, и выдумывать их на своей стороне значит управлять по несуществующей
        конфигурации.
        """
        return _faults_from_inputs(self.ics_inputs) if self.ics_inputs else frozenset()

    @property
    def weather(self) -> Optional[WeatherState]:
        """Фактические погодные условия со стенда (ветер, сцепление, осадки, видимость)."""
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


class ICSSim:
    """Обмен со стендом заказчика: телеметрия внутрь, команды наружу.

    Управление включается **только** после рукопожатия (`io/ics_engagement.py`). Факт включения
    определяет **стенд**, а не мы: он подтверждает приём управления полем `AgentIsActive = 1` во
    входной телеметрии. Наша задача в прогреве — гнать корректный стимул (`ModeAIReady = 1`
    непрерывно и переход `ControlMode`), а `engaged` лишь читает подтверждение стенда. Пока его
    нет, `ControlValidMask = 0` и органы не выдаются.
    """

    def __init__(self, connector: Optional[ICSBenchConnector] = None,
                 listen_ip: str = "127.0.0.1", listen_port: int = 3030, timeout: float = 1.0,
                 engagement: Optional[IcsEngagement] = None):
        self.connector = connector if connector is not None else ICSBenchConnector(listen_ip, listen_port)
        self.timeout = timeout
        self.engagement = engagement if engagement is not None else IcsEngagement()
        self._last_telemetry: Optional[Telemetry] = None

    @property
    def engaged(self) -> bool:
        """Принимает ли стенд наши команды. До включения любой `step` уходит вхолостую."""
        return self.engagement.engaged

    # --- жизненный цикл эпизода ---

    def reset(self, scenario=None) -> Telemetry:
        """Начало эпизода: сброс рукопожатия и первый кадр со стенда.

        Средой распоряжается Заказчик, поэтому сбрасывать здесь нечего — ни телепорта, ни
        погоды, ни отказов мы не задаём. `scenario` принимается только ради единообразия вызова
        из `RolloutEnv` и на состояние стенда не влияет.
        """
        self.engagement.reset()
        return self.read_telemetry()

    def step(self, command: ControlsState) -> Telemetry:
        outputs = self._to_outputs(command)
        if self.connector.send_outputs(outputs):
            # Автомат узнаёт о ФАКТЕ передачи: выдержка по ICD — это время, в течение которого
            # стенд получает готовность, а не время, которое мы считаем у себя.
            self.engagement.on_frame_sent(outputs.ModeAIReady)
        return self.read_telemetry()

    def read_telemetry(self) -> Telemetry:
        inputs = self.connector.receive_inputs(timeout=self.timeout)
        telemetry = Telemetry.invalid() if inputs is None else Telemetry.from_ics(inputs)

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

    def request_taxi(self) -> bool:
        """Передать управление в руление (`3 → 4`) — по решению вызывающего, что пробег окончен."""
        return self.engagement.request_taxi(self._engagement_inputs(self._last_telemetry))

    def close(self) -> None:
        self.connector.close()

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
        )

    @property
    def active_failures(self) -> set:
        """На стенде отказы приходят телеметрией, а не инжектируются нами."""
        return set(self._last_telemetry.faults) if self._last_telemetry else set()

    def _to_outputs(self, command: ControlsState) -> ICSOutputs:
        """`ControlsState` (нормированные) → `ICSOutputs` (единицы ICD).

        Три вещи, без которых стенд команду не исполнит:

        * `ControlValidMask` — какие каналы мы вообще заявляем. Пустая маска бессмысленна:
          команда без заявленных каналов ничего не значит.
        * `ControlMode` и `ModeAIReady` — состояние рукопожатия, а не константы (см.
          `io/ics_engagement.py`). До включения команды органов не выдаются вовсе.
        * Единицы: тормоза в миллиметрах хода педали, руль и тиллер в градусах, реверс — углом
          РУД. Нормированные значения здесь дали бы ~1/37 от задуманного торможения.
        """
        out = ICSOutputs()
        out.ControlMode = self.engagement.control_mode
        out.ModeAIReady = self.engagement.mode_ai_ready
        out.ModeRollout = 1 if out.ControlMode is ControlModeState.Rollout else 0
        out.ModeTaxi = 1 if out.ControlMode is ControlModeState.Taxi else 0

        if not self.engagement.engaged:
            # Рукопожатие не завершено: заявлять каналы нельзя, иначе мы возьмём на себя
            # ответственность за органы, которыми стенд нам управлять ещё не разрешил.
            out.ControlValidMask = 0
            return out

        out.ControlValidMask = int(ROLLOUT_CONTROL_MASK)

        # Тормоза: [0, 1] → ход педали в мм.
        out.BrakeLeftCmd = command.cmd_brake_l * BRAKE_PEDAL_MAX_MM
        out.BrakeRightCmd = command.cmd_brake_r * BRAKE_PEDAL_MAX_MM

        # Путевое управление: руль направления и передняя стойка — оба в градусах.
        out.RudderCmd = command.rudder_cmd * RUDDER_MAX_DEG
        out.NoseWheelTillerCmd = command.rudder_cmd * TILLER_MAX_DEG

        # Реверс: команда [-1, 0] → отрицательный угол РУД (обратная тяга). Створки реверса —
        # отдельный сигнал: угол задаёт величину, `ReverseXCmd` — состояние механизации.
        out.ThrottleLeft = -command.cmd_rev_l * THROTTLE_ANGLE_MIN_DEG
        out.ThrottleRight = -command.cmd_rev_r * THROTTLE_ANGLE_MIN_DEG
        out.ReverseLeftCmd = (ReverseEngineType.Deploy if command.cmd_rev_l < 0
                              else ReverseEngineType.Off)
        out.ReverseRightCmd = (ReverseEngineType.Deploy if command.cmd_rev_r < 0
                               else ReverseEngineType.Off)
        return out
