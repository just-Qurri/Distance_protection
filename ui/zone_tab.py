# -*- coding: utf-8 -*-
"""
Вкладка для настройки параметров зоны
"""

import tkinter as tk
from tkinter import ttk

from widgets.color_combo import ColorCombo
from widgets.float_entry import FloatEntry


class ZoneTab:
    """Вкладка для настройки параметров зоны"""

    def __init__(self, notebook, zone, visualizer, colors, linestyles, is_common=False):
        self.zone = zone
        self.is_common = is_common
        self.viz = visualizer
        self.colors = colors
        self.linestyles = linestyles
        self._entry_widgets = []
        self._current_entry = None
        self._updating = False

        if is_common:
            tab_text = "Common"
        else:
            tab_text = f"Зона {zone.zone_id}"

        self.tab = ttk.Frame(notebook, padding=10)
        notebook.add(self.tab, text=tab_text)

        self.vars = {}

        if is_common:
            self._create_common_ui()
        else:
            self._create_dz_ui()

    def _create_dz_ui(self):
        """Создание UI для зоны DZ"""
        title_frame = ttk.Frame(self.tab)
        title_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(title_frame, text=self.zone.name,
                  font=('Segoe UI', 16, 'bold'), foreground='#9C27B0').pack(side=tk.LEFT)

        enabled_var = tk.BooleanVar(value=self.zone.enabled)
        enabled_check = ttk.Checkbutton(title_frame, text="Показать", variable=enabled_var)
        enabled_check.pack(side=tk.RIGHT)
        self.vars["enabled"] = enabled_var

        direction_var = tk.StringVar(value=self.zone.direction_mode)
        color_var = tk.StringVar(value=self.zone.color)
        style_var = tk.StringVar(value=self.zone.linestyle)

        self.vars.update({
            "direction": direction_var,
            "color": color_var,
            "style": style_var,
            "x1": tk.StringVar(value=f"{self.zone.x1:.2f}"),
            "r1": tk.StringVar(value=f"{self.zone.r1:.2f}"),
            "rfpp": tk.StringVar(value=f"{self.zone.rfpp:.2f}"),
            "x0": tk.StringVar(value=f"{self.zone.x0:.2f}"),
            "r0": tk.StringVar(value=f"{self.zone.r0:.2f}"),
            "rfpe": tk.StringVar(value=f"{self.zone.rfpe:.2f}"),
        })

        self._create_direction_frame()
        self._create_phph_frame()
        self._create_phe_frame()
        self._create_style_frame()

        self._bind_entry_events()
        enabled_var.trace('w', lambda *args: self._on_enabled_toggle())

    def _create_common_ui(self):
        """Создание UI для Common Settings"""
        obj = self.zone

        title_frame = ttk.Frame(self.tab)
        title_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(title_frame, text=obj.name,
                  font=('Segoe UI', 16, 'bold'), foreground=obj.color).pack(side=tk.LEFT)

        enabled_var = tk.BooleanVar(value=obj.enabled)
        enabled_check = ttk.Checkbutton(title_frame, text="Показать", variable=enabled_var)
        enabled_check.pack(side=tk.RIGHT)
        self.vars["enabled"] = enabled_var

        self.vars.update({
            "color": tk.StringVar(value=obj.color),
            "style": tk.StringVar(value=obj.linestyle),
            "u_base": tk.StringVar(value=f"{obj.u_base:.0f}"),
            "i_base": tk.StringVar(value=f"{obj.i_base:.0f}"),
            "i_secondary": tk.StringVar(value=f"{obj.i_secondary:.1f}"),
            "u_secondary": tk.StringVar(value=f"{obj.u_secondary:.1f}"),
            "angle_phs": tk.StringVar(value=f"{obj.angle_phs:.1f}"),
            "angle_quad2": tk.StringVar(value=f"{obj.angle_quad2:.1f}"),
            "angle_quad4": tk.StringVar(value=f"{obj.angle_quad4:.1f}")
        })

        self._create_common_frames()
        self._bind_entry_events()
        enabled_var.trace('w', lambda *args: self._on_enabled_toggle())

    def _create_common_frames(self):
        """Создание фреймов для Common Settings"""
        params_frame = ttk.LabelFrame(self.tab, text="Общие параметры", padding=5)
        params_frame.pack(fill=tk.X, pady=5)

        grid = ttk.Frame(params_frame)
        grid.pack(fill=tk.X)

        entries = [
            ("U base (В):", "u_base", 0),
            ("I base (А):", "i_base", 1),
            ("I secondary (А):", "i_secondary", 2),
            ("U secondary (В):", "u_secondary", 3),
            ("Angle PHS:", "angle_phs", 4),
            ("Angle 2-й квадрант:", "angle_quad2", 5),
            ("Angle 4-й квадрант:", "angle_quad4", 6),
        ]

        for label, key, row in entries:
            ttk.Label(grid, text=label, font=('Segoe UI', 10)).grid(
                row=row, column=0, sticky=tk.W, pady=5
            )
            entry = FloatEntry(grid, textvariable=self.vars[key], width=12)
            entry.grid(row=row, column=1, sticky=tk.W, padx=10)
            self._entry_widgets.append(entry)

        self._create_style_frame()

    def _create_direction_frame(self):
        dir_frame = ttk.LabelFrame(self.tab, text="Направленность", padding=5)
        dir_frame.pack(fill=tk.X, pady=5)

        dir_combo = ttk.Combobox(dir_frame, textvariable=self.vars["direction"],
                                 values=["forward", "reverse", "non-directional"],
                                 state="readonly")
        dir_combo.pack(fill=tk.X)
        dir_combo.bind('<<ComboboxSelected>>', lambda e: self._apply_changes())

    def _create_phph_frame(self):
        phph_frame = ttk.LabelFrame(self.tab, text="Параметры Ph-Ph", padding=5)
        phph_frame.pack(fill=tk.X, pady=5)

        grid = ttk.Frame(phph_frame)
        grid.pack(fill=tk.X)

        entries = [
            ("X₁ (Ом):", "x1", 0, 0),
            ("R₁ (Ом):", "r1", 0, 2),
            ("RFPP (Ом):", "rfpp", 1, 0),
        ]

        for label, key, row, col in entries:
            ttk.Label(grid, text=label, font=('Segoe UI', 9)).grid(
                row=row, column=col, sticky=tk.W, pady=2
            )
            entry = FloatEntry(grid, textvariable=self.vars[key], width=8)
            entry.grid(row=row, column=col + 1, sticky=tk.W, padx=5)
            self._entry_widgets.append(entry)

    def _create_phe_frame(self):
        phe_frame = ttk.LabelFrame(self.tab, text="Параметры Ph-E", padding=5)
        phe_frame.pack(fill=tk.X, pady=5)

        grid = ttk.Frame(phe_frame)
        grid.pack(fill=tk.X)

        entries = [
            ("X₀ (Ом):", "x0", 0, 0),
            ("R₀ (Ом):", "r0", 0, 2),
            ("RFPE (Ом):", "rfpe", 1, 0),
        ]

        for label, key, row, col in entries:
            ttk.Label(grid, text=label, font=('Segoe UI', 9)).grid(
                row=row, column=col, sticky=tk.W, pady=2
            )
            entry = FloatEntry(grid, textvariable=self.vars[key], width=8)
            entry.grid(row=row, column=col + 1, sticky=tk.W, padx=5)
            self._entry_widgets.append(entry)

    def _create_style_frame(self):
        style_frame = ttk.LabelFrame(self.tab, text="Оформление", padding=5)
        style_frame.pack(fill=tk.X, pady=5)

        grid = ttk.Frame(style_frame)
        grid.pack(fill=tk.X)

        ttk.Label(grid, text="Цвет:", font=('Segoe UI', 9)).grid(
            row=0, column=0, sticky=tk.W, pady=2
        )
        color_combo = ColorCombo(grid, textvariable=self.vars["color"],
                                 colors=self.colors, width=15)
        color_combo.grid(row=0, column=1, sticky=tk.W, padx=5)
        color_combo.bind('<<ComboboxSelected>>', lambda e: self._apply_changes())

        ttk.Label(grid, text="Стиль:", font=('Segoe UI', 9)).grid(
            row=1, column=0, sticky=tk.W, pady=2
        )
        style_combo = ttk.Combobox(grid, textvariable=self.vars["style"],
                                   values=[s[0] for s in self.linestyles],
                                   state="readonly", width=12)
        style_combo.grid(row=1, column=1, sticky=tk.W, padx=5)
        style_combo.bind('<<ComboboxSelected>>', lambda e: self._apply_changes())

    def _bind_entry_events(self):
        """Привязка событий для полей ввода"""
        for entry in self._entry_widgets:
            entry._zone_tab = self

            # Основные события
            entry.bind('<FocusIn>', self._on_focus_in)
            entry.bind('<FocusOut>', self._on_focus_out)

            # Для Enter используем прямой метод
            entry.entry.bind('<Return>', self._on_enter_pressed)
            entry.entry.bind('<KP_Enter>', self._on_enter_pressed)

            # Escape для отмены
            entry.entry.bind('<Escape>', self._cancel_changes)

    def _on_focus_in(self, event):
        """Запоминаем поле, в которое вошёл фокус"""
        self._current_entry = event.widget

    def _on_focus_out(self, event):
        """Потеря фокуса - применяем изменения"""
        if not self._updating:
            self._apply_changes()

    def _on_enter_pressed(self, event):
        """Нажатие Enter - применяем изменения и переходим к следующему полю"""
        if self._updating:
            return "break"

        self._updating = True

        try:
            # Применяем изменения
            self._apply_changes()

            # Находим текущий виджет
            current_widget = event.widget

            # Перемещаемся к следующему полю
            try:
                # Пробуем найти следующий виджет в табе
                next_widget = current_widget.tk_focusNext()
                if next_widget and next_widget.winfo_exists():
                    # Если это Entry внутри FloatEntry, фокусируем его
                    if isinstance(next_widget, ttk.Entry):
                        next_widget.focus_set()
                    else:
                        next_widget.focus_set()
                else:
                    self.tab.focus_set()
            except Exception:
                self.tab.focus_set()

            self._current_entry = None

        finally:
            self._updating = False

        return "break"

    def _apply_changes(self, event=None):
        """Применение изменений после подтверждения (FocusOut или Enter)"""
        if self._updating:
            return

        self._updating = True

        try:
            obj = self.zone

            # Общие параметры
            if "enabled" in self.vars:
                obj.enabled = self.vars["enabled"].get()
            if "color" in self.vars:
                obj.color = self.vars["color"].get()
            if "style" in self.vars:
                obj.linestyle = self.vars["style"].get()

            # Для DZ зон
            if not self.is_common:
                obj.direction_mode = self.vars["direction"].get()
                obj.x1 = float(self.vars["x1"].get().replace(',', '.'))
                obj.r1 = float(self.vars["r1"].get().replace(',', '.'))
                obj.rfpp = float(self.vars["rfpp"].get().replace(',', '.'))
                obj.x0 = float(self.vars["x0"].get().replace(',', '.'))
                obj.r0 = float(self.vars["r0"].get().replace(',', '.'))
                obj.rfpe = float(self.vars["rfpe"].get().replace(',', '.'))

            # Для Common Settings
            if self.is_common:
                obj.u_base = float(self.vars["u_base"].get().replace(',', '.'))
                obj.i_base = float(self.vars["i_base"].get().replace(',', '.'))
                obj.i_secondary = float(self.vars["i_secondary"].get().replace(',', '.'))
                obj.u_secondary = float(self.vars["u_secondary"].get().replace(',', '.'))
                obj.angle_phs = float(self.vars["angle_phs"].get().replace(',', '.'))
                obj.angle_quad2 = float(self.vars["angle_quad2"].get().replace(',', '.'))
                obj.angle_quad4 = float(self.vars["angle_quad4"].get().replace(',', '.'))

            # Обновляем график
            self.viz.plot_characteristics(keep_limits=True)
            self.viz._update_status()

        except ValueError as e:
            self.viz._show_notification(f"Ошибка: {e}")
        finally:
            self._updating = False

    def _cancel_changes(self, event):
        """Отмена изменений при нажатии Escape"""
        obj = self.zone
        if not self.is_common:
            self.vars["x1"].set(f"{obj.x1:.2f}")
            self.vars["r1"].set(f"{obj.r1:.2f}")
            self.vars["rfpp"].set(f"{obj.rfpp:.2f}")
            self.vars["x0"].set(f"{obj.x0:.2f}")
            self.vars["r0"].set(f"{obj.r0:.2f}")
            self.vars["rfpe"].set(f"{obj.rfpe:.2f}")
        else:
            self.vars["u_base"].set(f"{obj.u_base:.0f}")
            self.vars["i_base"].set(f"{obj.i_base:.0f}")
            self.vars["i_secondary"].set(f"{obj.i_secondary:.1f}")
            self.vars["u_secondary"].set(f"{obj.u_secondary:.1f}")
            self.vars["angle_phs"].set(f"{obj.angle_phs:.1f}")
            self.vars["angle_quad2"].set(f"{obj.angle_quad2:.1f}")
            self.vars["angle_quad4"].set(f"{obj.angle_quad4:.1f}")

        self.viz._show_notification("Изменения отменены")

        # Снимаем фокус
        if self._current_entry:
            try:
                next_widget = self._current_entry.tk_focusNext()
                if next_widget and next_widget.winfo_exists():
                    next_widget.focus_set()
                else:
                    self.tab.focus_set()
            except:
                self.tab.focus_set()
            self._current_entry = None

    def _on_enabled_toggle(self):
        """Обработка включения/отключения - сразу обновляем"""
        obj = self.zone
        obj.enabled = self.vars["enabled"].get()
        self.viz.plot_characteristics(keep_limits=True)
        self.viz._update_status()
