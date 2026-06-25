# -*- coding: utf-8 -*-
"""
Вкладка для настройки параметров зоны (оптимизирована)
"""

import tkinter as tk
from tkinter import ttk

from ui.base_tab import BaseTab


class ZoneTab(BaseTab):
    """Вкладка для настройки параметров зоны"""

    def __init__(self, notebook, zone, visualizer, colors, linestyles, is_common=False):
        self.zone = zone
        self.is_common = is_common
        super().__init__(notebook, visualizer, colors, linestyles)

    def get_tab_name(self) -> str:
        if self.is_common:
            return "Common"
        return f"Зона {self.zone.zone_id}"

    def _create_ui(self):
        """Создание UI для зоны"""
        if self.is_common:
            self._create_common_ui()
        else:
            self._create_dz_ui()

    def _get_target_object(self):
        return self.zone

    # ==================== COMMON SETTINGS ====================

    def _create_common_ui(self):
        """Создание UI для Common Settings"""
        obj = self.zone

        self.vars.update({
            "enabled": tk.BooleanVar(value=obj.enabled),
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

        self._create_title_frame_without_checkbox(obj.name, obj.color)

        params_frame = ttk.LabelFrame(self.tab, text="Общие параметры", padding=5)
        params_frame.pack(fill=tk.X, pady=5)

        entries = [
            ("U base (В):", "u_base", 0, 0),
            ("I base (А):", "i_base", 1, 0),
            ("I secondary (А):", "i_secondary", 2, 0),
            ("U secondary (В):", "u_secondary", 3, 0),
            ("Angle PHS:", "angle_phs", 4, 0),
            ("Angle 2-й квадрант:", "angle_quad2", 5, 0),
            ("Angle 4-й квадрант:", "angle_quad4", 6, 0),
        ]
        self._create_entries(params_frame, entries)
        self._create_style_frame(self.tab)

    def _do_apply(self, obj):
        """Применение common настроек"""
        if self.is_common:
            obj.u_base = self._get_float_value("u_base")
            obj.i_base = self._get_float_value("i_base")
            obj.i_secondary = self._get_float_value("i_secondary")
            obj.u_secondary = self._get_float_value("u_secondary")
            obj.angle_phs = self._get_float_value("angle_phs")
            obj.angle_quad2 = self._get_float_value("angle_quad2")
            obj.angle_quad4 = self._get_float_value("angle_quad4")

    def _do_cancel(self, obj):
        """Отмена common настроек"""
        if self.is_common:
            self._set_var("u_base", obj.u_base)
            self._set_var("i_base", obj.i_base)
            self._set_var("i_secondary", obj.i_secondary)
            self._set_var("u_secondary", obj.u_secondary)
            self._set_var("angle_phs", obj.angle_phs)
            self._set_var("angle_quad2", obj.angle_quad2)
            self._set_var("angle_quad4", obj.angle_quad4)

    # ==================== DZ ZONE ====================

    def _create_dz_ui(self):
        """Создание UI для DZ зоны"""
        obj = self.zone

        self.vars.update({
            "enabled": tk.BooleanVar(value=obj.enabled),
            "color": tk.StringVar(value=obj.color),
            "style": tk.StringVar(value=obj.linestyle),
            "direction": tk.StringVar(value=obj.direction_mode),
            "x1": tk.StringVar(value=f"{obj.x1:.2f}"),
            "r1": tk.StringVar(value=f"{obj.r1:.2f}"),
            "rfpp": tk.StringVar(value=f"{obj.rfpp:.2f}"),
            "x0": tk.StringVar(value=f"{obj.x0:.2f}"),
            "r0": tk.StringVar(value=f"{obj.r0:.2f}"),
            "rfpe": tk.StringVar(value=f"{obj.rfpe:.2f}"),
        })

        self._create_title_frame(obj.name, obj.color)

        # Направленность
        dir_frame = ttk.LabelFrame(self.tab, text="Направленность", padding=5)
        dir_frame.pack(fill=tk.X, pady=5)

        dir_combo = ttk.Combobox(dir_frame, textvariable=self.vars["direction"],
                                 values=["forward", "reverse", "non-directional"],
                                 state="readonly")
        dir_combo.pack(fill=tk.X)
        dir_combo.bind('<<ComboboxSelected>>', lambda e: self._apply_changes())

        # Ph-Ph параметры
        self._create_phph_frame()

        # Ph-E параметры
        self._create_phe_frame()

        self._create_style_frame(self.tab)

    def _create_phph_frame(self):
        """Создание фрейма параметров Ph-Ph"""
        phph_frame = ttk.LabelFrame(self.tab, text="Параметры Ph-Ph", padding=5)
        phph_frame.pack(fill=tk.X, pady=5)

        entries = [
            ("X₁ (Ом):", "x1", 0, 0),
            ("R₁ (Ом):", "r1", 0, 2),
            ("RFPP (Ом):", "rfpp", 1, 0),
        ]
        self._create_entries(phph_frame, entries)

    def _create_phe_frame(self):
        """Создание фрейма параметров Ph-E"""
        phe_frame = ttk.LabelFrame(self.tab, text="Параметры Ph-E", padding=5)
        phe_frame.pack(fill=tk.X, pady=5)

        entries = [
            ("X₀ (Ом):", "x0", 0, 0),
            ("R₀ (Ом):", "r0", 0, 2),
            ("RFPE (Ом):", "rfpe", 1, 0),
        ]
        self._create_entries(phe_frame, entries)

    def _do_apply(self, obj):
        """Применение DZ настроек"""
        if not self.is_common:
            obj.direction_mode = self.vars["direction"].get()
            obj.x1 = self._get_float_value("x1")
            obj.r1 = self._get_float_value("r1")
            obj.rfpp = self._get_float_value("rfpp")
            obj.x0 = self._get_float_value("x0")
            obj.r0 = self._get_float_value("r0")
            obj.rfpe = self._get_float_value("rfpe")

    def _do_cancel(self, obj):
        """Отмена DZ настроек"""
        if not self.is_common:
            self._set_var("x1", obj.x1)
            self._set_var("r1", obj.r1)
            self._set_var("rfpp", obj.rfpp)
            self._set_var("x0", obj.x0)
            self._set_var("r0", obj.r0)
            self._set_var("rfpe", obj.rfpe)
