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

        # Для перетаскивания (резервные переменные, основное в events.py)
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
        self.viz.figure = plt.Figure(figsize=(8, 8), dpi=100,
                                     facecolor='white', edgecolor='#dddddd')
        self.viz.ax = self.viz.figure.add_subplot(111)
        self.viz.ax.set_facecolor('#fafafa')

        self.viz.canvas = FigureCanvasTkAgg(self.viz.figure, master=self.frame)
        self.viz.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.viz.canvas.draw()

        # Привязка событий происходит в visualizer.py