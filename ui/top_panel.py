# -*- coding: utf-8 -*-
"""
Верхняя панель управления
"""

import tkinter as tk
from tkinter import ttk

from ui.constants import FAULT_TYPES
from widgets.terminal_selector import TerminalSelector


class TopPanel:
    """Верхняя панель с кнопками масштабирования и переключателем типа повреждения"""

    def __init__(self, parent, visualizer):
        self.parent = parent
        self.viz = visualizer
        self.frame = ttk.Frame(parent)
        self.fault_type_label = None
        self.fault_types = FAULT_TYPES
        self.terminal_selector = None
        self._create_widgets()

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)

    def _create_widgets(self):
        top_frame = self.frame

        # Левая часть - кнопки масштабирования
        left_frame = ttk.Frame(top_frame)
        left_frame.pack(side=tk.LEFT)

        ttk.Button(left_frame, text="➕", width=3, command=self.viz.zoom_in).pack(side=tk.LEFT, padx=2)
        ttk.Button(left_frame, text="➖", width=3, command=self.viz.zoom_out).pack(side=tk.LEFT, padx=2)
        ttk.Button(left_frame, text="⟳", width=3, command=self.viz.reset_to_initial_scale).pack(side=tk.LEFT, padx=2)
        ttk.Button(left_frame, text="⊡", width=3, command=self.viz.fit_to_view).pack(side=tk.LEFT, padx=2)

        ttk.Label(left_frame, text="Масштаб:", font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=(20, 5))
        ttk.Label(left_frame, textvariable=self.viz.zoom_level,
                  font=('Segoe UI', 10, 'bold'), foreground='#2196F3').pack(side=tk.LEFT)

        # Переключатель типа повреждения
        fault_frame = ttk.Frame(top_frame)
        fault_frame.pack(side=tk.LEFT, padx=(30, 0))

        ttk.Label(fault_frame, text="⚡ Тип:", font=('Segoe UI', 10)).pack(side=tk.LEFT)
        fault_combo = ttk.Combobox(fault_frame, textvariable=self.viz.fault_type,
                                   values=[f[0] for f in self.fault_types],
                                   state="readonly", width=12)
        fault_combo.pack(side=tk.LEFT, padx=5)

        self.fault_type_label = ttk.Label(fault_frame, text="", font=('Segoe UI', 9), foreground='#78909c')
        self.fault_type_label.pack(side=tk.LEFT)
        self.update_fault_type_label()

        # Выбор терминала
        terminal_frame = ttk.Frame(top_frame)
        terminal_frame.pack(side=tk.LEFT, padx=(20, 0))

        self.terminal_selector = TerminalSelector(
            terminal_frame,
            on_change=self._on_terminal_change
        )
        self.terminal_selector.pack()

        # Правая часть - дополнительные кнопки
        right_frame = ttk.Frame(top_frame)
        right_frame.pack(side=tk.RIGHT)

        # Кнопки управления зонами
        zone_btn_frame = ttk.Frame(right_frame)
        zone_btn_frame.pack(side=tk.LEFT, padx=2)

        ttk.Button(zone_btn_frame, text="Все вкл", width=10,
                   command=self.viz.enable_all_zones).pack(side=tk.LEFT, padx=1)
        ttk.Button(zone_btn_frame, text="Все выкл", width=10,
                   command=self.viz.disable_all_zones).pack(side=tk.LEFT, padx=1)

        # Кнопки сохранения/загрузки
        config_frame = ttk.Frame(right_frame)
        config_frame.pack(side=tk.LEFT, padx=(10, 2))

        ttk.Button(config_frame, text="💾 Сохранить", width=12,
                   command=self.viz.save_configuration_dialog).pack(side=tk.LEFT, padx=1)
        ttk.Button(config_frame, text="📂 Загрузить", width=12,
                   command=self.viz.load_configuration_dialog).pack(side=tk.LEFT, padx=1)

        # Кнопки экспорта
        export_frame = ttk.Frame(right_frame)
        export_frame.pack(side=tk.LEFT, padx=(10, 2))

        ttk.Button(export_frame, text="💾 PNG", width=10,
                   command=self.viz.save_as_png).pack(side=tk.LEFT, padx=1)
        ttk.Button(export_frame, text="✕ Маркеры", width=10,
                   command=self.viz.clear_all_markers).pack(side=tk.LEFT, padx=1)

    def _on_terminal_change(self, terminal_code: str):
        """Обработка изменения типа терминала"""
        self.viz.set_terminal_type(terminal_code)
        # Обновляем статус
        self.viz._update_status()

    def update_fault_type_label(self):
        """Обновление метки типа повреждения"""
        fault_type = self.viz.fault_type.get()
        for code, name in self.fault_types:
            if code == fault_type:
                self.fault_type_label.config(text=f"({name})")
                break
