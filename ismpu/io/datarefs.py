"""Именованные константы DataRef'ов X-Plane, используемых контуром.

Полный справочник DataRef'ов X-Plane 12 — в файле DataRefs.txt в корне репозитория
(колонки: имя, тип, writable, единица, описание). Здесь — только подмножество,
которое читает/пишет управляющий контур. Использование констант вместо строковых
литералов гарантирует, что имена в подписке (subscribeDREFs) и в чтении
current_dref_values совпадают.
"""

# --- Телеметрия (подписка, асинхронное чтение) ---
LATITUDE = "sim/flightmodel/position/latitude"
LONGITUDE = "sim/flightmodel/position/longitude"
GROUNDSPEED = "sim/flightmodel/position/groundspeed"
TRUE_PSI = "sim/flightmodel2/position/true_psi"

# --- Управляющие воздействия (запись) ---
YOKE_HEADING_RATIO = "sim/joystick/yoke_heading_ratio"
LEFT_BRAKE_RATIO = "sim/cockpit2/controls/left_brake_ratio"
RIGHT_BRAKE_RATIO = "sim/cockpit2/controls/right_brake_ratio"
THROTTLE_RATIO_L = "sim/cockpit2/engine/actuators/throttle_ratio[0]"
THROTTLE_RATIO_R = "sim/cockpit2/engine/actuators/throttle_ratio[1]"

# --- Установка сценария касания (запись векторов скоростей/угловых скоростей) ---
LOCAL_VX = "sim/flightmodel/position/local_vx"
LOCAL_VY = "sim/flightmodel/position/local_vy"
LOCAL_VZ = "sim/flightmodel/position/local_vz"
POS_P = "sim/flightmodel/position/P"
POS_Q = "sim/flightmodel/position/Q"
POS_R = "sim/flightmodel/position/R"
