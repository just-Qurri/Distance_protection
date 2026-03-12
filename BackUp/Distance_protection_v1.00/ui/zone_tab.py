import tkinter as tk
from tkinter import ttk

from widgets.float_entry import FloatEntry
from widgets.color_combo import ColorCombo


class ZoneTab:
    """Вкладка для настройки параметров зоны"""

    def __init__(self, notebook, zone, visualizer, colors, linestyles):
        """
        Инициализация вкладки

        Args:
            notebook: Виджет Notebook для добавления вкладки
            zone: Объект ZoneSettings
            visualizer: Главный объект визуализатора
            colors: Список доступных цветов
            linestyles: Список доступных стилей линий
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
        """Создание виджетов на вкладке"""
        # Заголовок с названием зоны
        title_frame = ttk.Frame(self.tab)
        title_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(title_frame, text=f"{self.zone.name}",
                  font=('Segoe UI', 12, 'bold')).pack(side=tk.LEFT)

        # Включение зоны
        enabled_var = tk.BooleanVar(value=self.zone.enabled)
        ttk.Checkbutton(title_frame, text="Показать",
                        variable=enabled_var).pack(side=tk.RIGHT)

        # Переменные
        direction_var = tk.StringVar(value=self.zone.direction_mode)
        color_var = tk.StringVar(value=self.zone.color)
        style_var = tk.StringVar(value=self.zone.linestyle)
        load_encroachment_var = tk.BooleanVar(value=self.zone.load_encroachment_enabled)
        show_selector_var = tk.BooleanVar(value=self.zone.show_selector)

        # Ph-Ph параметры
        x1_var = tk.StringVar(value=f"{self.zone.x1:.2f}")
        r1_var = tk.StringVar(value=f"{self.zone.r1:.2f}")
        rfpp_var = tk.StringVar(value=f"{self.zone.rfpp:.2f}")

        # Ph-E параметры
        x0_var = tk.StringVar(value=f"{self.zone.x0:.2f}")
        r0_var = tk.StringVar(value=f"{self.zone.r0:.2f}")
        rfpe_var = tk.StringVar(value=f"{self.zone.rfpe:.2f}")

        # Углы для зон дистанционной защиты
        angle_quad2_var = tk.StringVar(value=f"{self.zone.angle_quad2:.1f}")
        angle_quad4_var = tk.StringVar(value=f"{self.zone.angle_quad4:.1f}")

        # Параметры фазового селектора
        selector_angle_var = tk.StringVar(value=f"{self.zone.selector_angle:.1f}")
        rffw_pp_var = tk.StringVar(value=f"{self.zone.rffw_pp:.2f}")
        rfrv_pp_var = tk.StringVar(value=f"{self.zone.rfrv_pp:.2f}")
        rffw_pe_var = tk.StringVar(value=f"{self.zone.rffw_pe:.2f}")
        rfrv_pe_var = tk.StringVar(value=f"{self.zone.rfrv_pe:.2f}")

        rca_var = tk.StringVar(value=f"{self.zone.rca:.1f}")

        self.vars = {
            "enabled": enabled_var, "direction": direction_var,
            "color": color_var, "style": style_var,
            "load_encroachment": load_encroachment_var,
            "show_selector": show_selector_var,
            "x1": x1_var, "r1": r1_var, "rfpp": rfpp_var,
            "x0": x0_var, "r0": r0_var, "rfpe": rfpe_var,
            "angle_quad2": angle_quad2_var, "angle_quad4": angle_quad4_var,
            "selector_angle": selector_angle_var,
            "rffw_pp": rffw_pp_var, "rfrv_pp": rfrv_pp_var,
            "rffw_pe": rffw_pe_var, "rfrv_pe": rfrv_pe_var,
            "rca": rca_var
        }

        self.viz.zone_vars[self.zone.zone_id] = self.vars

        # Привязка отслеживания изменений
        self._bind_traces()

        # Направленность
        self._create_direction_frame()

        # Углы для зон защиты
        self._create_angles_frame(angle_quad2_var, angle_quad4_var)

        # Фазовый селектор
        self._create_selector_frame(show_selector_var, selector_angle_var,
                                    rffw_pp_var, rfrv_pp_var,
                                    rffw_pe_var, rfrv_pe_var)

        # Ph-Ph параметры
        self._create_phph_frame(x1_var, r1_var, rfpp_var)

        # Ph-E параметры
        self._create_phe_frame(x0_var, r0_var, rfpe_var, rca_var)

        # Оформление
        self._create_style_frame(color_var, style_var)

    def _bind_traces(self):
        """Привязка отслеживания изменений переменных"""

        def update_zone(*args):
            try:
                self.zone.enabled = self.vars["enabled"].get()
                self.zone.direction_mode = self.vars["direction"].get()
                self.zone.color = self.vars["color"].get()
                self.zone.linestyle = self.vars["style"].get()
                self.zone.load_encroachment_enabled = self.vars["load_encroachment"].get()
                self.zone.show_selector = self.vars["show_selector"].get()

                self.zone.x1 = float(self.vars["x1"].get().replace(',', '.'))
                self.zone.r1 = float(self.vars["r1"].get().replace(',', '.'))
                self.zone.rfpp = float(self.vars["rfpp"].get().replace(',', '.'))

                self.zone.x0 = float(self.vars["x0"].get().replace(',', '.'))
                self.zone.r0 = float(self.vars["r0"].get().replace(',', '.'))
                self.zone.rfpe = float(self.vars["rfpe"].get().replace(',', '.'))

                self.zone.angle_quad2 = float(self.vars["angle_quad2"].get().replace(',', '.'))
                self.zone.angle_quad4 = float(self.vars["angle_quad4"].get().replace(',', '.'))

                self.zone.selector_angle = float(self.vars["selector_angle"].get().replace(',', '.'))
                self.zone.rffw_pp = float(self.vars["rffw_pp"].get().replace(',', '.'))
                self.zone.rfrv_pp = float(self.vars["rfrv_pp"].get().replace(',', '.'))
                self.zone.rffw_pe = float(self.vars["rffw_pe"].get().replace(',', '.'))
                self.zone.rfrv_pe = float(self.vars["rfrv_pe"].get().replace(',', '.'))

                self.zone.rca = float(self.vars["rca"].get().replace(',', '.'))
                self.zone.update_angles()
                self.zone.update_polygon_points()

                if self.viz.update_job:
                    self.viz.root.after_cancel(self.viz.update_job)
                self.viz.update_job = self.viz.root.after(100, self.viz.deferred_update)

            except ValueError:
                pass

        # Привязка ко всем переменным
        for var in self.vars.values():
            var.trace('w', update_zone)

    def _create_direction_frame(self):
        """Создание фрейма для выбора направленности"""
        dir_frame = ttk.LabelFrame(self.tab, text="Направленность", padding=5)
        dir_frame.pack(fill=tk.X, pady=5)

        dir_combo = ttk.Combobox(dir_frame, textvariable=self.vars["direction"],
                                 values=["forward", "reverse", "non-directional"],
                                 state="readonly")
        dir_combo.pack(fill=tk.X)

    def _create_angles_frame(self, angle_quad2_var, angle_quad4_var):
        """Создание фрейма для углов зон защиты"""
        angles_frame = ttk.LabelFrame(self.tab, text="Углы для зон защиты (Ph-Ph/Ph-E)", padding=5)
        angles_frame.pack(fill=tk.X, pady=5)

        angles_grid = ttk.Frame(angles_frame)
        angles_grid.pack(fill=tk.X)

        ttk.Label(angles_grid, text="Угол 2-й квадрант:", font=('Segoe UI', 8)).grid(row=0, column=0, sticky=tk.W)
        FloatEntry(angles_grid, textvariable=angle_quad2_var, width=8).grid(row=0, column=1, padx=2)
        ttk.Label(angles_grid, text="° (115°)", font=('Segoe UI', 8), foreground='gray').grid(row=0, column=2,
                                                                                              sticky=tk.W)

        ttk.Label(angles_grid, text="Угол 4-й квадрант:", font=('Segoe UI', 8)).grid(row=1, column=0, sticky=tk.W)
        FloatEntry(angles_grid, textvariable=angle_quad4_var, width=8).grid(row=1, column=1, padx=2)
        ttk.Label(angles_grid, text="° (-15°)", font=('Segoe UI', 8), foreground='gray').grid(row=1, column=2,
                                                                                              sticky=tk.W)

    def _create_selector_frame(self, show_selector_var, selector_angle_var,
                               rffw_pp_var, rfrv_pp_var, rffw_pe_var, rfrv_pe_var):
        """Создание фрейма для фазового селектора"""
        selector_frame = ttk.LabelFrame(self.tab, text="Фазовый селектор FDPSPDIS", padding=5)
        selector_frame.pack(fill=tk.X, pady=5)

        ttk.Checkbutton(selector_frame, text="Показать фазовый селектор",
                        variable=show_selector_var).pack(anchor=tk.W, pady=2)
        ttk.Label(selector_frame, text="Ненаправленная характеристика",
                  font=('Segoe UI', 8), foreground='blue').pack(anchor=tk.W, padx=20)

        selector_grid = ttk.Frame(selector_frame)
        selector_grid.pack(fill=tk.X, pady=5)

        ttk.Label(selector_grid, text="Угол:", font=('Segoe UI', 8)).grid(row=0, column=0, sticky=tk.W)
        FloatEntry(selector_grid, textvariable=selector_angle_var, width=8).grid(row=0, column=1, padx=2)
        ttk.Label(selector_grid, text="° (60°)", font=('Segoe UI', 8), foreground='gray').grid(row=0, column=2,
                                                                                               sticky=tk.W)

        ttk.Label(selector_grid, text="RFFwPP (Ом):", font=('Segoe UI', 8)).grid(row=1, column=0, sticky=tk.W)
        FloatEntry(selector_grid, textvariable=rffw_pp_var, width=6).grid(row=1, column=1, padx=2)

        ttk.Label(selector_grid, text="RFRvPP (Ом):", font=('Segoe UI', 8)).grid(row=1, column=2, sticky=tk.W,
                                                                                 padx=(5, 0))
        FloatEntry(selector_grid, textvariable=rfrv_pp_var, width=6).grid(row=1, column=3, padx=2)

        ttk.Label(selector_grid, text="RFFwPE (Ом):", font=('Segoe UI', 8)).grid(row=2, column=0, sticky=tk.W)
        FloatEntry(selector_grid, textvariable=rffw_pe_var, width=6).grid(row=2, column=1, padx=2)

        ttk.Label(selector_grid, text="RFRvPE (Ом):", font=('Segoe UI', 8)).grid(row=2, column=2, sticky=tk.W,
                                                                                 padx=(5, 0))
        FloatEntry(selector_grid, textvariable=rfrv_pe_var, width=6).grid(row=2, column=3, padx=2)

    def _create_phph_frame(self, x1_var, r1_var, rfpp_var):
        """Создание фрейма для параметров Ph-Ph"""
        phph_frame = ttk.LabelFrame(self.tab, text="Параметры Ph-Ph", padding=5)
        phph_frame.pack(fill=tk.X, pady=5)

        phph_grid = ttk.Frame(phph_frame)
        phph_grid.pack(fill=tk.X)

        ttk.Label(phph_grid, text="X₁ (Ом):", font=('Segoe UI', 8)).grid(row=0, column=0, sticky=tk.W)
        FloatEntry(phph_grid, textvariable=x1_var, width=6).grid(row=0, column=1, padx=2)

        ttk.Label(phph_grid, text="R₁ (Ом):", font=('Segoe UI', 8)).grid(row=0, column=2, sticky=tk.W, padx=(5, 0))
        FloatEntry(phph_grid, textvariable=r1_var, width=6).grid(row=0, column=3, padx=2)

        ttk.Label(phph_grid, text="RFPP (Ом):", font=('Segoe UI', 8)).grid(row=1, column=0, sticky=tk.W)
        FloatEntry(phph_grid, textvariable=rfpp_var, width=6).grid(row=1, column=1, padx=2)

    def _create_phe_frame(self, x0_var, r0_var, rfpe_var, rca_var):
        """Создание фрейма для параметров Ph-E"""
        phe_frame = ttk.LabelFrame(self.tab, text="Параметры Ph-E", padding=5)
        phe_frame.pack(fill=tk.X, pady=5)

        phe_grid = ttk.Frame(phe_frame)
        phe_grid.pack(fill=tk.X)

        ttk.Label(phe_grid, text="X₀ (Ом):", font=('Segoe UI', 8)).grid(row=0, column=0, sticky=tk.W)
        FloatEntry(phe_grid, textvariable=x0_var, width=6).grid(row=0, column=1, padx=2)

        ttk.Label(phe_grid, text="R₀ (Ом):", font=('Segoe UI', 8)).grid(row=0, column=2, sticky=tk.W, padx=(5, 0))
        FloatEntry(phe_grid, textvariable=r0_var, width=6).grid(row=0, column=3, padx=2)

        ttk.Label(phe_grid, text="RFPE (Ом):", font=('Segoe UI', 8)).grid(row=1, column=0, sticky=tk.W)
        FloatEntry(phe_grid, textvariable=rfpe_var, width=6).grid(row=1, column=1, padx=2)

        ttk.Label(phe_grid, text="RCA (°):", font=('Segoe UI', 8)).grid(row=1, column=2, sticky=tk.W, padx=(5, 0))
        FloatEntry(phe_grid, textvariable=rca_var, width=6).grid(row=1, column=3, padx=2)

    def _create_style_frame(self, color_var, style_var):
        """Создание фрейма для оформления"""
        style_frame = ttk.LabelFrame(self.tab, text="Оформление", padding=5)
        style_frame.pack(fill=tk.X, pady=5)

        style_grid = ttk.Frame(style_frame)
        style_grid.pack(fill=tk.X)

        ttk.Label(style_grid, text="Цвет:", font=('Segoe UI', 8)).grid(row=0, column=0, sticky=tk.W)
        ColorCombo(style_grid, textvariable=color_var, colors=self.colors).grid(row=0, column=1, sticky=tk.W, padx=2)

        ttk.Label(style_grid, text="Стиль:", font=('Segoe UI', 8)).grid(row=0, column=2, sticky=tk.W, padx=(10, 0))
        style_combo = ttk.Combobox(style_grid, textvariable=style_var,
                                   values=[s[0] for s in self.linestyles],
                                   state="readonly", width=12)
        style_combo.grid(row=0, column=3, sticky=tk.W, padx=2)