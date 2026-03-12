"""
Константы для визуализатора REL670
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple, Any


# ========== ЦВЕТА ==========
@dataclass(frozen=True)
class Colors:
    """Цвета интерфейса"""
    # Основные цвета
    BLUE: str = '#2196F3'
    GREEN: str = '#4CAF50'
    ORANGE: str = '#FF9800'
    RED: str = '#F44336'
    PURPLE: str = '#9C27B0'
    BROWN: str = '#795548'
    CYAN: str = '#00BCD4'
    PINK: str = '#E91E63'

    # UI цвета
    ACCENT: str = '#2196F3'
    SECONDARY: str = '#666666'
    SEPARATOR: str = '#CCCCCC'
    TOOLTIP_BG: str = '#FFFFE0'
    ERROR: str = '#FF0000'
    SUCCESS: str = '#00AA00'
    WARNING: str = '#FFAA00'

    @classmethod
    def get_color_list(cls) -> List[Tuple[str, str]]:
        """Возвращает список цветов для выбора в UI"""
        return [
            (cls.BLUE, 'Синий'),
            (cls.GREEN, 'Зеленый'),
            (cls.ORANGE, 'Оранжевый'),
            (cls.RED, 'Красный'),
            (cls.PURPLE, 'Фиолетовый'),
            (cls.BROWN, 'Коричневый'),
            (cls.CYAN, 'Голубой'),
            (cls.PINK, 'Розовый')
        ]


# ========== ШРИФТЫ ==========
@dataclass(frozen=True)
class Fonts:
    """Настройки шрифтов"""
    FAMILY: str = 'Segoe UI'

    # Размеры
    SIZE_SMALL: int = 9
    SIZE_NORMAL: int = 10
    SIZE_LARGE: int = 12
    SIZE_TITLE: int = 14

    @classmethod
    def normal(cls) -> Tuple[str, int]:
        """Обычный шрифт"""
        return (cls.FAMILY, cls.SIZE_NORMAL)

    @classmethod
    def normal_bold(cls) -> Tuple[str, int, str]:
        """Жирный шрифт обычного размера"""
        return (cls.FAMILY, cls.SIZE_NORMAL, 'bold')

    @classmethod
    def small(cls) -> Tuple[str, int]:
        """Маленький шрифт"""
        return (cls.FAMILY, cls.SIZE_SMALL)

    @classmethod
    def large(cls) -> Tuple[str, int]:
        """Большой шрифт"""
        return (cls.FAMILY, cls.SIZE_LARGE)

    @classmethod
    def title(cls) -> Tuple[str, int, str]:
        """Шрифт для заголовков"""
        return (cls.FAMILY, cls.SIZE_TITLE, 'bold')


# ========== СТИЛИ ЛИНИЙ ==========
@dataclass(frozen=True)
class LineStyles:
    """Стили линий для графиков"""
    SOLID: str = '-'
    DASHED: str = '--'
    DASH_DOT: str = '-.'
    DOTTED: str = ':'

    @classmethod
    def get_styles_list(cls) -> List[Tuple[str, str]]:
        """Возвращает список стилей для выбора в UI"""
        return [
            (cls.SOLID, 'Сплошная'),
            (cls.DASHED, 'Пунктирная'),
            (cls.DASH_DOT, 'Штрих-пунктир'),
            (cls.DOTTED, 'Точечная')
        ]


# ========== НАПРАВЛЕННОСТЬ ==========
@dataclass(frozen=True)
class DirectionModes:
    """Режимы направленности зон"""
    FORWARD: str = "forward"
    REVERSE: str = "reverse"
    NON_DIRECTIONAL: str = "non-directional"

    @classmethod
    def get_display_names(cls) -> Dict[str, Tuple[str, str]]:
        """Возвращает словарь с отображаемыми названиями и иконками"""
        return {
            cls.FORWARD: ("Прямое", "↑"),
            cls.REVERSE: ("Обратное", "↓"),
            cls.NON_DIRECTIONAL: ("Ненаправленное", "↕")
        }

    @classmethod
    def get_list(cls) -> List[Tuple[str, str]]:
        """Возвращает список для выбора в UI"""
        display = cls.get_display_names()
        return [(mode, display[mode][0]) for mode in [cls.FORWARD, cls.REVERSE, cls.NON_DIRECTIONAL]]


# ========== ТИПЫ ПОВРЕЖДЕНИЙ ==========
@dataclass(frozen=True)
class FaultTypes:
    """Типы повреждений"""
    PH_PH: str = "Ph-Ph"
    PH_E: str = "Ph-E"
    SELECTOR: str = "Phase selector"

    @classmethod
    def get_display_names(cls) -> Dict[str, str]:
        """Возвращает словарь с отображаемыми названиями"""
        return {
            cls.PH_PH: "Ph-Ph (фаза-фаза)",
            cls.PH_E: "Ph-E (фаза-земля)",
            cls.SELECTOR: "PHS (фазовый селектор)"
        }

    @classmethod
    def get_list(cls) -> List[Tuple[str, str]]:
        """Возвращает список для выбора в UI"""
        display = cls.get_display_names()
        return [(code, display[code]) for code in [cls.PH_PH, cls.PH_E, cls.SELECTOR]]


# ========== ИНФОРМАЦИЯ ОБ УПРАВЛЕНИИ ==========
@dataclass(frozen=True)
class InfoItems:
    """Элементы информации об управлении"""
    MOUSE_DRAG: Tuple[str, str] = ("🖱️", "ЛКМ - перетащить")
    MOUSE_WHEEL: Tuple[str, str] = ("🖱️", "Колесо - масштаб")
    SEPARATOR: Tuple[str, str] = ("|", "")

    @classmethod
    def get_all(cls) -> List[Tuple[str, str]]:
        """Возвращает все элементы информации"""
        return [
            cls.MOUSE_DRAG,
            cls.SEPARATOR,
            cls.MOUSE_WHEEL
        ]


# ========== ПАРАМЕТРЫ ОТОБРАЖЕНИЯ ==========
@dataclass(frozen=True)
class DisplayConfig:
    """Параметры отображения графика"""
    FIGURE_SIZE: Tuple[int, int] = (10, 8)
    DPI: int = 100
    BACKGROUND_COLOR: str = '#F5F5F5'
    GRID_COLOR: str = '#E0E0E0'
    GRID_ALPHA: float = 0.3
    AXIS_COLOR: str = '#333333'

    # Размеры маркеров
    MARKER_SIZE: int = 50
    ZONE_ALPHA: float = 0.15
    ZONE_BORDER_WIDTH: int = 2


# ========== ПУТИ ==========
@dataclass(frozen=True)
class Paths:
    """Пути к файлам и директориям"""
    CONFIG_DIR: str = 'config'
    ZONES_CONFIG: str = 'config/zones.json'
    SETTINGS_CONFIG: str = 'config/settings.json'
    LOG_DIR: str = 'logs'


# Для обратной совместимости (если старый код использует прямые списки)
COLORS = Colors.get_color_list()
LINESTYLES = LineStyles.get_styles_list()
DIRECTION_MODES = DirectionModes.get_display_names()
FAULT_TYPES = FaultTypes.get_list()
INFO_ITEMS = InfoItems.get_all()