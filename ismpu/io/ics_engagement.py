"""Автомат включения управления на стенде заказчика.

Стенд принимает наши команды к исполнению **только** после корректного рукопожатия. Оно бывает
двух видов — воздушное и наземное, — и различаются они целевым режимом, а не сутью:

```
ВОЗДУШНОЕ (заход):   радиовысота > 400 футов
                     И  ModeAIReady = 1 непрерывно 2.2 секунды при ControlMode = Off
                     И  ControlMode переходит 0 → 1 (Approach)

НАЗЕМНОЕ (руление):  обжатие ВСЕХ стоек  И  путевая скорость < 2 узлов
                     И  ModeAIReady = 1 непрерывно 2 секунды
                     И  ControlMode переходит 0 → 4
ИЛИ                  обжатие ВСЕХ стоек  И  ControlMode переходит 3 → 4
```

Воздушная последовательность подтверждена на живом стенде вторым участником НИР
(`roman_aviacia_ics/README.md`, «Required airborne startup»), наземная — по ICD.

**Кто решает, что мы включены.** Решает стенд: он публикует `AgentIsActive`. Раньше этот класс
воспроизводил условия стенда у себя (считал обжатие/скорость/выдержку) и сам объявлял включение —
это догадка о чужом решении. Теперь подтверждение читается, а не вычисляется.

Но одного подтверждения мало, и это второй урок стенда: `AgentIsActive = 1` появляется уже
тогда, когда интерфейс ICS **включён оператором в IOS**, — то есть до всякого рукопожатия
(`roman_aviacia_ics/README.md`: «The simulator does not apply control commands just because UDP
telemetry reports AgentIsActive=1»; его запуск сначала *проверяет* `AgentIsActive = 1`, и только
потом гонит выдержку). Поэтому

    engaged = подтверждение стенда  И  наш стимул доведён до конца.

Второе слагаемое — не догадка о решении стенда, а учёт **своей** работы: пока выдержка не
выдержана и переход режима не отправлен, мы попросту ещё не спросили. Без него `warm_up`
возвращался бы мгновенно на любом стенде с включённым ICS, и управление ушло бы в пустоту.

Что автомат делает сам:

* **тайминг стимула** — держит `ModeAIReady = 1` c `ControlMode = Off` в течение выдержки, затем
  переводит `ControlMode` в целевой режим (`Approach` в воздухе, `Taxi` на земле). Радиовысота,
  обжатие и скорость нужны здесь лишь чтобы решить, *какой* стимул гнать и *когда начинать*, а не
  чтобы объявлять включение;
* **режимы** — вход в пробег (`ControlMode → Rollout`), подхват уже идущего пробега по фазе полёта
  (`FlightPhase = LandRun`, т.к. `ControlMode` во входной структуре нет), передача заход → пробег
  после касания и пробег → руление (`3 → 4`).

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
    ENGAGE_AIR_READY_DWELL_S, ENGAGE_MIN_RADIO_ALTITUDE_FT, TERMINAL_RADIO_ALTITUDE_FT,
    ROLLOUT_FLIGHT_PHASES,
)
from ismpu.io.ics_connector import ControlModeState


class EngagementState(Enum):
    """Состояние **исходящего стимула** (что мы шлём стенду), а не факта включения.

    Факт включения — отдельно, в `IcsEngagement.engaged` (стимул доведён + `AgentIsActive`).
    """
    IDLE = "idle"                    # стимула нет: ControlMode = Off, ModeAIReady = 0
    READY_DWELL = "ready_dwell"      # заявка готовности: Off + ModeAIReady = 1, идёт выдержка
    COMMAND_APPROACH = "command_approach"  # шлём ControlMode = Approach (заход и выравнивание)
    COMMAND_ROLLOUT = "command_rollout"  # шлём ControlMode = Rollout (вход/подхват пробега)
    COMMAND_TAXI = "command_taxi"    # шлём ControlMode = Taxi (переход 0→4 или 3→4)


COMMANDING_STATES = (EngagementState.COMMAND_APPROACH, EngagementState.COMMAND_ROLLOUT,
                     EngagementState.COMMAND_TAXI)
"""Состояния, в которых стимул доведён до конца: режим выставлен и держится."""


@dataclass(frozen=True)
class EngagementInputs:
    """Признаки со стенда, от которых зависит рукопожатие.

    `agent_is_active` — публикуемый стендом признак, что интерфейс ICS активен. Необходимое
    условие включения, но не достаточное (см. модуль).

    `groundspeed_kts` — именно **узлы**: телеметрия приходит в узлах, а порог включения задан в
    узлах. Пересчёт в м/с здесь был бы источником ошибки в 1.94 раза. По той же причине
    `radio_altitude_ft` — в футах.
    """
    all_gear_on_ground: bool
    groundspeed_kts: float
    flight_phase: int | None = None
    agent_is_active: int = 0
    telemetry_valid: bool = True
    radio_altitude_ft: float | None = None


class IcsEngagement:
    """Автомат включения. `step(inputs)` вызывается каждый такт до формирования команды."""

    def __init__(self, *, dwell_s: float = ENGAGE_READY_DWELL_S,
                 air_dwell_s: float = ENGAGE_AIR_READY_DWELL_S,
                 min_ready_frames: int = ENGAGE_MIN_READY_FRAMES,
                 max_groundspeed_kts: float = ENGAGE_MAX_GROUNDSPEED_KTS,
                 min_radio_altitude_ft: float = ENGAGE_MIN_RADIO_ALTITUDE_FT,
                 clock=time.monotonic):
        self.dwell_s = dwell_s
        self.air_dwell_s = air_dwell_s
        self.min_ready_frames = min_ready_frames
        self.max_groundspeed_kts = max_groundspeed_kts
        self.min_radio_altitude_ft = min_radio_altitude_ft
        self._clock = clock
        self.reset()

    def reset(self) -> None:
        """Полный сброс — новый эпизод начинается с невключённого состояния."""
        self.state = EngagementState.IDLE
        self._confirmed = False            # признак стенда (AgentIsActive)
        self._dwell_started: float | None = None
        self._ready_frames = 0
        self._adopted = False
        self._arm_target: ControlModeState | None = None   # режим, под который идёт выдержка

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
        включению с нуля.
        """
        self.state = EngagementState.COMMAND_ROLLOUT
        self._adopted = True
        self._dwell_started = None

    def request_rollout(self) -> None:
        """Войти в пробег самостоятельно: шлём `ControlMode = Rollout`.

        Это же — передача управления с воздушного участка на пробег после касания
        (`ControlMode 1 → 3`). Переход `1 → 3` в ICD **не описан** и является предположением:
        документированы только `0 → 4` и `3 → 4`. ТРЕБУЕТ ПОДТВЕРЖДЕНИЯ у разработчика стенда —
        если стенд его не принимает, здесь появится промежуточный `Landing (2)`.
        """
        self.state = EngagementState.COMMAND_ROLLOUT
        self._adopted = False
        self._dwell_started = None

    def request_approach(self) -> None:
        """Войти в заход самостоятельно: шлём `ControlMode = Approach`.

        Обычно вызывать не нужно — воздушное включение автомат ведёт сам по радиовысоте. Метод
        нужен для подхвата уже идущего захода и для отладки конкретного участка.
        """
        self.state = EngagementState.COMMAND_APPROACH
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
        """Продвинуть автомат: снять признак стенда и обновить исходящий стимул.

        `AgentIsActive` обновляется только по валидной телеметрии — единичный потерянный пакет
        (таймаут приёма) не должен «выключать» нас на один такт. Стимул: переход захода в пробег
        после касания, подхват уже идущего пробега по фазе полёта и включение с нуля (воздушное
        или наземное — по радиовысоте). Переход `3 → 4` инициирует вызывающий (`request_taxi`).
        """
        if inputs.telemetry_valid:
            # Стенд — авторитет по своему признаку. По обрыву связи держим прежнее значение.
            if not (self._confirmed and not inputs.agent_is_active
                    and self._in_terminal_window(inputs)):
                self._confirmed = bool(inputs.agent_is_active)
        else:
            self._reset_dwell()
            if self.state is EngagementState.READY_DWELL:
                self.state = EngagementState.IDLE
            return

        # Пробег: либо мы довели заход до касания, либо режим включил кто-то другой. Фаза
        # выравнивания (LAND_FLARE_AND_TOUCHDOWN) сюда не входит намеренно: смена режима до
        # касания сбрасывает автопилот стенда.
        if (inputs.flight_phase is not None
                and int(inputs.flight_phase) in ROLLOUT_FLIGHT_PHASES):
            if self.state is EngagementState.IDLE:
                self.adopt_rollout()       # пробег шёл без нас — это подхват
                return
            if self.state is EngagementState.COMMAND_APPROACH:
                self.request_rollout()     # заход довели мы — это передача, а не подхват
                return

        if self._commanding_mode:
            return   # режим уже выставлен; дальнейшие переходы — только по явному запросу

        # IDLE / READY_DWELL — включение с нуля: держим готовность, затем 0 → целевой режим.
        target = self._arm_target_for(inputs)
        if target is not None:
            now = self._clock()
            if self._dwell_started is None or target is not self._arm_target:
                # Смена цели посреди выдержки (например ВС коснулось полосы) отсчёт не
                # продолжает: стенд ждёт непрерывной готовности под конкретный переход.
                self._dwell_started = now
                self._ready_frames = 0
                self._arm_target = target
                self.state = EngagementState.READY_DWELL
            elif self._dwell_satisfied(now):
                self.state = (EngagementState.COMMAND_APPROACH
                              if target is ControlModeState.Approach
                              else EngagementState.COMMAND_TAXI)
        else:
            # Срыв предусловий — отсчёт начинается заново, а не продолжается.
            self._reset_dwell()
            self.state = EngagementState.IDLE

    def _dwell_satisfied(self, now: float) -> bool:
        """Оба условия сразу: прошло время И столько же кадров реально ушло.

        Время защищает от слишком частой отправки (30 кадров можно выпалить за 0.1 с), счётчик
        кадров — от «двух опросов с разрывом», при котором время есть, а передачи не было.
        """
        elapsed_ok = (now - self._dwell_started) >= self._required_dwell_s
        frames_ok = self._ready_frames >= self.min_ready_frames
        return elapsed_ok and frames_ok

    @property
    def _required_dwell_s(self) -> float:
        """Выдержка под текущую цель: воздушная длиннее наземной (2.2 с против 2.0)."""
        return (self.air_dwell_s if self._arm_target is ControlModeState.Approach
                else self.dwell_s)

    def _reset_dwell(self) -> None:
        self._dwell_started = None
        self._ready_frames = 0
        self._arm_target = None

    def _arm_target_for(self, inputs: EngagementInputs) -> ControlModeState | None:
        """Под какой режим гнать стимул. `None` — предусловий нет ни для одного.

        Воздушный вариант проверяется первым: у ВС в воздухе обжатия стоек нет, и наземные
        предусловия для него всё равно не выполнятся. Радиовысота обязана быть **объявлена** —
        отсутствующая (`None`) высота не «ноль», а «стенд не сообщил», и включаться по ней
        нельзя.
        """
        if (not inputs.all_gear_on_ground
                and inputs.radio_altitude_ft is not None
                and inputs.radio_altitude_ft > self.min_radio_altitude_ft):
            return ControlModeState.Approach
        if inputs.all_gear_on_ground and inputs.groundspeed_kts < self.max_groundspeed_kts:
            return ControlModeState.Taxi
        return None

    def _in_terminal_window(self, inputs: EngagementInputs) -> bool:
        """Последние футы перед касанием, где снятие `AgentIsActive` не повод бросать заход.

        До земли остаются секунды: отпустить органы здесь опаснее, чем доработать по последним
        данным. Окно узкое и одностороннее — оно только **удерживает** уже полученное
        подтверждение, но никогда не создаёт его само (на стенде это же поведение подтверждено
        коллегой: ниже 80 футов потеря активности логируется, а заход продолжается до касания).
        """
        if self.state is not EngagementState.COMMAND_APPROACH:
            return False
        ra = inputs.radio_altitude_ft
        return ra is not None and ra <= TERMINAL_RADIO_ALTITUDE_FT

    @property
    def _commanding_mode(self) -> bool:
        """Уже гоним какой-то режим (Approach/Rollout/Taxi), а не заявку готовности."""
        return self.state in COMMANDING_STATES

    # --- что отдавать в команде ----------------------------------------- #

    @property
    def confirmed(self) -> bool:
        """Признак стенда `AgentIsActive`: интерфейс ICS активен. Необходимое условие."""
        return self._confirmed

    @property
    def stimulus_complete(self) -> bool:
        """Довели ли мы рукопожатие до конца: выдержка выдержана, режим выставлен и держится."""
        return self._commanding_mode

    @property
    def engaged(self) -> bool:
        """Исполняет ли стенд наши команды: его признак **и** наш доведённый стимул.

        Одного `AgentIsActive` мало — он появляется, как только оператор включил ICS в IOS, ещё
        до всякого рукопожатия. Одного нашего стимула тоже мало — это была бы догадка о решении
        стенда. Нужны оба, и каждое слагаемое отвечает за свою сторону обмена.
        """
        return self._confirmed and self.stimulus_complete

    @property
    def adopted(self) -> bool:
        """Был ли режим подхвачен извне, а не установлен нами."""
        return self._adopted

    @property
    def control_mode(self) -> ControlModeState:
        """Значение `ControlMode` для исходящей команды (стимул).

        Во время выдержки — строго `Off`: стенд включается по **фронту** `Off → режим`, и если
        начать сразу с целевого значения, фронта не будет никогда.
        """
        if self.state is EngagementState.COMMAND_APPROACH:
            return ControlModeState.Approach
        if self.state is EngagementState.COMMAND_ROLLOUT:
            return ControlModeState.Rollout
        if self.state is EngagementState.COMMAND_TAXI:
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
        """Почему включение ещё не произошло — для диагностики при таймауте прогрева.

        Порядок проверок важен: состояние стимула спрашивается **до** предусловий включения с
        нуля. Иначе на подхваченном пробеге причиной объявлялась бы «путевая скорость 100 узлов ≥
        2» — верное само по себе, но к делу не относящееся: предусловия наземного включения к
        уже идущему пробегу неприменимы, и ждём мы там совсем другого.
        """
        if self.engaged:
            return "включено (стимул доведён, AgentIsActive=1)"
        if not inputs.telemetry_valid:
            return "нет валидной телеметрии со стенда"
        if self._commanding_mode:
            # Всё, что зависело от нас, отправлено; ждём решения стенда.
            return (f"стимул доведён (ControlMode={self.control_mode.name}), но стенд ещё не "
                    f"подтвердил активность (AgentIsActive=0)")
        if self.state is EngagementState.READY_DWELL:
            if self._ready_frames < self.min_ready_frames:
                return (f"отправлено {self._ready_frames} кадров с ModeAIReady=1 из "
                        f"{self.min_ready_frames} требуемых")
            return (f"выдержка {self.dwell_elapsed_s():.2f} с из "
                    f"{self._required_dwell_s:.2f} требуемых")
        if not inputs.all_gear_on_ground:
            ra = inputs.radio_altitude_ft
            if ra is None:
                return ("обжаты не все стойки, а радиовысота стендом не объявлена — "
                        "включаться не по чему: ни наземное условие, ни воздушное не проверить")
            return (f"обжаты не все стойки, радиовысота {ra:.0f} футов ≤ "
                    f"{self.min_radio_altitude_ft:.0f} — не выполнено ни наземное условие "
                    f"включения, ни воздушное")
        return (f"путевая скорость {inputs.groundspeed_kts:.1f} узла ≥ "
                f"{self.max_groundspeed_kts:.1f}")

    def as_dict(self) -> dict:
        """Слепок для логов и отчётов приёмки."""
        return {
            "state": self.state.value,
            "engaged": self.engaged,
            "confirmed": self._confirmed,
            "stimulus_complete": self.stimulus_complete,
            "adopted": self.adopted,
            "control_mode": int(self.control_mode),
            "arm_target": None if self._arm_target is None else int(self._arm_target),
            "mode_ai_ready": self.mode_ai_ready,
            "dwell_elapsed_s": self.dwell_elapsed_s(),
            "ready_frames_sent": self._ready_frames,
        }
