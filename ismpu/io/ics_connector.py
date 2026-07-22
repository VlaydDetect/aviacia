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
from typing import Optional

logger = logging.getLogger(__name__)

LISTEN_IP_ANY = "0.0.0.0"
"""Адрес прослушивания по умолчанию. Именно `0.0.0.0`, а не `127.0.0.1`: стенд может стоять на
другой машине, и тогда петлевой адрес не принял бы от него ни одного пакета. Локальный запуск
`0.0.0.0` покрывает тоже."""


class GearState(IntEnum):
    NoneState = 0
    UpLock = 1
    Move = 2
    DownLock = 3


class ControlModeState(IntEnum):
    Off = 0
    Approach = 1
    Landing = 2
    Rollout = 3
    Taxi = 4
    ManualTest = 5


class ReverseEngineType(IntEnum):
    Off = 0
    Arm = 1
    Deploy = 2


@dataclass
class ICSInputs:
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
        **лишние** ключи игнорируются — стенд может добавить сигнал, и нас это не должно ронять;
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
        return cls(**payload)


@dataclass
class ICSOutputs:
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
        return self._sender.send(outputs.to_json_bytes(), self.send_addr)

    @property
    def send_error_count(self) -> int:
        return self._sender.error_count

    def close(self):
        self.sock.close()


def main():
    """Диагностический приём телеметрии. Управление отсюда **не выдаётся**.

    Прежняя версия гнала `ElevatorCmd = 200.0` в цикле без пауз. В единицах ICD это 200 g —
    команда вне физического смысла, да ещё и с неограниченным темпом отправки. Для проверки
    авторитета органов есть отдельные инструменты; точка входа транспорта должна только читать.
    """
    connector = ICSBenchConnector(listen_ip=LISTEN_IP_ANY, listen_port=3030)
    print("Интерфейс ICS запущен. Ожидание данных от стенда...")
    try:
        while True:
            inputs = connector.receive_inputs(timeout=2.0)
            if inputs is None:
                print("[ICS] телеметрии нет")
                continue
            print(f"[ICS] active={inputs.AgentIsActive} phase={inputs.FlightPhase} "
                  f"ra={inputs.RadioAltitude:.1f} ias={inputs.IndicatedAirspeed:.1f} "
                  f"gs={inputs.GroundSpeed:.1f} wow="
                  f"{inputs.NoseGearWeightOnWheels}/{inputs.LeftGearWeightOnWheels}/"
                  f"{inputs.RightGearWeightOnWheels}")
    except KeyboardInterrupt:
        print("\nИнтерфейс остановлен пользователем.")
    finally:
        connector.close()


if __name__ == "__main__":
    main()