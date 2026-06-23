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

        self.tab = ttk.Frame(notebook, padding=15)
        notebook.add(self.tab, text="⚡ Фазовый селектор")

        self.vars = {}
        self._create_widgets()
        self.viz.selector = selector_settings

    def _create_widgets(self):
        """Создание всех виджетов на вкладке"""
        # Заголовок
        title_frame = ttk.Frame(self.tab)
        title_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(
            title_frame,
            text="Фазовый селектор FDPSPDIS",
            font=('Segoe UI', 16, 'bold'),
            foreground='#9C27B0'
        ).pack(side=tk.LEFT)

        # Включение/отключение
        enabled_var = tk.BooleanVar(value=self.selector.enabled)
        ttk.Checkbutton(
            title_frame,
            text="Показать на графике",
            variable=enabled_var,
            command=self._on_enabled_toggle
        ).pack(side=tk.RIGHT)
        self.vars["enabled"] = enabled_var

        ttk.Separator(self.tab).pack(fill=tk.X, pady=10)

        # Основные параметры
        self._create_main_params()

        ttk.Separator(self.tab).pack(fill=tk.X, pady=10)

        # Параметры Ph-Ph
        self._create_phph_params()

        ttk.Separator(self.tab).pack(fill=tk.X, pady=10)

        # Параметры Ph-E
        self._create_phe_params()

        ttk.Separator(self.tab).pack(fill=tk.X, pady=10)

        # Оформление
        self._create_style_params()

        # Кнопка сброса
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

        # Привязка изменений
        self._bind_traces()

    def _create_main_params(self):
        """Создание основных параметров с отстройкой от нагрузки"""
        main_frame = ttk.LabelFrame(self.tab, text="Основные параметры", padding=5)
        main_frame.pack(fill=tk.X, pady=5)

        grid = ttk.Frame(main_frame)
        grid.pack(fill=tk.X)

        # X1
        ttk.Label(grid, text="X₁ (Ом/фаза):", font=('Segoe UI', 10)).grid(
            row=0, column=0, sticky=tk.W, pady=4
        )
        x1_var = tk.StringVar(value=f"{self.selector.x1:.2f}")
        FloatEntry(grid, textvariable=x1_var, width=10).grid(
            row=0, column=1, sticky=tk.W, padx=10
        )
        self.vars["x1"] = x1_var

        # X0
        ttk.Label(grid, text="X₀ (Ом/фаза):", font=('Segoe UI', 10)).grid(
            row=1, column=0, sticky=tk.W, pady=4
        )
        x0_var = tk.StringVar(value=f"{self.selector.x0:.2f}")
        FloatEntry(grid, textvariable=x0_var, width=10).grid(
            row=1, column=1, sticky=tk.W, padx=10
        )
        self.vars["x0"] = x0_var

        # Направленность
        ttk.Label(grid, text="Направленность:", font=('Segoe UI', 10)).grid(
            row=2, column=0, sticky=tk.W, pady=4
        )
        direction_var = tk.StringVar(value=self.selector.direction_mode)
        dir_combo = ttk.Combobox(
            grid,
            textvariable=direction_var,
            values=["forward", "reverse", "non-directional"],
            state="readonly",
            width=15
        )
        dir_combo.grid(row=2, column=1, sticky=tk.W, padx=10)
        self.vars["direction"] = direction_var

        # ===== ОТСТРОЙКА ОТ НАГРУЗКИ =====
        ttk.Separator(grid, orient='horizontal').grid(
            row=3, column=0, columnspan=3, sticky=tk.EW, pady=10
        )

        ttk.Label(grid, text="--- Отстройка от нагрузки (Load Encroachment) ---",
                  font=('Segoe UI', 10, 'bold'), foreground='#F57F17').grid(
            row=4, column=0, sticky=tk.W, pady=4, columnspan=2
        )

        # Включение отстройки
        load_enabled_var = tk.BooleanVar(value=self.selector.load_enabled)
        ttk.Checkbutton(grid, text="Включить отстройку от нагрузки",
                        variable=load_enabled_var).grid(
            row=5, column=0, sticky=tk.W, pady=4, columnspan=2
        )
        self.vars["load_enabled"] = load_enabled_var

        # RLdFw
        ttk.Label(grid, text="RLdFw (Ом) - вперед:", font=('Segoe UI', 10)).grid(
            row=6, column=0, sticky=tk.W, pady=4
        )
        rld_fw_var = tk.StringVar(value=f"{self.selector.rld_forward:.2f}")
        FloatEntry(grid, textvariable=rld_fw_var, width=10).grid(
            row=6, column=1, sticky=tk.W, padx=10
        )
        self.vars["rld_forward"] = rld_fw_var

        # RLdRv
        ttk.Label(grid, text="RLdRv (Ом) - назад:", font=('Segoe UI', 10)).grid(
            row=7, column=0, sticky=tk.W, pady=4
        )
        rld_rv_var = tk.StringVar(value=f"{self.selector.rld_reverse:.2f}")
        FloatEntry(grid, textvariable=rld_rv_var, width=10).grid(
            row=7, column=1, sticky=tk.W, padx=10
        )
        self.vars["rld_reverse"] = rld_rv_var

        # ArgLd
        ttk.Label(grid, text="ArgLd (градусы) - угол нагрузки:", font=('Segoe UI', 10)).grid(
            row=8, column=0, sticky=tk.W, pady=4
        )
        arg_ld_var = tk.StringVar(value=f"{self.selector.arg_load:.1f}")
        FloatEntry(grid, textvariable=arg_ld_var, width=10).grid(
            row=8, column=1, sticky=tk.W, padx=10
        )
        self.vars["arg_load"] = arg_ld_var

    def _create_phph_params(self):
        """Создание параметров для Ph-Ph"""
        phph_frame = ttk.LabelFrame(self.tab, text="Параметры для Ph-Ph", padding=5)
        phph_frame.pack(fill=tk.X, pady=5)

        header = ttk.Frame(phph_frame)
        header.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(header, text="∿", font=('Segoe UI', 14)).pack(side=tk.LEFT, padx=5)
        ttk.Label(header, text="Междуфазные повреждения", font=('Segoe UI', 10, 'italic')).pack(side=tk.LEFT)

        grid = ttk.Frame(phph_frame)
        grid.pack(fill=tk.X)

        # RFFwPP - прямое направление
        ttk.Label(grid, text="RFFwPP (Ом/петля):", font=('Segoe UI', 10)).grid(
            row=0, column=0, sticky=tk.W, pady=5, padx=20
        )
        fw_pp_var = tk.StringVar(value=f"{self.selector.rfpp_forward:.2f}")
        FloatEntry(grid, textvariable=fw_pp_var, width=10).grid(
            row=0, column=1, sticky=tk.W, padx=10
        )
        self.vars["rfpp_forward"] = fw_pp_var

        # RFRvPP - обратное направление
        ttk.Label(grid, text="RFRvPP (Ом/петля):", font=('Segoe UI', 10)).grid(
            row=1, column=0, sticky=tk.W, pady=5, padx=20
        )
        rv_pp_var = tk.StringVar(value=f"{self.selector.rfpp_reverse:.2f}")
        FloatEntry(grid, textvariable=rv_pp_var, width=10).grid(
            row=1, column=1, sticky=tk.W, padx=10
        )
        self.vars["rfpp_reverse"] = rv_pp_var

    def _create_phe_params(self):
        """Создание параметров для Ph-E"""
        phe_frame = ttk.LabelFrame(self.tab, text="Параметры для Ph-E", padding=5)
        phe_frame.pack(fill=tk.X, pady=5)

        header = ttk.Frame(phe_frame)
        header.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(header, text="⏚", font=('Segoe UI', 14)).pack(side=tk.LEFT, padx=5)
        ttk.Label(header, text="Однофазные повреждения на землю", font=('Segoe UI', 10, 'italic')).pack(side=tk.LEFT)

        grid = ttk.Frame(phe_frame)
        grid.pack(fill=tk.X)

        # RFFwPE - прямое направление
        ttk.Label(grid, text="RFFwPE (Ом/петля):", font=('Segoe UI', 10)).grid(
            row=0, column=0, sticky=tk.W, pady=5, padx=20
        )
        fw_pe_var = tk.StringVar(value=f"{self.selector.rfpe_forward:.2f}")
        FloatEntry(grid, textvariable=fw_pe_var, width=10).grid(
            row=0, column=1, sticky=tk.W, padx=10
        )
        self.vars["rfpe_forward"] = fw_pe_var

        # RFRvPE - обратное направление
        ttk.Label(grid, text="RFRvPE (Ом/петля):", font=('Segoe UI', 10)).grid(
            row=1, column=0, sticky=tk.W, pady=5, padx=20
        )
        rv_pe_var = tk.StringVar(value=f"{self.selector.rfpe_reverse:.2f}")
        FloatEntry(grid, textvariable=rv_pe_var, width=10).grid(
            row=1, column=1, sticky=tk.W, padx=10
        )
        self.vars["rfpe_reverse"] = rv_pe_var

    def _create_style_params(self):
        """Создание параметров оформления"""
        style_frame = ttk.LabelFrame(self.tab, text="Оформление", padding=5)
        style_frame.pack(fill=tk.X, pady=5)

        grid = ttk.Frame(style_frame)
        grid.pack(fill=tk.X)

        # Цвет
        ttk.Label(grid, text="Цвет:", font=('Segoe UI', 10)).grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        color_var = tk.StringVar(value=self.selector.color)
        ColorCombo(grid, textvariable=color_var, colors=self.colors, width=20).grid(
            row=0, column=1, sticky=tk.W, padx=10
        )
        self.vars["color"] = color_var

        # Стиль линии
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

        # Прозрачность
        ttk.Label(grid, text="Прозрачность:", font=('Segoe UI', 10)).grid(
            row=2, column=0, sticky=tk.W, pady=5
        )
        opacity_var = tk.StringVar(value=f"{self.selector.opacity:.1f}")
        opacity_frame = ttk.Frame(grid)
        opacity_frame.grid(row=2, column=1, sticky=tk.W, padx=10)
        FloatEntry(opacity_frame, textvariable=opacity_var, width=6).pack(side=tk.LEFT)
        ttk.Label(opacity_frame, text="(0.0-1.0)", font=('Segoe UI', 8), foreground='#666').pack(side=tk.LEFT, padx=5)
        self.vars["opacity"] = opacity_var

    def _bind_traces(self):
        """Привязка отслеживания изменений переменных"""

        def update_selector(*args):
            try:
                # Общие параметры
                self.selector.enabled = self.vars["enabled"].get()
                self.selector.x1 = float(self.vars["x1"].get().replace(',', '.'))
                self.selector.x0 = float(self.vars["x0"].get().replace(',', '.'))
                self.selector.direction_mode = self.vars["direction"].get()

                # Параметры Ph-Ph
                self.selector.rfpp_forward = float(self.vars["rfpp_forward"].get().replace(',', '.'))
                self.selector.rfpp_reverse = float(self.vars["rfpp_reverse"].get().replace(',', '.'))

                # Параметры Ph-E
                self.selector.rfpe_forward = float(self.vars["rfpe_forward"].get().replace(',', '.'))
                self.selector.rfpe_reverse = float(self.vars["rfpe_reverse"].get().replace(',', '.'))

                # Параметры отстройки от нагрузки
                self.selector.load_enabled = self.vars["load_enabled"].get()
                self.selector.rld_forward = float(self.vars["rld_forward"].get().replace(',', '.'))
                self.selector.rld_reverse = float(self.vars["rld_reverse"].get().replace(',', '.'))
                self.selector.arg_load = float(self.vars["arg_load"].get().replace(',', '.'))

                # Оформление
                self.selector.color = self.vars["color"].get()
                self.selector.linestyle = self.vars["linestyle"].get()
                self.selector.opacity = float(self.vars["opacity"].get().replace(',', '.'))

                # Обновляем график
                if self.viz.update_job:
                    self.viz.root.after_cancel(self.viz.update_job)
                self.viz.update_job = self.viz.root.after(100, self.viz.deferred_update)

            except ValueError as e:
                print(f"Ошибка обновления: {e}")

        # Привязываем отслеживание ко всем переменным
        for var in self.vars.values():
            var.trace('w', update_selector)

    def _on_enabled_toggle(self):
        """Обработка включения/отключения селектора"""
        if self.viz.update_job:
            self.viz.root.after_cancel(self.viz.update_job)
        self.viz.update_job = self.viz.root.after(100, self.viz.deferred_update)

    def _reset_to_default(self):
        """Сброс к рекомендуемым значениям"""
        self.vars["x1"].set("5.0")
        self.vars["x0"].set("15.0")
        self.vars["rfpp_forward"].set("8.0")
        self.vars["rfpp_reverse"].set("4.0")
        self.vars["rfpe_forward"].set("12.0")
        self.vars["rfpe_reverse"].set("6.0")
        self.vars["direction"].set("forward")
        self.vars["load_enabled"].set(True)
        self.vars["rld_forward"].set("8.0")
        self.vars["rld_reverse"].set("3.0")
        self.vars["arg_load"].set("30.0")
        self.vars["color"].set("#9C27B0")
        self.vars["linestyle"].set("-")
        self.vars["opacity"].set("0.8")
        self._show_notification("Сброшено к рекомендуемым значениям")

    def _show_notification(self, message):
        """Показ уведомления"""
        if hasattr(self.viz, '_show_notification'):
            self.viz._show_notification(message)
        else:
            print(f"ℹ️ {message}")
