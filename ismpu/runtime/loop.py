"""Управляющий цикл 20 Гц против стенда заказчика — **весь интервал полёта**.

Порядок: подключение к стенду → рукопожатие под текущий участок → цикл `control_step` до
скорости руления (или Ctrl-C) → передача управления в руление и снятие заявки каналов.

Участок выбирается по первому кадру стенда (`control/flight.py`):

* ВС в воздухе выше 400 футов — начинаем с **захода**: рукопожатие `ControlMode 0 → 1`, дальше
  заход по ILS, выравнивание, касание, и в тот же момент передача на пробег (`1 → 3`);
* ВС на полосе — начинаем с **пробега** (или подхватываем уже идущий), как раньше.

Стенд слушается по UDP (по умолчанию на всех интерфейсах, порт 3030); адрес самого стенда
определяется из заголовка первого входящего пакета, задавать его не нужно.
"""

import argparse
import logging
import time

from ismpu.control.system import ControllingSystem
from ismpu.control.flight import FlightSegment, initial_segment
from ismpu.config.constants import DT
from ismpu.io.ics_connector import LISTEN_IP_ANY
from ismpu.envs.backend_factory import build_sim
from ismpu.envs.sim_interface import (
    RunResult, RunStopReason, ShutdownReport, SimInterface,
)
from ismpu.runtime.run_recorder import RunRecorder
from ismpu.config.run_matrix import CASE_BY_CODE
from ismpu.config.scenarios import (
    SCENARIOS, Scenario, resolve_scenario, select_for_telemetry,
    compose_matrix_scenario,
)

logger = logging.getLogger(__name__)


def run(controller: ControllingSystem, sim: SimInterface, scenario: Scenario, *,
        start: str | None = None, recorder: RunRecorder | None = None,
        dashboard_state=None) -> RunResult:
    """Прогоняет один полёт на уже настроенном контуре."""
    reason = RunStopReason.ERROR
    details: str | None = None
    shutdown_report: ShutdownReport | None = None
    run_started = time.monotonic()
    try:
        telemetry = sim.reset(scenario, start=start)

        # Участок определяется ДО рукопожатия: от него зависит стимул включения.
        segment = controller.begin_flight(telemetry)
        print(f"Участок по телеметрии стенда: {segment.value}")

        print("Прогрев (ожидание, пока стенд примет управление)...")
        sim.warm_up()
        controller.last_telemetry = sim.read_telemetry()
        run_started = time.monotonic()
        if recorder is not None:
            recorder.record(controller.last_telemetry, controller, elapsed_s=0.0)
        if dashboard_state is not None:
            dashboard_state.capture(elapsed_s=0.0)

        print("Управление включено.")
        last_time = time.monotonic()
        while True:
            current_time = time.monotonic()
            dt = current_time - last_time

            if dt >= DT:
                if dashboard_state is not None:
                    dashboard_state.apply_pending_gain_updates()
                # Контур сам читает телеметрию и сам отправляет команды через sim.
                finished = controller.control_step(dt)
                if recorder is not None and controller.last_telemetry is not None:
                    recorder.record(
                        controller.last_telemetry,
                        controller,
                        elapsed_s=time.monotonic() - run_started,
                    )
                if dashboard_state is not None:
                    dashboard_state.capture(
                        elapsed_s=time.monotonic() - run_started)
                if finished:
                    if controller.segment is FlightSegment.ROLLOUT:
                        # Пробег окончен — передаём управление в руление (ControlMode 3 → 4).
                        controller.hand_over_to_taxi()
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
    dashboard: bool = False,
    dashboard_tune: bool = False,
):
    """Точка входа: подключиться к стенду, выбрать пресет и провести полёт.

    `preset=None` — пресет **подбирается по телеметрии** стенда: по фактическим отказам и погоде
    выбирается сценарий, под который эти условия калибровались (`select_for_telemetry`). Это
    рабочий режим поставки: конфигурацию борта задаёт Заказчик, и угадывать её именем в
    командной строке незачем.

    Явное имя (`"default"`, `"nws_fail"`, …, см. `SCENARIOS`), **шифр матрицы прогонов**
    (`"Б.3.1"`, `"А.1.2"` — см. `config/run_matrix.py`) или готовый `Scenario` перекрывает подбор.
    Ручная проверка по матрице выглядит так:

        python -c "from ismpu.runtime.loop import main; main('Б.2.2')"

    Черновые пресеты матрицы автоматическим подбором **не берутся** — только по имени или шифру,
    и запуск об этом предупреждает.
    """
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

    if isinstance(preset, Scenario):
        scenario = preset
    elif preset is None and backend == "ics":
        frame = sim.read_telemetry()
        scenario = select_for_telemetry(
            frame,
            aircraft_profile=profile_name,
            segment=initial_segment(frame),
        )
        print(f"Сценарий подобран по телеметрии стенда: {scenario.scenario_id}")
    elif preset is None:
        scenario = SCENARIOS["default"]
    else:
        scenario = resolve_scenario(preset)

    if scenario.matrix_code:
        case = CASE_BY_CODE.get(scenario.matrix_code)
        print(f"Прогон матрицы {scenario.matrix_code}: {case.title if case else ''}")
        requested_segment = (
            FlightSegment.APPROACH if start == "approach" else FlightSegment.ROLLOUT)
        if scenario.is_draft(profile_name, requested_segment):
            print("ВНИМАНИЕ: пресет черновой — коэффициенты под этот шифр ещё не настроены.")
        if case and case.ambiguous_with:
            print(f"По телеметрии неотличим от {', '.join(case.ambiguous_with)} — "
                  f"убедитесь, что на стенде выставлен именно этот прогон.")

    controller.bind_scenario(scenario, profile_name)
    recorder = RunRecorder(
        backend=sim.backend_name,
        aircraft_profile=sim.aircraft_profile_name,
        scenario=scenario,
        start=start,
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
        )
        dashboard_server = DashboardServer(dashboard_state).start()
        mode = "tuning" if dashboard_tune else "monitor-only"
        print(
            f"PID dashboard: http://{dashboard_server.address[0]}:"
            f"{dashboard_server.address[1]} ({mode})"
        )
    try:
        run(
            controller,
            sim,
            scenario,
            start=start,
            recorder=recorder,
            dashboard_state=dashboard_state,
        )
    finally:
        if dashboard_server is not None:
            dashboard_server.stop()
        sim.close()


if __name__ == "__main__":
    # The generic matrix runtime remains available through ``main(...)`` for
    # X-Plane and ground-only experiments.  Live ICS approach flights use the
    # byte-for-byte port of the contour validated in ``aviacia_v2``: its
    # receive/update/send timing and 0 -> 1 handshake are part of the control
    # contract and must not be substituted by the generic backend adapter.
    from ismpu.working_ics.runner import live_main

    raise SystemExit(live_main())

    # Historical generic live entrypoint retained below as documentation.
    # time.sleep(2)
    # sim = build_sim(
    #     "ics",
    #     aircraft_profile="a330-300",
    #     runway_profile="uuee-06r",
    # )
    # controller = ControllingSystem(sim)
    # scenario = SCENARIOS["default"]
    # scenario.apply_control(controller)
    #
    # try:
    #     telemetry = sim.reset(scenario, start="approach")
    #
    #     segment = controller.begin_flight(telemetry)
    #     print(f"Участок по телеметрии стенда: {segment.value}")
    #
    #     print("Прогрев (ожидание, пока стенд примет управление)...")
    #     sim.warm_up()
    #     controller.last_telemetry = sim.read_telemetry()
    #     run_started = time.monotonic()
    #
    #     last_time = time.monotonic()
    #     while True:
    #         current_time = time.monotonic()
    #         dt = current_time - last_time
    #
    #         if dt >= DT:
    #             finished = controller.control_step(dt)
    #             if finished:
    #                 if controller.segment is FlightSegment.ROLLOUT:
    #                     # Пробег окончен — передаём управление в руление (ControlMode 3 → 4).
    #                     controller.hand_over_to_taxi()
    #                     reason = RunStopReason.COMPLETED
    #                 elif controller.go_around_reason is not None:
    #                     # Уход на второй круг: заявка каналов снимается ниже (control_exception),
    #                     # руление не запрашиваем — ВС в воздухе, управление уходит пилоту.
    #                     print(f"[loop] уход на второй круг: {controller.go_around_reason}")
    #                     reason = RunStopReason.GO_AROUND
    #                     details = controller.go_around_reason
    #                 else:
    #                     reason = RunStopReason.COMPLETED
    #                 break
    #
    #             if _lost_engagement(controller, sim):
    #                 reason = RunStopReason.ENGAGEMENT_LOST
    #                 details = f"{sim.backend_name}: {controller.segment.value}"
    #                 break
    #
    #             last_time = current_time
    #
    #         time.sleep(0.01)  # Снижение нагрузки на CPU
    # finally:
    #     sim.close()

    # parser = argparse.ArgumentParser(description="ИСМПУ: стенд ICS или X-Plane 12")
    # parser.add_argument("preset", nargs="?", default=None)
    # parser.add_argument("--backend", choices=("ics", "xplane"), default="xplane")
    # parser.add_argument("--start", choices=("approach", "rollout"), default=None)
    # parser.add_argument("--ip", default=None)
    # parser.add_argument("--port", type=int, default=None)
    # parser.add_argument("--xplane-root", default=None)
    # parser.add_argument("--aircraft-profile", default="a330-300")
    # parser.add_argument("--runway-profile", default="uuee-06r")
    # parser.add_argument("--dashboard", action="store_true")
    # parser.add_argument("--dashboard-tune", action="store_true")
    # args = parser.parse_args()

    main(
        preset=compose_matrix_scenario(
            scenario_id="full",
            approach_case="А.1.2",
            ground_case="Б.1.1",
        ),
        backend="ics",
        start="approach",
        aircraft_profile="mc21",
        runway_profile="uuee-06r",
    )
