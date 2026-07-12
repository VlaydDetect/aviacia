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

# --- Погода X-Plane 12 (writable region; старые sim/weather/wind_* — DEPRECATED) ---
# Скалярные управляющие:
WX_CHANGE_MODE = "sim/weather/region/change_mode"               # int enum; 3 = Static (ручная, не real weather)
WX_UPDATE_IMMEDIATELY = "sim/weather/region/update_immediately"  # bool; 1 = применить сразу, не ждать 60 с
WX_WEATHER_PRESET = "sim/weather/region/weather_preset"         # int enum UI-пресета (Clear=0 … Storms=8)
WX_RUNWAY_FRICTION = "sim/weather/region/runway_friction"       # float enum 0..15 — прокси μ (см. RunwayCondition)
WX_VARIABILITY_PCT = "sim/weather/region/variability_pct"       # 0..1 — пространственная изменчивость погоды
WX_RAIN_PERCENT = "sim/weather/region/rain_percent"             # 0..1 — доля дождя
WX_VISIBILITY_SM = "sim/weather/region/visibility_reported_sm"  # statute miles
WX_SEALEVEL_TEMP_C = "sim/weather/region/sealevel_temperature_c"
WX_SEALEVEL_PRESSURE_PA = "sim/weather/region/sealevel_pressure_pas"

# Массивы по 13 атмосферным слоям — индексируются как "<dref>[i]":
WX_N_LAYERS = 13
WX_WIND_ALT_MSL_M = "sim/weather/region/wind_altitude_msl_m"    # [13] высоты слоёв, м MSL
WX_WIND_SPEED_MSC = "sim/weather/region/wind_speed_msc"         # [13] скорость ветра, м/с
WX_WIND_DIR_DEGT = "sim/weather/region/wind_direction_degt"     # [13] откуда дует, ° от истинного севера
WX_SHEAR_SPEED_MSC = "sim/weather/region/shear_speed_msc"       # [13] прирост от сдвига (порывы), м/с
WX_SHEAR_DIR_DEGT = "sim/weather/region/shear_direction_degt"   # [13] направление сдвига, °
WX_TURBULENCE = "sim/weather/region/turbulence"                 # [13] 0..10 — турбулентность/болтанка

# Фактический ветер у ЛА (read-only) — для диагностики/наблюдателя:
WX_AC_WIND_SPEED_MSC = "sim/weather/aircraft/wind_now_speed_msc"       # м/с
WX_AC_WIND_DIR_DEGT = "sim/weather/aircraft/wind_now_direction_degt"   # ° (откуда)

# --- Расширенная телеметрия (подписка SimInterface / XPlaneBackend) ---
ELEVATION = "sim/flightmodel/position/elevation"   # высота MSL, м
Y_AGL = "sim/flightmodel/position/y_agl"           # высота над рельефом, м
TRUE_THETA = "sim/flightmodel/position/true_theta"  # тангаж, °
TRUE_PHI = "sim/flightmodel/position/true_phi"      # крен, °
PRAD = "sim/flightmodel/position/Prad"              # угловая скорость крена, рад/с
QRAD = "sim/flightmodel/position/Qrad"              # угловая скорость тангажа, рад/с
RRAD = "sim/flightmodel/position/Rrad"              # угловая скорость рыскания, рад/с
G_AXIL = "sim/flightmodel/forces/g_axil"            # продольная перегрузка, g
G_NRML = "sim/flightmodel/forces/g_nrml"            # нормальная перегрузка, g
G_SIDE = "sim/flightmodel/forces/g_side"            # боковая перегрузка, g

# --- Инъекция отказов (X-Plane failure_enum: 0 = исправно, 6 = отказ немедленно) ---
FAILURE_ENUM_OK = 0
FAILURE_ENUM_INOP = 6
FAIL_ENGINE = "sim/operation/failures/rel_engfai"    # + индекс двигателя (0 = левый, 1 = правый)
FAIL_REVERSER = "sim/operation/failures/rel_revers"  # + индекс двигателя
