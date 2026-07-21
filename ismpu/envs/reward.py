"""Objective — единое определение «хорошего пробега» (§11 + приёмка ТЗ разд. 5).

Форма заимствована из `roman_repo/scripts/neural_pid_objective.py` и адаптирована под
пробег (у него — заход до порога ВПП). Что взято и почему:

* **Гейт вместо линейной нормировки.** Раньше `xte = |xte| / 3 м` штрафовал даже полностью
  соответствующее ТЗ поведение, и градиент тянул к нулю там, где требование уже выполнено.
  Теперь порог ТЗ — точка излома: внутри допуска штраф растёт мягко, за порогом — резко.
  (У Романа чистый hinge `max(|x|−limit, 0)/limit`; для PPO чистый hinge даёт **нулевой
  градиент внутри допуска** — сети безразлично, держит она 0.1 м или 2.9 м. Поэтому здесь
  внутри полосы оставлен слабый линейный наклон `SHAPING_SLOPE`, а за порогом наклон в
  ~1/SHAPING_SLOPE раз круче. Это сохраняет и смысл гейта, и плотный сигнал обучения.)
* **Saturation ratio** — доля тактов, где команда упёрлась в границу PID. Тормоза зажаты в
  `[0,1]`, реверсы в `[-1,0]`; на пробеге насыщение почти постоянно, и это означает потерю
  управляемости, которую прежний reward не видел вообще.
* **Асимметрия по скорости** — перелёт по скорости к концу ВПП катастрофичен, недолёт просто
  медленный. Одной симметричной `|speed_error|` это не выражается.
* **p95 темпа команд** (эпизодный уровень) вместо только мгновенного рывка: один выброс не
  ловится суммой модулей за такт, а устойчивая дрожь в ней размазывается.

Два уровня, **одно** определение (у Романа это же свойство: objective общий для reward,
приёмки и отбора кандидатов):

* `compute_reward(...)` — потактовый reward для PPO (чистая функция, тестируется без среды);
* `EpisodeObjective` — накопитель по эпизоду → компоненты `{raw, weight, weighted}` для
  приёмки (`runtime/evaluate.py`), взвешивания качества SFT-меток и отбора чекпоинтов.

Пороги — из `config/requirements.py` (единый источник истины с приёмочными гейтами).
Reward = − Σ (вес · компонента); все компоненты ≥ 0.
"""

from dataclasses import dataclass, field, asdict

from ismpu.config.requirements import (
    XTE_ROLLOUT_MAX_M, XTE_TAXI_MAX_M, HEADING_FAULT_MAX_DEG, HEADING_HOLD_UNTIL_KTS,
)
from ismpu.agent.normalization import SPEED_ERR_SCALE

# --- Параметры формы (не из ТЗ — предмет калибровки на Этапе 4) --------------- #

SHAPING_SLOPE = 0.15
"""Наклон штрафа ВНУТРИ допуска ТЗ. 0 = чистый hinge (как у Романа) — корректно для офлайн-
отбора, но лишает PPO градиента внутри полосы. За порогом наклон = 1.0, т.е. в ~6.7 раза круче."""

TAXI_PHASE_KTS = HEADING_HOLD_UNTIL_KTS
"""Ниже этой путевой скорости считаем фазу рулением → действует более жёсткий допуск ±1 м
(ТЗ 5.1.3.1). Совпадает с порогом удержания курса (5.1.3.3) — граница фазы одна."""

SPEED_TOL_MS = 5.0          # мёртвая зона по ошибке следования эталонной кривой скорости
OVERSPEED_FACTOR = 3.0      # во столько раз перелёт по скорости дороже недолёта
ROLL_SCALE_DEG = 45.0       # масштаб крена в компоненте нестабильности


# --- Элементарные формы штрафа ----------------------------------------------- #

def excess(value: float, limit: float) -> float:
    """Чистый hinge: превышение допуска, нормированное на допуск. Внутри допуска = 0."""
    if limit <= 0.0:
        return 0.0
    return max(abs(value) - limit, 0.0) / limit


def graded(value: float, limit: float, slope: float = SHAPING_SLOPE) -> float:
    """Штраф с гейтом ТЗ: мягкий линейный наклон внутри допуска + резкий рост за порогом.

    `value == 0` → 0; `|value| == limit` → `slope`; дальше растёт с наклоном 1.0 на единицу
    допуска. Именно излом в точке `limit` делает требование ТЗ настоящим гейтом.
    """
    if limit <= 0.0:
        return 0.0
    inside = min(abs(value) / limit, 1.0)
    return slope * inside + excess(value, limit)


def signed_excess(value: float, limit: float) -> float:
    """Односторонний hinge: штрафуется только превышение сверху (для асимметричных величин)."""
    return max(value - limit, 0.0)


def xte_limit_for(groundspeed_kts: float | None) -> float:
    """Допуск по оси ВПП для текущей фазы: пробег ±3 м, руление ±1 м (ТЗ 5.1.3.1)."""
    if groundspeed_kts is not None and groundspeed_kts < TAXI_PHASE_KTS:
        return XTE_TAXI_MAX_M
    return XTE_ROLLOUT_MAX_M


def _effort_saturated(value: float, pid, tol: float) -> bool:
    """Упёрлась ли команда в границу **со стороны усилия**.

    Важное различие: нулевая граница — это не исчерпанный авторитет, а его отсутствие.
    Тормоз на 0 означает «торможение не требуется» (мы медленнее эталона), реверс на 0 —
    то же самое. Считать это насыщением значит поднимать флаг на каждом такте начала
    пробега. Насыщение — только ненулевая граница: тормоз на 1, реверс на −1, руль на ±1.
    """
    if value >= pid.max_out - tol and abs(pid.max_out) > tol:
        return True
    if value <= pid.min_out + tol and abs(pid.min_out) > tol:
        return True
    return False


def saturation_fraction(command, pids: dict, *, tol: float = 1e-6) -> float:
    """Доля из 5 команд, исчерпавших авторитет (упёршихся в ненулевую границу PID).

    Насыщение = регулятор больше ничего не может: дальнейшая ошибка не парируется.
    Границы берутся из самих PID, а не хардкодятся, — они часть пресета сценария.
    """
    pairs = (
        ("runway_center_pid", command.rudder_cmd),
        ("pid_brake_l", command.cmd_brake_l),
        ("pid_brake_r", command.cmd_brake_r),
        ("pid_rev_l", command.cmd_rev_l),
        ("pid_rev_r", command.cmd_rev_r),
    )
    hits = 0
    counted = 0
    for name, value in pairs:
        pid = pids.get(name)
        if pid is None:
            continue
        counted += 1
        if _effort_saturated(value, pid, tol):
            hits += 1
    return hits / counted if counted else 0.0


# --- Потактовый reward (PPO) -------------------------------------------------- #

@dataclass(frozen=True)
class RewardWeights:
    xte: float = 1.0
    speed: float = 0.3
    jerk: float = 0.2
    shield: float = 0.5
    heading: float = 0.5
    instability: float = 0.2
    saturation: float = 0.4


@dataclass
class RewardComponents:
    xte: float
    speed: float
    jerk: float
    shield: float
    heading: float
    instability: float
    saturation: float
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


def _speed_penalty(speed_error_ms: float) -> float:
    """Асимметрия: перелёт (едем быстрее эталона) дороже недолёта в `OVERSPEED_FACTOR` раз."""
    over = signed_excess(speed_error_ms, SPEED_TOL_MS) / SPEED_ERR_SCALE
    under = signed_excess(-speed_error_ms, SPEED_TOL_MS) / SPEED_ERR_SCALE
    return OVERSPEED_FACTOR * over + under


def compute_reward(*, xte_m: float, heading_error_deg: float, speed_error_ms: float,
                   command, prev_command=None, roll_deg: float = 0.0, yaw_rate: float = 0.0,
                   shield_l_shield: float = 0.0, groundspeed_kts: float | None = None,
                   saturation: float = 0.0,
                   weights: RewardWeights | None = None) -> RewardComponents:
    """Считает компоненты и суммарный reward. Все компоненты ≥ 0; reward = −Σ вес·компонента.

    `groundspeed_kts` выбирает фазовый допуск по оси (пробег ±3 м / руление ±1 м);
    `saturation` — доля насыщенных команд за такт (см. `saturation_fraction`).
    """
    w = weights or RewardWeights()

    xte = graded(xte_m, xte_limit_for(groundspeed_kts))          # гейт ТЗ 5.1.3.1
    heading = graded(heading_error_deg, HEADING_FAULT_MAX_DEG)   # гейт ТЗ 5.1.3.3
    speed = _speed_penalty(speed_error_ms)
    jerk = _command_jerk(command, prev_command)
    shield = shield_l_shield
    instability = abs(roll_deg) / ROLL_SCALE_DEG + abs(yaw_rate)

    total = -(w.xte * xte + w.speed * speed + w.jerk * jerk
              + w.shield * shield + w.heading * heading + w.instability * instability
              + w.saturation * saturation)
    return RewardComponents(xte=xte, speed=speed, jerk=jerk, shield=shield,
                            heading=heading, instability=instability,
                            saturation=saturation, total=total)


# --- Эпизодный objective (приёмка / качество меток / отбор чекпоинтов) -------- #

def _rms(values: list) -> float | None:
    if not values:
        return None
    return (sum(v * v for v in values) / len(values)) ** 0.5


def _p95(values: list) -> float | None:
    """95-й перцентиль. Устойчивее максимума к одиночному выбросу телеметрии."""
    if not values:
        return None
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * 0.95)))
    return ordered[idx]


def _component(raw: float, weight: float) -> dict:
    return {"raw": float(raw), "weight": float(weight), "weighted": float(raw * weight)}


@dataclass(frozen=True)
class ObjectiveWeights:
    """Веса эпизодных компонент. Отдельно от `RewardWeights`: там — плотный сигнал для PPO,
    здесь — сводная оценка прогона для приёмки и отбора."""
    xte_rollout: float = 1.0
    xte_taxi: float = 1.0
    heading: float = 1.0
    speed: float = 0.85
    smooth: float = 0.25
    saturation: float = 1.10
    instability: float = 0.70
    shield: float = 1.00


@dataclass
class EpisodeObjective:
    """Накопитель по эпизоду: собирает потактовые отсчёты → сводные компоненты.

    Использование: `add(...)` каждый такт, `summary()` в конце эпизода. Возвращает те же
    `{raw, weight, weighted}` + `total_loss`/`reward`, что и потактовый уровень, поэтому
    приёмка, отбор чекпоинтов и взвешивание SFT-меток говорят на одном языке.
    """
    weights: ObjectiveWeights = field(default_factory=ObjectiveWeights)

    _xte_rollout: list = field(default_factory=list)
    _xte_taxi: list = field(default_factory=list)
    _heading_above_hold: list = field(default_factory=list)
    _speed_err: list = field(default_factory=list)
    _saturation: list = field(default_factory=list)
    _roll: list = field(default_factory=list)
    _yaw_rate: list = field(default_factory=list)
    _rates: dict = field(default_factory=lambda: {"brake_l": [], "brake_r": [],
                                                  "rev_l": [], "rev_r": [], "rudder": []})
    _shield_activations: int = 0
    _shield_fallbacks: int = 0
    _l_shield: float = 0.0
    _prev_command = None
    _samples: int = 0
    _final_xte_m: float | None = None
    _final_speed_kts: float | None = None
    _stop_distance_m: float | None = None

    def add(self, *, xte_m: float, heading_error_deg: float, speed_error_ms: float,
            groundspeed_kts: float, command, saturation: float = 0.0,
            roll_deg: float = 0.0, yaw_rate: float = 0.0,
            traveled_distance_m: float | None = None, shield_report=None) -> None:
        self._samples += 1

        if groundspeed_kts < TAXI_PHASE_KTS:
            self._xte_taxi.append(xte_m)
        else:
            self._xte_rollout.append(xte_m)

        # ТЗ 5.1.3.3: курс держим до снижения скорости ниже 30 узлов — ниже не оцениваем.
        if groundspeed_kts >= HEADING_HOLD_UNTIL_KTS:
            self._heading_above_hold.append(heading_error_deg)

        self._speed_err.append(speed_error_ms)
        self._saturation.append(saturation)
        self._roll.append(roll_deg)
        self._yaw_rate.append(yaw_rate)

        if self._prev_command is not None:
            p = self._prev_command
            self._rates["brake_l"].append(abs(command.cmd_brake_l - p["brake_l"]))
            self._rates["brake_r"].append(abs(command.cmd_brake_r - p["brake_r"]))
            self._rates["rev_l"].append(abs(command.cmd_rev_l - p["rev_l"]))
            self._rates["rev_r"].append(abs(command.cmd_rev_r - p["rev_r"]))
            self._rates["rudder"].append(abs(command.rudder_cmd - p["rudder"]))
        self._prev_command = {"brake_l": command.cmd_brake_l, "brake_r": command.cmd_brake_r,
                              "rev_l": command.cmd_rev_l, "rev_r": command.cmd_rev_r,
                              "rudder": command.rudder_cmd}

        if shield_report is not None:
            if getattr(shield_report, "active", False):
                self._shield_activations += 1
            if getattr(shield_report, "fallback", False):
                self._shield_fallbacks += 1
            self._l_shield += getattr(shield_report, "l_shield", 0.0)

        self._final_xte_m = xte_m
        self._final_speed_kts = groundspeed_kts
        if traveled_distance_m is not None:
            self._stop_distance_m = traveled_distance_m

    def diagnostics(self) -> dict:
        """Сырые измерения эпизода. `None` там, где данных не было — приёмка обязана
        трактовать `None` как FAIL, а не как «условно прошло» (ср. `tz_compliance_audit.md`)."""
        return {
            "samples": self._samples,
            "xte_rollout_rms_m": _rms(self._xte_rollout),
            "xte_rollout_max_m": max((abs(v) for v in self._xte_rollout), default=None),
            "xte_taxi_rms_m": _rms(self._xte_taxi),
            "xte_taxi_max_m": max((abs(v) for v in self._xte_taxi), default=None),
            "heading_rms_deg": _rms(self._heading_above_hold),
            "heading_max_deg": max((abs(v) for v in self._heading_above_hold), default=None),
            "speed_err_rms_ms": _rms(self._speed_err),
            "overspeed_max_ms": max((v for v in self._speed_err), default=None),
            "saturation_ratio": (sum(self._saturation) / len(self._saturation)
                                 if self._saturation else None),
            "roll_max_deg": max((abs(v) for v in self._roll), default=None),
            "yaw_rate_p95": _p95([abs(v) for v in self._yaw_rate]),
            "rate_p95": {k: _p95(v) for k, v in self._rates.items()},
            "shield_activations": self._shield_activations,
            "shield_fallbacks": self._shield_fallbacks,
            "final_xte_m": self._final_xte_m,
            "final_speed_kts": self._final_speed_kts,
            "stop_distance_m": self._stop_distance_m,
        }

    def summary(self) -> dict:
        """Компоненты `{raw, weight, weighted}` + `total_loss`/`reward` + диагностика."""
        d = self.diagnostics()
        w = self.weights

        def _or0(x):
            return 0.0 if x is None else x

        rate_p95 = d["rate_p95"]
        smooth_raw = sum(_or0(v) for v in rate_p95.values())

        components = {
            "xte_rollout": _component(
                excess(_or0(d["xte_rollout_rms_m"]), XTE_ROLLOUT_MAX_M)
                + excess(_or0(d["xte_rollout_max_m"]), XTE_ROLLOUT_MAX_M),
                w.xte_rollout),
            "xte_taxi": _component(
                excess(_or0(d["xte_taxi_rms_m"]), XTE_TAXI_MAX_M)
                + excess(_or0(d["xte_taxi_max_m"]), XTE_TAXI_MAX_M),
                w.xte_taxi),
            "heading": _component(
                excess(_or0(d["heading_rms_deg"]), HEADING_FAULT_MAX_DEG)
                + excess(_or0(d["heading_max_deg"]), HEADING_FAULT_MAX_DEG),
                w.heading),
            "speed": _component(
                OVERSPEED_FACTOR * signed_excess(_or0(d["overspeed_max_ms"]), SPEED_TOL_MS) / SPEED_ERR_SCALE
                + _or0(d["speed_err_rms_ms"]) / SPEED_ERR_SCALE,
                w.speed),
            "smooth": _component(smooth_raw, w.smooth),
            "saturation": _component(_or0(d["saturation_ratio"]), w.saturation),
            "instability": _component(
                _or0(d["roll_max_deg"]) / ROLL_SCALE_DEG + _or0(d["yaw_rate_p95"]),
                w.instability),
            "shield": _component(
                self._l_shield / max(self._samples, 1) + 10.0 * float(self._shield_fallbacks > 0),
                w.shield),
        }
        total_loss = sum(c["weighted"] for c in components.values())
        return {
            "components": components,
            "diagnostics": d,
            "total_loss": total_loss,
            "reward": -total_loss,
        }
