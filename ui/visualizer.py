# -*- coding: utf-8 -*-
"""
Главный класс визуализатора REL670
"""

import tkinter as tk
from datetime import datetime
from tkinter import ttk
from typing import List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Polygon as MPLPolygon

from models.calculation_points import CalculationPointsSettings, CalculationPoint
from models.common_settings import CommonSettings
from models.selector_calculator import SelectorCalculator
from models.selector_default_settings import SelectorSettings
from models.swing_blocking import SwingBlockingSettings, SwingCalculator
from models.terminal_types import get_terminal_type
from models.zone_calculation import DZSettings
from ui.config_manager import ConfigManager
from ui.constants import COLORS, LINESTYLES, FAULT_TYPES
from ui.events import EventHandler
from ui.markers import MarkerManager
from ui.points_tab import PointsTab
from ui.selector_tab import SelectorTab
from ui.swing_tab import SwingTab
from ui.top_panel import TopPanel
from ui.zone_tab import ZoneTab


class Visualizer:
    """Главный класс визуализатора REL670"""

    FAULT_TYPES = FAULT_TYPES

    def __init__(self, title):
        self.title = title
        self.zones: List[DZSettings] = []  # [DZSettings] - не влияет на работу программы, аннотация
        self.common_settings: Optional[CommonSettings] = None
        self.selector: Optional[SelectorSettings] = None
        self.selector_calculator: Optional[SelectorCalculator] = None
        self.swing_settings: Optional[SwingBlockingSettings] = None
        self.swing_calculator: Optional[SwingCalculator] = None
        self.points_settings: Optional[CalculationPointsSettings] = None
        self.terminal_code: str = "rel670"

        # UI элементы - создаем позже, после создания root в create_window ()
        # Параметры для инициализации окна
        self.root: Optional[tk.Tk] = None  # Создание окна со всеми виджетами
        self.figure = None
        self.ax = None
        self.canvas = None

        # Переменные состояния - создаем позже
        self.zoom_level: Optional[tk.StringVar] = None  # Отрисовка по масштабу
        self.fault_type: Optional[tk.StringVar] = None  # Для понимания типа повреждения

        # Компоненты
        self.markers: Optional[MarkerManager] = None
        self.events: Optional[EventHandler] = None
        self.top_panel: Optional[TopPanel] = None
        self.zone_tabs: List[ZoneTab] = []
        self.selector_tab: Optional[SelectorTab] = None
        self.swing_tab: Optional[SwingTab] = None
        self.points_tab: Optional[PointsTab] = None
        self.status_label: Optional[ttk.Label] = None

        # Контекстное меню
        self.context_menu: Optional[tk.Menu] = None
        self.context_menu_marker = None
        self.context_x: Optional[float] = None
        self.context_y: Optional[float] = None

        # Оптимизация
        self._update_scheduled = False
        self._dirty = False

        # Менеджер конфигурации
        self.config_manager = ConfigManager()

    def add_zone(self, zone: DZSettings) -> None:
        """Добавление зоны"""
        zone.zone_id = len(self.zones) + 1
        if zone.zone_id <= len(COLORS):
            zone.color = COLORS[zone.zone_id - 1][0]
            zone.color_name = COLORS[zone.zone_id - 1][1]
        self.zones.append(zone)  # Здесь хранятся зоны до отрисовки

    def add_common_settings(self, common: CommonSettings) -> None:
        """Добавление общих настроек"""
        self.common_settings = common

    def set_terminal_type(self, terminal_code: str) -> None:
        """Установка типа терминала"""
        terminal = get_terminal_type(terminal_code)
        if terminal:
            self.terminal_code = terminal_code
            # Обновляем параметры селектора
            if self.selector:
                self.selector.x1 = terminal.default_x1
                self.selector.rfpp_forward = terminal.default_rfpp
                self.selector.rfpe_forward = terminal.default_rfpe
                self.selector.rfpp_reverse = terminal.default_rfpp
                self.selector.rfpe_reverse = terminal.default_rfpe
                self.selector_calculator = SelectorCalculator(self.selector)

            # Обновляем параметры блокировки от качаний
            if self.swing_settings:
                self.swing_settings.x1_zin = terminal.default_x1 * terminal.k_zin
                self.swing_settings.rfpp_zin = terminal.default_rfpp * terminal.k_zin
                self.swing_settings.rfpe_zin = terminal.default_rfpe * terminal.k_zin
                self.swing_settings.x1_zout = terminal.default_x1 * terminal.k_zout
                self.swing_settings.rfpp_zout = terminal.default_rfpp * terminal.k_zout
                self.swing_settings.rfpe_zout = terminal.default_rfpe * terminal.k_zout
                self.swing_calculator = SwingCalculator(self.swing_settings)

            self.plot_characteristics(keep_limits=False)
            self._update_status()
            self._show_notification(f"Установлен терминал: {terminal.name}")

    def create_window(self) -> None:
        """Создание главного окна"""
        self.root = tk.Tk()
        self.root.title(self.title)
        self.root.state('zoomed')

        # Создаем StringVar после создания root
        self.zoom_level = tk.StringVar(value="100%")
        self.fault_type = tk.StringVar(value="ph-ph")

        self._configure_styles()
        self.fault_type.trace('w', lambda *args: self.on_fault_type_change())

        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        self.top_panel = TopPanel(main_container, self)
        self.top_panel.pack(fill=tk.X)

        middle_frame = ttk.Frame(main_container)
        middle_frame.pack(fill=tk.BOTH, expand=True, pady=15)

        plot_frame = ttk.Frame(middle_frame)
        plot_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))

        self._create_plot_area(plot_frame)

        control_frame = ttk.Frame(middle_frame, width=650)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y, expand=False)
        control_frame.pack_propagate(False)

        self._create_control_panel(control_frame)
        self._create_status_bar(main_container)
        self._create_context_menu()

        # Инициализируем селектор и калькулятор
        if self.selector is None:
            self.selector = SelectorSettings()
            self.selector_calculator = SelectorCalculator(self.selector)

        # Инициализируем блокировку от качаний
        if self.swing_settings is None:
            self.swing_settings = SwingBlockingSettings()
            self.swing_calculator = SwingCalculator(self.swing_settings)

        # Инициализируем расчетные точки
        if self.points_settings is None:
            self.points_settings = CalculationPointsSettings()
            # Добавляем стандартные точки
            self._add_default_points()

    def _add_default_points(self):
        """Добавление стандартных расчетных точек"""
        from models.calculation_points import DEFAULT_POINTS_REL670
        for point in DEFAULT_POINTS_REL670:
            self.points_settings.add_point(point.name, point.r, point.x)

    def _configure_styles(self) -> None:
        """Настройка стилей"""
        style = ttk.Style()
        style.theme_use('clam')
        bg_color = '#f8f9fa'

        style.configure('TLabel', font=('Segoe UI', 10), background=bg_color)
        style.configure('TButton', font=('Segoe UI', 10), padding=8)
        style.configure('TCheckbutton', font=('Segoe UI', 10), background=bg_color)
        style.configure('TFrame', background=bg_color)
        style.configure('TLabelframe', background=bg_color, font=('Segoe UI', 11, 'bold'))
        style.configure('TEntry', font=('Segoe UI', 9))
        style.configure('TCombobox', font=('Segoe UI', 9))
        style.configure('TNotebook', background=bg_color)
        style.configure('TNotebook.Tab', font=('Segoe UI', 10), padding=[10, 5])

        self.root.configure(bg=bg_color)

    def _create_plot_area(self, parent: ttk.Frame) -> None:
        """Создание области графика"""
        self.figure = plt.Figure(figsize=(8, 8), dpi=100,
                                 facecolor='white', edgecolor='#dddddd')
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('#fafafa')

        self.canvas = FigureCanvasTkAgg(self.figure, master=parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.markers = MarkerManager(self.ax, self.canvas, self)
        self.events = EventHandler(self, self.markers)

        # Подключение событий
        self.canvas.mpl_connect('scroll_event', self.events.on_scroll)
        self.canvas.mpl_connect('button_press_event', self.events.on_mouse_press)
        self.canvas.mpl_connect('button_release_event', self.events.on_mouse_release)
        self.canvas.mpl_connect('motion_notify_event', self.events.on_mouse_motion)
        self.canvas.mpl_connect('pick_event', self.events.on_pick_event)
        self.canvas.get_tk_widget().bind('<Button-3>', self.events.show_context_menu)
        self.canvas.get_tk_widget().configure(cursor="arrow")

        self.ax.set_aspect('equal', adjustable='box')
        self.canvas.draw()

    def _create_context_menu(self) -> None:
        """Создание контекстного меню"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="➕ Добавить маркер на ось R",
                                      command=self._add_marker_r_from_menu)
        self.context_menu.add_command(label="➕ Добавить маркер на ось X",
                                      command=self._add_marker_x_from_menu)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🗑️ Удалить выбранный маркер",
                                      command=self._delete_selected_marker)
        self.context_menu.add_command(label="🗑️ Удалить все маркеры",
                                      command=self.clear_all_markers)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="❌ Отмена")

    def _create_control_panel(self, parent: ttk.Frame) -> None:
        """Создание панели управления"""
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Вкладки зон
        for zone in self.zones:
            tab = ZoneTab(notebook, zone, self, COLORS, LINESTYLES)
            self.zone_tabs.append(tab)

        # Вкладка общих настроек
        if self.common_settings:
            tab = ZoneTab(notebook, self.common_settings, self, COLORS, LINESTYLES, is_common=True)
            self.zone_tabs.append(tab)

        # Вкладка селектора
        if self.selector is None:
            self.selector = SelectorSettings()
            self.selector_calculator = SelectorCalculator(self.selector)
        self.selector_tab = SelectorTab(notebook, self.selector, self, COLORS, LINESTYLES)

        # Вкладка блокировки от качаний
        if self.swing_settings is None:
            self.swing_settings = SwingBlockingSettings()
            self.swing_calculator = SwingCalculator(self.swing_settings)
        self.swing_tab = SwingTab(notebook, self.swing_settings, self, COLORS, LINESTYLES)

        # Вкладка расчетных точек
        if self.points_settings is None:
            self.points_settings = CalculationPointsSettings()
            self._add_default_points()
        self.points_tab = PointsTab(notebook, self.points_settings, self, COLORS, LINESTYLES)

    def _create_status_bar(self, parent: ttk.Frame) -> None:
        """Создание строки состояния"""
        self.status_bar = ttk.Frame(parent)
        self.status_bar.pack(fill=tk.X, pady=(10, 0))

        status_left = ttk.Frame(self.status_bar)
        status_left.pack(side=tk.LEFT)

        instructions = [
            "🖱️ ЛКМ - перетаскивание", "|",
            "🖱️ Колесо - масштаб", "|",
            "Ctrl+ЛКМ - точечный маркер", "|",
            "ПКМ - меню маркеров", "|",
            "Enter - подтвердить параметры"
        ]

        for instr in instructions:
            if instr == "|":
                ttk.Label(status_left, text="|", font=('Segoe UI', 10),
                          foreground='#ccc').pack(side=tk.LEFT, padx=5)
            else:
                ttk.Label(status_left, text=instr, font=('Segoe UI', 9),
                          foreground='#2196F3').pack(side=tk.LEFT)

        status_right = ttk.Frame(self.status_bar)
        status_right.pack(side=tk.RIGHT)

        self.status_label = ttk.Label(status_right, text="Загрузка...",
                                      font=('Segoe UI', 9), foreground='#666666')
        self.status_label.pack(side=tk.RIGHT)

    def _add_marker_r_from_menu(self) -> None:
        """Добавление маркера на ось R из меню"""
        if self.context_x is not None and self.markers:
            self.markers.add_axis_marker_r(self.context_x)
            self.canvas.draw_idle()
            self._show_notification(f"Маркер на оси R: {self.context_x:.2f}")

    def _add_marker_x_from_menu(self) -> None:
        """Добавление маркера на ось X из меню"""
        if self.context_y is not None and self.markers:
            self.markers.add_axis_marker_x(self.context_y)
            self.canvas.draw_idle()
            self._show_notification(f"Маркер на оси X: {self.context_y:.2f}")

    def _delete_selected_marker(self) -> None:
        """Удаление выбранного маркера"""
        if self.context_menu_marker and self.markers:
            marker_type, index = self.context_menu_marker
            if self.markers.delete_marker(marker_type, index):
                self.canvas.draw_idle()
                self._update_status()
                self._show_notification("Маркер удален")
            else:
                self._show_notification("Не удалось удалить маркер")
            self.context_menu_marker = None
        else:
            self._show_notification("Маркер не выбран")

    def clear_all_markers(self) -> None:
        """Очистка всех маркеров"""
        if self.markers:
            self.markers.clear_all_markers()
            self.canvas.draw_idle()
            self._update_status()
            self._show_notification("Все маркеры удалены")

    def reset_measurement_lines(self) -> None:
        """Сброс измерительных линий"""
        if self.markers:
            self.markers.reset_measurement_lines()
            self.canvas.draw_idle()
            self._show_notification("Основные линии сброшены в (0, 0)")

    def zoom_in(self) -> None:
        """Увеличение масштаба"""
        if self.ax is None:
            return
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        x_center = (xlim[0] + xlim[1]) / 2
        y_center = (ylim[0] + ylim[1]) / 2

        self.ax.set_xlim(x_center - (x_center - xlim[0]) * 0.8,
                         x_center + (xlim[1] - x_center) * 0.8)
        self.ax.set_ylim(y_center - (y_center - ylim[0]) * 0.8,
                         y_center + (ylim[1] - y_center) * 0.8)

        if self.markers:
            self.markers.update_marker_positions()
        self.canvas.draw_idle()
        self._update_zoom_level()

    def zoom_out(self) -> None:
        """Уменьшение масштаба"""
        if self.ax is None:
            return
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        x_center = (xlim[0] + xlim[1]) / 2
        y_center = (ylim[0] + ylim[1]) / 2

        self.ax.set_xlim(x_center - (x_center - xlim[0]) * 1.25,
                         x_center + (xlim[1] - x_center) * 1.25)
        self.ax.set_ylim(y_center - (y_center - ylim[0]) * 1.25,
                         y_center + (ylim[1] - y_center) * 1.25)

        if self.markers:
            self.markers.update_marker_positions()
        self.canvas.draw_idle()
        self._update_zoom_level()

    def reset_scale(self) -> None:
        """Сброс масштаба"""
        xlim, ylim = self.calculate_optimal_bounds()
        self.ax.set_xlim(xlim)
        self.ax.set_ylim(ylim)
        if self.markers:
            self.markers.update_marker_positions()
        self.canvas.draw_idle()
        self._update_zoom_level()
        self._show_notification("Масштаб оптимизирован")

    def reset_to_initial_scale(self) -> None:
        """Сброс к начальному масштабу"""
        self.reset_scale()

    def fit_to_view(self) -> None:
        """Подгонка под содержимое"""
        self.reset_scale()

    def on_fault_type_change(self) -> None:
        """Обработка изменения типа повреждения"""
        if self.top_panel:
            self.top_panel.update_fault_type_label()
        self.plot_characteristics(keep_limits=False)
        self._update_status()

    def calculate_optimal_bounds(self) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """Расчет оптимальных границ графика"""
        all_min_r = float('inf')
        all_max_r = float('-inf')
        all_min_x = float('inf')
        all_max_x = float('-inf')

        fault_type = self.fault_type.get() if self.fault_type else "ph-ph"

        # Сбор границ зон
        for zone in self.zones:
            if zone.enabled:
                min_r, max_r, min_x, max_x = zone.get_bounds(fault_type)
                all_min_r = min(all_min_r, min_r)
                all_max_r = max(all_max_r, max_r)
                all_min_x = min(all_min_x, min_x)
                all_max_x = max(all_max_x, max_x)

        # Сбор границ селектора
        if self.selector and self.selector.enabled and self.selector_calculator:
            points = self.selector_calculator.get_polygon_points(fault_type)
            for r, x in points:
                all_min_r = min(all_min_r, r)
                all_max_r = max(all_max_r, r)
                all_min_x = min(all_min_x, x)
                all_max_x = max(all_max_x, x)

        # Сбор границ блокировки от качаний
        if self.swing_settings and self.swing_settings.enabled and self.swing_calculator:
            if self.swing_settings.show_zin:
                points = self.swing_calculator.get_zin_polygon_points()
                for r, x in points:
                    all_min_r = min(all_min_r, r)
                    all_max_r = max(all_max_r, r)
                    all_min_x = min(all_min_x, x)
                    all_max_x = max(all_max_x, x)
            if self.swing_settings.show_zout:
                points = self.swing_calculator.get_zout_polygon_points()
                for r, x in points:
                    all_min_r = min(all_min_r, r)
                    all_max_r = max(all_max_r, r)
                    all_min_x = min(all_min_x, x)
                    all_max_x = max(all_max_x, x)

        # Сбор границ расчетных точек
        if self.points_settings and self.points_settings.enabled:
            for point in self.points_settings.points:
                all_min_r = min(all_min_r, point.r)
                all_max_r = max(all_max_r, point.r)
                all_min_x = min(all_min_x, point.x)
                all_max_x = max(all_max_x, point.x)

        if all_min_r == float('inf'):
            return (-5, 10), (-5, 8)

        # Добавление отступов
        r_range = all_max_r - all_min_r
        x_range = all_max_x - all_min_x
        r_margin = max(r_range * 0.2, 1.0)
        x_margin = max(x_range * 0.2, 1.0)

        xlim = (all_min_r - r_margin, all_max_r + r_margin)
        ylim = (all_min_x - x_margin, all_max_x + x_margin)

        # Сохранение соотношения сторон
        x_range = xlim[1] - xlim[0]
        y_range = ylim[1] - ylim[0]
        max_range = max(x_range, y_range)
        x_center = (xlim[0] + xlim[1]) / 2
        y_center = (ylim[0] + ylim[1]) / 2

        return (x_center - max_range / 2, x_center + max_range / 2), \
            (y_center - max_range / 2, y_center + max_range / 2)

    def plot_characteristics(self, keep_limits: bool = True) -> None:
        """Полная перерисовка характеристик"""
        if not self.ax:
            return

        # Сохраняем состояние маркеров
        if self.markers:
            self.markers.save_state()
            line_pos_r = self.markers.line_position_r
            line_pos_x = self.markers.line_position_x
        else:
            line_pos_r = 0.0
            line_pos_x = 0.0

        # Очистка графика
        self.ax.clear()

        fault_type = self.fault_type.get() if self.fault_type else "ph-ph"
        fault_type_name = dict(self.FAULT_TYPES).get(fault_type, "")

        # Отрисовка компонентов
        self._plot_load_encroachment(fault_type)
        self._plot_selector(fault_type)
        self._plot_zones(fault_type)
        self._plot_swing_blocking(fault_type)
        self._plot_calculation_points()

        # Восстановление маркеров
        self.markers = MarkerManager(self.ax, self.canvas, self)
        self.markers.line_position_r = line_pos_r
        self.markers.line_position_x = line_pos_x
        self.markers.vertical_line.set_xdata([line_pos_r, line_pos_r])
        self.markers.horizontal_line.set_ydata([line_pos_x, line_pos_x])
        self.markers._update_measurement_text()

        # Настройка осей
        self._configure_axes(fault_type_name)

        # Легенда
        handles, labels = self.ax.get_legend_handles_labels()
        if handles:
            self.ax.legend(loc='upper right', fontsize=9, framealpha=0.9,
                           facecolor='white', edgecolor='#CCCCCC')

        self.canvas.draw_idle()
        self._update_zoom_level()

    def _plot_load_encroachment(self, fault_type: str) -> None:
        """Отрисовка зоны нагрузки"""
        if not (self.selector and self.selector.load_enabled and self.selector.enabled and self.selector_calculator):
            return

        # Полигоны нагрузки
        load_polygons = self.selector_calculator.get_load_encroachment_polygons(fault_type)
        for i, poly_points in enumerate(load_polygons):
            if len(poly_points) >= 3:
                load_array = np.array(poly_points)
                load_patch = MPLPolygon(load_array, closed=True,
                                        facecolor='#FFEB3B',
                                        alpha=0.2,
                                        label="Зона нагрузки" if i == 0 else "_nolegend_")
                self.ax.add_patch(load_patch)

        # Линии нагрузки
        load_lines = self._get_load_lines_from_polygons(load_polygons)
        for x1, y1, x2, y2 in load_lines:
            self.ax.plot([x1, x2], [y1, y2],
                         color='#F57F17', linestyle='--',
                         linewidth=2.0, alpha=0.8)

    def _get_load_lines_from_polygons(self, polygons: List) -> List:
        """Извлечение линий из полигонов нагрузки"""
        lines = []
        for poly in polygons:
            if len(poly) >= 3:
                n = len(poly)
                for i in range(n):
                    p1 = poly[i]
                    p2 = poly[(i + 1) % n]
                    lines.append((p1[0], p1[1], p2[0], p2[1]))
        return lines

    def _plot_selector(self, fault_type: str) -> None:
        """Отрисовка фазового селектора"""
        if not (self.selector and self.selector.enabled and self.selector_calculator):
            return

        # Полный селектор
        selector_points = self.selector_calculator.get_polygon_points(fault_type)
        if len(selector_points) >= 3:
            points_array = np.array(selector_points)
            poly = MPLPolygon(points_array, closed=True, fill=None,
                              edgecolor=self.selector.color,
                              linestyle=self.selector.linestyle,
                              linewidth=3.0, alpha=self.selector.opacity,
                              label="Фазовый селектор")
            self.ax.add_patch(poly)

        # Обрезанный селектор
        if self.selector.load_enabled:
            clipped_points = self.selector_calculator.get_clipped_selector_points(fault_type)
            if clipped_points and len(clipped_points) >= 3:
                points_array = np.array(clipped_points)
                poly_fill = MPLPolygon(points_array, closed=True,
                                       facecolor=self.selector.color,
                                       alpha=0.15, label="_nolegend_")
                self.ax.add_patch(poly_fill)

                poly_edge = MPLPolygon(points_array, closed=True, fill=None,
                                       edgecolor='#FF6F00', linestyle='-',
                                       linewidth=4.0, alpha=1.0,
                                       label="Селектор (обрезанный)")
                self.ax.add_patch(poly_edge)

                # Точки пересечения
                intersection_points = self.selector_calculator.get_intersection_points(fault_type)
                if intersection_points:
                    x_coords = [p[0] for p in intersection_points]
                    y_coords = [p[1] for p in intersection_points]
                    self.ax.scatter(x_coords, y_coords,
                                    color='red', s=80, zorder=10,
                                    marker='o', edgecolors='white', linewidth=2,
                                    label="Точки пересечения")

                    for r, x in intersection_points:
                        self.ax.annotate(f'({r:.1f}, {x:.1f})',
                                         xy=(r, x), xytext=(10, 10),
                                         textcoords='offset points',
                                         fontsize=8,
                                         bbox=dict(boxstyle='round,pad=0.3',
                                                   facecolor='white',
                                                   edgecolor='red',
                                                   alpha=0.8))

    def _plot_zones(self, fault_type: str) -> None:
        """Отрисовка зон защиты"""
        print(f"[Visualizer] Отрисовка зон, fault_type={fault_type}, zones={len(self.zones)}")
        for zone in self.zones:
            print(f"  Zone {zone.zone_id}: enabled={zone.enabled}, x1={zone.x1}, r1={zone.r1}")
            if not zone.enabled:
                continue

            points = zone.get_polygon_points(fault_type)
            if points:
                points_array = np.array(points)
                direction_symbol = {
                    "forward": "↑",
                    "reverse": "↓",
                    "non-directional": "↕"
                }.get(zone.direction_mode, "")

                poly = MPLPolygon(points_array, closed=True, fill=None,
                                  edgecolor=zone.color, linestyle=zone.linestyle,
                                  linewidth=2.5, alpha=zone.opacity,
                                  label=f"Зона {zone.zone_id} {direction_symbol}")
                self.ax.add_patch(poly)
                print(f"    Добавлен полигон с {len(points)} точками")

    def _plot_swing_blocking(self, fault_type: str) -> None:
        """Отрисовка блокировки от качаний"""
        if not (self.swing_settings and self.swing_settings.enabled and self.swing_calculator):
            return

        # ZIN - внутренняя зона
        if self.swing_settings.show_zin:
            zin_points = self.swing_calculator.get_clipped_zin_points()
            if zin_points and len(zin_points) >= 3:
                points_array = np.array(zin_points)

                # Заливка
                poly_fill = MPLPolygon(points_array, closed=True,
                                       facecolor=self.swing_settings.color_zin,
                                       alpha=self.swing_settings.opacity_zin * 0.3,
                                       label="_nolegend_")
                self.ax.add_patch(poly_fill)

                # Контур
                poly_edge = MPLPolygon(points_array, closed=True, fill=None,
                                       edgecolor=self.swing_settings.color_zin,
                                       linestyle=self.swing_settings.linestyle_zin,
                                       linewidth=2.5,
                                       alpha=self.swing_settings.opacity_zin,
                                       label="ZIN (внутренняя)")
                self.ax.add_patch(poly_edge)

        # ZOUT - внешняя зона
        if self.swing_settings.show_zout:
            zout_points = self.swing_calculator.get_clipped_zout_points()
            if zout_points and len(zout_points) >= 3:
                points_array = np.array(zout_points)

                # Заливка
                poly_fill = MPLPolygon(points_array, closed=True,
                                       facecolor=self.swing_settings.color_zout,
                                       alpha=self.swing_settings.opacity_zout * 0.2,
                                       label="_nolegend_")
                self.ax.add_patch(poly_fill)

                # Контур
                poly_edge = MPLPolygon(points_array, closed=True, fill=None,
                                       edgecolor=self.swing_settings.color_zout,
                                       linestyle=self.swing_settings.linestyle_zout,
                                       linewidth=2.0,
                                       alpha=self.swing_settings.opacity_zout,
                                       label="ZOUT (внешняя)")
                self.ax.add_patch(poly_edge)

    def _plot_calculation_points(self) -> None:
        """Отрисовка расчетных точек"""
        if not (self.points_settings and self.points_settings.enabled):
            return

        for point in self.points_settings.points:
            if not point.enabled:
                continue

            # Маркер
            self.ax.scatter([point.r], [point.x],
                            color=point.color,
                            s=self.points_settings.marker_size ** 2 * 2,
                            zorder=15,
                            marker='o',
                            edgecolors='white',
                            linewidth=2,
                            label=f"Точка: {point.name}" if self.points_settings.show_labels else "_nolegend_")

            # Подпись
            if self.points_settings.show_labels:
                self.ax.annotate(f'  {point.name}',
                                 xy=(point.r, point.x),
                                 xytext=(10, 5),
                                 textcoords='offset points',
                                 fontsize=9,
                                 fontweight='bold',
                                 color=point.color,
                                 bbox=dict(boxstyle='round,pad=0.3',
                                           facecolor='white',
                                           edgecolor=point.color,
                                           alpha=0.8))

    def _configure_axes(self, fault_type_name: str) -> None:
        """Настройка осей"""
        self.ax.set_xlabel('R (Ом) - Активное сопротивление', fontsize=11, fontweight='bold')
        self.ax.set_ylabel('X (Ом) - Реактивное сопротивление', fontsize=11, fontweight='bold')

        terminal_name = get_terminal_type(self.terminal_code).name if get_terminal_type(
            self.terminal_code) else "REL670"
        self.ax.set_title(f"{self.title} | {terminal_name} | {fault_type_name}",
                          fontsize=14, fontweight='bold', pad=15, color='#2196F3')

        self.ax.grid(True, alpha=0.7, linestyle='-', color='#AAAAAA', linewidth=0.8)
        self.ax.grid(True, which='minor', alpha=0.3, linestyle=':', color='#666666', linewidth=0.5)
        self.ax.minorticks_on()

        self.ax.axhline(y=0, color='#333333', linewidth=2, alpha=0.9)
        self.ax.axvline(x=0, color='#333333', linewidth=2, alpha=0.9)
        self.ax.set_facecolor('#fafafa')
        self.ax.set_aspect('equal', adjustable='box')

        xlim, ylim = self.calculate_optimal_bounds()
        self.ax.set_xlim(xlim)
        self.ax.set_ylim(ylim)

        if self.markers:
            self.markers.update_marker_positions()

    def _update_zoom_level(self) -> None:
        """Обновление уровня зума"""
        if self.zoom_level and self.ax:
            xlim, ylim = self.calculate_optimal_bounds()
            current_xlim = self.ax.get_xlim()
            zoom_x = (xlim[1] - xlim[0]) / (current_xlim[1] - current_xlim[0])
            self.zoom_level.set(f"{zoom_x * 100:.0f}%")

    def _update_status(self) -> None:
        """Обновление строки состояния"""
        if not hasattr(self, 'status_label') or not self.status_label:
            return

        visible_zones = sum(1 for z in self.zones if z.enabled)
        visible_common = 1 if (self.common_settings and self.common_settings.enabled) else 0
        visible_selector = 1 if (self.selector and self.selector.enabled) else 0
        visible_swing = 1 if (self.swing_settings and self.swing_settings.enabled) else 0
        visible_points = 1 if (self.points_settings and self.points_settings.enabled) else 0
        total_visible = visible_zones + visible_common + visible_selector + visible_swing + visible_points
        total_items = len(self.zones) + (1 if self.common_settings else 0) + 1 + 1 + 1

        fault_type_name = dict(self.FAULT_TYPES).get(self.fault_type.get() if self.fault_type else "ph-ph", "")

        if self.markers and hasattr(self.markers, 'get_stats'):
            stats = self.markers.get_stats()
        else:
            stats = {'point': 0, 'r': 0, 'x': 0}

        terminal_name = get_terminal_type(self.terminal_code).name if get_terminal_type(
            self.terminal_code) else "REL670"

        self.status_label.config(
            text=f"Терминал: {terminal_name}  |  "
                 f"Элементов: {total_visible}/{total_items}  |  "
                 f"Маркеры: ●{stats['point']}  |  "
                 f"R↓{stats['r']}  |  "
                 f"X→{stats['x']}  |  "
                 f"Тип: {fault_type_name}"
        )

    def enable_all_zones(self) -> None:
        """Включить все зоны"""
        for zone in self.zones:
            zone.enabled = True
        if self.selector:
            self.selector.enabled = True
        if self.swing_settings:
            self.swing_settings.enabled = True
        if self.points_settings:
            self.points_settings.enabled = True

        self._update_ui_checkboxes(True)
        self.plot_characteristics(keep_limits=False)
        self._update_status()
        self._show_notification("Все элементы включены")

    def disable_all_zones(self) -> None:
        """Выключить все зоны"""
        for zone in self.zones:
            zone.enabled = False
        if self.selector:
            self.selector.enabled = False
        if self.swing_settings:
            self.swing_settings.enabled = False
        if self.points_settings:
            self.points_settings.enabled = False

        self._update_ui_checkboxes(False)
        self.plot_characteristics(keep_limits=False)
        self._update_status()
        self._show_notification("Все элементы выключены")

    def _update_ui_checkboxes(self, value: bool) -> None:
        """Обновление чекбоксов в UI"""
        for tab in self.zone_tabs:
            if hasattr(tab, 'vars') and 'enabled' in tab.vars:
                tab.vars['enabled'].set(value)

        if self.selector_tab and hasattr(self.selector_tab, 'vars') and 'enabled' in self.selector_tab.vars:
            self.selector_tab.vars['enabled'].set(value)

        if self.swing_tab and hasattr(self.swing_tab, 'vars') and 'enabled' in self.swing_tab.vars:
            self.swing_tab.vars['enabled'].set(value)

        if self.points_tab and hasattr(self.points_tab, 'vars') and 'enabled' in self.points_tab.vars:
            self.points_tab.vars['enabled'].set(value)

    def _update_all_calculators(self) -> None:
        """Обновляет все калькуляторы после изменения параметров"""
        # Обновляем калькулятор селектора
        if self.selector:
            from models.selector_calculator import SelectorCalculator
            self.selector_calculator = SelectorCalculator(self.selector)

        # Обновляем калькулятор блокировки от качаний
        if self.swing_settings:
            from models.swing_blocking import SwingCalculator
            self.swing_calculator = SwingCalculator(self.swing_settings)

    def save_as_png(self) -> None:
        """Сохранение в PNG"""
        from tkinter import filedialog
        default_name = f"rel670_{self.fault_type.get() if self.fault_type else 'ph-ph'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filename = filedialog.asksaveasfilename(defaultextension=".png", initialfile=default_name,
                                                filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
        if filename:
            self.figure.savefig(filename, dpi=300, bbox_inches='tight',
                                facecolor='white', edgecolor='none')
            self._show_notification(f"Сохранено: {filename}")

    def save_configuration(self, filename: str = "config.json") -> bool:
        """Сохранение конфигурации"""
        config = {
            'terminal_code': self.terminal_code,
            'zones': [],
            'common_settings': None,
            'selector': None,
            'swing_settings': None,
            'points_settings': None,
        }

        # Сохраняем зоны
        for zone in self.zones:
            config['zones'].append({
                'x1': zone.x1,
                'r1': zone.r1,
                'rfpp': zone.rfpp,
                'x0': zone.x0,
                'r0': zone.r0,
                'rfpe': zone.rfpe,
                'direction_mode': zone.direction_mode,
                'name': zone.name,
                'enabled': zone.enabled,
                'color': zone.color,
                'linestyle': zone.linestyle,
                'opacity': zone.opacity,
                'zone_id': zone.zone_id,
            })

        # Сохраняем Common Settings
        if self.common_settings:
            config['common_settings'] = {
                'u_base': self.common_settings.u_base,
                'i_base': self.common_settings.i_base,
                'i_secondary': self.common_settings.i_secondary,
                'u_secondary': self.common_settings.u_secondary,
                'angle_quad2': self.common_settings.angle_quad2,
                'angle_quad4': self.common_settings.angle_quad4,
                'angle_phs': self.common_settings.angle_phs,
            }

        # Сохраняем Selector
        if self.selector:
            config['selector'] = {
                'x1': self.selector.x1,
                'x0': self.selector.x0,
                'rfpp_forward': self.selector.rfpp_forward,
                'rfpp_reverse': self.selector.rfpp_reverse,
                'rfpe_forward': self.selector.rfpe_forward,
                'rfpe_reverse': self.selector.rfpe_reverse,
                'rld_forward': self.selector.rld_forward,
                'rld_reverse': self.selector.rld_reverse,
                'arg_load': self.selector.arg_load,
                'arg_load_phph': self.selector.arg_load_phph,
                'arg_load_3ph': self.selector.arg_load_3ph,
                'load_enabled': self.selector.load_enabled,
                'enabled': self.selector.enabled,
                'color': self.selector.color,
                'linestyle': self.selector.linestyle,
                'opacity': self.selector.opacity,
            }

        # Сохраняем Swing Blocking
        if self.swing_settings:
            config['swing_settings'] = {
                'x1_zin': self.swing_settings.x1_zin,
                'rfpp_zin': self.swing_settings.rfpp_zin,
                'rfpe_zin': self.swing_settings.rfpe_zin,
                'x1_zout': self.swing_settings.x1_zout,
                'rfpp_zout': self.swing_settings.rfpp_zout,
                'rfpe_zout': self.swing_settings.rfpe_zout,
                'rld_forward_zin': self.swing_settings.rld_forward_zin,
                'rld_reverse_zin': self.swing_settings.rld_reverse_zin,
                'arg_load_zin': self.swing_settings.arg_load_zin,
                'rld_forward_zout': self.swing_settings.rld_forward_zout,
                'rld_reverse_zout': self.swing_settings.rld_reverse_zout,
                'arg_load_zout': self.swing_settings.arg_load_zout,
                'load_enabled': self.swing_settings.load_enabled,
                'enabled': self.swing_settings.enabled,
                'show_zin': self.swing_settings.show_zin,
                'show_zout': self.swing_settings.show_zout,
                'color_zin': self.swing_settings.color_zin,
                'color_zout': self.swing_settings.color_zout,
                'linestyle_zin': self.swing_settings.linestyle_zin,
                'linestyle_zout': self.swing_settings.linestyle_zout,
                'opacity_zin': self.swing_settings.opacity_zin,
                'opacity_zout': self.swing_settings.opacity_zout,
            }

        # Сохраняем Points
        if self.points_settings:
            config['points_settings'] = {
                'points': [
                    {
                        'name': p.name,
                        'r': p.r,
                        'x': p.x,
                        'color': p.color,
                        'enabled': p.enabled,
                    }
                    for p in self.points_settings.points
                ],
                'enabled': self.points_settings.enabled,
                'show_labels': self.points_settings.show_labels,
                'marker_size': self.points_settings.marker_size,
            }

        return self.config_manager.save_config(config, filename)

    def load_configuration(self, filename: str = "config.json") -> bool:
        """Загрузка конфигурации"""
        config = self.config_manager.load_config(filename)
        if not config:
            return False

        try:
            # Очищаем текущие зоны
            self.zones.clear()

            # Загружаем тип терминала
            if 'terminal_code' in config:
                self.set_terminal_type(config['terminal_code'])

            # Загружаем зоны
            if 'zones' in config:
                for zone_data in config['zones']:
                    zone = DZSettings(
                        x1=zone_data.get('x1', 3.0),
                        r1=zone_data.get('r1', 1.5),
                        rfpp=zone_data.get('rfpp', 5.0),
                        x0=zone_data.get('x0', 9.0),
                        r0=zone_data.get('r0', 4.5),
                        rfpe=zone_data.get('rfpe', 8.0),
                        direction_mode=zone_data.get('direction_mode', 'forward'),
                        name=zone_data.get('name', 'Zone'),
                        enabled=zone_data.get('enabled', True),
                        color=zone_data.get('color', '#2196F3'),
                        linestyle=zone_data.get('linestyle', '-'),
                        opacity=zone_data.get('opacity', 0.8),
                    )
                    zone.zone_id = zone_data.get('zone_id', len(self.zones) + 1)
                    self.zones.append(zone)

            # Загружаем Common Settings
            if 'common_settings' in config and self.common_settings:
                cs = config['common_settings']
                self.common_settings.u_base = cs.get('u_base', 115000.0)
                self.common_settings.i_base = cs.get('i_base', 600.0)
                self.common_settings.i_secondary = cs.get('i_secondary', 5.0)
                self.common_settings.u_secondary = cs.get('u_secondary', 100.0)
                self.common_settings.angle_quad2 = cs.get('angle_quad2', -15.0)
                self.common_settings.angle_quad4 = cs.get('angle_quad4', 115.0)
                self.common_settings.angle_phs = cs.get('angle_phs', 60.0)

            # Загружаем Selector
            if 'selector' in config and self.selector:
                sel = config['selector']
                self.selector.x1 = sel.get('x1', 37.0)
                self.selector.x0 = sel.get('x0', 43.0)
                self.selector.rfpp_forward = sel.get('rfpp_forward', 164.0)
                self.selector.rfpp_reverse = sel.get('rfpp_reverse', 164.0)
                self.selector.rfpe_forward = sel.get('rfpe_forward', 135.0)
                self.selector.rfpe_reverse = sel.get('rfpe_reverse', 135.0)
                self.selector.rld_forward = sel.get('rld_forward', 96.0)
                self.selector.rld_reverse = sel.get('rld_reverse', 96.0)
                self.selector.arg_load = sel.get('arg_load', 35.0)
                self.selector.arg_load_phph = sel.get('arg_load_phph', 30.0)
                self.selector.arg_load_3ph = sel.get('arg_load_3ph', 30.0)
                self.selector.load_enabled = sel.get('load_enabled', True)
                self.selector.enabled = sel.get('enabled', True)
                self.selector.color = sel.get('color', '#9C27B0')
                self.selector.linestyle = sel.get('linestyle', '-')
                self.selector.opacity = sel.get('opacity', 0.8)
                self.selector_calculator = SelectorCalculator(self.selector)

            # Загружаем Swing Blocking
            if 'swing_settings' in config and self.swing_settings:
                sw = config['swing_settings']
                self.swing_settings.x1_zin = sw.get('x1_zin', 37.0)
                self.swing_settings.rfpp_zin = sw.get('rfpp_zin', 164.0)
                self.swing_settings.rfpe_zin = sw.get('rfpe_zin', 135.0)
                self.swing_settings.x1_zout = sw.get('x1_zout', 55.0)
                self.swing_settings.rfpp_zout = sw.get('rfpp_zout', 200.0)
                self.swing_settings.rfpe_zout = sw.get('rfpe_zout', 180.0)
                self.swing_settings.rld_forward_zin = sw.get('rld_forward_zin', 96.0)
                self.swing_settings.rld_reverse_zin = sw.get('rld_reverse_zin', 96.0)
                self.swing_settings.arg_load_zin = sw.get('arg_load_zin', 35.0)
                self.swing_settings.rld_forward_zout = sw.get('rld_forward_zout', 80.0)
                self.swing_settings.rld_reverse_zout = sw.get('rld_reverse_zout', 80.0)
                self.swing_settings.arg_load_zout = sw.get('arg_load_zout', 30.0)
                self.swing_settings.load_enabled = sw.get('load_enabled', True)
                self.swing_settings.enabled = sw.get('enabled', True)
                self.swing_settings.show_zin = sw.get('show_zin', True)
                self.swing_settings.show_zout = sw.get('show_zout', True)
                self.swing_settings.color_zin = sw.get('color_zin', '#FF5722')
                self.swing_settings.color_zout = sw.get('color_zout', '#FF9800')
                self.swing_settings.linestyle_zin = sw.get('linestyle_zin', '-')
                self.swing_settings.linestyle_zout = sw.get('linestyle_zout', '-')
                self.swing_settings.opacity_zin = sw.get('opacity_zin', 0.6)
                self.swing_settings.opacity_zout = sw.get('opacity_zout', 0.4)
                self.swing_calculator = SwingCalculator(self.swing_settings)

            # Загружаем Points
            if 'points_settings' in config and self.points_settings:
                pts = config['points_settings']
                self.points_settings.points.clear()
                for p in pts.get('points', []):
                    self.points_settings.points.append(
                        CalculationPoint(
                            name=p.get('name', 'Point'),
                            r=p.get('r', 0.0),
                            x=p.get('x', 0.0),
                            color=p.get('color', '#E91E63'),
                            enabled=p.get('enabled', True),
                        )
                    )
                self.points_settings.enabled = pts.get('enabled', True)
                self.points_settings.show_labels = pts.get('show_labels', True)
                self.points_settings.marker_size = pts.get('marker_size', 8.0)

            # Обновляем UI
            self._update_ui_from_config()

            self.plot_characteristics(keep_limits=False)
            self._update_status()
            self._show_notification("Конфигурация загружена")
            return True

        except Exception as e:
            self._show_notification(f"Ошибка загрузки: {e}")
            return False

    def _update_ui_from_config(self) -> None:
        """Обновление UI из загруженной конфигурации"""
        # Обновляем вкладки зон
        for i, tab in enumerate(self.zone_tabs):
            if i < len(self.zones):
                zone = self.zones[i]
                if hasattr(tab, 'vars'):
                    if 'enabled' in tab.vars:
                        tab.vars['enabled'].set(zone.enabled)
                    if 'color' in tab.vars:
                        tab.vars['color'].set(zone.color)
                    if 'style' in tab.vars:
                        tab.vars['style'].set(zone.linestyle)

        # Обновляем селектор
        if self.selector_tab and self.selector:
            if hasattr(self.selector_tab, 'vars'):
                self.selector_tab.vars['enabled'].set(self.selector.enabled)
                self.selector_tab.vars['color'].set(self.selector.color)
                self.selector_tab.vars['style'].set(self.selector.linestyle)
                self.selector_tab.vars['load_enabled'].set(self.selector.load_enabled)

        # Обновляем блокировку от качаний
        if self.swing_tab and self.swing_settings:
            if hasattr(self.swing_tab, 'vars'):
                self.swing_tab.vars['enabled'].set(self.swing_settings.enabled)
                self.swing_tab.vars['load_enabled'].set(self.swing_settings.load_enabled)
                self.swing_tab.vars['show_zin'].set(self.swing_settings.show_zin)
                self.swing_tab.vars['show_zout'].set(self.swing_settings.show_zout)

        # Обновляем расчетные точки
        if self.points_tab and self.points_settings:
            if hasattr(self.points_tab, 'vars'):
                self.points_tab.vars['enabled'].set(self.points_settings.enabled)
                self.points_tab.vars['show_labels'].set(self.points_settings.show_labels)
            if hasattr(self.points_tab, '_update_points_list'):
                self.points_tab._update_points_list()

    def save_configuration_dialog(self) -> None:
        """Диалог сохранения конфигурации"""
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            if self.config_manager.export_config(self._get_full_config(), filename):
                self._show_notification(f"Конфигурация сохранена: {filename}")
            else:
                self._show_notification("Ошибка сохранения конфигурации")

    def load_configuration_dialog(self) -> None:
        """Диалог загрузки конфигурации"""
        from tkinter import filedialog
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            config = self.config_manager.import_config(filename)
            if config:
                self._apply_full_config(config)
                self.plot_characteristics(keep_limits=False)
                self._update_status()
                self._show_notification(f"Конфигурация загружена: {filename}")
            else:
                self._show_notification("Ошибка загрузки конфигурации")

    def _get_full_config(self) -> dict:
        """Получить полную конфигурацию"""
        config = {
            'terminal_code': self.terminal_code,
            'zones': [],
            'common_settings': None,
            'selector': None,
            'swing_settings': None,
            'points_settings': None,
        }

        # Сохраняем зоны
        for zone in self.zones:
            config['zones'].append({
                'x1': zone.x1,
                'r1': zone.r1,
                'rfpp': zone.rfpp,
                'x0': zone.x0,
                'r0': zone.r0,
                'rfpe': zone.rfpe,
                'direction_mode': zone.direction_mode,
                'name': zone.name,
                'enabled': zone.enabled,
                'color': zone.color,
                'linestyle': zone.linestyle,
                'opacity': zone.opacity,
                'zone_id': zone.zone_id,
            })

        # Сохраняем Common Settings
        if self.common_settings:
            config['common_settings'] = {
                'u_base': self.common_settings.u_base,
                'i_base': self.common_settings.i_base,
                'i_secondary': self.common_settings.i_secondary,
                'u_secondary': self.common_settings.u_secondary,
                'angle_quad2': self.common_settings.angle_quad2,
                'angle_quad4': self.common_settings.angle_quad4,
                'angle_phs': self.common_settings.angle_phs,
            }

        # Сохраняем Selector
        if self.selector:
            config['selector'] = {
                'x1': self.selector.x1,
                'x0': self.selector.x0,
                'rfpp_forward': self.selector.rfpp_forward,
                'rfpp_reverse': self.selector.rfpp_reverse,
                'rfpe_forward': self.selector.rfpe_forward,
                'rfpe_reverse': self.selector.rfpe_reverse,
                'rld_forward': self.selector.rld_forward,
                'rld_reverse': self.selector.rld_reverse,
                'arg_load': self.selector.arg_load,
                'arg_load_phph': self.selector.arg_load_phph,
                'arg_load_3ph': self.selector.arg_load_3ph,
                'load_enabled': self.selector.load_enabled,
                'enabled': self.selector.enabled,
                'color': self.selector.color,
                'linestyle': self.selector.linestyle,
                'opacity': self.selector.opacity,
            }

        # Сохраняем Swing Blocking
        if self.swing_settings:
            config['swing_settings'] = {
                'x1_zin': self.swing_settings.x1_zin,
                'rfpp_zin': self.swing_settings.rfpp_zin,
                'rfpe_zin': self.swing_settings.rfpe_zin,
                'x1_zout': self.swing_settings.x1_zout,
                'rfpp_zout': self.swing_settings.rfpp_zout,
                'rfpe_zout': self.swing_settings.rfpe_zout,
                'rld_forward_zin': self.swing_settings.rld_forward_zin,
                'rld_reverse_zin': self.swing_settings.rld_reverse_zin,
                'arg_load_zin': self.swing_settings.arg_load_zin,
                'rld_forward_zout': self.swing_settings.rld_forward_zout,
                'rld_reverse_zout': self.swing_settings.rld_reverse_zout,
                'arg_load_zout': self.swing_settings.arg_load_zout,
                'load_enabled': self.swing_settings.load_enabled,
                'enabled': self.swing_settings.enabled,
                'show_zin': self.swing_settings.show_zin,
                'show_zout': self.swing_settings.show_zout,
                'color_zin': self.swing_settings.color_zin,
                'color_zout': self.swing_settings.color_zout,
                'linestyle_zin': self.swing_settings.linestyle_zin,
                'linestyle_zout': self.swing_settings.linestyle_zout,
                'opacity_zin': self.swing_settings.opacity_zin,
                'opacity_zout': self.swing_settings.opacity_zout,
            }

        # Сохраняем Points
        if self.points_settings:
            config['points_settings'] = {
                'points': [
                    {
                        'name': p.name,
                        'r': p.r,
                        'x': p.x,
                        'color': p.color,
                        'enabled': p.enabled,
                    }
                    for p in self.points_settings.points
                ],
                'enabled': self.points_settings.enabled,
                'show_labels': self.points_settings.show_labels,
                'marker_size': self.points_settings.marker_size,
            }

        return config

    def _apply_full_config(self, config: dict) -> None:
        """Применить полную конфигурацию"""
        # Используем существующий метод load_configuration
        # Но сначала сохраняем в файл и загружаем оттуда
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            import json
            json.dump(config, f, indent=2)
            temp_file = f.name

        try:
            self.load_configuration(temp_file)
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def _show_notification(self, message: str) -> None:
        """Показ уведомления"""
        if not self.root:
            return

        notification = tk.Toplevel(self.root)
        notification.overrideredirect(True)
        notification.geometry("+{}+{}".format(
            self.root.winfo_rootx() + self.root.winfo_width() - 300,
            self.root.winfo_rooty() + 50
        ))
        frame = tk.Frame(notification, bg='#333333', padx=20, pady=10, relief='flat')
        frame.pack()
        tk.Label(frame, text=message, bg='#333333', fg='white', font=('Segoe UI', 10)).pack()
        self.root.after(2000, notification.destroy)

    def show(self) -> None:
        """Запуск приложения"""
        if self.root is None:
            self.create_window()
            self.plot_characteristics(keep_limits=False)
            self._update_status()
        self.root.mainloop()
