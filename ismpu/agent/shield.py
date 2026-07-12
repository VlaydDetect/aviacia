"""Shield — детерминированный защитный контур между актором и классическим PID.

Философия (плана §1/§9): актор выдаёт **мультипликативные поправки** к коэффициентам
PID (`α_p, α_i, α_d` на каждый регулятор) и веса влияния каналов (`w_lon, w_lat`).
Shield — НЕ обучается, всегда активен, и нейросеть не может подать команду мимо него.
Он гарантирует, что при тождественных поправках (α = 1, веса = 1) поведение бит-в-бит
совпадает с классикой (инвариант identity).

Три уровня + fallback (диаграмма, блок 4):

1. **Поправки** — clip слишком больших `α`/весов к допустимым границам.
2. **Коэффициенты PID** — после применения поправок: hard bounds, консистентность
   (неотрицательность gain'ов), rate-limit между тактами, OOD-детектор (сырой выход
   сети далеко за обучающим диапазоном → fallback на классику).
3. **Runtime safety** — поведенческие проверки итоговых команд: реверс на низкой
   скорости (<60 узлов), чрезмерно резкое торможение (rate), срыв по курсу.
4. **Fallback** — при OOD или грубом нарушении курса поправки заменяются на identity
   (чистый классический PID) на этот/следующий такт.

Связь с loss (§11): активация уровня → штраф в `L_shield`; резкие скачки коэффициентов
и команд → в `L_smooth`. Обе величины накапливаются в `ShieldReport`.

Интеграция (Этап 4): в inference-пути актора среда вызывает
`guard_coefficients(corrections, base_gains)` ДО расчёта команд контуром, применяет
эффективные gain'ы к PID, затем `guard_command(command, runtime_state)` ПОСЛЕ — на
итоговом `ControlsState`. Здесь модуль автономен и покрыт юнит-тестами (§9: «Shield
реализуется и тестируется до актора»).
"""

from dataclasses import dataclass, field
from typing import Optional

from ismpu.control.channels import ControlsState
from ismpu.control.pid import PIDController

# Порядок регуляторов = ключи словаря `pids` в ControllingSystem (см. clamp_all).
REGULATOR_ORDER = ("runway_center_pid", "pid_brake_l", "pid_brake_r", "pid_rev_l", "pid_rev_r")
N_ALPHA = len(REGULATOR_ORDER) * 3  # 15 поправок к (kp, ki, kd)
ACTION_DIM = N_ALPHA + 2            # + (w_lon, w_lat) = 17


def _clip(x, lo, hi):
    return lo if x < lo else hi if x > hi else x


# --------------------------------------------------------------------------- #
# Структуры данных
# --------------------------------------------------------------------------- #

@dataclass
class Corrections:
    """Выход актора: мультипликативные поправки к gain'ам + веса каналов.

    `alpha[reg] = (α_p, α_i, α_d)` — множители к (kp, ki, kd) регулятора `reg`.
    `w_lon`, `w_lat` — веса влияния продольного/латерального каналов.
    """
    alpha: dict
    w_lon: float = 1.0
    w_lat: float = 1.0

    @classmethod
    def identity(cls, regulators=REGULATOR_ORDER) -> "Corrections":
        return cls(alpha={reg: (1.0, 1.0, 1.0) for reg in regulators}, w_lon=1.0, w_lat=1.0)

    @classmethod
    def from_vector(cls, vec, regulators=REGULATOR_ORDER) -> "Corrections":
        """Плоский вектор актора (17,) → Corrections. Layout: [α×15, w_lon, w_lat]."""
        alpha, i = {}, 0
        for reg in regulators:
            alpha[reg] = (float(vec[i]), float(vec[i + 1]), float(vec[i + 2]))
            i += 3
        return cls(alpha=alpha, w_lon=float(vec[i]), w_lat=float(vec[i + 1]))

    def to_vector(self, regulators=REGULATOR_ORDER) -> list:
        vec = []
        for reg in regulators:
            vec.extend(self.alpha[reg])
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
    # Уровень 1 — clip поправок
    alpha_min: float = 0.5
    alpha_max: float = 1.5
    weight_min: float = 0.0
    weight_max: float = 2.0
    # OOD — сырой выход сети за этими границами → fallback на классику
    alpha_ood_min: float = 0.2
    alpha_ood_max: float = 2.0
    weight_ood_min: float = -0.5
    weight_ood_max: float = 3.0
    # Уровень 2 — эффективные gain'ы (мультипликативные границы вокруг базовых)
    hard_low_factor: float = 0.3
    hard_high_factor: float = 2.5
    rate_limit_frac: float = 0.25   # макс |Δgain|/base за такт
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
    """Снимок базовых (kp, ki, kd) регуляторов — вход Shield."""
    return {reg: {"kp": p.kp, "ki": p.ki, "kd": p.kd} for reg, p in pids.items()}


def apply_gains_to_pids(pids: dict, gains: dict) -> None:
    """Записывает эффективные gain'ы обратно в регуляторы (Этап 4, перед control_step)."""
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

    # --- Уровни 1–2: поправки → безопасные эффективные gain'ы --------------- #

    def guard_coefficients(self, corrections: Corrections, base_gains: dict) -> tuple:
        """Уровни 1–2. Возвращает `(effective_gains, safe_corrections, report)`.

        `effective_gains[reg] = {'kp','ki','kd'}` — после clip поправок, применения к
        базе, hard bounds, консистентности и rate-limit. При OOD/защёлкнутом fallback —
        identity (классические gain'ы).
        """
        cfg = self.config
        report = ShieldReport()

        if self._fallback_latched:
            report.fallback = True
            report.rules.append("FALLBACK:latched")
            report.l_shield += cfg.w_fallback
            report._mark_level(3)
            self._fallback_latched = False
            safe = Corrections.identity(tuple(base_gains))
        elif self._is_ood(corrections):
            report.ood = True
            report.fallback = True
            report.rules.append("OOD:fallback")
            report.l_shield += cfg.w_fallback
            report._mark_level(2)
            safe = Corrections.identity(tuple(base_gains))
        else:
            safe = self._clip_corrections(corrections, report)

        eff = self._apply(safe, base_gains)
        self._enforce_bounds(eff, base_gains, report)
        self._enforce_rate_limit(eff, base_gains, report)
        self._prev_gains = {reg: dict(g) for reg, g in eff.items()}
        return eff, safe, report

    def _clip_corrections(self, corr: Corrections, report: ShieldReport) -> Corrections:
        cfg = self.config
        new_alpha = {}
        for reg, (ap, ai, ad) in corr.alpha.items():
            cap, cai, cad = (_clip(ap, cfg.alpha_min, cfg.alpha_max),
                             _clip(ai, cfg.alpha_min, cfg.alpha_max),
                             _clip(ad, cfg.alpha_min, cfg.alpha_max))
            if (cap, cai, cad) != (ap, ai, ad):
                self._flag(report, f"L1:alpha_clip:{reg}", level=1)
            new_alpha[reg] = (cap, cai, cad)
        w_lon = _clip(corr.w_lon, cfg.weight_min, cfg.weight_max)
        w_lat = _clip(corr.w_lat, cfg.weight_min, cfg.weight_max)
        if w_lon != corr.w_lon or w_lat != corr.w_lat:
            self._flag(report, "L1:weight_clip", level=1)
        return Corrections(alpha=new_alpha, w_lon=w_lon, w_lat=w_lat)

    def _is_ood(self, corr: Corrections) -> bool:
        cfg = self.config
        for triple in corr.alpha.values():
            for a in triple:
                if a < cfg.alpha_ood_min or a > cfg.alpha_ood_max:
                    return True
        for w in (corr.w_lon, corr.w_lat):
            if w < cfg.weight_ood_min or w > cfg.weight_ood_max:
                return True
        return False

    @staticmethod
    def _apply(corr: Corrections, base: dict) -> dict:
        eff = {}
        for reg, g in base.items():
            ap, ai, ad = corr.alpha.get(reg, (1.0, 1.0, 1.0))
            eff[reg] = {"kp": g["kp"] * ap, "ki": g["ki"] * ai, "kd": g["kd"] * ad}
        return eff

    def _enforce_bounds(self, eff: dict, base: dict, report: ShieldReport) -> None:
        cfg = self.config
        for reg, g in eff.items():
            for k in ("kp", "ki", "kd"):
                b = base[reg][k]
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

    def _enforce_rate_limit(self, eff: dict, base: dict, report: ShieldReport) -> None:
        cfg = self.config
        if self._prev_gains is None:
            return
        for reg, g in eff.items():
            for k in ("kp", "ki", "kd"):
                b = base[reg][k]
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
