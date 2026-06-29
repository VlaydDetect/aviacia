import socket
import json
from enum import IntEnum
from dataclasses import dataclass, asdict
from typing import Optional


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
        # Конвертируем сырые значения в IntEnum, где это необходимо
        if 'NoseGearStatus' in data:
            data['NoseGearStatus'] = GearState(data['NoseGearStatus'])
        if 'LeftGearStatus' in data:
            data['LeftGearStatus'] = GearState(data['LeftGearStatus'])
        if 'RightGearStatus' in data:
            data['RightGearStatus'] = GearState(data['RightGearStatus'])
        return cls(**data)


@dataclass
class ICSOutputs:
    ControlValidMask: int = 0
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


class ICSBenchConnector:
    def __init__(self, listen_ip: str, listen_port: int):
        self.listen_addr = (listen_ip, listen_port)

        # Адрес стенда определится из заголовка входящего пакета
        self.send_addr: Optional[tuple[str, int]] = None

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(self.listen_addr)

    def receive_inputs(self, timeout: float = 1.0) -> Optional[ICSInputs]:
        """
        Ожидание и получение структуры ICSInputs от стенда.
        Автоматически извлекает адрес стенда из заголовка UDP-пакета.
        """
        self.sock.settimeout(timeout)
        try:
            # Получаем данные и кортеж (IP, Port) отправителя (стенда)
            data, sender_addr = self.sock.recvfrom(65535)

            if self.send_addr != sender_addr:
                self.send_addr = sender_addr
                print(f"[ICS] Удаленный адрес стенда определен автоматически: {self.send_addr[0]}:{self.send_addr[1]}")

            json_str = data.decode('utf-8')
            parsed_dict = json.loads(json_str)
            return ICSInputs.from_dict(parsed_dict)

        except socket.timeout:
            return None
        except Exception as e:
            print(f"[ICS] Ошибка десериализации данных от стенда: {e}")
            return None

    def send_outputs(self, outputs: ICSOutputs):
        """
        Отправка структуры ICSOutputs на стенд.
        Выполняется только в том случае, если адрес стенда уже был определен.
        """
        if self.send_addr is None:
            print("[ICS] Ошибка отправки: адрес стенда еще не определен (не получено ни одного входящего сообщения).")
            return

        try:
            packet = outputs.to_json_bytes()
            self.sock.sendto(packet, self.send_addr)
        except Exception as e:
            print(f"[ICS] Ошибка отправки данных на стенд {self.send_addr}: {e}")

    def close(self):
        self.sock.close()


def main():
    connector = ICSBenchConnector(listen_ip="127.0.0.1", listen_port=3030)

    print("Интерфейс ICS запущен. Ожидание данных от стенда...")

    connector.receive_inputs(timeout=2.0)

    try:
        while True:
            # # 1. Принимаем телеметрию (Входные сигналы)
            # inputs = connector.receive_inputs(timeout=2.0)
            #
            # if inputs is None:
            #     print("Таймаут ожидания данных от стенда.")
            #     continue

            # 3. Формируем ответ (Выходные сигналы)
            outputs = ICSOutputs()
            outputs.ControlValidMask = 0
            outputs.ControlMode = ControlModeState.ManualTest
            outputs.ElevatorCmd = -0.1

            # 4. Отправляем управление обратно на стенд
            connector.send_outputs(outputs)

    except KeyboardInterrupt:
        print("\nИнтерфейс остановлен пользователем.")
    finally:
        connector.close()