"""Контракт обучаемого слоя (Этап 4): что именно сеть имеет право менять.

Аргумент ТЗ-совместимости в виде тестов, а не докстрингов: сеть — ограниченный советчик по
коэффициентам, а не регулятор. Ключевая проверка — `test_applying_an_action_moves_nothing_but_gains`:
проходит по **всем** полям контура и утверждает, что действие сети не сдвинуло ничего, кроме
`kp/ki/kd` и весов каналов. Границы выхода, anti-windup, фильтры, микс-коэффициенты и параметры
эталонной траектории структурно недостижимы для сети.
"""

import numpy as np
import pytest

from ismpu.config.regulators import (
    REGULATOR_ORDER, GAIN_KEYS, N_GAINS, ACTION_DIM,
    REGULATOR_SPECS, FORBIDDEN_DIRECT_OUTPUTS, MUTABLE_PID_FIELDS,
    LIVE_CONTROL_ARCHITECTURE, ControlArchitecture, validate_action_contract,
)
from ismpu.control.channels import ControlsState
from ismpu.control.system import ControllingSystem
from ismpu.envs.scenario import SCENARIO_PRESETS
from ismpu.envs.action import decode, apply_corrections, preset_action
from ismpu.agent.shield import base_gains_from_pids

from fakes import static_sim


# --------------------------------------------------------------------------- #
# Сам контракт
# --------------------------------------------------------------------------- #

def test_contract_validates():
    validate_action_contract()      # не должно бросать на актуальной конфигурации


def test_specs_cover_exactly_the_regulators():
    assert tuple(s.name for s in REGULATOR_SPECS) == REGULATOR_ORDER
    assert len(REGULATOR_SPECS) * len(GAIN_KEYS) == N_GAINS


def test_every_regulator_has_a_rationale_for_the_customer():
    """Пустое обоснование = контракт непредъявим по ТЗ."""
    for spec in REGULATOR_SPECS:
        assert spec.rationale.strip()
        assert spec.layer in {"lateral", "longitudinal"}
        assert spec.actuator.strip()


def test_network_never_owns_direct_actuator_authority():
    """Машиночитаемое утверждение «сеть не является регулятором»."""
    assert LIVE_CONTROL_ARCHITECTURE.direct_actuator_authority is False
    assert LIVE_CONTROL_ARCHITECTURE.learned_component_role == "advisory_gain_scheduler"
    # Классический PID стоит между обучаемым слоем и актуаторами — это порядок слоёв.
    layers = LIVE_CONTROL_ARCHITECTURE.layers
    assert layers.index("classical_pid") < layers.index("actuators")
    assert layers.index("shield") < layers.index("actuators")


def test_forbidden_outputs_are_the_actual_command_fields():
    """Список запретов должен совпадать с реальными полями команд, иначе он декоративный."""
    declared = {f for f in dir(ControlsState) if f.startswith(("cmd_", "rudder_"))}
    assert FORBIDDEN_DIRECT_OUTPUTS == declared
    assert FORBIDDEN_DIRECT_OUTPUTS.isdisjoint(REGULATOR_ORDER)


def test_contract_rejects_direct_actuator_authority():
    architecture = ControlArchitecture(direct_actuator_authority=True)
    import ismpu.config.regulators as reg
    original = reg.LIVE_CONTROL_ARCHITECTURE
    reg.LIVE_CONTROL_ARCHITECTURE = architecture
    try:
        with pytest.raises(ValueError, match="direct_actuator_authority"):
            validate_action_contract()
    finally:
        reg.LIVE_CONTROL_ARCHITECTURE = original


def test_contract_rejects_a_regulator_without_a_spec():
    """Добавили регулятор, но не описали его — обучение должно упасть на старте."""
    import ismpu.config.regulators as reg
    original = reg.REGULATOR_SPECS
    reg.REGULATOR_SPECS = original[:-1]
    try:
        with pytest.raises(ValueError, match="REGULATOR_SPECS"):
            validate_action_contract()
    finally:
        reg.REGULATOR_SPECS = original


def test_contract_rejects_an_empty_rationale():
    import ismpu.config.regulators as reg
    from dataclasses import replace
    original = reg.REGULATOR_SPECS
    reg.REGULATOR_SPECS = (replace(original[0], rationale="  "),) + original[1:]
    try:
        with pytest.raises(ValueError, match="обоснование"):
            validate_action_contract()
    finally:
        reg.REGULATOR_SPECS = original


# --------------------------------------------------------------------------- #
# Главная проверка: действие сети не двигает ничего, кроме коэффициентов
# --------------------------------------------------------------------------- #

_PID_FIELDS = ("kp", "ki", "kd", "min_out", "max_out",
               "anti_windup", "integral_decay", "der_filter_tf", "name")


def _controller(preset="nws_fail"):
    ctrl = ControllingSystem(static_sim()[0])
    SCENARIO_PRESETS[preset].apply_control(ctrl)
    return ctrl


def _snapshot(ctrl) -> dict:
    """Полный слепок настраиваемого состояния контура — всё, что действие могло бы сдвинуть."""
    snap = {}
    for name in REGULATOR_ORDER:
        pid = ctrl.pids[name]
        for field in _PID_FIELDS:
            snap[f"pids.{name}.{field}"] = getattr(pid, field)

    lat, lon = ctrl.lateral_channel, ctrl.longitudinal_channel
    snap["lateral.steering_brake_gain"] = lat.steering_brake_gain
    snap["lateral.steering_rev_gain"] = lat.steering_rev_gain
    snap["lateral.w_lat"] = lat.w_lat
    snap["longitudinal.w_lon"] = lon.w_lon
    for field in ("v_target_ms", "v_touchdown_ms", "landing_distance_m", "mode"):
        if hasattr(lon.trajectory, field):
            snap[f"trajectory.{field}"] = getattr(lon.trajectory, field)
    return snap


def test_applying_an_action_moves_nothing_but_gains():
    """Действие сети меняет только kp/ki/kd и веса каналов — всё остальное неприкосновенно.

    Это структурное свойство `apply_gains_to_pids`, и именно оно защищает пределы выхода,
    anti-windup, фильтры и коэффициенты дифференциального микса: они принадлежат пресету
    (контуру безопасности), а не обучаемому слою.
    """
    ctrl = _controller()
    preset = base_gains_from_pids(ctrl.pids)
    before = _snapshot(ctrl)

    # Заведомо НЕ пресетное действие: все коэффициенты сдвинуты, веса не единичные.
    rng = np.random.default_rng(0)
    action = preset_action(preset)
    action[:N_GAINS] *= rng.uniform(0.5, 1.5, size=N_GAINS)
    action[N_GAINS:] = [0.7, 1.3]
    apply_corrections(decode(action), preset, ctrl, shield=None)

    after = _snapshot(ctrl)
    changed = {k for k in before if before[k] != after[k]}
    allowed = ({f"pids.{r}.{g}" for r in REGULATOR_ORDER for g in MUTABLE_PID_FIELDS}
               | {"lateral.w_lat", "longitudinal.w_lon"})

    assert changed <= allowed, f"действие сдвинуло запрещённые поля: {sorted(changed - allowed)}"
    assert changed, "действие не изменило вообще ничего — тест бы ничего не доказывал"
    # Веса каналов действительно применились.
    assert after["longitudinal.w_lon"] == pytest.approx(0.7)
    assert after["lateral.w_lat"] == pytest.approx(1.3)


def test_preset_action_is_a_complete_no_op():
    """Действие = коэффициенты пресета → не сдвигается ни одно поле контура (аналог identity)."""
    ctrl = _controller()
    preset = base_gains_from_pids(ctrl.pids)
    before = _snapshot(ctrl)

    apply_corrections(decode(preset_action(preset)), preset, ctrl, shield=None)

    after = _snapshot(ctrl)
    assert after == before


def test_output_bounds_survive_an_out_of_range_action():
    """Даже гротескное действие не может расширить пределы выхода регулятора.

    Границы `[min_out, max_out]` — контур безопасности: именно они не дают выдать реверс
    там, где допустим только тормоз. Сеть до них не дотягивается по построению.
    """
    ctrl = _controller()
    preset = base_gains_from_pids(ctrl.pids)
    bounds_before = {r: (ctrl.pids[r].min_out, ctrl.pids[r].max_out) for r in REGULATOR_ORDER}

    action = preset_action(preset)
    action[:N_GAINS] = 1e6          # абсурдные коэффициенты
    action[N_GAINS:] = [1e3, 1e3]
    apply_corrections(decode(action), preset, ctrl, shield=None)

    assert {r: (ctrl.pids[r].min_out, ctrl.pids[r].max_out)
            for r in REGULATOR_ORDER} == bounds_before


def test_action_dim_matches_the_declared_contract():
    ctrl = _controller()
    action = preset_action(base_gains_from_pids(ctrl.pids))
    assert action.shape == (ACTION_DIM,)
    assert ACTION_DIM == N_GAINS + 2
