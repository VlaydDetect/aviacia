from dataclasses import dataclass


@dataclass
class Converts:
    KTS_TO_MS = 0.51444444444
    MS_TO_KTS = 1.94384449244

    FT_TO_M = 0.3048

    FTM_TO_MS = FT_TO_M / 60.0   # фут/мин → м/с, точно (стенд шлёт VerticalSpeed в фут/мин)
    KTS_TO_FTM = 101.2686

    SM_TO_M = 1609.344       # статутная миля → метры
    M_TO_SM = 1.0 / 1609.344  # метры → статутные мили

    @staticmethod
    def dms_to_float(degrees, minutes, seconds, direction='N'):
        # Базовый расчет
        float_val = degrees + (minutes / 60.0) + (seconds / 3600.0)

        # Меняем знак для Южной широты и Западной долготы
        if direction in ['S', 'W', 'Ю', 'З']:
            float_val = -float_val

        return round(float_val, 6)
