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

import time

from ismpu.control.system import ControllingSystem
from ismpu.control.flight import FlightSegment
from ismpu.config.constants import DT
from ismpu.io.ics_connector import LISTEN_IP_ANY
from ismpu.envs.ics_sim import ICSSim
from ismpu.config.run_matrix import CASE_BY_CODE
from ismpu.envs.scenario import (
    Scenario, SCENARIO_PRESETS, select_for_telemetry, resolve_preset,
)


def run(controller: ControllingSystem, sim: ICSSim, scenario: Scenario):
    """Прогоняет один полёт на уже настроенном контуре."""
    telemetry = sim.reset(scenario)

    # Участок определяется ДО рукопожатия: от него зависит, какой стимул гнать (переход в
    # `Approach` или в `Taxi`) — автомат включения выбирает его по той же телеметрии.
    segment = controller.begin_flight(telemetry)
    print(f"Участок по телеметрии стенда: {segment.value}")

    # Рукопожатие ДО управления: стенд принимает команды только после того, как получит
    # ModeAIReady=1 в течение выдержки и увидит переход ControlMode.
    print("Прогрев (ожидание, пока стенд примет управление)...")
    sim.warm_up()
    controller.last_telemetry = sim.read_telemetry()

    print("Управление включено.")
    last_time = time.time()
    try:
        while True:
            current_time = time.time()
            dt = current_time - last_time

            if dt >= DT:
                # Контур сам читает телеметрию и сам отправляет команды через sim.
                if controller.control_step(dt):
                    if controller.segment is FlightSegment.ROLLOUT:
                        # Пробег окончен — передаём управление в руление (ControlMode 3 → 4).
                        controller.hand_over_to_taxi()
                    elif controller.go_around_reason is not None:
                        # Уход на второй круг: заявка каналов снимается ниже (control_exception),
                        # руление не запрашиваем — ВС в воздухе, управление уходит пилоту.
                        print(f"[loop] уход на второй круг: {controller.go_around_reason}")
                    raise KeyboardInterrupt

                if _lost_engagement(controller, sim):
                    raise KeyboardInterrupt

                last_time = current_time

            time.sleep(0.01)  # Снижение нагрузки на CPU

    except KeyboardInterrupt:
        controller.control_exception()


def _lost_engagement(controller: ControllingSystem, sim: ICSSim) -> bool:
    """Снял ли стенд активность посреди прогона. → пора останавливаться.

    Без этой проверки потеря включения проходит **молча**: `ICSSim._to_outputs` перестаёт
    заявлять каналы (`ControlValidMask = 0`), контур продолжает считать и печатать команды, и
    прогон досчитывается до конца при нулевом авторитете органов — то есть засчитывается
    успешным пробег, которого не было. Терминальное окно (ниже 80 футов на заходе) сюда не
    попадает: там подтверждение удерживается самим автоматом.
    """
    if sim.engaged:
        return False
    print(f"[loop] стенд снял активность (AgentIsActive=0) на участке "
          f"{controller.segment.value}: {sim.engagement.as_dict()}")
    return True


def main(preset: "str | Scenario | None" = None, ip: str = LISTEN_IP_ANY, port: int = 3030):
    """Точка входа: подключиться к стенду, выбрать пресет и провести полёт.

    `preset=None` — пресет **подбирается по телеметрии** стенда: по фактическим отказам и погоде
    выбирается сценарий, под который эти условия калибровались (`select_for_telemetry`). Это
    рабочий режим поставки: конфигурацию борта задаёт Заказчик, и угадывать её именем в
    командной строке незачем.

    Явное имя (`"default"`, `"nws_fail"`, …, см. `SCENARIO_PRESETS`), **шифр матрицы прогонов**
    (`"Б.3.1"`, `"А.1.2"` — см. `config/run_matrix.py`) или готовый `Scenario` перекрывает подбор.
    Ручная проверка по матрице выглядит так:

        python -c "from ismpu.runtime.loop import main; main('Б.2.2')"

    Черновые пресеты матрицы автоматическим подбором **не берутся** — только по имени или шифру,
    и запуск об этом предупреждает.
    """
    sim = ICSSim(listen_ip=ip, listen_port=port)
    controller = ControllingSystem(sim)

    if isinstance(preset, Scenario):
        scenario = preset
    elif preset is None:
        scenario = select_for_telemetry(sim.read_telemetry())
        print(f"Сценарий подобран по телеметрии стенда: {scenario.scenario_id}")
    else:
        scenario = resolve_preset(preset)

    if scenario.matrix_code:
        case = CASE_BY_CODE.get(scenario.matrix_code)
        print(f"Прогон матрицы {scenario.matrix_code}: {case.title if case else ''}")
        if scenario.control.draft:
            print("ВНИМАНИЕ: пресет черновой — коэффициенты под этот шифр ещё не настроены.")
        if case and case.ambiguous_with:
            print(f"По телеметрии неотличим от {', '.join(case.ambiguous_with)} — "
                  f"убедитесь, что на стенде выставлен именно этот прогон.")

    scenario.apply_control(controller)   # PID пресета (отказы уточняются по телеметрии)
    run(controller, sim, scenario)


if __name__ == "__main__":
    main()
