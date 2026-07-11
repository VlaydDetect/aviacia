"""Установка ЛА в сценарий касания на ВПП.

Мгновенно воссоздаёт этап touchdown с корректным физическим расчётом пробега.
Перенесено из main.ipynb без изменений (комментарий про 24C сохранён как в
оригинале, фактически используется порог из config.runway — 06R).
"""

import time

import numpy as np

from ismpu.io.xplane_connector import XPlaneConnectX
from ismpu.utils.converts import Converts
from ismpu.config.runway import RWY_START_LAT, RWY_START_LON, RWY_HEADING_TRUE, ELEVATION_MSL, ELEVATION_AIRCRAFT
from ismpu.io.datarefs import LOCAL_VX, LOCAL_VY, LOCAL_VZ, POS_P, POS_Q, POS_R


def setup_touchdown_uuee(xpc: XPlaneConnectX, speed_knots: float = 140.0, descent_rate_fpm: float = 120.0,
                         pitch_deg: float = 0.0):
    """
    Мгновенно воссоздает этап касания (touchdown) самолета на ВПП 24C аэропорта Шереметьево (UUEE)
    с последующим корректным физическим расчетом пробега, обжатия шасси и торможения.

    :param xpc: Экземпляр инициализированного класса XPlaneConnectX
    :param speed_knots: Путевая скорость самолета в узлах в момент касания
    :param descent_rate_fpm: Вертикальная скорость снижения в футах в минуту (положительное число)
    :param pitch_deg: Угол тангажа (типичный угол кабрирования при касании основных стоек)
    """
    # 1. Замораживаем физическое время симулятора.
    # Это необходимо, чтобы все сетевые пакеты (позиция, конфигурация, скорости)
    # применились в рамках одного расчетного кадра до начала обсчета физики.
    xpc.pauseSIM(True)
    time.sleep(0.1)  # Короткая пауза для стабилизации сетевого цикла X-Plane

    roll_deg = 0.0  # Крен равен нулю (крылья параллельны ВПП)

    # 3. Установка пространственного положения планера
    xpc.sendPOSI(lat=RWY_START_LAT, lon=RWY_START_LON, elev=ELEVATION_MSL + ELEVATION_AIRCRAFT, phi=roll_deg,
                 theta=pitch_deg,
                 psi_true=RWY_HEADING_TRUE)

    # 4. Конфигурация органов управления и механизации крыла
    # Тяга на малый газ (0.0), шасси выпущено (1), закрылки на максимум (1.0), спидбрейки армированы (-0.5)
    xpc.sendCTRL(lat_control=0.0, lon_control=0.0, rudder_control=0.0,
                 throttle=0.0, gear=1, flaps=1.0, speedbrakes=-0.5, park_brake=0.0)

    # 5. Расчет проекций векторов скоростей в локальной системе координат X-Plane (OpenGL)
    # Перевод исходных параметров в систему СИ (метры в секунду)
    v_ground_ms = speed_knots * Converts.KTS_TO_MS
    v_vertical_ms = -abs(descent_rate_fpm) * Converts.FTM_TO_MS  # Гарантируем отрицательное значение (движение вниз)

    # Перевод истинного курса в радианы
    heading_rad = np.radians(RWY_HEADING_TRUE)

    # Математический расчет проекций скоростей на оси декартовой сетки X-Plane:
    # Ось X направлена на Восток, ось Z — на Юг.
    local_vx = v_ground_ms * np.sin(heading_rad)
    local_vz = -v_ground_ms * np.cos(heading_rad)
    local_vy = v_vertical_ms

    # 6. Запись векторов скоростей напрямую в DataRefs через команду DREF
    xpc.sendDREF(LOCAL_VX, local_vx)
    xpc.sendDREF(LOCAL_VY, local_vy)
    xpc.sendDREF(LOCAL_VZ, local_vz)

    # Демпфирование (обнуление) угловых скоростей для предотвращения паразитного вращения планера
    xpc.sendDREF(POS_P, 0.0)
    xpc.sendDREF(POS_Q, 0.0)
    xpc.sendDREF(POS_R, 0.0)

    time.sleep(0.1)
