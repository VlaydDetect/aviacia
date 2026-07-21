"""Автомат включения управления на стенде заказчика.

Стенд принимает наши команды к исполнению **только** после корректного рукопожатия. Условия
наземного включения:

```
обжатие ВСЕХ стоек  И  путевая скорость < 2 узлов
                    И  ModeAIReady = 1 непрерывно 2 секунды
                    И  ControlMode переходит 0 → 4
ИЛИ
обжатие ВСЕХ стоек  И  ControlMode переходит 3 → 4
```

Ключевой момент: `ControlMode` — **состояние**, а не константа. Пока мы шлём одно и то же
значение каждый такт, перехода не происходит и управление не включается никогда, сколько бы
корректных команд ни отправлялось.

Автомат поддерживает обе роли:

* **самостоятельный вход** — с нуля в пробег (`0 → 3`) или сразу в руление (`0 → 4`);
* **подхват** уже идущего пробега, если режим включён извне.

`ControlMode` отсутствует в `ICSInputs`, поэтому прочитать текущий режим со стенда невозможно;
подхват опирается на фазу полёта (`FlightPhase = LandRun`) — см. `config/ics.ROLLOUT_FLIGHT_PHASES`.

Класс намеренно не знает про сокеты и не трогает время сам: часы инжектируются, вход — простая
структура признаков. Так автомат тестируется без стенда и без ожидания реального времени.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from enum import Enum

from ismpu.config.ics import (
    ENGAGE_MAX_GROUNDSPEED_KTS, ENGAGE_READY_DWELL_S, ROLLOUT_FLIGHT_PHASES,
)
from ismpu.io.ics_connector import ControlModeState


class EngagementState(Enum):
    """Состояние рукопожатия."""
    IDLE = "idle"                       # управление не включено, предусловия не набраны
    READY_DWELL = "ready_dwell"         # предусловия держатся, идёт выдержка ModeAIReady
    ENGAGED_ROLLOUT = "engaged_rollout"  # ControlMode = 3, ведём пробег
    ENGAGED_TAXI = "engaged_taxi"       # ControlMode = 4, ведём руление


@dataclass(frozen=True)
class EngagementInputs:
    """Признаки со стенда, от которых зависит рукопожатие.

    `groundspeed_kts` — именно **узлы**: телеметрия приходит в узлах, а порог включения задан в
    узлах. Пересчёт в м/с здесь был бы источником ошибки в 1.94 раза.
    """
    all_gear_on_ground: bool
    groundspeed_kts: float
    flight_phase: int | None = None
    telemetry_valid: bool = True


class IcsEngagement:
    """Автомат включения. `step(inputs)` вызывается каждый такт до формирования команды."""

    def __init__(self, *, dwell_s: float = ENGAGE_READY_DWELL_S,
                 max_groundspeed_kts: float = ENGAGE_MAX_GROUNDSPEED_KTS,
                 clock=time.monotonic):
        self.dwell_s = dwell_s
        self.max_groundspeed_kts = max_groundspeed_kts
        self._clock = clock
        self.reset()

    def reset(self) -> None:
        """Полный сброс — новый эпизод начинается с невключённого состояния."""
        self.state = EngagementState.IDLE
        self._dwell_started: float | None = None
        self._adopted = False

    # --- запросы вызывающего ------------------------------------------- #

    def adopt_rollout(self) -> None:
        """Подхватить уже включённый извне пробег: считаем, что `ControlMode` уже равен 3.

        Используется, когда режим установил другой модуль (заход/посадка), а мы принимаем
        управление на пробеге. Выдержка `ModeAIReady` не требуется — она относится только к
        наземному включению с нуля.
        """
        self.state = EngagementState.ENGAGED_ROLLOUT
        self._adopted = True
        self._dwell_started = None

    def request_rollout(self) -> None:
        """Войти в пробег самостоятельно (`ControlMode 0 → 3`).

        Условия воздушного включения в ICD не описаны (вопрос разработчику стенда), поэтому
        решение принимает вызывающий, а автомат лишь фиксирует состояние.
        """
        self.state = EngagementState.ENGAGED_ROLLOUT
        self._adopted = False
        self._dwell_started = None

    def request_taxi(self, inputs: EngagementInputs) -> bool:
        """Передать управление в руление (`ControlMode 3 → 4`). → удался ли переход.

        Обжатие всех стоек — **разрешающее условие**, а не триггер: на пробеге оно истинно всегда,
        и если переходить по нему, руление наступило бы сразу после касания, пропустив пробег
        целиком. Триггер — решение вызывающего, что пробег окончен (достигнута скорость руления).
        """
        if self.state is not EngagementState.ENGAGED_ROLLOUT:
            return False
        if not inputs.all_gear_on_ground:
            return False
        self.state = EngagementState.ENGAGED_TAXI
        return True

    # --- такт ----------------------------------------------------------- #

    def step(self, inputs: EngagementInputs) -> None:
        """Продвинуть автомат по текущим признакам.

        Обрабатывает только автоматические переходы: подхват пробега по фазе полёта и наземное
        включение с нуля. Переходы `0 → 3` и `3 → 4` инициирует вызывающий — см. `request_*`.
        """
        if not inputs.telemetry_valid:
            # Без телеметрии предусловия проверить нечем: выдержку копить нельзя.
            self._dwell_started = None
            if self.state is EngagementState.READY_DWELL:
                self.state = EngagementState.IDLE
            return

        # Подхват: стенд сообщает фазу пробега, а мы ещё не включены.
        if (self.state is EngagementState.IDLE
                and inputs.flight_phase is not None
                and int(inputs.flight_phase) in ROLLOUT_FLIGHT_PHASES):
            self.adopt_rollout()
            return

        if self.engaged:
            return   # дальнейшие переходы — только по явному запросу

        # IDLE / READY_DWELL — наземное включение с нуля (0 → 4).
        if self._preconditions_hold(inputs):
            now = self._clock()
            if self._dwell_started is None:
                self._dwell_started = now
                self.state = EngagementState.READY_DWELL
            elif now - self._dwell_started >= self.dwell_s:
                self.state = EngagementState.ENGAGED_TAXI
        else:
            # Срыв предусловий — отсчёт начинается заново, а не продолжается.
            self._dwell_started = None
            self.state = EngagementState.IDLE

    def _preconditions_hold(self, inputs: EngagementInputs) -> bool:
        return bool(inputs.all_gear_on_ground
                    and inputs.groundspeed_kts < self.max_groundspeed_kts)

    # --- что отдавать в команде ----------------------------------------- #

    @property
    def engaged(self) -> bool:
        """Принимает ли стенд наши команды к исполнению."""
        return self.state in (EngagementState.ENGAGED_ROLLOUT, EngagementState.ENGAGED_TAXI)

    @property
    def adopted(self) -> bool:
        """Был ли режим подхвачен извне, а не установлен нами."""
        return self._adopted

    @property
    def control_mode(self) -> ControlModeState:
        """Значение `ControlMode` для исходящей команды."""
        if self.state is EngagementState.ENGAGED_ROLLOUT:
            return ControlModeState.Rollout
        if self.state is EngagementState.ENGAGED_TAXI:
            return ControlModeState.Taxi
        return ControlModeState.Off

    @property
    def mode_ai_ready(self) -> int:
        """`ModeAIReady`: держится, пока предусловия выполняются, и после включения."""
        return 1 if (self.state is EngagementState.READY_DWELL or self.engaged) else 0

    def dwell_elapsed_s(self) -> float:
        """Сколько уже держится выдержка. 0.0, если отсчёт не идёт (для диагностики)."""
        if self._dwell_started is None:
            return 0.0
        return self._clock() - self._dwell_started

    def as_dict(self) -> dict:
        """Слепок для логов и отчётов приёмки."""
        return {
            "state": self.state.value,
            "engaged": self.engaged,
            "adopted": self.adopted,
            "control_mode": int(self.control_mode),
            "mode_ai_ready": self.mode_ai_ready,
            "dwell_elapsed_s": self.dwell_elapsed_s(),
        }
