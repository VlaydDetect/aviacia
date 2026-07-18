"""Канонический порядок регуляторов и размерности действия — нейтральный низкоуровневый
модуль, чтобы `shield` и `gain_space` могли ссылаться на него без циклического импорта.

`REGULATOR_ORDER` = ключи словаря `pids` в `ControllingSystem` (см. `system.setup`/`clamp_all`).
Действие NPGS = `[gains×15, w_lon, w_lat]` (15 = 5 регуляторов × (kp, ki, kd)); совпадает с
порядком слотов gain-пространства (`agent.gain_space`).
"""

REGULATOR_ORDER = ("runway_center_pid", "pid_brake_l", "pid_brake_r", "pid_rev_l", "pid_rev_r")
GAIN_KEYS = ("kp", "ki", "kd")
N_GAINS = len(REGULATOR_ORDER) * len(GAIN_KEYS)   # 15
ACTION_DIM = N_GAINS + 2                            # 17 (+ w_lon, w_lat)
