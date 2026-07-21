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

import math
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
from ismpu.io.ics_engagement import IcsEngagement, EngagementInputs
from ismpu.config.ics import (
    BRAKE_PEDAL_MAX_MM, THROTTLE_ANGLE_MIN_DEG, TILLER_MAX_DEG, RUDDER_MAX_DEG,
    ROLLOUT_CONTROL_MASK, runway_condition_from_bench,
)
from ismpu.io.datarefs import (
    LATITUDE, LONGITUDE, GROUNDSPEED, TRUE_PSI, TRUE_THETA, TRUE_PHI, ELEVATION, Y_AGL,
    LOCAL_VX, LOCAL_VY, LOCAL_VZ, PRAD, QRAD, RRAD, G_AXIL, G_NRML, G_SIDE,
    WX_AC_WIND_SPEED_MSC, WX_AC_WIND_DIR_DEGT,
    FAIL_ENGINE, FAIL_REVERSER, FAILURE_ENUM_OK, FAILURE_ENUM_INOP,
    POS_P, POS_Q, POS_R, TOTAL_FLIGHT_TIME, SIM_SPEED_ACTUAL,
    LEFT_BRAKE_RATIO, RIGHT_BRAKE_RATIO, THROTTLE_RATIO_L, THROTTLE_RATIO_R,
    YOKE_HEADING_RATIO,
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
    """Сырая структурированная телеметрия. **Единицы СИ** — граница пересчёта проходит здесь.

    Каждый бэкенд обязан привести свои единицы к СИ при заполнении: стенд отдаёт узлы, футы,
    футы/мин и градусы/с (см. `ICSInterface.cs`), X-Plane — в основном СИ. Ниже по коду единицы
    больше нигде не пересчитываются, поэтому пропущенный перевод здесь означает ошибку в разы.

    `None` — поле недоступно у бэкенда. Проверять надо `valid` **до** полей: бэкенд стенда при
    таймауте отдаёт нули, а не `None`.
    """
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

    # --- сигналы, которые даёт стенд (на X-Plane частью отсутствуют) ---
    ias_ms: Optional[float] = None
    """Приборная скорость. Отсечки реверса заданы по ней, а не по путевой."""
    runway_heading_deg: Optional[float] = None
    runway_length_m: Optional[float] = None
    runway_width_m: Optional[float] = None
    lateral_deviation_m: Optional[float] = None
    """Боковое отклонение от оси, измеренное стендом. Позволяет не считать геодезию самим."""
    weight_on_wheels: Optional[bool] = None
    """Обжатие ВСЕХ стоек. Условие включения управления на земле."""
    flight_phase: Optional[int] = None
    """Фаза полёта по `config.ics.FlightPhase` — по ней распознаётся уже идущий пробег."""
    faults: frozenset = frozenset()
    """Отказы, о которых сообщает борт. На стенде они приходят телеметрией, а не инжектируются
    нами, поэтому источник истины здесь, а не в `FailureManager`."""
    runway_condition: Optional[float] = None
    """Состояние ВПП в нашей шкале сцепления (`envs.weather.RunwayCondition`)."""

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
_VIEW_ZOOM_STEPS = 9       # sim/general/up_fast — отдалить камеру

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
        self._send_commands(command)
        return self.read_telemetry()

    def _send_commands(self, command: ControlsState) -> None:
        """Пять DataRef'ов управления. Живёт в бэкенде, а не в `ControlsState`: запись DataRef'ов
        специфична для X-Plane, и в контуре ей делать нечего — иначе контур не запускается на
        стенде заказчика."""
        self.xpc.sendDREF(LEFT_BRAKE_RATIO, command.cmd_brake_l)
        self.xpc.sendDREF(RIGHT_BRAKE_RATIO, command.cmd_brake_r)
        self.xpc.sendDREF(THROTTLE_RATIO_L, command.cmd_rev_l)
        self.xpc.sendDREF(THROTTLE_RATIO_R, command.cmd_rev_r)
        self.xpc.sendDREF(YOKE_HEADING_RATIO, command.rudder_cmd)

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
        """Опциональная настройка вида (для eval/GUI/скриншотов)."""
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

def _faults_from_inputs(inp: ICSInputs) -> frozenset:
    """Сигналы отказов со стенда → наши `FailureMode`.

    На стенде отказы **сообщает борт**, а не инжектируем мы. Поэтому здесь источник истины о том,
    что отказало, — а не `FailureManager`, который на X-Plane моделирует деградацию команд.

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


class ICSBackend(SimInterface):
    """Бэкенд поставки: стенд Заказчика через `ICSBenchConnector` (ПИВ, JSON/UDP).

    Погоду, отказы и позиционирование задаёт стенд — эти методы no-op. Диагностика (ветер,
    состояние ВПП, отказы) приходит в `ICSInputs`; единицы приводятся к СИ в `_to_telemetry`.

    Управление включается **только** после рукопожатия (`io/ics_engagement.py`): пока автомат
    не в состоянии `ENGAGED*`, команды органов не выдаются, а `ControlMode` остаётся `Off`.
    Свойство `engaged` показывает, принимает ли стенд наши команды к исполнению.
    """

    def __init__(self, connector: Optional[ICSBenchConnector] = None,
                 listen_ip: str = "127.0.0.1", listen_port: int = 3030, timeout: float = 1.0,
                 engagement: Optional[IcsEngagement] = None):
        self.connector = connector if connector is not None else ICSBenchConnector(listen_ip, listen_port)
        self.timeout = timeout
        self.engagement = engagement if engagement is not None else IcsEngagement()
        self._last_inputs: Optional[ICSInputs] = None
        self._last_telemetry: Optional[Telemetry] = None

    @property
    def engaged(self) -> bool:
        """Принимает ли стенд наши команды. До включения любой `step` уходит вхолостую."""
        return self.engagement.engaged

    def reset(self, scenario: Scenario) -> Telemetry:
        # Среду на стенде конфигурирует Заказчик; ждём первую валидную телеметрию.
        self.engagement.reset()
        return self.read_telemetry()

    def step(self, command: ControlsState) -> Telemetry:
        self.connector.send_outputs(self._to_outputs(command))
        return self.read_telemetry()

    def request_rollout(self) -> None:
        """Войти в пробег самостоятельно (`ControlMode 0 → 3`)."""
        self.engagement.request_rollout()

    def request_taxi(self) -> bool:
        """Передать управление в руление (`3 → 4`) — по решению вызывающего, что пробег окончен."""
        return self.engagement.request_taxi(self._engagement_inputs(self._last_telemetry))

    def read_telemetry(self) -> Telemetry:
        inputs = self.connector.receive_inputs(timeout=self.timeout)
        if inputs is None:
            telemetry = Telemetry(lat=0.0, lon=0.0, groundspeed_ms=0.0,
                                  heading_true_deg=0.0, valid=False)
        else:
            self._last_inputs = inputs
            telemetry = self._to_telemetry(inputs)

        self._last_telemetry = telemetry
        self.engagement.step(self._engagement_inputs(telemetry))
        return telemetry

    @staticmethod
    def _engagement_inputs(telemetry: Optional[Telemetry]) -> EngagementInputs:
        """Признаки для автомата включения. Путевая скорость — обратно в узлы: порог задан в них."""
        if telemetry is None:
            return EngagementInputs(all_gear_on_ground=False, groundspeed_kts=0.0,
                                    telemetry_valid=False)
        return EngagementInputs(
            all_gear_on_ground=bool(telemetry.weight_on_wheels),
            groundspeed_kts=(telemetry.groundspeed_ms or 0.0) * Converts.MS_TO_KTS,
            flight_phase=telemetry.flight_phase,
            telemetry_valid=telemetry.valid,
        )

    @property
    def active_failures(self) -> set:
        """На стенде отказы приходят телеметрией, а не инжектируются нами."""
        return set(self._last_telemetry.faults) if self._last_telemetry else set()

    @staticmethod
    def _to_telemetry(inp: ICSInputs) -> Telemetry:
        """`ICSInputs` → `Telemetry` с приведением единиц ICD к СИ.

        Стенд отдаёт узлы, футы, футы/мин и градусы/с. Пропущенный здесь перевод — не косметика:
        путевая скорость в узлах, положенная в поле м/с, даёт ошибку в 1.94 раза, и продольный
        канал прочитает 140 узлов как 272 и немедленно даст полное торможение.
        """
        return Telemetry(
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
            ias_ms=inp.IndicatedAirspeed * Converts.KTS_TO_MS,          # kt → м/с
            runway_heading_deg=inp.RunwayHeading if inp.RunwayHeadingValid else None,
            runway_length_m=inp.RunwayLength,
            runway_width_m=inp.RunwayWidth,
            lateral_deviation_m=inp.LateralDeviation,
            weight_on_wheels=bool(inp.NoseGearWeightOnWheels
                                  and inp.LeftGearWeightOnWheels
                                  and inp.RightGearWeightOnWheels),
            flight_phase=inp.FlightPhase if inp.FlightPhaseValid else None,
            faults=_faults_from_inputs(inp),
            runway_condition=float(runway_condition_from_bench(inp.RunwayCondition).value),
        )

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
