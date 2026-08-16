"""Управляющий цикл 20 Гц против стенда заказчика — **весь интервал полёта**.

Порядок: подключение к стенду → рукопожатие под текущий участок → цикл `control_step` до
скорости руления (или Ctrl-C) → передача управления в руление и снятие заявки каналов.

Участок выбирается по первому кадру стенда (`control/flight.py`):

* ВС в воздухе выше 400 футов — начинаем с **захода**: рукопожатие `ControlMode 0 → 1`, дальше
  заход по ILS, `Landing` с 25 ft, касание и передача на пробег (`2 → 3`);
* ВС на полосе — начинаем с **пробега** (или подхватываем уже идущий), как раньше.

Стенд слушается по UDP (по умолчанию на всех интерфейсах, порт 3030); адрес самого стенда
определяется из заголовка первого входящего пакета, задавать его не нужно.
"""

import argparse
import logging
import time

from ismpu.control.system import ControllingSystem
from ismpu.control.flight import FlightSegment, initial_segment
from ismpu.control.trajectory import CompletionRule
from ismpu.config.constants import DT
from ismpu.io.ics_connector import LISTEN_IP_ANY
from ismpu.envs.backend_factory import build_sim
from ismpu.envs.sim_interface import (
    RunResult, RunStopReason, ShutdownReport, SimInterface,
)
from ismpu.runtime.run_recorder import RunRecorder
from ismpu.config.run_matrix import CASE_BY_CODE, SOURCE_SHA256
from ismpu.config.scenarios import (
    SCENARIOS, ProfileStatus, Scenario, rebind_matrix_run, resolve_scenario,
    scenario_for_matrix_run, select_for_telemetry, compose_matrix_scenario,
)
from ismpu.config.json_config import load_scenario

logger = logging.getLogger(__name__)


def run(controller: ControllingSystem, sim: SimInterface, scenario: Scenario, *,
        start: str | None = None, recorder: RunRecorder | None = None,
        dashboard_state=None, sft_runtime=None) -> RunResult:
    """Прогоняет один полёт на уже настроенном контуре."""
    reason = RunStopReason.ERROR
    details: str | None = None
    shutdown_report: ShutdownReport | None = None
    run_started = time.monotonic()
    try:
        if recorder is not None:
            recorder.attach_sim(sim)
            recorder.start()
        telemetry = sim.reset(scenario, start=start)

        # Участок определяется ДО рукопожатия: от него зависит стимул включения.
        segment = controller.begin_flight(
            telemetry,
            FlightSegment.TAXI if start == "taxi" else None,
        )
        print(f"Участок по телеметрии стенда: {segment.value}")

        print("Прогрев (ожидание, пока стенд примет управление)...")
        sim.warm_up()
        controller.last_telemetry = sim.read_telemetry()
        run_started = time.monotonic()

        print("Управление включено.")
        last_time = time.monotonic()
        while True:
            current_time = time.monotonic()
            dt = current_time - last_time

            if dt >= DT:
                if dashboard_state is not None:
                    dashboard_state.apply_pending_gain_updates()
                if sft_runtime is not None:
                    sft_runtime.before_step(controller, controller.last_telemetry, dt)
                # Контур сам читает телеметрию и сам отправляет команды через sim.
                finished = controller.control_step(dt)
                if sft_runtime is not None and controller.last_step_telemetry is not None:
                    sft_runtime.after_step(
                        controller, controller.last_step_telemetry, dt)
                if recorder is not None and controller.last_step_telemetry is not None:
                    recorder.record(
                        controller.last_step_telemetry,
                        controller,
                        elapsed_s=time.monotonic() - run_started,
                        dt=dt,
                    )
                if finished:
                    if controller.segment is FlightSegment.ROLLOUT:
                        rule = controller.longitudinal_channel.trajectory.completion_rule
                        if rule is CompletionRule.HANDOVER_TAXI:
                            # Эксплуатационный полёт: ControlMode 3 → 4 на 7,5 узла.
                            if controller.hand_over_to_taxi() and recorder is not None:
                                elapsed = time.monotonic() - run_started
                                recorder.record_event(
                                    "segment",
                                    data={"previous": "rollout", "value": "taxi",
                                          "handover_only": True},
                                    time_s=elapsed,
                                    tick_id=controller.tick_id,
                                    segment="taxi",
                                )
                                recorder.record_event(
                                    "control_mode",
                                    data={"previous": 3, "value": 4,
                                          "handover_only": True},
                                    time_s=elapsed,
                                    tick_id=controller.tick_id,
                                    segment="taxi",
                                )
                        # Матричный FULL_STOP завершается на месте и ниже снимает каналы.
                        reason = RunStopReason.COMPLETED
                    elif controller.go_around_reason is not None:
                        # Уход на второй круг: заявка каналов снимается ниже (control_exception),
                        # руление не запрашиваем — ВС в воздухе, управление уходит пилоту.
                        print(f"[loop] уход на второй круг: {controller.go_around_reason}")
                        reason = RunStopReason.GO_AROUND
                        details = controller.go_around_reason
                    else:
                        reason = RunStopReason.COMPLETED
                    break

                if _lost_engagement(controller, sim):
                    reason = RunStopReason.ENGAGEMENT_LOST
                    details = f"{sim.backend_name}: {controller.segment.value}"
                    break

                last_time = current_time

            time.sleep(0.01)  # Снижение нагрузки на CPU

        if reason is RunStopReason.ERROR:
            reason = RunStopReason.COMPLETED
    except KeyboardInterrupt:
        trajectory = getattr(
            getattr(controller, "longitudinal_channel", None), "trajectory", None)
        if (
            controller.tick_id > 0
            and controller.segment is FlightSegment.TAXI
            and getattr(trajectory, "completion_rule", None) is CompletionRule.OPERATOR
        ):
            reason = RunStopReason.OPERATOR_COMPLETED
        else:
            reason = RunStopReason.INTERRUPTED
    finally:
        try:
            controller.control_exception()
        except Exception:
            logger.exception("Ошибка нейтрализации контроллера")
        try:
            shutdown_report = sim.shutdown()
        except Exception as exc:
            # Старый сторонний backend может ещё не реализовать новый контракт.
            logger.exception("Ошибка shutdown backend")
            shutdown_report = ShutdownReport(
                backend=getattr(sim, "backend_name", "unknown"),
                errors=(f"shutdown: {type(exc).__name__}: {exc}",),
            )
        if dashboard_state is not None:
            dashboard_state.cancel_pending_gain_updates()
        if recorder is not None:
            try:
                recorder.finish({
                    "tolerances": controller.tolerance_report,
                    "approach_criteria_a11": controller.approach_criteria.verdict(),
                    "stop_reason": reason.value,
                    "conditions_valid": getattr(sim, "conditions_valid", True),
                    "condition_matches": getattr(sim, "condition_matches", ()),
                    "shutdown": shutdown_report,
                })
            except Exception:
                logger.exception("Ошибка завершения журнала прогона")
        if dashboard_state is not None:
            try:
                dashboard_state.complete()
            except Exception:
                logger.exception("Ошибка перевода dashboard в completed replay")
    return RunResult(reason=reason, shutdown=shutdown_report, details=details)


def _lost_engagement(controller: ControllingSystem, sim: SimInterface) -> bool:
    """Снял ли стенд активность посреди прогона. → пора останавливаться.

    Без этой проверки потеря включения проходит **молча**: `ICSSim._to_outputs` перестаёт
    заявлять каналы (`ControlValidMask = 0`), контур продолжает считать и печатать команды, и
    прогон досчитывается до конца при нулевом авторитете органов — то есть засчитывается
    успешным пробег, которого не было. Терминальное окно (ниже 80 футов на заходе) сюда не
    попадает: там подтверждение удерживается самим автоматом.
    """
    if sim.engaged:
        return False
    details = getattr(getattr(sim, "engagement", None), "as_dict", lambda: {})()
    print(f"[loop] backend {sim.backend_name} снял управление на участке "
          f"{controller.segment.value}: {details}")
    return True


def main(
    preset: "str | Scenario | None" = None,
    ip: str | None = None,
    port: int | None = None,
    *,
    backend: str = "ics",
    start: str | None = None,
    xplane_root: str | None = None,
    aircraft_profile: str | None = None,
    runway_profile: str | None = None,
    run_id: str | None = None,
    scenario_json: str | None = None,
    dashboard: bool = False,
    dashboard_tune: bool = False,
    dashboard_hold_seconds: float = 300.0,
    control_mode: str = "classical",
    sft_air_checkpoint: str | None = None,
    sft_ground_checkpoint: str | None = None,
):
    """Точка входа: подключиться к стенду, выбрать пресет и провести полёт.

    `preset=None` — пресет **подбирается по телеметрии** стенда: по фактическим отказам и погоде
    выбирается сценарий, под который эти условия калибровались (`select_for_telemetry`). Это
    рабочий режим поставки: конфигурацию борта задаёт Заказчик, и угадывать её именем в
    командной строке незачем.

    Матричный запуск требует конкретную строку, а не шифр:

        python -m ismpu.runtime.loop --aircraft-profile mc21 --run-id Б.2.2/4

    Фактические условия стенда сверяются с выбранной строкой, но не используются для угадывания
    неоднозначных Б.2.* и Б.3.*.
    """
    if preset is not None and (run_id is not None or scenario_json is not None):
        raise ValueError("preset нельзя смешивать с run_id/scenario_json")
    if dashboard_hold_seconds < 0.0:
        raise ValueError("dashboard_hold_seconds must be non-negative")
    if control_mode not in {"classical", "sft-shadow", "sft-active"}:
        raise ValueError(f"unknown control mode: {control_mode}")
    if control_mode == "classical":
        if sft_air_checkpoint is not None or sft_ground_checkpoint is not None:
            raise ValueError("SFT checkpoints require sft-shadow or sft-active")
        sft_runtime = None
    elif sft_air_checkpoint is None and sft_ground_checkpoint is None:
        raise ValueError(f"{control_mode} requires at least one SFT checkpoint")
    loaded = load_scenario(
        scenario_json, legacy_aircraft_profile=aircraft_profile or "mc21") \
        if scenario_json is not None else None
    if loaded is not None:
        selected = rebind_matrix_run(loaded, run_id) if run_id is not None else loaded
    elif run_id is not None:
        selected = scenario_for_matrix_run(run_id)
    elif isinstance(preset, Scenario):
        selected = preset
    else:
        selected = resolve_scenario(preset) if preset is not None else None
    if selected is not None and selected.matrix_codes and not selected.matrix_runs:
        raise ValueError(
            "матричный сценарий нельзя запускать по одному шифру; "
            "укажите --run-id <шифр>/<номер>")
    sim = build_sim(
        backend,
        ip=ip,
        port=port,
        xplane_root=xplane_root,
        aircraft_profile=aircraft_profile,
        runway_profile=runway_profile,
    )
    controller = ControllingSystem(sim)
    profile_name = sim.aircraft_profile_name
    if control_mode != "classical":
        try:
            # Локальный импорт сохраняет torch опциональным для production-default classical.
            from ismpu.runtime.sft import SftRuntime
            sft_runtime = SftRuntime.from_checkpoints(
                mode=control_mode,
                air_path=sft_air_checkpoint,
                ground_path=sft_ground_checkpoint,
                backend=backend,
                aircraft_profile=profile_name,
            )
        except Exception:
            sim.close()
            raise

    if selected is not None:
        scenario = selected
    elif backend == "ics":
        frame = sim.read_telemetry()
        scenario = select_for_telemetry(
            frame,
            aircraft_profile=profile_name,
            segment=initial_segment(frame),
        )
        print(f"Сценарий подобран по телеметрии стенда: {scenario.scenario_id}")
    else:
        scenario = SCENARIOS["default"]
    if scenario.matrix_runs:
        if start is None:
            start = (
                "approach" if FlightSegment.APPROACH in scenario.matrix_runs
                else "taxi" if set(scenario.matrix_runs) == {FlightSegment.TAXI}
                else "rollout")
        print(f"Каталог матрицы SHA-256: {SOURCE_SHA256}")
        for segment, selected_run_id in scenario.matrix_runs.items():
            code = scenario.matrix_codes.get(segment, "")
            case = CASE_BY_CODE.get(code)
            print(
                f"Прогон матрицы {selected_run_id} [{segment.value}]: "
                f"{case.title if case else ''}")
        requested_segment = (
            FlightSegment.APPROACH if start == "approach"
            else FlightSegment.TAXI
            if set(scenario.matrix_runs) == {FlightSegment.TAXI}
            else FlightSegment.ROLLOUT
        )
        status = scenario.control_status(profile_name, requested_segment)
        if status is not ProfileStatus.ACCEPTED:
            print(
                f"ВНИМАНИЕ: статус профиля {status.value} — "
                "результат не допускается в SFT.")
        ambiguous = {
            item
            for code in scenario.matrix_codes.values()
            for item in CASE_BY_CODE[code].ambiguous_with
        }
        if ambiguous:
            print(f"По телеметрии неотличим от {', '.join(sorted(ambiguous))} — "
                  "проверяется именно явно выбранный run_id.")

    controller.bind_scenario(scenario, profile_name)
    recorder = RunRecorder(
        backend=sim.backend_name,
        aircraft_profile=sim.aircraft_profile_name,
        scenario=scenario,
        start=start,
        extra_metadata={
            "control_policy": control_mode,
            "sft_checkpoints": getattr(sft_runtime, "metadata", {}),
        },
    )
    print(f"Журнал прогона будет сохранён в: {recorder.directory}")
    dashboard_server = None
    dashboard_state = None
    if dashboard or dashboard_tune:
        from ismpu.gui.dashboard import DashboardServer, DashboardState
        dashboard_state = DashboardState(
            controller,
            sim=sim,
            scenario=scenario,
            recorder=recorder,
            tune_enabled=dashboard_tune,
            control_mode=control_mode,
        )
        dashboard_server = DashboardServer(dashboard_state).start()
        mode = "tuning" if dashboard_tune else "monitor-only"
        print(
            f"PID dashboard: http://{dashboard_server.address[0]}:"
            f"{dashboard_server.address[1]} ({mode})"
        )
    try:
        result = run(
            controller,
            sim,
            scenario,
            start=start,
            recorder=recorder,
            dashboard_state=dashboard_state,
            sft_runtime=sft_runtime,
        )
        if (
            dashboard_server is not None
            and result.reason is not RunStopReason.INTERRUPTED
            and dashboard_hold_seconds > 0.0
        ):
            print(
                f"Dashboard доступен ещё {dashboard_hold_seconds:g} с; "
                "Ctrl+C — закрыть"
            )
            try:
                time.sleep(dashboard_hold_seconds)
            except KeyboardInterrupt:
                pass
    finally:
        if dashboard_server is not None:
            dashboard_server.stop()
        sim.close()


def cli(argv: list[str] | None = None) -> int:
    """Единственная production CLI-точка для ICS и явного тестового X-Plane backend."""
    parser = argparse.ArgumentParser(description="ИСМПУ: полный полёт через ICS или X-Plane 12")
    parser.add_argument("preset", nargs="?", default=None)
    parser.add_argument("--backend", choices=("ics", "xplane"), default="ics")
    parser.add_argument("--start", choices=("approach", "rollout", "taxi"), default=None)
    parser.add_argument("--ip", default=None)
    parser.add_argument("--port", type=int, default=None)
    parser.add_argument("--xplane-root", default=None)
    parser.add_argument("--aircraft-profile", default="mc21")
    parser.add_argument("--runway-profile", default="uuee-06r")
    parser.add_argument("--run-id", default="Б.4.1")
    parser.add_argument(
        "--scenario-json", default=None,
        help="promoted scenario JSON; вместе с --run-id переносит overrides на строку того же шифра")
    parser.add_argument("--dashboard", action="store_true")
    parser.add_argument("--dashboard-tune", action="store_true")
    parser.add_argument("--dashboard-hold-seconds", type=float, default=300.0)
    parser.add_argument(
        "--control-mode", choices=("classical", "sft-shadow", "sft-active"),
        default="classical")
    parser.add_argument("--sft-air-checkpoint", default=None)
    parser.add_argument("--sft-ground-checkpoint", default=None)
    args = parser.parse_args(argv)
    if args.backend == "ics" and args.aircraft_profile is None:
        parser.error("для ICS требуется --aircraft-profile (например, mc21)")
    main(**vars(args))
    return 0


if __name__ == "__main__":
    # raise SystemExit(cli())

    main(
        preset=compose_matrix_scenario("AB-default", approach_run="A.1.2/1", rollout_run="B.1.1/1"),
        backend="ics",
        aircraft_profile="mc21",
        runway_profile="uuee-06r",
        # dashboard=True,
        # dashboard_tune=True,
    )

