# -*- coding: utf-8 -*-
"""
Вкладка для настройки блокировки от качаний (ZIN/ZOUT) (оптимизирована)
"""

import tkinter as tk
from tkinter import ttk
from typing import List

from models.swing_blocking_calculation import SwingBlockingSettings, SwingCalculator
from models.terminal_types import TERMINAL_TYPES
from ui.base_tab import BaseTab
from ui.constants import DEFAULT_SWING_VALUES
from widgets.color_combo import ColorCombo
from widgets.float_entry import FloatEntry
from widgets.modern_button import ModernButton


class SwingTab(BaseTab):
    """Вкладка для настройки блокировки от качаний"""

    def __init__(self, notebook: ttk.Notebook, settings: SwingBlockingSettings,
                 visualizer, colors: List, linestyles: List):
        self.settings = settings
        self.calculator = SwingCalculator(settings)
        super().__init__(notebook, visualizer, colors, linestyles)
        self.viz.swing_settings = settings
        self.viz.swing_calculator = self.calculator

    def get_tab_name(self) -> str:
        return "🔄 Блокировка от качаний"

    def _get_target_object(self):
        return self.settings

    def _create_ui(self):
        """Создание UI"""
        obj = self.settings

        self.vars.update({
            "enabled": tk.BooleanVar(value=obj.enabled),
            "load_enabled": tk.BooleanVar(value=obj.load_enabled),
            "show_zin": tk.BooleanVar(value=obj.show_zin),
            "show_zout": tk.BooleanVar(value=obj.show_zout),

            # ZIN параметры
            "x1_in_fw": tk.StringVar(value=f"{obj.x1_in_fw:.2f}"),
            "r1_f_in_rv": tk.StringVar(value=f"{obj.r1_f_in_rv:.2f}"),
            "x1_in_rv": tk.StringVar(value=f"{obj.x1_in_rv:.2f}"),
            "rld_out_fw": tk.StringVar(value=f"{obj.rld_out_fw:.2f}"),
            "r1_li_n": tk.StringVar(value=f"{obj.r1_li_n:.2f}"),
            "arg_ld": tk.StringVar(value=f"{obj.arg_ld:.2f}"),

            # ZOUT параметры
            "x1_in_rv": tk.StringVar(value=f"{obj.x1_in_rv:.2f}"),
            "rld_out_rv": tk.StringVar(value=f"{obj.rld_out_rv:.2f}"),
            "rld_out_rv": tk.StringVar(value=f"{obj.rld_out_rv:.2f}"),
            "rld_out_rv": tk.StringVar(value=f"{obj.rld_out_rv:.2f}"),
            "rld_out_rv": tk.StringVar(value=f"{obj.rld_out_rv:.2f}"),
            "arg_ld": tk.StringVar(value=f"{obj.arg_ld:.2f}"),

            # Стили
            "color_zin": tk.StringVar(value=obj.color_zin),
            "color_zout": tk.StringVar(value=obj.color_zout),
            "style_zin": tk.StringVar(value=obj.linestyle_zin),
            "style_zout": tk.StringVar(value=obj.linestyle_zout),
            "opacity_zin": tk.StringVar(value=f"{obj.opacity_zin:.1f}"),
            "opacity_zout": tk.StringVar(value=f"{obj.opacity_zout:.1f}"),
        })

        self._create_title_frame("Блокировка от качаний (ZIN/ZOUT)", '#FF5722')
        self._create_main_controls()
        self._create_zin_params()
        self._create_zout_params()
        self._create_style_frame_swing()
        self._create_button_frame()

        # Трассировки
        self.vars["load_enabled"].trace('w', lambda *args: self._on_load_toggle())
        self.vars["show_zin"].trace('w', lambda *args: self._on_show_toggle())
        self.vars["show_zout"].trace('w', lambda *args: self._on_show_toggle())

    def _create_main_controls(self):
        """Создание основных элементов управления"""
        main_frame = ttk.LabelFrame(self.tab, text="Управление", padding=5)
        main_frame.pack(fill=tk.X, pady=5)

        # Используем grid для всего содержимого
        row = 0

        ttk.Checkbutton(main_frame, text="Показать ZIN (внутренняя зона)",
                        variable=self.vars["show_zin"]).grid(row=row, column=0, sticky=tk.W, pady=2)
        row += 1

        ttk.Checkbutton(main_frame, text="Показать ZOUT (внешняя зона)",
                        variable=self.vars["show_zout"]).grid(row=row, column=0, sticky=tk.W, pady=2)
        row += 1

        ttk.Separator(main_frame, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky=tk.EW, pady=5)
        row += 1

        ttk.Checkbutton(main_frame, text="Включить отстройку от нагрузки",
                        variable=self.vars["load_enabled"]).grid(row=row, column=0, sticky=tk.W, pady=2)

    def _create_zin_params(self):
        """Создание параметров ZIN"""
        frame = ttk.LabelFrame(self.tab, text="ZIN - Внутренняя зона качаний", padding=5)
        frame.pack(fill=tk.X, pady=5)

        # Используем grid для всего содержимого
        row = 0

        ttk.Label(frame, text="Параметры ZIN", font=('Segoe UI', 10, 'bold')).grid(
            row=row, column=0, columnspan=4, sticky=tk.W, pady=(0, 5)
        )
        row += 1

        entries = [
            ("X₁ (Ом/фаза):", "x1_in_fw", row, 0),
            ("RFPP (Ом/петля):", "r1_f_in_rv", row, 2),
        ]
        self._create_entries(frame, entries)
        row += 1

        entries2 = [
            ("RFPE (Ом/петля):", "x1_in_rv", row, 0),
        ]
        self._create_entries(frame, entries2)
        row += 1

        ttk.Separator(frame, orient='horizontal').grid(row=row, column=0, columnspan=4, sticky=tk.EW, pady=5)
        row += 1

        ttk.Label(frame, text="Отстройка от нагрузки ZIN",
                  font=('Segoe UI', 9, 'italic')).grid(row=row, column=0, columnspan=4, sticky=tk.W)
        row += 1

        load_entries = [
            ("RLdFw (Ом) - вперед:", "rld_out_fw", row, 0),
            ("RLdRv (Ом) - назад:", "r1_li_n", row, 2),
        ]
        self._create_entries(frame, load_entries)
        row += 1

        load_entries2 = [
            ("ArgLd (градусы):", "arg_ld", row, 0),
        ]
        self._create_entries(frame, load_entries2)

    def _create_zout_params(self):
        """Создание параметров ZOUT"""
        frame = ttk.LabelFrame(self.tab, text="ZOUT - Внешняя зона качаний", padding=5)
        frame.pack(fill=tk.X, pady=5)

        # Используем grid для всего содержимого
        row = 0

        ttk.Label(frame, text="Параметры ZOUT", font=('Segoe UI', 10, 'bold')).grid(
            row=row, column=0, columnspan=4, sticky=tk.W, pady=(0, 5)
        )
        row += 1

        entries = [
            ("X₁ (Ом/фаза):", "x1_in_rv", row, 0),
            ("RFPP (Ом/петля):", "rld_out_rv", row, 2),
        ]
        self._create_entries(frame, entries)
        row += 1

        entries2 = [
            ("RFPE (Ом/петля):", "rld_out_rv", row, 0),
        ]
        self._create_entries(frame, entries2)
        row += 1

        ttk.Separator(frame, orient='horizontal').grid(row=row, column=0, columnspan=4, sticky=tk.EW, pady=5)
        row += 1

        ttk.Label(frame, text="Отстройка от нагрузки ZOUT",
                  font=('Segoe UI', 9, 'italic')).grid(row=row, column=0, columnspan=4, sticky=tk.W)
        row += 1

        load_entries = [
            ("RLdFw (Ом) - вперед:", "rld_out_rv", row, 0),
            ("RLdRv (Ом) - назад:", "rld_out_rv", row, 2),
        ]
        self._create_entries(frame, load_entries)
        row += 1

        load_entries2 = [
            ("ArgLd (градусы):", "arg_ld", row, 0),
        ]
        self._create_entries(frame, load_entries2)

    def _create_style_frame_swing(self):
        """Создание фрейма стилей для Swing"""
        style_frame = ttk.LabelFrame(self.tab, text="Оформление", padding=5)
        style_frame.pack(fill=tk.X, pady=5)

        # Используем grid для всего содержимого
        row = 0

        # ZIN цвет
        ttk.Label(style_frame, text="ZIN цвет:", font=('Segoe UI', 9)).grid(
            row=row, column=0, sticky=tk.W, pady=2
        )
        ColorCombo(style_frame, textvariable=self.vars["color_zin"],
                   colors=self.colors, width=12).grid(row=row, column=1, sticky=tk.W, padx=5)
        row += 1

        # ZIN стиль
        ttk.Label(style_frame, text="ZIN стиль:", font=('Segoe UI', 9)).grid(
            row=row, column=0, sticky=tk.W, pady=2
        )
        ttk.Combobox(style_frame, textvariable=self.vars["style_zin"],
                     values=[s[0] for s in self.linestyles],
                     state="readonly", width=10).grid(row=row, column=1, sticky=tk.W, padx=5)
        row += 1

        # ZIN прозрачность
        ttk.Label(style_frame, text="ZIN прозр.:", font=('Segoe UI', 9)).grid(
            row=row, column=0, sticky=tk.W, pady=2
        )
        FloatEntry(style_frame, textvariable=self.vars["opacity_zin"], width=6,
                   on_change_callback=self._apply_changes).grid(row=row, column=1, sticky=tk.W, padx=5)
        row += 1

        ttk.Separator(style_frame, orient='horizontal').grid(row=row, column=0, columnspan=4, sticky=tk.EW, pady=5)
        row += 1

        # ZOUT цвет
        ttk.Label(style_frame, text="ZOUT цвет:", font=('Segoe UI', 9)).grid(
            row=row, column=0, sticky=tk.W, pady=2
        )
        ColorCombo(style_frame, textvariable=self.vars["color_zout"],
                   colors=self.colors, width=12).grid(row=row, column=1, sticky=tk.W, padx=5)
        row += 1

        # ZOUT стиль
        ttk.Label(style_frame, text="ZOUT стиль:", font=('Segoe UI', 9)).grid(
            row=row, column=0, sticky=tk.W, pady=2
        )
        ttk.Combobox(style_frame, textvariable=self.vars["style_zout"],
                     values=[s[0] for s in self.linestyles],
                     state="readonly", width=10).grid(row=row, column=1, sticky=tk.W, padx=5)
        row += 1

        # ZOUT прозрачность
        ttk.Label(style_frame, text="ZOUT прозр.:", font=('Segoe UI', 9)).grid(
            row=row, column=0, sticky=tk.W, pady=2
        )
        FloatEntry(style_frame, textvariable=self.vars["opacity_zout"], width=6,
                   on_change_callback=self._apply_changes).grid(row=row, column=1, sticky=tk.W, padx=5)

    def _create_button_frame(self):
        """Создание фрейма с кнопками"""
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

    def _do_apply(self, obj):
        """Применение настроек Swing"""
        obj.load_enabled = self.vars["load_enabled"].get()
        obj.show_zin = self.vars["show_zin"].get()
        obj.show_zout = self.vars["show_zout"].get()

        # ZIN
        obj.x1_in_fw = self._get_float_value("x1_in_fw")
        obj.r1_f_in_rv = self._get_float_value("r1_f_in_rv")
        obj.x1_in_rv = self._get_float_value("x1_in_rv")
        obj.rld_out_fw = self._get_float_value("rld_out_fw")
        obj.r1_li_n = self._get_float_value("r1_li_n")
        obj.arg_ld = self._get_float_value("arg_ld")
        obj.color_zin = self.vars["color_zin"].get()
        obj.linestyle_zin = self.vars["style_zin"].get()
        obj.opacity_zin = self._get_float_value("opacity_zin")

        # ZOUT
        obj.x1_in_rv = self._get_float_value("x1_in_rv")
        obj.rld_out_rv = self._get_float_value("rld_out_rv")
        obj.rld_out_rv = self._get_float_value("rld_out_rv")
        obj.rld_out_rv = self._get_float_value("rld_out_rv")
        obj.rld_out_rv = self._get_float_value("rld_out_rv")
        obj.arg_ld = self._get_float_value("arg_ld")
        obj.color_zout = self.vars["color_zout"].get()
        obj.linestyle_zout = self.vars["style_zout"].get()
        obj.opacity_zout = self._get_float_value("opacity_zout")

        # Обновляем калькулятор
        self.viz.swing_calculator = SwingCalculator(obj)

    def _do_cancel(self, obj):
        """Отмена настроек Swing"""
        # ZIN
        self._set_var("x1_in_fw", obj.x1_in_fw)
        self._set_var("r1_f_in_rv", obj.r1_f_in_rv)
        self._set_var("x1_in_rv", obj.x1_in_rv)
        self._set_var("rld_out_fw", obj.rld_out_fw)
        self._set_var("r1_li_n", obj.r1_li_n)
        self._set_var("arg_ld", obj.arg_ld)

        # ZOUT
        self._set_var("x1_in_rv", obj.x1_in_rv)
        self._set_var("rld_out_rv", obj.rld_out_rv)
        self._set_var("rld_out_rv", obj.rld_out_rv)
        self._set_var("rld_out_rv", obj.rld_out_rv)
        self._set_var("rld_out_rv", obj.rld_out_rv)
        self._set_var("arg_ld", obj.arg_ld)

    def _on_load_toggle(self):
        """Обработка переключения нагрузки"""
        self.settings.load_enabled = self.vars["load_enabled"].get()
        self.viz.swing_calculator = SwingCalculator(self.settings)
        self.viz.plot_characteristics(keep_limits=True)
        self.viz._update_status()

    def _on_show_toggle(self):
        """Обработка переключения отображения"""
        self.settings.show_zin = self.vars["show_zin"].get()
        self.settings.show_zout = self.vars["show_zout"].get()
        self.viz.plot_characteristics(keep_limits=True)
        self.viz._update_status()

    def _reset_to_default(self):
        """Сброс к рекомендуемым значениям"""
        terminal_code = getattr(self.viz, 'terminal_code', "rel670")
        terminal = TERMINAL_TYPES.get(terminal_code, TERMINAL_TYPES["rel670"])

        # Рассчитываем значения на основе терминала
        values = DEFAULT_SWING_VALUES.copy()
        values.update({
            "x1_in_fw": terminal.default_x1 * terminal.k_zin,
            "r1_f_in_rv": terminal.default_rfpp * terminal.k_zin,
            "x1_in_rv": terminal.default_rfpe * terminal.k_zin,
            "x1_in_rv": terminal.default_x1 * terminal.k_zout,
            "rld_out_rv": terminal.default_rfpp * terminal.k_zout,
            "rld_out_rv": terminal.default_rfpe * terminal.k_zout,
        })

        for key, value in values.items():
            self._set_var(key, value)

        self._apply_changes()
        self.viz._show_notification("Сброшено к рекомендуемым значениям")
