class Common_Settings:
    """
    Настройки для общих параметров
    """
    _instance = None
    u_base: float = 115000.0  # Базовое напряжение (В)
    i_base: float = 600.0  # Базовый ток (А)
    i_secondary: float = 5.0  # Вторичный ток (А)
    u_secondary: float = 100.0  # Вторичное напряжение (В)
    angle_quad2: float = -15.0  # Угол 2-го квадранта
    angle_quad4: float = 115.0  # Угол 4-го квадранта
    angle_phs: float = 60.0  # Угол PHS

    # Дополнительные параметры
    name: str = "Общие настройки (U, I)"
    enabled: bool = True
    color: str = '#FF9800'
    color_name: str = "Оранжевый"
    linestyle: str = '--'
    opacity: float = 0.6

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if not hasattr(self, '_initialized'):
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            self._initialized = True


_common_instance = None


def set_common_settings(settings):
    """Установить глобальные общие настройки"""
    global _common_instance
    _common_instance = settings


def get_common_settings():
    """Получить глобальные общие настройки"""
    return _common_instance
