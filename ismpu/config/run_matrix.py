"""Матрица прогонов для настройки базовых ПИД-регуляторов.

Машиночитаемая форма `docs/Матрица_прогонов_ПИД_ИСМПУ.xlsx` (версия 3): 22 варианта отказа/режима
(«шифра») × справочник условий = 280 прогонов. Лист А — заход и посадка (156), лист Б — ВПП и
руление (124).

**Один шифр = один набор коэффициентов.** Так устроена сама матрица: внутри шифра прогоны идут от
простого к сложному, и коэффициенты предыдущего служат начальным приближением следующего. Поэтому
пресет заводится на шифр, а не на строку — 280 пресетов не только неподъёмны, но и противоречили
бы замыслу.

**Условия задаёт оператор стенда, а не мы.** Средой распоряжается Заказчик, поэтому здесь описано,
*что попросить выставить* и *как это будет выглядеть в телеметрии*, чтобы под эти условия
подобрался нужный пресет. Ни ветра, ни сцепления, ни отказа мы не устанавливаем.

## Чего телеметрия не различает

Матрица различает тоньше, чем ICD. `FaultNWS` — один байт, и заедание стойки в нейтрали (Б.2.1),
заедание с уводом (Б.2.2) и ограничение диапазона (Б.2.3) приходят одинаково. То же с реверсом:
Б.3.1 и Б.3.2 неотличимы по `FaultLeftEngineReverse`. Практическое следствие: такие пресеты
**нельзя выбрать автоматически** по телеметрии — только по имени, руками, зная какой прогон
выставлен на стенде. Поле `bench_faults` says, что именно придёт, и это же объясняет, почему у
нескольких шифров оно совпадает.

Ступени ветра, коэффициенты сцепления, высоты и моменты ввода отказов — рабочие значения
Исполнителя: в ТЗ их нет, и они подлежат согласованию с Заказчиком (ТЗ 5.1.5.1).
"""

from dataclasses import dataclass, field

from ismpu.control.failures import FailureMode
from ismpu.envs.weather import WeatherState, RunwayCondition
from ismpu.utils.converts import Converts


def _kts(ms: float) -> float:
    """Матрица задаёт ветер в м/с, телеметрия приходит в узлах."""
    return ms * Converts.MS_TO_KTS


@dataclass(frozen=True)
class MatrixCondition:
    """Условие прогона из справочника матрицы (П.1–П.5 для захода, У.1–У.8 для ВПП).

    `weather` — то, как условие должно выглядеть в телеметрии стенда; по нему и подбирается
    пресет. `note` описывает то, что в `WeatherState` не выражается: порывистость и сдвиг ветра —
    это процессы, а `WeatherState` — мгновенное показание, а не рычаг.
    """
    code: str
    title: str
    weather: WeatherState
    note: str = ""


# Видимость: матрица задаёт RVR 300 м, телеметрия — футы (см. `WeatherState.from_ics`).
_RVR_300_M = 300.0
_CAT_I_M = 5000.0

# Сцепление: матрица даёт μ, у нас — монотонная шкала скользкости `RunwayCondition` (это разные
# величины, а не разные единицы одной). Сопоставление: μ≈0.8 — сухо, μ≈0.4 — мокро,
# μ≈0.2 и слой воды — лужи/лёд.
_DRY = RunwayCondition.DRY.value
_WET = RunwayCondition.WET.value
_PUDDLY = RunwayCondition.PUDDLY.value
_ICY = RunwayCondition.ICY.value


APPROACH_CONDITIONS: tuple[MatrixCondition, ...] = (
    MatrixCondition("П.1", "Штиль, стандартная атмосфера",
                    WeatherState(visibility_m=_CAT_I_M)),
    MatrixCondition("П.2-L5", "Боковой ветер 5 м/с слева",
                    WeatherState.from_crosswind(-_kts(5.0), 0.0)),
    MatrixCondition("П.2-R5", "Боковой ветер 5 м/с справа",
                    WeatherState.from_crosswind(_kts(5.0), 0.0)),
    MatrixCondition("П.2-L10", "Боковой ветер 10 м/с слева",
                    WeatherState.from_crosswind(-_kts(10.0), 0.0)),
    MatrixCondition("П.2-R10", "Боковой ветер 10 м/с справа",
                    WeatherState.from_crosswind(_kts(10.0), 0.0)),
    MatrixCondition("П.2-L15", "Боковой ветер 15 м/с слева",
                    WeatherState.from_crosswind(-_kts(15.0), 0.0)),
    MatrixCondition("П.2-R15", "Боковой ветер 15 м/с справа",
                    WeatherState.from_crosswind(_kts(15.0), 0.0)),
    MatrixCondition("П.3-GL", "Порывистый ветер слева: фон 7 м/с, порывы до 12 м/с",
                    WeatherState.from_crosswind(-_kts(7.0), 0.0),
                    note="порывы до 12 м/с с периодом 3–5 с — процесс, в WeatherState не выражается"),
    MatrixCondition("П.3-GR", "Порывистый ветер справа: фон 7 м/с, порывы до 12 м/с",
                    WeatherState.from_crosswind(_kts(7.0), 0.0),
                    note="порывы до 12 м/с с периодом 3–5 с"),
    MatrixCondition("П.3-WS", "Сдвиг ветра: встречный 10 → 0 м/с от H = 150 м до земли",
                    WeatherState.from_crosswind(0.0, _kts(10.0)),
                    note="убывание встречной составляющей с высоты 150 м — процесс"),
    MatrixCondition("П.4-H", "Встречный ветер 10 м/с",
                    WeatherState.from_crosswind(0.0, _kts(10.0))),
    MatrixCondition("П.4-T", "Попутный ветер 5 м/с",
                    WeatherState.from_crosswind(0.0, -_kts(5.0))),
    MatrixCondition("П.5", "Низкая видимость RVR 300 м (Cat II), заход по ILS",
                    WeatherState(visibility_m=_RVR_300_M)),
)

GROUND_CONDITIONS: tuple[MatrixCondition, ...] = (
    MatrixCondition("У.1", "Сухая ВПП (μ ≈ 0,8), штиль",
                    WeatherState(runway_friction=_DRY, visibility_m=_CAT_I_M)),
    MatrixCondition("У.2-L5", "Сухая ВПП, боковой ветер 5 м/с слева",
                    WeatherState.from_crosswind(-_kts(5.0), 0.0, runway_friction=_DRY)),
    MatrixCondition("У.2-R5", "Сухая ВПП, боковой ветер 5 м/с справа",
                    WeatherState.from_crosswind(_kts(5.0), 0.0, runway_friction=_DRY)),
    MatrixCondition("У.2-L10", "Сухая ВПП, боковой ветер 10 м/с слева",
                    WeatherState.from_crosswind(-_kts(10.0), 0.0, runway_friction=_DRY)),
    MatrixCondition("У.2-R10", "Сухая ВПП, боковой ветер 10 м/с справа",
                    WeatherState.from_crosswind(_kts(10.0), 0.0, runway_friction=_DRY)),
    MatrixCondition("У.2-L15", "Сухая ВПП, боковой ветер 15 м/с слева",
                    WeatherState.from_crosswind(-_kts(15.0), 0.0, runway_friction=_DRY)),
    MatrixCondition("У.2-R15", "Сухая ВПП, боковой ветер 15 м/с справа",
                    WeatherState.from_crosswind(_kts(15.0), 0.0, runway_friction=_DRY)),
    MatrixCondition("У.3-GL", "Сухая ВПП, порывистый ветер слева (фон 7, порывы 12 м/с)",
                    WeatherState.from_crosswind(-_kts(7.0), 0.0, runway_friction=_DRY),
                    note="порывы до 12 м/с — процесс"),
    MatrixCondition("У.3-GR", "Сухая ВПП, порывистый ветер справа (фон 7, порывы 12 м/с)",
                    WeatherState.from_crosswind(_kts(7.0), 0.0, runway_friction=_DRY),
                    note="порывы до 12 м/с — процесс"),
    MatrixCondition("У.4", "Мокрая ВПП (μ ≈ 0,4), штиль",
                    WeatherState(runway_friction=_WET, rain_pct=0.5, visibility_m=_CAT_I_M)),
    MatrixCondition("У.5-L", "Мокрая ВПП + боковой ветер 10 м/с слева",
                    WeatherState.from_crosswind(-_kts(10.0), 0.0, runway_friction=_WET)),
    MatrixCondition("У.5-R", "Мокрая ВПП + боковой ветер 10 м/с справа",
                    WeatherState.from_crosswind(_kts(10.0), 0.0, runway_friction=_WET)),
    MatrixCondition("У.6", "Переменное сцепление по третям: μ 0,8 / 0,4 / 0,2",
                    WeatherState(runway_friction=_WET, visibility_m=_CAT_I_M),
                    note="сцепление меняется по длине ВПП; телеметрия отдаёт одно значение — "
                         "пресет калибруется на худшую треть"),
    MatrixCondition("У.7", "Слой воды 5 мм по всей длине — риск аквапланирования",
                    WeatherState(runway_friction=_PUDDLY, rain_pct=1.0, visibility_m=_CAT_I_M),
                    note="для руления не применяется"),
    MatrixCondition("У.8", "Низкая видимость RVR 300 м, сухая ВПП, штиль",
                    WeatherState(runway_friction=_DRY, visibility_m=_RVR_300_M)),
)


@dataclass(frozen=True)
class MatrixCase:
    """Один шифр матрицы — вариант отказа/режима, под который настраивается набор коэффициентов."""
    code: str                       # «А.1.1», «Б.3.2»
    preset: str                     # имя пресета в SCENARIOS / APPROACH_PRESETS
    segment: str                    # approach | rollout | taxi | through
    title: str
    failure: str                    # как отказ описан в матрице
    injection: str                  # момент ввода
    criteria: str                   # критерии успеха из матрицы
    conditions: tuple[MatrixCondition, ...]
    bench_faults: tuple[FailureMode, ...] = ()
    """Как отказ придёт в телеметрии (`Telemetry.faults`). Пусто — штатный режим.

    Совпадение у разных шифров не ошибка, а факт: ICD беднее матрицы (см. модуль)."""
    ambiguous_with: tuple[str, ...] = ()
    """Шифры, неотличимые от этого по телеметрии. Выбирать такой пресет — только по имени."""

    @property
    def runs(self) -> int:
        return len(self.conditions)


APPROACH_CASES: tuple[MatrixCase, ...] = (
    MatrixCase(
        "А.1.1", "a_1_1_track", "approach",
        "Штатно: захват и удержание курса и глиссады до H = 30 м",
        "без отказов", "—",
        "Курс ≤ 0,7°; глиссада ≤ 0,5°; на H=30 м ось ВС = ось ВПП ± 5 м",
        APPROACH_CONDITIONS),
    MatrixCase(
        "А.1.2", "a_1_2_flare", "approach",
        "Штатно: выравнивание (flare), decrab, касание",
        "без отказов", "—",
        "Касание в первой трети ВПП (≤ 900 м от торца); Vy касания в согласованных пределах",
        APPROACH_CONDITIONS),
    MatrixCase(
        "А.2.1", "a_2_1_gear_left_up", "approach",
        "Шасси: не выпущена / не на замке левая основная стойка",
        "левая основная стойка убрана; аэродинамика и балансировка изменены",
        "конфигурация с начала глиссады (H = 300 м)",
        "Глиссада ≤ ± 0,7°; посадочные критерии п. 5.1.1.2",
        APPROACH_CONDITIONS, (FailureMode.GEAR_CONFIG,),
        ambiguous_with=("А.2.2", "А.2.3")),
    MatrixCase(
        "А.2.2", "a_2_2_gear_nose_up", "approach",
        "Шасси: не выпущена носовая стойка",
        "носовая стойка убрана; изменение продольной балансировки",
        "конфигурация с начала глиссады (H = 300 м)",
        "Глиссада ≤ ± 0,7°; посадочные критерии п. 5.1.1.2",
        APPROACH_CONDITIONS, (FailureMode.GEAR_CONFIG,),
        ambiguous_with=("А.2.1", "А.2.3")),
    MatrixCase(
        "А.2.3", "a_2_3_gear_partial", "approach",
        "Шасси: несимметричный/неполный выпуск",
        "левая основная стойка в промежуточном положении (~50 %), створки открыты",
        "конфигурация с начала глиссады (H = 300 м)",
        "Глиссада ≤ ± 0,7°; посадочные критерии п. 5.1.1.2",
        APPROACH_CONDITIONS, (FailureMode.GEAR_CONFIG,),
        ambiguous_with=("А.2.1", "А.2.2")),
    MatrixCase(
        "А.3.1", "a_3_1_stab_nose_down_high", "approach",
        "Стабилизатор: заклинение на пикирование, начало глиссады",
        "заклинение −2° от балансировочного положения", "H = 300 м (вход в глиссаду)",
        "Удержание ± 1° глиссады; продольная управляемость",
        APPROACH_CONDITIONS,
        ambiguous_with=("А.3.2", "А.3.3", "А.3.4")),
    MatrixCase(
        "А.3.2", "a_3_2_stab_nose_up_high", "approach",
        "Стабилизатор: заклинение на кабрирование, начало глиссады",
        "заклинение +2° от балансировочного положения", "H = 300 м (вход в глиссаду)",
        "Удержание ± 1° глиссады; продольная управляемость",
        APPROACH_CONDITIONS,
        ambiguous_with=("А.3.1", "А.3.3", "А.3.4")),
    MatrixCase(
        "А.3.3", "a_3_3_stab_nose_down_low", "approach",
        "Стабилизатор: заклинение на пикирование перед выравниванием",
        "заклинение −2° от балансировочного положения", "H = 60 м (перед выравниванием)",
        "Удержание ± 1° глиссады; продольная управляемость",
        APPROACH_CONDITIONS,
        ambiguous_with=("А.3.1", "А.3.2", "А.3.4")),
    MatrixCase(
        "А.3.4", "a_3_4_stab_nose_up_low", "approach",
        "Стабилизатор: заклинение на кабрирование перед выравниванием",
        "заклинение +2° от балансировочного положения", "H = 60 м (перед выравниванием)",
        "Удержание ± 1° глиссады; продольная управляемость",
        APPROACH_CONDITIONS,
        ambiguous_with=("А.3.1", "А.3.2", "А.3.3")),
    MatrixCase(
        "А.4.1", "a_4_1_engine_out_high", "approach",
        "Двигатель: полный отказ левого двигателя на глиссаде",
        "тяга левого двигателя → 0 за 1 с", "H = 300 м (вход в глиссаду)",
        "Компенсация асимметрии тяги; курс ± 5° от оси ВПП",
        APPROACH_CONDITIONS, (FailureMode.ENGINE_OUT_LEFT,),
        ambiguous_with=("А.4.3",)),
    MatrixCase(
        "А.4.2", "a_4_2_engine_partial", "approach",
        "Двигатель: частичная потеря тяги левого двигателя",
        "тяга левого двигателя снижается до 50 % за 2 с", "H = 300 м (вход в глиссаду)",
        "Компенсация асимметрии тяги; курс ± 5° от оси ВПП",
        APPROACH_CONDITIONS, (FailureMode.THRUST_LEFT_DEGRADED,)),
    MatrixCase(
        "А.4.3", "a_4_3_engine_out_low", "approach",
        "Двигатель: полный отказ левого двигателя на малой высоте",
        "тяга левого двигателя → 0 за 1 с", "H = 60 м (перед выравниванием)",
        "Компенсация асимметрии тяги; курс ± 5° от оси ВПП",
        APPROACH_CONDITIONS, (FailureMode.ENGINE_OUT_LEFT,),
        ambiguous_with=("А.4.1",)),
)

_THROUGH_CONDITIONS = (GROUND_CONDITIONS[0], GROUND_CONDITIONS[3], GROUND_CONDITIONS[10])

GROUND_CASES: tuple[MatrixCase, ...] = (
    MatrixCase(
        "Б.1.1", "b_1_1_rollout", "rollout",
        "Штатно: пробег от касания до полной остановки по оси ВПП",
        "без отказов", "касание на V ≈ 140 уз",
        "Ось ВПП ≤ ± 3 м на пробеге; корректная диагностика (сцепление, ветер, аквапланирование)",
        GROUND_CONDITIONS),
    MatrixCase(
        "Б.1.2", "b_1_2_taxi", "taxi",
        "Штатно: руление по прямому участку",
        "без отказов", "руление V ≈ 15 уз",
        "Осевая линия ≤ ± 1 м при рулении по прямому участку",
        tuple(c for c in GROUND_CONDITIONS if c.code != "У.7")),
    MatrixCase(
        "Б.2.1", "b_2_1_nws_stuck_neutral", "rollout",
        "Носовая стойка: заедание в нейтральном положении",
        "стойка фиксирована на 0°; управление стойкой недоступно", "ввод при касании (V ≈ 140 уз)",
        "Перераспределение на дифф. торможение + асимм. тягу; ось ≤ ± 5 м до полной остановки",
        GROUND_CONDITIONS, (FailureMode.NWS_FAIL,),
        ambiguous_with=("Б.2.2", "Б.2.3")),
    MatrixCase(
        "Б.2.2", "b_2_2_nws_stuck_offset", "rollout",
        "Носовая стойка: заедание с ненулевым углом",
        "стойка фиксирована на +5° (увод вправо)", "ввод при касании (V ≈ 140 уз)",
        "Перераспределение на дифф. торможение + асимм. тягу; ось ≤ ± 5 м до полной остановки",
        GROUND_CONDITIONS, (FailureMode.NWS_FAIL,),
        ambiguous_with=("Б.2.1", "Б.2.3")),
    MatrixCase(
        "Б.2.3", "b_2_3_nws_limited", "rollout",
        "Носовая стойка: ограничение диапазона поворота",
        "диапазон ограничен до ± 3°; смешанное управление стойка + тормоза + тяга",
        "ввод при касании (V ≈ 140 уз)",
        "Перераспределение на дифф. торможение + асимм. тягу; ось ≤ ± 5 м до полной остановки",
        GROUND_CONDITIONS, (FailureMode.NWS_FAIL,),
        ambiguous_with=("Б.2.1", "Б.2.2")),
    MatrixCase(
        "Б.3.1", "b_3_1_reverse_left_fail", "rollout",
        "Реверс: отказ реверса левого двигателя",
        "реверс левого не включается; правый работает штатно", "команда на реверс при V ≈ 120 уз",
        "Компенсация рысканья; курс ± 5° от направления ВПП до V < 30 уз; скоростной профиль",
        GROUND_CONDITIONS, (FailureMode.REVERSE_LEFT_FAIL,),
        ambiguous_with=("Б.3.2",)),
    MatrixCase(
        "Б.3.2", "b_3_2_reverse_asymmetric", "rollout",
        "Реверс: несимметричное включение",
        "левый выходит на реверс с задержкой 3 с относительно правого",
        "команда на реверс при V ≈ 120 уз",
        "Компенсация рысканья; курс ± 5° от направления ВПП до V < 30 уз; скоростной профиль",
        GROUND_CONDITIONS, (FailureMode.REVERSE_LEFT_FAIL,),
        ambiguous_with=("Б.3.1",)),
    MatrixCase(
        "Б.3.3", "b_3_3_residual_thrust", "rollout",
        "Тяга: несимметричная остаточная прямая тяга",
        "левый двигатель не выходит на малый газ, остаётся ~30 % тяги",
        "с момента касания (V ≈ 140 уз)",
        "Компенсация рысканья; курс ± 5° от направления ВПП до V < 30 уз; скоростной профиль",
        GROUND_CONDITIONS, (FailureMode.THRUST_LEFT_DEGRADED,)),
    MatrixCase(
        "Б.4.1", "b_4_1_through", "through",
        "Сквозной: глиссада → касание → пробег до остановки, без отказов",
        "без отказов", "—",
        "Все критерии А.1.1, А.1.2, Б.1.1; без скачка управляющих воздействий на стыке модулей",
        _THROUGH_CONDITIONS),
    MatrixCase(
        "Б.4.2", "b_4_2_through_engine_out", "through",
        "Сквозной с отказом: отказ левого двигателя на глиссаде + отказ реверса левого на пробеге",
        "тяга левого → 0 на глиссаде; реверс левого не включается",
        "H = 300 м; реверс при V ≈ 120 уз",
        "Критерии А.4.1 и Б.3.1",
        (GROUND_CONDITIONS[0], GROUND_CONDITIONS[10]),
        (FailureMode.ENGINE_OUT_LEFT, FailureMode.REVERSE_LEFT_FAIL)),
)

RUN_MATRIX: tuple[MatrixCase, ...] = APPROACH_CASES + GROUND_CASES

CASE_BY_CODE = {case.code: case for case in RUN_MATRIX}
CASE_BY_PRESET = {case.preset: case for case in RUN_MATRIX}

TOTAL_RUNS = sum(case.runs for case in RUN_MATRIX)
"""Полный объём матрицы. Сверяется с итогом в таблице Заказчика (280 прогонов)."""


def cases_for_segment(segment: str) -> tuple[MatrixCase, ...]:
    """Шифры одного участка: `approach` / `rollout` / `taxi` / `through`."""
    return tuple(c for c in RUN_MATRIX if c.segment == segment)


def ground_cases() -> tuple[MatrixCase, ...]:
    """Шифры, у которых настраиваются коэффициенты **пробега** (пригодны для SFT).

    Сквозные прогоны сюда входят: у них есть наземный участок, и его коэффициенты — те же пять
    регуляторов. Заход (`approach`) не входит: там своя, статическая настройка
    (`config/approach.py`), которую сеть не планирует.
    """
    return tuple(c for c in RUN_MATRIX if c.segment in ("rollout", "taxi", "through"))
