# ui/events/event_handler.py
import tkinter as tk
import numpy as np
from typing import Optional, Tuple

from ui.events.drag_handler import DragHandler
from ui.events.marker_interaction import MarkerInteraction
from ui.events.zoom_handler import ZoomHandler


class EventHandler:
    """Главный обработчик событий мыши"""

    def __init__(self, visualizer, marker_manager):
        self.viz = visualizer
        self.markers = marker_manager

        # Инициализируем под-обработчики
        self.drag_handler = DragHandler(visualizer)
        self.marker_handler = MarkerInteraction(visualizer, marker_manager)
        self.zoom_handler = ZoomHandler(visualizer)

        # Для обратной совместимости
        self.drag_start = None
        self.drag_start_xlim = None
        self.drag_start_ylim = None
        self.is_dragging = False
        self.captured_marker = None
        self.capture_radius = 50

    def on_mouse_press(self, event):
        """Обработка нажатия кнопки мыши"""
        if not event.inaxes:
            return

        # Ctrl+ЛКМ - точечный маркер
        if event.key in ['control', 'ctrl'] and event.button == 1:
            self.markers.add_point_marker(event.xdata, event.ydata)
            self.viz.canvas.draw_idle()
            self._show_notification(f"Точечный маркер: ({event.xdata:.2f}, {event.ydata:.2f})")
            return

        # Проверяем захват маркера
        if self.marker_handler.try_capture_marker(event):
            self.captured_marker = self.marker_handler.captured_marker
            return

        # Начинаем перетаскивание графика
        self.drag_handler.start_drag(event)
        self.is_dragging = self.drag_handler.is_dragging
        self.drag_start = self.drag_handler.drag_start
        self.drag_start_xlim = self.drag_handler.drag_start_xlim
        self.drag_start_ylim = self.drag_handler.drag_start_ylim

    def on_mouse_release(self, event):
        """Обработка отпускания кнопки мыши"""
        self.captured_marker = None
        self.marker_handler.captured_marker = None

        # Проверяем отпускание маркера
        if self.markers.handle_mouse_release(event):
            self.viz._update_zoom_level()
            return

        # Обрабатываем отпускание при перетаскивании графика
        if self.drag_handler.on_mouse_release(event):
            self.is_dragging = False
            self.viz._update_zoom_level()

    def on_mouse_motion(self, event):
        """Обработка движения мыши"""
        # Сначала проверяем перетаскивание маркеров
        if self.markers.handle_mouse_motion(event):
            return

        # Затем перетаскивание графика
        if self.drag_handler.on_mouse_motion(event):
            # Обновляем позиции маркеров
            if hasattr(self.markers, 'update_marker_positions'):
                self.markers.update_marker_positions()
            self.viz.canvas.draw_idle()

    def on_scroll(self, event):
        """Масштабирование колесиком"""
        self.zoom_handler.on_scroll(event)
        # Обновляем позиции маркеров после масштабирования
        if hasattr(self.markers, 'update_marker_positions'):
            self.markers.update_marker_positions()
        self.viz.canvas.draw_idle()
        self.viz._update_zoom_level()

    def on_pick_event(self, event):
        """Обработка выбора объекта"""
        if not hasattr(event, 'artist') or self.is_dragging:
            return

        self.markers.handle_pick_event(event)

    def show_context_menu(self, event):
        """Отображение контекстного меню"""
        if self.viz.ax is None:
            return

        if self.viz.ax.contains_point((event.x, event.y)):
            x, y = self.viz.ax.transData.inverted().transform((event.x, event.y))
            self.viz.context_x = x
            self.viz.context_y = y
            self.viz.context_menu_marker = self.markers.find_marker_at_position(x, y)
            self.viz.context_menu.post(event.x_root, event.y_root)

    def _show_notification(self, message):
        """Показать уведомление"""
        if hasattr(self.viz, '_show_notification'):
            self.viz._show_notification(message)