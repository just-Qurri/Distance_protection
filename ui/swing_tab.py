# -*- coding: utf-8 -*-
"""
Вкладка для настройки блокировки от качаний (ZIN/ZOUT) (оптимизирована)
"""

import tkinter as tk
from tkinter import ttk
from typing import List

from models.swing_blocking import SwingBlockingSettings, SwingCalculator
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
            "x1_zin": tk.StringVar(value=f"{obj.x1_zin:.2f}"),
            "rfpp_zin": tk.StringVar(value=f"{obj.rfpp_zin:.2f}"),
            "rfpe_zin": tk.StringVar(value=f"{obj.rfpe_zin:.2f}"),
            "rld_forward_zin": tk.StringVar(value=f"{obj.rld_forward_zin:.2f}"),
            "rld_reverse_zin": tk.StringVar(value=f"{obj.rld_reverse_zin:.2f}"),
            "arg_load_zin": tk.StringVar(value=f"{obj.arg_load_zin:.2f}"),

            # ZOUT параметры
            "x1_zout": tk.StringVar(value=f"{obj.x1_zout:.2f}"),
            "rfpp_zout": tk.StringVar(value=f"{obj.rfpp_zout:.2f}"),
            "rfpe_zout": tk.StringVar(value=f"{obj.rfpe_zout:.2f}"),
            "rld_forward_zout": tk.StringVar(value=f"{obj.rld_forward_zout:.2f}"),
            "rld_reverse_zout": tk.StringVar(value=f"{obj.rld_reverse_zout:.2f}"),
            "arg_load_zout": tk.StringVar(value=f"{obj.arg_load_zout:.2f}"),

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
            ("X₁ (Ом/фаза):", "x1_zin", row, 0),
            ("RFPP (Ом/петля):", "rfpp_zin", row, 2),
        ]
        self._create_entries(frame, entries)
        row += 1

        entries2 = [
            ("RFPE (Ом/петля):", "rfpe_zin", row, 0),
        ]
        self._create_entries(frame, entries2)
        row += 1

        ttk.Separator(frame, orient='horizontal').grid(row=row, column=0, columnspan=4, sticky=tk.EW, pady=5)
        row += 1

        ttk.Label(frame, text="Отстройка от нагрузки ZIN",
                  font=('Segoe UI', 9, 'italic')).grid(row=row, column=0, columnspan=4, sticky=tk.W)
        row += 1

        load_entries = [
            ("RLdFw (Ом) - вперед:", "rld_forward_zin", row, 0),
            ("RLdRv (Ом) - назад:", "rld_reverse_zin", row, 2),
        ]
        self._create_entries(frame, load_entries)
        row += 1

        load_entries2 = [
            ("ArgLd (градусы):", "arg_load_zin", row, 0),
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
            ("X₁ (Ом/фаза):", "x1_zout", row, 0),
            ("RFPP (Ом/петля):", "rfpp_zout", row, 2),
        ]
        self._create_entries(frame, entries)
        row += 1

        entries2 = [
            ("RFPE (Ом/петля):", "rfpe_zout", row, 0),
        ]
        self._create_entries(frame, entries2)
        row += 1

        ttk.Separator(frame, orient='horizontal').grid(row=row, column=0, columnspan=4, sticky=tk.EW, pady=5)
        row += 1

        ttk.Label(frame, text="Отстройка от нагрузки ZOUT",
                  font=('Segoe UI', 9, 'italic')).grid(row=row, column=0, columnspan=4, sticky=tk.W)
        row += 1

        load_entries = [
            ("RLdFw (Ом) - вперед:", "rld_forward_zout", row, 0),
            ("RLdRv (Ом) - назад:", "rld_reverse_zout", row, 2),
        ]
        self._create_entries(frame, load_entries)
        row += 1

        load_entries2 = [
            ("ArgLd (градусы):", "arg_load_zout", row, 0),
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
        obj.x1_zin = self._get_float_value("x1_zin")
        obj.rfpp_zin = self._get_float_value("rfpp_zin")
        obj.rfpe_zin = self._get_float_value("rfpe_zin")
        obj.rld_forward_zin = self._get_float_value("rld_forward_zin")
        obj.rld_reverse_zin = self._get_float_value("rld_reverse_zin")
        obj.arg_load_zin = self._get_float_value("arg_load_zin")
        obj.color_zin = self.vars["color_zin"].get()
        obj.linestyle_zin = self.vars["style_zin"].get()
        obj.opacity_zin = self._get_float_value("opacity_zin")

        # ZOUT
        obj.x1_zout = self._get_float_value("x1_zout")
        obj.rfpp_zout = self._get_float_value("rfpp_zout")
        obj.rfpe_zout = self._get_float_value("rfpe_zout")
        obj.rld_forward_zout = self._get_float_value("rld_forward_zout")
        obj.rld_reverse_zout = self._get_float_value("rld_reverse_zout")
        obj.arg_load_zout = self._get_float_value("arg_load_zout")
        obj.color_zout = self.vars["color_zout"].get()
        obj.linestyle_zout = self.vars["style_zout"].get()
        obj.opacity_zout = self._get_float_value("opacity_zout")

        # Обновляем калькулятор
        self.viz.swing_calculator = SwingCalculator(obj)

    def _do_cancel(self, obj):
        """Отмена настроек Swing"""
        # ZIN
        self._set_var("x1_zin", obj.x1_zin)
        self._set_var("rfpp_zin", obj.rfpp_zin)
        self._set_var("rfpe_zin", obj.rfpe_zin)
        self._set_var("rld_forward_zin", obj.rld_forward_zin)
        self._set_var("rld_reverse_zin", obj.rld_reverse_zin)
        self._set_var("arg_load_zin", obj.arg_load_zin)

        # ZOUT
        self._set_var("x1_zout", obj.x1_zout)
        self._set_var("rfpp_zout", obj.rfpp_zout)
        self._set_var("rfpe_zout", obj.rfpe_zout)
        self._set_var("rld_forward_zout", obj.rld_forward_zout)
        self._set_var("rld_reverse_zout", obj.rld_reverse_zout)
        self._set_var("arg_load_zout", obj.arg_load_zout)

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
            "x1_zin": terminal.default_x1 * terminal.k_zin,
            "rfpp_zin": terminal.default_rfpp * terminal.k_zin,
            "rfpe_zin": terminal.default_rfpe * terminal.k_zin,
            "x1_zout": terminal.default_x1 * terminal.k_zout,
            "rfpp_zout": terminal.default_rfpp * terminal.k_zout,
            "rfpe_zout": terminal.default_rfpe * terminal.k_zout,
        })

        for key, value in values.items():
            self._set_var(key, value)

        self._apply_changes()
        self.viz._show_notification("Сброшено к рекомендуемым значениям")
