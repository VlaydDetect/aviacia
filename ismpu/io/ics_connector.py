"""UDP-мост к стенду заказчика (порт 3030) — транспорт пути поставки.

`ICSInputs` — телеметрия, которую шлёт стенд; `ICSOutputs` — структура управления обратно.

**Кодировка подтверждена разработчиком стенда:** `Struct → Newtonsoft.Json.JsonConvert → string →
Encoding.UTF8.GetBytes()`, адрес берётся из UDP-заголовка входящего пакета. То есть на проводе
**чистый JSON**: ни заголовка, ни CRC, ни серийных номеров. Никакого кадрирования на нашей стороне
быть не должно — добавленные перед payload байты сломали бы разбор на стороне стенда.

Единицы, пределы органов и биты маски валидности — в `config/ics.py`.
"""

import socket
import json
import logging
import time
from enum import IntEnum
from dataclasses import dataclass, asdict, fields
from typing import Callable, Optional

logger = logging.getLogger(__name__)

LISTEN_IP_ANY = "0.0.0.0"
"""Адрес прослушивания по умолчанию. Именно `0.0.0.0`, а не `127.0.0.1`: стенд может стоять на
другой машине, и тогда петлевой адрес не принял бы от него ни одного пакета. Локальный запуск
`0.0.0.0` покрывает тоже."""


class GearState(IntEnum):
    """Дискретное положение стойки в кодировке ICSInputs."""

    NoneState = 0
    UpLock = 1
    Move = 2
    DownLock = 3


class ControlModeState(IntEnum):
    """Режим управления/индикации, передаваемый в каждом ICSOutputs."""

    Off = 0
    Approach = 1
    Landing = 2
    Rollout = 3
    Taxi = 4
    ManualTest = 5


class ReverseEngineType(IntEnum):
    """Состояние створок реверса; величину задаёт отрицательный throttle rate."""

    Off = 0
    Arm = 1
    Deploy = 2


@dataclass
class ICSInputs:
    """Полная известная входная схема стенда; единицы определены в ``ICSInterface.cs``."""

    AgentIsActive: int

    # Фаза полета
    FlightPhaseValid: int
    FlightPhase: int

    # Координаты
    LatitudeValid: int
    Latitude: float
    LongitudeValid: int
    Longitude: float

    # Высота
    RadioAltitudeValid: int
    RadioAltitude: float
    BaroAltitudeValid: int
    BaroAltitude: float

    # Скорости
    IndicatedAirspeedValid: int
    IndicatedAirspeed: float
    TrueAirspeedValid: int
    TrueAirspeed: float
    GroundSpeedValid: int
    GroundSpeed: float
    VerticalSpeedValid: int
    VerticalSpeed: float

    # Углы и курс
    PitchAngleValid: int
    PitchAngle: float
    RollAngleValid: int
    RollAngle: float
    MagneticHeadingValid: int
    MagneticHeading: float
    TrueHeadingValid: int
    TrueHeading: float
    TrkAngleMagneticValid: int
    TrkAngleMagnetic: float
    TrkAngleTrueValid: int
    TrkAngleTrue: float

    # Угловые скорости и ускорения
    BodyPitchRateValid: int
    BodyPitchRate: float
    BodyRollRateValid: int
    BodyRollRate: float
    BodyYawRateValid: int
    BodyYawRate: float
    BodyNormAccelValid: int
    BodyNormAccel: float
    BodyLongAccelValid: int
    BodyLongAccel: float
    BodyLatAccelValid: int
    BodyLatAccel: float

    # Параметры ВПП и отклонения
    RunwayHeadingValid: int
    RunwayHeading: float
    RunwayLength: float
    RunwayWidth: float
    LateralDeviation: float
    LocDeviationValid: int
    LocDeviation: float
    GSDeviationValid: int
    GSDeviation: float

    # Шасси и обжатие
    NoseGearStatus: GearState
    LeftGearStatus: GearState
    RightGearStatus: GearState
    NoseGearWeightOnWheels: int
    LeftGearWeightOnWheels: int
    RightGearWeightOnWheels: int
    NoseWheelAngle: float

    # Механизация и управляющие поверхности
    SlatsAngle: float
    FlapsAngle: float
    StabilizerAngle: float
    ElevatorLeftAngle: float
    ElevatorRightAngle: float
    AileronLeftAngle: float
    AileronRightAngle: float
    RudderAngle: float

    # Двигатели и РУД
    EngLeftThrust: float
    EngRigntThrust: float
    LeftThrottleAngle: float
    RightThrottleAngle: float

    # Тормоза и интерцепторы
    LeftBrakePedal: float
    RightBrakePedal: float
    LeftSpoiler1: float
    LeftSpoiler2: float
    LeftSpoiler3: float
    LeftSpoiler4: float
    LeftAirBrake: float
    RightSpoiler1: float
    RightSpoiler2: float
    RightSpoiler3: float
    RightSpoiler4: float
    RightAirBrake: float

    # Окружающая среда
    WindDirectionTrue: float
    WindSpeed: float
    Visibility: float
    PrecipitationRatio: float
    RunwayCondition: int
    AirfieldTemp: float

    # Сигналы отказов
    FaultLeftEngine: int
    FaultRightEngine: int
    FaultLeftEngineReverse: int
    FaultRightEngineReverse: int
    FaultLeftLandingGear: int
    FaultRightLandingGear: int
    FaultNoseLandingGear: int
    FaultLeftStab: int
    FaultRightStab: int
    FaultNWS: int

    @classmethod
    def from_dict(cls, data: dict) -> 'ICSInputs':
        """Разбор телеметрии стенда с совместимостью вперёд.

        Асимметрия намеренная (JSON-аналог дописывания полей в бинарный payload):
        **лишние** ключи сохраняются для аудита — стенд может добавить сигнал, и нас это не
        должно ронять;
        **отсутствующие** ключи — ошибка. Подставить им ноль значило бы выдумать телеметрию,
        по которой потом считается управление.
        """
        known = {f.name for f in fields(cls)}
        missing = known - set(data)
        if missing:
            raise ValueError(f"[ICS] в пакете стенда нет обязательных полей: {sorted(missing)}")

        payload = {k: v for k, v in data.items() if k in known}
        # Конвертируем сырые значения в IntEnum, где это необходимо
        for gear_field in ('NoseGearStatus', 'LeftGearStatus', 'RightGearStatus'):
            payload[gear_field] = GearState(payload[gear_field])
        result = cls(**payload)
        # Не объявляем extras полем dataclass: публичная схема остаётся ровно той же, что у
        # стенда (99 полей), а будущие добавления всё равно не теряются в RunRecorder.
        result._raw_fields = {k: v for k, v in data.items() if k not in known}
        return result

    @property
    def raw_fields(self) -> dict[str, object]:
        """Неизвестные поля исходного JSON; они доступны аудиту, но не закону управления."""
        return dict(getattr(self, "_raw_fields", {}))


@dataclass
class ICSOutputs:
    """Команды и mode flags, сериализуемые ровно в ожидаемый стендом JSON."""

    ControlValidMask: int = 0
    """По умолчанию **не заявлен ни один канал**. Прежняя единица означала, что каждый пакет,
    собранный без явной маски (в том числе пакет деактивации), заявлял руль высоты со значением
    0.0 — то есть выдавал команду там, где мы намеревались молчать."""
    ControlMode: ControlModeState = ControlModeState.Off
    ElevatorCmd: float = 0.0
    AileronCmd: float = 0.0
    RudderCmd: float = 0.0
    ThrottleLeftRate: float = 0.0
    ThrottleRightRate: float = 0.0
    ThrottleLeft: float = 0.0
    ThrottleRight: float = 0.0
    NoseWheelTillerCmd: float = 0.0
    RudderPedalCmd: float = 0.0
    BrakeLeftCmd: float = 0.0
    BrakeRightCmd: float = 0.0
    AirbrakeCmd: float = 0.0
    ReverseLeftCmd: ReverseEngineType = ReverseEngineType.Off
    ReverseRightCmd: ReverseEngineType = ReverseEngineType.Off
    ModeAIReady: int = 0
    ModeLocCapture: int = 0
    ModeLocTrack: int = 0
    ModeGSCapture: int = 0
    ModeGSTrack: int = 0
    ModeFlareArm: int = 0
    ModeFlare: int = 0
    ModeAlignArm: int = 0
    ModeAlign: int = 0
    ModeRolloutArm: int = 0
    ModeRollout: int = 0
    ModeTaxiArm: int = 0
    ModeTaxi: int = 0
    ModeSpeed: int = 0
    ModeThrust: int = 0
    WarningFlags: int = 0
    QualityLateralError: float = 0.0
    QualityHeadingError: float = 0.0
    QualitySpeedError: float = 0.0

    reserved: str = ""

    def to_json_bytes(self) -> bytes:
        """Сериализовать enums и 14 reserved zeros в точные UTF‑8 bytes wire contract."""
        dict_data = asdict(self)
        # Преобразуем Enums обратно в их целочисленные значения перед сериализацией
        dict_data['ControlMode'] = int(dict_data['ControlMode'])
        dict_data['ReverseLeftCmd'] = int(dict_data['ReverseLeftCmd'])
        dict_data['ReverseRightCmd'] = int(dict_data['ReverseRightCmd'])

        dict_data['reserved'] = [0] * 14

        json_str = json.dumps(dict_data, ensure_ascii=False)
        return json_str.encode('utf-8')


class ResilientSender:
    """Отправка best-effort со счётчиком ошибок и разрежённым логом.

    Windows отдаёт `WSAECONNRESET` (10054) на UDP-сокете, если получатель закрыл порт: ICMP
    «port unreachable» всплывает как ошибка на следующей отправке, хотя UDP не соединение.
    Ронять из-за этого цикл управления нельзя, но и молчать нельзя — отсюда счётчик и лог не
    чаще раза в `log_interval_s`.
    """

    WINDOWS_CONNRESET = 10054

    def __init__(self, sock, *, log_interval_s: float = 2.0, clock=time.monotonic):
        self.sock = sock
        self.log_interval_s = log_interval_s
        self._clock = clock
        self.error_count = 0
        self._last_log = None

    def send(self, packet: bytes, address) -> bool:
        """→ True если отправлено. Исключение наружу не выпускается."""
        try:
            self.sock.sendto(packet, address)
            return True
        except OSError as exc:
            self.error_count += 1
            now = self._clock()
            if self._last_log is None or (now - self._last_log) >= self.log_interval_s:
                self._last_log = now
                kind = ("сброс соединения (порт получателя закрыт)"
                        if getattr(exc, "winerror", None) == self.WINDOWS_CONNRESET
                        or getattr(exc, "errno", None) == self.WINDOWS_CONNRESET
                        else "ошибка отправки")
                logger.warning("[ICS] %s: %s (всего ошибок: %d)", kind, exc, self.error_count)
            return False


class ICSBenchConnector:
    """Мост к стенду: JSON поверх UDP, адрес стенда определяется из входящего пакета."""

    def __init__(self, listen_ip: str, listen_port: int, *, sock=None):
        self.listen_addr = (listen_ip, listen_port)

        # Адрес стенда определится из заголовка входящего пакета
        self.send_addr: Optional[tuple[str, int]] = None

        self.sock = sock if sock is not None else socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if sock is None:
            self.sock.bind(self.listen_addr)

        self._sender = ResilientSender(self.sock)
        self._packet_observer: Callable[[str, bytes, tuple[str, int]], None] | None = None
        self.last_received_packet: bytes | None = None
        self.last_sent_packet: bytes | None = None

    def set_packet_observer(
        self,
        observer: Callable[[str, bytes, tuple[str, int]], None] | None,
    ) -> None:
        """Подключить best-effort аудит сырых успешно принятых/отправленных UDP payload."""
        self._packet_observer = observer

    def _observe(self, direction: str, packet: bytes, address: tuple[str, int]) -> None:
        observer = self._packet_observer
        if observer is None:
            return
        try:
            observer(direction, packet, address)
        except Exception:
            # Аудит не имеет права разомкнуть контур управления.
            logger.exception("[ICS] ошибка записи сырого %s-пакета", direction)

    def receive_inputs(self, timeout: float = 1.0) -> Optional[ICSInputs]:
        """Приём телеметрии стенда. Адрес отправителя определяется автоматически."""
        self.sock.settimeout(timeout)
        try:
            data, sender_addr = self.sock.recvfrom(65535)
        except socket.timeout:
            return None
        except OSError as e:
            logger.warning("[ICS] Ошибка приёма: %s", e)
            return None

        self.last_received_packet = data
        self._observe("rx", data, sender_addr)

        if self.send_addr != sender_addr:
            self.send_addr = sender_addr
            print(f"[ICS] Удаленный адрес стенда определен автоматически: "
                  f"{self.send_addr[0]}:{self.send_addr[1]}")

        try:
            return ICSInputs.from_dict(json.loads(data.decode('utf-8')))
        except Exception as e:
            logger.warning("[ICS] Ошибка десериализации данных от стенда: %s", e)
            return None

    def send_outputs(self, outputs: ICSOutputs) -> bool:
        """Отправка управления на стенд. → отправлено ли (исключение наружу не выпускается)."""
        if self.send_addr is None:
            logger.warning("[ICS] Отправка невозможна: адрес стенда ещё не определён "
                           "(не получено ни одного входящего сообщения).")
            return False
        packet = outputs.to_json_bytes()
        sent = self._sender.send(packet, self.send_addr)
        if sent:
            self.last_sent_packet = packet
            self._observe("tx", packet, self.send_addr)
        return sent

    @property
    def send_error_count(self) -> int:
        """Число последовательных best-effort ошибок текущего sender."""
        return self._sender.error_count

    def close(self):
        """Освободить единственный UDP-сокет коннектора."""
        self.sock.close()
