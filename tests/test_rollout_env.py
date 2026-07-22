"""Тесты Этапа 2: Observation/Action/reward/RolloutEnv + инвариант identity == классика."""

import numpy as np
import pytest

from ismpu.config.constants import DT
from ismpu.config.runway import RWY_START_LAT, RWY_START_LON, RWY_HEADING_TRUE
from ismpu.control.system import ControllingSystem
from ismpu.control.channels import ControlsState
from ismpu.envs.ics_sim import ICSSim, Telemetry
from ismpu.envs.scenario import SCENARIO_PRESETS
from ismpu.envs.observation import ObservationBuilder, OBS_DIM, FEATURE_NAMES, ObserverEstimate
from ismpu.envs.action import decode, apply_corrections, preset_action, REFERENCE_ACTION, ACTION_LOW, ACTION_HIGH
from ismpu.envs.reward import (
    compute_reward, RewardWeights, EpisodeObjective, saturation_fraction,
    graded, excess, xte_limit_for, SHAPING_SLOPE, SPEED_TOL_MS, OVERSPEED_FACTOR,
)
from ismpu.config.requirements import XTE_ROLLOUT_MAX_M, XTE_TAXI_MAX_M, HEADING_FAULT_MAX_DEG
from ismpu.envs.rollout_env import RolloutEnv, heading_deviation_deg
from ismpu.control.runway_tracker import RunwayTracker
from ismpu.agent.shield import base_gains_from_pids
from ismpu.agent import normalization as norm

from fakes import static_sim, make_ics_inputs, telemetry as _telemetry


# --------------------------------------------------------------------------- #
# Парити классики: env.step(preset_action) == классический control_step (§1)
# (сеть теперь выдаёт АБСОЛЮТНЫЕ gain'ы; классику воспроизводит действие = коэффициенты пресета)
# --------------------------------------------------------------------------- #

def test_env_preset_action_parity_matches_classical_control_step():
    scenario = SCENARIO_PRESETS["default"]     # пресет default → preset_action == REFERENCE_ACTION
    n_steps = 6

    # (A) чистая классика. Телеметрию читаем тем же стендом, что и среда, — иначе парити
    # проверяло бы заодно и совпадение двух разных способов собрать кадр.
    sim_a, conn_a = static_sim()
    ctrl_a = ControllingSystem(sim_a)
    scenario.apply_control(ctrl_a)
    for _ in range(n_steps):
        ctrl_a.control_step(DT, sim_a.read_telemetry(), send=True)
    classical = conn_a.commands()

    # (B) среда с действием = точные коэффициенты пресета (float64) без Shield
    sim_b, conn_b = static_sim()
    ctrl_b = ControllingSystem(sim_b)
    env = RolloutEnv(sim_b, ctrl_b, shield=None)
    env.reset(scenario)
    action = preset_action(base_gains_from_pids(ctrl_b.pids))   # точная запись пресета
    for _ in range(n_steps):
        env.step(action)
    via_env = conn_b.commands()

    assert len(classical) == n_steps
    assert via_env == pytest.approx(classical)   # бит-в-бит совпадение команд


def test_preset_action_leaves_scenario_gains_unchanged():
    ctrl = ControllingSystem(static_sim()[0])
    SCENARIO_PRESETS["nws_fail"].apply_control(ctrl)
    preset = base_gains_from_pids(ctrl.pids)

    # действие = абсолютные коэффициенты пресета → gain'ы не меняются
    apply_corrections(decode(preset_action(preset)), preset, ctrl, shield=None)

    for reg in preset:
        assert ctrl.pids[reg].kp == pytest.approx(preset[reg]["kp"])
        assert ctrl.pids[reg].ki == pytest.approx(preset[reg]["ki"])
        assert ctrl.pids[reg].kd == pytest.approx(preset[reg]["kd"])
    assert ctrl.longitudinal_channel.w_lon == 1.0
    assert ctrl.lateral_channel.w_lat == 1.0


# --------------------------------------------------------------------------- #
# Observation Space
# --------------------------------------------------------------------------- #

def _ready_controller(preset="nws_fail"):
    ctrl = ControllingSystem(static_sim()[0])
    SCENARIO_PRESETS[preset].apply_control(ctrl)
    ctrl.control_step(DT, _telemetry(), send=True)   # заполнить state/PID-внутренности/traveled
    return ctrl


def test_observation_dim_and_names_consistent():
    assert OBS_DIM == len(FEATURE_NAMES)
    assert OBS_DIM == 56


def test_observation_in_normalized_range():
    ctrl = _ready_controller()
    telem = Telemetry(lat=RWY_START_LAT, lon=RWY_START_LON, groundspeed_ms=50.0,
                      heading_true_deg=float(RWY_HEADING_TRUE), roll_deg=2.0, accel_long_g=-0.3)
    obs = ObservationBuilder().build(telem, ctrl, SCENARIO_PRESETS["nws_fail"].weather, ObserverEstimate())
    assert obs.shape == (OBS_DIM,)
    assert obs.dtype == np.float32
    assert np.all(obs >= -1.0) and np.all(obs <= 1.0)


def test_observation_invalid_telemetry_is_zeros():
    ctrl = _ready_controller()
    telem = Telemetry(lat=0.0, lon=0.0, groundspeed_ms=0.0, heading_true_deg=0.0, valid=False)
    obs = ObservationBuilder().build(telem, ctrl, SCENARIO_PRESETS["default"].weather)
    assert np.count_nonzero(obs) == 0


# --------------------------------------------------------------------------- #
# Action Space
# --------------------------------------------------------------------------- #

def test_reference_action_decodes_to_default_gains():
    from ismpu.agent import gain_space as gs
    cmd = decode(REFERENCE_ACTION)
    for i, (reg, key) in enumerate(gs.SLOTS):
        assert cmd.gains[reg][key] == pytest.approx(gs.GAIN_DEFAULT[i])
    assert cmd.w_lon == 1.0 and cmd.w_lat == 1.0


def test_action_bounds_shape():
    assert ACTION_LOW.shape == (17,) and ACTION_HIGH.shape == (17,)
    assert np.all(ACTION_LOW <= REFERENCE_ACTION) and np.all(REFERENCE_ACTION <= ACTION_HIGH)


# --------------------------------------------------------------------------- #
# ControlsState: настоящие поля dataclass и сброс между эпизодами
# --------------------------------------------------------------------------- #

def test_controls_state_has_real_dataclass_fields():
    """Без аннотаций типов @dataclass не видит полей, и тогда любые два экземпляра равны.

    Это делало бы бессмысленной любую проверку команд через `==`: тест проходил бы всегда.
    """
    from dataclasses import fields
    names = [f.name for f in fields(ControlsState)]
    assert names == ["break_control", "rudder_cmd",
                     "cmd_brake_l", "cmd_brake_r", "cmd_rev_l", "cmd_rev_r"]

    a, b = ControlsState(), ControlsState()
    assert a == b                      # одинаковые команды — равны
    a.cmd_brake_l = 1.0
    assert a != b                      # разные команды — НЕ равны
    assert b.cmd_brake_l == 0.0        # экземпляры независимы


def test_controls_state_values_live_in_the_instance_from_construction():
    """Свежий экземпляр обязан нести все поля в собственном `__dict__`.

    Без аннотаций они были бы атрибутами КЛАССА, а `vars()` нового экземпляра — пустым:
    значение читалось бы из общего состояния до первой записи в экземпляр.
    """
    own = vars(ControlsState())
    assert set(own) == {"break_control", "rudder_cmd",
                        "cmd_brake_l", "cmd_brake_r", "cmd_rev_l", "cmd_rev_r"}
    assert own["cmd_rev_l"] == 0.0


def test_break_control_is_cleared_when_a_scenario_is_applied():
    """`break_control` взводится в конце КАЖДОГО нормального пробега (достигнута скорость
    руления). Без сброса при настройке сценария следующий эпизод завершался бы на первом такте —
    в обучении PPO это давало бы эпизоды длиной 1."""
    ctrl = ControllingSystem(static_sim()[0])
    SCENARIO_PRESETS["default"].apply_control(ctrl)

    ctrl.state.break_control = True          # имитируем завершившийся эпизод
    SCENARIO_PRESETS["default"].apply_control(ctrl)
    assert ctrl.state.break_control is False

    # ...и такт после сброса действительно выполняется, а не завершается сразу
    assert ctrl.control_step(DT, _telemetry(), send=True) is False


def test_env_reset_clears_a_latched_break_control():
    scenario = SCENARIO_PRESETS["default"]
    sim, _conn = static_sim()
    ctrl = ControllingSystem(sim)
    env = RolloutEnv(sim, ctrl, shield=None)

    env.reset(scenario)
    ctrl.state.break_control = True
    env.reset(scenario)
    assert ctrl.state.break_control is False

    action = preset_action(base_gains_from_pids(ctrl.pids))
    _obs, _reward, terminated, _truncated, _info = env.step(action)
    assert terminated is False


# --------------------------------------------------------------------------- #
# Прогрев: такты рукопожатия не должны попадать в эпизод
# --------------------------------------------------------------------------- #

class _WarmUpSim(ICSSim):
    """Стенд, включающий управление только после N тактов прогрева.

    Само рукопожатие проверяется в `test_ics_sim.py`; здесь важно лишь то, что его такты не
    считаются шагами эпизода.
    """

    def __init__(self, warm_ticks=5):
        sim, conn = static_sim()
        super().__init__(connector=conn, engagement=sim.engagement)
        self.warm_ticks = warm_ticks
        self.warm_frames = 0
        self._forced_engaged = False

    @property
    def engaged(self):
        return self._forced_engaged

    def warm_up(self, timeout_s=10.0, dt=None):
        while not self._forced_engaged:
            self.step(ControlsState())
            self.warm_frames += 1
            if self.warm_frames >= self.warm_ticks:
                self._forced_engaged = True
        return True


def test_warm_up_runs_before_the_episode_and_is_not_counted():
    """Такты рукопожатия — не шаги эпизода: в это время ВС нами не управлялось.

    Иначе они попали бы в `_steps`, в reward и в `EpisodeObjective`, который использует приёмка.
    """
    sim = _WarmUpSim(warm_ticks=5)
    env = RolloutEnv(sim, ControllingSystem(sim), shield=None)

    env.reset(SCENARIO_PRESETS["default"])

    assert sim.engaged is True              # прогрев отработал внутри reset
    assert sim.warm_frames == 5
    assert env._steps == 0                  # но в счётчик эпизода не попал
    assert env.objective.diagnostics()["samples"] == 0


def test_env_reports_engagement_state_in_info():
    sim = _WarmUpSim(warm_ticks=2)
    env = RolloutEnv(sim, ControllingSystem(sim), shield=None)
    env.reset(SCENARIO_PRESETS["default"])

    action = preset_action(base_gains_from_pids(env.controller.pids))
    _obs, _r, _term, _trunc, info = env.step(action)
    assert info["engaged"] is True


# --------------------------------------------------------------------------- #
# Метрика курса: отклонение от ВПП, а не ошибка команды руления
# --------------------------------------------------------------------------- #

def _telemetry_at(offset_m: float, heading_deg: float, *, runway_heading=None):
    """Телеметрия ВС на оси ВПП, смещённого вбок на `offset_m` и с заданным курсом.

    Курс ВПП, если задан, приходит «сырым» пакетом стенда (как на реальном стенде), а не отдельным
    полем: его отдаёт property `Telemetry.runway_heading_deg`. Без пакета — `ics_inputs=None`.
    """
    from dataclasses import fields as _fields
    from ismpu.io.ics_connector import ICSInputs
    t = RunwayTracker()
    brg = np.radians(RWY_HEADING_TRUE)
    lat, lon = t.destination(RWY_START_LAT, RWY_START_LON, brg, 800.0)
    if offset_m:
        side = np.radians(RWY_HEADING_TRUE + (90.0 if offset_m > 0 else -90.0))
        lat, lon = t.destination(lat, lon, side, abs(offset_m))
    ics = None
    if runway_heading is not None:
        data = {f.name: 0 for f in _fields(ICSInputs)}
        data.update(RunwayHeadingValid=1, RunwayHeading=runway_heading)
        ics = ICSInputs.from_dict(data)
    return Telemetry(lat=lat, lon=lon, groundspeed_ms=50.0, heading_true_deg=heading_deg,
                     ics_inputs=ics)


def test_heading_deviation_ignores_lateral_offset():
    """ТЗ 5.1.3.3 нормирует курс «от направления ВПП». Смещение от оси на него не влияет.

    Ошибка команды руления (`guidance()["heading_error_deg"]`) на 5 м смещения показывает −6.35°
    и объявила бы провал гейта ±5° при идеально выдержанном курсе.
    """
    tracker = RunwayTracker()
    for offset in (0.0, 3.0, 5.0, 10.0):
        telem = _telemetry_at(offset, float(RWY_HEADING_TRUE))
        assert heading_deviation_deg(telem) == pytest.approx(0.0, abs=1e-6)

    # А ошибка команды на тех же данных растёт с отклонением — это разные величины.
    telem = _telemetry_at(5.0, float(RWY_HEADING_TRUE))
    command_error = tracker.guidance(telem.lat, telem.lon, telem.heading_true_deg, 50.0)
    assert abs(command_error["heading_error_deg"]) > 5.0


def test_heading_deviation_tracks_actual_yaw():
    telem = _telemetry_at(0.0, float(RWY_HEADING_TRUE) + 4.0)
    assert heading_deviation_deg(telem) == pytest.approx(4.0)
    telem = _telemetry_at(0.0, float(RWY_HEADING_TRUE) - 6.0)
    assert heading_deviation_deg(telem) == pytest.approx(-6.0)


def test_heading_deviation_wraps_across_north():
    telem = _telemetry_at(0.0, float(RWY_HEADING_TRUE) + 358.0)
    assert heading_deviation_deg(telem) == pytest.approx(-2.0)


def test_heading_deviation_prefers_runway_heading_from_telemetry():
    """На стенде курс ВПП приходит телеметрией; конфиг — только значение по умолчанию."""
    telem = _telemetry_at(0.0, 100.0, runway_heading=97.0)
    assert heading_deviation_deg(telem) == pytest.approx(3.0)


def test_tz_gate_verdicts_flip_to_correct_after_the_fix():
    """Таблица из находки: раньше оба случая давали противоположный результат."""
    from ismpu.runtime.evaluate import evaluate_tz, PASS, FAIL

    def verdict(offset_m, yaw_deg):
        telem = _telemetry_at(offset_m, float(RWY_HEADING_TRUE) + yaw_deg)
        diagnostics = {"samples": 100, "xte_rollout_max_m": abs(offset_m),
                       "xte_taxi_max_m": None, "final_speed_kts": 70.0,
                       "heading_max_deg": abs(heading_deviation_deg(telem))}
        criteria = evaluate_tz(diagnostics, SCENARIO_PRESETS["left_reverse_fail"])
        return next(c.verdict for c in criteria if c.name == "heading_max")

    assert verdict(offset_m=5.0, yaw_deg=0.0) == PASS    # курс выдержан, смещение не при чём
    assert verdict(offset_m=0.0, yaw_deg=6.0) == FAIL    # курс сорван на оси


# --------------------------------------------------------------------------- #
# Reward
# --------------------------------------------------------------------------- #

def test_reward_zero_deviation_is_least_penalized():
    cmd = ControlsState()
    good = compute_reward(xte_m=0.0, heading_error_deg=0.0, speed_error_ms=0.0, command=cmd)
    bad = compute_reward(xte_m=6.0, heading_error_deg=10.0, speed_error_ms=20.0, command=cmd)
    assert good.total == pytest.approx(0.0)
    assert bad.total < good.total
    # 6 м при допуске 3 м: наклон внутри полосы + превышение (6−3)/3 = 1.0
    assert bad.xte == pytest.approx(SHAPING_SLOPE + 1.0)


def test_reward_counts_shield_and_jerk():
    prev = ControlsState()
    cmd = ControlsState()
    cmd.cmd_brake_l = 0.7   # рывок относительно prev (0)
    r = compute_reward(xte_m=0.0, heading_error_deg=0.0, speed_error_ms=0.0,
                       command=cmd, prev_command=prev, shield_l_shield=1.0,
                       weights=RewardWeights())
    assert r.jerk == pytest.approx(0.7)
    assert r.shield == pytest.approx(1.0)
    assert r.total < 0.0


# --- форма гейта ТЗ ---------------------------------------------------------- #

def test_graded_penalty_breaks_exactly_at_the_tz_limit():
    """Ровно на пороге ТЗ штраф = наклон внутри полосы; дальше растёт много круче."""
    limit = XTE_ROLLOUT_MAX_M
    assert graded(0.0, limit) == pytest.approx(0.0)
    assert graded(limit, limit) == pytest.approx(SHAPING_SLOPE)
    # Внутри полосы наклон слабый, за порогом — 1.0 на допуск, т.е. в 1/SHAPING_SLOPE раз круче.
    inside_slope = graded(limit, limit) - graded(0.0, limit)
    outside_slope = graded(2 * limit, limit) - graded(limit, limit)
    assert outside_slope == pytest.approx(1.0)
    assert outside_slope > inside_slope / SHAPING_SLOPE * 0.9


def test_excess_is_zero_inside_the_tolerance():
    assert excess(2.9, XTE_ROLLOUT_MAX_M) == pytest.approx(0.0)
    assert excess(-2.9, XTE_ROLLOUT_MAX_M) == pytest.approx(0.0)   # знак не важен
    assert excess(6.0, XTE_ROLLOUT_MAX_M) == pytest.approx(1.0)


def test_xte_limit_switches_to_taxi_tolerance_at_low_speed():
    assert xte_limit_for(80.0) == XTE_ROLLOUT_MAX_M
    assert xte_limit_for(10.0) == XTE_TAXI_MAX_M
    assert xte_limit_for(None) == XTE_ROLLOUT_MAX_M   # неизвестна фаза → менее строгий допуск
    # Одно и то же отклонение на рулении штрафуется сильнее, чем на пробеге.
    cmd = ControlsState()
    rollout = compute_reward(xte_m=2.0, heading_error_deg=0.0, speed_error_ms=0.0,
                             command=cmd, groundspeed_kts=80.0)
    taxi = compute_reward(xte_m=2.0, heading_error_deg=0.0, speed_error_ms=0.0,
                          command=cmd, groundspeed_kts=10.0)
    assert taxi.xte > rollout.xte


def test_speed_penalty_is_asymmetric_overspeed_costs_more():
    """Перелёт по скорости к концу ВПП опаснее недолёта — симметричным модулем не выражается."""
    cmd = ControlsState()
    delta = SPEED_TOL_MS + 10.0
    fast = compute_reward(xte_m=0.0, heading_error_deg=0.0, speed_error_ms=delta, command=cmd)
    slow = compute_reward(xte_m=0.0, heading_error_deg=0.0, speed_error_ms=-delta, command=cmd)
    assert fast.speed == pytest.approx(OVERSPEED_FACTOR * slow.speed)
    # Внутри мёртвой зоны штрафа нет вообще.
    inside = compute_reward(xte_m=0.0, heading_error_deg=0.0,
                            speed_error_ms=SPEED_TOL_MS - 0.1, command=cmd)
    assert inside.speed == pytest.approx(0.0)


def test_heading_gate_uses_tz_threshold():
    cmd = ControlsState()
    at_limit = compute_reward(xte_m=0.0, heading_error_deg=HEADING_FAULT_MAX_DEG,
                              speed_error_ms=0.0, command=cmd)
    beyond = compute_reward(xte_m=0.0, heading_error_deg=2 * HEADING_FAULT_MAX_DEG,
                            speed_error_ms=0.0, command=cmd)
    assert at_limit.heading == pytest.approx(SHAPING_SLOPE)
    assert beyond.heading == pytest.approx(SHAPING_SLOPE + 1.0)


# --- насыщение --------------------------------------------------------------- #

def test_saturation_fraction_counts_commands_pegged_at_their_pid_bounds():
    controller = ControllingSystem(static_sim()[0])
    SCENARIO_PRESETS["default"].apply_control(controller)
    pids = controller.pids

    cmd = ControlsState()
    cmd.cmd_brake_l = cmd.cmd_brake_r = 0.5      # в середине [0, 1]
    cmd.cmd_rev_l = cmd.cmd_rev_r = -0.5         # в середине [-1, 0]
    cmd.rudder_cmd = 0.0
    assert saturation_fraction(cmd, pids) == pytest.approx(0.0)

    cmd.cmd_brake_l = pids["pid_brake_l"].max_out    # тормоз на максимуме — авторитет исчерпан
    cmd.cmd_rev_l = pids["pid_rev_l"].min_out        # реверс на максимуме (−1) — тоже
    assert saturation_fraction(cmd, pids) == pytest.approx(2.0 / 5.0)


def test_zero_bound_is_not_counted_as_saturation():
    """Тормоз на 0 = «торможение не требуется», а не «авторитет исчерпан».

    Иначе флаг насыщения поднимался бы на каждом такте, где ВС медленнее эталонной кривой,
    т.е. в начале почти любого пробега.
    """
    controller = ControllingSystem(static_sim()[0])
    SCENARIO_PRESETS["default"].apply_control(controller)
    pids = controller.pids

    cmd = ControlsState()
    cmd.cmd_brake_l = cmd.cmd_brake_r = 0.0      # нижняя граница [0, 1] — но это ноль усилия
    cmd.cmd_rev_l = cmd.cmd_rev_r = 0.0          # верхняя граница [-1, 0] — тоже ноль усилия
    cmd.rudder_cmd = 0.0
    assert saturation_fraction(cmd, pids) == pytest.approx(0.0)

    # А симметричный руль упирается с обеих сторон — обе границы означают усилие.
    cmd.rudder_cmd = pids["runway_center_pid"].max_out
    assert saturation_fraction(cmd, pids) == pytest.approx(1.0 / 5.0)
    cmd.rudder_cmd = pids["runway_center_pid"].min_out
    assert saturation_fraction(cmd, pids) == pytest.approx(1.0 / 5.0)

    # Насыщение попадает в reward — прежняя версия его не видела вообще.
    saturated = compute_reward(xte_m=0.0, heading_error_deg=0.0, speed_error_ms=0.0,
                               command=cmd, saturation=1.0)
    clean = compute_reward(xte_m=0.0, heading_error_deg=0.0, speed_error_ms=0.0,
                           command=cmd, saturation=0.0)
    assert saturated.total < clean.total


# --- эпизодный objective ----------------------------------------------------- #

def test_episode_objective_separates_rollout_and_taxi_phases():
    obj = EpisodeObjective()
    cmd = ControlsState()
    # Пробег: 2 м от оси — внутри ±3 м, нарушения нет.
    for _ in range(10):
        obj.add(xte_m=2.0, heading_error_deg=0.0, speed_error_ms=0.0,
                groundspeed_kts=80.0, command=cmd)
    # Руление: те же 2 м — уже вне ±1 м.
    for _ in range(10):
        obj.add(xte_m=2.0, heading_error_deg=0.0, speed_error_ms=0.0,
                groundspeed_kts=10.0, command=cmd)

    d = obj.diagnostics()
    assert d["xte_rollout_max_m"] == pytest.approx(2.0)
    assert d["xte_taxi_max_m"] == pytest.approx(2.0)
    comp = obj.summary()["components"]
    assert comp["xte_rollout"]["raw"] == pytest.approx(0.0)   # в допуске пробега
    assert comp["xte_taxi"]["raw"] > 0.0                       # вне допуска руления


def test_episode_objective_reports_none_for_unobserved_phases():
    """Отсутствие данных даёт None, а не 0 — приёмка обязана трактовать это как FAIL."""
    obj = EpisodeObjective()
    cmd = ControlsState()
    obj.add(xte_m=0.5, heading_error_deg=0.0, speed_error_ms=0.0,
            groundspeed_kts=80.0, command=cmd)
    d = obj.diagnostics()
    assert d["xte_rollout_max_m"] is not None
    assert d["xte_taxi_max_m"] is None       # фазы руления в эпизоде не было
    assert obj.summary()["total_loss"] >= 0.0


def test_episode_objective_p95_rate_is_robust_to_a_single_spike():
    """p95 темпа не ловится одиночным выбросом — в отличие от максимума."""
    obj = EpisodeObjective()
    for i in range(100):
        cmd = ControlsState()
        cmd.cmd_brake_l = 0.5 if i != 50 else 1.0    # один выброс из ста тактов
        obj.add(xte_m=0.0, heading_error_deg=0.0, speed_error_ms=0.0,
                groundspeed_kts=80.0, command=cmd)
    p95 = obj.diagnostics()["rate_p95"]["brake_l"]
    assert p95 < 0.5    # выброс (скачок 0.5) не попал в 95-й перцентиль


# --------------------------------------------------------------------------- #
# RolloutEnv API
# --------------------------------------------------------------------------- #

def test_env_reset_and_step_shapes_and_history():
    scenario = SCENARIO_PRESETS["default"]
    sim, _conn = static_sim()
    ctrl = ControllingSystem(sim)
    env = RolloutEnv(sim, ctrl, history_len=3, shield=None)

    obs, info = env.reset(scenario)
    assert obs.shape == (3, OBS_DIM)        # окно истории как последовательность (T, 56)
    assert info == {}

    obs, reward, terminated, truncated, info = env.step(REFERENCE_ACTION)
    assert obs.shape == (3, OBS_DIM)
    assert isinstance(reward, float)
    assert not terminated and not truncated
    assert "reward_components" in info


def test_env_with_shield_at_preset_still_parity():
    # Действие = пресет → Shield no-op (пресет внутри всех границ), команды = классика.
    from ismpu.agent.shield import Shield
    scenario = SCENARIO_PRESETS["default"]
    n = 4

    sim_a, conn_a = static_sim()
    ctrl_a = ControllingSystem(sim_a)
    scenario.apply_control(ctrl_a)
    for _ in range(n):
        ctrl_a.control_step(DT, sim_a.read_telemetry(), send=True)

    sim_b, conn_b = static_sim()
    ctrl_b = ControllingSystem(sim_b)
    env = RolloutEnv(sim_b, ctrl_b, shield=Shield())
    env.reset(scenario)
    action = preset_action(base_gains_from_pids(ctrl_b.pids))
    for _ in range(n):
        env.step(action)

    assert conn_b.commands() == pytest.approx(conn_a.commands())


# --------------------------------------------------------------------------- #
# Нормировка
# --------------------------------------------------------------------------- #

def test_normalization_snapshot_serializable():
    snap = norm.snapshot()
    assert snap["version"] == norm.NORM_VERSION
    assert snap["xte"] == norm.XTE_SCALE
    import json
    json.dumps(snap)   # сериализуемо
