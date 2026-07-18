"""Тесты Этапа 2: Observation/Action/reward/RolloutEnv + инвариант identity == классика."""

import numpy as np
import pytest

from ismpu.config.constants import DT
from ismpu.config.runway import RWY_START_LAT, RWY_START_LON, RWY_HEADING_TRUE
from ismpu.control.system import ControllingSystem
from ismpu.control.channels import ControlsState
from ismpu.envs.sim_interface import XPlaneBackend
from ismpu.envs.scenario import SCENARIO_PRESETS
from ismpu.envs.observation import ObservationBuilder, OBS_DIM, FEATURE_NAMES, ObserverEstimate
from ismpu.envs.action import decode, apply_corrections, preset_action, REFERENCE_ACTION, ACTION_LOW, ACTION_HIGH
from ismpu.envs.reward import compute_reward, RewardWeights
from ismpu.envs.rollout_env import RolloutEnv
from ismpu.agent.shield import base_gains_from_pids
from ismpu.agent import normalization as norm
from ismpu.io.datarefs import (
    LATITUDE, LONGITUDE, GROUNDSPEED, TRUE_PSI,
    LEFT_BRAKE_RATIO, RIGHT_BRAKE_RATIO, THROTTLE_RATIO_L, THROTTLE_RATIO_R, YOKE_HEADING_RATIO,
)

_CONTROL_DREFS = {LEFT_BRAKE_RATIO, RIGHT_BRAKE_RATIO, THROTTLE_RATIO_L, THROTTLE_RATIO_R, YOKE_HEADING_RATIO}


def _scripted_values(groundspeed=50.0):
    return {
        LATITUDE: {"value": RWY_START_LAT},
        LONGITUDE: {"value": RWY_START_LON},
        GROUNDSPEED: {"value": groundspeed},
        TRUE_PSI: {"value": float(RWY_HEADING_TRUE)},
    }


class FakeXPC:
    """Мок X-Plane со скриптованной телеметрией; subscribe не перезатирает заданные значения."""

    def __init__(self, values):
        self.current_dref_values = dict(values)
        self.sent = []

    def sendDREF(self, dref, value):
        self.sent.append((dref, value))

    def sendCTRL(self, **kw):
        pass

    def sendPOSI(self, **kw):
        pass

    def sendCMND(self, *a):
        pass

    def pauseSIM(self, *a):
        pass

    def fix_all_systems(self):
        pass

    def subscribeDREFs(self, subs, timeout=5.0):
        for dref, _ in subs:
            self.current_dref_values.setdefault(dref, {"value": 0.0})

    def getDREF(self, dref):
        v = self.current_dref_values.get(dref)
        return v["value"] if v else 0.0

    def control_sends(self):
        return [(d, v) for d, v in self.sent if d in _CONTROL_DREFS]


# --------------------------------------------------------------------------- #
# Парити классики: env.step(preset_action) == классический control_step (§1)
# (сеть теперь выдаёт АБСОЛЮТНЫЕ gain'ы; классику воспроизводит действие = коэффициенты пресета)
# --------------------------------------------------------------------------- #

def test_env_preset_action_parity_matches_classical_control_step():
    scenario = SCENARIO_PRESETS["default"]     # пресет default → preset_action == REFERENCE_ACTION
    n_steps = 6

    # (A) чистая классика
    fake_a = FakeXPC(_scripted_values())
    ctrl_a = ControllingSystem(xpc=fake_a)
    scenario.apply_control(ctrl_a)
    for _ in range(n_steps):
        ctrl_a.control_step(DT, send=True)
    classical = fake_a.control_sends()

    # (B) среда с действием = точные коэффициенты пресета (float64) без Shield
    fake_b = FakeXPC(_scripted_values())
    sim = XPlaneBackend(xpc=fake_b, settle_s=0.0, reload_each_reset=False)
    ctrl_b = ControllingSystem(xpc=fake_b)
    env = RolloutEnv(sim, ctrl_b, shield=None)
    env.reset(scenario)
    action = preset_action(base_gains_from_pids(ctrl_b.pids))   # точная запись пресета
    for _ in range(n_steps):
        env.step(action)
    via_env = fake_b.control_sends()

    assert len(classical) == 5 * n_steps
    assert via_env == pytest.approx(classical)   # бит-в-бит совпадение команд


def test_preset_action_leaves_scenario_gains_unchanged():
    fake = FakeXPC(_scripted_values())
    ctrl = ControllingSystem(xpc=fake)
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
    fake = FakeXPC(_scripted_values())
    ctrl = ControllingSystem(xpc=fake)
    SCENARIO_PRESETS[preset].apply_control(ctrl)
    ctrl.control_step(DT, send=True)   # заполнить state/PID-внутренности/traveled
    return ctrl


def test_observation_dim_and_names_consistent():
    assert OBS_DIM == len(FEATURE_NAMES)
    assert OBS_DIM == 56


def test_observation_in_normalized_range():
    from ismpu.envs.sim_interface import Telemetry
    ctrl = _ready_controller()
    telem = Telemetry(lat=RWY_START_LAT, lon=RWY_START_LON, groundspeed_ms=50.0,
                      heading_true_deg=float(RWY_HEADING_TRUE), roll_deg=2.0, accel_long_g=-0.3)
    obs = ObservationBuilder().build(telem, ctrl, SCENARIO_PRESETS["nws_fail"].weather, ObserverEstimate())
    assert obs.shape == (OBS_DIM,)
    assert obs.dtype == np.float32
    assert np.all(obs >= -1.0) and np.all(obs <= 1.0)


def test_observation_invalid_telemetry_is_zeros():
    from ismpu.envs.sim_interface import Telemetry
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
# Reward
# --------------------------------------------------------------------------- #

def test_reward_zero_deviation_is_least_penalized():
    cmd = ControlsState()
    good = compute_reward(xte_m=0.0, heading_error_deg=0.0, speed_error_ms=0.0, command=cmd)
    bad = compute_reward(xte_m=6.0, heading_error_deg=10.0, speed_error_ms=20.0, command=cmd)
    assert good.total == pytest.approx(0.0)
    assert bad.total < good.total
    assert bad.xte == pytest.approx(2.0)   # 6 м / 3 м = 2 (вне гейта ±3 м)


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


# --------------------------------------------------------------------------- #
# RolloutEnv API
# --------------------------------------------------------------------------- #

def test_env_reset_and_step_shapes_and_history():
    scenario = SCENARIO_PRESETS["default"]
    fake = FakeXPC(_scripted_values())
    sim = XPlaneBackend(xpc=fake, settle_s=0.0, reload_each_reset=False)
    ctrl = ControllingSystem(xpc=fake)
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

    fake_a = FakeXPC(_scripted_values())
    ctrl_a = ControllingSystem(xpc=fake_a)
    scenario.apply_control(ctrl_a)
    for _ in range(n):
        ctrl_a.control_step(DT, send=True)

    fake_b = FakeXPC(_scripted_values())
    ctrl_b = ControllingSystem(xpc=fake_b)
    env = RolloutEnv(XPlaneBackend(xpc=fake_b, settle_s=0.0, reload_each_reset=False),
                     ctrl_b, shield=Shield())
    env.reset(scenario)
    action = preset_action(base_gains_from_pids(ctrl_b.pids))
    for _ in range(n):
        env.step(action)

    assert fake_b.control_sends() == pytest.approx(fake_a.control_sends())


# --------------------------------------------------------------------------- #
# Нормировка
# --------------------------------------------------------------------------- #

def test_normalization_snapshot_serializable():
    snap = norm.snapshot()
    assert snap["version"] == norm.NORM_VERSION
    assert snap["xte"] == norm.XTE_SCALE
    import json
    json.dumps(snap)   # сериализуемо
