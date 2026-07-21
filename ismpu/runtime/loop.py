"""Управляющий цикл 20 Гц — замена run-ячейки main.ipynb.

Требует запущенного X-Plane 12 на 127.0.0.1:49000. Порядок: телепорт в точку
касания → снятие паузы → подписка на телеметрию → цикл `control_step` до
достижения скорости руления (или Ctrl-C), затем сброс органов управления.
"""

import time

from ismpu.io.xplane_connector import XPlaneConnectX
from ismpu.control.system import ControllingSystem
from ismpu.config.constants import DT
from ismpu.envs.sim_interface import SimInterface, XPlaneBackend
from ismpu.envs.scenario import Scenario, SCENARIO_PRESETS


def run(controller: ControllingSystem, sim: SimInterface, scenario: Scenario):
    """Прогоняет один эпизод пробега на уже настроенном контуре по сценарию.

    Телепорт, погода и подписка на телеметрию — забота бэкенда (`SimInterface.reset`), а не
    цикла: раньше здесь был свой список подписки из четырёх DataRef'ов, расходившийся с
    двадцатью одним у `XPlaneBackend`.
    """
    controller.last_telemetry = sim.reset(scenario)
    print("Запуск системы удержания оси ВПП...")

    last_time = time.time()
    try:
        while True:
            current_time = time.time()
            dt = current_time - last_time

            if dt >= DT:
                # Контур сам читает телеметрию и сам отправляет команды через sim.
                if controller.control_step(dt):
                    raise KeyboardInterrupt

                sim.update(controller.longitudinal_channel.traveled_distance_m)
                last_time = current_time

            time.sleep(0.01)  # Снижение нагрузки на CPU

    except KeyboardInterrupt:
        controller.control_exception()


def main(preset: "str | Scenario" = "nws_fail", ip: str = "127.0.0.1", port: int = 49000):
    """Точка входа: выбрать пресет по имени (или Scenario), настроить контур и запустить.

    Готовые пресеты: `SCENARIO_PRESETS` ("default", "nws_fail", "left_reverse_fail",
    "right_reverse_fail") — те же коэффициенты, что и раньше, плюс стандартная погода.
    """
    scenario = preset if isinstance(preset, Scenario) else SCENARIO_PRESETS[preset]

    xpc = XPlaneConnectX(ip=ip, port=port)
    # reload_each_reset=False — лёгкий сброс только телепортом, как было в классическом цикле
    # (перезагрузка планера нужна обучению, чтобы не копился износ между эпизодами).
    sim = XPlaneBackend(xpc=xpc, reload_each_reset=False, setup_view=True)
    controller = ControllingSystem(sim)

    scenario.apply_control(controller)   # PID + активация связанного отказа
    run(controller, sim, scenario)


if __name__ == "__main__":
    main()
