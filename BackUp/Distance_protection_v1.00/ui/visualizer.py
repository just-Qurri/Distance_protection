# -*- coding: utf-8 -*-
"""
Главный класс визуализатора REL670
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Optional
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from models.zone_settings import ZoneSettings
from ui.top_panel import TopPanel
from ui.plot_area import PlotArea
from ui.zone_tab import ZoneTab
from ui.constants import COLORS, LINESTYLES, FAULT_TYPES


class REL670Visualizer:
    """Главный класс визуализатора REL670"""

    # Типы повреждений
    FAULT_TYPES = FAULT_TYPES

    def __init__(self, title="REL670 - Дистанционная защита"):
        """
        Инициализация визуализатора

        Args:
            title: Заголовок окна
        """
        self.title = title
        self.zones: List[ZoneSettings] = []
        self.root = None
        self.figure = None
        self.ax = None
        self.canvas = None
        self.initial_xlim = None
        self.initial_ylim = None
        self.zone_vars = {}
        self.status_bar = None
        self.zoom_level = None
        self.fault_type = None
        self.show_selector_var = None

        # Для перетаскивания
        self.drag_start = None
        self.drag_start_xlim = None
        self.drag_start_ylim = None
        self.is_dragging = False

        # Для отложенного обновления
        self.update_job = None

        # Компоненты UI
        self.top_panel = None
        self.plot_area = None
        self.zone_tabs = []

    def add_zone(self, zone: ZoneSettings):
        """Добавление зоны"""
        zone.zone_id = len(self.zones) + 1
        if zone.zone_id <= len(COLORS):
            zone.color = COLORS[zone.zone_id - 1][0]
            zone.color_name = COLORS[zone.zone_id - 1][1]
        self.zones.append(zone)

    def calculate_initial_limits(self):
        """Расчет начальных пределов графика"""
        if not self.zones or not self.fault_type:
            self.initial_xlim = (-10, 20)
            self.initial_ylim = (-15, 15)
            return

        all_min_r = float('inf')
        all_max_r = float('-inf')
        all_min_x = float('inf')
        all_max_x = float('-inf')

        visible_zones = [z for z in self.zones if z.enabled]
        if not visible_zones:
            self.initial_xlim = (-10, 20)
            self.initial_ylim = (-15, 15)
            return

        fault_type = self.fault_type.get()

        for zone in visible_zones:
            if fault_type == "selector" and not zone.show_selector:
                continue
            min_r, max_r, min_x, max_x = zone.get_zone_bounds(fault_type)

            all_min_r = min(all_min_r, min_r)
            all_max_r = max(all_max_r, max_r)
            all_min_x = min(all_min_x, min_x)
            all_max_x = max(all_max_x, max_x)

        if all_min_r != float('inf') and all_max_r != float('-inf'):
            r_range = all_max_r - all_min_r
            r_margin = max(r_range * 0.2, 2.0)

            x_range = all_max_x - all_min_x
            x_margin = max(x_range * 0.2, 2.0)

            self.initial_xlim = (all_min_r - r_margin, all_max_r + r_margin)
            self.initial_ylim = (all_min_x - x_margin, all_max_x + x_margin)
        else:
            self.initial_xlim = (-10, 20)
            self.initial_ylim = (-15, 15)

    def create_window(self):
        """Создание главного окна"""
        self.root = tk.Tk()
        self.root.title(self.title)
        self.root.state('zoomed')

        # Создаем переменные
        self.zoom_level = tk.StringVar(value="100%")
        self.fault_type = tk.StringVar(value="phph")
        self.show_selector_var = tk.BooleanVar(value=False)

        # Настройка стиля
        self._configure_styles()

        # Привязка событий
        self.fault_type.trace('w', lambda *args: self.on_fault_type_change())
        self.show_selector_var.trace('w', lambda *args: self.on_selector_toggle())

        # Расчет начальных границ
        self.calculate_initial_limits()

        # Главный контейнер
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Верхняя панель
        self.top_panel = TopPanel(main_container, self)
        self.top_panel.pack()

        # Средняя часть: график + управление зонами
        middle_frame = ttk.Frame(main_container)
        middle_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Область графика
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        self.plot_area = PlotArea(middle_frame, self, screen_width, screen_height)
        self.plot_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Правая панель управления зонами
        control_frame = ttk.LabelFrame(middle_frame, text="УСТАВКИ ЗОН",
                                       padding=10, width=650)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y, expand=False)
        control_frame.pack_propagate(False)

        self._create_control_panel(control_frame)

        # Нижняя панель статуса
        self._create_status_bar(main_container)

    def _configure_styles(self):
        """Настройка стилей ttk"""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', font=('Segoe UI', 10))
        style.configure('TButton', font=('Segoe UI', 10), padding=5)
        style.configure('TCheckbutton', font=('Segoe UI', 10))
        style.configure('TFrame', background='#f5f5f5')
        style.configure('TLabelframe', background='#f5f5f5',
                        font=('Segoe UI', 10, 'bold'))
        style.configure('TEntry', font=('Segoe UI', 9))
        style.configure('TCombobox', font=('Segoe UI', 9))

        self.root.configure(bg='#f5f5f5')

    def _create_control_panel(self, parent):
        """Создание панели управления зонами с вкладками"""
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)

        for zone in self.zones:
            tab = ZoneTab(notebook, zone, self, COLORS, LINESTYLES)
            self.zone_tabs.append(tab)

        self._create_global_buttons(parent)

    def _create_global_buttons(self, parent):
        """Создание глобальных кнопок управления"""
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=10)

        buttons = [
            ("✓ Показать все", self.enable_all_zones),
            ("✗ Скрыть все", self.disable_all_zones),
            ("💾 Сохранить PNG", self.save_as_png),
            ("✕ Закрыть", self.root.quit)
        ]

        btn_row = ttk.Frame(btn_frame)
        btn_row.pack()

        for text, command in buttons:
            ttk.Button(btn_row, text=text, command=command,
                       width=18).pack(side=tk.LEFT, padx=2)

    def _create_status_bar(self, parent):
        """Создание строки статуса"""
        self.status_bar = ttk.Frame(parent)
        self.status_bar.pack(fill=tk.X, pady=(5, 0))

        ttk.Label(self.status_bar, text="✓ Готов",
                  font=('Segoe UI', 9)).pack(side=tk.LEFT)

        self._update_status()

    def _update_status(self):
        """Обновление строки статуса"""
        visible_zones = sum(1 for z in self.zones if z.enabled)
        fault_type_name = dict(self.FAULT_TYPES).get(self.fault_type.get(), "")
        status_text = f"Видимых зон: {visible_zones}/{len(self.zones)} | Тип: {fault_type_name}"
        ttk.Label(self.status_bar,
                  text=status_text,
                  font=('Segoe UI', 9), foreground='#666').pack(side=tk.RIGHT)

    def on_fault_type_change(self):
        """Обработка изменения типа повреждения"""
        self.top_panel.update_fault_type_label()
        self.calculate_initial_limits()
        self.plot_characteristics(keep_limits=False)

    def on_selector_toggle(self):
        """Обработка переключения фазового селектора"""
        show_selector = self.show_selector_var.get()
        for zone in self.zones:
            zone.show_selector = show_selector
        self.calculate_initial_limits()
        self.plot_characteristics(keep_limits=True)

    def deferred_update(self):
        """Отложенное обновление графика"""
        self.plot_characteristics(keep_limits=True)
        self.update_job = None

    def plot_characteristics(self, keep_limits=True):
        """Построение характеристик"""
        if self.ax is None:
            return

        current_xlim = self.ax.get_xlim() if keep_limits and self.ax.has_data() else None
        current_ylim = self.ax.get_ylim() if keep_limits and self.ax.has_data() else None

        self.ax.clear()
        visible_zones = 0
        fault_type = self.fault_type.get()
        fault_type_name = dict(self.FAULT_TYPES).get(fault_type, "")

        for zone in self.zones:
            if not zone.enabled:
                continue
            if fault_type == "selector" and not zone.show_selector:
                continue

            visible_zones += 1
            from calculations.characteristic import REL670PolygonalCharacteristic
            poly_char = REL670PolygonalCharacteristic(zone, fault_type)
            points = poly_char.calculate_polygon_points()

            direction_symbol = poly_char.get_direction_symbol()
            type_symbol = poly_char.get_fault_type_symbol()

            from matplotlib.patches import Polygon
            poly = Polygon(points, closed=True, fill=None,
                           edgecolor=zone.color, linestyle=zone.linestyle,
                           linewidth=2.5, alpha=zone.opacity,
                           label=f"Зона {zone.zone_id} {direction_symbol} {type_symbol}")
            self.ax.add_patch(poly)

            # Линия RCA
            rca_x, rca_y = poly_char.get_rca_line()
            self.ax.plot(rca_x, rca_y, color=zone.color, linestyle=':',
                         linewidth=1.5, alpha=0.5)

        # Добавляем подписи углов
        self._add_angle_labels(fault_type)

        # Настройка графика
        self.ax.set_xlabel('R (Ом) - Активное сопротивление', fontsize=10)
        self.ax.set_ylabel('X (Ом) - Реактивное сопротивление', fontsize=10)
        self.ax.set_title(f"{self.title} | {fault_type_name}",
                          fontsize=12, fontweight='bold', pad=5)
        self.ax.grid(True, alpha=0.2, linestyle='--')
        self.ax.axhline(y=0, color='#333', linewidth=1, alpha=0.5)
        self.ax.axvline(x=0, color='#333', linewidth=1, alpha=0.5)
        self.ax.set_aspect('equal')

        # Восстановление пределов
        if keep_limits and current_xlim and current_ylim:
            self.ax.set_xlim(current_xlim)
            self.ax.set_ylim(current_ylim)
        elif self.initial_xlim and self.initial_ylim:
            self.ax.set_xlim(self.initial_xlim)
            self.ax.set_ylim(self.initial_ylim)

        if visible_zones > 0:
            self.ax.legend(loc='upper right', fontsize=8, framealpha=0.9)

        self.canvas.draw_idle()
        self._update_zoom_level()

    def _add_angle_labels(self, fault_type):
        """Добавление подписей углов на график"""
        if fault_type == "phph" or fault_type == "phe":
            # Подпись для угла 115° (2-й квадрант) - для зон защиты
            self.ax.annotate('115°', xy=(3, 8), xytext=(6, 10),
                             arrowprops=dict(arrowstyle='->', color='gray', alpha=0.5),
                             fontsize=8, color='gray')
            # Подпись для угла -15° (4-й квадрант) - для зон защиты
            self.ax.annotate('-15°', xy=(4, -3), xytext=(7, -6),
                             arrowprops=dict(arrowstyle='->', color='gray', alpha=0.5),
                             fontsize=8, color='gray')
        elif fault_type == "selector":
            # Подпись для угла 60° - для фазового селектора
            self.ax.annotate('60°', xy=(3, 5), xytext=(6, 7),
                             arrowprops=dict(arrowstyle='->', color='blue', alpha=0.5),
                             fontsize=8, color='blue')
            self.ax.annotate('-60°', xy=(3, -5), xytext=(6, -7),
                             arrowprops=dict(arrowstyle='->', color='blue', alpha=0.5),
                             fontsize=8, color='blue')
            self.ax.text(0, 10, "Ненаправленная", fontsize=9, color='blue',
                         ha='center', style='italic', alpha=0.7)

    def _update_zoom_level(self):
        """Обновление отображения уровня масштаба"""
        if self.initial_xlim and self.zoom_level:
            xlim = self.ax.get_xlim()
            zoom = (self.initial_xlim[1] - self.initial_xlim[0]) / (xlim[1] - xlim[0])
            self.zoom_level.set(f"{zoom * 100:.0f}%")

    # Методы управления масштабом
    def zoom_in(self):
        """Увеличение масштаба"""
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        x_center = (xlim[0] + xlim[1]) / 2
        y_center = (ylim[0] + ylim[1]) / 2

        self.ax.set_xlim(x_center - (x_center - xlim[0]) * 0.8,
                         x_center + (xlim[1] - x_center) * 0.8)
        self.ax.set_ylim(y_center - (y_center - ylim[0]) * 0.8,
                         y_center + (ylim[1] - y_center) * 0.8)
        self.canvas.draw_idle()
        self._update_zoom_level()

    def zoom_out(self):
        """Уменьшение масштаба"""
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        x_center = (xlim[0] + xlim[1]) / 2
        y_center = (ylim[0] + ylim[1]) / 2

        self.ax.set_xlim(x_center - (x_center - xlim[0]) * 1.25,
                         x_center + (xlim[1] - x_center) * 1.25)
        self.ax.set_ylim(y_center - (y_center - ylim[0]) * 1.25,
                         y_center + (ylim[1] - y_center) * 1.25)
        self.canvas.draw_idle()
        self._update_zoom_level()

    def fit_to_view(self):
        """Подгон под все видимые зоны"""
        self.calculate_initial_limits()
        if self.initial_xlim and self.initial_ylim:
            self.ax.set_xlim(self.initial_xlim)
            self.ax.set_ylim(self.initial_ylim)
            self.canvas.draw_idle()
            self._update_zoom_level()

    def reset_to_initial_scale(self):
        """Сброс к начальному масштабу"""
        if self.ax and self.initial_xlim and self.initial_ylim:
            self.ax.set_xlim(self.initial_xlim)
            self.ax.set_ylim(self.initial_ylim)
            self.canvas.draw_idle()
            self._update_zoom_level()

    def enable_all_zones(self):
        """Включение всех зон"""
        for zone in self.zones:
            zone.enabled = True
            if zone.zone_id in self.zone_vars:
                self.zone_vars[zone.zone_id]["enabled"].set(True)
        self.plot_characteristics(keep_limits=True)

    def disable_all_zones(self):
        """Отключение всех зон"""
        for zone in self.zones:
            zone.enabled = False
            if zone.zone_id in self.zone_vars:
                self.zone_vars[zone.zone_id]["enabled"].set(False)
        self.plot_characteristics(keep_limits=True)

    def save_as_png(self):
        """Сохранение графика в PNG"""
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if filename:
            self.figure.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')

    def show(self):
        """Запуск приложения"""
        if self.root is None:
            self.create_window()
            self.plot_characteristics(keep_limits=False)
        self.root.mainloop()