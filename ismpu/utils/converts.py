from dataclasses import dataclass


@dataclass
class Converts:
    KTS_TO_MS = 0.51444444444
    MS_TO_KTS = 1.94384449244

    FTM_TO_MS = 0.00507999999
    KTS_TO_FTM = 101.2686

    FT_TO_M = 0.3048

    @staticmethod
    def dms_to_float(degrees, minutes, seconds, direction='N'):
        # Базовый расчет
        float_val = degrees + (minutes / 60.0) + (seconds / 3600.0)

        # Меняем знак для Южной широты и Западной долготы
        if direction in ['S', 'W', 'Ю', 'З']:
            float_val = -float_val

        return round(float_val, 6)
