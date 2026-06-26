"""
Модель общих настроек (Singleton)
"""
from typing import Optional

# Значения по умолчанию для общих настроек
DEFAULT_COMMON_SETTINGS = {
    'u_base': 115000.0,
    'i_base': 600.0,
    'i_secondary': 5.0,
    'u_secondary': 100.0,
    'angle_quad2': -15.0,
    'angle_quad4': 115.0,
    'angle_phs': 60.0,
    'name': "Общие настройки (U, I, angles)",
    'color': '#FF9800',
    'color_name': "Оранжевый",
    'linestyle': '--',
    'opacity': 0.6,
    'enabled': True,
}


class CommonSettings:
    """
    Настройки для общих параметров (Singleton)
    """
    _instance: Optional['CommonSettings'] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if hasattr(self, '_initialized'):
            return
        for key, default in DEFAULT_COMMON_SETTINGS.items():
            setattr(self, key, kwargs.get(key, default))
        self._initialized = True

    @staticmethod
    def create_and_add(visualizer):
        """Создать и добавить общие настройки в визуализатор"""
        visualizer.add_common_settings(CommonSettings())
