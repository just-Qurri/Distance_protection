# -*- coding: utf-8 -*-
"""
Модуль для управления интерактивными маркерами на графике
"""

import tkinter as tk
from typing import Optional, List, Dict, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import numpy as np

from ui.constants import Colors, Fonts


class MarkerType(Enum):
    """Типы маркеров"""
    AXIS_R = 'r'
    AXIS_X = 'x'
    POINT = 'point'
    VERTICAL_LINE = 'v'
    HORIZONTAL_LINE = 'h'


class CursorType(Enum):
    """Типы курсоров"""
    DEFAULT = "arrow"
    H_RESIZE = "sb_h_double_arrow"
    V_RESIZE = "sb_v_double_arrow"
    MOVE = "fleur"
    CROSS = "cross"


@dataclass
class MarkerConfig:
    """Конфигурация отображения маркеров"""
    # Основные измерительные линии
    vertical_line: Dict[str, Any] = field(default_factory=lambda: {
        'color': Colors.RED,
        'linestyle': '--',
        'linewidth': 2,
        'alpha': 0.7,
        'picker': True,
        'pickradius': 10
    })

    horizontal_line: Dict[str, Any] = field(default_factory=lambda: {
        'color': Colors.BLUE,
        'linestyle': '--',
        'linewidth': 2,
        'alpha': 0.7,
        'picker': True,
        'pickradius': 10
    })

    # Маркеры на осях
    axis_r_marker: Dict[str, Any] = field(default_factory=lambda: {
        'color': Colors.ORANGE,
        'linestyle': '-',
        'linewidth': 2,
        'alpha': 0.8,
        'picker': True,
        'pickradius': 10
    })

    axis_x_marker: Dict[str, Any] = field(default_factory=lambda: {
        'color': Colors.PURPLE,
        'linestyle': '-',
        'linewidth': 2,
        'alpha': 0.8,
        'picker': True,
        'pickradius': 10
    })

    # Точечные маркеры
    point_marker: Dict[str, Any] = field(default_factory=lambda: {
        'x_color': Colors.GREEN,
        'o_color': Colors.GREEN,
        'size': 12,
        'markeredgewidth': 2,
        'picker': True,
        'pickradius': 10
    })

    # Текстовые метки
    text: Dict[str, Any] = field(default_factory=lambda: {
        'fontsize': 8,
        'fontweight': 'bold',
        'bbox': {
            'boxstyle': 'round,pad=0.2',
            'facecolor': 'white',
            'alpha': 0.7
        },
        'picker': True,
        'pickradius': 10
    })

    # Измерительный текст
    measure_text: Dict[str, Any] = field(default_factory=lambda: {
        'fontsize': 10,
        'fontweight': 'bold',
        'bbox': {
            'boxstyle': 'round',
            'facecolor': 'white',
            'edgecolor': Colors.SEPARATOR,
            'alpha': 0.9
        }
    })

    # Позиционирование
    text_offset: float = 0.95  # Коэффициент для позиционирования текста у границ

    # Перетаскивание
    pickradius: int = 10


@dataclass
class MarkerState:
    """Состояние маркеров для сохранения/восстановления"""
    axis_markers_r: List[Dict[str, float]] = field(default_factory=list)
    axis_markers_x: List[Dict[str, float]] = field(default_factory=list)
    point_markers: List[Dict[str, Union[float, str]]] = field(default_factory=list)
    line_position_r: float = 0.0
    line_position_x: float = 0.0


class AxisRMarker:
    """Маркер на оси R (вертикальная линия)"""

    def __init__(self, ax, x: float, config: MarkerConfig):
        self.ax = ax
        self.x = x
        self.config = config

        # Создаем линию
        self.line = ax.axvline(x=x, **config.axis_r_marker)

        # Создаем текстовую метку
        self.text = self._create_text()

    def _create_text(self):
        """Создание текстовой метки"""
        y_top = self.ax.get_ylim()[1] * self.config.text_offset
        text = self.ax.text(
            self.x, y_top, f' {self.x:.2f}',
            rotation=90,
            verticalalignment='top',
            **self.config.text
        )
        text.set_picker(self.config.pickradius)
        return text

    def update_position(self, x: float):
        """Обновление позиции маркера"""
        self.x = x
        self.line.set_xdata([x, x])

        # Обновляем текст
        y_top = self.ax.get_ylim()[1] * self.config.text_offset
        self.text.set_position((x, y_top))
        self.text.set_text(f' {x:.2f}')

    def update_text_position(self):
        """Обновление позиции текста после изменения масштаба"""
        y_top = self.ax.get_ylim()[1] * self.config.text_offset
        self.text.set_position((self.x, y_top))

    def contains_artist(self, artist) -> bool:
        """Проверка, принадлежит ли artist этому маркеру"""
        return artist is self.line or artist is self.text

    def to_dict(self) -> Dict[str, float]:
        """Сериализация в словарь"""
        return {'x': self.x}


class AxisXMarker:
    """Маркер на оси X (горизонтальная линия)"""

    def __init__(self, ax, y: float, config: MarkerConfig):
        self.ax = ax
        self.y = y
        self.config = config

        # Создаем линию
        self.line = ax.axhline(y=y, **config.axis_x_marker)

        # Создаем текстовую метку
        self.text = self._create_text()

    def _create_text(self):
        """Создание текстовой метки"""
        x_right = self.ax.get_xlim()[1] * self.config.text_offset
        text = self.ax.text(
            x_right, self.y, f'{self.y:.2f} ',
            horizontalalignment='right',
            verticalalignment='center',
            **self.config.text
        )
        text.set_picker(self.config.pickradius)
        return text

    def update_position(self, y: float):
        """Обновление позиции маркера"""
        self.y = y
        self.line.set_ydata([y, y])

        # Обновляем текст
        x_right = self.ax.get_xlim()[1] * self.config.text_offset
        self.text.set_position((x_right, y))
        self.text.set_text(f'{y:.2f} ')

    def update_text_position(self):
        """Обновление позиции текста после изменения масштаба"""
        x_right = self.ax.get_xlim()[1] * self.config.text_offset
        self.text.set_position((x_right, self.y))

    def contains_artist(self, artist) -> bool:
        """Проверка, принадлежит ли artist этому маркеру"""
        return artist is self.line or artist is self.text

    def to_dict(self) -> Dict[str, float]:
        """Сериализация в словарь"""
        return {'y': self.y}


class PointMarker:
    """Точечный маркер"""

    def __init__(self, ax, x: float, y: float, color: str, config: MarkerConfig):
        self.ax = ax
        self.x = x
        self.y = y
        self.color = color
        self.config = config

        # Создаем линии маркера (крестик и кружок)
        self.lines = self._create_lines()

        # Создаем текстовую метку
        self.text = self._create_text()

    def _create_lines(self):
        """Создание линий маркера"""
        line1 = self.ax.plot(
            [self.x], [self.y], 'x',
            color=self.color,
            markersize=self.config.point_marker['size'],
            markeredgewidth=self.config.point_marker['markeredgewidth'],
            picker=self.config.point_marker['picker'],
            pickradius=self.config.point_marker['pickradius']
        )[0]

        line2 = self.ax.plot(
            [self.x], [self.y], 'o',
            color=self.color,
            markersize=self.config.point_marker['size'] // 2,
            markerfacecolor='none',
            markeredgewidth=self.config.point_marker['markeredgewidth'],
            picker=self.config.point_marker['picker'],
            pickradius=self.config.point_marker['pickradius']
        )[0]

        return [line1, line2]

    def _create_text(self):
        """Создание текстовой метки"""
        text_config = self.config.text.copy()
        text_config['bbox'] = text_config['bbox'].copy()
        text_config['bbox']['edgecolor'] = self.color

        text = self.ax.text(
            self.x, self.y, f'({self.x:.2f}, {self.y:.2f})',
            **text_config
        )
        text.set_picker(self.config.pickradius)
        return text

    def update_position(self, x: float, y: float):
        """Обновление позиции маркера"""
        self.x = x
        self.y = y

        for line in self.lines:
            line.set_data([x], [y])

        self.text.set_position((x, y))
        self.text.set_text(f'({x:.2f}, {y:.2f})')

    def update_text_position(self):
        """Обновление позиции текста после изменения масштаба"""
        self.text.set_position((self.x, self.y))

    def contains_artist(self, artist) -> bool:
        """Проверка, принадлежит ли artist этому маркеру"""
        return artist in self.lines or artist is self.text

    def to_dict(self) -> Dict[str, Union[float, str]]:
        """Сериализация в словарь"""
        return {
            'x': self.x,
            'y': self.y,
            'color': self.color
        }


class MeasurementLines:
    """Основные измерительные линии"""

    def __init__(self, ax, config: MarkerConfig):
        self.ax = ax
        self.config = config

        self.vertical_line = ax.axvline(x=0, **config.vertical_line)
        self.horizontal_line = ax.axhline(y=0, **config.horizontal_line)

        self.measure_text = self._create_measure_text()

    def _create_measure_text(self):
        """Создание текста с измерениями"""
        text = self.ax.text(
            0.02, 0.98, 'R = 0.00 Ω\nX = 0.00 Ω',
            transform=self.ax.transAxes,
            verticalalignment='top',
            **self.config.measure_text
        )
        text.set_picker(self.config.pickradius)
        return text

    def update_position(self, r: float, x: float):
        """Обновление позиций линий"""
        self.vertical_line.set_xdata([r, r])
        self.horizontal_line.set_ydata([x, x])
        self.measure_text.set_text(f'R = {r:.2f} Ω\nX = {x:.2f} Ω')

    def contains_artist(self, artist) -> bool:
        """Проверка, принадлежит ли artist линиям"""
        return artist in [self.vertical_line, self.horizontal_line, self.measure_text]


class MarkerManager:
    """Класс для управления всеми типами маркеров"""

    _instance: Optional['MarkerManager'] = None
    _initialized: bool = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, ax=None, canvas=None, visualizer=None, config: Optional[MarkerConfig] = None):
        """
        Инициализация менеджера маркеров
        """
        if MarkerManager._initialized:
            self._update_references(ax, canvas, visualizer)
            return

        self.ax = ax
        self.canvas = canvas
        self.viz = visualizer
        self.config = config or MarkerConfig()

        # Состояние
        self._state = MarkerState()

        # Коллекции маркеров
        self._axis_markers_r: List[AxisRMarker] = []
        self._axis_markers_x: List[AxisXMarker] = []
        self._point_markers: List[PointMarker] = []

        # Измерительные линии
        self._measurement_lines: Optional[MeasurementLines] = None

        # Состояние перетаскивания
        self._dragged_object: Optional[Union[str, Tuple[str, int]]] = None

        if ax is not None:
            self._create_measurement_lines()
            self._restore_from_state()

        MarkerManager._initialized = True

    def _update_references(self, ax, canvas, visualizer):
        """Обновление ссылок на объекты"""
        if ax is not None:
            self.ax = ax
        if canvas is not None:
            self.canvas = canvas
        if visualizer is not None:
            self.viz = visualizer

    def _create_measurement_lines(self):
        """Создание основных измерительных линий"""
        self._measurement_lines = MeasurementLines(self.ax, self.config)

    # ========== Публичные методы для добавления маркеров ==========

    def add_axis_marker_r(self, x: float) -> AxisRMarker:
        """Добавление маркера на ось R"""
        marker = AxisRMarker(self.ax, x, self.config)
        self._axis_markers_r.append(marker)
        self.save_state()
        self._redraw()
        return marker

    def add_axis_marker_x(self, y: float) -> AxisXMarker:
        """Добавление маркера на ось X"""
        marker = AxisXMarker(self.ax, y, self.config)
        self._axis_markers_x.append(marker)
        self.save_state()
        self._redraw()
        return marker

    def add_point_marker(self, x: float, y: float, color: str = Colors.GREEN) -> PointMarker:
        """Добавление точечного маркера"""
        if x is None or y is None:
            raise ValueError("Coordinates cannot be None")

        marker = PointMarker(self.ax, x, y, color, self.config)
        self._point_markers.append(marker)
        self.save_state()
        self._redraw()
        return marker

    # ========== Обработка событий ==========

    def handle_pick_event(self, event) -> bool:
        """Обработка события выбора объекта"""
        if not hasattr(event, 'artist'):
            return False

        artist = event.artist

        # Проверяем измерительные линии
        if self._measurement_lines and self._measurement_lines.contains_artist(artist):
            if artist is self._measurement_lines.vertical_line or artist is self._measurement_lines.measure_text:
                self._dragged_object = 'v'
                self._set_cursor(CursorType.H_RESIZE)
            elif artist is self._measurement_lines.horizontal_line:
                self._dragged_object = 'h'
                self._set_cursor(CursorType.V_RESIZE)
            return True

        # Проверяем маркеры на оси R
        for i, marker in enumerate(self._axis_markers_r):
            if marker.contains_artist(artist):
                self._dragged_object = ('r', i)
                self._set_cursor(CursorType.H_RESIZE)
                return True

        # Проверяем маркеры на оси X
        for i, marker in enumerate(self._axis_markers_x):
            if marker.contains_artist(artist):
                self._dragged_object = ('x', i)
                self._set_cursor(CursorType.V_RESIZE)
                return True

        # Проверяем точечные маркеры
        for i, marker in enumerate(self._point_markers):
            if marker.contains_artist(artist):
                self._dragged_object = ('point', i)
                self._set_cursor(CursorType.MOVE)
                return True

        return False

    def handle_mouse_motion(self, event) -> bool:
        """Обработка движения мыши для перетаскивания"""
        if not event.inaxes or self._dragged_object is None:
            return False

        # Перетаскивание измерительных линий
        if self._dragged_object == 'v' and event.xdata is not None:
            self._measurement_lines.update_position(event.xdata, self._state.line_position_x)
            self._state.line_position_r = event.xdata
            self.save_state()
            self._redraw()
            return True

        elif self._dragged_object == 'h' and event.ydata is not None:
            self._measurement_lines.update_position(self._state.line_position_r, event.ydata)
            self._state.line_position_x = event.ydata
            self._ave_state()
            self._redraw()
            return True

        # Перетаскивание маркеров
        elif isinstance(self._dragged_object, tuple):
            marker_type, idx = self._dragged_object

            if marker_type == 'r' and event.xdata is not None and idx < len(self._axis_markers_r):
                self._axis_markers_r[idx].update_position(event.xdata)
                self.save_state()
                self._redraw()
                return True

            elif marker_type == 'x' and event.ydata is not None and idx < len(self._axis_markers_x):
                self._axis_markers_x[idx].update_position(event.ydata)
                self.save_state()
                self._redraw()
                return True

            elif marker_type == 'point' and idx < len(self._point_markers):
                if event.xdata is not None and event.ydata is not None:
                    self._point_markers[idx].update_position(event.xdata, event.ydata)
                    self.save_state()
                    self._redraw()
                    return True

        return False

    def handle_mouse_release(self, event) -> bool:
        """Обработка отпускания кнопки мыши"""
        if self._dragged_object is not None:
            self._dragged_object = None
            self._set_cursor(CursorType.DEFAULT)
            self._redraw()
            return True
        return False

    # ========== Обновление и утилиты ==========

    def update_marker_positions(self):
        """Обновление позиций текста маркеров после изменения масштаба"""
        for marker in self._axis_markers_r:
            marker.update_text_position()

        for marker in self._axis_markers_x:
            marker.update_text_position()

        for marker in self._point_markers:
            marker.update_text_position()

        self._redraw()

    def find_marker_at_position(self, x: float, y: float, tolerance: float = 2.0) -> Optional[Tuple[str, int]]:
        """Поиск маркера в заданной позиции"""
        # Проверяем маркеры на оси R
        for i, marker in enumerate(self._axis_markers_r):
            if abs(marker.x - x) < tolerance:
                return ('r', i)

        # Проверяем маркеры на оси X
        for i, marker in enumerate(self._axis_markers_x):
            if abs(marker.y - y) < tolerance:
                return ('x', i)

        # Проверяем точечные маркеры
        for i, marker in enumerate(self._point_markers):
            if abs(marker.x - x) < tolerance and abs(marker.y - y) < tolerance:
                return ('point', i)

        return None

    def clear_all_markers(self):
        """Очистка всех маркеров"""
        # Удаляем графические объекты
        for marker in self._axis_markers_r + self._axis_markers_x:
            marker.line.remove()
            marker.text.remove()

        for marker in self._point_markers:
            for line in marker.lines:
                line.remove()
            marker.text.remove()

        # Очищаем списки
        self._axis_markers_r.clear()
        self._axis_markers_x.clear()
        self._point_markers.clear()

        # Сбрасываем состояние
        self._state = MarkerState()
        self.save_state()
        self._redraw()

    def get_stats(self) -> Dict[str, int]:
        """Получение статистики маркеров"""
        return {
            'point': len(self._point_markers),
            'r': len(self._axis_markers_r),
            'x': len(self._axis_markers_x)
        }

    # ========== Приватные методы ==========

    def _set_cursor(self, cursor_type: CursorType):
        """Установка курсора"""
        if self.canvas:
            self.canvas.get_tk_widget().configure(cursor=cursor_type.value)

    def _redraw(self):
        """Перерисовка канваса"""
        if self.canvas:
            self.canvas.draw_idle()

    def save_state(self):
        """Сохранение состояния маркеров"""
        self._state.axis_markers_r = [m.to_dict() for m in self._axis_markers_r]
        self._state.axis_markers_x = [m.to_dict() for m in self._axis_markers_x]
        self._state.point_markers = [m.to_dict() for m in self._point_markers]

        if self._measurement_lines:
            # Получаем позиции из линий
            r_pos = self._measurement_lines.vertical_line.get_xdata()[0]
            x_pos = self._measurement_lines.horizontal_line.get_ydata()[0]
            self._state.line_position_r = r_pos
            self._state.line_position_x = x_pos

    def _restore_from_state(self):
        """Восстановление маркеров из сохраненного состояния"""
        # Восстанавливаем позиции измерительных линий
        if self._state.line_position_r != 0.0 or self._state.line_position_x != 0.0:
            self._measurement_lines.update_position(
                self._state.line_position_r,
                self._state.line_position_x
            )

        # Восстанавливаем маркеры на оси R
        for data in self._state.axis_markers_r:
            self.add_axis_marker_r(data['x'])

        # Восстанавливаем маркеры на оси X
        for data in self._state.axis_markers_x:
            self.add_axis_marker_x(data['y'])

        # Восстанавливаем точечные маркеры
        for data in self._state.point_markers:
            self.add_point_marker(data['x'], data['y'], data.get('color', Colors.GREEN))

    # ========== Свойства для доступа к данным ==========

    @property
    def axis_markers_r(self) -> List[Dict[str, float]]:
        """Получение данных маркеров на оси R (для совместимости)"""
        return [{'x': m.x} for m in self._axis_markers_r]

    @property
    def axis_markers_x(self) -> List[Dict[str, float]]:
        """Получение данных маркеров на оси X (для совместимости)"""
        return [{'y': m.y} for m in self._axis_markers_x]

    @property
    def point_markers(self) -> List[Dict[str, Union[float, str]]]:
        """Получение данных точечных маркеров (для совместимости)"""
        return [{'x': m.x, 'y': m.y, 'color': m.color} for m in self._point_markers]

    @property
    def line_position_r(self) -> float:
        """Позиция вертикальной линии (только для чтения)"""
        return self._state.line_position_r

    @line_position_r.setter
    def line_position_r(self, value: float):
        """Установка позиции вертикальной линии"""
        self._state.line_position_r = value
        if self._measurement_lines:
            # Обновляем линию на графике
            self._measurement_lines.vertical_line.set_xdata([value, value])
            self._measurement_lines.measure_text.set_text(
                f'R = {value:.2f} Ω\nX = {self._state.line_position_x:.2f} Ω'
            )
            self._redraw()

    @property
    def line_position_x(self) -> float:
        """Позиция горизонтальной линии (только для чтения)"""
        return self._state.line_position_x

    @line_position_x.setter
    def line_position_x(self, value: float):
        """Установка позиции горизонтальной линии"""
        self._state.line_position_x = value
        if self._measurement_lines:
            # Обновляем линию на графике
            self._measurement_lines.horizontal_line.set_ydata([value, value])
            self._measurement_lines.measure_text.set_text(
                f'R = {self._state.line_position_r:.2f} Ω\nX = {value:.2f} Ω'
            )
            self._redraw()

    @property
    def dragging_axis_marker(self):
        """Текущий перетаскиваемый маркер на оси (для совместимости)"""
        if isinstance(self._dragged_object, tuple) and self._dragged_object[0] in ['r', 'x']:
            return self._dragged_object
        return None

    @property
    def dragging_point_marker(self):
        """Текущий перетаскиваемый точечный маркер (для совместимости)"""
        if isinstance(self._dragged_object, tuple) and self._dragged_object[0] == 'point':
            return self._dragged_object[1]
        return None