"""Юнит-тесты Shield (абсолютные коэффициенты): уровни/правила, пресет как якорь, fallback."""

import pytest

from ismpu.agent.shield import (
    Shield, ShieldConfig, GainCommand, RuntimeState, ACTION_DIM, REGULATOR_ORDER,
    base_gains_from_pids, apply_gains_to_pids,
)
from ismpu.agent import gain_space as gs
from ismpu.control.channels import ControlsState
from ismpu.control.pid import PIDController


# Пресет-якорь = коэффициенты DEFAULT (внутри физической полосы gain-пространства).
PRESET = {
    "runway_center_pid": {"kp": 0.0015, "ki": 0.0001, "kd": 0.065},
    "pid_brake_l": {"kp": 0.1, "ki": 0.01, "kd": 0.05},
    "pid_brake_r": {"kp": 0.1, "ki": 0.01, "kd": 0.05},
    "pid_rev_l": {"kp": 0.03, "ki": 0.002, "kd": 0.01},
    "pid_rev_r": {"kp": 0.03, "ki": 0.002, "kd": 0.01},
}
BRAKE_HI = gs.GAIN_HI_MAP["pid_brake_l"]["kp"]   # физический потолок brake kp (0.24)


def _cmd(**overrides) -> GainCommand:
    """GainCommand = пресет с абсолютными override'ами по регуляторам."""
    c = GainCommand.from_gains(PRESET)
    for reg, gains in overrides.items():
        c.gains[reg].update(gains)
    return c


# --------------------------------------------------------------------------- #
# Пресет-как-команда → эффективные gain'ы == пресет (identity-аналог)
# --------------------------------------------------------------------------- #

def test_preset_command_reproduces_preset_no_activation():
    sh = Shield()
    eff, safe, rep = sh.guard_coefficients(GainCommand.from_gains(PRESET), PRESET)
    for reg in PRESET:
        assert eff[reg] == pytest.approx(PRESET[reg])
    assert not rep.active and rep.l_shield == 0.0 and rep.l_smooth == 0.0 and rep.fallback is False


def test_preset_command_inert_across_ticks():
    sh = Shield()
    for _ in range(5):
        eff, _, rep = sh.guard_coefficients(GainCommand.from_gains(PRESET), PRESET)
        assert not rep.active
        assert eff["pid_brake_l"]["kp"] == pytest.approx(PRESET["pid_brake_l"]["kp"])


# --------------------------------------------------------------------------- #
# Уровень 1 — clip к физической полосе gain-пространства
# --------------------------------------------------------------------------- #

def test_level1_clips_gain_to_physical_band():
    sh = Shield()
    eff, safe, rep = sh.guard_coefficients(_cmd(pid_brake_l={"kp": 0.5}), PRESET)  # 0.5 > hi(0.24), < OOD
    assert safe.gains["pid_brake_l"]["kp"] == pytest.approx(BRAKE_HI)
    assert eff["pid_brake_l"]["kp"] == pytest.approx(BRAKE_HI)  # hi(0.24) < 2.5·preset(0.25) → L2 не режет
    assert rep.level1_active
    assert rep.l_shield == pytest.approx(sh.config.w_level1)


def test_level1_clips_channel_weights():
    sh = Shield()
    cmd = GainCommand.from_gains(PRESET)
    cmd.w_lon = 2.5   # > weight_max(2.0), но < weight_ood_max(3.0) → clip, не OOD
    _, safe, rep = sh.guard_coefficients(cmd, PRESET)
    assert safe.w_lon == pytest.approx(2.0)
    assert rep.level1_active and not rep.ood


# --------------------------------------------------------------------------- #
# OOD → fallback на пресет
# --------------------------------------------------------------------------- #

def test_ood_triggers_fallback_to_preset():
    sh = Shield()
    eff, safe, rep = sh.guard_coefficients(_cmd(pid_brake_l={"kp": 1.0}), PRESET)  # > hi·factor → OOD
    assert rep.ood and rep.fallback
    assert safe.gains["pid_brake_l"]["kp"] == pytest.approx(PRESET["pid_brake_l"]["kp"])
    assert eff["pid_brake_l"]["kp"] == pytest.approx(PRESET["pid_brake_l"]["kp"])
    assert rep.l_shield == pytest.approx(sh.config.w_fallback)


# --------------------------------------------------------------------------- #
# Уровень 2 — hard bounds вокруг пресета, rate-limit
# --------------------------------------------------------------------------- #

def test_level2_hard_bounds_clip_around_preset():
    sh = Shield(ShieldConfig(hard_high_factor=1.2))     # узкая граница вокруг пресета
    eff, safe, rep = sh.guard_coefficients(_cmd(pid_brake_l={"kp": 0.15}), PRESET)  # 1.5·preset
    assert eff["pid_brake_l"]["kp"] == pytest.approx(PRESET["pid_brake_l"]["kp"] * 1.2)
    assert rep.level2_active


def test_level2_rate_limit_between_ticks():
    sh = Shield()
    sh.guard_coefficients(GainCommand.from_gains(PRESET), PRESET)                     # такт 1: prev = preset
    eff, _, rep = sh.guard_coefficients(_cmd(pid_brake_l={"kp": 0.15}), PRESET)       # такт 2: +0.05 = 0.5·base
    base_kp = PRESET["pid_brake_l"]["kp"]
    assert eff["pid_brake_l"]["kp"] == pytest.approx(base_kp * 1.25)                  # зажат до +0.25·base
    assert rep.level2_active and rep.l_smooth > 0.0


# --------------------------------------------------------------------------- #
# Уровень 3 — поведение команд (без изменений)
# --------------------------------------------------------------------------- #

def test_level3_disables_reverse_below_60kts():
    sh = Shield()
    cmd = ControlsState()
    cmd.cmd_rev_l, cmd.cmd_rev_r = -0.5, -0.3
    out, rep = sh.guard_command(cmd, RuntimeState(groundspeed_kts=40.0))
    assert out.cmd_rev_l == 0.0 and out.cmd_rev_r == 0.0
    assert rep.level3_active and "L3:reverse_low_speed" in rep.rules


def test_level3_keeps_reverse_above_60kts():
    sh = Shield()
    cmd = ControlsState()
    cmd.cmd_rev_l = -0.5
    out, rep = sh.guard_command(cmd, RuntimeState(groundspeed_kts=100.0))
    assert out.cmd_rev_l == pytest.approx(-0.5)
    assert not rep.level3_active


def test_level3_limits_brake_jerk():
    sh = Shield()
    c1 = ControlsState(); c1.cmd_brake_l = 0.0
    sh.guard_command(c1, RuntimeState(groundspeed_kts=100.0))
    c2 = ControlsState(); c2.cmd_brake_l = 1.0
    out, rep = sh.guard_command(c2, RuntimeState(groundspeed_kts=100.0))
    assert out.cmd_brake_l == pytest.approx(0.5)
    assert rep.level3_active and rep.l_smooth > 0.0


def test_level3_heading_soft_penalty_no_fallback():
    sh = Shield()
    _, rep = sh.guard_command(ControlsState(), RuntimeState(groundspeed_kts=100.0, heading_error_deg=9.0))
    assert rep.level3_active and "L3:heading_soft" in rep.rules and not rep.fallback


def test_level3_heading_hard_latches_fallback_next_tick():
    sh = Shield()
    _, rep = sh.guard_command(ControlsState(), RuntimeState(groundspeed_kts=100.0, heading_error_deg=20.0))
    assert rep.fallback and "L3:heading_hard" in rep.rules
    # следующий такт коэффициентов — пресет, даже с агрессивной командой
    eff, safe, rep2 = sh.guard_coefficients(_cmd(pid_brake_l={"kp": 0.15}), PRESET)
    assert rep2.fallback
    assert eff["pid_brake_l"]["kp"] == pytest.approx(PRESET["pid_brake_l"]["kp"])


# --------------------------------------------------------------------------- #
# Состояние / служебное
# --------------------------------------------------------------------------- #

def test_reset_clears_state():
    sh = Shield()
    sh.guard_coefficients(_cmd(pid_brake_l={"kp": 0.15}), PRESET)
    sh.guard_command(ControlsState(), RuntimeState(groundspeed_kts=100.0, heading_error_deg=20.0))
    sh.reset()
    assert sh._prev_gains is None and sh._prev_brakes is None and sh._fallback_latched is False
    _, _, rep = sh.guard_coefficients(_cmd(pid_brake_l={"kp": 0.15}), PRESET)
    assert not any(r.startswith("L2:rate") for r in rep.rules)


def test_gain_command_vector_roundtrip():
    c = GainCommand.from_gains(PRESET)
    c.gains["pid_rev_l"] = {"kp": 0.05, "ki": 0.003, "kd": 0.02}
    c.w_lat = 1.3
    vec = c.to_vector()
    assert len(vec) == ACTION_DIM
    back = GainCommand.from_vector(vec)
    assert back.gains == c.gains
    assert back.w_lon == pytest.approx(c.w_lon) and back.w_lat == pytest.approx(1.3)


def test_gain_bridge_helpers_with_real_pids():
    pids = {reg: PIDController(kp=PRESET[reg]["kp"], ki=PRESET[reg]["ki"], kd=PRESET[reg]["kd"], name=reg)
            for reg in REGULATOR_ORDER}
    bg = base_gains_from_pids(pids)
    assert bg["pid_brake_l"]["kp"] == pytest.approx(0.1)
    eff = {reg: {"kp": 0.09, "ki": 0.008, "kd": 0.007} for reg in REGULATOR_ORDER}
    apply_gains_to_pids(pids, eff)
    assert pids["pid_brake_l"].kp == 0.09 and pids["pid_rev_r"].kd == 0.007
