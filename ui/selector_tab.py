# -*- coding: utf-8 -*-
"""
Вкладка для настройки фазового селектора FDPSPDIS
"""

import tkinter as tk
from tkinter import ttk

from widgets.color_combo import ColorCombo
from widgets.float_entry import FloatEntry
from widgets.modern_button import ModernButton


class SelectorTab:
    """Вкладка для настройки фазового селектора FDPSPDIS"""

    def __init__(self, notebook, selector_settings, visualizer, colors, linestyles):
        self.selector = selector_settings
        self.viz = visualizer
        self.colors = colors
        self.linestyles = linestyles
        self._entry_widgets = []
        self._current_entry = None

        self.tab = ttk.Frame(notebook, padding=15)
        notebook.add(self.tab, text="⚡ Фазовый селектор")

        self.vars = {}
        self._create_widgets()
        self.viz.selector = selector_settings

    def _create_widgets(self):
        """Создание всех виджетов на вкладке"""
        title_frame = ttk.Frame(self.tab)
        title_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(
            title_frame,
            text="Фазовый селектор FDPSPDIS",
            font=('Segoe UI', 16, 'bold'),
            foreground='#9C27B0'
        ).pack(side=tk.LEFT)

        enabled_var = tk.BooleanVar(value=self.selector.enabled)
        enabled_check = ttk.Checkbutton(
            title_frame,
            text="Показать на графике",
            variable=enabled_var
        )
        enabled_check.pack(side=tk.RIGHT)
        self.vars["enabled"] = enabled_var

        ttk.Separator(self.tab).pack(fill=tk.X, pady=10)

        self._create_main_params()
        ttk.Separator(self.tab).pack(fill=tk.X, pady=10)

        self._create_phph_params()
        ttk.Separator(self.tab).pack(fill=tk.X, pady=10)

        self._create_phe_params()
        ttk.Separator(self.tab).pack(fill=tk.X, pady=10)

        self._create_style_params()

        button_frame = ttk.Frame(self.tab)
        button_frame.pack(fill=tk.X, pady=20)

        ModernButton(
            button_frame,
            text="Сбросить к рекомендуемым",
            icon="↺",
            style="info",
            width=25,
            command=self._reset_to_default
        ).pack(side=tk.RIGHT)

        self._bind_entry_events()
        enabled_var.trace('w', lambda *args: self._on_enabled_toggle())

    def _create_main_params(self):
        main_frame = ttk.LabelFrame(self.tab, text="Основные параметры", padding=5)
        main_frame.pack(fill=tk.X, pady=5)

        grid = ttk.Frame(main_frame)
        grid.pack(fill=tk.X)

        entries = [
            ("X₁ (Ом/фаза):", "x1", 0),
            ("X₀ (Ом/фаза):", "x0", 1),
        ]

        for label, key, row in entries:
            ttk.Label(grid, text=label, font=('Segoe UI', 10)).grid(
                row=row, column=0, sticky=tk.W, pady=4
            )
            var = tk.StringVar(value=f"{getattr(self.selector, key):.2f}")
            entry = FloatEntry(grid, textvariable=var, width=10)
            entry.grid(row=row, column=1, sticky=tk.W, padx=10)
            self.vars[key] = var
            self._entry_widgets.append(entry)

        ttk.Separator(grid, orient='horizontal').grid(
            row=3, column=0, columnspan=3, sticky=tk.EW, pady=10
        )

        ttk.Label(grid, text="--- Отстройка от нагрузки (Load Encroachment) ---",
                  font=('Segoe UI', 10, 'bold'), foreground='#F57F17').grid(
            row=4, column=0, sticky=tk.W, pady=4, columnspan=2
        )

        load_enabled_var = tk.BooleanVar(value=self.selector.load_enabled)
        load_check = ttk.Checkbutton(grid, text="Включить отстройку от нагрузки",
                                     variable=load_enabled_var)
        load_check.grid(row=5, column=0, sticky=tk.W, pady=4, columnspan=2)
        self.vars["load_enabled"] = load_enabled_var
        load_enabled_var.trace('w', lambda *args: self._on_load_toggle())

        load_entries = [
            ("RLdFw (Ом) - вперед:", "rld_forward", 6),
            ("RLdRv (Ом) - назад:", "rld_reverse", 7),
            ("ArgLd (градусы) - угол нагрузки:", "arg_load", 8),
        ]

        for label, key, row in load_entries:
            ttk.Label(grid, text=label, font=('Segoe UI', 10)).grid(
                row=row, column=0, sticky=tk.W, pady=4
            )
            var = tk.StringVar(value=f"{getattr(self.selector, key):.2f}")
            entry = FloatEntry(grid, textvariable=var, width=10)
            entry.grid(row=row, column=1, sticky=tk.W, padx=10)
            self.vars[key] = var
            self._entry_widgets.append(entry)

    def _create_phph_params(self):
        phph_frame = ttk.LabelFrame(self.tab, text="Параметры для Ph-Ph", padding=5)
        phph_frame.pack(fill=tk.X, pady=5)

        header = ttk.Frame(phph_frame)
        header.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(header, text="∿", font=('Segoe UI', 14)).pack(side=tk.LEFT, padx=5)
        ttk.Label(header, text="Междуфазные повреждения", font=('Segoe UI', 10, 'italic')).pack(side=tk.LEFT)

        grid = ttk.Frame(phph_frame)
        grid.pack(fill=tk.X)

        entries = [
            ("RFFwPP (Ом/петля):", "rfpp_forward", 0),
            ("RFRvPP (Ом/петля):", "rfpp_reverse", 1),
        ]

        for label, key, row in entries:
            ttk.Label(grid, text=label, font=('Segoe UI', 10)).grid(
                row=row, column=0, sticky=tk.W, pady=5, padx=20
            )
            var = tk.StringVar(value=f"{getattr(self.selector, key):.2f}")
            entry = FloatEntry(grid, textvariable=var, width=10)
            entry.grid(row=row, column=1, sticky=tk.W, padx=10)
            self.vars[key] = var
            self._entry_widgets.append(entry)

    def _create_phe_params(self):
        phe_frame = ttk.LabelFrame(self.tab, text="Параметры для Ph-E", padding=5)
        phe_frame.pack(fill=tk.X, pady=5)

        header = ttk.Frame(phe_frame)
        header.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(header, text="⏚", font=('Segoe UI', 14)).pack(side=tk.LEFT, padx=5)
        ttk.Label(header, text="Однофазные повреждения на землю", font=('Segoe UI', 10, 'italic')).pack(side=tk.LEFT)

        grid = ttk.Frame(phe_frame)
        grid.pack(fill=tk.X)

        entries = [
            ("RFFwPE (Ом/петля):", "rfpe_forward", 0),
            ("RFRvPE (Ом/петля):", "rfpe_reverse", 1),
        ]

        for label, key, row in entries:
            ttk.Label(grid, text=label, font=('Segoe UI', 10)).grid(
                row=row, column=0, sticky=tk.W, pady=5, padx=20
            )
            var = tk.StringVar(value=f"{getattr(self.selector, key):.2f}")
            entry = FloatEntry(grid, textvariable=var, width=10)
            entry.grid(row=row, column=1, sticky=tk.W, padx=10)
            self.vars[key] = var
            self._entry_widgets.append(entry)

    def _create_style_params(self):
        style_frame = ttk.LabelFrame(self.tab, text="Оформление", padding=5)
        style_frame.pack(fill=tk.X, pady=5)

        grid = ttk.Frame(style_frame)
        grid.pack(fill=tk.X)

        ttk.Label(grid, text="Цвет:", font=('Segoe UI', 10)).grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        color_var = tk.StringVar(value=self.selector.color)
        color_combo = ColorCombo(grid, textvariable=color_var, colors=self.colors, width=20)
        color_combo.grid(row=0, column=1, sticky=tk.W, padx=10)
        self.vars["color"] = color_var
        color_combo.bind('<<ComboboxSelected>>', lambda e: self._apply_changes())

        ttk.Label(grid, text="Стиль линии:", font=('Segoe UI', 10)).grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        style_var = tk.StringVar(value=self.selector.linestyle)
        style_combo = ttk.Combobox(
            grid,
            textvariable=style_var,
            values=[s[0] for s in self.linestyles],
            state="readonly",
            width=18
        )
        style_combo.grid(row=1, column=1, sticky=tk.W, padx=10)
        self.vars["linestyle"] = style_var
        style_combo.bind('<<ComboboxSelected>>', lambda e: self._apply_changes())

        ttk.Label(grid, text="Прозрачность:", font=('Segoe UI', 10)).grid(
            row=2, column=0, sticky=tk.W, pady=5
        )
        opacity_var = tk.StringVar(value=f"{self.selector.opacity:.1f}")
        opacity_frame = ttk.Frame(grid)
        opacity_frame.grid(row=2, column=1, sticky=tk.W, padx=10)
        entry = FloatEntry(opacity_frame, textvariable=opacity_var, width=6)
        entry.pack(side=tk.LEFT)
        self.vars["opacity"] = opacity_var
        self._entry_widgets.append(entry)

        ttk.Label(opacity_frame, text="(0.0-1.0)", font=('Segoe UI', 8), foreground='#666').pack(side=tk.LEFT, padx=5)

    def _bind_entry_events(self):
        """Привязка событий для полей ввода"""
        for entry in self._entry_widgets:
            entry._selector_tab = self

            entry.bind('<FocusIn>', self._on_focus_in)
            entry.bind('<FocusOut>', self._on_focus_out)

            # Для Enter используем прямой метод
            entry.entry.bind('<Return>', self._on_enter_pressed)
            entry.entry.bind('<KP_Enter>', self._on_enter_pressed)

            entry.entry.bind('<Escape>', self._cancel_changes)

    def _on_focus_in(self, event):
        self._current_entry = event.widget

    def _on_focus_out(self, event):
        self._apply_changes()

    def _on_enter_pressed(self, event):
        """Нажатие Enter - применяем изменения и переходим к следующему полю"""
        self._apply_changes()
        if self._current_entry:
            try:
                next_widget = self._current_entry.entry.tk_focusNext()
                if next_widget and next_widget.winfo_exists():
                    next_widget.focus_set()
                else:
                    self.tab.focus_set()
            except:
                self.tab.focus_set()
            self._current_entry = None
        return "break"

    def _apply_changes(self, event=None):
        try:
            self.selector.enabled = self.vars["enabled"].get()
            self.selector.load_enabled = self.vars["load_enabled"].get()

            self.selector.x1 = float(self.vars["x1"].get().replace(',', '.'))
            self.selector.x0 = float(self.vars["x0"].get().replace(',', '.'))
            self.selector.rfpp_forward = float(self.vars["rfpp_forward"].get().replace(',', '.'))
            self.selector.rfpp_reverse = float(self.vars["rfpp_reverse"].get().replace(',', '.'))
            self.selector.rfpe_forward = float(self.vars["rfpe_forward"].get().replace(',', '.'))
            self.selector.rfpe_reverse = float(self.vars["rfpe_reverse"].get().replace(',', '.'))
            self.selector.rld_forward = float(self.vars["rld_forward"].get().replace(',', '.'))
            self.selector.rld_reverse = float(self.vars["rld_reverse"].get().replace(',', '.'))
            self.selector.arg_load = float(self.vars["arg_load"].get().replace(',', '.'))
            self.selector.color = self.vars["color"].get()
            self.selector.linestyle = self.vars["linestyle"].get()
            self.selector.opacity = float(self.vars["opacity"].get().replace(',', '.'))

            self.viz.plot_characteristics(keep_limits=True)
            self.viz._update_status()

        except ValueError as e:
            self.viz._show_notification(f"Ошибка: {e}")

    def _cancel_changes(self, event):
        self.vars["x1"].set(f"{self.selector.x1:.2f}")
        self.vars["x0"].set(f"{self.selector.x0:.2f}")
        self.vars["rfpp_forward"].set(f"{self.selector.rfpp_forward:.2f}")
        self.vars["rfpp_reverse"].set(f"{self.selector.rfpp_reverse:.2f}")
        self.vars["rfpe_forward"].set(f"{self.selector.rfpe_forward:.2f}")
        self.vars["rfpe_reverse"].set(f"{self.selector.rfpe_reverse:.2f}")
        self.vars["rld_forward"].set(f"{self.selector.rld_forward:.2f}")
        self.vars["rld_reverse"].set(f"{self.selector.rld_reverse:.2f}")
        self.vars["arg_load"].set(f"{self.selector.arg_load:.2f}")
        self.vars["opacity"].set(f"{self.selector.opacity:.1f}")
        self.viz._show_notification("Изменения отменены")

        if self._current_entry:
            try:
                next_widget = self._current_entry.entry.tk_focusNext()
                if next_widget and next_widget.winfo_exists():
                    next_widget.focus_set()
                else:
                    self.tab.focus_set()
            except:
                self.tab.focus_set()
            self._current_entry = None

    def _on_enabled_toggle(self):
        self.selector.enabled = self.vars["enabled"].get()
        self.viz.plot_characteristics(keep_limits=True)
        self.viz._update_status()

    def _on_load_toggle(self):
        self.selector.load_enabled = self.vars["load_enabled"].get()
        self.viz.plot_characteristics(keep_limits=True)
        self.viz._update_status()

    def _reset_to_default(self):
        self.vars["x1"].set("5.0")
        self.vars["x0"].set("15.0")
        self.vars["rfpp_forward"].set("8.0")
        self.vars["rfpp_reverse"].set("4.0")
        self.vars["rfpe_forward"].set("12.0")
        self.vars["rfpe_reverse"].set("6.0")
        self.vars["load_enabled"].set(True)
        self.vars["rld_forward"].set("8.0")
        self.vars["rld_reverse"].set("3.0")
        self.vars["arg_load"].set("30.0")
        self.vars["color"].set("#9C27B0")
        self.vars["linestyle"].set("-")
        self.vars["opacity"].set("0.8")
        self._apply_changes()
        self.viz._show_notification("Сброшено к рекомендуемым значениям")
