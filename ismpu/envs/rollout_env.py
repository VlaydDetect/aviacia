"""RolloutEnv — Gymnasium-совместимая среда поверх SimInterface + классического контура.

Оборачивает `SimInterface` (сброс/телеметрия/погода/отказы) и `ControllingSystem`
(классический PID-контур). Действие актора — **абсолютные коэффициенты PID** (+ веса
каналов): на каждом такте они записываются в регуляторы, затем контур считает команду,
(опц.) её проверяет Shield (пресет — якорь), команда уходит в симулятор, а из новой
телеметрии собирается наблюдение (§5) и покомпонентный reward (§11).

**Парити классики (§1):** `env.step(preset_action(preset))` при `shield=None` даёт ровно
те же команды, что классический `control_step` со связанным пресетом — проверяется тестом.

Gymnasium импортируется опционально: если пакет есть — пространства это `gym.spaces.Box`,
иначе — лёгкий `_SimpleBox` (среда всё равно работает и тестируется без gymnasium).
API совместим: `reset(scenario) -> (obs, info)`, `step(action) -> (obs, reward,
terminated, truncated, info)`.

Замечание о транспорте: и телеметрия, и команды идут через `SimInterface` — среда читает кадр
`sim.read_telemetry()` и передаёт его в `control_step` параметром. Контур не знает, против чего
он работает, поэтому общий коннектор `sim` и `controller` больше не требуется: тот же код
исполняется и на X-Plane, и на стенде заказчика.
"""

from collections import deque
from dataclasses import dataclass

import numpy as np

from ismpu.config.constants import DT
from ismpu.config.runway import RWY_HEADING_TRUE
from ismpu.utils.converts import Converts
from ismpu.control.channels import ControlsState
from ismpu.control.runway_tracker import RunwayTracker
from ismpu.control.system import ControllingSystem
from ismpu.envs.sim_interface import SimInterface
from ismpu.envs.scenario import Scenario
from ismpu.envs.observation import ObservationBuilder, OBS_DIM, ObserverEstimate
from ismpu.envs.action import decode, apply_corrections, ACTION_LOW, ACTION_HIGH
from ismpu.envs.reward import (
    compute_reward, RewardWeights, EpisodeObjective, saturation_fraction,
)
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


def heading_deviation_deg(telemetry) -> float:
    """Отклонение курса ВС от направления ВПП — приёмочная величина ТЗ 5.1.3.3 / 5.1.2.4.

    ТЗ формулирует требование как «удержание курса в пределах ±5° **от направления ВПП**», то есть
    нормируется состояние ВС, а не команда. `RunwayTracker.guidance()["heading_error_deg"]` для
    этого не годится: там пеленг на точку упреждения минус курс плюс Stanley-коррекция по сносу,
    то есть **ошибка команды руления**. При смещении 5 м от оси и идеально выдержанном курсе она
    показывает −6.35° и объявила бы провал гейта ±5°, хотя отклонение курса ровно нулевое.

    Курс ВПП берётся из телеметрии, если бэкенд его сообщает (стенд заказчика), иначе — из
    конфигурации (X-Plane, где ВПП фиксирована).
    """
    runway_heading = getattr(telemetry, "runway_heading_deg", None)
    if runway_heading is None:
        runway_heading = RWY_HEADING_TRUE
    return RunwayTracker.wrap_deg(telemetry.heading_true_deg - runway_heading)


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
        self._preset_gains: dict | None = None   # пресет сценария — якорь Shield (не база obs)
        self._scenario: Scenario | None = None
        self._prev_command: ControlsState | None = None
        self._steps = 0
        # Эпизодный objective: то же определение «хорошего пробега», что и у потактового
        # reward, но сводное — идёт в приёмку, отбор чекпоинтов и вес SFT-меток.
        self.objective = EpisodeObjective()

        # Наблюдение — окно истории как ПОСЛЕДОВАТЕЛЬНОСТЬ (T, 56) (вход NPGS, §10/Этап 4),
        # а не плоский вектор: сеть обрабатывает временную ось (GRU/attention).
        self.observation_space = _make_box(np.full((history_len, OBS_DIM), -1.0),
                                           np.full((history_len, OBS_DIM), 1.0))
        self.action_space = _make_box(ACTION_LOW, ACTION_HIGH)

    # --- Gymnasium API ---

    def reset(self, scenario: Scenario, *, seed=None):
        self._scenario = scenario
        telemetry = self.sim.reset(scenario)          # телепорт + погода + отказы (среда)
        scenario.apply_control(self.controller)        # seed PID пресета + активация отказа
        self._preset_gains = base_gains_from_pids(self.controller.pids)  # пресет-якорь Shield
        if self.shield is not None:
            self.shield.reset()
        self.controller.set_channel_weights(1.0, 1.0)
        self._steps = 0
        self._prev_command = None
        self.objective = EpisodeObjective(weights=self.objective.weights)

        obs = self._observe(telemetry)
        self._history.clear()
        for _ in range(self.history_len):
            self._history.append(obs)
        return self._stacked(), {}

    def step(self, action):
        # 1) Абсолютные коэффициенты актора → PID + веса каналов (опц. через Shield, якорь — пресет).
        command = decode(action)
        apply_corrections(command, self._preset_gains, self.controller, shield=self.shield)

        # 2) Состояние для поведенческих проверок Shield (по текущей телеметрии).
        pre = self.sim.read_telemetry()
        runtime = self._runtime_state(pre)

        # 3) Расчёт команды контуром по прочитанному кадру, без отправки.
        break_control = self.controller.control_step(self.dt, pre, send=False)
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
        if terminated or truncated:
            # Сводка эпизода — для приёмки (runtime/evaluate.py), веса SFT-меток и отбора
            # чекпоинтов. Считается из тех же отсчётов, что и потактовый reward.
            info["objective"] = self.objective.summary()
        return self._stacked(), reward, terminated, truncated, info

    def close(self):
        self.sim.close()

    # --- внутреннее ---

    def _observe(self, telemetry) -> np.ndarray:
        return self.obs_builder.build(telemetry, self.controller,
                                      self._scenario.weather, ObserverEstimate())

    def _stacked(self) -> np.ndarray:
        """Окно истории → тензор `(history_len, OBS_DIM)` (последовательность кадров для NPGS)."""
        return np.stack(list(self._history)).astype(np.float32)

    def _runtime_state(self, telemetry) -> RuntimeState:
        """Состояние для поведенческих проверок Shield.

        Курс здесь — отклонение от направления ВПП, а не ошибка команды: Shield ловит **срыв по
        курсу**, то есть расхождение состояния, и на ошибке команды он срабатывал бы просто от
        бокового смещения при идеально выдержанном курсе.
        """
        gs_kts = (telemetry.groundspeed_ms or 0.0) * Converts.MS_TO_KTS
        heading_dev = 0.0
        if telemetry.valid and telemetry.heading_true_deg is not None:
            heading_dev = heading_deviation_deg(telemetry)
        return RuntimeState(groundspeed_kts=gs_kts, heading_error_deg=heading_dev)

    def _reward(self, telemetry, command, shield_report):
        if not telemetry.valid or None in (telemetry.lat, telemetry.lon,
                                           telemetry.heading_true_deg, telemetry.groundspeed_ms):
            comp = compute_reward(xte_m=0.0, heading_error_deg=0.0, speed_error_ms=0.0,
                                  command=command, prev_command=self._prev_command,
                                  weights=self.reward_weights)
            return -INVALID_TELEMETRY_PENALTY, comp, None

        g = self.controller.lateral_channel.tracker.guidance(
            telemetry.lat, telemetry.lon, telemetry.heading_true_deg, telemetry.groundspeed_ms)
        lon_channel = self.controller.longitudinal_channel
        ref = lon_channel.trajectory.get_reference_speed(lon_channel.traveled_distance_m)
        speed_error_ms = telemetry.groundspeed_ms - ref
        gs_kts = telemetry.groundspeed_ms * Converts.MS_TO_KTS
        # Насыщение — доля команд, упёршихся в границу своего PID: регулятор исчерпал
        # авторитет, дальнейшая ошибка ничем не парируется.
        saturation = saturation_fraction(command, self.controller.pids)
        roll_deg = telemetry.roll_deg or 0.0
        yaw_rate = telemetry.r_rad or 0.0
        heading_dev = heading_deviation_deg(telemetry)

        comp = compute_reward(
            xte_m=g["xte"], heading_error_deg=heading_dev,
            speed_error_ms=speed_error_ms,
            command=command, prev_command=self._prev_command,
            roll_deg=roll_deg, yaw_rate=yaw_rate,
            shield_l_shield=(shield_report.l_shield if shield_report else 0.0),
            groundspeed_kts=gs_kts, saturation=saturation,
            weights=self.reward_weights)

        self.objective.add(
            xte_m=g["xte"], heading_error_deg=heading_dev,
            speed_error_ms=speed_error_ms, groundspeed_kts=gs_kts,
            command=command, saturation=saturation,
            roll_deg=roll_deg, yaw_rate=yaw_rate,
            traveled_distance_m=lon_channel.traveled_distance_m,
            shield_report=shield_report)
        # `heading_error_deg` из guidance — ошибка КОМАНДЫ руления, полезная для диагностики
        # контура, но не приёмочная величина; кладём её рядом, не подменяя ею отклонение курса.
        guidance = dict(g)
        guidance["heading_deviation_deg"] = heading_dev
        return comp.total, comp, guidance
