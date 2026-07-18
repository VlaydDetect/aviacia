"""In-process захват классических траекторий для SFT-датасета (план Stage B).

Гоняет **классический** контур внутри `RolloutEnv` (действие = коэффициенты пресета →
`env.step` воспроизводит классику) и на каждом такте сохраняет `(obs_окно, target_z)`,
где target = коэффициенты пресета этого прогона. Это единственный корректный путь: obs
включает внутреннее состояние PID (integral/deriv/last_output, traveled) — его НЕТ в сырых
DataRef'ах, поэтому obs берём из того же `ObservationBuilder`, что и на инференсе (гарантия
контракта train↔deploy).

Реальный захват — на X-Plane-бэкенде (`RolloutEnv` с `XPlaneBackend`); в тестах — на
скриптованном бэкенде. `startRECORDING` (при наличии) можно вести параллельно как сырой
аудит-архив, но для obs он не нужен.
"""

from __future__ import annotations

import numpy as np

from ismpu.envs.action import preset_action
from ismpu.agent.shield import base_gains_from_pids
from ismpu.agent.pretrain import SFTDataset, target_z_from_gains


def capture_scenario(env, scenario, max_steps: int = 2000) -> SFTDataset:
    """Один классический прогон сценария → `SFTDataset` (окна obs + постоянный target_z)."""
    obs, _ = env.reset(scenario)
    preset = base_gains_from_pids(env.controller.pids)   # коэффициенты пресета сценария
    action = preset_action(preset)                       # точная запись → классика
    tz = target_z_from_gains(preset)

    windows = [np.asarray(obs, dtype=np.float32)]
    for _ in range(max_steps):
        obs, _reward, terminated, truncated, _info = env.step(action)
        windows.append(np.asarray(obs, dtype=np.float32))
        if terminated or truncated:
            break

    obs_arr = np.stack(windows).astype(np.float32)
    tz_arr = np.repeat(tz[None, :], len(windows), axis=0).astype(np.float32)
    return SFTDataset(obs=obs_arr, target_z=tz_arr)


def capture_dataset(env, scenarios, max_steps: int = 2000, log=print) -> SFTDataset:
    """Захват набора сценариев (каждый в своих условиях) → объединённый `SFTDataset`."""
    parts = []
    for i, scenario in enumerate(scenarios):
        ds = capture_scenario(env, scenario, max_steps=max_steps)
        parts.append(ds)
        if log:
            sid = getattr(scenario, "scenario_id", f"#{i}")
            log(f"captured {sid}: {len(ds)} windows")
    return SFTDataset.concat(parts)
