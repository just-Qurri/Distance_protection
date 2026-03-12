"""
Верхняя панель управления
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Optional

from ui.constants import Colors, Fonts, FaultTypes, InfoItems


class TopPanel:
    """Верхняя панель с кнопками масштабирования и переключателем типа повреждения"""

    def __init__(self, parent, visualizer):
        """
        Args:
            parent: Родительский виджет
            visualizer: Главный объект визуализатора
        """
        self.parent = parent
        self.viz = visualizer
        self.frame = ttk.Frame(parent)

        # UI элементы
        self.fault_type_label: Optional[ttk.Label] = None
        self.fault_combo: Optional[ttk.Combobox] = None

        # Данные
        self.fault_type_names: Dict[str, str] = FaultTypes.get_display_names()
        self.fault_type_list = FaultTypes.get_list()

        self._create_widgets()
        self._bind_events()

    def pack(self, **kwargs):
        """Упаковка панели"""
        self.frame.pack(**kwargs)

    def _create_widgets(self):
        """Создание виджетов"""
        top_frame = self.frame

        # Левая часть - кнопки масштабирования
        left_frame = ttk.Frame(top_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        self._create_zoom_controls(left_frame)
        self._create_fault_selector(top_frame)
        self._create_info_panel(top_frame)

    def _create_zoom_controls(self, parent):
        """Создание элементов управления масштабом"""
        # Кнопки масштабирования
        zoom_buttons = [
            ("+", self.viz.zoom_in, "Увеличить масштаб"),
            ("-", self.viz.zoom_out, "Уменьшить масштаб"),
            ("↺", self.viz.reset_to_initial_scale, "Сбросить масштаб"),
            ("⤢", self.viz.fit_to_view, "Подогнать под экран")
        ]

        for text, command, tooltip in zoom_buttons:
            btn = ttk.Button(parent, text=text, width=3, command=command)
            btn.pack(side=tk.LEFT, padx=2)
            self._add_tooltip(btn, tooltip)

        # Индикатор масштаба
        ttk.Label(parent, text="Масштаб:",
                  font=Fonts.normal()).pack(side=tk.LEFT, padx=(20, 5))

        ttk.Label(parent, textvariable=self.viz.zoom_level,
                  font=Fonts.normal_bold(),
                  foreground=Colors.ACCENT).pack(side=tk.LEFT)

    def _create_fault_selector(self, parent):
        """Создание селектора типа повреждения"""
        fault_frame = ttk.Frame(parent)
        fault_frame.pack(side=tk.LEFT, padx=(30, 0))

        ttk.Label(fault_frame, text="Тип:",
                  font=Fonts.normal()).pack(side=tk.LEFT)

        self.fault_combo = ttk.Combobox(fault_frame,
                                        textvariable=self.viz.fault_type,
                                        values=[code for code, _ in self.fault_type_list],
                                        state="readonly",
                                        width=10)
        self.fault_combo.pack(side=tk.LEFT, padx=5)

        # Привязываем событие выбора
        self.fault_combo.bind('<<ComboboxSelected>>', self._on_fault_type_changed)

        # Отображение названия типа повреждения
        self.fault_type_label = ttk.Label(fault_frame,
                                          text="",
                                          font=Fonts.small(),
                                          foreground=Colors.SECONDARY)
        self.fault_type_label.pack(side=tk.LEFT)
        self.update_fault_type_label()

    def _create_info_panel(self, parent):
        """Создание панели с информацией об управлении"""
        info_frame = ttk.Frame(parent)
        info_frame.pack(side=tk.RIGHT)

        for icon, text in InfoItems.get_all():
            if icon == "|":
                ttk.Label(info_frame, text="|",
                          font=Fonts.normal(),
                          foreground=Colors.SEPARATOR).pack(side=tk.LEFT, padx=5)
            else:
                frame = ttk.Frame(info_frame)
                frame.pack(side=tk.LEFT)

                ttk.Label(frame, text=icon,
                          font=Fonts.normal()).pack(side=tk.LEFT, padx=2)

                ttk.Label(frame, text=text,
                          font=Fonts.small(),
                          foreground=Colors.SECONDARY).pack(side=tk.LEFT)

    def _add_tooltip(self, widget, text):
        """Добавление всплывающей подсказки"""

        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")

            label = ttk.Label(tooltip, text=text,
                              background=Colors.TOOLTIP_BG,
                              relief="solid",
                              borderwidth=1)
            label.pack()

            # Автоматическое скрытие через 2 секунды
            tooltip.after(2000, tooltip.destroy)

            widget.tooltip = tooltip

        widget.bind('<Enter>', show_tooltip)

    def _bind_events(self):
        """Привязка событий"""
        # Отслеживаем изменение переменной fault_type
        self.viz.fault_type.trace_add('write', self._on_fault_type_var_changed)

    def _on_fault_type_changed(self, event=None):
        self.update_fault_type_label()

    def _on_fault_type_var_changed(self, *args):
        self.update_fault_type_label()

        if self.fault_combo and self.fault_combo.get() != self.viz.fault_type.get():
            self.fault_combo.set(self.viz.fault_type.get())

    def update_fault_type_label(self):
        """Обновление отображения типа повреждения"""
        fault_type = self.viz.fault_type.get()

        # Используем словарь для быстрого поиска
        name = self.fault_type_names.get(fault_type)

        if name:
            self.fault_type_label.config(text=f"({name})",
                                         foreground=Colors.SECONDARY)
        else:
            # Если тип не найден, показываем предупреждение
            self.fault_type_label.config(text="(Неизвестный тип)",
                                         foreground=Colors.ERROR)

    def set_fault_type(self, fault_type: str) -> bool:
        """
        Установка типа повреждения программно
        Args:
            fault_type: код типа повреждения
        Returns:
            bool: True если тип установлен, False если тип не найден
        """
        if fault_type in self.fault_type_names:
            self.viz.fault_type.set(fault_type)
            return True
        else:
            print(f"Предупреждение: неизвестный тип '{fault_type}'")
            return False