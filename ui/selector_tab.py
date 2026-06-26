# -*- coding: utf-8 -*-
"""
Вкладка для настройки фазового селектора FDPSPDIS (оптимизирована)
"""

import tkinter as tk
from tkinter import ttk

from models.selector_calculator import SelectorCalculator
from models.selector_default_settings import SelectorSettings
from ui.base_tab import BaseTab
from ui.constants import DEFAULT_SELECTOR_VALUES
from widgets.modern_button import ModernButton


class SelectorTab(BaseTab):
    """Вкладка для настройки фазового селектора"""

    def __init__(self, notebook, selector_settings: SelectorSettings, visualizer, colors, linestyles):
        self.selector = selector_settings
        super().__init__(notebook, visualizer, colors, linestyles)
        self.viz.selector = selector_settings
        self.viz.selector_calculator = SelectorCalculator(selector_settings)

    def get_tab_name(self) -> str:
        return "⚡ Фазовый селектор"

    def _get_target_object(self):
        return self.selector

    def _create_ui(self):
        """Создание UI для фазового селектора"""
        obj = self.selector

        self.vars.update({
            "enabled": tk.BooleanVar(value=obj.enabled),
            "color": tk.StringVar(value=obj.color),
            "style": tk.StringVar(value=obj.linestyle),
            "opacity": tk.StringVar(value=f"{obj.opacity:.1f}"),
            "load_enabled": tk.BooleanVar(value=obj.load_enabled),
            "x1": tk.StringVar(value=f"{obj.x1:.2f}"),
            "x0": tk.StringVar(value=f"{obj.x0:.2f}"),
            "rfpp_forward": tk.StringVar(value=f"{obj.rfpp_forward:.2f}"),
            "rfpp_reverse": tk.StringVar(value=f"{obj.rfpp_reverse:.2f}"),
            "rfpe_forward": tk.StringVar(value=f"{obj.rfpe_forward:.2f}"),
            "rfpe_reverse": tk.StringVar(value=f"{obj.rfpe_reverse:.2f}"),
            "rld_forward": tk.StringVar(value=f"{obj.rld_forward:.2f}"),
            "rld_reverse": tk.StringVar(value=f"{obj.rld_reverse:.2f}"),
            "arg_load": tk.StringVar(value=f"{obj.arg_load:.2f}"),
            "arg_load_phph": tk.StringVar(value=f"{obj.arg_load_phph:.2f}"),
            "arg_load_3ph": tk.StringVar(value=f"{obj.arg_load_3ph:.2f}"),
        })

        self._create_title_frame("Фазовый селектор FDPSPDIS", '#9C27B0')
        self._create_main_params()
        self._create_phph_params()
        self._create_phe_params()
        self._create_style_frame(self.tab, opacity_key="opacity")
        self._create_button_frame()

        # Трассировки
        self.vars["load_enabled"].trace('w', lambda *args: self._on_load_toggle())

    def _create_main_params(self):
        """Создание основных параметров"""
        main_frame = ttk.LabelFrame(self.tab, text="Основные параметры", padding=5)
        main_frame.pack(fill=tk.X, pady=5)

        # Используем grid для всего содержимого
        entries = [
            ("X₁ (Ом/фаза):", "x1", 0, 0),
            ("X₀ (Ом/фаза):", "x0", 1, 0),
        ]
        self._create_entries(main_frame, entries)

        # Разделитель - тоже через grid
        ttk.Separator(main_frame, orient='horizontal').grid(
            row=2, column=0, columnspan=4, sticky=tk.EW, pady=10
        )

        # Отстройка от нагрузки
        load_frame = ttk.Frame(main_frame)
        load_frame.grid(row=3, column=0, columnspan=4, sticky=tk.W, pady=4)

        ttk.Label(load_frame, text="--- Отстройка от нагрузки ---",
                  font=('Segoe UI', 10, 'bold'), foreground='#F57F17').pack(anchor=tk.W, pady=4)

        ttk.Checkbutton(load_frame, text="Включить отстройку от нагрузки",
                        variable=self.vars["load_enabled"]).pack(anchor=tk.W, pady=4)

        # Поля для нагрузки - используем отдельный фрейм с grid
        load_grid = ttk.Frame(main_frame)
        load_grid.grid(row=4, column=0, columnspan=4, sticky=tk.W, pady=4)

        load_entries = [
            ("RLdFw (Ом) - вперед:", "rld_forward", 0, 0),
            ("RLdRv (Ом) - назад:", "rld_reverse", 0, 2),
            ("ArgLd (градусы):", "arg_load", 1, 0),
            ("ArgLd Ph-Ph:", "arg_load_phph", 1, 2),
            ("ArgLd 3-Ph:", "arg_load_3ph", 2, 0),
        ]
        self._create_entries(load_grid, load_entries)

    def _create_phph_params(self):
        """Создание фрейма параметров Ph-Ph"""
        phph_frame = ttk.LabelFrame(self.tab, text="Параметры для Ph-Ph", padding=5)
        phph_frame.pack(fill=tk.X, pady=5)

        # Используем grid для всего содержимого
        ttk.Label(phph_frame, text="∿ Междуфазные повреждения",
                  font=('Segoe UI', 10, 'italic')).grid(row=0, column=0, columnspan=4, sticky=tk.W, pady=(0, 10))

        entries = [
            ("RFFwPP (Ом/петля):", "rfpp_forward", 1, 0),
            ("RFRvPP (Ом/петля):", "rfpp_reverse", 1, 2),
        ]
        self._create_entries(phph_frame, entries)

    def _create_phe_params(self):
        """Создание фрейма параметров Ph-E"""
        phe_frame = ttk.LabelFrame(self.tab, text="Параметры для Ph-E", padding=5)
        phe_frame.pack(fill=tk.X, pady=5)

        # Используем grid для всего содержимого
        ttk.Label(phe_frame, text="⏚ Однофазные повреждения на землю",
                  font=('Segoe UI', 10, 'italic')).grid(row=0, column=0, columnspan=4, sticky=tk.W, pady=(0, 10))

        entries = [
            ("RFFwPE (Ом/петля):", "rfpe_forward", 1, 0),
            ("RFRvPE (Ом/петля):", "rfpe_reverse", 1, 2),
        ]
        self._create_entries(phe_frame, entries)

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
        """Применение настроек селектора"""
        obj.load_enabled = self.vars["load_enabled"].get()
        obj.x1 = self._get_float_value("x1")
        obj.x0 = self._get_float_value("x0")
        obj.rfpp_forward = self._get_float_value("rfpp_forward")
        obj.rfpp_reverse = self._get_float_value("rfpp_reverse")
        obj.rfpe_forward = self._get_float_value("rfpe_forward")
        obj.rfpe_reverse = self._get_float_value("rfpe_reverse")
        obj.rld_forward = self._get_float_value("rld_forward")
        obj.rld_reverse = self._get_float_value("rld_reverse")
        obj.arg_load = self._get_float_value("arg_load")
        obj.arg_load_phph = self._get_float_value("arg_load_phph")
        obj.arg_load_3ph = self._get_float_value("arg_load_3ph")
        obj.opacity = self._get_float_value("opacity")

        # Обновляем калькулятор
        self.viz.selector_calculator = SelectorCalculator(obj)

    def _do_cancel(self, obj):
        """Отмена настроек селектора"""
        self._set_var("x1", obj.x1)
        self._set_var("x0", obj.x0)
        self._set_var("rfpp_forward", obj.rfpp_forward)
        self._set_var("rfpp_reverse", obj.rfpp_reverse)
        self._set_var("rfpe_forward", obj.rfpe_forward)
        self._set_var("rfpe_reverse", obj.rfpe_reverse)
        self._set_var("rld_forward", obj.rld_forward)
        self._set_var("rld_reverse", obj.rld_reverse)
        self._set_var("arg_load", obj.arg_load)
        self._set_var("arg_load_phph", obj.arg_load_phph)
        self._set_var("arg_load_3ph", obj.arg_load_3ph)
        self._set_var("opacity", obj.opacity)

    def _on_load_toggle(self):
        """Обработка переключения нагрузки"""
        self.selector.load_enabled = self.vars["load_enabled"].get()
        self.viz.selector_calculator = SelectorCalculator(self.selector)
        self.viz.plot_characteristics(keep_limits=True)
        self.viz._update_status()

    def _reset_to_default(self):
        """Сброс к рекомендуемым значениям"""
        for key, value in DEFAULT_SELECTOR_VALUES.items():
            self._set_var(key, value)
        self._apply_changes()
        self.viz._show_notification("Сброшено к рекомендуемым значениям")
