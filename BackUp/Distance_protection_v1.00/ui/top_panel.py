# -*- coding: utf-8 -*-
"""
Верхняя панель управления
"""

import tkinter as tk
from tkinter import ttk

from ui.constants import INFO_ITEMS, FAULT_TYPES


class TopPanel:
    """Верхняя панель с кнопками масштабирования и переключателем типа повреждения"""

    def __init__(self, parent, visualizer):
        """
        Инициализация верхней панели

        Args:
            parent: Родительский виджет
            visualizer: Главный объект визуализатора
        """
        self.parent = parent
        self.viz = visualizer
        self.frame = ttk.Frame(parent)
        self.fault_type_label = None
        self.fault_types = FAULT_TYPES

        self._create_widgets()

    def pack(self, **kwargs):
        """Упаковка панели"""
        self.frame.pack(**kwargs)

    def _create_widgets(self):
        """Создание виджетов"""
        top_frame = self.frame

        # Левая часть - кнопки масштабирования
        left_frame = ttk.Frame(top_frame)
        left_frame.pack(side=tk.LEFT)

        # Кнопки масштабирования
        ttk.Button(left_frame, text="+", width=3,
                   command=self.viz.zoom_in).pack(side=tk.LEFT, padx=2)
        ttk.Button(left_frame, text="-", width=3,
                   command=self.viz.zoom_out).pack(side=tk.LEFT, padx=2)
        ttk.Button(left_frame, text="↺", width=3,
                   command=self.viz.reset_to_initial_scale).pack(side=tk.LEFT, padx=2)
        ttk.Button(left_frame, text="⤢", width=3,
                   command=self.viz.fit_to_view).pack(side=tk.LEFT, padx=2)

        # Индикатор масштаба
        ttk.Label(left_frame, text="Масштаб:", font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=(20, 5))
        ttk.Label(left_frame, textvariable=self.viz.zoom_level,
                  font=('Segoe UI', 10, 'bold'), foreground='#2196F3').pack(side=tk.LEFT)

        # Переключатель типа повреждения
        fault_frame = ttk.Frame(top_frame)
        fault_frame.pack(side=tk.LEFT, padx=(30, 0))

        ttk.Label(fault_frame, text="Тип:", font=('Segoe UI', 10)).pack(side=tk.LEFT)
        fault_combo = ttk.Combobox(fault_frame, textvariable=self.viz.fault_type,
                                   values=[f[0] for f in self.fault_types],
                                   state="readonly", width=10)
        fault_combo.pack(side=tk.LEFT, padx=5)

        # Отображение названия типа повреждения
        self.fault_type_label = ttk.Label(fault_frame, text="", font=('Segoe UI', 9), foreground='#666')
        self.fault_type_label.pack(side=tk.LEFT)
        self.update_fault_type_label()

        # Информация об управлении
        info_frame = ttk.Frame(top_frame)
        info_frame.pack(side=tk.RIGHT)

        for icon, text in INFO_ITEMS:
            if icon == "|":
                ttk.Label(info_frame, text="|", font=('Segoe UI', 12),
                          foreground='#ccc').pack(side=tk.LEFT, padx=5)
            else:
                frame = ttk.Frame(info_frame)
                frame.pack(side=tk.LEFT)
                ttk.Label(frame, text=icon, font=('Segoe UI', 12)).pack(side=tk.LEFT, padx=2)
                ttk.Label(frame, text=text, font=('Segoe UI', 9),
                          foreground='#666').pack(side=tk.LEFT)

    def update_fault_type_label(self):
        """Обновление отображения типа повреждения"""
        fault_type = self.viz.fault_type.get()
        for code, name in self.fault_types:
            if code == fault_type:
                self.fault_type_label.config(text=f"({name})")
                break