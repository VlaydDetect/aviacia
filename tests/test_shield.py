"""Юнит-тесты Shield: каждый уровень/правило, инвариант identity, fallback."""

import pytest

from ismpu.agent.shield import (
    Shield, ShieldConfig, Corrections, RuntimeState, ACTION_DIM, REGULATOR_ORDER,
    base_gains_from_pids, apply_gains_to_pids,
)
from ismpu.control.channels import ControlsState
from ismpu.control.pid import PIDController


BASE = {
    "runway_center_pid": {"kp": 0.0015, "ki": 0.0001, "kd": 0.065},
    "pid_brake_l": {"kp": 0.1, "ki": 0.01, "kd": 0.05},
    "pid_brake_r": {"kp": 0.1, "ki": 0.01, "kd": 0.05},
    "pid_rev_l": {"kp": 0.03, "ki": 0.002, "kd": 0.01},
    "pid_rev_r": {"kp": 0.03, "ki": 0.002, "kd": 0.01},
}


def _corr(**overrides) -> Corrections:
    c = Corrections.identity()
    for reg, triple in overrides.items():
        c.alpha[reg] = triple
    return c


# --------------------------------------------------------------------------- #
# Инвариант identity (§1): α = 1, веса = 1 → эффективные gain'ы == базовым
# --------------------------------------------------------------------------- #

def test_identity_reproduces_base_gains_no_activation():
    sh = Shield()
    eff, safe, rep = sh.guard_coefficients(Corrections.identity(), BASE)
    for reg in BASE:
        assert eff[reg] == pytest.approx(BASE[reg])
    assert not rep.active
    assert rep.l_shield == 0.0 and rep.l_smooth == 0.0
    assert rep.fallback is False


def test_identity_stays_inert_across_ticks():
    sh = Shield()
    for _ in range(5):
        eff, _, rep = sh.guard_coefficients(Corrections.identity(), BASE)
        assert not rep.active
        assert eff["pid_brake_l"]["kp"] == pytest.approx(BASE["pid_brake_l"]["kp"])


# --------------------------------------------------------------------------- #
# Уровень 1 — clip поправок
# --------------------------------------------------------------------------- #

def test_level1_clips_alpha_to_band():
    sh = Shield()
    eff, safe, rep = sh.guard_coefficients(_corr(pid_brake_l=(2.0, 1.0, 1.0)), BASE)
    assert safe.alpha["pid_brake_l"][0] == pytest.approx(1.5)   # 2.0 → alpha_max
    assert eff["pid_brake_l"]["kp"] == pytest.approx(BASE["pid_brake_l"]["kp"] * 1.5)
    assert rep.level1_active
    assert rep.l_shield == pytest.approx(sh.config.w_level1)


def test_level1_clips_channel_weights():
    sh = Shield()
    corr = Corrections.identity()
    corr.w_lon = 2.5   # > weight_max(2.0), но < weight_ood_max(3.0) → clip, не OOD
    _, safe, rep = sh.guard_coefficients(corr, BASE)
    assert safe.w_lon == pytest.approx(2.0)
    assert rep.level1_active and not rep.ood


# --------------------------------------------------------------------------- #
# OOD → fallback на классику
# --------------------------------------------------------------------------- #

def test_ood_triggers_fallback_to_identity():
    sh = Shield()
    eff, safe, rep = sh.guard_coefficients(_corr(pid_brake_l=(3.0, 1.0, 1.0)), BASE)
    assert rep.ood and rep.fallback
    assert safe.alpha["pid_brake_l"] == (1.0, 1.0, 1.0)          # заменено на identity
    assert eff["pid_brake_l"]["kp"] == pytest.approx(BASE["pid_brake_l"]["kp"])
    assert rep.l_shield == pytest.approx(sh.config.w_fallback)


# --------------------------------------------------------------------------- #
# Уровень 2 — hard bounds, rate-limit
# --------------------------------------------------------------------------- #

def test_level2_hard_bounds_clip_effective_gain():
    sh = Shield(ShieldConfig(hard_high_factor=1.2))   # искусственно узкая граница
    eff, safe, rep = sh.guard_coefficients(_corr(pid_brake_l=(1.5, 1.0, 1.0)), BASE)
    # α=1.5 не режется уровнем 1, но 1.5·base > 1.2·base → зажимается уровнем 2
    assert eff["pid_brake_l"]["kp"] == pytest.approx(BASE["pid_brake_l"]["kp"] * 1.2)
    assert rep.level2_active


def test_level2_rate_limit_between_ticks():
    sh = Shield()
    sh.guard_coefficients(Corrections.identity(), BASE)              # такт 1: prev = base
    eff, _, rep = sh.guard_coefficients(_corr(pid_brake_l=(1.5, 1.0, 1.0)), BASE)  # такт 2
    base_kp = BASE["pid_brake_l"]["kp"]
    # Δ = 0.5·base зажимается rate_limit_frac=0.25 → prev + 0.25·base = 1.25·base
    assert eff["pid_brake_l"]["kp"] == pytest.approx(base_kp * 1.25)
    assert rep.level2_active and rep.l_smooth > 0.0


# --------------------------------------------------------------------------- #
# Уровень 3 — поведение команд
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
    c1 = ControlsState()
    c1.cmd_brake_l = 0.0
    sh.guard_command(c1, RuntimeState(groundspeed_kts=100.0))   # prev = 0
    c2 = ControlsState()
    c2.cmd_brake_l = 1.0
    out, rep = sh.guard_command(c2, RuntimeState(groundspeed_kts=100.0))
    assert out.cmd_brake_l == pytest.approx(0.5)   # прирост зажат brake_rate_limit
    assert rep.level3_active and rep.l_smooth > 0.0


def test_level3_heading_soft_penalty_no_fallback():
    sh = Shield()
    _, rep = sh.guard_command(ControlsState(), RuntimeState(groundspeed_kts=100.0, heading_error_deg=9.0))
    assert rep.level3_active and "L3:heading_soft" in rep.rules
    assert not rep.fallback


def test_level3_heading_hard_latches_fallback_next_tick():
    sh = Shield()
    _, rep = sh.guard_command(ControlsState(), RuntimeState(groundspeed_kts=100.0, heading_error_deg=20.0))
    assert rep.fallback and "L3:heading_hard" in rep.rules
    # следующий такт коэффициентов — классика (identity), даже с агрессивной поправкой
    eff, safe, rep2 = sh.guard_coefficients(_corr(pid_brake_l=(1.5, 1.0, 1.0)), BASE)
    assert rep2.fallback
    assert safe.alpha["pid_brake_l"] == (1.0, 1.0, 1.0)
    assert eff["pid_brake_l"]["kp"] == pytest.approx(BASE["pid_brake_l"]["kp"])


# --------------------------------------------------------------------------- #
# Состояние / служебное
# --------------------------------------------------------------------------- #

def test_reset_clears_state():
    sh = Shield()
    sh.guard_coefficients(_corr(pid_brake_l=(1.5, 1.0, 1.0)), BASE)
    sh.guard_command(ControlsState(), RuntimeState(groundspeed_kts=100.0, heading_error_deg=20.0))
    sh.reset()
    assert sh._prev_gains is None and sh._prev_brakes is None and sh._fallback_latched is False
    # после reset rate-лимит не срабатывает на первом такте
    _, _, rep = sh.guard_coefficients(_corr(pid_brake_l=(1.5, 1.0, 1.0)), BASE)
    assert not any(r.startswith("L2:rate") for r in rep.rules)


def test_corrections_vector_roundtrip():
    c = Corrections.identity()
    c.alpha["pid_rev_l"] = (1.2, 0.9, 1.1)
    c.w_lat = 1.3
    vec = c.to_vector()
    assert len(vec) == ACTION_DIM
    back = Corrections.from_vector(vec)
    assert back.alpha == c.alpha
    assert back.w_lon == pytest.approx(c.w_lon) and back.w_lat == pytest.approx(1.3)


def test_gain_bridge_helpers_with_real_pids():
    pids = {reg: PIDController(kp=BASE[reg]["kp"], ki=BASE[reg]["ki"], kd=BASE[reg]["kd"], name=reg)
            for reg in REGULATOR_ORDER}
    bg = base_gains_from_pids(pids)
    assert bg["pid_brake_l"]["kp"] == pytest.approx(0.1)
    eff = {reg: {"kp": 9.0, "ki": 8.0, "kd": 7.0} for reg in REGULATOR_ORDER}
    apply_gains_to_pids(pids, eff)
    assert pids["pid_brake_l"].kp == 9.0 and pids["pid_rev_r"].kd == 7.0
