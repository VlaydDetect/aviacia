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

    # Рукопожатие ДО управления: стенд заказчика принимает команды только после того, как
    # получит ModeAIReady=1 в течение двух секунд. На X-Plane это no-op.
    print("Прогрев (ожидание готовности симулятора)...")
    sim.warm_up()
    controller.last_telemetry = sim.read_telemetry()

    print("Запуск системы удержания оси ВПП...")
    last_time = time.time()
    try:
        while True:
            current_time = time.time()
            dt = current_time - last_time

            if dt >= DT:
                # Контур сам читает телеметрию и сам отправляет команды через sim.
                if controller.control_step(dt):
                    # Пробег окончен — передаём управление в руление (ControlMode 3 → 4).
                    controller.hand_over_to_taxi()
                    raise KeyboardInterrupt

                sim.update(controller.longitudinal_channel.traveled_distance_m)
                last_time = current_time

            time.sleep(0.01)  # Снижение нагрузки на CPU

    except KeyboardInterrupt:
        controller.control_exception()


def build_sim(backend: str, ip: str, port: int) -> SimInterface:
    """Бэкенд по имени: `"xplane"` — обучение/отладка, `"ics"` — стенд заказчика."""
    if backend == "ics":
        from ismpu.envs.sim_interface import ICSBackend
        return ICSBackend(listen_ip=ip, listen_port=port)
    if backend == "xplane":
        from ismpu.io.xplane_connector import XPlaneConnectX
        # reload_each_reset=False — лёгкий сброс только телепортом, как было в классическом цикле
        # (перезагрузка планера нужна обучению, чтобы не копился износ между эпизодами).
        return XPlaneBackend(xpc=XPlaneConnectX(ip=ip, port=port),
                             reload_each_reset=False, setup_view=True)
    raise ValueError(f"неизвестный бэкенд: {backend!r} (ожидается 'xplane' или 'ics')")


def main(preset: "str | Scenario" = "default", ip: str = "127.0.0.1", port: int = 49000,
         backend: str = "xplane"):
    """Точка входа: выбрать пресет по имени (или Scenario), настроить контур и запустить.

    Готовые пресеты: `SCENARIO_PRESETS` ("default", "nws_fail", "left_reverse_fail",
    "right_reverse_fail") — те же коэффициенты, что и раньше, плюс стандартная погода.

    `backend="ics"` запускает тот же контур против стенда заказчика (порт по умолчанию 3030):

        python -c "from ismpu.runtime.loop import main; main(backend='ics', port=3030)"
    """
    scenario = preset if isinstance(preset, Scenario) else SCENARIO_PRESETS[preset]

    sim = build_sim("ics", ip, port)
    controller = ControllingSystem(sim)

    scenario.apply_control(controller)   # PID + активация связанного отказа
    run(controller, sim, scenario)


if __name__ == "__main__":
    main()
