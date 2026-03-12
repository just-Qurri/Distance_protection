# -*- coding: utf-8 -*-
"""
Область графика с поддержкой перетаскивания и масштабирования
"""

import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class PlotArea:
    """Область графика с поддержкой интерактивных операций"""

    def __init__(self, parent, visualizer):
        """
        Инициализация области графика

        Args:
            parent: Родительский виджет
            visualizer: Главный объект визуализатора
        """
        self.parent = parent
        self.viz = visualizer
        self.frame = ttk.Frame(parent)

        # Для перетаскивания
        self.drag_start = None
        self.drag_start_xlim = None
        self.drag_start_ylim = None
        self.is_dragging = False

        self._create_plot()

    def pack(self, **kwargs):
        """Упаковка фрейма"""
        self.frame.pack(**kwargs)

    def _create_plot(self):
        """Создание области графика"""
        self.viz.figure = plt.Figure(figsize=(10, 8), dpi=100,
                                     facecolor='white', edgecolor='#dddddd')
        self.viz.ax = self.viz.figure.add_subplot(111)
        self.viz.ax.set_facecolor('#fafafa')
        self.viz.ax.grid(True, alpha=0.15, linestyle='--', color='#CCCCCC')

        self.viz.canvas = FigureCanvasTkAgg(self.viz.figure, master=self.frame)
        self.viz.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.viz.canvas.draw()

        # Привязка событий мыши
        self.viz.canvas.mpl_connect('scroll_event', self._on_scroll)
        self.viz.canvas.mpl_connect('button_press_event', self._on_mouse_press)
        self.viz.canvas.mpl_connect('button_release_event', self._on_mouse_release)
        self.viz.canvas.mpl_connect('motion_notify_event', self._on_mouse_motion)
        self.viz.canvas.mpl_connect('figure_enter_event', self._on_figure_enter)
        self.viz.canvas.mpl_connect('figure_leave_event', self._on_figure_leave)

        self.viz.canvas.get_tk_widget().configure(cursor="arrow")

    def _on_figure_enter(self, event):
        """При входе в область графика"""
        self.viz.canvas.get_tk_widget().configure(cursor="hand2")

    def _on_figure_leave(self, event):
        """При выходе из области графика"""
        self.viz.canvas.get_tk_widget().configure(cursor="arrow")

    def _on_mouse_press(self, event):
        """Начало перетаскивания"""
        if event.button == 1 and event.inaxes:
            self.drag_start = (event.x, event.y)
            self.drag_start_xlim = self.viz.ax.get_xlim()
            self.drag_start_ylim = self.viz.ax.get_ylim()
            self.is_dragging = True
            self.viz.canvas.get_tk_widget().configure(cursor="fleur")

    def _on_mouse_release(self, event):
        """Конец перетаскивания"""
        if event.button == 1:
            self.drag_start = None
            self.drag_start_xlim = None
            self.drag_start_ylim = None
            self.is_dragging = False
            self.viz.canvas.get_tk_widget().configure(cursor="hand2")
            self.viz._update_zoom_level()

    def _on_mouse_motion(self, event):
        """Процесс перетаскивания"""
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
                    self.viz.canvas.draw_idle()

    def _on_scroll(self, event):
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
        self.viz.canvas.draw_idle()
        self.viz._update_zoom_level()