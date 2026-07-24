"""Участки полёта и переходы между ними.

Управление ведётся на всём интервале — от захода по ILS до скорости руления, — но законы на
участках разные: в воздухе работает `control/approach.py`, на земле — продольный и латеральный
каналы `control/channels.py`. Здесь описано, **какой участок сейчас** и когда он сменяется.

Два свойства этой машины важнее её простоты:

* **Она движется только вперёд.** `APPROACH → ROLLOUT → TAXI`, назад — никогда. «Козление» после
  касания на секунду снимает обжатие стоек, и машина без защёлки вернула бы управление воздушному
  закону — с нулевым РУД, разогнанными тормозами и попыткой выйти на глиссаду с полосы.
* **По умолчанию участок — пробег.** В воздух машина уходит только если стенд **явно** сообщил,
  что ВС в воздухе. Кадр без пакета стенда (синтетическая телеметрия в тестах и офлайн-разборах)
  не «в воздухе», а «нечем судить», и трактовать одно как другое нельзя: весь наземный контур и
  среда обучения работают именно на таких кадрах.
"""

from enum import Enum

from ismpu.config.ics import (
    ENGAGE_MIN_RADIO_ALTITUDE_FT, TERMINAL_RADIO_ALTITUDE_FT, FlightPhase,
)
from ismpu.config.requirements import (
    GO_AROUND_DECISION_HEIGHT_FT, GO_AROUND_LATERAL_GATE_BAND_FT,
)


class ApproachRefused(RuntimeError):
    """Воздушный участок начинать нельзя — с названной причиной.

    Отдельное исключение, а не «молча поедем по земле»: ВС в воздухе, и тихий откат на наземный
    закон был бы хуже отказа. Оператор стенда должен увидеть причину и поправить условия.
    """


class FlightSegment(Enum):
    """Участок полёта, за который отвечает контур."""
    APPROACH = "approach"   # заход по ILS и выравнивание — воздушный канал
    ROLLOUT = "rollout"     # пробег после касания — тормоза, реверс, удержание оси
    TAXI = "taxi"           # скорость руления достигнута, управление передано


def is_airborne(telemetry, *, min_radio_altitude_ft: float = ENGAGE_MIN_RADIO_ALTITUDE_FT) -> bool:
    """Сообщает ли стенд, что ВС в воздухе и достаточно высоко для приёма захода.

    Требуется **вся** совокупность: пакет стенда есть, ни одна основная стойка не обжата, и
    радиовысота объявлена валидной и выше порога. Отсутствующая радиовысота — не ноль и не
    «высоко»: это «стенд не сообщил», и включаться по ней нельзя.
    """
    if telemetry is None or not getattr(telemetry, "valid", False):
        return False
    if getattr(telemetry, "ics_inputs", None) is None:
        return False
    if telemetry.main_gear_contact:
        return False
    ra = telemetry.radio_altitude_ft
    return ra is not None and ra > min_radio_altitude_ft


def segment_is_decidable(telemetry) -> bool:
    """Можно ли вообще судить об участке по этому кадру.

    Кадр без пакета стенда (таймаут приёма на старте, синтетическая телеметрия) участок не
    определяет. Решение по нему было бы не «пробег», а «мы не знаем и назвали это пробегом» —
    а машина участков движется только вперёд, так что ошибка стала бы необратимой на весь заход.
    """
    return (telemetry is not None
            and getattr(telemetry, "valid", False)
            and getattr(telemetry, "ics_inputs", None) is not None)


def initial_segment(telemetry, **kwargs) -> FlightSegment:
    """С какого участка начинать. Пробег — ответ по умолчанию (см. модуль)."""
    return FlightSegment.APPROACH if is_airborne(telemetry, **kwargs) else FlightSegment.ROLLOUT


def approach_blocker(telemetry) -> "str | None":
    """Почему нельзя вести заход по этому кадру. `None` — можно.

    Пока проверка одна, но принципиальная: **посадочная конфигурация механизации**. Весь
    воздушный закон построен на таблицах МС-21 для FLAPS 3 / FULL — VAPP, VSR1, порог защиты по
    углу атаки, — а `detect_landing_flaps` при непосадочном положении молча подставляет
    настроенный запасной вариант. Без этой проверки заход с неубранной механизацией шёл бы к
    VAPP посадочной конфигурации на чистом крыле, причём весь мониторинг огибающей молчал бы:
    он сравнивает с порогами той же неприменимой таблицы.

    Эталон отвергает такой запуск, не отправив ни одного кадра
    (`roman_aviacia_ics/tools/run_ics_pid.py`, код возврата 8). Отличие: он требует **совпадения**
    с заказанной конфигурацией, мы же запрещаем только «не посадочная вовсе» — иначе штатная
    посадка в FULL отвергалась бы при настройке FLAPS 3.
    """
    if telemetry is None or getattr(telemetry, "ics_inputs", None) is None:
        return "нет пакета стенда"
    if telemetry.landing_flaps is None:
        angle = telemetry.ics_inputs.FlapsAngle
        return (f"механизация не в посадочной конфигурации (закрылки {angle:.1f}°): таблицы "
                f"захода МС-21 к ней неприменимы")
    return None


def in_terminal_window(telemetry, *, limit_ft: float = TERMINAL_RADIO_ALTITUDE_FT) -> bool:
    """Последние футы перед касанием, где прерывать заход опаснее, чем доработать.

    Внутри окна не действуют прерывания по потере валидности ILS и активности стенда: до земли
    остаются секунды, и отпустить органы здесь — худший из вариантов.
    """
    if telemetry is None or getattr(telemetry, "ics_inputs", None) is None:
        return False
    if telemetry.main_gear_contact:
        return True
    ra = telemetry.radio_altitude_ft
    return ra is not None and ra <= limit_ft


def above_decision_height(telemetry, *, limit_ft: float = GO_AROUND_DECISION_HEIGHT_FT) -> bool:
    """ВС выше высоты решения ухода на второй круг (30 м по ТЗ 5.1.1.2). → уход разрешён.

    Требует **положительно известной** радиовысоты выше порога: без неё уход не инициируется —
    выставлять взлётный режим и набирать вслепую хуже, чем довести заход. Обжатая основная стойка
    — уже не воздух: на земле ухода нет даже при козлении.
    """
    if telemetry is None or getattr(telemetry, "ics_inputs", None) is None:
        return False
    if telemetry.main_gear_contact:
        return False
    ra = telemetry.radio_altitude_ft
    return ra is not None and ra > limit_ft


def at_lateral_alignment_gate(telemetry, *, limit_ft: float = GO_AROUND_DECISION_HEIGHT_FT,
                              band_ft: float = GO_AROUND_LATERAL_GATE_BAND_FT) -> bool:
    """Полоса подхода к гейту совмещения с осью ± 5 м: `(30 м, 30 м + band]`.

    Только в ней проверяется боковое отклонение ± 5 м (ТЗ 5.1.1.2, «на высоте 30 м ось совмещена»):
    это последний рубеж перед высотой решения, а выше него боковое положение ограничивает курсовой
    допуск, а не эта планка.
    """
    if telemetry is None or getattr(telemetry, "ics_inputs", None) is None:
        return False
    ra = telemetry.radio_altitude_ft
    return ra is not None and limit_ft < ra <= limit_ft + band_ft


def ils_blocker(telemetry) -> "str | None":
    """Почему нельзя продолжать заход по этому кадру. `None` — можно.

    Закон читает `LocDeviation`/`GSDeviation` без оглядки на флаги валидности — так же, как
    эталон, и это правильно: прерывание живёт не в законе, а в цикле над ним
    (`run_ics_pid.py`, код возврата 7). При снятой валидности отклонение равно нулю, что
    неотличимо от «точно на оси», и контур доведёт ВС до земли по несуществующей глиссаде.
    """
    if in_terminal_window(telemetry):
        return None
    if telemetry is None or getattr(telemetry, "ics_inputs", None) is None:
        return None
    if telemetry.ils_valid is False:
        return "стенд снял валидность курсового или глиссадного канала"
    return None


def touched_down(telemetry) -> bool:
    """Окончен ли воздушный участок.

    Два независимых признака, любой достаточен: обжатие **любой основной** стойки (так же
    определяет касание контур коллеги на стенде) и объявленная стендом фаза пробега. Носовая
    стойка не участвует — она обжимается позже основных.
    """
    if telemetry is None or not getattr(telemetry, "valid", False):
        return False
    if getattr(telemetry, "ics_inputs", None) is None:
        return False
    if telemetry.main_gear_contact:
        return True
    phase = telemetry.flight_phase
    return phase is not None and int(phase) == int(FlightPhase.LAND_RUN)
