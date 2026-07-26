"""Курируемый набор DataRef X-Plane 12, используемый ИСМПУ."""

# Навигация и кинематика
LATITUDE = "sim/flightmodel/position/latitude"
LONGITUDE = "sim/flightmodel/position/longitude"
GROUNDSPEED = "sim/flightmodel/position/groundspeed"
TRUE_PSI = "sim/flightmodel2/position/true_psi"
MAG_PSI = "sim/flightmodel/position/mag_psi"
MAG_TRACK = "sim/cockpit2/gauges/indicators/ground_track_mag_pilot"
MAGNETIC_VARIATION = "sim/flightmodel/position/magnetic_variation"
ELEVATION = "sim/flightmodel/position/elevation"
Y_AGL = "sim/flightmodel/position/y_agl"
TRUE_THETA = "sim/flightmodel/position/true_theta"
TRUE_PHI = "sim/flightmodel/position/true_phi"
LOCAL_VX = "sim/flightmodel/position/local_vx"
LOCAL_VY = "sim/flightmodel/position/local_vy"
LOCAL_VZ = "sim/flightmodel/position/local_vz"
POS_P = "sim/flightmodel/position/P"
POS_Q = "sim/flightmodel/position/Q"
POS_R = "sim/flightmodel/position/R"
PRAD = "sim/flightmodel/position/Prad"
QRAD = "sim/flightmodel/position/Qrad"
RRAD = "sim/flightmodel/position/Rrad"
G_AXIL = "sim/flightmodel/forces/g_axil"
G_NRML = "sim/flightmodel/forces/g_nrml"
G_SIDE = "sim/flightmodel/forces/g_side"

# Воздушные и ILS-сигналы
RADIO_ALT_FT = "sim/cockpit2/gauges/indicators/radio_altimeter_height_ft_pilot"
IAS_KTS = "sim/cockpit2/gauges/indicators/airspeed_kts_pilot"
TAS_KTS = "sim/cockpit2/gauges/indicators/true_airspeed_kts_pilot"
VVI_FPM = "sim/cockpit2/gauges/indicators/vvi_fpm_pilot"
NAV1_HDEF_DOTS = "sim/cockpit2/radios/indicators/nav1_hdef_dots_pilot"
NAV1_VDEF_DOTS = "sim/cockpit2/radios/indicators/nav1_vdef_dots_pilot"
NAV1_GS_FLAG = "sim/cockpit2/radios/indicators/nav1_flag_glideslope"
NAV1_FROM_TO = "sim/cockpit2/radios/indicators/nav1_flag_from_to_pilot"
NAV1_FREQ_HZ = "sim/cockpit2/radios/actuators/nav1_frequency_hz"
FLAP_RATIO = "sim/flightmodel2/controls/flap1_deploy_ratio"
FLAP_HANDLE_RATIO = "sim/cockpit2/controls/flap_handle_request_ratio"
GEAR_HANDLE_DOWN = "sim/cockpit2/controls/gear_handle_down"
SPEEDBRAKE_RATIO = "sim/cockpit2/controls/speedbrake_ratio"
GEAR_ON_GROUND = "sim/flightmodel2/gear/on_ground"

# Органы управления и override
YOKE_ROLL_RATIO = "sim/joystick/yoke_roll_ratio"
YOKE_PITCH_RATIO = "sim/joystick/yoke_pitch_ratio"
YOKE_HEADING_RATIO = "sim/joystick/yoke_heading_ratio"
LEFT_BRAKE_RATIO = "sim/cockpit2/controls/left_brake_ratio"
RIGHT_BRAKE_RATIO = "sim/cockpit2/controls/right_brake_ratio"
THROTTLE_RATIO = "sim/cockpit2/engine/actuators/throttle_ratio"
THROTTLE_COMMAND = "sim/flightmodel/engine/ENGN_thro"
OVERRIDE_ROLL = "sim/operation/override/override_joystick_roll"
OVERRIDE_PITCH = "sim/operation/override/override_joystick_pitch"
OVERRIDE_HEADING = "sim/operation/override/override_joystick_heading"
OVERRIDE_THROTTLES = "sim/operation/override/override_throttles"
OVERRIDE_TOE_BRAKES = "sim/operation/override/override_toe_brakes"

# Состояние и позиционирование
PAUSED = "sim/time/paused"
TOTAL_FLIGHT_TIME = "sim/time/total_flight_time_sec"
SIM_SPEED_ACTUAL = "sim/time/sim_speed_actual"

# Погода X-Plane 12
WX_CHANGE_MODE = "sim/weather/region/change_mode"
WX_UPDATE_IMMEDIATELY = "sim/weather/region/update_immediately"
WX_RUNWAY_FRICTION = "sim/weather/region/runway_friction"
WX_VARIABILITY_PCT = "sim/weather/region/variability_pct"
WX_RAIN_PERCENT = "sim/weather/region/rain_percent"
WX_VISIBILITY_SM = "sim/weather/region/visibility_reported_sm"
WX_SEALEVEL_TEMP_C = "sim/weather/region/sealevel_temperature_c"
WX_WIND_ALT_MSL_M = "sim/weather/region/wind_altitude_msl_m"
WX_WIND_SPEED_MSC = "sim/weather/region/wind_speed_msc"
WX_WIND_DIR_DEGT = "sim/weather/region/wind_direction_degt"
WX_SHEAR_SPEED_MSC = "sim/weather/region/shear_speed_msc"
WX_TURBULENCE = "sim/weather/region/turbulence"
WX_AC_WIND_SPEED_MSC = "sim/weather/aircraft/wind_now_speed_msc"
WX_AC_WIND_DIR_DEGT = "sim/weather/aircraft/wind_now_direction_degt"

# Отказы
FAILURE_ENUM_OK = 0
FAILURE_ENUM_INOP = 6
FAIL_ENGINE = "sim/operation/failures/rel_engfai"
FAIL_REVERSER = "sim/operation/failures/rel_revers"


COMMON_SUBSCRIPTIONS = (
    LATITUDE, LONGITUDE, GROUNDSPEED, TRUE_PSI, MAG_PSI, MAG_TRACK, MAGNETIC_VARIATION,
    ELEVATION, Y_AGL, TRUE_THETA, TRUE_PHI, PRAD, QRAD, RRAD,
    G_AXIL, G_NRML, G_SIDE, RADIO_ALT_FT, IAS_KTS, TAS_KTS, VVI_FPM,
    NAV1_HDEF_DOTS, NAV1_VDEF_DOTS, NAV1_GS_FLAG, NAV1_FROM_TO,
    NAV1_FREQ_HZ, FLAP_RATIO, TOTAL_FLIGHT_TIME, SIM_SPEED_ACTUAL,
    WX_AC_WIND_SPEED_MSC, WX_AC_WIND_DIR_DEGT,
)
