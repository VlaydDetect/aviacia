"""Управляющий цикл 20 Гц против стенда заказчика.

Порядок: подключение к стенду → рукопожатие (`ModeAIReady` + переход `ControlMode`) → цикл
`control_step` до достижения скорости руления (или Ctrl-C), затем передача управления в руление
и сброс органов.

Стенд слушается по UDP (по умолчанию `127.0.0.1:3030`); адрес самого стенда определяется из
заголовка первого входящего пакета, задавать его не нужно.
"""

import time

from ismpu.control.system import ControllingSystem
from ismpu.config.constants import DT
from ismpu.envs.ics_sim import ICSSim
from ismpu.envs.scenario import Scenario, SCENARIO_PRESETS, select_for_telemetry


def run(controller: ControllingSystem, sim: ICSSim, scenario: Scenario):
    """Прогоняет один эпизод пробега на уже настроенном контуре."""
    controller.last_telemetry = sim.reset(scenario)

    # Рукопожатие ДО управления: стенд принимает команды только после того, как получит
    # ModeAIReady=1 в течение двух секунд и увидит переход ControlMode.
    print("Прогрев (ожидание, пока стенд примет управление)...")
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

                last_time = current_time

            time.sleep(0.01)  # Снижение нагрузки на CPU

    except KeyboardInterrupt:
        controller.control_exception()


def main(preset: "str | Scenario | None" = None, ip: str = "127.0.0.1", port: int = 3030):
    """Точка входа: подключиться к стенду, выбрать пресет и запустить пробег.

    `preset=None` — пресет **подбирается по телеметрии** стенда: по фактическим отказам и погоде
    выбирается сценарий, под который эти условия калибровались (`select_for_telemetry`). Это
    рабочий режим поставки: конфигурацию борта задаёт Заказчик, и угадывать её именем в
    командной строке незачем.

    Явное имя (`"default"`, `"nws_fail"`, `"left_reverse_fail"`, `"right_reverse_fail"`, …, см.
    `SCENARIO_PRESETS`) или готовый `Scenario` перекрывает подбор — для отладки конкретного
    режима.
    """
    sim = ICSSim(listen_ip=ip, listen_port=port)
    controller = ControllingSystem(sim)

    if isinstance(preset, Scenario):
        scenario = preset
    elif preset is None:
        scenario = select_for_telemetry(sim.read_telemetry())
        print(f"Сценарий подобран по телеметрии стенда: {scenario.scenario_id}")
    else:
        scenario = SCENARIO_PRESETS[preset]

    scenario.apply_control(controller)   # PID пресета (отказы уточняются по телеметрии)
    run(controller, sim, scenario)


if __name__ == "__main__":
    main()
