"""Shield — детерминированный защитный контур между актором и классическим PID.

Философия (плана §1/§9): актор (NPGS) выдаёт **абсолютные коэффициенты PID** (`kp, ki, kd`
на каждый регулятор) и веса влияния каналов (`w_lon, w_lat`). Shield — НЕ обучается, всегда
активен, и нейросеть не может подать команду мимо него.

**Пресет сценария — якорь безопасности.** Даже при абсолютном выходе Shield центрирует
допустимый коридор на сертифицированном пресете сценария (передаётся как `preset_gains`):
hard-bounds и rate-limit — вокруг пресета, fallback — прямая запись пресета. Так классический
контроллер остаётся активной границей и точкой отката (ключевой аргумент ТЗ-совместимости:
сеть — ограниченный советчик вокруг классики, не сам регулятор). PID-передаточная функция в
сеть не встроена — её считает `PIDController`.

Три уровня + fallback (диаграмма, блок 4):

1. **Коэффициенты** — clip абсолютных gain'ов к физическому диапазону gain-пространства
   (`agent.gain_space`, `[lo, hi]`) и весов к `[weight_min, weight_max]`.
2. **Согласованность с пресетом** — hard-bounds `[hard_low·preset, hard_high·preset]`,
   неотрицательность, rate-limit между тактами; OOD-детектор (грубо аномальный вход → fallback).
3. **Runtime safety** — поведенческие проверки итоговых команд: реверс на низкой скорости
   (<60 узлов), чрезмерно резкое торможение (rate), срыв по курсу.
4. **Fallback** — при OOD или грубом нарушении курса эффективные gain'ы = пресет сценария
   (чистая классика) на этот/следующий такт.

Связь с loss (§11): активация уровня → штраф в `L_shield`; резкие скачки коэффициентов и
команд → в `L_smooth`. Обе величины накапливаются в `ShieldReport`.

Интеграция (Этап 4): в inference-пути среда вызывает
`guard_coefficients(gain_command, preset_gains)` ДО расчёта команд контуром, применяет
эффективные gain'ы к PID, затем `guard_command(command, runtime_state)` ПОСЛЕ — на итоговом
`ControlsState`.
"""

from dataclasses import dataclass, field
from typing import Optional

from ismpu.control.channels import ControlsState
from ismpu.config.regulators import REGULATOR_ORDER, GAIN_KEYS, N_GAINS, ACTION_DIM
from ismpu.agent import gain_space

# Обратная совместимость имён (ранее объявлялись здесь).
N_ALPHA = N_GAINS   # 15 коэффициентов (kp, ki, kd) × 5 регуляторов


def _clip(x, lo, hi):
    return lo if x < lo else hi if x > hi else x


# --------------------------------------------------------------------------- #
# Структуры данных
# --------------------------------------------------------------------------- #

@dataclass
class GainCommand:
    """Выход актора: абсолютные коэффициенты PID + веса каналов.

    `gains[reg] = {'kp','ki','kd'}` — абсолютные коэффициенты регулятора `reg`.
    `w_lon`, `w_lat` — веса влияния продольного/латерального каналов.
    """
    gains: dict
    w_lon: float = 1.0
    w_lat: float = 1.0

    @classmethod
    def from_gains(cls, gains: dict, w_lon: float = 1.0, w_lat: float = 1.0) -> "GainCommand":
        """Построение из словаря коэффициентов (напр. пресета сценария)."""
        return cls(gains={reg: dict(g) for reg, g in gains.items()}, w_lon=w_lon, w_lat=w_lat)

    @classmethod
    def from_vector(cls, vec, regulators=REGULATOR_ORDER) -> "GainCommand":
        """Плоский вектор действия (17,) → GainCommand. Layout: [gains×15, w_lon, w_lat]."""
        gains, i = {}, 0
        for reg in regulators:
            gains[reg] = {k: float(vec[i + j]) for j, k in enumerate(GAIN_KEYS)}
            i += len(GAIN_KEYS)
        return cls(gains=gains, w_lon=float(vec[i]), w_lat=float(vec[i + 1]))

    def to_vector(self, regulators=REGULATOR_ORDER) -> list:
        vec = []
        for reg in regulators:
            vec.extend(self.gains[reg][k] for k in GAIN_KEYS)
        vec.extend((self.w_lon, self.w_lat))
        return vec


@dataclass
class RuntimeState:
    """Наблюдаемое состояние для поведенческих проверок уровня 3."""
    groundspeed_kts: float
    heading_error_deg: float = 0.0
    xte_m: float = 0.0


@dataclass
class ShieldReport:
    """Что сделал Shield за такт: активированные правила, штрафы, fallback."""
    level1_active: bool = False
    level2_active: bool = False
    level3_active: bool = False
    ood: bool = False
    fallback: bool = False
    l_shield: float = 0.0
    l_smooth: float = 0.0
    rules: list = field(default_factory=list)

    def _mark_level(self, level: int):
        if level == 1:
            self.level1_active = True
        elif level == 2:
            self.level2_active = True
        elif level == 3:
            self.level3_active = True

    @property
    def active(self) -> bool:
        return self.level1_active or self.level2_active or self.level3_active or self.fallback


@dataclass(frozen=True)
class ShieldConfig:
    """Границы и веса штрафов Shield (все — настраиваемые, а не свойства сети)."""
    # Уровень 1 — веса каналов
    weight_min: float = 0.0
    weight_max: float = 2.0
    # OOD — грубо аномальный вход → fallback на пресет
    gain_ood_factor: float = 3.0    # gain вне [lo/factor, hi·factor] → OOD
    weight_ood_min: float = -0.5
    weight_ood_max: float = 3.0
    # Уровень 2 — эффективные gain'ы (мультипликативные границы вокруг ПРЕСЕТА)
    hard_low_factor: float = 0.3
    hard_high_factor: float = 2.5
    rate_limit_frac: float = 0.25   # макс |Δgain|/preset за такт
    # Уровень 3 — поведение
    reverse_min_speed_kts: float = 60.0   # реверс запрещён ниже (ср. LongitudinalChannel)
    brake_rate_limit: float = 0.5         # макс прирост тормозной команды за такт
    heading_soft_deg: float = 8.0         # срыв по курсу: штраф (ТЗ-гейт 5°, это запас)
    heading_hard_deg: float = 15.0        # грубый срыв → fallback
    # Веса штрафов в L_shield
    w_level1: float = 0.1
    w_level2: float = 0.3
    w_level3: float = 0.5
    w_fallback: float = 1.0


# --------------------------------------------------------------------------- #
# Вспомогательные функции интеграции
# --------------------------------------------------------------------------- #

def base_gains_from_pids(pids: dict) -> dict:
    """Снимок (kp, ki, kd) регуляторов — пресет-якорь для Shield и т.п."""
    return {reg: {"kp": p.kp, "ki": p.ki, "kd": p.kd} for reg, p in pids.items()}


def apply_gains_to_pids(pids: dict, gains: dict) -> None:
    """Записывает эффективные gain'ы обратно в регуляторы (перед control_step)."""
    for reg, g in gains.items():
        pids[reg].kp = g["kp"]
        pids[reg].ki = g["ki"]
        pids[reg].kd = g["kd"]


# --------------------------------------------------------------------------- #
# Shield
# --------------------------------------------------------------------------- #

class Shield:
    """Защитный контур. Детерминирован; хранит состояние прошлого такта для rate-лимитов."""

    def __init__(self, config: Optional[ShieldConfig] = None):
        self.config = config or ShieldConfig()
        self.reset()

    def reset(self) -> None:
        self._prev_gains: Optional[dict] = None
        self._prev_brakes: Optional[tuple] = None
        self._fallback_latched = False

    # --- Уровни 1–2: абсолютные коэффициенты → безопасные эффективные gain'ы ---- #

    def guard_coefficients(self, command: GainCommand, preset_gains: dict) -> tuple:
        """Уровни 1–2. Возвращает `(effective_gains, safe_command, report)`.

        `effective_gains[reg] = {'kp','ki','kd'}` — после clip к физдиапазону, hard-bounds
        вокруг пресета, неотрицательности и rate-limit. При OOD/защёлкнутом fallback —
        коэффициенты пресета сценария (классика)."""
        cfg = self.config
        report = ShieldReport()

        if self._fallback_latched:
            report.fallback = True
            report.rules.append("FALLBACK:latched")
            report.l_shield += cfg.w_fallback
            report._mark_level(3)
            self._fallback_latched = False
            safe = GainCommand.from_gains(preset_gains)
        elif self._is_ood(command):
            report.ood = True
            report.fallback = True
            report.rules.append("OOD:fallback")
            report.l_shield += cfg.w_fallback
            report._mark_level(2)
            safe = GainCommand.from_gains(preset_gains)
        else:
            safe = self._clip_command(command, report)

        eff = {reg: dict(safe.gains[reg]) for reg in safe.gains}
        self._enforce_bounds(eff, preset_gains, report)
        self._enforce_rate_limit(eff, preset_gains, report)
        self._prev_gains = {reg: dict(g) for reg, g in eff.items()}
        return eff, safe, report

    def _clip_command(self, cmd: GainCommand, report: ShieldReport) -> GainCommand:
        cfg = self.config
        new_gains = {}
        for reg, g in cmd.gains.items():
            lo, hi = gain_space.GAIN_LO_MAP[reg], gain_space.GAIN_HI_MAP[reg]
            clipped = {k: _clip(g[k], lo[k], hi[k]) for k in GAIN_KEYS}
            if any(clipped[k] != g[k] for k in GAIN_KEYS):
                self._flag(report, f"L1:gain_clip:{reg}", level=1)
            new_gains[reg] = clipped
        w_lon = _clip(cmd.w_lon, cfg.weight_min, cfg.weight_max)
        w_lat = _clip(cmd.w_lat, cfg.weight_min, cfg.weight_max)
        if w_lon != cmd.w_lon or w_lat != cmd.w_lat:
            self._flag(report, "L1:weight_clip", level=1)
        return GainCommand(gains=new_gains, w_lon=w_lon, w_lat=w_lat)

    def _is_ood(self, cmd: GainCommand) -> bool:
        cfg = self.config
        for reg, g in cmd.gains.items():
            lo, hi = gain_space.GAIN_LO_MAP[reg], gain_space.GAIN_HI_MAP[reg]
            for k in GAIN_KEYS:
                if g[k] < lo[k] / cfg.gain_ood_factor or g[k] > hi[k] * cfg.gain_ood_factor:
                    return True
        for w in (cmd.w_lon, cmd.w_lat):
            if w < cfg.weight_ood_min or w > cfg.weight_ood_max:
                return True
        return False

    def _enforce_bounds(self, eff: dict, preset: dict, report: ShieldReport) -> None:
        cfg = self.config
        for reg, g in eff.items():
            for k in GAIN_KEYS:
                b = preset[reg][k]
                v = g[k]
                if v < 0.0:  # консистентность: gain'ы неотрицательны
                    v = 0.0
                    self._flag(report, f"L2:negative:{reg}:{k}", level=2)
                if b > 0.0:
                    cv = _clip(v, b * cfg.hard_low_factor, b * cfg.hard_high_factor)
                    if cv != v:
                        self._flag(report, f"L2:hardbound:{reg}:{k}", level=2)
                    v = cv
                g[k] = v

    def _enforce_rate_limit(self, eff: dict, preset: dict, report: ShieldReport) -> None:
        cfg = self.config
        if self._prev_gains is None:
            return
        for reg, g in eff.items():
            for k in GAIN_KEYS:
                b = preset[reg][k]
                if b <= 0.0:
                    continue
                prev = self._prev_gains[reg][k]
                max_delta = cfg.rate_limit_frac * b
                delta = g[k] - prev
                if abs(delta) > max_delta:
                    excess = abs(delta) - max_delta
                    g[k] = prev + _clip(delta, -max_delta, max_delta)
                    self._flag(report, f"L2:rate:{reg}:{k}", level=2, smooth=excess / b)

    # --- Уровень 3: поведенческие проверки итоговых команд ------------------ #

    def guard_command(self, command: ControlsState, runtime: RuntimeState,
                      report: Optional[ShieldReport] = None) -> tuple:
        """Уровень 3. Правит небезопасные команды и возвращает `(command, report)`."""
        cfg = self.config
        report = report or ShieldReport()

        # Реверс на низкой скорости — принудительное отключение.
        if runtime.groundspeed_kts < cfg.reverse_min_speed_kts and (
                command.cmd_rev_l != 0.0 or command.cmd_rev_r != 0.0):
            command.cmd_rev_l = 0.0
            command.cmd_rev_r = 0.0
            self._flag(report, "L3:reverse_low_speed", level=3)

        # Чрезмерно резкое торможение — ограничение прироста команды за такт.
        if self._prev_brakes is not None:
            pl, pr = self._prev_brakes
            if command.cmd_brake_l - pl > cfg.brake_rate_limit:
                excess = (command.cmd_brake_l - pl) - cfg.brake_rate_limit
                command.cmd_brake_l = pl + cfg.brake_rate_limit
                self._flag(report, "L3:brake_rate:l", level=3, smooth=excess)
            if command.cmd_brake_r - pr > cfg.brake_rate_limit:
                excess = (command.cmd_brake_r - pr) - cfg.brake_rate_limit
                command.cmd_brake_r = pr + cfg.brake_rate_limit
                self._flag(report, "L3:brake_rate:r", level=3, smooth=excess)
        self._prev_brakes = (command.cmd_brake_l, command.cmd_brake_r)

        # Срыв по курсу.
        he = abs(runtime.heading_error_deg)
        if he > cfg.heading_hard_deg:
            self._flag(report, "L3:heading_hard", level=3, penalty=cfg.w_fallback)
            report.fallback = True
            self._fallback_latched = True   # следующий такт коэффициентов — классика
        elif he > cfg.heading_soft_deg:
            self._flag(report, "L3:heading_soft", level=3)

        return command, report

    # --- учёт штрафов ------------------------------------------------------- #

    def _flag(self, report: ShieldReport, name: str, level: int,
              penalty: Optional[float] = None, smooth: float = 0.0) -> None:
        report.rules.append(name)
        report._mark_level(level)
        if penalty is None:
            penalty = {1: self.config.w_level1, 2: self.config.w_level2, 3: self.config.w_level3}[level]
        report.l_shield += penalty
        report.l_smooth += smooth
