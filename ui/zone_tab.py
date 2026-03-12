# -*- coding: utf-8 -*-
"""
Вкладка для настройки параметров зоны (без масштабирования)
"""

import tkinter as tk
from tkinter import ttk

from widgets.float_entry import FloatEntry
from widgets.color_combo import ColorCombo


class ZoneTab:
    """Вкладка для настройки параметров зоны"""

    def __init__(self, notebook, zone, visualizer, colors, linestyles):
        """
        Инициализация вкладки
        """
        self.zone = zone
        self.viz = visualizer
        self.colors = colors
        self.linestyles = linestyles

        self.tab = ttk.Frame(notebook, padding=10)
        notebook.add(self.tab, text=f"Зона {zone.zone_id}")

        self.vars = {}
        self._create_widgets()

    def _create_widgets(self):
        """Создание виджетов"""
        # Заголовок
        title_frame = ttk.Frame(self.tab)
        title_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(title_frame, text=f"{self.zone.name}",
                  font=('Segoe UI', 12, 'bold')).pack(side=tk.LEFT)

        # Включение зоны
        enabled_var = tk.BooleanVar(value=self.zone.enabled)
        ttk.Checkbutton(title_frame, text="Показать",
                        variable=enabled_var).pack(side=tk.RIGHT)

        # Переменные для всех параметров
        direction_var = tk.StringVar(value=self.zone.direction_mode)
        color_var = tk.StringVar(value=self.zone.color)
        style_var = tk.StringVar(value=self.zone.linestyle)

        # Параметры Ph-Ph
        x1_var = tk.StringVar(value=f"{self.zone.x1:.2f}")
        r1_var = tk.StringVar(value=f"{self.zone.r1:.2f}")
        rfpp_var = tk.StringVar(value=f"{self.zone.rfpp:.2f}")

        # Параметры Ph-E
        x0_var = tk.StringVar(value=f"{self.zone.x0:.2f}")
        r0_var = tk.StringVar(value=f"{self.zone.r0:.2f}")
        rfpe_var = tk.StringVar(value=f"{self.zone.rfpe:.2f}")

        # Углы
        rca_var = tk.StringVar(value=f"{self.zone.rca:.1f}")
        angle_quad2_var = tk.StringVar(value=f"{self.zone.angle_quad2:.1f}")
        angle_quad4_var = tk.StringVar(value=f"{self.zone.angle_quad4:.1f}")

        self.vars = {
            "enabled": enabled_var,
            "direction": direction_var,
            "color": color_var,
            "style": style_var,
            "x1": x1_var, "r1": r1_var, "rfpp": rfpp_var,
            "x0": x0_var, "r0": r0_var, "rfpe": rfpe_var,
            "rca": rca_var,
            "angle_quad2": angle_quad2_var,
            "angle_quad4": angle_quad4_var
        }

        self.viz.zone_vars[self.zone.zone_id] = self.vars

        # Привязка отслеживания
        self._bind_traces()

        # Направленность
        self._create_direction_frame()

        # Параметры Ph-Ph
        self._create_phph_frame()

        # Параметры Ph-E
        self._create_phe_frame()

        # Углы
        self._create_angles_frame()

        # Оформление
        self._create_style_frame()

    def _bind_traces(self):
        """Привязка отслеживания изменений"""

        def update_zone(*args):
            try:
                self.zone.enabled = self.vars["enabled"].get()
                self.zone.direction_mode = self.vars["direction"].get()
                self.zone.color = self.vars["color"].get()
                self.zone.linestyle = self.vars["style"].get()

                # Обновляем параметры Ph-Ph
                self.zone.x1 = float(self.vars["x1"].get().replace(',', '.'))
                self.zone.r1 = float(self.vars["r1"].get().replace(',', '.'))
                self.zone.rfpp = float(self.vars["rfpp"].get().replace(',', '.'))

                # Обновляем параметры Ph-E
                self.zone.x0 = float(self.vars["x0"].get().replace(',', '.'))
                self.zone.r0 = float(self.vars["r0"].get().replace(',', '.'))
                self.zone.rfpe = float(self.vars["rfpe"].get().replace(',', '.'))

                # Обновляем углы
                self.zone.rca = float(self.vars["rca"].get().replace(',', '.'))
                self.zone.angle_quad2 = float(self.vars["angle_quad2"].get().replace(',', '.'))
                self.zone.angle_quad4 = float(self.vars["angle_quad4"].get().replace(',', '.'))

                self.zone.update_angles()

                if self.viz.update_job:
                    self.viz.root.after_cancel(self.viz.update_job)
                self.viz.update_job = self.viz.root.after(100, self.viz.deferred_update)

            except ValueError:
                pass

        for var in self.vars.values():
            var.trace('w', update_zone)

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

        ttk.Label(grid, text="RCA (°):", font=('Segoe UI', 9)).grid(row=0, column=0, sticky=tk.W, pady=2)
        FloatEntry(grid, textvariable=self.vars["rca"], width=8).grid(row=0, column=1, sticky=tk.W, padx=5)

        ttk.Label(grid, text="Угол 2 кв.:", font=('Segoe UI', 9)).grid(row=0, column=2, sticky=tk.W, pady=2,
                                                                       padx=(10, 0))
        FloatEntry(grid, textvariable=self.vars["angle_quad2"], width=8).grid(row=0, column=3, sticky=tk.W, padx=5)

        ttk.Label(grid, text="Угол 4 кв.:", font=('Segoe UI', 9)).grid(row=1, column=0, sticky=tk.W, pady=2)
        FloatEntry(grid, textvariable=self.vars["angle_quad4"], width=8).grid(row=1, column=1, sticky=tk.W, padx=5)

    def _create_style_frame(self):
        """Фрейм для оформления"""
        style_frame = ttk.LabelFrame(self.tab, text="Оформление", padding=5)
        style_frame.pack(fill=tk.X, pady=5)

        grid = ttk.Frame(style_frame)
        grid.pack(fill=tk.X)

        ttk.Label(grid, text="Цвет:", font=('Segoe UI', 9)).grid(row=0, column=0, sticky=tk.W, pady=2)
        ColorCombo(grid, textvariable=self.vars["color"], colors=self.colors, width=15).grid(row=0, column=1,
                                                                                             sticky=tk.W, padx=5)

        ttk.Label(grid, text="Стиль:", font=('Segoe UI', 9)).grid(row=1, column=0, sticky=tk.W, pady=2)
        style_combo = ttk.Combobox(grid, textvariable=self.vars["style"],
                                   values=[s[0] for s in self.linestyles],
                                   state="readonly", width=12)
        style_combo.grid(row=1, column=1, sticky=tk.W, padx=5)