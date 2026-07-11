"""Управляющий цикл 20 Гц — замена run-ячейки main.ipynb.

Требует запущенного X-Plane 12 на 127.0.0.1:49000. Порядок: телепорт в точку
касания → снятие паузы → подписка на телеметрию → цикл `control_step` до
достижения скорости руления (или Ctrl-C), затем сброс органов управления.
"""

import time

from ismpu.io.xplane_connector import XPlaneConnectX
from ismpu.io.datarefs import LATITUDE, LONGITUDE, GROUNDSPEED, TRUE_PSI
from ismpu.control.system import ControllingSystem
from ismpu.config.constants import DT, FREQ
from ismpu.config.aircraft import A330_SETUP
from ismpu.config.scenarios import ScenarioConfig, NWS_FAIL
from ismpu.runtime.setup import setup_touchdown_uuee


def build_subscribed_drefs(freq: int = FREQ):
    """Список (DataRef, частота) для асинхронной подписки телеметрии."""
    return [
        (LATITUDE, freq),
        (LONGITUDE, freq),
        (GROUNDSPEED, freq),
        (TRUE_PSI, freq),
    ]


def run(controller: ControllingSystem, xpc: XPlaneConnectX, *, aircraft_setup: dict = A330_SETUP):
    """Прогоняет один эпизод пробега на уже настроенном контуре."""
    time.sleep(2)
    setup_touchdown_uuee(xpc, **aircraft_setup)

    print("Запуск системы удержания оси ВПП...")
    xpc.pauseSIM(False)

    time.sleep(1.2)
    print("Настройка подписки на телеметрию X-Plane...")
    xpc.subscribeDREFs(build_subscribed_drefs(), timeout=10.)
    last_time = time.time()
    try:
        while True:
            current_time = time.time()
            dt = current_time - last_time

            if dt >= DT:
                if controller.control_step(dt):
                    raise KeyboardInterrupt

                last_time = current_time

            time.sleep(0.01)  # Снижение нагрузки на CPU

    except KeyboardInterrupt:
        controller.control_exception()


def main(scenario: ScenarioConfig = NWS_FAIL, ip: str = "127.0.0.1", port: int = 49000):
    """Точка входа: создать соединение, настроить контур под сценарий, запустить."""
    xpc = XPlaneConnectX(ip=ip, port=port)
    controller = ControllingSystem(xpc=xpc)
    scenario.apply(controller)
    run(controller, xpc)


if __name__ == "__main__":
    main()
