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

        # Определяем название вкладки
        if is_common:
            tab_text = "Common"
        else:
            tab_text = f"Зона {zone.zone_id}"

        self.tab = ttk.Frame(notebook, padding=10)
        notebook.add(self.tab, text=tab_text)

        self.vars = {}

        # Создаем UI в зависимости от типа
        if is_common:
            self._create_common_ui()
        else:
            self._create_dz_ui()

    def _create_dz_ui(self):
        """Создание UI для зоны DZ"""
        # Заголовок
        title_frame = ttk.Frame(self.tab)
        title_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(title_frame, text=self.zone.name,
                  font=('Segoe UI', 16, 'bold'), foreground='#9C27B0').pack(side=tk.LEFT)

        enabled_var = tk.BooleanVar(value=self.zone.enabled)
        ttk.Checkbutton(title_frame, text="Показать",
                        variable=enabled_var).pack(side=tk.RIGHT)

        # Направленность
        direction_var = tk.StringVar(value=self.zone.direction_mode)
        color_var = tk.StringVar(value=self.zone.color)
        style_var = tk.StringVar(value=self.zone.linestyle)

        # Параметры
        self.vars = {
            "enabled": enabled_var,
            "direction": direction_var,
            "color": color_var,
            "style": style_var,
            "x1": tk.StringVar(value=f"{self.zone.x1:.2f}"),
            "r1": tk.StringVar(value=f"{self.zone.r1:.2f}"),
            "rfpp": tk.StringVar(value=f"{self.zone.rfpp:.2f}"),
            "x0": tk.StringVar(value=f"{self.zone.x0:.2f}"),
            "r0": tk.StringVar(value=f"{self.zone.r0:.2f}"),
            "rfpe": tk.StringVar(value=f"{self.zone.rfpe:.2f}"),
            "angle_quad2": tk.StringVar(value=f"{self.zone.angle_quad2:.1f}"),
            "angle_quad4": tk.StringVar(value=f"{self.zone.angle_quad4:.1f}")
        }

        # Создаем фреймы
        self._create_direction_frame()
        self._create_phph_frame()
        self._create_phe_frame()
        self._create_angles_frame()
        self._create_style_frame()

        self._bind_traces()

    def _create_common_ui(self):
        """Создание UI для Common Settings"""
        obj = self.zone  # Это Common_Settings

        # Заголовок
        title_frame = ttk.Frame(self.tab)
        title_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(title_frame, text=obj.name,
                  font=('Segoe UI', 16, 'bold'), foreground=obj.color).pack(side=tk.LEFT)

        enabled_var = tk.BooleanVar(value=obj.enabled)
        ttk.Checkbutton(title_frame, text="Показать",
                        variable=enabled_var).pack(side=tk.RIGHT)

        self.vars = {
            "enabled": enabled_var,
            "color": tk.StringVar(value=obj.color),
            "style": tk.StringVar(value=obj.linestyle),
            "u_base": tk.StringVar(value=f"{obj.u_base:.0f}"),
            "i_base": tk.StringVar(value=f"{obj.i_base:.0f}"),
            "i_secondary": tk.StringVar(value=f"{obj.i_secondary:.1f}"),
            "u_secondary": tk.StringVar(value=f"{obj.u_secondary:.1f}"),
            "angle_phs": tk.StringVar(value=f"{obj.angle_phs:.1f}"),
            "angle_quad2": tk.StringVar(value=f"{obj.angle_quad2:.1f}"),
            "angle_quad4": tk.StringVar(value=f"{obj.angle_quad4:.1f}")
        }

        self._create_common_frames()
        self._bind_traces()

    def _create_common_frames(self):
        """Создание фреймов для Common Settings"""
        params_frame = ttk.LabelFrame(self.tab, text="Общие параметры", padding=5)
        params_frame.pack(fill=tk.X, pady=5)

        grid = ttk.Frame(params_frame)
        grid.pack(fill=tk.X)

        # U Base
        ttk.Label(grid, text="U base (В):", font=('Segoe UI', 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
        FloatEntry(grid, textvariable=self.vars["u_base"], width=12).grid(row=0, column=1, sticky=tk.W, padx=10)

        # I Base
        ttk.Label(grid, text="I base (А):", font=('Segoe UI', 10)).grid(row=1, column=0, sticky=tk.W, pady=5)
        FloatEntry(grid, textvariable=self.vars["i_base"], width=12).grid(row=1, column=1, sticky=tk.W, padx=10)

        # I Secondary
        ttk.Label(grid, text="I secondary (А):", font=('Segoe UI', 10)).grid(row=2, column=0, sticky=tk.W, pady=5)
        FloatEntry(grid, textvariable=self.vars["i_secondary"], width=12).grid(row=2, column=1, sticky=tk.W, padx=10)

        # U Secondary
        ttk.Label(grid, text="U secondary (В):", font=('Segoe UI', 10)).grid(row=3, column=0, sticky=tk.W, pady=5)
        FloatEntry(grid, textvariable=self.vars["u_secondary"], width=12).grid(row=3, column=1, sticky=tk.W, padx=10)

        # Углы
        ttk.Label(grid, text="Angle PHS:", font=('Segoe UI', 10)).grid(row=4, column=0, sticky=tk.W, pady=5)
        FloatEntry(grid, textvariable=self.vars["angle_phs"], width=12).grid(row=4, column=1, sticky=tk.W, padx=10)

        ttk.Label(grid, text="Angle 2-й квадрант:", font=('Segoe UI', 10)).grid(row=5, column=0, sticky=tk.W, pady=5)
        FloatEntry(grid, textvariable=self.vars["angle_quad2"], width=12).grid(row=5, column=1, sticky=tk.W, padx=10)

        ttk.Label(grid, text="Angle 4-й квадрант:", font=('Segoe UI', 10)).grid(row=6, column=0, sticky=tk.W, pady=5)
        FloatEntry(grid, textvariable=self.vars["angle_quad4"], width=12).grid(row=6, column=1, sticky=tk.W, padx=10)

        # Оформление
        self._create_style_frame()

    # ========== ОБЩИЕ МЕТОДЫ ==========

    def _create_direction_frame(self):
        """Фрейм для направленности"""
        dir_frame = ttk.LabelFrame(self.tab, text="Направленность", padding=5)
        dir_frame.pack(fill=tk.X, pady=5)

        dir_combo = ttk.Combobox(dir_frame, textvariable=self.vars["direction"],
                                 values=["forward", "reverse", "non-directional"],
                                 state="readonly")
        dir_combo.pack(fill=tk.X)

    def _create_phph_frame(self):
        """Фрейм для параметров Ph-Ph"""
        phph_frame = ttk.LabelFrame(self.tab, text="Параметры Ph-Ph", padding=5)
        phph_frame.pack(fill=tk.X, pady=5)

        grid = ttk.Frame(phph_frame)
        grid.pack(fill=tk.X)

        ttk.Label(grid, text="X₁ (Ом):", font=('Segoe UI', 9)).grid(row=0, column=0, sticky=tk.W, pady=2)
        FloatEntry(grid, textvariable=self.vars["x1"], width=8).grid(row=0, column=1, sticky=tk.W, padx=5)

        ttk.Label(grid, text="R₁ (Ом):", font=('Segoe UI', 9)).grid(row=0, column=2, sticky=tk.W, pady=2, padx=(10, 0))
        FloatEntry(grid, textvariable=self.vars["r1"], width=8).grid(row=0, column=3, sticky=tk.W, padx=5)

        ttk.Label(grid, text="RFPP (Ом):", font=('Segoe UI', 9)).grid(row=1, column=0, sticky=tk.W, pady=2)
        FloatEntry(grid, textvariable=self.vars["rfpp"], width=8).grid(row=1, column=1, sticky=tk.W, padx=5)

    def _create_phe_frame(self):
        """Фрейм для параметров Ph-E"""
        phe_frame = ttk.LabelFrame(self.tab, text="Параметры Ph-E", padding=5)
        phe_frame.pack(fill=tk.X, pady=5)

        grid = ttk.Frame(phe_frame)
        grid.pack(fill=tk.X)

        ttk.Label(grid, text="X₀ (Ом):", font=('Segoe UI', 9)).grid(row=0, column=0, sticky=tk.W, pady=2)
        FloatEntry(grid, textvariable=self.vars["x0"], width=8).grid(row=0, column=1, sticky=tk.W, padx=5)

        ttk.Label(grid, text="R₀ (Ом):", font=('Segoe UI', 9)).grid(row=0, column=2, sticky=tk.W, pady=2, padx=(10, 0))
        FloatEntry(grid, textvariable=self.vars["r0"], width=8).grid(row=0, column=3, sticky=tk.W, padx=5)

        ttk.Label(grid, text="RFPE (Ом):", font=('Segoe UI', 9)).grid(row=1, column=0, sticky=tk.W, pady=2)
        FloatEntry(grid, textvariable=self.vars["rfpe"], width=8).grid(row=1, column=1, sticky=tk.W, padx=5)

    def _create_angles_frame(self):
        """Фрейм для углов"""
        angles_frame = ttk.LabelFrame(self.tab, text="Углы", padding=5)
        angles_frame.pack(fill=tk.X, pady=5)

        grid = ttk.Frame(angles_frame)
        grid.pack(fill=tk.X)

        ttk.Label(grid, text="Угол 2-й кв.:", font=('Segoe UI', 9)).grid(row=0, column=0, sticky=tk.W, pady=2)
        FloatEntry(grid, textvariable=self.vars["angle_quad2"], width=8).grid(row=0, column=1, sticky=tk.W, padx=5)

        ttk.Label(grid, text="Угол 4-й кв.:", font=('Segoe UI', 9)).grid(row=1, column=0, sticky=tk.W, pady=2)
        FloatEntry(grid, textvariable=self.vars["angle_quad4"], width=8).grid(row=1, column=1, sticky=tk.W, padx=5)

    def _create_style_frame(self):
        """Фрейм для оформления"""
        style_frame = ttk.LabelFrame(self.tab, text="Оформление", padding=5)
        style_frame.pack(fill=tk.X, pady=5)

        grid = ttk.Frame(style_frame)
        grid.pack(fill=tk.X)

        ttk.Label(grid, text="Цвет:", font=('Segoe UI', 9)).grid(row=0, column=0, sticky=tk.W, pady=2)
        ColorCombo(grid, textvariable=self.vars["color"], colors=self.colors, width=15).grid(
            row=0, column=1, sticky=tk.W, padx=5
        )

        ttk.Label(grid, text="Стиль:", font=('Segoe UI', 9)).grid(row=1, column=0, sticky=tk.W, pady=2)
        style_combo = ttk.Combobox(grid, textvariable=self.vars["style"],
                                   values=[s[0] for s in self.linestyles],
                                   state="readonly", width=12)
        style_combo.grid(row=1, column=1, sticky=tk.W, padx=5)

    def _bind_traces(self):
        """Привязка отслеживания изменений"""

        def update_zone(*args):
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
                if self.viz.update_job:
                    self.viz.root.after_cancel(self.viz.update_job)
                self.viz.update_job = self.viz.root.after(100, self.viz.deferred_update)

            except ValueError:
                pass

        for var in self.vars.values():
            var.trace('w', update_zone)
