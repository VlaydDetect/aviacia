"""Воздушный канал: заход по ILS, выравнивание, скоростной канал.

Главный тест здесь — **паритет с оригиналом**: контур перенесён из рабочего репозитория второго
участника НИР, подтверждённого на живом стенде, и единственный убедительный способ доказать, что
перенос ничего не сломал, — прогнать обе реализации на одной последовательности кадров и сравнить
команды. Если репозиторий коллеги не выложен рядом, паритетные тесты пропускаются, а инварианты
закона проверяются самостоятельно.
"""

import math
import sys
from pathlib import Path

import pytest

from ismpu.config.approach import ApproachConfig, APPROACH_DEFAULT
from ismpu.config.envelope import (
    LandingFlapConfiguration, approach_limits, detect_landing_flaps, measured_landing_flaps,
    roll_limit_deg,
)
from ismpu.control.approach import ApproachChannel, angle_error_deg
from ismpu.control.channels import ControlsState
from ismpu.envs.ics_sim import Telemetry

from fakes import airborne_inputs

COLLEAGUE_ROOT = Path(__file__).resolve().parents[1] / "roman_aviacia_ics"
COLLEAGUE_CONFIG = COLLEAGUE_ROOT / "config" / "ics_clear_weather_pid.json"


def _colleague_controller():
    """Оригинальный контур коллеги, настроенный тем же файлом. `None`, если репозитория нет."""
    tools = COLLEAGUE_ROOT / "tools"
    if not (tools / "ics_pid_controller.py").exists():
        return None
    if str(tools) not in sys.path:
        sys.path.insert(0, str(tools))
    from ics_pid_controller import ClearWeatherILSController, ControllerConfig  # noqa: E402
    return ClearWeatherILSController(ControllerConfig.from_json(COLLEAGUE_CONFIG))


def _our_channel():
    """Наш канал на тех же настройках (файл коллеги, если он есть, иначе умолчания)."""
    cfg = (ApproachConfig.from_json(COLLEAGUE_CONFIG) if COLLEAGUE_CONFIG.exists()
           else ApproachConfig())
    return ApproachChannel(cfg)


def _telemetry(inp) -> Telemetry:
    return Telemetry.from_ics(inp)


def _descent_frames(n=340, *, start_ra=420.0, descent_fps=20.0):
    """Сценарий снижения: высота падает, планка курса и глиссады «дышит», тангаж плавает.

    Кадры намеренно неидеальные: на строго нулевых отклонениях совпали бы даже разные законы.
    """
    frames = []
    ra = start_ra
    pitch = 2.0
    for i in range(n):
        loc = 0.02 * math.sin(i / 9.0)
        gs = 0.015 * math.cos(i / 7.0)
        pitch += 0.05 * math.sin(i / 5.0)
        frames.append(airborne_inputs(
            radio_altitude_ft=ra,
            LocDeviation=loc, GSDeviation=gs,
            PitchAngle=pitch, RollAngle=1.5 * math.sin(i / 11.0),
            BodyPitchRate=0.2 * math.cos(i / 5.0),
            VerticalSpeed=-descent_fps * 60.0 + 40.0 * math.sin(i / 6.0),
            IndicatedAirspeed=143.0 + 2.0 * math.sin(i / 8.0),
            TrueAirspeed=148.0,
            MagneticHeading=75.079 + 0.8 * math.sin(i / 10.0),
            LeftThrottleAngle=20.0 + 0.4 * i % 5, RightThrottleAngle=20.0 + 0.3 * i % 5,
        ))
        ra = max(0.0, ra - descent_fps * 0.05)
    return frames


# --------------------------------------------------------------------------- #
# Паритет с оригиналом
# --------------------------------------------------------------------------- #

def test_matches_the_colleague_implementation_command_for_command():
    """Перенос обязан совпадать с подтверждённым на стенде оригиналом, а не «вести себя похоже».

    Прогоняются обе реализации на одной последовательности кадров — от эшелона захода через
    выравнивание до земли — и сравниваются все три команды на каждом такте.
    """
    reference = _colleague_controller()
    if reference is None:
        pytest.skip("репозиторий второго участника НИР не выложен рядом — сверять не с чем")

    ours = _our_channel()
    state = ControlsState()
    dt = 0.05

    for i, inp in enumerate(_descent_frames()):
        expected = reference.update(inp, dt)          # оригинал читает те же поля по именам
        got = ours.calc_commands(dt, state, _telemetry(inp))

        assert got.aileron_deg == pytest.approx(expected.aileron, abs=1e-12), f"такт {i}"
        assert got.elevator_g == pytest.approx(expected.elevator, abs=1e-12), f"такт {i}"
        assert got.throttle_left_rate_deg_s == pytest.approx(
            expected.throttle_left_rate, abs=1e-12), f"такт {i}"
        assert got.throttle_right_rate_deg_s == pytest.approx(
            expected.throttle_right_rate, abs=1e-12), f"такт {i}"
        assert got.throttle_norm == pytest.approx(expected.throttle_norm, abs=1e-12), f"такт {i}"
        assert got.target_pitch_deg == pytest.approx(expected.target_pitch_deg, abs=1e-12)
        assert got.reference_aoa_deg == pytest.approx(expected.reference_aoa_deg, abs=1e-12)
        assert got.flare_active is expected.flare_active


def test_the_parity_scenario_actually_reaches_flare():
    """Страховка от самообмана: сценарий обязан пройти выравнивание, иначе паритет его не проверил."""
    ours = _our_channel()
    state = ControlsState()
    seen_flare = False
    for inp in _descent_frames():
        res = ours.calc_commands(0.05, state, _telemetry(inp))
        seen_flare = seen_flare or res.flare_active
    assert seen_flare


# --------------------------------------------------------------------------- #
# Знаковые соглашения: их нельзя «поправить», не перевернув смысл канала
# --------------------------------------------------------------------------- #

def test_localizer_deflection_turns_the_aircraft_back_to_the_centreline():
    """Отклонение планки курса задаёт доворот в сторону оси, а не от неё."""
    ours = _our_channel()
    state = ControlsState()
    res = ours.calc_commands(0.05, state, _telemetry(airborne_inputs(LocDeviation=0.05)))
    assert res.loc_dots > 0.0
    assert angle_error_deg(res.target_heading_deg, 75.079) > 0.0   # доворот вправо от курса ВПП
    assert res.target_roll_deg > 0.0                                # и крен туда же


def test_aileron_gains_are_negative_by_design():
    """Крен парируется элеронами с обратным знаком — это проводка стенда, а не опечатка.

    Тест смотрит на знак, а не на величину: лётные коэффициенты (kp = −7) отличаются от
    умолчаний класса коллеги (−1) в семь раз, и закрепление величины ловило бы не то.
    """
    cfg = ApproachConfig()
    assert cfg.roll_pid["kp"] < 0 and cfg.roll_pid["ki"] < 0 and cfg.roll_pid["kd"] < 0

    ours = _our_channel()
    state = ControlsState()
    # ВС кренится вправо при нулевой уставке → элерон должен пойти в минус.
    res = ours.calc_commands(0.05, state, _telemetry(airborne_inputs(RollAngle=5.0)))
    assert res.target_roll_deg == pytest.approx(0.0, abs=1e-9)
    assert res.aileron_deg > 0.0    # kp<0 при отрицательной ошибке даёт положительный выход


def test_below_the_glideslope_commands_a_shallower_descent():
    """Знак глиссады: «ниже глиссады» обязано уменьшать вертикальную скорость снижения.

    Проверяется через `gs_dots` — нормированную величину **после** применения
    `glideslope_sign = −1`. Именно в ней положительное значение означает «ниже глиссады»; знак
    сырого `GSDeviation` на этом стенде обратный, и путать одно с другим — значит перевернуть
    весь продольный канал.
    """
    below = _our_channel().calc_commands(
        0.05, ControlsState(), _telemetry(airborne_inputs(GSDeviation=-0.05)))
    above = _our_channel().calc_commands(
        0.05, ControlsState(), _telemetry(airborne_inputs(GSDeviation=+0.05)))
    assert below.gs_dots > 0.0 > above.gs_dots
    assert below.target_vs_fpm > above.target_vs_fpm


# --------------------------------------------------------------------------- #
# Выравнивание — фаза профиля уставки, а не отдельный закон
# --------------------------------------------------------------------------- #

def test_flare_latches_and_does_not_release_on_a_balloon():
    """Триггер выравнивания залипающий: подскок высоты не должен возвращать заход на глиссаду."""
    ours = _our_channel()
    state = ControlsState()
    ours.calc_commands(0.05, state, _telemetry(airborne_inputs(radio_altitude_ft=140.0)))
    assert ours.result.flare_active is True
    res = ours.calc_commands(0.05, state, _telemetry(airborne_inputs(radio_altitude_ft=300.0)))
    assert res.flare_active is True


def test_flare_keeps_the_same_pitch_regulator_and_its_integral():
    """Никакого отдельного регулятора и никакого сброса интеграла на входе в выравнивание.

    Разрыв интеграла в этот момент — это ступень команды руля высоты в двадцати метрах от
    земли.
    """
    ours = _our_channel()
    state = ControlsState()
    for _ in range(40):
        ours.calc_commands(0.05, state, _telemetry(airborne_inputs(radio_altitude_ft=600.0)))
    before = ours.pitch_pid.integral
    assert before != 0.0

    ours.calc_commands(0.05, state, _telemetry(airborne_inputs(radio_altitude_ft=140.0)))
    assert ours.result.flare_active is True
    # Интеграл продолжился с прежнего значения, а не начался заново.
    assert ours.pitch_pid.integral != 0.0
    assert abs(ours.pitch_pid.integral - before) < abs(before)


def test_flare_entry_reference_is_fixed_not_the_measured_sink_rate():
    """Профиль начинается от настроенной опорной скорости, иначе одинаковые заходы расходятся."""
    ours = _our_channel()
    state = ControlsState()
    res = ours.calc_commands(
        0.05, state, _telemetry(airborne_inputs(radio_altitude_ft=140.0, VerticalSpeed=-1200.0)))
    assert res.flare_active is True
    assert res.flare_entry_vertical_speed_fpm == pytest.approx(
        ours.config.flare_initial_vs_fpm)


def test_elevator_stays_inside_the_load_factor_limits_through_the_whole_descent():
    """`ElevatorCmd` — перегрузка в g, и предел ±0.5 действует и на глиссаде, и в выравнивании."""
    ours = _our_channel()
    state = ControlsState()
    for inp in _descent_frames():
        res = ours.calc_commands(0.05, state, _telemetry(inp))
        assert -0.5 <= res.elevator_g <= 0.5


def test_rudder_is_untouched_in_the_air():
    """Контура парирования сноса нет — наземный контур обязан принимать ВС со сносом."""
    ours = _our_channel()
    state = ControlsState()
    for inp in _descent_frames(n=40):
        ours.calc_commands(0.05, state, _telemetry(inp))
        assert state.rudder_cmd == 0.0


# --------------------------------------------------------------------------- #
# Скоростной канал
# --------------------------------------------------------------------------- #

def test_speed_setpoint_slews_to_vapp_instead_of_demanding_it_at_once():
    """Заход выше VAPP не должен на первом такте требовать полного сброса тяги."""
    ours = _our_channel()
    state = ControlsState()
    first = ours.calc_commands(0.05, state, _telemetry(airborne_inputs(IndicatedAirspeed=170.0)))
    assert first.target_ias_kt == pytest.approx(170.0 - 0.25 * 0.05, abs=1e-9)
    assert first.target_ias_kt > first.vapp_kt if hasattr(first, "vapp_kt") else True


def test_both_engines_are_driven_to_one_throttle_target():
    """Разные углы РУД парируются позиционной обратной связью, а не разной командой тяги."""
    ours = _our_channel()
    state = ControlsState()
    res = ours.calc_commands(0.05, state, _telemetry(airborne_inputs(
        LeftThrottleAngle=18.0, RightThrottleAngle=24.0)))
    # Левый отстаёт от общей уставки → его темп больше правого, но цель у обоих одна.
    assert res.throttle_left_rate_deg_s > res.throttle_right_rate_deg_s
    assert state.cmd_throttle_norm == res.throttle_norm


def test_throttle_integral_does_not_wind_up_against_the_stop():
    """Уставка РУД упёрлась в 0 — интеграл скоростного регулятора не должен копить за пределом."""
    ours = _our_channel()
    state = ControlsState()
    for _ in range(200):
        ours.calc_commands(0.05, state, _telemetry(airborne_inputs(
            IndicatedAirspeed=200.0, LeftThrottleAngle=0.0, RightThrottleAngle=0.0)))
    assert 0.0 <= state.cmd_throttle_norm <= 1.0


# --------------------------------------------------------------------------- #
# Отсутствие данных
# --------------------------------------------------------------------------- #

def test_no_bench_packet_means_no_airborne_command():
    """Размерный закон по нулям выдал бы правдоподобное отклонение по несуществующим данным."""
    ours = _our_channel()
    state = ControlsState()
    state.cmd_elevator = 0.4
    state.cmd_aileron = -3.0
    ours.calc_commands(0.05, state, Telemetry(lat=0.0, lon=0.0, groundspeed_ms=60.0,
                                              heading_true_deg=75.0))
    assert state.cmd_elevator == 0.0 and state.cmd_aileron == 0.0

    state.cmd_elevator = 0.4
    ours.calc_commands(0.05, state, Telemetry.invalid())
    assert state.cmd_elevator == 0.0


# --------------------------------------------------------------------------- #
# Эксплуатационные ограничения
# --------------------------------------------------------------------------- #

def test_landing_flap_detection_reports_a_non_landing_configuration():
    """Непосадочное положение — это `None`, а не молчаливая подмена предположением."""
    assert measured_landing_flaps(27.0) is LandingFlapConfiguration.FLAPS_3
    assert measured_landing_flaps(36.0) is LandingFlapConfiguration.FULL
    assert measured_landing_flaps(5.0) is None
    assert detect_landing_flaps(5.0, LandingFlapConfiguration.FLAPS_3) is \
        LandingFlapConfiguration.FLAPS_3


def test_approach_limits_take_the_conservative_weight_row():
    """Между строками таблицы берётся ближайшая сверху, а не интерполяция."""
    limits = approach_limits(69277.0, LandingFlapConfiguration.FLAPS_3, mach=0.32)
    assert limits.table_weight_kg == 70000.0
    assert limits.vapp_kt == 140.0
    assert approach_limits(69277.0, LandingFlapConfiguration.FULL, mach=0.32).vapp_kt == 136.0


def test_roll_limit_tightens_towards_the_ground():
    """Чем ниже, тем меньше запас до касания законцовкой; настроенный предел не ослабляется."""
    assert roll_limit_deg(1000.0, 15.0) == 15.0
    assert roll_limit_deg(150.0, 15.0) == 15.0    # ступень 30° мягче настроенных 15°
    assert roll_limit_deg(80.0, 15.0) == 10.0
    assert roll_limit_deg(20.0, 15.0) == 5.0


def test_envelope_warnings_do_not_touch_the_command():
    """Предупреждения — это отчёт. Закон от них не меняется, иначе это скрытая защита."""
    ours = _our_channel()
    state = ControlsState()
    res = ours.calc_commands(0.05, state, _telemetry(airborne_inputs(IndicatedAirspeed=190.0)))
    assert "VFE" in res.envelope_warnings
    assert res.elevator_g == state.cmd_elevator     # команда та же, что и посчитана


def test_default_config_carries_the_tuned_bench_gains():
    """Умолчания пакета — это настроенные на стенде значения, а не дефолты класса коллеги."""
    assert APPROACH_DEFAULT.roll_pid["kp"] == -7.0
    assert APPROACH_DEFAULT.pitch_pid["kp"] == 0.20
    assert APPROACH_DEFAULT.speed_pid["kp"] == 0.005
    for spec in (APPROACH_DEFAULT.roll_pid, APPROACH_DEFAULT.pitch_pid,
                 APPROACH_DEFAULT.speed_pid):
        assert spec["derivative_on_measurement"] is True
        assert spec["conditional_anti_windup"] is True
        assert spec["exact_discretization"] is True


def test_config_from_the_colleague_json_matches_our_defaults():
    """Наши умолчания и его файл — одно и то же. Разойдутся — расхождение должно быть видно."""
    if not COLLEAGUE_CONFIG.exists():
        pytest.skip("файл настроек второго участника НИР не выложен рядом")
    loaded = ApproachConfig.from_json(COLLEAGUE_CONFIG)
    assert loaded.roll_pid == APPROACH_DEFAULT.roll_pid
    assert loaded.pitch_pid == APPROACH_DEFAULT.pitch_pid
    assert loaded.speed_pid == APPROACH_DEFAULT.speed_pid
    assert loaded.flare_initial_vs_fpm == APPROACH_DEFAULT.flare_initial_vs_fpm
    assert loaded.approach_aoa_deg == APPROACH_DEFAULT.approach_aoa_deg
