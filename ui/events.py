# -*- coding: utf-8 -*-
"""
Модуль для обработки событий мыши на графике
"""

import tkinter as tk
from typing import Optional, Tuple, Any
import numpy as np
from dataclasses import dataclass

from ui.constants import Colors


@dataclass
class DragState:
    """Состояние перетаскивания графика"""
    start: Optional[Tuple[int, int]] = None
    start_xlim: Optional[Tuple[float, float]] = None
    start_ylim: Optional[Tuple[float, float]] = None
    is_active: bool = False


@dataclass
class CaptureConfig:
    """Конфигурация захвата маркеров"""
    radius: int = 50  # пикселей
    min_distance: float = 0.1


class EventHandler:
    """Класс для обработки событий мыши"""

    # Типы курсоров
    CURSORS = {
        'default': "arrow",
        'drag': "fleur",
        'h_resize': "sb_h_double_arrow",
        'v_resize': "sb_v_double_arrow",
        'cross': "cross"
    }

    def __init__(self, visualizer, marker_manager):
        """
        Инициализация обработчика событий

        Args:
            visualizer: Главный объект визуализатора
            marker_manager: Менеджер маркеров
        """
        self._viz = visualizer
        self._markers = marker_manager
        self._config = CaptureConfig()

        # Состояние перетаскивания графика
        self._drag_state = DragState()

        # Для захвата маркеров по радиусу
        self._captured_marker: Optional[Tuple[str, int]] = None

    @property
    def is_dragging(self) -> bool:
        """Флаг перетаскивания графика"""
        return self._drag_state.is_active

    def on_mouse_press(self, event):
        """Обработка нажатия кнопки мыши"""
        if not self._is_in_axes(event):
            return

        # Ctrl+ЛКМ - точечный маркер
        if self._is_ctrl_click(event):
            self._handle_ctrl_click(event)
            return

        # Проверяем, есть ли маркер в радиусе захвата
        if self._try_capture_marker(event):
            return

        # Иначе начинаем перетаскивание графика
        self._start_drag(event)

    def _is_in_axes(self, event) -> bool:
        """Проверка, находится ли событие в области графика"""
        return event.inaxes is not None

    def _is_ctrl_click(self, event) -> bool:
        """Проверка, является ли событие Ctrl+клик"""
        return event.key in ['control', 'ctrl'] and event.button == 1

    def _handle_ctrl_click(self, event):
        """Обработка Ctrl+клик для создания точечного маркера"""
        self._markers.add_point_marker(event.xdata, event.ydata)
        self._viz.canvas.draw_idle()
        self._show_notification(f"Точечный маркер: ({event.xdata:.2f}, {event.ydata:.2f})")

    def _try_capture_marker(self, event) -> bool:
        """
        Попытка захватить маркер в позиции курсора

        Returns:
            bool: True если маркер захвачен
        """
        marker_info = self._find_marker_at_position(event)

        if marker_info:
            self._capture_marker(*marker_info)
            return True

        return False

    def _find_marker_at_position(self, event) -> Optional[Tuple[str, int]]:
        """
        Поиск маркера в позиции курсора

        Returns:
            Tuple[str, int] | None: (тип_маркера, индекс) или None
        """
        screen_x, screen_y = event.x, event.y

        # Поиск ближайшего маркера
        candidates = []

        # Проверяем маркеры на оси R
        for i, marker_data in enumerate(self._markers.axis_markers_r):
            # Получаем экранные координаты линии маркера
            line_screen_x, _ = self._viz.ax.transData.transform((marker_data['x'], 0))
            distance = abs(screen_x - line_screen_x)

            if distance < self._config.radius:
                candidates.append((distance, ('r', i)))

        # Проверяем маркеры на оси X
        for i, marker_data in enumerate(self._markers.axis_markers_x):
            # Получаем экранные координаты линии маркера
            _, line_screen_y = self._viz.ax.transData.transform((0, marker_data['y']))
            distance = abs(screen_y - line_screen_y)

            if distance < self._config.radius:
                candidates.append((distance, ('x', i)))

        # Проверяем точечные маркеры
        for i, marker_data in enumerate(self._markers.point_markers):
            # Получаем экранные координаты точки
            point_screen_x, point_screen_y = self._viz.ax.transData.transform(
                (marker_data['x'], marker_data['y'])
            )
            distance = np.sqrt(
                (screen_x - point_screen_x) ** 2 +
                (screen_y - point_screen_y) ** 2
            )

            if distance < self._config.radius:
                candidates.append((distance, ('point', i)))

        # Возвращаем ближайший маркер, если найден
        if candidates:
            candidates.sort(key=lambda x: x[0])
            return candidates[0][1]

        return None

    def _capture_marker(self, marker_type: str, index: int):
        """Захват маркера для перетаскивания"""
        self._captured_marker = (marker_type, index)

        # Устанавливаем соответствующий курсор и захватываем маркер
        if marker_type == 'r':
            # В новой версии markers.py dragging_axis_marker ожидает кортеж
            self._markers.dragging_axis_marker = ('r', index)
            self._set_cursor('h_resize')
        elif marker_type == 'x':
            self._markers.dragging_axis_marker = ('x', index)
            self._set_cursor('v_resize')
        elif marker_type == 'point':
            self._markers.dragging_point_marker = index
            self._set_cursor('drag')

        # Выводим отладочную информацию
        marker_pos = self._get_marker_position(marker_type, index)
        print(f"Captured {marker_type} marker {index} at {marker_pos}")

    def _get_marker_position(self, marker_type: str, index: int) -> str:
        """Получение позиции маркера для отладки"""
        try:
            if marker_type == 'r' and index < len(self._markers.axis_markers_r):
                return f"x={self._markers.axis_markers_r[index]['x']:.2f}"
            elif marker_type == 'x' and index < len(self._markers.axis_markers_x):
                return f"y={self._markers.axis_markers_x[index]['y']:.2f}"
            elif marker_type == 'point' and index < len(self._markers.point_markers):
                p = self._markers.point_markers[index]
                return f"({p['x']:.2f}, {p['y']:.2f})"
        except:
            pass
        return "unknown"

    def _start_drag(self, event):
        """Начало перетаскивания графика"""
        if event.button == 1:
            self._drag_state = DragState(
                start=(event.x, event.y),
                start_xlim=self._viz.ax.get_xlim(),
                start_ylim=self._viz.ax.get_ylim(),
                is_active=True
            )
            self._set_cursor('drag')

    def on_mouse_release(self, event):
        """Обработка отпускания кнопки мыши"""
        # Сбрасываем захваченный маркер
        self._captured_marker = None

        # Сначала проверяем, не отпустили ли мы маркер
        if self._markers.handle_mouse_release(event):
            self._update_zoom_level()
            return

        if self.is_dragging:
            self._drag_state = DragState()
            self._set_cursor('default')
            self._update_zoom_level()

    def on_mouse_motion(self, event):
        """Обработка движения мыши"""
        # Сначала проверяем, не перетаскиваем ли мы маркер
        if self._markers.handle_mouse_motion(event):
            return

        # Затем проверяем перетаскивание графика
        if self._should_drag_graph(event):
            self._drag_graph(event)

    def _should_drag_graph(self, event) -> bool:
        """Проверка, нужно ли перетаскивать график"""
        return (self.is_dragging and
                event.inaxes is not None and
                event.button == 1 and
                self._drag_state.start is not None)

    def _drag_graph(self, event):
        """Перетаскивание графика"""
        drag = self._drag_state
        if not drag.start or event.x is None or event.y is None:
            return

        x0, y0 = drag.start
        x1, y1 = event.x, event.y

        bbox = self._viz.ax.get_window_extent()
        if bbox.width <= 0 or bbox.height <= 0:
            return

        # Вычисляем смещение в координатах данных
        dx_data = (x0 - x1) * (drag.start_xlim[1] - drag.start_xlim[0]) / bbox.width
        dy_data = (y0 - y1) * (drag.start_ylim[1] - drag.start_ylim[0]) / bbox.height

        # Применяем новое смещение
        self._viz.ax.set_xlim(
            drag.start_xlim[0] + dx_data,
            drag.start_xlim[1] + dx_data
        )
        self._viz.ax.set_ylim(
            drag.start_ylim[0] + dy_data,
            drag.start_ylim[1] + dy_data
        )

        # Обновляем позиции текста маркеров после изменения масштаба
        if hasattr(self._markers, 'update_marker_positions'):
            self._markers.update_marker_positions()

        self._viz.canvas.draw_idle()

    def on_scroll(self, event):
        """Масштабирование колесиком"""
        if not self._is_in_axes(event):
            return

        scale_factor = 0.9 if event.button == 'up' else 1.1

        # Получаем текущие границы
        xlim = self._viz.ax.get_xlim()
        ylim = self._viz.ax.get_ylim()

        # Центр масштабирования
        x_center = event.xdata if event.xdata else (xlim[0] + xlim[1]) / 2
        y_center = event.ydata if event.ydata else (ylim[0] + ylim[1]) / 2

        # Вычисляем новые границы
        new_xlim = self._calculate_zoomed_limits(xlim, x_center, scale_factor)
        new_ylim = self._calculate_zoomed_limits(ylim, y_center, scale_factor)

        # Применяем
        self._viz.ax.set_xlim(new_xlim)
        self._viz.ax.set_ylim(new_ylim)

        # Обновляем позиции текста маркеров после изменения масштаба
        if hasattr(self._markers, 'update_marker_positions'):
            self._markers.update_marker_positions()

        self._viz.canvas.draw_idle()
        self._update_zoom_level()

    def _calculate_zoomed_limits(self, limits: Tuple[float, float],
                                 center: float,
                                 factor: float) -> Tuple[float, float]:
        """
        Вычисление новых границ после масштабирования

        Args:
            limits: (min, max) текущие границы
            center: центр масштабирования
            factor: коэффициент масштабирования

        Returns:
            Tuple[float, float]: новые границы
        """
        return (
            center - (center - limits[0]) * factor,
            center + (limits[1] - center) * factor
        )

    def on_pick_event(self, event):
        """Обработка выбора объекта для перетаскивания (резервный метод)"""
        if not hasattr(event, 'artist'):
            return

        # Если мы уже перетаскиваем график, игнорируем pick
        if self.is_dragging:
            return

        # Передаем событие менеджеру маркеров
        self._markers.handle_pick_event(event)

    def show_context_menu(self, event):
        """Отображение контекстного меню"""
        if self._viz.ax is None:
            return

        x, y = self._viz.ax.transData.inverted().transform((event.x, event.y))

        if self._viz.ax.contains_point((event.x, event.y)):
            self._viz.context_x = x
            self._viz.context_y = y
            self._viz.context_menu_marker = self._markers.find_marker_at_position(x, y)
            self._viz.context_menu.post(event.x_root, event.y_root)

    # ========== Вспомогательные методы ==========

    def _set_cursor(self, cursor_type: str):
        """Установка курсора"""
        cursor = self.CURSORS.get(cursor_type, self.CURSORS['default'])
        self._viz.canvas.get_tk_widget().configure(cursor=cursor)

    def _update_zoom_level(self):
        """Обновление отображения уровня зума"""
        self._viz._update_zoom_level()

    def _show_notification(self, message: str):
        """Показать уведомление"""
        if hasattr(self._viz, '_show_notification'):
            self._viz._show_notification(message)

    # ========== Свойства для совместимости ==========

    @property
    def captured_marker(self) -> Optional[Tuple[str, int]]:
        """Текущий захваченный маркер"""
        return self._captured_marker

    @captured_marker.setter
    def captured_marker(self, value):
        """Сеттер для совместимости"""
        self._captured_marker = value

    @property
    def capture_radius(self) -> int:
        """Радиус захвата"""
        return self._config.radius

    @capture_radius.setter
    def capture_radius(self, value: int):
        """Сеттер для радиуса захвата"""
        self._config.radius = value

    @property
    def drag_start(self):
        """Начальная точка перетаскивания (для совместимости)"""
        return self._drag_state.start

    @drag_start.setter
    def drag_start(self, value):
        """Сеттер для совместимости"""
        self._drag_state.start = value

    @property
    def drag_start_xlim(self):
        """Начальные границы по X (для совместимости)"""
        return self._drag_state.start_xlim

    @drag_start_xlim.setter
    def drag_start_xlim(self, value):
        """Сеттер для совместимости"""
        self._drag_state.start_xlim = value

    @property
    def drag_start_ylim(self):
        """Начальные границы по Y (для совместимости)"""
        return self._drag_state.start_ylim

    @drag_start_ylim.setter
    def drag_start_ylim(self, value):
        """Сеттер для совместимости"""
        self._drag_state.start_ylim = value

    @property
    def is_dragging(self) -> bool:
        """Флаг перетаскивания (для совместимости)"""
        return self._drag_state.is_active

    @is_dragging.setter
    def is_dragging(self, value: bool):
        """Сеттер для совместимости"""
        self._drag_state.is_active = value