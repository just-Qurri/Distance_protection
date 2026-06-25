"""
Модель общих настроек (Singleton)
"""

from typing import Optional


class CommonSettings:
    """
    Настройки для общих параметров (Singleton)
    """
    _instance: Optional['CommonSettings'] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
            self,
            u_base: float = 115000.0,
            i_base: float = 600.0,
            i_secondary: float = 5.0,
            u_secondary: float = 100.0,
            angle_quad2: float = -15.0,
            angle_quad4: float = 115.0,
            angle_phs: float = 60.0,
            name: str = "Общие настройки (U, I)",
            enabled: bool = True,
            color: str = '#FF9800',
            color_name: str = "Оранжевый",
            linestyle: str = '--',
            opacity: float = 0.6
    ):
        if hasattr(self, '_initialized'):
            return

        self.u_base = u_base
        self.i_base = i_base
        self.i_secondary = i_secondary
        self.u_secondary = u_secondary
        self.angle_quad2 = angle_quad2
        self.angle_quad4 = angle_quad4
        self.angle_phs = angle_phs
        self.name = name
        self.enabled = enabled
        self.color = color
        self.color_name = color_name
        self.linestyle = linestyle
        self.opacity = opacity
        self.type = "common"
        self._initialized = True


# Глобальный экземпляр для обратной совместимости
_common_instance: Optional[CommonSettings] = None


def set_common_settings(settings: CommonSettings) -> None:
    """Установить глобальные общие настройки"""
    global _common_instance
    _common_instance = settings


def get_common_settings() -> Optional[CommonSettings]:
    """Получить глобальные общие настройки"""
    return _common_instance
