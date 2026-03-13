"""
Вкладка для настройки параметров зоны
"""

import tkinter as tk
from tkinter import ttk

from widgets.color_combo import ColorCombo
from widgets.float_entry import FloatEntry


class ZoneTab:
    """Вкладка для настройки параметров зоны"""

    def __init__(self, notebook, zone, visualizer, phs, cs, colors, linestyles):
        """
        Инициализация вкладки
        """
        self.zone = zone
        self.phs = phs
        self.common_settings = cs
        self.viz = visualizer
        self.colors = colors
        self.linestyles = linestyles

        self.tab = ttk.Frame(notebook, padding=10)

        if phs is not None:
            notebook.add(self.tab, text=f"PHS")
        elif cs is not None:
            notebook.add(self.tab, text=f"Common")
        else:
            notebook.add(self.tab, text=f"Зона {zone.zone_id}")

        self.vars = {}
        if phs is not None:
            self._create_phs_ui()
        elif cs is not None:
            self._create_common_ui()
        else:
            self._create_dz_ui()

    def _create_common_settings(self):
        """Создание пяти контуров"""
        # Заголовок
        title_frame = ttk.Frame(self.tab)
        title_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(title_frame, text=f"{self.zone.name}",
                  font=('Segoe UI', 16, 'bold'), foreground='#9C27B0').pack(side=tk.LEFT)

        # Включение зоны
        enabled_var = tk.BooleanVar(value=self.zone.enabled)
        ttk.Checkbutton(title_frame, text="Показать",
                        variable=enabled_var).pack(side=tk.RIGHT)

    def _create_PHS_setting(self):
        """Создание пяти контуров"""
        # Заголовок
        title_frame = ttk.Frame(self.tab)
        title_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(title_frame, text=f"{self.zone.name}",
                  font=('Segoe UI', 16, 'bold'), foreground='#9C27B0').pack(side=tk.LEFT)

        # Включение зоны
        enabled_var = tk.BooleanVar(value=self.zone.enabled)
        ttk.Checkbutton(title_frame, text="Показать",
                        variable=enabled_var).pack(side=tk.RIGHT)

    def _create_dz_ui(self):
        """Создание пяти контуров"""
        # Заголовок
        title_frame = ttk.Frame(self.tab)
        title_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(title_frame, text=f"{self.zone.name}",
                  font=('Segoe UI', 16, 'bold'), foreground='#9C27B0').pack(side=tk.LEFT)

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
        angle_quad2_var = tk.StringVar(value=f"{self.zone.angle_quad2:.1f}")
        angle_quad4_var = tk.StringVar(value=f"{self.zone.angle_quad4:.1f}")

        self.vars = {
            "enabled": enabled_var,
            "direction": direction_var,
            "color": color_var,
            "style": style_var,
            "x1": x1_var, "r1": r1_var, "rfpp": rfpp_var,
            "x0": x0_var, "r0": r0_var, "rfpe": rfpe_var,
            "angle_quad2": angle_quad2_var,
            "angle_quad4": angle_quad4_var,
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
                # Определяем, какой объект обновляем
                if self.phs is not None:
                    obj = self.phs
                elif self.common_settings is not None:
                    obj = self.common_settings
                else:
                    obj = self.zone

                if "enabled" in self.vars:
                    obj.enabled = self.vars["enabled"].get()

                if "direction" in self.vars:
                    obj.direction_mode = self.vars["direction"].get()

                if "color" in self.vars:
                    obj.color = self.vars["color"].get()

                if "style" in self.vars:
                    obj.linestyle = self.vars["style"].get()

                # Обновляем параметры Ph-Ph
                if "x1" in self.vars:
                    obj.x1 = float(self.vars["x1"].get().replace(',', '.'))
                    obj.r1 = float(self.vars["r1"].get().replace(',', '.'))
                    obj.rfpp = float(self.vars["rfpp"].get().replace(',', '.'))

                # Обновляем параметры Ph-E
                if "x0" in self.vars:
                    obj.x0 = float(self.vars["x0"].get().replace(',', '.'))
                    obj.r0 = float(self.vars["r0"].get().replace(',', '.'))
                    obj.rfpe = float(self.vars["rfpe"].get().replace(',', '.'))

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

    def _create_phs_ui(self):
        """Создание UI для PHS"""
        obj = self.phs

        # Заголовок
        title_frame = ttk.Frame(self.tab)
        title_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(title_frame, text=obj.name,
                  font=('Segoe UI', 16, 'bold'), foreground=obj.color).pack(side=tk.LEFT)

        enabled_var = tk.BooleanVar(value=obj.enabled)
        ttk.Checkbutton(title_frame, text="Показать",
                        variable=enabled_var).pack(side=tk.RIGHT)

        # Параметры PHS
        self.vars = {
            "enabled": enabled_var,
            "color": tk.StringVar(value=obj.color),
            "style": tk.StringVar(value=obj.linestyle),
            "rld_forward": tk.StringVar(value=f"{obj.rld_forward:.1f}"),
            "rld_reverse": tk.StringVar(value=f"{obj.rld_reverse:.1f}"),
            "angle_load": tk.StringVar(value=f"{obj.angle_load:.1f}"),
            "x1": tk.StringVar(value=f"{obj.x1:.1f}"),
            "x0": tk.StringVar(value=f"{obj.x0:.1f}"),
            "rfpp_forward": tk.StringVar(value=f"{obj.rfpp_forward:.1f}"),
            "rfpp_reverse": tk.StringVar(value=f"{obj.rfpp_reverse:.1f}"),
            "rfpe_forward": tk.StringVar(value=f"{obj.rfpe_forward:.1f}"),
            "rfpe_reverse": tk.StringVar(value=f"{obj.rfpe_reverse:.1f}"),
            "direction": tk.StringVar(value=obj.direction_mode),
        }

        self._create_phs_frames()
        self._bind_traces()

    def _create_phs_frames(self):
        """Создание основных параметров"""
        main_frame = ttk.LabelFrame(self.tab, text="Основные параметры", padding=5)
        main_frame.pack(fill=tk.X, pady=5)

        # Сетка для параметров
        grid = ttk.Frame(main_frame)
        grid.pack(fill=tk.X)

        # X1
        ttk.Label(grid, text="X₁ (Ом/фаза):", font=('Segoe UI', 10)).grid(row=0, column=0, sticky=tk.W, pady=8)
        x1_var = tk.StringVar(value=f"{self.phs.x1:.2f}")
        FloatEntry(grid, textvariable=x1_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=10)
        self.vars["x1"] = x1_var

        # X0
        ttk.Label(grid, text="X₀ (Ом/фаза):", font=('Segoe UI', 10)).grid(row=1, column=0, sticky=tk.W, pady=8)
        x0_var = tk.StringVar(value=f"{self.phs.x0:.2f}")
        FloatEntry(grid, textvariable=x0_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=10)
        self.vars["x0"] = x0_var

        """Создание параметров для Ph-Ph"""
        phph_frame = ttk.LabelFrame(self.tab, text="Параметры для Ph-Ph", padding=5)
        phph_frame.pack(fill=tk.X, pady=5)

        # Заголовок с иконкой
        header = ttk.Frame(phph_frame)
        header.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(header, text="∿", font=('Segoe UI', 14)).pack(side=tk.LEFT, padx=5)
        ttk.Label(header, text="Междуфазные повреждения", font=('Segoe UI', 10, 'italic')).pack(side=tk.LEFT)

        # Сетка для параметров
        grid = ttk.Frame(phph_frame)
        grid.pack(fill=tk.X)

        # Прямое направление
        ttk.Label(grid, text="Прямое направление (RFFwPP):", font=('Segoe UI', 10, 'bold')).grid(row=0,
                                                                                                 column=0,
                                                                                                 sticky=tk.W,
                                                                                                 pady=8,
                                                                                                 columnspan=2)

        ttk.Label(grid, text="RFFwPP (Ом/петля):", font=('Segoe UI', 10)).grid(row=1,
                                                                               column=0,
                                                                               sticky=tk.W,
                                                                               padx=20,
                                                                               pady=5)
        fw_pp_var = tk.StringVar(value=f"{self.phs.rfpp_forward:.2f}")
        FloatEntry(grid, textvariable=fw_pp_var, width=10).grid(row=1,
                                                                column=1,
                                                                sticky=tk.W,
                                                                padx=10)
        self.vars["rfpp_forward"] = fw_pp_var

        # Разделитель
        ttk.Separator(grid, orient='horizontal').grid(row=2,
                                                      column=0,
                                                      columnspan=3,
                                                      sticky=tk.EW,
                                                      pady=10)

        # Обратное направление
        ttk.Label(grid, text="Обратное направление (RFRvPP):", font=('Segoe UI', 10, 'bold')).grid(row=3,
                                                                                                   column=0,
                                                                                                   sticky=tk.W,
                                                                                                   pady=8,
                                                                                                   columnspan=2)

        ttk.Label(grid, text="RFRvPP (Ом/петля):", font=('Segoe UI', 10)).grid(row=4,
                                                                               column=0,
                                                                               sticky=tk.W,
                                                                               padx=20,
                                                                               pady=5)
        rv_pp_var = tk.StringVar(value=f"{self.phs.rfpp_reverse:.2f}")
        FloatEntry(grid, textvariable=rv_pp_var, width=10).grid(row=4,
                                                                column=1,
                                                                sticky=tk.W,
                                                                padx=10)
        self.vars["rfpp_reverse"] = rv_pp_var

        """Создание параметров для Ph-E"""
        phe_frame = ttk.LabelFrame(self.tab, text="Параметры для Ph-E", padding=5)
        phe_frame.pack(fill=tk.X, pady=5)

        # Заголовок с иконкой
        header = ttk.Frame(phe_frame)
        header.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(header, text="⏚", font=('Segoe UI', 14)).pack(side=tk.LEFT, padx=5)
        ttk.Label(header, text="Однофазные повреждения на землю", font=('Segoe UI', 10, 'italic')).pack(side=tk.LEFT)

        # Сетка для параметров
        grid = ttk.Frame(phe_frame)
        grid.pack(fill=tk.X)

        # Прямое направление
        ttk.Label(grid, text="Прямое направление (RFFwPE):", font=('Segoe UI', 10, 'bold')).grid(row=0,
                                                                                                 column=0,
                                                                                                 sticky=tk.W,
                                                                                                 pady=8,
                                                                                                 columnspan=2)

        ttk.Label(grid, text="RFFwPE (Ом/петля):", font=('Segoe UI', 10)).grid(row=1,
                                                                               column=0,
                                                                               sticky=tk.W,
                                                                               padx=20,
                                                                               pady=5)
        fw_pe_var = tk.StringVar(value=f"{self.phs.rfpe_forward:.2f}")
        FloatEntry(grid, textvariable=fw_pe_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=10)
        self.vars["rfpe_forward"] = fw_pe_var

        # Разделитель
        ttk.Separator(grid, orient='horizontal').grid(row=2, column=0, columnspan=3, sticky=tk.EW, pady=10)

        # Обратное направление
        ttk.Label(grid, text="Обратное направление (RFRvPE):", font=('Segoe UI', 10, 'bold')).grid(row=3,
                                                                                                   column=0,
                                                                                                   sticky=tk.W,
                                                                                                   pady=8,
                                                                                                   columnspan=2)

        ttk.Label(grid, text="RFRvPE (Ом/петля):", font=('Segoe UI', 10)).grid(row=4,
                                                                               column=0,
                                                                               sticky=tk.W,
                                                                               padx=20,
                                                                               pady=5)
        rv_pe_var = tk.StringVar(value=f"{self.phs.rfpe_reverse:.2f}")
        FloatEntry(grid, textvariable=rv_pe_var, width=10).grid(row=4, column=1, sticky=tk.W, padx=10)
        self.vars["rfpe_reverse"] = rv_pe_var

        # Оформление
        self._create_style_frame()

    def _create_common_ui(self):
        """Создание UI для Common Settings"""
        obj = self.common_settings

        # Заголовок
        title_frame = ttk.Frame(self.tab)
        title_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(title_frame, text=obj.name,
                  font=('Segoe UI', 16, 'bold'), foreground=obj.color).pack(side=tk.LEFT)

        enabled_var = tk.BooleanVar(value=obj.enabled)
        ttk.Checkbutton(title_frame, text="Показать",
                        variable=enabled_var).pack(side=tk.RIGHT)

        # Параметры Common Settings
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

        ttk.Label(grid, text="U base (В):").grid(row=0, column=0, sticky=tk.W, pady=2)
        FloatEntry(grid, textvariable=self.vars["u_base"], width=10).grid(row=0, column=1, padx=5)

        ttk.Label(grid, text="I base (А):").grid(row=0, column=2, sticky=tk.W, pady=2, padx=(10, 0))
        FloatEntry(grid, textvariable=self.vars["i_base"], width=10).grid(row=0, column=3, padx=5)

        ttk.Label(grid, text="I secondary:").grid(row=1, column=0, sticky=tk.W, pady=2)
        FloatEntry(grid, textvariable=self.vars["i_secondary"], width=10).grid(row=1, column=1, padx=5)

        ttk.Label(grid, text="U secondary:").grid(row=1, column=2, sticky=tk.W, pady=2, padx=(10, 0))
        FloatEntry(grid, textvariable=self.vars["u_secondary"], width=10).grid(row=1, column=3, padx=5)

        ttk.Label(grid, text="Angle PHS:").grid(row=2, column=0, sticky=tk.W, pady=2)
        FloatEntry(grid, textvariable=self.vars["angle_phs"], width=10).grid(row=2, column=1, padx=5)

        ttk.Label(grid, text="Angle 2-nd quadrant:").grid(row=3, column=0, sticky=tk.W, pady=2)
        FloatEntry(grid, textvariable=self.vars["angle_quad2"], width=10).grid(row=3, column=1, padx=5)

        ttk.Label(grid, text="Angle 4-nd quadrant:").grid(row=3, column=2, sticky=tk.W, pady=2)
        FloatEntry(grid, textvariable=self.vars["angle_quad4"], width=10).grid(row=3, column=3, padx=5)

        # Оформление
        self._create_style_frame()
