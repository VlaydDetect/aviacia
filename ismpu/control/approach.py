"""Воздушный канал: заход по ILS, выравнивание, управление скоростью.

Перенос рабочего контура второго участника НИР (`roman_aviacia_ics/tools/ics_pid_controller.py`,
класс `ClearWeatherILSController`) в архитектуру пакета. Контур подтверждён на живом стенде — от
захода на 400+ футах до касания, — поэтому закон управления перенесён **без изменения численного
поведения**: те же коэффициенты, те же знаки, тот же порядок операций. Изменилось только
обрамление: регулятор наш (`control/pid.py` с флагами, воспроизводящими его численность),
телеметрия приходит параметром, а команда складывается в общий `ControlsState`.

Три контура:

* **курсовой** — отклонение курсового маяка (ddm → «точки») задаёт угол доворота, доворот → крен,
  крен → элероны;
* **продольный** — отклонение глиссады задаёт вертикальную скорость, из неё и опорного угла атаки
  формируется уставка тангажа, тангаж → `ElevatorCmd` (**в g**, так он задокументирован в датапуле
  стенда, это не градусы руля);
* **скоростной** — приборная скорость задаёт **темп** РУД; темп интегрируется в абсолютную
  уставку, а на стенд уходит и темп (град/с), и положение.

**Выравнивание — это фаза профиля уставки, а не отдельный закон.** Меняется только уставка
тангажа; тот же регулятор с тем же интегралом и теми же пределами ±0.5 g превращает её в команду.
Отдельного форсажа, «пола» команды и прямого перехвата руля высоты нет намеренно: они и создают
разрыв на входе в выравнивание. По той же причине `ControlMode` во время выравнивания **не
меняется** — смена режима отключает автопилот стенда (проверено коллегой на стенде), поэтому
`ModeFlare*`/`ModeAlign*`/`ModeRollout*` остаются нулями весь воздушный участок.

## Почему здесь единицы стенда, а не СИ

`Telemetry` — граница пересчёта в СИ, и весь наземный контур работает в СИ. Воздушный закон —
исключение, и осознанное: его коэффициенты размерные (градусы на фут-в-минуту, фут-в-минуту на
точку, узлы), откалиброваны на стенде именно в этих единицах, и перевод в СИ означал бы пересчёт
каждого коэффициента с последующей перекалибровкой. Поэтому канал читает «сырой» пакет
(`Telemetry.ics_inputs`) напрямую. Без пакета стенда воздушное управление невозможно — канал
честно отдаёт нейтральную команду, а не считает по нулям.
"""

import math
from dataclasses import dataclass

from ismpu.config.approach import ApproachConfig, APPROACH_DEFAULT
from ismpu.config.ics import RUDDER_MAX_DEG
from ismpu.config.envelope import (
    LandingFlapConfiguration, ApproachLimits, approach_limits, detect_landing_flaps,
    roll_limit_deg,
)
from ismpu.control.pid import PIDController


def clamp(value: float, lower: float, upper: float) -> float:
    return min(upper, max(lower, value))


def angle_error_deg(target: float, actual: float) -> float:
    """Разность курсов, приведённая к (-180, 180]."""
    return (target - actual + 180.0) % 360.0 - 180.0


@dataclass
class ApproachResult:
    """Внутренние величины такта: для логов, полей качества и приёмки.

    Команды отсюда не берутся — они уже записаны в `ControlsState`. Это диагностический срез:
    по нему видно, почему получилась именно такая команда (какая уставка, какая фаза, какой
    угол атаки), а без него разбор прогона на стенде сводится к угадыванию.
    """
    aileron_deg: float = 0.0
    elevator_g: float = 0.0
    rudder_deg: float = 0.0
    throttle_left_rate_deg_s: float = 0.0
    throttle_right_rate_deg_s: float = 0.0
    throttle_norm: float = 0.0
    throttle_target_angle_deg: float = 0.0

    loc_dots: float = 0.0
    gs_dots: float = 0.0
    course_deg: float = 0.0
    """Отклонение от курса в градусах (`loc_dots · loc_full_scale_deg`) — для допуска ТЗ 5.1.2.1."""
    glideslope_deg: float = 0.0
    """Отклонение от глиссады в градусах (`gs_dots · gs_full_scale_deg`) — для допуска ТЗ 5.1.2."""
    go_around: bool = False
    """Такт посчитан законом ухода на второй круг, а не заходом."""
    target_heading_deg: float = 0.0
    heading_error_deg: float = 0.0
    target_roll_deg: float = 0.0
    target_vs_fpm: float = 0.0
    target_pitch_deg: float = 0.0
    vertical_correction_deg: float = 0.0
    flight_path_angle_deg: float = 0.0
    target_flight_path_angle_deg: float = 0.0
    estimated_aoa_deg: float = 0.0
    reference_aoa_deg: float = 0.0
    mach: float = 0.0
    target_ias_kt: float = 0.0
    groundspeed_fpm: float = 0.0
    roll_limit_deg: float = 0.0

    limits: ApproachLimits | None = None
    flare_armed: bool = False
    flare_active: bool = False
    flare_progress: float = 0.0
    flare_entry_radio_altitude_ft: float = 0.0
    flare_entry_vertical_speed_fpm: float = 0.0
    envelope_warnings: tuple = ()


class ApproachChannel:
    """Заход по ILS с выравниванием. Телеметрию получает параметром, не читает сам.

    Коэффициенты статические (`config/approach.py`) — на воздушном участке нейросети пока нет.
    Регуляторы создаются здесь и **не попадают** в `ControllingSystem.pids`: тот словарь задаёт
    пространство коэффициентов NPGS, и лишние ключи в нём переопределили бы `ACTION_DIM`.
    """

    def __init__(self, config: ApproachConfig | None = None):
        self.config = config or APPROACH_DEFAULT
        self.roll_pid = PIDController(**self.config.roll_pid)
        self.pitch_pid = PIDController(**self.config.pitch_pid)
        self.speed_pid = PIDController(**self.config.speed_pid)
        self.result = ApproachResult()
        self.reset()

    @property
    def pids(self) -> dict:
        """Регуляторы канала по именам — для логов и приёмки, не для `ControllingSystem.pids`."""
        return {"roll_pid": self.roll_pid, "pitch_pid": self.pitch_pid,
                "speed_pid": self.speed_pid}

    def reset(self) -> None:
        """Сброс регуляторов и всей памяти профиля — новый заход начинается с чистого состояния."""
        self.roll_pid.reset()
        self.pitch_pid.reset()
        self.speed_pid.reset()
        self._target_pitch_deg = None
        self._reference_aoa_deg = None
        self._flare_active = False
        self._flare_entry_radio_altitude_ft = None
        self._flare_entry_vertical_speed_fpm = None
        self._flare_entry_pitch_target_deg = None
        self._throttle_norm = None
        self._target_ias_kt = None
        self.result = ApproachResult()

    # ------------------------------------------------------------------ #
    # Такт
    # ------------------------------------------------------------------ #

    def calc_commands(self, dt: float, state, telemetry) -> ApproachResult:
        """Такт воздушного управления: пишет команды в `state`, возвращает диагностику.

        Кадр без пакета стенда (`ics_inputs is None`) или невалидный — команда нейтральная:
        воздушный закон размерный и считать его по нулям значит выдать осмысленно выглядящее
        отклонение по несуществующим данным.
        """
        inp = getattr(telemetry, "ics_inputs", None) if telemetry is not None else None
        if telemetry is None or not telemetry.valid or inp is None:
            state.neutralize_airborne()
            return self.result

        cfg = self.config
        dt = clamp(dt, cfg.dt_min_s, cfg.dt_max_s)
        res = ApproachResult()

        limits = self._limits(inp, res)
        self._speed_setpoint(inp, limits, dt, res)
        self._lateral(inp, cfg, dt, res)
        target_vs = self._vertical_target(inp, cfg, res)
        self._pitch(inp, cfg, limits, dt, target_vs, res)
        self._throttle(inp, cfg, dt, res)
        res.course_deg = res.loc_dots * cfg.loc_full_scale_deg
        res.glideslope_deg = res.gs_dots * cfg.gs_full_scale_deg
        res.envelope_warnings = self._envelope_warnings(inp, limits, res)

        state.cmd_aileron = res.aileron_deg
        state.cmd_elevator = res.elevator_g
        # Руль направления живёт в общем нормированном поле: на заходе он нулевой, а когда
        # появится закон парирования сноса, он будет выражен так же, как на пробеге.
        state.rudder_cmd = res.rudder_deg / RUDDER_MAX_DEG
        state.cmd_throttle_l_rate = res.throttle_left_rate_deg_s
        state.cmd_throttle_r_rate = res.throttle_right_rate_deg_s
        state.cmd_throttle_norm = res.throttle_norm
        state.quality_lateral = abs(res.loc_dots)
        state.quality_heading = abs(res.heading_error_deg)
        state.quality_speed = abs(res.target_ias_kt - inp.IndicatedAirspeed)

        self.result = res
        return res

    def go_around_command(self, dt: float, state, telemetry) -> ApproachResult:
        """Такт ухода на второй круг: взлётный режим, кабрирование, крылья в горизонт.

        Заход больше не ведётся — локализатор и глиссаду не отслеживаем. Тангаж ведётся к
        **положительной** вертикальной скорости `go_around_target_vs_fpm` тем же `pitch_pid`, что
        и заход (отдельного закона набора нет), крен — к нулю, РУД — на полный вперёд максимальным
        темпом. `ControlMode` остаётся `Approach`: смена режима в воздухе сбрасывает автопилот
        стенда. Выравнивание принудительно снимается — на уходе оно неприменимо.
        """
        inp = getattr(telemetry, "ics_inputs", None) if telemetry is not None else None
        if telemetry is None or not telemetry.valid or inp is None:
            state.neutralize_airborne()
            return self.result

        cfg = self.config
        dt = clamp(dt, cfg.dt_min_s, cfg.dt_max_s)
        res = ApproachResult()
        res.go_around = True
        self._flare_active = False

        limits = self._limits(inp, res)

        # Набор: тангаж ведётся к положительной вертикальной скорости тем же продольным контуром.
        res.groundspeed_fpm = max(inp.GroundSpeed, 35.0) * 101.268591
        target_vs = cfg.go_around_target_vs_fpm
        res.target_vs_fpm = target_vs
        self._pitch(inp, cfg, limits, dt, target_vs, res)

        # Крылья в горизонт: уставка крена 0, руль направления 0.
        res.roll_limit_deg = roll_limit_deg(inp.RadioAltitude, cfg.max_roll_target_deg)
        res.target_roll_deg = clamp(cfg.go_around_roll_target_deg,
                                    -res.roll_limit_deg, res.roll_limit_deg)
        roll_error = res.target_roll_deg - inp.RollAngle
        res.aileron_deg = self.roll_pid.compute(roll_error, dt, measurement=inp.RollAngle)
        res.rudder_deg = 0.0

        # Взлётный режим: РУД → полный вперёд максимальным темпом на оба двигателя.
        self._throttle_norm = cfg.go_around_throttle_norm
        res.throttle_norm = cfg.go_around_throttle_norm
        res.throttle_target_angle_deg = cfg.go_around_throttle_norm * cfg.throttle_forward_max_deg
        res.throttle_left_rate_deg_s = cfg.throttle_left_rate_sign * cfg.throttle_rate_max_deg_per_s
        res.throttle_right_rate_deg_s = cfg.throttle_right_rate_sign * cfg.throttle_rate_max_deg_per_s

        state.cmd_aileron = res.aileron_deg
        state.cmd_elevator = res.elevator_g
        state.rudder_cmd = res.rudder_deg / RUDDER_MAX_DEG
        state.cmd_throttle_l_rate = res.throttle_left_rate_deg_s
        state.cmd_throttle_r_rate = res.throttle_right_rate_deg_s
        state.cmd_throttle_norm = res.throttle_norm
        # На уходе органы не выдерживают ни оси, ни скорости — показатели качества неприменимы.
        state.quality_lateral = 0.0
        state.quality_heading = 0.0
        state.quality_speed = 0.0

        self.result = res
        return res

    # ------------------------------------------------------------------ #
    # Составляющие такта
    # ------------------------------------------------------------------ #

    def _limits(self, inp, res: ApproachResult) -> ApproachLimits:
        """Эксплуатационные ограничения по фактической конфигурации и числу Маха."""
        cfg = self.config
        fallback = LandingFlapConfiguration(cfg.landing_flap_fallback)
        flaps = detect_landing_flaps(inp.FlapsAngle, fallback)
        static_temperature_k = max(180.0, 273.15 + inp.AirfieldTemp)
        speed_of_sound_kt = 38.967854 * math.sqrt(static_temperature_k)
        mach = (inp.TrueAirspeed / speed_of_sound_kt
                if inp.TrueAirspeedValid and inp.TrueAirspeed > 0.0 else 0.32)
        res.mach = mach
        limits = approach_limits(cfg.landing_weight_kg, flaps, mach)
        res.limits = limits
        return limits

    def _speed_setpoint(self, inp, limits: ApproachLimits, dt: float, res: ApproachResult) -> None:
        """Уставка приборной скорости, сводимая к VAPP ограниченным темпом.

        Начальное значение — фактическая скорость: заход, начатый выше VAPP, иначе на первом же
        такте потребовал бы полного сброса тяги.
        """
        cfg = self.config
        if self._target_ias_kt is None:
            self._target_ias_kt = (inp.IndicatedAirspeed
                                   if inp.IndicatedAirspeedValid and inp.IndicatedAirspeed > 0.0
                                   else limits.vapp_kt)
        step = cfg.target_ias_rate_kt_per_s * dt
        self._target_ias_kt += clamp(limits.vapp_kt - self._target_ias_kt, -step, step)
        res.target_ias_kt = self._target_ias_kt

    def _lateral(self, inp, cfg: ApproachConfig, dt: float, res: ApproachResult) -> None:
        """Курсовой маяк → угол доворота → уставка крена → элероны.

        Руль направления на заходе остаётся нулевым: снос парируется креном, а рыскание рулём
        на глиссаде рассогласовало бы контур с автопилотом стенда.
        """
        res.loc_dots = inp.LocDeviation / cfg.loc_full_scale_ddm
        intercept = clamp(cfg.localizer_sign * cfg.localizer_intercept_deg_per_dot * res.loc_dots,
                          -cfg.max_intercept_angle_deg, cfg.max_intercept_angle_deg)
        res.target_heading_deg = (inp.RunwayHeading + intercept) % 360.0
        res.heading_error_deg = angle_error_deg(res.target_heading_deg, inp.MagneticHeading)

        # Предел крена ужимается с высотой: у земли запас до касания законцовкой минимален.
        res.roll_limit_deg = roll_limit_deg(inp.RadioAltitude, cfg.max_roll_target_deg)
        res.target_roll_deg = clamp(cfg.heading_to_roll_gain * res.heading_error_deg,
                                    -res.roll_limit_deg, res.roll_limit_deg)
        roll_error = res.target_roll_deg - inp.RollAngle
        res.aileron_deg = self.roll_pid.compute(roll_error, dt, measurement=inp.RollAngle)
        res.rudder_deg = 0.0

    def _vertical_target(self, inp, cfg: ApproachConfig, res: ApproachResult) -> float:
        """Уставка вертикальной скорости: глиссада, а после входа — профиль выравнивания."""
        groundspeed_fpm = max(inp.GroundSpeed, 35.0) * 101.268591
        res.groundspeed_fpm = groundspeed_fpm
        nominal_vs = -groundspeed_fpm * math.tan(math.radians(cfg.glideslope_angle_deg))
        res.gs_dots = cfg.glideslope_sign * inp.GSDeviation / cfg.gs_full_scale_ddm
        target_vs = clamp(nominal_vs + cfg.glideslope_vs_correction_fpm_per_dot * res.gs_dots,
                          cfg.min_approach_target_vs_fpm, cfg.max_approach_target_vs_fpm)

        res.flare_armed = bool(inp.RadioAltitude <= cfg.flare_arm_radio_altitude_ft)
        if not self._flare_active:
            self._maybe_enter_flare(inp, cfg)

        res.flare_active = self._flare_active
        if self._flare_active:
            entry_altitude = (self._flare_entry_radio_altitude_ft
                              if self._flare_entry_radio_altitude_ft is not None
                              else cfg.flare_start_radio_altitude_ft)
            entry_vs = (self._flare_entry_vertical_speed_fpm
                        if self._flare_entry_vertical_speed_fpm is not None
                        else cfg.flare_initial_vs_fpm)
            span = max(entry_altitude - cfg.flare_end_radio_altitude_ft, 1.0)
            res.flare_progress = clamp((entry_altitude - inp.RadioAltitude) / span, 0.0, 1.0)
            target_vs = entry_vs + res.flare_progress * (cfg.touchdown_target_vs_fpm - entry_vs)
            res.flare_entry_radio_altitude_ft = entry_altitude
            res.flare_entry_vertical_speed_fpm = entry_vs
        else:
            res.flare_entry_radio_altitude_ft = cfg.flare_start_radio_altitude_ft
            res.flare_entry_vertical_speed_fpm = inp.VerticalSpeed

        res.target_vs_fpm = target_vs
        return target_vs

    def _maybe_enter_flare(self, inp, cfg: ApproachConfig) -> None:
        """Вход в выравнивание: по высоте либо по времени до земли.

        Второй признак нужен, потому что при большой вертикальной скорости фиксированные 150
        футов проходятся быстрее, чем профиль успевает отработать.
        """
        fixed_height_trigger = inp.RadioAltitude <= cfg.flare_start_radio_altitude_ft
        descent_rate_fps = max(-inp.VerticalSpeed / 60.0, 0.0)
        time_to_ground_s = (inp.RadioAltitude / descent_rate_fps
                            if descent_rate_fps > 0.1 else math.inf)
        time_trigger = (inp.VerticalSpeed < -50.0
                        and inp.RadioAltitude <= cfg.flare_max_start_radio_altitude_ft
                        and time_to_ground_s <= cfg.flare_time_to_ground_s)
        if not (fixed_height_trigger or time_trigger):
            return

        self._flare_active = True
        self._flare_entry_radio_altitude_ft = clamp(
            max(inp.RadioAltitude, cfg.flare_start_radio_altitude_ft),
            cfg.flare_end_radio_altitude_ft + 1.0, cfg.flare_max_start_radio_altitude_ft)
        # Опорная скорость входа фиксированная, а не измеренная: уставка тангажа всё равно
        # идёт с ограниченным темпом, поэтому ступени на входе это не создаёт.
        self._flare_entry_vertical_speed_fpm = cfg.flare_initial_vs_fpm
        self._flare_entry_pitch_target_deg = clamp(
            self._target_pitch_deg if self._target_pitch_deg is not None else inp.PitchAngle,
            cfg.flare_min_pitch_target_deg, cfg.flare_max_pitch_target_deg)

    def _pitch(self, inp, cfg: ApproachConfig, limits: ApproachLimits, dt: float,
               target_vs: float, res: ApproachResult) -> None:
        """Уставка тангажа (заход или выравнивание) → `ElevatorCmd` в g."""
        groundspeed_fpm = res.groundspeed_fpm
        res.flight_path_angle_deg = math.degrees(math.atan2(inp.VerticalSpeed, groundspeed_fpm))
        res.target_flight_path_angle_deg = math.degrees(math.atan2(target_vs, groundspeed_fpm))
        res.estimated_aoa_deg = inp.PitchAngle - res.flight_path_angle_deg
        vs_error = target_vs - inp.VerticalSpeed

        self._update_reference_aoa(inp, cfg, limits, dt, res, vs_error)
        res.reference_aoa_deg = (self._reference_aoa_deg if self._reference_aoa_deg is not None
                                 else cfg.approach_aoa_deg)

        if not self._flare_active:
            # На снижении быстрее нужного (ошибка > 0) коррекция агрессивнее: догонять глиссаду
            # сверху безопаснее, чем проваливаться под неё.
            gain = (cfg.vs_to_pitch_fast_descent_gain_deg_per_fpm if vs_error > 0.0
                    else cfg.vs_to_pitch_gain_deg_per_fpm)
            res.vertical_correction_deg = clamp(gain * vs_error,
                                                cfg.min_vertical_correction_deg,
                                                cfg.max_vertical_correction_deg)
            raw_target_pitch = clamp(
                res.reference_aoa_deg + res.target_flight_path_angle_deg
                + res.vertical_correction_deg,
                cfg.min_pitch_target_deg, cfg.max_pitch_target_deg)
        else:
            # Выравнивание ведётся прямо по ошибке вертикальной скорости и демпфируется как по
            # положению, так и по угловой скорости тангажа.
            res.vertical_correction_deg = cfg.flare_vs_to_pitch_gain_deg_per_fpm * vs_error
            pitch_rate = inp.BodyPitchRate if inp.BodyPitchRateValid else 0.0
            raw_target_pitch = clamp(
                cfg.flare_pitch_base_deg + res.vertical_correction_deg
                - cfg.flare_pitch_attitude_damping_gain * inp.PitchAngle
                - cfg.flare_pitch_rate_damping_gain * pitch_rate,
                cfg.flare_min_pitch_target_deg, cfg.flare_max_pitch_target_deg)
            if self._flare_entry_pitch_target_deg is not None:
                # Уставка не опускается ниже точки входа: опускание носа на выравнивании — это
                # удар основными стойками.
                raw_target_pitch = max(raw_target_pitch, self._flare_entry_pitch_target_deg)

        if self._target_pitch_deg is None:
            self._target_pitch_deg = clamp(inp.PitchAngle, cfg.min_pitch_target_deg,
                                           cfg.max_pitch_target_deg)
        rate = (cfg.flare_pitch_target_rate_deg_per_s if self._flare_active
                else cfg.pitch_target_rate_deg_per_s)
        step = rate * dt
        self._target_pitch_deg += clamp(raw_target_pitch - self._target_pitch_deg, -step, step)
        res.target_pitch_deg = self._target_pitch_deg

        pitch_error = res.target_pitch_deg - inp.PitchAngle
        effort = self.pitch_pid.compute(pitch_error, dt, measurement=inp.PitchAngle)
        if not math.isfinite(effort):
            raise ValueError("нефинитная команда руля высоты")
        res.elevator_g = cfg.elevator_command_sign * effort

    def _update_reference_aoa(self, inp, cfg: ApproachConfig, limits: ApproachLimits, dt: float,
                              res: ApproachResult, vs_error: float) -> None:
        """Медленная подстройка опорного угла атаки по фактическому полёту.

        Учиться разрешено **только на стабилизированной глиссаде**: иначе опорное значение
        впитает ошибку самого захода и контур начнёт держаться за собственный промах. Вне
        обучения при провале под глиссаду значение медленно возвращается к настроенному.
        """
        if not cfg.adaptive_aoa_enabled:
            return
        if not (inp.PitchAngleValid and inp.VerticalSpeedValid and inp.GroundSpeedValid):
            return

        upper = min(cfg.adaptive_aoa_max_deg, limits.alpha_prot_deg - 0.5)
        measured = clamp(res.estimated_aoa_deg, cfg.adaptive_aoa_min_deg, upper)
        configured = clamp(cfg.approach_aoa_deg, cfg.adaptive_aoa_min_deg, upper)
        learning_allowed = bool(not self._flare_active
                                and abs(res.gs_dots) <= cfg.adaptive_aoa_max_gs_dots
                                and abs(vs_error) <= cfg.adaptive_aoa_max_vs_error_fpm)

        if self._reference_aoa_deg is None:
            self._reference_aoa_deg = measured
        elif learning_allowed:
            alpha = (1.0 if cfg.adaptive_aoa_filter_tau_s <= 0.0
                     else -math.expm1(-dt / cfg.adaptive_aoa_filter_tau_s))
            filtered_step = alpha * (measured - self._reference_aoa_deg)
            max_step = cfg.adaptive_aoa_rate_deg_per_s * dt
            self._reference_aoa_deg += clamp(filtered_step, -max_step, max_step)
        elif not self._flare_active and res.gs_dots > 0.0 and vs_error > 0.0:
            recovery_step = cfg.adaptive_aoa_recovery_rate_deg_per_s * dt
            self._reference_aoa_deg += clamp(configured - self._reference_aoa_deg,
                                             -recovery_step, recovery_step)

    def _throttle(self, inp, cfg: ApproachConfig, dt: float, res: ApproachResult) -> None:
        """Ошибка скорости → темп РУД → абсолютная уставка → темпы на оба двигателя.

        Регулятор выдаёт **темп** нормированного положения, который интегрируется в уставку.
        Поэтому anti-windup здесь свой: если уставка упёрлась в 0 или 1, интеграл откатывается —
        иначе он копил бы за пределом хода РУД.

        Оба двигателя ведутся к **одной** уставке; разница углов РУД парируется позиционной
        обратной связью, а не разной командой, чтобы не создать асимметричную тягу.
        """
        speed_error = res.target_ias_kt - inp.IndicatedAirspeed
        if self._throttle_norm is None:
            measured_deg = 0.5 * (inp.LeftThrottleAngle + inp.RightThrottleAngle)
            self._throttle_norm = clamp(measured_deg / cfg.throttle_forward_max_deg, 0.0, 1.0)

        previous_integral = self.speed_pid.integral
        norm_rate = self.speed_pid.compute(speed_error, dt, measurement=inp.IndicatedAirspeed)
        unclamped = self._throttle_norm + norm_rate * dt
        if unclamped < 0.0 or unclamped > 1.0:
            self.speed_pid.integral = previous_integral
        self._throttle_norm = clamp(unclamped, 0.0, 1.0)

        logical_rate = clamp(norm_rate * cfg.throttle_forward_max_deg,
                             -cfg.throttle_rate_max_deg_per_s, cfg.throttle_rate_max_deg_per_s)
        target_angle = self._throttle_norm * cfg.throttle_forward_max_deg
        position_gain = cfg.throttle_position_gain_per_s
        if (abs(inp.LeftThrottleAngle - inp.RightThrottleAngle)
                >= cfg.throttle_sync_boost_threshold_deg):
            position_gain = max(position_gain, cfg.throttle_sync_boost_gain_per_s)

        left = clamp(logical_rate + position_gain * (target_angle - inp.LeftThrottleAngle),
                     -cfg.throttle_rate_max_deg_per_s, cfg.throttle_rate_max_deg_per_s)
        right = clamp(logical_rate + position_gain * (target_angle - inp.RightThrottleAngle),
                      -cfg.throttle_rate_max_deg_per_s, cfg.throttle_rate_max_deg_per_s)
        res.throttle_left_rate_deg_s = cfg.throttle_left_rate_sign * left
        res.throttle_right_rate_deg_s = cfg.throttle_right_rate_sign * right
        res.throttle_norm = self._throttle_norm
        res.throttle_target_angle_deg = target_angle

    def _envelope_warnings(self, inp, limits: ApproachLimits, res: ApproachResult) -> tuple:
        """Выход за эксплуатационные границы. Предупреждения, а не вмешательство в управление:
        закон остаётся тем же, а факт выхода попадает в лог и в отчёт приёмки."""
        warnings = []
        if inp.IndicatedAirspeed >= limits.vfe_kt:
            warnings.append("VFE")
        if inp.IndicatedAirspeed <= limits.vsr1_kt:
            warnings.append("VSR1")
        elif inp.IndicatedAirspeed < limits.vapp_kt:
            warnings.append("BELOW_VAPP")
        if res.estimated_aoa_deg >= limits.alpha_prot_deg:
            warnings.append("ALPHA_PROT")
        if res.estimated_aoa_deg >= limits.alpha_sw_deg:
            warnings.append("ALPHA_SW")
        if abs(inp.RollAngle) > res.roll_limit_deg:
            warnings.append("ROLL_LIMIT")
        # Нормальное ускорение от ИНС смещено к нулю: установившийся полёт = 0, а не 1 g.
        if inp.BodyNormAccelValid and abs(inp.BodyNormAccel) > 1.0:
            warnings.append("LOAD_FACTOR")
        if self._flare_active:
            if inp.IndicatedAirspeed <= limits.touchdown_speed_min_kt:
                warnings.append("TOUCHDOWN_SPEED_LOW")
            elif inp.IndicatedAirspeed >= limits.touchdown_speed_max_kt:
                warnings.append("TOUCHDOWN_SPEED_HIGH")
            if abs(inp.VerticalSpeed) > limits.touchdown_vertical_speed_limit_fpm:
                warnings.append("TOUCHDOWN_VS")
            if not 0.0 < inp.PitchAngle < limits.touchdown_pitch_limit_deg:
                warnings.append("TOUCHDOWN_PITCH")
        return tuple(warnings)
