"""Канонический порядок регуляторов, размерности действия и **контракт обучаемого слоя**.

Нейтральный низкоуровневый модуль, чтобы `shield` и `gain_space` могли ссылаться на него без
циклического импорта.

`REGULATOR_ORDER` = ключи словаря `pids` в `ControllingSystem` (см. `system.setup`/`clamp_all`).
Действие NPGS = `[gains×15, w_lon, w_lat]` (15 = 5 регуляторов × (kp, ki, kd)); совпадает с
порядком слотов gain-пространства (`agent.gain_space`).

## Контракт обучаемого слоя (аргумент ТЗ-совместимости)

Заимствовано из `roman_repo/xp_pid_bridge/adaptive_gain_contract.py`. У нас граница «что сеть
имеет право менять» и раньше соблюдалась (`apply_gains_to_pids` пишет только `kp/ki/kd`), но
жила в докстрингах. Здесь она становится **машиночитаемой и проверяемой**:

* `REGULATOR_SPECS` — по каждому регулятору: слой контура, актуатор и **обоснование**, зачем
  сети дан доступ именно к нему. Это то, что предъявляется заказчику по ТЗ.
* `FORBIDDEN_DIRECT_OUTPUTS` — имена прямых команд актуаторов. Сеть не выдаёт их никогда:
  её выход — только коэффициенты, команды считает классический `PIDController`.
* `LIVE_CONTROL_ARCHITECTURE` — утверждение «сеть не является регулятором» в виде данных,
  а не прозы: `direct_actuator_authority = False`, роль — ограниченный советчик.

`validate_action_contract()` вызывается на старте обучения (`train.py`, `pretrain.py`): нарушение
контракта должно ронять запуск **до** того, как потрачен прогон, а не всплывать на инференсе.
"""

from dataclasses import dataclass, asdict

REGULATOR_ORDER = ("runway_center_pid", "pid_brake_l", "pid_brake_r", "pid_rev_l", "pid_rev_r")
GAIN_KEYS = ("kp", "ki", "kd")
N_GAINS = len(REGULATOR_ORDER) * len(GAIN_KEYS)   # 15
ACTION_DIM = N_GAINS + 2                            # 17 (+ w_lon, w_lat)


# --------------------------------------------------------------------------- #
# Что именно обучаемый слой имеет право настраивать
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class RegulatorSpec:
    """Один регулятор, коэффициенты которого (kp/ki/kd) разрешено настраивать сети."""
    name: str
    layer: str
    actuator: str
    rationale: str


REGULATOR_SPECS: tuple[RegulatorSpec, ...] = (
    RegulatorSpec(
        "runway_center_pid", "lateral", "руль направления + дифференциальный микс",
        "Ошибка курса → команда руля; от неё же берутся дифференциальное торможение и "
        "асимметричная тяга. Авторитет канала скачкообразно меняется при отказе NWS "
        "(руль мёртв, ось держится тормозами), поэтому фиксированная настройка не покрывает "
        "оба режима.",
    ),
    RegulatorSpec(
        "pid_brake_l", "longitudinal", "левый гидравлический тормоз",
        "Следование эталонной кривой скорости. Эффективность тормоза зависит от сцепления "
        "(μ по ВПП, дождь, лёд), которое пресет заранее не знает.",
    ),
    RegulatorSpec(
        "pid_brake_r", "longitudinal", "правый гидравлический тормоз",
        "То же, что левый. Раздельная настройка нужна при асимметричных отказах: "
        "симметрия — априорная гипотеза, а не ограничение.",
    ),
    RegulatorSpec(
        "pid_rev_l", "longitudinal", "левый реверс тяги",
        "Основное торможение на высокой скорости. При отказе противоположного реверса "
        "требуется перераспределение усилия между каналами.",
    ),
    RegulatorSpec(
        "pid_rev_r", "longitudinal", "правый реверс тяги",
        "То же, что левый.",
    ),
)

FORBIDDEN_DIRECT_OUTPUTS = frozenset({
    # пробег
    "cmd_brake_l", "cmd_brake_r", "cmd_rev_l", "cmd_rev_r", "rudder_cmd",
    # воздушный участок (заход и выравнивание)
    "cmd_elevator", "cmd_aileron",
    "cmd_throttle_l_rate", "cmd_throttle_r_rate", "cmd_throttle_norm",
})
"""Прямые команды актуаторов (поля `ControlsState`). Сеть не выдаёт их ни при каких условиях:
её выход — коэффициенты PID, команды считает классический контур. Это буквальное требование
ТЗ («передаточная функция PID в сеть не встраивается»).

Список покрывает **весь** полёт, а не только пробег: воздушными коэффициентами сеть пока не
управляет вовсе (там статические пресеты, `config/approach.py`), но запрет на прямую выдачу
руля высоты и элеронов от этого не становится менее обязательным — он должен действовать
раньше, чем появится соблазн."""

MUTABLE_PID_FIELDS = frozenset(GAIN_KEYS)
"""Единственные поля `PIDController`, которые разрешено записывать по действию сети. Границы
выхода (`min_out`/`max_out`), anti-windup, утечка интегратора и фильтр производной остаются
за пресетом — они и есть контур безопасности."""


@dataclass(frozen=True)
class ControlArchitecture:
    """Фиксированный порядок слоёв и роль обучаемого компонента."""
    layers: tuple = ("telemetry", "guidance", "classical_pid", "shield", "actuators")
    learned_component_role: str = "advisory_gain_scheduler"
    direct_actuator_authority: bool = False

    def as_dict(self) -> dict:
        return asdict(self)


LIVE_CONTROL_ARCHITECTURE = ControlArchitecture()


def validate_action_contract() -> None:
    """Проверяет контракт обучаемого слоя. Нарушение → `ValueError` на старте обучения.

    Ловит рассинхронизацию, которая иначе всплыла бы только на инференсе: добавили регулятор,
    но не описали его; изменили ACTION_DIM, но не порядок; протащили в обучаемые выходы имя
    прямой команды актуатора.
    """
    spec_names = tuple(s.name for s in REGULATOR_SPECS)
    if spec_names != REGULATOR_ORDER:
        raise ValueError(
            f"REGULATOR_SPECS не совпадает с REGULATOR_ORDER: {spec_names} != {REGULATOR_ORDER}")

    if len(set(spec_names)) != len(spec_names):
        raise ValueError(f"дублирующиеся регуляторы в REGULATOR_SPECS: {spec_names}")

    forbidden = set(spec_names) & FORBIDDEN_DIRECT_OUTPUTS
    if forbidden:
        raise ValueError(
            f"обучаемый выход совпал с прямой командой актуатора: {sorted(forbidden)}")

    if ACTION_DIM != N_GAINS + 2:
        raise ValueError(f"ACTION_DIM ({ACTION_DIM}) != N_GAINS + 2 ({N_GAINS + 2})")

    if LIVE_CONTROL_ARCHITECTURE.direct_actuator_authority:
        raise ValueError(
            "direct_actuator_authority=True: сеть получила бы прямое управление актуаторами, "
            "что запрещено ТЗ")

    for spec in REGULATOR_SPECS:
        if not spec.rationale.strip():
            raise ValueError(f"{spec.name}: пустое обоснование — контракт непредъявим по ТЗ")
