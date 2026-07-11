"""Геометрия целевой ВПП и высоты установки ЛА.

Смена целевой полосы = правка констант в этом файле.
Текущая конфигурация: Шереметьево (UUEE), ВПП 06R.
"""

from ismpu.utils.converts import Converts

# UUEE 06R
RWY_START_LAT = 55.967296600
RWY_START_LON = 37.387516022
RWY_END_LAT = 55.975555420
RWY_END_LON = 37.442829132
RWY_HEADING_TRUE = 75  # Истинный курс полосы для инициализации

ELEVATION_MSL = 619.0 * Converts.FT_TO_M  # Высота порога над уровнем моря
ELEVATION_AIRCRAFT = 3 * Converts.FT_TO_M  # Высота ЛА над ВПП
