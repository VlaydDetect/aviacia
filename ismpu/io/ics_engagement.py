"""Автомат включения управления на стенде заказчика.

Стенд принимает наши команды к исполнению **только** после корректного рукопожатия. Условия
наземного включения (проверяет их сам стенд, у себя):

```
обжатие ВСЕХ стоек  И  путевая скорость < 2 узлов
                    И  ModeAIReady = 1 непрерывно 2 секунды
                    И  ControlMode переходит 0 → 4
ИЛИ
обжатие ВСЕХ стоек  И  ControlMode переходит 3 → 4
```

**Кто решает, что мы включены.** Решает стенд, а не мы. Он подтверждает приём управления полем
`AgentIsActive = 1` во входной телеметрии. Раньше этот класс воспроизводил условия стенда у себя
(считал обжатие/скорость/выдержку) и сам объявлял включение — это догадка о чужом решении: можно
было «включиться» на своей стороне, пока стенд всё отбрасывает. Теперь `engaged` читает
`AgentIsActive`, а автомат отвечает лишь за **исходящий стимул**: что слать (`ModeAIReady`,
`ControlMode`), чтобы стенд это включение выполнил.

Две вещи, которые автомат по-прежнему делает сам:

* **тайминг стимула** — держит `ModeAIReady = 1` c `ControlMode = Off` в течение выдержки, затем
  переводит `ControlMode` в `Taxi` (переход `0 → 4`). Обжатие/скорость нужны здесь лишь чтобы
  решить, *когда начинать* гнать стимул, а не чтобы объявлять включение;
* **режимы** — самостоятельный вход в пробег (`ControlMode → Rollout`), подхват уже идущего
  пробега по фазе полёта (`FlightPhase = LandRun`, т.к. `ControlMode` во входной структуре нет) и
  передача пробег → руление (`Rollout → Taxi`, `3 → 4`).

Класс намеренно не знает про сокеты и не трогает время сам: часы инжектируются, вход — простая
структура признаков (включая `agent_is_active`, снятый со стенда). Так автомат тестируется без
стенда и без ожидания реального времени.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from enum import Enum

from ismpu.config.ics import (
    ENGAGE_MAX_GROUNDSPEED_KTS, ENGAGE_READY_DWELL_S, ENGAGE_MIN_READY_FRAMES,
    ROLLOUT_FLIGHT_PHASES,
)
from ismpu.io.ics_connector import ControlModeState


class EngagementState(Enum):
    """Состояние **исходящего стимула** (что мы шлём стенду), а не факта включения.

    Факт включения — отдельно, в `IcsEngagement.engaged` (по `AgentIsActive` со стенда).
    """
    IDLE = "idle"                    # стимула нет: ControlMode = Off, ModeAIReady = 0
    READY_DWELL = "ready_dwell"      # заявка готовности: Off + ModeAIReady = 1, идёт выдержка
    COMMAND_ROLLOUT = "command_rollout"  # шлём ControlMode = Rollout (вход/подхват пробега)
    COMMAND_TAXI = "command_taxi"    # шлём ControlMode = Taxi (переход 0→4 или 3→4)


@dataclass(frozen=True)
class EngagementInputs:
    """Признаки со стенда, от которых зависит рукопожатие.

    `agent_is_active` — подтверждение стенда, что он **принял** наше управление. Единственный
    авторитет по факту включения.

    `groundspeed_kts` — именно **узлы**: телеметрия приходит в узлах, а порог включения задан в
    узлах. Пересчёт в м/с здесь был бы источником ошибки в 1.94 раза.
    """
    all_gear_on_ground: bool
    groundspeed_kts: float
    flight_phase: int | None = None
    agent_is_active: int = 0
    telemetry_valid: bool = True


class IcsEngagement:
    """Автомат включения. `step(inputs)` вызывается каждый такт до формирования команды."""

    def __init__(self, *, dwell_s: float = ENGAGE_READY_DWELL_S,
                 min_ready_frames: int = ENGAGE_MIN_READY_FRAMES,
                 max_groundspeed_kts: float = ENGAGE_MAX_GROUNDSPEED_KTS,
                 clock=time.monotonic):
        self.dwell_s = dwell_s
        self.min_ready_frames = min_ready_frames
        self.max_groundspeed_kts = max_groundspeed_kts
        self._clock = clock
        self.reset()

    def reset(self) -> None:
        """Полный сброс — новый эпизод начинается с невключённого состояния."""
        self.state = EngagementState.IDLE
        self._confirmed = False            # подтверждение стенда (AgentIsActive)
        self._dwell_started: float | None = None
        self._ready_frames = 0
        self._adopted = False

    # --- обратная связь от транспорта ----------------------------------- #

    def on_frame_sent(self, mode_ai_ready: int) -> None:
        """Сообщить автомату, что кадр **фактически ушёл** на стенд.

        Вызывается транспортом после успешной отправки. Без этого выдержка была бы чистым
        временем между опросами и могла бы «набраться» вообще без передачи — стенд не получил бы
        двух секунд готовности.

        Кадр без `ModeAIReady = 1` рвёт серию: требование ICD — непрерывность.
        """
        if mode_ai_ready and self.state is EngagementState.READY_DWELL:
            self._ready_frames += 1
        else:
            self._ready_frames = 0

    # --- запросы вызывающего ------------------------------------------- #

    def adopt_rollout(self) -> None:
        """Подхватить уже включённый извне пробег: шлём `ControlMode = Rollout`.

        Используется, когда режим установил другой модуль (заход/посадка), а мы принимаем
        управление на пробеге. Выдержка `ModeAIReady` не требуется — она относится только к
        наземному включению с нуля.
        """
        self.state = EngagementState.COMMAND_ROLLOUT
        self._adopted = True
        self._dwell_started = None

    def request_rollout(self) -> None:
        """Войти в пробег самостоятельно: шлём `ControlMode = Rollout`.

        Условия воздушного включения в ICD не описаны (вопрос разработчику стенда), поэтому
        решение принимает вызывающий, а автомат лишь фиксирует стимул.
        """
        self.state = EngagementState.COMMAND_ROLLOUT
        self._adopted = False
        self._dwell_started = None

    def request_taxi(self, inputs: EngagementInputs) -> bool:
        """Передать управление в руление (`ControlMode 3 → 4`). → удался ли переход.

        Обжатие всех стоек — **разрешающее условие**, а не триггер: на пробеге оно истинно всегда,
        и если переходить по нему, руление наступило бы сразу после касания, пропустив пробег
        целиком. Триггер — решение вызывающего, что пробег окончен (достигнута скорость руления).
        """
        if self.state is EngagementState.COMMAND_TAXI:
            return True                                  # уже в руле́нии — идемпотентно
        if self.state is not EngagementState.COMMAND_ROLLOUT:
            return False
        if not inputs.all_gear_on_ground:
            return False
        self.state = EngagementState.COMMAND_TAXI
        return True

    # --- такт ----------------------------------------------------------- #

    def step(self, inputs: EngagementInputs) -> None:
        """Продвинуть автомат: снять подтверждение стенда и обновить исходящий стимул.

        Подтверждение (`AgentIsActive`) обновляется только по валидной телеметрии — единичный
        потерянный пакет (таймаут приёма) не должен «выключать» нас на один такт. Стимул: подхват
        пробега по фазе полёта и наземное включение с нуля; переходы `0 → 3` и `3 → 4` инициирует
        вызывающий (`request_*`).
        """
        if inputs.telemetry_valid:
            # Стенд — авторитет. По обрыву связи держим прежнее подтверждение, а не сбрасываем.
            self._confirmed = bool(inputs.agent_is_active)
        else:
            self._reset_dwell()
            if self.state is EngagementState.READY_DWELL:
                self.state = EngagementState.IDLE
            return

        # Подхват: стенд сообщает фазу пробега, а мы ещё не гоним режим.
        if (self.state is EngagementState.IDLE
                and inputs.flight_phase is not None
                and int(inputs.flight_phase) in ROLLOUT_FLIGHT_PHASES):
            self.adopt_rollout()
            return

        if self._commanding_mode:
            return   # режим уже выставлен; дальнейшие переходы — только по явному запросу

        # IDLE / READY_DWELL — наземное включение с нуля: держим готовность, затем 0 → 4.
        if self._preconditions_hold(inputs):
            now = self._clock()
            if self._dwell_started is None:
                self._dwell_started = now
                self._ready_frames = 0
                self.state = EngagementState.READY_DWELL
            elif self._dwell_satisfied(now):
                self.state = EngagementState.COMMAND_TAXI
        else:
            # Срыв предусловий — отсчёт начинается заново, а не продолжается.
            self._reset_dwell()
            self.state = EngagementState.IDLE

    def _dwell_satisfied(self, now: float) -> bool:
        """Оба условия сразу: прошло время И столько же кадров реально ушло.

        Время защищает от слишком частой отправки (30 кадров можно выпалить за 0.1 с), счётчик
        кадров — от «двух опросов с разрывом», при котором время есть, а передачи не было.
        """
        elapsed_ok = (now - self._dwell_started) >= self.dwell_s
        frames_ok = self._ready_frames >= self.min_ready_frames
        return elapsed_ok and frames_ok

    def _reset_dwell(self) -> None:
        self._dwell_started = None
        self._ready_frames = 0

    def _preconditions_hold(self, inputs: EngagementInputs) -> bool:
        return bool(inputs.all_gear_on_ground
                    and inputs.groundspeed_kts < self.max_groundspeed_kts)

    @property
    def _commanding_mode(self) -> bool:
        """Уже гоним какой-то режим (Rollout/Taxi), а не заявку готовности."""
        return self.state in (EngagementState.COMMAND_ROLLOUT, EngagementState.COMMAND_TAXI)

    # --- что отдавать в команде ----------------------------------------- #

    @property
    def engaged(self) -> bool:
        """Принял ли стенд наши команды к исполнению — по его подтверждению `AgentIsActive`."""
        return self._confirmed

    @property
    def adopted(self) -> bool:
        """Был ли режим подхвачен извне, а не установлен нами."""
        return self._adopted

    @property
    def control_mode(self) -> ControlModeState:
        """Значение `ControlMode` для исходящей команды (стимул)."""
        if self.state is EngagementState.COMMAND_ROLLOUT:
            return ControlModeState.Rollout
        if self.state is EngagementState.COMMAND_TAXI:
            return ControlModeState.Taxi
        # Стенд подтвердил включение раньше, чем стимул дошёл до режима (напр. мгновенный подхват):
        # держим Taxi, чтобы ControlMode не противоречил выданной маске.
        if self._confirmed:
            return ControlModeState.Taxi
        return ControlModeState.Off

    @property
    def mode_ai_ready(self) -> int:
        """`ModeAIReady`: держится, пока идёт заявка/режим, и после подтверждения стенда."""
        return 1 if (self.state is not EngagementState.IDLE or self._confirmed) else 0

    def dwell_elapsed_s(self) -> float:
        """Сколько уже держится выдержка. 0.0, если отсчёт не идёт (для диагностики)."""
        if self._dwell_started is None:
            return 0.0
        return self._clock() - self._dwell_started

    @property
    def ready_frames_sent(self) -> int:
        """Сколько кадров с `ModeAIReady = 1` реально ушло подряд."""
        return self._ready_frames

    def blocking_reason(self, inputs: EngagementInputs) -> str:
        """Почему включение ещё не произошло — для диагностики при таймауте прогрева."""
        if self.engaged:
            return "включено (AgentIsActive=1)"
        if not inputs.telemetry_valid:
            return "нет валидной телеметрии со стенда"
        if not inputs.all_gear_on_ground:
            return "обжаты не все стойки"
        if inputs.groundspeed_kts >= self.max_groundspeed_kts:
            return (f"путевая скорость {inputs.groundspeed_kts:.1f} узла ≥ "
                    f"{self.max_groundspeed_kts:.1f}")
        if self._commanding_mode:
            # Всё, что зависело от нас, отправлено; ждём решения стенда.
            return "стенд ещё не подтвердил включение (AgentIsActive=0)"
        if self._ready_frames < self.min_ready_frames:
            return (f"отправлено {self._ready_frames} кадров с ModeAIReady=1 из "
                    f"{self.min_ready_frames} требуемых")
        return f"выдержка {self.dwell_elapsed_s():.2f} с из {self.dwell_s:.2f} требуемых"

    def as_dict(self) -> dict:
        """Слепок для логов и отчётов приёмки."""
        return {
            "state": self.state.value,
            "engaged": self.engaged,
            "confirmed": self._confirmed,
            "adopted": self.adopted,
            "control_mode": int(self.control_mode),
            "mode_ai_ready": self.mode_ai_ready,
            "dwell_elapsed_s": self.dwell_elapsed_s(),
            "ready_frames_sent": self._ready_frames,
        }
