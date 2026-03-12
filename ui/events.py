# -*- coding: utf-8 -*-
"""
Модуль для обработки событий мыши на графике
"""

import tkinter as tk
import numpy as np


class EventHandler:
    """Класс для обработки событий мыши"""

    def __init__(self, visualizer, marker_manager):
        """
        Инициализация обработчика событий

        Args:
            visualizer: Главный объект визуализатора
            marker_manager: Менеджер маркеров
        """
        self.viz = visualizer
        self.markers = marker_manager

        # Для перетаскивания графика
        self.drag_start = None
        self.drag_start_xlim = None
        self.drag_start_ylim = None
        self.is_dragging = False

        # Для захвата маркеров по радиусу
        self.captured_marker = None
        self.capture_radius = 50  # пикселей

    def on_mouse_press(self, event):
        """Обработка нажатия кнопки мыши"""
        if not event.inaxes:
            return

        # Ctrl+ЛКМ - точечный маркер
        if event.key in ['control', 'ctrl'] and event.button == 1:
            self.markers.add_point_marker(event.xdata, event.ydata)
            self.viz.canvas.draw_idle()
            self.viz._show_notification(f"Точечный маркер: ({event.xdata:.2f}, {event.ydata:.2f})")
            return

        # Проверяем, есть ли маркер в радиусе захвата
        captured = self._capture_marker_at_position(event.x, event.y)

        if captured:
            # Если нашли маркер по радиусу, не начинаем перетаскивание графика
            return

        # Иначе начинаем перетаскивание графика
        if event.button == 1:
            self.drag_start = (event.x, event.y)
            self.drag_start_xlim = self.viz.ax.get_xlim()
            self.drag_start_ylim = self.viz.ax.get_ylim()
            self.is_dragging = True
            self.viz.canvas.get_tk_widget().configure(cursor="fleur")

    def _capture_marker_at_position(self, screen_x, screen_y):
        """
        Поиск маркера в радиусе от заданных экранных координат

        Args:
            screen_x, screen_y: Экранные координаты мыши

        Returns:
            bool: True если маркер найден и захвачен
        """
        # Получаем координаты мыши в системе данных
        data_x, data_y = self.viz.ax.transData.inverted().transform((screen_x, screen_y))

        # Проверяем все маркеры
        best_distance = float('inf')
        best_marker = None
        best_type = None
        best_index = None

        # Проверяем маркеры на оси R
        for i, marker in enumerate(self.markers.axis_markers_r):
            # Получаем экранные координаты линии маркера
            line_screen_x, _ = self.viz.ax.transData.transform((marker['x'], 0))
            distance = abs(screen_x - line_screen_x)

            if distance < best_distance and distance < self.capture_radius:
                best_distance = distance
                best_marker = ('r', i)
                best_type = 'r'
                best_index = i

        # Проверяем маркеры на оси X
        for i, marker in enumerate(self.markers.axis_markers_x):
            # Получаем экранные координаты линии маркера
            _, line_screen_y = self.viz.ax.transData.transform((0, marker['y']))
            distance = abs(screen_y - line_screen_y)

            if distance < best_distance and distance < self.capture_radius:
                best_distance = distance
                best_marker = ('x', i)
                best_type = 'x'
                best_index = i

        # Проверяем точечные маркеры
        for i, marker in enumerate(self.markers.point_markers):
            # Получаем экранные координаты точки
            point_screen_x, point_screen_y = self.viz.ax.transData.transform((marker['x'], marker['y']))
            distance = np.sqrt((screen_x - point_screen_x) ** 2 + (screen_y - point_screen_y) ** 2)

            if distance < best_distance and distance < self.capture_radius:
                best_distance = distance
                best_marker = ('point', i)
                best_type = 'point'
                best_index = i

        # Если нашли маркер, захватываем его
        if best_marker:
            print(f"Captured marker at distance {best_distance:.1f}px")
            marker_type, index = best_marker

            if marker_type == 'r':
                self.markers.dragging_axis_marker = ('r', index)
                self.viz.canvas.get_tk_widget().configure(cursor="sb_h_double_arrow")
            elif marker_type == 'x':
                self.markers.dragging_axis_marker = ('x', index)
                self.viz.canvas.get_tk_widget().configure(cursor="sb_v_double_arrow")
            elif marker_type == 'point':
                self.markers.dragging_point_marker = index
                self.viz.canvas.get_tk_widget().configure(cursor="fleur")

            self.captured_marker = best_marker
            return True

        return False

    def on_mouse_release(self, event):
        """Обработка отпускания кнопки мыши"""
        # Сбрасываем захваченный маркер
        self.captured_marker = None

        # Сначала проверяем, не отпустили ли мы маркер
        if self.markers.handle_mouse_release(event):
            self.viz._update_zoom_level()
            return

        if self.is_dragging:
            self.drag_start = None
            self.drag_start_xlim = None
            self.drag_start_ylim = None
            self.is_dragging = False
            self.viz.canvas.get_tk_widget().configure(cursor="arrow")
            self.viz._update_zoom_level()

    def on_mouse_motion(self, event):
        """Обработка движения мыши"""
        # Сначала проверяем, не перетаскиваем ли мы маркер
        if self.markers.handle_mouse_motion(event):
            return

        # Затем проверяем перетаскивание графика
        if self.is_dragging and event.inaxes and event.button == 1:
            if self.drag_start and event.x is not None and event.y is not None:
                x0, y0 = self.drag_start
                x1, y1 = event.x, event.y

                bbox = self.viz.ax.get_window_extent()
                if bbox.width > 0 and bbox.height > 0:
                    dx_data = (x0 - x1) * (self.drag_start_xlim[1] - self.drag_start_xlim[0]) / bbox.width
                    dy_data = (y0 - y1) * (self.drag_start_ylim[1] - self.drag_start_ylim[0]) / bbox.height

                    self.viz.ax.set_xlim(self.drag_start_xlim[0] + dx_data,
                                         self.drag_start_xlim[1] + dx_data)
                    self.viz.ax.set_ylim(self.drag_start_ylim[0] + dy_data,
                                         self.drag_start_ylim[1] + dy_data)

                    # Обновляем позиции текста маркеров после изменения масштаба
                    if hasattr(self.markers, 'update_marker_positions'):
                        self.markers.update_marker_positions()

                    self.viz.canvas.draw_idle()

    def on_scroll(self, event):
        """Масштабирование колесиком"""
        scale_factor = 0.9 if event.button == 'up' else 1.1
        xlim = self.viz.ax.get_xlim()
        ylim = self.viz.ax.get_ylim()

        x_center = event.xdata if event.xdata else (xlim[0] + xlim[1]) / 2
        y_center = event.ydata if event.ydata else (ylim[0] + ylim[1]) / 2

        new_xlim = (x_center - (x_center - xlim[0]) * scale_factor,
                    x_center + (xlim[1] - x_center) * scale_factor)
        new_ylim = (y_center - (y_center - ylim[0]) * scale_factor,
                    y_center + (ylim[1] - y_center) * scale_factor)

        self.viz.ax.set_xlim(new_xlim)
        self.viz.ax.set_ylim(new_ylim)

        # Обновляем позиции текста маркеров после изменения масштаба
        if hasattr(self.markers, 'update_marker_positions'):
            self.markers.update_marker_positions()

        self.viz.canvas.draw_idle()
        self.viz._update_zoom_level()

    def on_pick_event(self, event):
        """Обработка выбора объекта для перетаскивания (резервный метод)"""
        if not hasattr(event, 'artist'):
            return

        # Если мы уже перетаскиваем график, игнорируем pick
        if self.is_dragging:
            return

        # Передаем событие менеджеру маркеров
        self.markers.handle_pick_event(event)

    def show_context_menu(self, event):
        """Отображение контекстного меню"""
        if self.viz.ax is None:
            return

        x, y = self.viz.ax.transData.inverted().transform((event.x, event.y))

        if self.viz.ax.contains_point((event.x, event.y)):
            self.viz.context_x = x
            self.viz.context_y = y
            self.viz.context_menu_marker = self.markers.find_marker_at_position(x, y)
            self.viz.context_menu.post(event.x_root, event.y_root)