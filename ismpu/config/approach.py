"""Настройки воздушного участка: заход по ILS, выравнивание, управление скоростью.

Коэффициенты и пороги перенесены из `roman_aviacia_ics/config/ics_clear_weather_pid.json` —
это **настроенный на живом стенде** набор второго участника НИР, а не наши догадки. Менять их
имеет смысл только по результатам прогона на стенде.

## Почему коэффициенты записаны как аргументы нашего `PIDController`

Регулятор коллеги (`tools/ics_pid_controller.py::PID`) — это фильтрованный PID с производной **по
измерению** и **условным** anti-windup. Ровно эта численность у нашего `PIDController` уже есть, в
виде трёх флагов (`derivative_on_measurement`, `conditional_anti_windup`, `exact_discretization`),
поэтому второй класс регулятора в проекте не заводится: воздушные PID — это тот же
`PIDController`, просто с другими флагами. Соответствие полей:

| у коллеги          | у нас             |
|--------------------|-------------------|
| `integrator_min/max` (симметричные) | `anti_windup` |
| `output_min/max`   | `min_out`/`max_out` |
| `derivative_tau_s` | `der_filter_tf`   |

`integral_decay` остаётся нулевым: в его регуляторе утечки интеграла нет, а leaky-интегратор
изменил бы поведение на длинном заходе.

## Почему воздушные PID не входят в пространство коэффициентов NPGS

`config/regulators.py` фиксирует пять регуляторов пробега, из которых собраны `ACTION_DIM`,
`gain_space` и все сохранённые чекпоинты. Добавить сюда ещё три регулятора значило бы
переопределить пространство действий и обесценить обученные веса. На воздушном участке
управление пока **классическое, со статическими коэффициентами** — как и договорено; когда
воздушный участок пойдёт под нейросеть, это будет отдельное расширение `REGULATOR_ORDER`
с переобучением, а не побочный эффект.
"""

import json
from dataclasses import dataclass, field, replace
from pathlib import Path

# --------------------------------------------------------------------------- #
# Регуляторы воздушного участка (аргументы `control.pid.PIDController`)
# --------------------------------------------------------------------------- #

_ROMAN_PID_FLAGS = dict(
    derivative_on_measurement=True,
    conditional_anti_windup=True,
    exact_discretization=True,
)
"""Флаги, которыми наш `PIDController` воспроизводит численность регулятора коллеги."""

ROLL_PID = dict(kp=-7.0, ki=-0.35, kd=-0.60, min_out=-10.0, max_out=10.0,
                anti_windup=40.0, der_filter_tf=0.2, name="Roll", **_ROMAN_PID_FLAGS)
"""Крен → элероны (градусы). Коэффициенты отрицательные: положительная ошибка крена
парируется отклонением элеронов в минус — знак закреплён проводкой стенда, не опечатка."""

PITCH_PID = dict(kp=0.20, ki=0.0045, kd=0.06, min_out=-0.5, max_out=0.5,
                 anti_windup=20.0, der_filter_tf=0.2, name="Pitch", **_ROMAN_PID_FLAGS)
"""Тангаж → `ElevatorCmd`. Выход — **нормальная перегрузка в g** (так задокументирован
`ElevatorCmd` в датапуле стенда), поэтому предел ±0.5 g, а не градусы руля высоты.
Тот же регулятор и тот же интеграл работают и на выравнивании: меняется только уставка."""

SPEED_PID = dict(kp=0.005, ki=0.0, kd=0.005, min_out=-0.10, max_out=0.10,
                 anti_windup=100.0, der_filter_tf=0.5, name="Speed", **_ROMAN_PID_FLAGS)
"""Приборная скорость → **темп** изменения нормированного положения РУД (1/с). Выход
интегрируется в абсолютную уставку РУД, а на стенд уходит темп в град/с."""


@dataclass
class ApproachConfig:
    """Параметры воздушного контура. Значения по умолчанию — настроенные на стенде.

    Все величины в единицах ICD стенда (узлы, футы, фут/мин, градусы): закон управления
    размерный (град/фут-мин, фут-мин/точка), и перевод в СИ потребовал бы пересчёта каждого
    коэффициента заново.
    """

    name: str = "default"
    draft: bool = False
    """`True` — заготовка под шифр матрицы прогонов, коэффициенты не калиброваны. Такие пресеты
    не подбираются автоматически: до настройки они хуже подтверждённого умолчания, а тихая
    подстановка неоткалиброванного набора на заходе — худший вид ошибки."""

    # --- курсовой канал: курсовой маяк → крен → элероны --- #
    loc_full_scale_ddm: float = 0.155
    """Полное отклонение планки курсового маяка в ddm — делитель для перевода в «точки»."""
    gs_full_scale_ddm: float = 0.175
    localizer_sign: float = 1.0
    localizer_intercept_deg_per_dot: float = 10.0
    max_intercept_angle_deg: float = 15.0
    heading_to_roll_gain: float = 0.70
    max_roll_target_deg: float = 15.0

    # --- глиссада → вертикальная скорость → тангаж --- #
    glideslope_sign: float = -1.0
    """Знак глиссадного отклонения. На этом стенде положительная нормированная величина
    означает «ниже глиссады», отсюда минус."""
    glideslope_vs_correction_fpm_per_dot: float = 400.0
    glideslope_angle_deg: float = 3.0

    # --- опорный угол атаки --- #
    approach_aoa_deg: float = 7.1
    adaptive_aoa_enabled: bool = True
    adaptive_aoa_filter_tau_s: float = 10.0
    adaptive_aoa_min_deg: float = 2.0
    adaptive_aoa_max_deg: float = 10.0
    adaptive_aoa_max_gs_dots: float = 0.25
    adaptive_aoa_max_vs_error_fpm: float = 250.0
    adaptive_aoa_rate_deg_per_s: float = 0.2
    adaptive_aoa_recovery_rate_deg_per_s: float = 0.08

    # --- формирование уставки тангажа --- #
    vs_to_pitch_gain_deg_per_fpm: float = 0.001
    vs_to_pitch_fast_descent_gain_deg_per_fpm: float = 0.0015
    min_approach_target_vs_fpm: float = -900.0
    max_approach_target_vs_fpm: float = -300.0
    min_vertical_correction_deg: float = -1.0
    max_vertical_correction_deg: float = 2.0
    pitch_target_rate_deg_per_s: float = 1.5
    min_pitch_target_deg: float = -1.0
    max_pitch_target_deg: float = 8.0

    # --- масса и конфигурация --- #
    landing_weight_kg: float = 69277.0
    landing_flap_fallback: str = "FLAPS_3"

    # --- выравнивание --- #
    flare_arm_radio_altitude_ft: float = 400.0
    flare_start_radio_altitude_ft: float = 150.0
    flare_max_start_radio_altitude_ft: float = 200.0
    flare_time_to_ground_s: float = 15.0
    flare_end_radio_altitude_ft: float = 5.0
    flare_initial_vs_fpm: float = -472.44
    """Опорная вертикальная скорость входа в выравнивание — **фиксированная**, а не измеренная.
    По мгновенному замеру профиль начинался бы с разной точки при одинаковом заходе."""
    touchdown_target_vs_fpm: float = -68.90
    flare_vs_to_pitch_gain_deg_per_fpm: float = 0.00635
    flare_pitch_base_deg: float = 1.8
    flare_pitch_attitude_damping_gain: float = 0.15
    flare_pitch_rate_damping_gain: float = 0.08
    flare_min_pitch_target_deg: float = 0.5
    flare_pitch_target_rate_deg_per_s: float = 4.0
    flare_max_pitch_target_deg: float = 6.0

    # --- продольная тяга --- #
    elevator_command_sign: float = 1.0
    throttle_forward_max_deg: float = 55.7
    throttle_rate_max_deg_per_s: float = 8.0
    throttle_left_rate_sign: float = 1.0
    throttle_right_rate_sign: float = 1.0
    throttle_position_gain_per_s: float = 0.8
    throttle_sync_boost_threshold_deg: float = 1.0
    throttle_sync_boost_gain_per_s: float = 2.0
    target_ias_rate_kt_per_s: float = 0.25
    """Темп сведения уставки скорости к VAPP. Заход с превышением над VAPP не должен
    оборачиваться немедленным требованием полного торможения."""

    # --- регуляторы --- #
    roll_pid: dict = field(default_factory=lambda: dict(ROLL_PID))
    pitch_pid: dict = field(default_factory=lambda: dict(PITCH_PID))
    speed_pid: dict = field(default_factory=lambda: dict(SPEED_PID))

    # --- ограничения такта --- #
    dt_min_s: float = 0.001
    dt_max_s: float = 0.25
    """Такт зажимается перед расчётом: просадка цикла не должна превращаться в скачок
    интеграла и производной."""

    @classmethod
    def from_json(cls, path) -> "ApproachConfig":
        """Загрузка настроек из JSON коллеги (`config/ics_clear_weather_pid.json`).

        Секции `roll_pid`/`pitch_pid`/`speed_pid` записаны в его терминах и переводятся в
        аргументы нашего `PIDController`; остальные ключи копируются как есть. Неизвестные
        ключи игнорируются — файл может описывать параметры, которых у нас нет.
        """
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        cfg = cls()
        for key, value in raw.items():
            if key in ("roll_pid", "pitch_pid", "speed_pid"):
                setattr(cfg, key, _pid_from_colleague(value, name=key.removesuffix("_pid").title()))
            elif hasattr(cfg, key):
                setattr(cfg, key, value)
        return cfg


def _pid_from_colleague(spec: dict, *, name: str) -> dict:
    """`PIDConfig` коллеги → аргументы нашего `PIDController`.

    Предел интегратора у него задаётся парой `integrator_min/max`, у нас — симметричным
    `anti_windup`. Несимметричная пара выразима не была бы, поэтому она отвергается явно, а не
    молча усредняется.
    """
    integrator_min = float(spec.get("integrator_min", -10.0))
    integrator_max = float(spec.get("integrator_max", 10.0))
    if abs(integrator_min + integrator_max) > 1e-9:
        raise ValueError(
            f"PID '{name}': несимметричные пределы интегратора ({integrator_min}, "
            f"{integrator_max}) не выражаются одним anti_windup")
    return dict(
        kp=float(spec["kp"]), ki=float(spec["ki"]), kd=float(spec["kd"]),
        min_out=float(spec["output_min"]), max_out=float(spec["output_max"]),
        anti_windup=integrator_max,
        der_filter_tf=float(spec.get("derivative_tau_s", 0.25)),
        name=name,
        **_ROMAN_PID_FLAGS,
    )


APPROACH_DEFAULT = ApproachConfig()
"""Настройки захода по умолчанию — «чистая» погода без отказов, откалибровано на стенде."""


def _draft(name: str) -> ApproachConfig:
    """Заготовка воздушного пресета под шифр матрицы: копия подтверждённой настройки.

    Копия, а не нули: стартовать настройку от работающего на стенде набора — это то, как матрица
    и предписывает работать («коэффициенты предыдущего прогона — начальное приближение
    следующего»). Пометка `draft` при этом честно говорит, что под конкретный отказ он ещё не
    считался.
    """
    return replace(APPROACH_DEFAULT, name=name, draft=True,
                   roll_pid=dict(APPROACH_DEFAULT.roll_pid),
                   pitch_pid=dict(APPROACH_DEFAULT.pitch_pid),
                   speed_pid=dict(APPROACH_DEFAULT.speed_pid))


APPROACH_PRESETS: dict[str, ApproachConfig] = {
    "default": APPROACH_DEFAULT,
    # Лист А матрицы прогонов: один шифр — один набор коэффициентов (см. config/run_matrix.py).
    "a_1_1_track": _draft("a_1_1_track"),
    "a_1_2_flare": _draft("a_1_2_flare"),
    "a_2_1_gear_left_up": _draft("a_2_1_gear_left_up"),
    "a_2_2_gear_nose_up": _draft("a_2_2_gear_nose_up"),
    "a_2_3_gear_partial": _draft("a_2_3_gear_partial"),
    "a_3_1_stab_nose_down_high": _draft("a_3_1_stab_nose_down_high"),
    "a_3_2_stab_nose_up_high": _draft("a_3_2_stab_nose_up_high"),
    "a_3_3_stab_nose_down_low": _draft("a_3_3_stab_nose_down_low"),
    "a_3_4_stab_nose_up_low": _draft("a_3_4_stab_nose_up_low"),
    "a_4_1_engine_out_high": _draft("a_4_1_engine_out_high"),
    "a_4_2_engine_partial": _draft("a_4_2_engine_partial"),
    "a_4_3_engine_out_low": _draft("a_4_3_engine_out_low"),
}
"""Пресеты воздушного участка по шифрам матрицы. Все, кроме `default`, — черновые."""
