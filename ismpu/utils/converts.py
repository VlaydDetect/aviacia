from dataclasses import dataclass
from typing import ClassVar, Literal


@dataclass
class Converts:
    """Коэффициенты перевода единиц на границе телеметрии и управления."""

    KTS_TO_MS: ClassVar[float] = 0.51444444444
    MS_TO_KTS: ClassVar[float] = 1.94384449244

    FT_TO_M: ClassVar[float] = 0.3048

    FTM_TO_MS: ClassVar[float] = FT_TO_M / 60.0  # VerticalSpeed: фут/мин → м/с
    KTS_TO_FTM: ClassVar[float] = 101.2686

    SM_TO_M: ClassVar[float] = 1609.344
    M_TO_SM: ClassVar[float] = 1.0 / 1609.344

    @staticmethod
    def dms_to_float(
        degrees: float,
        minutes: float,
        seconds: float,
        direction: Literal["N", "S", "E", "W", "С", "Ю", "В", "З"] = "N",
    ) -> float:
        """Преобразовать координату из градусов, минут и секунд в signed degrees."""
        float_val = degrees + (minutes / 60.0) + (seconds / 3600.0)

        if direction in ['S', 'W', 'Ю', 'З']:
            float_val = -float_val

        return round(float_val, 6)
