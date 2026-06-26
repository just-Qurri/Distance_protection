"""
Константы для визуализатора REL670 (оптимизированы)
"""

# Цвета с понятными названиями
COLORS = [
    ('#2196F3', 'Синий'),
    ('#4CAF50', 'Зеленый'),
    ('#FF9800', 'Оранжевый'),
    ('#F44336', 'Красный'),
    ('#9C27B0', 'Фиолетовый'),
    ('#795548', 'Коричневый'),
    ('#00BCD4', 'Голубой'),
    ('#E91E63', 'Розовый')
]

# Стили линий
LINESTYLES = [
    ('-', 'Сплошная'),
    ('--', 'Пунктирная'),
    ('-.', 'Штрих-пунктир'),
    (':', 'Точечная')
]

# Направленность
DIRECTION_MODES = {
    "forward": ("Прямое", "↑"),
    "reverse": ("Обратное", "↓"),
    "non-directional": ("Ненаправленное", "↕")
}

# Типы повреждений
FAULT_TYPES = [
    ("ph-ph", "Фаза-Фаза"),
    ("ph-e", "Фаза-Земля"),
    ("3-ph", "Трехфазное КЗ")
]

# Информация для верхней панели
INFO_ITEMS = [
    ("🖱️", "ЛКМ - перетаскивание"),
    ("|", ""),
    ("🖱️", "Колесо - масштаб"),
    ("|", ""),
    ("Ctrl+ЛКМ", "точечный маркер"),
    ("|", ""),
    ("ПКМ", "меню маркеров")
]

# ==================== ЗНАЧЕНИЯ ПО УМОЛЧАНИЮ ====================

DEFAULT_COMMON_SETTINGS = {
    'u_base': 115000.0,
    'i_base': 600.0,
    'i_secondary': 5.0,
    'u_secondary': 100.0,
    'angle_quad2': -15.0,
    'angle_quad4': 115.0,
    'angle_phs': 60.0,
    'name': "Общие настройки (U, I, angles)",
    'color': '#FF9800'
}

DEFAULT_SELECTOR_VALUES = {
    "x1": 37.0,
    "x0": 43.0,
    "rfpp_forward": 164.0,
    "rfpp_reverse": 164.0,
    "rfpe_forward": 135.0,
    "rfpe_reverse": 135.0,
    "rld_forward": 96.0,
    "rld_reverse": 96.0,
    "arg_load": 35.0,
    "arg_load_phph": 30.0,
    "arg_load_3ph": 30.0,
    "color": "#9C27B0",
    "style": "-",
    "opacity": 0.8,
    "load_enabled": True,
}

DEFAULT_SWING_VALUES = {
    "rld_out_fw": 96.0,
    "r1_li_n": 96.0,
    "arg_ld": 35.0,
    "rld_out_rv": 80.0,
    "rld_out_rv": 80.0,
    "arg_ld": 30.0,
    "color_zin": "#FF5722",
    "color_zout": "#FF9800",
    "style_zin": "-",
    "style_zout": "-",
    "opacity_zin": 0.6,
    "opacity_zout": 0.4,
    "show_zin": True,
    "show_zout": True,
    "load_enabled": True,
}

DEFAULT_POINTS_VALUES = {
    "enabled": True,
    "show_labels": True,
    "marker_size": 8.0,
}


def apply_defaults_to_object(obj, defaults: dict) -> None:
    """Применить значения по умолчанию к объекту"""
    for key, value in defaults.items():
        if hasattr(obj, key):
            setattr(obj, key, value)
