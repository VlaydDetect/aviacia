"""Единый интерфейс взаимодействия с симулятором и два бэкенда.

`SimInterface` (ABC) скрывает транспорт: контур/среда/актор работают только с ним.
Два бэкенда:

- `XPlaneBackend` — обучение на X-Plane 12 (обёртка над `XPlaneConnectX`): телеметрия
  через `subscribeDREFs`, команды через `sendDREF`, телепорт/пауза, погода через
  `WeatherManager`, инъекция отказов через failure-DataRef'ы (двигатели/реверс).
- `ICSBackend` — поставка на стенд Заказчика (обёртка над `ICSBenchConnector`):
  телеметрия из `ICSInputs`, команды в `ICSOutputs` по ПИВ. Погоду/отказы/телепорт
  задаёт стенд, поэтому соответствующие методы — no-op (среда управляется Заказчиком).

Слой: `envs/` (выше `io/`), т.к. интерфейс зависит от `WeatherState` (envs),
`FailureMode`/`ControlsState` (control) и `Scenario` (envs) — держать его в `io/`
нарушило бы правило «io = только транспорт».

Единицы `Telemetry`: СИ (м, м/с, рад/с, °, g). Отсутствующие у бэкенда поля — None.
"""

import time
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

import numpy as np

from ismpu.io.xplane_connector import XPlaneConnectX
from ismpu.io.ics_connector import (
    ICSBenchConnector, ICSInputs, ICSOutputs, ControlModeState, ReverseEngineType,
)
from ismpu.io.datarefs import (
    LATITUDE, LONGITUDE, GROUNDSPEED, TRUE_PSI, TRUE_THETA, TRUE_PHI, ELEVATION, Y_AGL,
    LOCAL_VX, LOCAL_VY, LOCAL_VZ, PRAD, QRAD, RRAD, G_AXIL, G_NRML, G_SIDE,
    WX_AC_WIND_SPEED_MSC, WX_AC_WIND_DIR_DEGT,
    FAIL_ENGINE, FAIL_REVERSER, FAILURE_ENUM_OK, FAILURE_ENUM_INOP,
    POS_P, POS_Q, POS_R, TOTAL_FLIGHT_TIME, SIM_SPEED_ACTUAL,
)

logger = logging.getLogger(__name__)
from ismpu.utils.converts import Converts
from ismpu.config.constants import FREQ
from ismpu.config.runway import (
    RWY_START_LAT, RWY_START_LON, RWY_HEADING_TRUE, ELEVATION_MSL, ELEVATION_AIRCRAFT,
)
from ismpu.control.channels import ControlsState
from ismpu.control.failures import FailureMode
from ismpu.control.runway_tracker import RunwayTracker
from ismpu.envs.weather import WeatherManager, WeatherState
from ismpu.envs.scenario import Scenario, TouchdownSetup


@dataclass
class Telemetry:
    """Сырая структурированная телеметрия (единицы СИ). None — недоступно у бэкенда."""
    lat: float
    lon: float
    groundspeed_ms: float
    heading_true_deg: float
    pitch_deg: Optional[float] = None
    roll_deg: Optional[float] = None
    elevation_m: Optional[float] = None
    agl_m: Optional[float] = None
    vx_ms: Optional[float] = None
    vy_ms: Optional[float] = None
    vz_ms: Optional[float] = None
    p_rad: Optional[float] = None
    q_rad: Optional[float] = None
    r_rad: Optional[float] = None
    accel_long_g: Optional[float] = None
    accel_norm_g: Optional[float] = None
    accel_side_g: Optional[float] = None
    wind_speed_ms: Optional[float] = None
    wind_dir_from_deg: Optional[float] = None
    valid: bool = True   # False — телеметрия отсутствует (напр. таймаут стенда)


class SimInterface(ABC):
    """Абстракция симулятора: единственная зависимость контура/среды от транспорта."""

    @abstractmethod
    def reset(self, scenario: Scenario) -> Telemetry:
        """Готовит эпизод по сценарию (телепорт, погода, отказы) и возвращает телеметрию."""

    @abstractmethod
    def step(self, command: ControlsState) -> Telemetry:
        """Отправляет команды управления и возвращает свежую телеметрию (такт 20 Гц)."""

    @abstractmethod
    def read_telemetry(self) -> Telemetry:
        """Читает текущую телеметрию без отправки команд."""

    @abstractmethod
    def apply_weather(self, weather: WeatherState) -> None:
        """Устанавливает погодные условия."""

    @abstractmethod
    def inject_failure(self, mode: FailureMode) -> None:
        """Активирует отказ в симуляторе (где поддерживается)."""

    @abstractmethod
    def clear_failures(self) -> None:
        """Снимает все ранее инъецированные отказы."""

    @abstractmethod
    def teleport_touchdown(self, setup: TouchdownSetup) -> None:
        """Мгновенно ставит ЛА в точку касания по НУ сценария."""

    @abstractmethod
    def pause(self, flag: bool) -> None:
        """Пауза/снятие паузы симулятора."""

    def update(self, distance_m: float) -> None:
        """Потактовое обновление среды (напр. переменное сцепление). По умолчанию no-op."""

    def close(self) -> None:
        """Освобождает ресурсы. По умолчанию no-op."""

    @property
    def active_failures(self) -> set:
        return set()


# --------------------------------------------------------------------------- #
# X-Plane backend (обучение)
# --------------------------------------------------------------------------- #

# Телеметрия, на которую подписываемся (имена проверены по DataRefs.txt).
# TOTAL_FLIGHT_TIME/SIM_SPEED_ACTUAL — служебные индикаторы готовности после reload
# (в Telemetry не мапятся, читаются только детектором готовности).
_TELEMETRY_DREFS = [
    LATITUDE, LONGITUDE, GROUNDSPEED, TRUE_PSI, TRUE_THETA, TRUE_PHI, ELEVATION, Y_AGL,
    LOCAL_VX, LOCAL_VY, LOCAL_VZ, PRAD, QRAD, RRAD, G_AXIL, G_NRML, G_SIDE,
    WX_AC_WIND_SPEED_MSC, WX_AC_WIND_DIR_DEGT, TOTAL_FLIGHT_TIME, SIM_SPEED_ACTUAL,
]

# Детектор готовности после reload планера (см. XPlaneBackend._wait_until_ready).
_READY_POLL_S = 0.1        # период опроса flight_time
_READY_STABLE_TICKS = 3    # сколько подряд возрастаний flight_time считаем «физика пошла»
_VIEW_ZOOM_STEPS = 9       # sim/general/up_fast — отдалить камеру (как в runtime/setup.py)

# Индексы двигателей: 0 = левый, 1 = правый (двухдвигательный A330-класс).
_ENGINE_INDEX = {
    FailureMode.ENGINE_OUT_LEFT: 0,
    FailureMode.ENGINE_OUT_RIGHT: 1,
}
_REVERSER_INDEX = {
    FailureMode.REVERSE_LEFT_FAIL: 0,
    FailureMode.REVERSE_RIGHT_FAIL: 1,
}


class XPlaneBackend(SimInterface):
    """Бэкенд обучения: X-Plane 12 через `XPlaneConnectX`."""

    def __init__(self, xpc: Optional[XPlaneConnectX] = None, ip: str = "127.0.0.1", port: int = 49000,
                 settle_s: float = 0.2, reload_each_reset: bool = True,
                 ready_timeout: float = 25.0, setup_view: bool = False):
        self.xpc = xpc if xpc is not None else XPlaneConnectX(ip=ip, port=port)
        self.weather = WeatherManager(self.xpc)
        self._tracker = RunwayTracker()  # только для геодезии (смещение НУ)
        self._settle_s = settle_s
        # Перезагрузка планера между эпизодами: сбрасывает накопленный износ/тепло тормозов/
        # повреждения (иначе они переносятся из эпизода в эпизод — ломает воспроизводимость).
        # Требует реального X-Plane; для юнит-тестов на моке — reload_each_reset=False.
        self._reload_each_reset = reload_each_reset
        self._ready_timeout = ready_timeout   # таймаут ожидания готовности после reload
        self._setup_view = setup_view         # опц. настройка вида (chase/zoom) — для eval/GUI
        self._subscribed = False
        self._active_failures: set[FailureMode] = set()
        self._injected_drefs: set[str] = set()  # какие failure-DataRef'ы записаны (для сброса)

    # --- жизненный цикл эпизода ---

    def reset(self, scenario: Scenario) -> Telemetry:
        # Свежий планер каждый эпизод (сброс износа/повреждений), затем атомарный телепорт.
        if self._reload_each_reset:
            self._reload_airframe()
        else:
            self.xpc.fix_all_systems()
            self._ensure_subscribed()

        self.pause(True)                       # заморозить на время конфигурации/телепорта
        self.clear_failures()                  # reload уже обнулил отказы — сбрасываем и учёт
        self.teleport_touchdown(scenario.touchdown)
        self.apply_weather(scenario.weather)
        for failure in scenario.failures:
            self.inject_failure(failure)
        self.pause(False)
        if self._settle_s > 0:
            time.sleep(self._settle_s)
        if self._setup_view:
            self._apply_view()
        return self.read_telemetry()

    def step(self, command: ControlsState) -> Telemetry:
        command.send_commands(self.xpc)  # отправляет 5 DataRef'ов управления (X-Plane)
        return self.read_telemetry()

    # --- перезагрузка планера и детектор готовности ---

    def _reload_airframe(self) -> None:
        """Перезагружает планер (reload_aircraft_no_art) и ждёт готовности симулятора.

        Сбрасывает накопленный износ/повреждения/тепло тормозов. После reload поток RREF
        может прерваться → переподписываемся (retransmission дождётся первых значений уже
        от перезагруженного сима), снимаем паузу (чтобы физика шла) и ждём, пока
        `total_flight_time_sec` начнёт устойчиво расти — признак «перезагрузка завершена».
        """
        self.xpc.reload_aircraft()             # sim/operation/reload_aircraft_no_art (~12–14 с)
        self._subscribe()                      # переподписка: блокирует до первых значений
        self.pause(False)                      # физика должна идти, иначе flight_time не растёт
        self._wait_until_ready()

    def _wait_until_ready(self) -> None:
        """Ждёт, пока `total_flight_time_sec` возрастёт `_READY_STABLE_TICKS` раз подряд.

        Неблокирующий опрос подписанного значения (не `getDREF`, который во время загрузки
        может зависнуть навсегда). По истечении `ready_timeout` — предупреждение и продолжение
        (телепорт применяется в любом случае; лучше идти дальше, чем висеть)."""
        cur = self.xpc.current_dref_values
        deadline = time.monotonic() + self._ready_timeout
        prev, stable = None, 0
        while time.monotonic() < deadline:
            entry = cur.get(TOTAL_FLIGHT_TIME)
            t = entry["value"] if entry else None
            if t is not None and prev is not None and t > prev:
                stable += 1
                if stable >= _READY_STABLE_TICKS:
                    return
            else:
                stable = 0
            prev = t
            time.sleep(_READY_POLL_S)
        logger.warning("X-Plane readiness timeout (%.1f с): продолжаю без подтверждения "
                       "роста total_flight_time_sec", self._ready_timeout)

    def _apply_view(self) -> None:
        """Опциональная настройка вида (для eval/GUI/скриншотов) — как в runtime/setup.py."""
        self.xpc.sendCMND("sim/view/chase")
        for _ in range(_VIEW_ZOOM_STEPS):
            self.xpc.sendCMND("sim/general/up_fast")

    # --- телеметрия ---

    def _subscribe(self) -> None:
        """(Пере)подписка на телеметрию. Блокирует до первых значений (retransmission)."""
        self.xpc.subscribeDREFs([(d, FREQ) for d in _TELEMETRY_DREFS], timeout=self._ready_timeout)
        self._subscribed = True

    def _ensure_subscribed(self):
        if not self._subscribed:
            self._subscribe()

    def read_telemetry(self) -> Telemetry:
        cur = self.xpc.current_dref_values

        def v(dref):
            entry = cur.get(dref)
            return entry["value"] if entry else None

        lat, lon = v(LATITUDE), v(LONGITUDE)
        gs, heading = v(GROUNDSPEED), v(TRUE_PSI)
        valid = None not in (lat, lon, gs, heading)
        return Telemetry(
            lat=lat, lon=lon, groundspeed_ms=gs, heading_true_deg=heading,
            pitch_deg=v(TRUE_THETA), roll_deg=v(TRUE_PHI),
            elevation_m=v(ELEVATION), agl_m=v(Y_AGL),
            vx_ms=v(LOCAL_VX), vy_ms=v(LOCAL_VY), vz_ms=v(LOCAL_VZ),
            p_rad=v(PRAD), q_rad=v(QRAD), r_rad=v(RRAD),
            accel_long_g=v(G_AXIL), accel_norm_g=v(G_NRML), accel_side_g=v(G_SIDE),
            wind_speed_ms=v(WX_AC_WIND_SPEED_MSC), wind_dir_from_deg=v(WX_AC_WIND_DIR_DEGT),
            valid=valid,
        )

    # --- окружение ---

    def apply_weather(self, weather: WeatherState) -> None:
        self.weather.apply(weather)

    def update(self, distance_m: float) -> None:
        self.weather.update(distance_m)  # переменное сцепление по дистанции

    def inject_failure(self, mode: FailureMode) -> None:
        """Активирует отказ. Двигатель/реверс — реальным failure-DataRef'ом; NWS/деградация
        тяги/шасси у X-Plane отдельного датарефа не имеют → только помечаются активными
        (эффект даёт деградация команд в контуре, `FailureManager`)."""
        if mode is FailureMode.NONE:
            return
        self._active_failures.add(mode)
        dref = None
        if mode in _ENGINE_INDEX:
            dref = f"{FAIL_ENGINE}{_ENGINE_INDEX[mode]}"
        elif mode in _REVERSER_INDEX:
            dref = f"{FAIL_REVERSER}{_REVERSER_INDEX[mode]}"
        if dref is not None:
            self.xpc.sendDREF(dref, float(FAILURE_ENUM_INOP))
            self._injected_drefs.add(dref)

    def clear_failures(self) -> None:
        for dref in self._injected_drefs:
            self.xpc.sendDREF(dref, float(FAILURE_ENUM_OK))
        self._injected_drefs.clear()
        self._active_failures.clear()

    @property
    def active_failures(self) -> set:
        return set(self._active_failures)

    # --- позиционирование / пауза ---

    def teleport_touchdown(self, setup: TouchdownSetup) -> None:
        """Атомарный телепорт в точку касания со смещением от оси и по курсу.

        Только позиционирование: перезагрузку планера и ожидание готовности берёт на себя
        `reset` (`_reload_airframe`) — здесь предполагается, что сим уже перезагружен, готов
        и стоит на паузе (её ставит `reset` перед вызовом), чтобы позиция/скорости
        применились в одном кадре и не были затёрты процессом загрузки.
        """
        # Смещение стартовой точки перпендикулярно оси ВПП (± lateral_offset_m).
        lat, lon = RWY_START_LAT, RWY_START_LON
        if setup.lateral_offset_m:
            side = 90.0 if setup.lateral_offset_m > 0 else -90.0
            bearing = np.radians(RWY_HEADING_TRUE + side)
            lat, lon = self._tracker.destination(lat, lon, bearing, abs(setup.lateral_offset_m))

        heading = RWY_HEADING_TRUE + setup.heading_offset_deg
        self.xpc.sendPOSI(lat=lat, lon=lon, elev=ELEVATION_MSL + ELEVATION_AIRCRAFT,
                          phi=0.0, theta=setup.pitch_deg, psi_true=heading)

        # Конфигурация: малый газ, шасси выпущено, закрылки на макс, спидбрейки армированы.
        self.xpc.sendCTRL(lat_control=0.0, lon_control=0.0, rudder_control=0.0,
                          throttle=0.0, gear=1, flaps=1.0, speedbrakes=-0.5, park_brake=0.0)

        # Проекции скорости на локальные оси X-Plane (X — восток, Z — юг).
        v_ground = setup.speed_knots * Converts.KTS_TO_MS
        v_vert = -abs(setup.descent_rate_fpm) * Converts.FTM_TO_MS
        heading_rad = np.radians(heading)
        self.xpc.sendDREF(LOCAL_VX, v_ground * np.sin(heading_rad))
        self.xpc.sendDREF(LOCAL_VY, v_vert)
        self.xpc.sendDREF(LOCAL_VZ, -v_ground * np.cos(heading_rad))
        # Обнуляем угловые скорости, чтобы не было паразитного вращения.
        self.xpc.sendDREF(POS_P, 0.0)
        self.xpc.sendDREF(POS_Q, 0.0)
        self.xpc.sendDREF(POS_R, 0.0)

    def pause(self, flag: bool) -> None:
        self.xpc.pauseSIM(flag)


# --------------------------------------------------------------------------- #
# ICS bench backend (поставка)
# --------------------------------------------------------------------------- #

class ICSBackend(SimInterface):
    """Бэкенд поставки: стенд Заказчика через `ICSBenchConnector` (ПИВ, JSON/UDP).

    Погоду, отказы и позиционирование задаёт стенд — эти методы no-op. Диагностика
    (ветер, состояние ВПП, отказы) приходит в `ICSInputs`. Точная спецификация ПИВ
    (единицы, поля) согласуется с Заказчиком (implementation_plan §17 п.2) — маппинг
    ниже предварительный.
    """

    def __init__(self, connector: Optional[ICSBenchConnector] = None,
                 listen_ip: str = "127.0.0.1", listen_port: int = 3030, timeout: float = 1.0):
        self.connector = connector if connector is not None else ICSBenchConnector(listen_ip, listen_port)
        self.timeout = timeout
        self._last_inputs: Optional[ICSInputs] = None

    def reset(self, scenario: Scenario) -> Telemetry:
        # Среду на стенде конфигурирует Заказчик; ждём первую валидную телеметрию.
        return self.read_telemetry()

    def step(self, command: ControlsState) -> Telemetry:
        self.connector.send_outputs(self._to_outputs(command))
        return self.read_telemetry()

    def read_telemetry(self) -> Telemetry:
        inputs = self.connector.receive_inputs(timeout=self.timeout)
        if inputs is None:
            return Telemetry(lat=0.0, lon=0.0, groundspeed_ms=0.0, heading_true_deg=0.0, valid=False)
        self._last_inputs = inputs
        return self._to_telemetry(inputs)

    @staticmethod
    def _to_telemetry(inp: ICSInputs) -> Telemetry:
        return Telemetry(
            lat=inp.Latitude, lon=inp.Longitude, groundspeed_ms=inp.GroundSpeed,
            heading_true_deg=inp.TrueHeading, pitch_deg=inp.PitchAngle, roll_deg=inp.RollAngle,
            elevation_m=inp.BaroAltitude, agl_m=inp.RadioAltitude,
            p_rad=inp.BodyRollRate, q_rad=inp.BodyPitchRate, r_rad=inp.BodyYawRate,
            accel_long_g=inp.BodyLongAccel, accel_norm_g=inp.BodyNormAccel, accel_side_g=inp.BodyLatAccel,
            wind_speed_ms=inp.WindSpeed, wind_dir_from_deg=inp.WindDirectionTrue,
        )

    @staticmethod
    def _to_outputs(command: ControlsState) -> ICSOutputs:
        out = ICSOutputs()
        out.ControlMode = ControlModeState.Rollout
        out.BrakeLeftCmd = command.cmd_brake_l
        out.BrakeRightCmd = command.cmd_brake_r
        out.RudderCmd = command.rudder_cmd
        out.ThrottleLeft = command.cmd_rev_l   # реверс: отрицательная тяга [-1, 0]
        out.ThrottleRight = command.cmd_rev_r
        out.ReverseLeftCmd = ReverseEngineType.Deploy if command.cmd_rev_l < 0 else ReverseEngineType.Off
        out.ReverseRightCmd = ReverseEngineType.Deploy if command.cmd_rev_r < 0 else ReverseEngineType.Off
        return out

    # Средой на стенде управляет Заказчик — здесь no-op.
    def apply_weather(self, weather: WeatherState) -> None:
        pass

    def inject_failure(self, mode: FailureMode) -> None:
        pass

    def clear_failures(self) -> None:
        pass

    def teleport_touchdown(self, setup: TouchdownSetup) -> None:
        pass

    def pause(self, flag: bool) -> None:
        pass

    def close(self) -> None:
        self.connector.close()
