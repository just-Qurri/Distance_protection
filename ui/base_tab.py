# -*- coding: utf-8 -*-
"""
Базовый класс для всех вкладок настроек (оптимизирован)
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, List, Dict, Callable, Any, Tuple

from widgets.color_combo import ColorCombo
from widgets.float_entry import FloatEntry


class BaseTab:
    """Базовый класс для всех вкладок настроек"""

    def __init__(self, notebook: ttk.Notebook, visualizer, colors: List, linestyles: List):
        self.viz = visualizer
        self.colors = colors
        self.linestyles = linestyles
        self._entry_widgets: List[FloatEntry] = []
        self._current_entry: Optional[tk.Widget] = None
        self._updating: bool = False
        self.vars: Dict[str, tk.Variable] = {}
        self.tab = ttk.Frame(notebook, padding=10)
        notebook.add(self.tab, text=self.get_tab_name())
        self._create_ui()
        self._bind_events()
        self._setup_traces()

    # ==================== АБСТРАКТНЫЕ МЕТОДЫ ====================

    def get_tab_name(self) -> str:
        """Возвращает имя вкладки (должен быть переопределен)"""
        return "Tab"

    def _create_ui(self):
        """Создание UI (должен быть переопределен)"""
        pass

    def _get_target_object(self):
        """Возвращает целевой объект (должен быть переопределен)"""
        return None

    def _do_apply(self, obj) -> None:
        """Применение изменений к объекту (переопределяется)"""
        pass

    def _do_cancel(self, obj) -> None:
        """Отмена изменений (переопределяется)"""
        pass

    # ==================== ОБЩИЕ МЕТОДЫ ====================

    def _setup_traces(self):
        """Настройка отслеживания изменений переменных"""
        if "enabled" in self.vars:
            self.vars["enabled"].trace('w', lambda *args: self._on_enabled_toggle())

    def _bind_events(self):
        """Привязка событий для полей ввода"""
        for entry in self._entry_widgets:
            entry.bind('<FocusIn>', self._on_focus_in)
            if hasattr(entry, 'entry'):
                entry.entry.bind('<Escape>', self._cancel_changes)

    def _on_focus_in(self, event):
        """Запоминаем поле, в которое вошёл фокус"""
        self._current_entry = event.widget

    def _focus_next(self, current_widget=None):
        """Переход к следующему полю ввода"""
        try:
            widget = current_widget or self._current_entry
            if widget and widget.winfo_exists():
                next_widget = widget.tk_focusNext()
                if next_widget and next_widget.winfo_exists():
                    next_widget.focus_set()
                    return
            self.tab.focus_set()
        except Exception:
            self.tab.focus_set()
        self._current_entry = None

    def _on_enabled_toggle(self):
        """Обработка включения/отключения"""
        obj = self._get_target_object()
        if obj and "enabled" in self.vars:
            obj.enabled = self.vars["enabled"].get()
            self.viz.plot_characteristics(keep_limits=True)
            self.viz._update_status()

    def _apply_changes(self, event=None):
        """Применение изменений (общая логика)"""
        if self._updating:
            return

        self._updating = True
        try:
            obj = self._get_target_object()
            if obj:
                # Применяем общие параметры
                if "enabled" in self.vars:
                    obj.enabled = self.vars["enabled"].get()
                if "color" in self.vars:
                    obj.color = self.vars["color"].get()
                if "style" in self.vars:
                    obj.linestyle = self.vars["style"].get()

                # Применяем специфичные параметры
                self._do_apply(obj)

                self.viz.plot_characteristics(keep_limits=True)
                self.viz._update_status()
        except ValueError as e:
            self.viz._show_notification(f"Ошибка: {e}")
        finally:
            self._updating = False

    def _cancel_changes(self, event):
        """Отмена изменений (общая логика)"""
        obj = self._get_target_object()
        if obj:
            self._do_cancel(obj)
            self.viz._show_notification("Изменения отменены")
        self._focus_next()

    # ==================== МЕТОДЫ СОЗДАНИЯ UI ====================

    def _create_title_frame(self, title: str, color: str):
        """Создание заголовка вкладки с чекбоксом"""
        title_frame = ttk.Frame(self.tab)
        title_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(title_frame, text=title,
                  font=('Segoe UI', 16, 'bold'), foreground=color).pack(side=tk.LEFT)

        if "enabled" in self.vars:
            ttk.Checkbutton(title_frame, text="Показать",
                            variable=self.vars["enabled"]).pack(side=tk.RIGHT)

    def _create_title_frame_without_checkbox(self, title: str, color: str):
        """Создание заголовка вкладки без чекбокса"""
        title_frame = ttk.Frame(self.tab)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(title_frame, text=title,
                  font=('Segoe UI', 16, 'bold'), foreground=color).pack(side=tk.LEFT)

    def _create_style_frame(self, parent, opacity_key: Optional[str] = None):
        """Создание фрейма для настройки стиля"""
        style_frame = ttk.LabelFrame(parent, text="Оформление", padding=5)
        style_frame.pack(fill=tk.X, pady=5)

        # Используем grid для всего содержимого
        row = 0

        # Цвет
        ttk.Label(style_frame, text="Цвет:", font=('Segoe UI', 9)).grid(
            row=row, column=0, sticky=tk.W, pady=2
        )
        color_combo = ColorCombo(style_frame, textvariable=self.vars["color"],
                                 colors=self.colors, width=15)
        color_combo.grid(row=row, column=1, sticky=tk.W, padx=5)
        color_combo.bind('<<ComboboxSelected>>', lambda e: self._apply_changes())
        row += 1

        # Стиль линии
        ttk.Label(style_frame, text="Стиль:", font=('Segoe UI', 9)).grid(
            row=row, column=0, sticky=tk.W, pady=2
        )
        style_combo = ttk.Combobox(style_frame, textvariable=self.vars["style"],
                                   values=[s[0] for s in self.linestyles],
                                   state="readonly", width=12)
        style_combo.grid(row=row, column=1, sticky=tk.W, padx=5)
        style_combo.bind('<<ComboboxSelected>>', lambda e: self._apply_changes())
        row += 1

        # Прозрачность (если указана)
        if opacity_key and opacity_key in self.vars:
            ttk.Label(style_frame, text="Прозрачность:", font=('Segoe UI', 9)).grid(
                row=row, column=0, sticky=tk.W, pady=2
            )
            opacity_entry = FloatEntry(style_frame, textvariable=self.vars[opacity_key], width=6,
                                       on_change_callback=self._apply_changes)
            opacity_entry.grid(row=row, column=1, sticky=tk.W, padx=5)
            ttk.Label(style_frame, text="(0.0-1.0)",
                      font=('Segoe UI', 8), foreground='#666').grid(
                row=row, column=2, sticky=tk.W, padx=5
            )
            self._entry_widgets.append(opacity_entry)

        return style_frame

    def _create_entry(self, parent: ttk.Frame, label: str, key: str,
                      row: int, col: int, width: int = 8,
                      callback: Optional[Callable] = None) -> FloatEntry:
        """Создание одного поля ввода"""
        ttk.Label(parent, text=label, font=('Segoe UI', 9)).grid(
            row=row, column=col, sticky=tk.W, pady=2
        )

        entry = FloatEntry(
            parent,
            textvariable=self.vars[key],
            width=width,
            on_change_callback=callback or self._apply_changes
        )
        entry.grid(row=row, column=col + 1, sticky=tk.W, padx=5)
        self._entry_widgets.append(entry)
        return entry

    def _create_entries(self, parent: ttk.Frame, entries: List[Tuple[str, str, int, int]],
                        callback: Optional[Callable] = None) -> None:
        """Создание группы полей ввода"""
        for label, key, row, col in entries:
            self._create_entry(parent, label, key, row, col, callback=callback)

    def _get_float_value(self, key: str) -> float:
        """Получение значения из переменной"""
        try:
            value = self.vars[key].get().replace(',', '.')
            return float(value)
        except (ValueError, tk.TclError):
            return 0.0

    def _set_var(self, key: str, value: Any) -> None:
        """Установка значения переменной"""
        if key in self.vars:
            if isinstance(value, bool):
                self.vars[key].set(value)
            else:
                self.vars[key].set(str(value))

    def _update_vars_from_obj(self, obj, mapping: Dict[str, str]) -> None:
        """Обновление переменных из объекта"""
        for var_key, attr_name in mapping.items():
            if var_key in self.vars and hasattr(obj, attr_name):
                self._set_var(var_key, getattr(obj, attr_name))
