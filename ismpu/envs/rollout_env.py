"""RolloutEnv — Gymnasium-совместимая среда поверх SimInterface + классического контура.

Оборачивает `SimInterface` (сброс/телеметрия/погода/отказы) и `ControllingSystem`
(классический PID-контур). Действие актора — мультипликативные поправки (§6): на
каждом такте они применяются к коэффициентам PID и весам каналов, затем контур
считает команду, (опц.) её проверяет Shield, команда уходит в симулятор, а из новой
телеметрии собирается наблюдение (§5) и покомпонентный reward (§11).

**Инвариант identity (§1):** `env.step(IDENTITY_ACTION)` при `shield=None` даёт ровно
те же команды, что классический `control_step` — проверяется тестом.

Gymnasium импортируется опционально: если пакет есть — пространства это `gym.spaces.Box`,
иначе — лёгкий `_SimpleBox` (среда всё равно работает и тестируется без gymnasium).
API совместим: `reset(scenario) -> (obs, info)`, `step(action) -> (obs, reward,
terminated, truncated, info)`.

Замечание о транспорте: команды отправляются через `SimInterface.step`, но контур
читает телеметрию из `xpc.current_dref_values` — поэтому для обучения `sim` и
`controller` должны делить один коннектор (X-Plane). Это тренировочный путь; поставка
(Этап 6) — отдельный детерминированный рантайм.
"""

from collections import deque
from dataclasses import dataclass

import numpy as np

from ismpu.config.constants import DT
from ismpu.utils.converts import Converts
from ismpu.control.channels import ControlsState
from ismpu.control.system import ControllingSystem
from ismpu.envs.sim_interface import SimInterface
from ismpu.envs.scenario import Scenario
from ismpu.envs.observation import ObservationBuilder, OBS_DIM, ObserverEstimate
from ismpu.envs.action import decode, apply_corrections, ACTION_LOW, ACTION_HIGH
from ismpu.envs.reward import compute_reward, RewardWeights
from ismpu.agent.shield import RuntimeState, base_gains_from_pids

try:  # gymnasium опционален
    from gymnasium import spaces as _gym_spaces
except Exception:  # pragma: no cover
    _gym_spaces = None

OFF_RUNWAY_XTE_M = 30.0     # выход за пределы ВПП → аварийное завершение эпизода
INVALID_TELEMETRY_PENALTY = 10.0


@dataclass
class _SimpleBox:
    """Минимальная замена gym.spaces.Box, когда gymnasium не установлен."""
    low: np.ndarray
    high: np.ndarray
    shape: tuple


def _make_box(low, high):
    low = np.asarray(low, dtype=np.float32)
    high = np.asarray(high, dtype=np.float32)
    if _gym_spaces is not None:
        return _gym_spaces.Box(low=low, high=high, dtype=np.float32)
    return _SimpleBox(low=low, high=high, shape=low.shape)


def _snapshot_command(state: ControlsState) -> ControlsState:
    snap = ControlsState()
    snap.cmd_brake_l = state.cmd_brake_l
    snap.cmd_brake_r = state.cmd_brake_r
    snap.cmd_rev_l = state.cmd_rev_l
    snap.cmd_rev_r = state.cmd_rev_r
    snap.rudder_cmd = state.rudder_cmd
    return snap


class RolloutEnv:
    def __init__(self, sim: SimInterface, controller: ControllingSystem, *,
                 dt: float = DT, history_len: int = 1, shield=None,
                 obs_builder: ObservationBuilder | None = None,
                 reward_weights: RewardWeights | None = None, max_steps: int = 4000):
        self.sim = sim
        self.controller = controller
        self.dt = dt
        self.history_len = history_len
        self.shield = shield
        self.obs_builder = obs_builder or ObservationBuilder()
        self.reward_weights = reward_weights or RewardWeights()
        self.max_steps = max_steps

        self._history: deque = deque(maxlen=history_len)
        self._base_gains: dict | None = None
        self._scenario: Scenario | None = None
        self._prev_command: ControlsState | None = None
        self._steps = 0

        # Наблюдение — окно истории как ПОСЛЕДОВАТЕЛЬНОСТЬ (T, 56) (вход NPGS, §10/Этап 4),
        # а не плоский вектор: сеть обрабатывает временную ось (GRU/attention).
        self.observation_space = _make_box(np.full((history_len, OBS_DIM), -1.0),
                                           np.full((history_len, OBS_DIM), 1.0))
        self.action_space = _make_box(ACTION_LOW, ACTION_HIGH)

    # --- Gymnasium API ---

    def reset(self, scenario: Scenario, *, seed=None):
        self._scenario = scenario
        telemetry = self.sim.reset(scenario)          # телепорт + погода + отказы (среда)
        scenario.apply_control(self.controller)        # базовые PID + активация отказа пресета
        self._base_gains = base_gains_from_pids(self.controller.pids)
        if self.shield is not None:
            self.shield.reset()
        self.controller.set_channel_weights(1.0, 1.0)
        self._steps = 0
        self._prev_command = None

        obs = self._observe(telemetry)
        self._history.clear()
        for _ in range(self.history_len):
            self._history.append(obs)
        return self._stacked(), {}

    def step(self, action):
        # 1) Поправки актора → коэффициенты PID + веса каналов (опц. через Shield).
        corrections = decode(action)
        apply_corrections(corrections, self._base_gains, self.controller, shield=self.shield)

        # 2) Состояние для поведенческих проверок Shield (по текущей телеметрии).
        pre = self.sim.read_telemetry()
        runtime = self._runtime_state(pre)

        # 3) Расчёт команды контуром без отправки.
        break_control = self.controller.control_step(self.dt, send=False)
        command = self.controller.state
        shield_report = None
        if self.shield is not None and not break_control:
            command, shield_report = self.shield.guard_command(command, runtime)

        # 4) Отправка команды и получение новой телеметрии.
        post = self.sim.step(command)
        self.sim.update(self.controller.longitudinal_channel.traveled_distance_m)

        # 5) Наблюдение + reward.
        obs = self._observe(post)
        self._history.append(obs)
        reward, components, guidance = self._reward(post, command, shield_report)

        # 6) Завершение.
        off_runway = guidance is not None and abs(guidance["xte"]) > OFF_RUNWAY_XTE_M
        terminated = bool(break_control or off_runway or not post.valid)
        self._steps += 1
        truncated = self._steps >= self.max_steps

        self._prev_command = _snapshot_command(command)
        info = {"reward_components": components, "shield": shield_report,
                "break_control": break_control, "off_runway": off_runway}
        return self._stacked(), reward, terminated, truncated, info

    def close(self):
        self.sim.close()

    # --- внутреннее ---

    def _observe(self, telemetry) -> np.ndarray:
        return self.obs_builder.build(telemetry, self.controller, self._base_gains,
                                      self._scenario.weather, ObserverEstimate())

    def _stacked(self) -> np.ndarray:
        """Окно истории → тензор `(history_len, OBS_DIM)` (последовательность кадров для NPGS)."""
        return np.stack(list(self._history)).astype(np.float32)

    def _runtime_state(self, telemetry) -> RuntimeState:
        gs_kts = (telemetry.groundspeed_ms or 0.0) * Converts.MS_TO_KTS
        heading_err = 0.0
        if telemetry.valid and None not in (telemetry.lat, telemetry.lon, telemetry.heading_true_deg):
            g = self.controller.lateral_channel.tracker.guidance(
                telemetry.lat, telemetry.lon, telemetry.heading_true_deg, telemetry.groundspeed_ms)
            heading_err = g["heading_error_deg"]
        return RuntimeState(groundspeed_kts=gs_kts, heading_error_deg=heading_err)

    def _reward(self, telemetry, command, shield_report):
        if not telemetry.valid or None in (telemetry.lat, telemetry.lon,
                                           telemetry.heading_true_deg, telemetry.groundspeed_ms):
            comp = compute_reward(xte_m=0.0, heading_error_deg=0.0, speed_error_ms=0.0,
                                  command=command, prev_command=self._prev_command,
                                  weights=self.reward_weights)
            return -INVALID_TELEMETRY_PENALTY, comp, None

        g = self.controller.lateral_channel.tracker.guidance(
            telemetry.lat, telemetry.lon, telemetry.heading_true_deg, telemetry.groundspeed_ms)
        ref = self.controller.longitudinal_channel.trajectory.get_reference_speed(
            self.controller.longitudinal_channel.traveled_distance_m)
        comp = compute_reward(
            xte_m=g["xte"], heading_error_deg=g["heading_error_deg"],
            speed_error_ms=telemetry.groundspeed_ms - ref,
            command=command, prev_command=self._prev_command,
            roll_deg=telemetry.roll_deg or 0.0, yaw_rate=telemetry.r_rad or 0.0,
            shield_l_shield=(shield_report.l_shield if shield_report else 0.0),
            weights=self.reward_weights)
        return comp.total, comp, g
