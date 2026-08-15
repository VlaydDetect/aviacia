"""Оркестратор классического контура управления — на всём интервале полёта.

`ControllingSystem` на каждом такте выбирает участок (`control/flight.py`) и вызывает его закон:
в воздухе — `ApproachController` (заход по ILS и выравнивание), на земле — speed controller,
guidance и allocator органов управления.

**Транспорта здесь нет.** Контур получает объект стенда (`envs.ics_sim.ICSSim`) и общается с ним
только через `read_telemetry`/`step`; ни JSON, ни UDP, ни единиц ICD он не знает — их переводит
`ICSSim`.

**Воздушные регуляторы живут отдельно от `self.pids`.** Словарь `pids` — это ровно пять
регуляторов пробега из `config/regulators.py`, и из него собраны `ACTION_DIM`, пространство
коэффициентов и все сохранённые чекпоинты NPGS. Положить туда регуляторы захода значило бы молча
переопределить пространство действий; они лежат в самом канале
(`approach_channel.pids`) и настраиваются статически.
"""

from typing import TYPE_CHECKING, ClassVar, Optional
from dataclasses import dataclass

from ismpu.control.pid import PIDController
from ismpu.control.trajectory import CompletionRule, ReferenceTrajectory, VelocityLaw
from ismpu.control.runway_tracker import RunwayTracker
from ismpu.control.channels import ControlsState, LongitudinalChannel, LateralChannel
from ismpu.control.ground_allocator import GroundControlAllocator
from ismpu.control.approach import ApproachController
from ismpu.control.approach_criteria import ApproachCriteriaMonitor
from ismpu.control.tolerance import ToleranceReport, evaluate_approach_tolerances
from ismpu.control.failures import FailureManager, FailureMode
from ismpu.control.flight import (
    FlightSegment, ApproachRefused, initial_segment, segment_is_decidable, touched_down,
    approach_blocker, ils_blocker, above_decision_height, at_lateral_alignment_gate,
)
from ismpu.config.approach import ApproachConfig
from ismpu.config.constants import TARGET_SPEED_KTS
from ismpu.config.requirements import GO_AROUND_CONFIRM_TICKS
from ismpu.config.ics import LANDING_MODE_RADIO_ALTITUDE_FT
from ismpu.config.runway import RWY_START_LAT, RWY_START_LON, RWY_END_LAT, RWY_END_LON
from ismpu.envs.ics_sim import Telemetry
from ismpu.envs.sim_interface import SimInterface
from ismpu.config.regulators import PidMap
from ismpu.config.scenarios import ConditionMatch
from ismpu.utils.converts import Converts

if TYPE_CHECKING:
    from ismpu.config.scenarios import Scenario


@dataclass
class GoAroundManeuver:
    """Состояние идущего ухода на второй круг. Пока он активен, заход не ведётся."""
    reason: str
    entry_radio_altitude_ft: float
    elapsed_s: float = 0.0


class ControllingSystem:
    """Оркестратор классического контура поверх стенда (`envs.ics_sim.ICSSim`).

    Простейший цикл:

        sim = ICSSim(listen_port=3030)
        controller = ControllingSystem(sim)
        scenario.apply_control(controller)
        controller.begin_flight(sim.read_telemetry())   # с какого участка начинаем
        while not controller.control_step(DT):
            pass

    `control_step` сам читает телеметрию и сам отправляет команды через `sim`. Среда обучения
    (`RolloutEnv`) вместо этого подаёт кадр параметром и ставит `send=False`, чтобы вклинить
    Shield между расчётом и отправкой.

    Без `begin_flight` участок остаётся пробегом. Это осознанное умолчание: среда обучения и все
    офлайн-разборы работают именно с пробегом, и «угадывать» для них воздушный заход по кадру без
    пакета стенда нельзя.
    """

    def __init__(
        self,
        sim: SimInterface | None = None,
        approach_config: Optional[ApproachConfig] = None,
    ) -> None:
        self.sim: SimInterface | None = sim

        self.failures: FailureManager = FailureManager()

        self.pids: PidMap = {}
        self.state: ControlsState = ControlsState()
        self.last_telemetry: Telemetry | None = None
        # Каналы создаются в setup(); аннотации фиксируют их публичный контракт.
        self.lateral_channel: LateralChannel
        self.longitudinal_channel: LongitudinalChannel
        self.ground_allocator: GroundControlAllocator

        self.segment: FlightSegment = FlightSegment.ROLLOUT
        self._segment_decided: bool = True
        """Определён ли участок окончательно. `False` только между `begin_flight` по
        непригодному кадру и первым пригодным — см. `begin_flight`."""
        self.approach_channel: ApproachController = ApproachController(approach_config)
        self.landing_committed: bool = False
        self.abort_reason: Optional[str] = None

        # Уход на второй круг (fallback в воздухе). `go_around` активен → заход не ведётся.
        self.go_around: Optional[GoAroundManeuver] = None
        self.go_around_reason: Optional[str] = None
        self.tolerance_report: ToleranceReport | None = None
        self.approach_criteria: ApproachCriteriaMonitor = ApproachCriteriaMonitor()
        """Отчёт монитора допусков за последний такт захода (диагностика/логи)."""
        self._violation_ticks: int = 0
        """Дебаунс триггера ухода: сколько тактов подряд допуски не выполняются."""
        self.scenario: Scenario | None = None
        self.aircraft_profile_name: str | None = None
        self._configured_segment: FlightSegment | None = None

    def bind_scenario(self, scenario: "Scenario", aircraft_profile: str) -> None:
        """Связать сценарий с контуром; PID активируются после определения участка."""
        if aircraft_profile not in scenario.aircraft_controls:
            known = ", ".join(sorted(scenario.aircraft_controls))
            raise KeyError(
                f"сценарий {scenario.scenario_id!r} не содержит профиль "
                f"{aircraft_profile!r}; доступны: {known}")
        self.scenario = scenario
        self.aircraft_profile_name = aircraft_profile
        self._configured_segment = None

    def activate_segment(
        self,
        segment: FlightSegment,
        telemetry: Telemetry | None = None,
    ) -> None:
        """Пересобрать stateful PID и уведомить backend до первого такта участка."""
        if self.scenario is None or self.aircraft_profile_name is None:
            raise RuntimeError("сценарий и AircraftProfile не привязаны к контроллеру")
        if self._configured_segment is segment:
            return
        self.scenario.apply_control(self, self.aircraft_profile_name, segment)
        self._configured_segment = segment
        if self.sim is not None:
            enter_segment = getattr(self.sim, "enter_segment", None)
            if enter_segment is not None:
                report = enter_segment(self.scenario, segment, telemetry)
                if (
                    isinstance(report, ConditionMatch)
                    and getattr(self.sim, "validate_conditions", True)
                ):
                    # ICS cannot set conditions.  On a boundary its current telemetry remains
                    # authoritative for degradation on the very first tick; the scenario is
                    # only the expected set recorded by ConditionMatch.
                    expected = self.scenario.conditions_for(segment).failures
                    actual = (
                        expected - report.missing_failures
                    ) | report.unexpected_failures
                    self.failures.sync(actual)

    def setup(
        self,
        pids: PidMap,
        lookahead_min: float = 15.0,
        lookahead_gain: float = 1.5,
        xte_gain: float = 1.0,
        steering_brake_gain: float = 0.4,
        steering_rev_gain: float = 0.0,
        law: VelocityLaw = VelocityLaw.GAUSS_BELL,
        target_speed_kts: float = TARGET_SPEED_KTS,
        braking_distance_m: float | None = None,
        completion_rule: CompletionRule = CompletionRule.HANDOVER_TAXI,
        steering_rate_per_s: float = 1.0,
        brake_rate_per_s: float = 1.0,
        reverse_rate_per_s: float = 1.0,
        failure_yaw_compensation_gain: float = 1.0,
    ) -> None:
        self.pids = pids

        # Настройка сценария = начало эпизода: команды сбрасываются вместе с PID и каналами.
        # Иначе `break_control`, выставленный в конце прошлого пробега, оставался бы взведён
        # и следующий эпизод завершался бы на первом такте.
        self.state.reset()
        self.go_around = None
        self.go_around_reason = None
        self.landing_committed = False
        self.tolerance_report = None
        self.approach_criteria = ApproachCriteriaMonitor()
        self._violation_ticks = 0

        tracker = RunwayTracker(lookahead_min, lookahead_gain, xte_gain)
        self.lateral_channel = LateralChannel(pids["runway_center_pid"], tracker)
        self.ground_allocator = GroundControlAllocator(
            steering_brake_gain=steering_brake_gain,
            steering_rev_gain=steering_rev_gain,
            steering_rate_per_s=steering_rate_per_s,
            brake_rate_per_s=brake_rate_per_s,
            reverse_rate_per_s=reverse_rate_per_s,
            failure_yaw_compensation_gain=failure_yaw_compensation_gain,
        )

        trajectory = ReferenceTrajectory(
            target_speed_kts,
            target_speed_kts,
            (tracker.haversine_distance(
                RWY_START_LAT, RWY_START_LON, RWY_END_LAT, RWY_END_LON)
             if braking_distance_m is None else braking_distance_m),
            law,
            completion_rule,
        )
        self.longitudinal_channel = LongitudinalChannel(
            pids["pid_brake_l"], pids["pid_brake_r"], pids["pid_rev_l"], pids["pid_rev_r"],
            trajectory)

    def setup_approach(self, config: Optional[ApproachConfig] = None) -> ApproachController:
        """Пересобрать воздушный канал под заданные настройки. → новый канал.

        Именно пересобрать, а не переписать коэффициенты: регуляторы захода **stateful**
        (интеграл, фильтр производной, память профиля выравнивания), и перенос состояния прошлого
        захода в новый — это ступень команды руля высоты на первом же такте.
        """
        self.approach_channel = ApproachController(config)
        return self.approach_channel

    def set_longitudinal_params(
        self,
        lookahead_min: float,
        lookahead_gain: float,
        xte_gain: float,
    ) -> None:
        """Обновить параметры геометрического наведения латерального канала.

        Имя сохранено для совместимости с ранним API конфигурации.
        """
        self.lateral_channel.tracker.lookahead_min = lookahead_min
        self.lateral_channel.tracker.lookahead_gain = lookahead_gain
        self.lateral_channel.tracker.xte_gain = xte_gain

    def set_lateral_params(self, steering_brake_gain: float, steering_rev_gain: float) -> None:
        self.ground_allocator.steering_brake_gain = steering_brake_gain
        self.ground_allocator.steering_rev_gain = steering_rev_gain

    def set_channel_weights(self, w_lon: float, w_lat: float) -> None:
        """Веса влияния каналов (актор, §6): множители к выходам каналов. 1.0 = классика."""
        self.longitudinal_channel.w_lon = w_lon
        self.lateral_channel.w_lat = w_lat

    def set_velocity_law(self, law: VelocityLaw) -> None:
        self.longitudinal_channel.trajectory.set_law(law)

    def apply_failure(self, mode: FailureMode) -> None:
        self.failures.activate(mode)

    def sync_failures(self, telemetry: Telemetry | None) -> None:
        """Привести модель отказов к тому, что сообщает борт (`ICSInputs.Fault*`).

        Отказы читаются, а не задаются: их источник — стенд. Пресет сценария выставляет лишь
        стартовое предположение, а фактическая конфигурация может отличаться и меняться посреди
        пробега, поэтому состояние пересобирается каждый такт.

        При невалидной телеметрии состояние **сохраняется**: единичный потерянный пакет не
        означает, что отказавший орган починился, а «починка» на такт вернула бы рулю авторитет,
        которого у него нет.

        Кадр без пакета стенда (синтетическая телеметрия в тестах и офлайн-разборах) не трогает
        отказы вовсе: пустой `faults` там означает «сообщать некому», а не «всё исправно», и
        приравнять одно к другому значило бы молча снимать отказ пресета.
        """
        if telemetry is None or not telemetry.valid:
            return
        if not telemetry.faults_available:
            return
        self.failures.sync(telemetry.faults)

    def begin_flight(
        self,
        telemetry: Telemetry | None,
        requested_segment: FlightSegment | None = None,
    ) -> FlightSegment:
        """Определить стартовый участок по кадру стенда. → выбранный участок.

        Вызывается в начале прогона. Если стенд сообщает, что ВС в воздухе и выше порога приёма
        захода, начинаем с захода; во всех остальных случаях — с пробега.

        **Непригодный кадр решением не считается.** Первый `read_telemetry` может вернуться по
        таймауту (стенд ещё не шлёт, оператор не нажал ICS) — тогда участок остаётся пробегом
        лишь *предварительно*, и решение принимается заново на первом кадре с пакетом стенда.
        Иначе получалась бы необратимая ошибка: автомат включения решает по **более поздним**
        кадрам и уходит в `Approach`, маска и содержимое команды берутся из его режима, а закон
        считают наземные каналы — на стенд ушли бы нулевой руль высоты (это команда нулевой
        перегрузки, а не нейтраль) и «пройденная дистанция», интегрируемая в полёте.

        Заход, который вести нельзя (`approach_blocker`), — это `ApproachRefused`, а не тихий
        откат на наземный закон: ВС в воздухе, и молча поехать по земле хуже, чем отказаться.
        """
        self.landing_committed = False
        if requested_segment not in (None, FlightSegment.TAXI):
            raise ValueError("явно начинать разрешено только с TAXI")
        self._segment_decided = (
            requested_segment is not None or segment_is_decidable(telemetry))
        self.segment = (
            (requested_segment or initial_segment(telemetry))
            if self._segment_decided else FlightSegment.ROLLOUT
        )
        if self.segment is FlightSegment.APPROACH:
            blocker = approach_blocker(telemetry)
            if blocker is not None:
                raise ApproachRefused(f"заход невозможен: {blocker}")
        if self._segment_decided and self.scenario is not None:
            self.activate_segment(self.segment, telemetry)
        elif self.segment is FlightSegment.APPROACH:
            self.approach_channel.reset()
        return self.segment

    def _settle_segment(self, telemetry: Telemetry) -> None:
        """Досчитать отложенное решение об участке на первом пригодном кадре."""
        if self._segment_decided or not segment_is_decidable(telemetry):
            return
        self._segment_decided = True
        settled = initial_segment(telemetry)
        if settled is not FlightSegment.APPROACH:
            self.segment = settled
            if self.scenario is not None:
                self.activate_segment(settled, telemetry)
            return
        blocker = approach_blocker(telemetry)
        if blocker is not None:
            raise ApproachRefused(f"заход невозможен: {blocker}")
        self.segment = FlightSegment.APPROACH
        if self.scenario is not None:
            self.activate_segment(FlightSegment.APPROACH, telemetry)
        else:
            self.approach_channel.reset()

    def control_step(
        self,
        dt: float,
        telemetry: Telemetry | None = None,
        send: bool = True,
    ) -> bool:
        """Такт управления. → True, если управление окончено (или телеметрия невалидна).

        `telemetry=None` — кадр берётся сам: сначала результат прошлого `sim.step` (он уже свежий),
        и только на первом такте делается отдельный `sim.read_telemetry()`. Так на стенде выходит
        ровно один приём UDP на такт, а не два.

        `send=False` — команды считаются в `self.state`, но не отправляются: между расчётом и
        отправкой вклинивается Shield (`RolloutEnv`), а отправляет уже вызывающий.
        """
        if telemetry is None:
            telemetry = self.last_telemetry if self.last_telemetry is not None else self._read()
        self.last_telemetry = telemetry
        self._settle_segment(telemetry)
        self.sync_failures(telemetry)

        if self.segment is FlightSegment.APPROACH:
            finished = self._approach_step(dt, telemetry)
        else:
            finished = self._ground_step(dt)
        if finished:
            return True

        if send:
            self.last_telemetry = self._require_sim().step(self.state)

        return False

    def _approach_step(self, dt: float, telemetry: Telemetry) -> bool:
        """Такт воздушного участка. → True, если управлять больше нечем.

        Касание проверяется **до** расчёта закона: после обжатия основных стоек воздушный закон
        неприменим (глиссады уже нет, а РУД пора отдавать реверсу), и такт нужно считать уже
        наземными каналами. Иначе первый такт пробега уходил бы с командой захода.
        """
        if touched_down(telemetry):
            # Касание важнее потери воздушного датчика: управление уже обязано перейти земле.
            # При этом отчётный cutoff обновляем только по полностью валидному воздушному кадру.
            if (
                telemetry.radio_altitude_ft is not None
                and not telemetry.invalid_approach_signals
                and telemetry.radio_altitude_ft
                <= self.approach_criteria.config.cutoff_radio_altitude_ft
                and not self.approach_criteria.cutoff_reached
            ):
                self.approach_criteria.observe(
                    telemetry, self.approach_channel.result.flight_path_angle_deg)
            self.hand_over_to_rollout()
            return self._ground_step(dt)

        # Если начатый выше высоты решения уход всё же закончился касанием, земля имеет
        # приоритет: воздушную команду на полосе не выдаём. Поэтому эта ветвь строго после WoW.
        if self.go_around is not None:
            return self._go_around_step(dt, telemetry)

        if not telemetry.valid:
            # Без кадра стенда воздушный закон считать не по чему: размерный расчёт по нулям
            # выдал бы правдоподобное отклонение по несуществующим данным.
            return self._abort_approach("нет валидной телеметрии со стенда")

        blocker = approach_blocker(telemetry)
        if blocker is not None:
            return self._abort_approach(blocker)

        self._commit_landing_mode(telemetry)

        criteria_ra = telemetry.radio_altitude_ft
        if (
            criteria_ra is not None
            and criteria_ra <= self.approach_criteria.config.cutoff_radio_altitude_ft
            and not self.approach_criteria.cutoff_reached
        ):
            self.approach_criteria.observe(
                telemetry, self.approach_channel.result.flight_path_angle_deg)

        # Прерывание по потере наведения живёт здесь, а не в законе: закон читает отклонения
        # безусловно (как и эталон), и решение «дальше вести нечем» принимает контур над ним.
        blocker = ils_blocker(telemetry)
        if blocker is not None:
            return self._abort_approach(blocker)

        self.approach_channel.calc_commands(dt, self.state, telemetry)
        if not self.approach_criteria.cutoff_reached:
            self.approach_criteria.observe(
                telemetry, self.approach_channel.result.flight_path_angle_deg)

        # Проверка допусков ТЗ на каждом такте. Если выше высоты решения они устойчиво не
        # выполняются — садиться нельзя: заход прерывается уходом на второй круг.
        self.tolerance_report = evaluate_approach_tolerances(
            telemetry, self.approach_channel.result, self.approach_channel.result.limits,
            telemetry.faults, at_decision_gate=at_lateral_alignment_gate(telemetry))
        reason = self._should_go_around(telemetry, self.tolerance_report)
        if reason is not None:
            self._start_go_around(reason, telemetry)
            self._go_around_step(dt, telemetry)   # первый такт набора — уже в этом кадре
        return False

    def _commit_landing_mode(self, telemetry: Telemetry) -> None:
        """Зафиксировать `Approach → Landing` на 25 ft без смены воздушного закона."""
        if self.landing_committed:
            return
        ra = telemetry.radio_altitude_ft
        if ra is None or ra > LANDING_MODE_RADIO_ALTITUDE_FT:
            return
        request = getattr(self.sim, "request_landing", None)
        if request is not None and request() is False:
            raise RuntimeError("backend отказал в переходе Approach → Landing")
        self.landing_committed = True

    def _abort_approach(self, reason: str) -> bool:
        """Прервать заход с названной причиной. → True (управлять больше нечем)."""
        self.abort_reason = reason
        print(f"[ControllingSystem] Заход прерван: {reason}")
        self.state.neutralize_airborne()
        self.state.break_control = True
        return True

    # ------------------------------------------------------------------ #
    # Уход на второй круг (fallback в воздухе)
    # ------------------------------------------------------------------ #

    def _reverse_stowed(self) -> bool:
        """Реверс убран: команды обратной тяги нулевые.

        В воздухе реверс не выдаётся вовсе, поэтому guard тут всегда истинен — но он прямо
        кодирует требование «если реверс уже включён, взлёт невозможен» и готов к тому дню, когда
        уход появится и на пробеге.
        """
        return self.state.cmd_rev_l == 0.0 and self.state.cmd_rev_r == 0.0

    def _should_go_around(
        self,
        telemetry: Telemetry,
        report: ToleranceReport | None,
    ) -> Optional[str]:
        """Нужно ли уходить на второй круг по этому такту. → причина или `None`.

        Только **в воздухе** (участок захода) и только **выше высоты решения** (30 м): на земле и
        ниже 30 м посадка неизбежна, ухода нет даже при козлении. Реверс должен быть убран.
        Срабатывает по **устойчивому** невыполнению допусков ТЗ (дебаунс `GO_AROUND_CONFIRM_TICKS`),
        а не по одиночному выбросу шумного сигнала ILS.
        """
        if self.segment is not FlightSegment.APPROACH:
            return None
        if self.landing_committed:
            self._violation_ticks = 0
            return None
        if not above_decision_height(telemetry):
            self._violation_ticks = 0
            return None
        if not self._reverse_stowed():
            return None
        if report is None or report.landing_allowed:
            self._violation_ticks = 0
            return None
        self._violation_ticks += 1
        if self._violation_ticks < GO_AROUND_CONFIRM_TICKS:
            return None
        return f"допуски захода не выполнены ({', '.join(report.violations)})"

    def _start_go_around(self, reason: str, telemetry: Telemetry) -> None:
        """Начать уход: зафиксировать состояние манёвра и высоту входа."""
        ra = telemetry.radio_altitude_ft if telemetry is not None else None
        self.go_around = GoAroundManeuver(reason=reason, entry_radio_altitude_ft=ra or 0.0)
        self.go_around_reason = reason
        self._violation_ticks = 0
        print(f"[ControllingSystem] Уход на второй круг: {reason}")

    def _go_around_step(self, dt: float, telemetry: Telemetry) -> bool:
        """Такт манёвра ухода. → True, когда набор устойчив (пора отдать управление пилоту).

        Взлётный режим + кабрирование + крылья в горизонт (`ApproachController.go_around_command`).
        `ControlMode` не меняется (остаётся `Approach`): смена режима в воздухе сбрасывает
        автопилот стенда. Завершение = устойчивый набор или страховочный таймаут; дальше цикл
        останавливается, и `control_exception` снимает заявку каналов — это и есть передача пилоту.
        """
        maneuver = self.go_around
        if maneuver is None:
            raise RuntimeError("манёвр ухода не инициализирован")
        maneuver.elapsed_s += dt
        cfg = self.approach_channel.config
        if telemetry is None or not telemetry.valid:
            self.abort_reason = "уход прерван: нет валидной телеметрии со стенда"
            self.state.neutralize_airborne()
            return True
        self.approach_channel.go_around_command(dt, self.state, telemetry)
        if self._climb_established(telemetry) or maneuver.elapsed_s >= cfg.go_around_max_seconds:
            print("[ControllingSystem] Набор установлен — управление передаётся пилоту.")
            self.state.neutralize_airborne()
            return True
        return False

    def _climb_established(self, telemetry: Telemetry) -> bool:
        """Набор устойчив: есть и вертикальная скорость вверх, и прирост радиовысоты над входом."""
        inp = telemetry.approach_inputs
        cfg = self.approach_channel.config
        climbing = inp.VerticalSpeed >= cfg.go_around_min_climb_fpm
        maneuver = self.go_around
        if maneuver is None:
            return False
        gained = ((telemetry.radio_altitude_ft or 0.0) - maneuver.entry_radio_altitude_ft
                  >= cfg.go_around_min_gain_ft)
        return bool(climbing and gained)

    def _ground_step(self, dt: float) -> bool:
        """Три блока: speed controller → guidance → allocator."""
        telemetry = self.last_telemetry
        longitudinal = self.longitudinal_channel.compute(dt, telemetry)
        lateral = self.lateral_channel.compute(dt, telemetry)
        allocation = self.ground_allocator.allocate(
            self.segment,
            longitudinal,
            lateral,
            self.failures.state,
            self.state,
            telemetry,
            dt,
        )
        command = allocation.limited
        self.state.cmd_rudder = command.rudder
        self.state.cmd_pedal = command.pedal
        self.state.cmd_tiller = command.tiller
        self.state.cmd_brake_l = command.brake_left
        self.state.cmd_brake_r = command.brake_right
        self.state.cmd_rev_l = command.reverse_left
        self.state.cmd_rev_r = command.reverse_right
        self.state.quality_speed = (
            abs(longitudinal.error * Converts.MS_TO_KTS)
            if longitudinal.error is not None else 0.0)
        self.state.quality_lateral = abs(lateral.xte) if lateral.xte is not None else 0.0
        self.state.quality_heading = (
            abs(lateral.course_error) if lateral.course_error is not None else 0.0)
        self.state.break_control = longitudinal.stop_requested

        self._track_applied(dt)
        return longitudinal.stop_requested

    def hand_over_to_rollout(self) -> None:
        """Передать управление с посадки на пробег (`ControlMode 2 → 3`).

        Момент — первое обжатие основной стойки. Раньше нельзя: смена `ControlMode` до касания
        сбрасывает автопилот стенда, поэтому весь заход и посадка используют один воздушный
        закон (`Approach`, затем `Landing` с 25 ft).
        """
        if self.segment is not FlightSegment.APPROACH:
            return
        self.segment = FlightSegment.ROLLOUT
        if self.scenario is not None:
            self.activate_segment(FlightSegment.ROLLOUT, self.last_telemetry)
        # Воздушные команды больше не выдаются — маска пробега их не заявляет, но оставлять в
        # структуре последнее отклонение элеронов значит хранить мусор в логах и в отчёте.
        self.state.neutralize_airborne()
        telemetry = self.last_telemetry
        if telemetry is not None and telemetry.valid and telemetry.groundspeed_ms is not None:
            self.longitudinal_channel.begin(telemetry.groundspeed_ms)
        if self.sim is not None:
            self.sim.request_rollout()

    TAXI_HANDOVER_FRAMES: ClassVar[int] = 4
    """Сколько кадров передать после перехода `3 → 4`. Транспорт — UDP: одиночный кадр с новым
    режимом может потеряться, и стенд не увидит фронта, по которому только и переключается."""

    def hand_over_to_taxi(self, frames: int = TAXI_HANDOVER_FRAMES) -> bool:
        """Передать управление в руление (`ControlMode 3 → 4`) — пробег окончен.

        Вызывается, когда контур объявил достижение скорости руления. Без этого стенд остаётся
        в режиме пробега, хотя ВС уже рулит. Разрешающее условие (обжатие стоек) проверяет сам
        автомат включения (`io/ics_engagement.py`).

        Переход **действительно передаётся**, а не только записывается у нас: `request_taxi`
        меняет лишь состояние автомата, а стенд переключается по фронту `ControlMode` в
        полученном кадре. Раньше после этого вызова управление уходило в остановку цикла, и
        режим `Taxi` не попадал на провод ни разу — стенд так и оставался в пробеге.
        """
        sim = self._require_sim()
        accepted = sim.request_taxi()
        if not accepted:
            return False
        self.segment = FlightSegment.TAXI
        if self.scenario is not None:
            self.activate_segment(FlightSegment.TAXI, self.last_telemetry)
        telemetry = self.last_telemetry
        if telemetry is not None and telemetry.valid and telemetry.groundspeed_ms is not None:
            self.longitudinal_channel.begin(telemetry.groundspeed_ms)
        for _ in range(max(1, frames)):
            sim.step(self.state)
        return True

    def _read(self) -> Telemetry:
        return self._require_sim().read_telemetry()

    def _require_sim(self) -> SimInterface:
        if self.sim is None:
            raise RuntimeError(
                "контуру не задан стенд: без него он не может ни прочитать телеметрию, ни "
                "отправить команды. Передайте ICSSim в ControllingSystem(sim=...) либо подавайте "
                "кадр параметром и используйте send=False.")
        return self.sim

    # Фактически применённая команда ≠ выходу PID: её меняют вес канала, allocator, rate limit
    # и доступность актуатора. Без tracking интегратор копит на недоступный орган.
    def _track_applied(self, dt: float) -> None:
        """Back-calculation по итоговым командам. No-op, пока у PID не задан `tracking_tau_s`."""
        allocation = self.ground_allocator.last_diagnostics
        steering = allocation.steering_applied if allocation is not None else self.state.cmd_rudder
        base = allocation.base if allocation is not None else None
        failures = self.failures.state
        brake_left = (
            min(base.brake_left * failures.brake_left_eff, self.state.cmd_brake_l)
            if base is not None else self.state.cmd_brake_l)
        brake_right = (
            min(base.brake_right * failures.brake_right_eff, self.state.cmd_brake_r)
            if base is not None else self.state.cmd_brake_r)
        reverse_left = (
            -min(abs(base.reverse_left * failures.reverse_left_eff * failures.thrust_left_eff),
                 abs(self.state.cmd_rev_l))
            if base is not None else self.state.cmd_rev_l)
        reverse_right = (
            -min(abs(base.reverse_right * failures.reverse_right_eff * failures.thrust_right_eff),
                 abs(self.state.cmd_rev_r))
            if base is not None else self.state.cmd_rev_r)
        applied = (
            ("runway_center_pid", steering,
             allocation.steering_request if allocation is not None else steering,
             self.lateral_channel.w_lat),
            ("pid_brake_l", brake_left,
             base.brake_left if base is not None else brake_left,
             self.longitudinal_channel.w_lon),
            ("pid_brake_r", brake_right,
             base.brake_right if base is not None else brake_right,
             self.longitudinal_channel.w_lon),
            ("pid_rev_l", reverse_left,
             base.reverse_left if base is not None else reverse_left,
             self.longitudinal_channel.w_lon),
            ("pid_rev_r", reverse_right,
             base.reverse_right if base is not None else reverse_right,
             self.longitudinal_channel.w_lon),
        )
        for regulator, command, requested, weight in applied:
            pid = self.pids.get(regulator)
            if pid is not None:
                if abs(weight) > 1e-12:
                    command /= weight
                    requested /= weight
                else:
                    command, requested = 0.0, pid.last_output
                pid.track(command, dt, commanded_output=requested)

    def control_exception(self) -> None:
        """Аварийная остановка: обнулить органы и **снять заявку каналов**.

        Именно отправить, а не замолчать: молчание оставит последнее отклонение приложенным до
        срабатывания сторожа на стороне стенда. Но и нулевой команды с заявленной маской мало —
        в воздухе нулевое положение РУД это команда «малый газ», а не отказ от управления.
        Поэтому уходим пакетом деактивации (`ControlValidMask = 0`, `ControlMode = Off`), и стенд
        забирает ВС себе.
        """
        print("\n[ControllingSystem] Остановка. Сброс органов и снятие заявки каналов.")
        self.state.neutralize()
        if self.sim is not None:
            self.sim.step(self.state)      # нейтраль в уже заявленных каналах
            self.sim.deactivate()          # затем снятие заявки
        self.state.break_control = True
