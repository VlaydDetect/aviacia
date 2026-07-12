"""Покомпонентный reward (§11, разд. V описания).

Отдельно штрафуются: боковое отклонение, ошибка скорости, рывки управления,
активация Shield, срыв по курсу, нестабильность. Пороги — из `config/requirements.py`
(единый источник истины с приёмочными гейтами). Reward = − Σ (вес · компонента);
чистая функция, тестируется без среды. Веса — предмет калибровки на Этапе 4.
"""

from dataclasses import dataclass, asdict

from ismpu.config.requirements import XTE_ROLLOUT_MAX_M, HEADING_FAULT_MAX_DEG
from ismpu.agent.normalization import SPEED_ERR_SCALE


@dataclass(frozen=True)
class RewardWeights:
    xte: float = 1.0
    speed: float = 0.3
    jerk: float = 0.2
    shield: float = 0.5
    heading: float = 0.5
    instability: float = 0.2


@dataclass
class RewardComponents:
    xte: float
    speed: float
    jerk: float
    shield: float
    heading: float
    instability: float
    total: float

    def as_dict(self) -> dict:
        return asdict(self)


def _command_jerk(command, prev_command) -> float:
    if prev_command is None:
        return 0.0
    return (abs(command.cmd_brake_l - prev_command.cmd_brake_l)
            + abs(command.cmd_brake_r - prev_command.cmd_brake_r)
            + abs(command.cmd_rev_l - prev_command.cmd_rev_l)
            + abs(command.cmd_rev_r - prev_command.cmd_rev_r)
            + abs(command.rudder_cmd - prev_command.rudder_cmd))


def compute_reward(*, xte_m: float, heading_error_deg: float, speed_error_ms: float,
                   command, prev_command=None, roll_deg: float = 0.0, yaw_rate: float = 0.0,
                   shield_l_shield: float = 0.0, weights: RewardWeights | None = None) -> RewardComponents:
    """Считает компоненты и суммарный reward. Все компоненты ≥ 0; reward = −Σ вес·компонента."""
    w = weights or RewardWeights()

    xte = abs(xte_m) / XTE_ROLLOUT_MAX_M               # >1 = вне ±3 м (гейт ТЗ 5.1.3.1)
    heading = abs(heading_error_deg) / HEADING_FAULT_MAX_DEG  # >1 = вне ±5° (ТЗ 5.1.3.3)
    speed = abs(speed_error_ms) / SPEED_ERR_SCALE
    jerk = _command_jerk(command, prev_command)
    shield = shield_l_shield
    instability = abs(roll_deg) / 45.0 + abs(yaw_rate)

    total = -(w.xte * xte + w.speed * speed + w.jerk * jerk
              + w.shield * shield + w.heading * heading + w.instability * instability)
    return RewardComponents(xte=xte, speed=speed, jerk=jerk, shield=shield,
                            heading=heading, instability=instability, total=total)
