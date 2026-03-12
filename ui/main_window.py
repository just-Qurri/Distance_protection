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
from models.selector_settings import SelectorSettings
from ui.top_panel import TopPanel
from ui.plot_area import PlotArea
from ui.zone_tab import ZoneTab
from ui.selector_tab import SelectorTab
from ui.markers import MarkerManager
from ui.events import EventHandler
from ui.constants import COLORS, LINESTYLES, FAULT_TYPES
from ui.visualizer.plot_manager import PlotManager

class REL670Visualizer:
    """Главный класс визуализатора REL670"""

    FAULT_TYPES = FAULT_TYPES

    def __init__(self, title="REL670 - Дистанционная защита"):
        self.title = title
        self.zones: List[ZoneSettings] = []
        self.root = None
        self.figure = None
        self.ax = None
        self.canvas = None
        self.plot_manager = None
        self.zone_vars = {}
        self.selector = None
        self.status_bar = None
        self.zoom_level = None
        self.fault_type = None

        # Менеджеры
        self.markers = None
        self.events = None

        # Для отложенного обновления
        self.update_job = None

        # Компоненты UI
        self.top_panel = None
        self.zone_tabs = []
        self.selector_tab = None

        # Контекстное меню
        self.context_menu = None
        self.context_menu_marker = None
        self.context_x = None
        self.context_y = None

    def add_zone(self, zone: ZoneSettings):
        """Добавление зоны"""
        zone.zone_id = len(self.zones) + 1
        if zone.zone_id <= len(COLORS):
            zone.color = COLORS[zone.zone_id - 1][0]
            zone.color_name = COLORS[zone.zone_id - 1][1]
        self.zones.append(zone)

    def calculate_optimal_bounds(self):
        """Расчет оптимальных границ графика"""
        all_min_r = float('inf')
        all_max_r = float('-inf')
        all_min_x = float('inf')
        all_max_x = float('-inf')

        visible_zones = [z for z in self.zones if z.enabled]
        fault_type = self.fault_type.get() if self.fault_type else "phph"

        for zone in visible_zones:
            min_r, max_r, min_x, max_x = zone.get_zone_bounds(fault_type)
            all_min_r = min(all_min_r, min_r)
            all_max_r = max(all_max_r, max_r)
            all_min_x = min(all_min_x, min_x)
            all_max_x = max(all_max_x, max_x)

        if hasattr(self, 'selector') and self.selector.enabled and fault_type == "selector":
            points = self.selector.get_polygon_points()
            for r, x in points:
                all_min_r = min(all_min_r, r)
                all_max_r = max(all_max_r, r)
                all_min_x = min(all_min_x, x)
                all_max_x = max(all_max_x, x)

        if all_min_r == float('inf'):
            return (-5, 10), (-5, 8)

        r_range = all_max_r - all_min_r
        x_range = all_max_x - all_min_x

        r_margin = max(r_range * 0.2, 1.0)
        x_margin = max(x_range * 0.2, 1.0)

        xlim = (all_min_r - r_margin, all_max_r + r_margin)
        ylim = (all_min_x - x_margin, all_max_x + x_margin)

        # Квадратное поле
        x_range = xlim[1] - xlim[0]
        y_range = ylim[1] - ylim[0]
        max_range = max(x_range, y_range)

        x_center = (xlim[0] + xlim[1]) / 2
        y_center = (ylim[0] + ylim[1]) / 2

        xlim = (x_center - max_range / 2, x_center + max_range / 2)
        ylim = (y_center - max_range / 2, y_center + max_range / 2)

        return xlim, ylim

    def create_window(self):
        """Создание главного окна"""
        self.root = tk.Tk()
        self.root.title(self.title)
        self.root.state('zoomed')

        self.zoom_level = tk.StringVar(value="100%")
        self.fault_type = tk.StringVar(value="phph")

        self._configure_styles()
        self.fault_type.trace('w', lambda *args: self.on_fault_type_change())

        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)


        self.plot_manager = PlotManager(self)

        self.top_panel = TopPanel(main_container, self)

        self.top_panel = TopPanel(main_container, self)
        self.top_panel.pack()

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

    def _create_plot_area(self, parent):
        """Создание области графика"""
        self.figure = plt.Figure(figsize=(8, 8), dpi=100,
                                 facecolor='white', edgecolor='#dddddd')
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('#fafafa')

        self.canvas = FigureCanvasTkAgg(self.figure, master=parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Создаем менеджеры
        self.markers = MarkerManager(self.ax, self.canvas, self)
        self.events = EventHandler(self, self.markers)

        # Привязка событий
        self.canvas.mpl_connect('scroll_event', self.events.on_scroll)
        self.canvas.mpl_connect('button_press_event', self.events.on_mouse_press)
        self.canvas.mpl_connect('button_release_event', self.events.on_mouse_release)
        self.canvas.mpl_connect('motion_notify_event', self.events.on_mouse_motion)
        self.canvas.mpl_connect('pick_event', self.events.on_pick_event)

        self.canvas.get_tk_widget().bind('<Button-3>', self.events.show_context_menu)
        self.canvas.get_tk_widget().configure(cursor="arrow")

        self.ax.set_aspect('equal', adjustable='box')
        self.canvas.draw()

    def _create_context_menu(self):
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

    def _add_marker_r_from_menu(self):
        """Добавление маркера на ось R"""
        if self.context_x is not None and self.markers:
            self.markers.add_axis_marker_r(self.context_x)
            self.canvas.draw_idle()
            self._show_notification(f"Маркер на оси R: {self.context_x:.2f}")

    def _add_marker_x_from_menu(self):
        """Добавление маркера на ось X"""
        if self.context_y is not None and self.markers:
            self.markers.add_axis_marker_x(self.context_y)
            self.canvas.draw_idle()
            self._show_notification(f"Маркер на оси X: {self.context_y:.2f}")

    def _delete_selected_marker(self):
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

    def clear_all_markers(self):
        """Очистка всех маркеров"""
        if self.markers:
            self.markers.clear_all_markers()
            self.canvas.draw_idle()
            self._update_status()
            self._show_notification("Все маркеры удалены")
        else:
            self._show_notification("Нет маркеров для удаления")

    def reset_measurement_lines(self):
        """Сброс измерительных линий"""
        if self.markers:
            self.markers.reset_measurement_lines()
            self.canvas.draw_idle()
            self._show_notification("Основные линии сброшены в (0, 0)")

    def _configure_styles(self):
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

    def _create_control_panel(self, parent):
        """Создание панели управления"""
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)

        for zone in self.zones:
            tab = ZoneTab(notebook, zone, self, COLORS, LINESTYLES)
            self.zone_tabs.append(tab)

        self.selector = SelectorSettings()
        from ui.selector_tab import SelectorTab
        self.selector_tab = SelectorTab(notebook, self.selector, self, COLORS, LINESTYLES)

    def _create_status_bar(self, parent):
        """Создание строки статуса"""
        self.status_bar = ttk.Frame(parent)
        self.status_bar.pack(fill=tk.X, pady=(10, 0))

        status_left = ttk.Frame(self.status_bar)
        status_left.pack(side=tk.LEFT)

        instructions = [
            "🖱️ ЛКМ - перетаскивание",
            "|",
            "🖱️ Колесо - масштаб",
            "|",
            "Ctrl+ЛКМ - точечный маркер",
            "|",
            "ПКМ - меню маркеров"
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
        self._update_status()

    # ============= МЕТОДЫ УПРАВЛЕНИЯ =============



    def reset_to_initial_scale(self):
        self.reset_scale()

    def fit_to_view(self):
        self.reset_scale()

    def reset_scale(self):
        xlim, ylim = self.calculate_optimal_bounds()
        self.ax.set_xlim(xlim)
        self.ax.set_ylim(ylim)

        if self.markers:
            self.markers.update_text_positions()

        self.canvas.draw_idle()
        self._update_zoom_level()
        self._show_notification("Масштаб оптимизирован")

    def on_fault_type_change(self):
        self.top_panel.update_fault_type_label()
        self.plot_characteristics(keep_limits=False)
        self._update_status()

    def deferred_update(self):
        self.plot_characteristics(keep_limits=True)
        self.update_job = None

    def plot_characteristics(self, keep_limits=True):
        """Построение характеристик"""
        if self.ax is None:
            return

        # Сохраняем состояние маркеров перед очисткой
        if self.markers:
            self.markers.save_state()
            line_pos_r = self.markers.line_position_r
            line_pos_x = self.markers.line_position_x
        else:
            line_pos_r = 0.0
            line_pos_x = 0.0

        # Очищаем оси
        self.ax.clear()

        # Построение зон и селектора
        fault_type = self.fault_type.get()
        fault_type_name = dict(self.FAULT_TYPES).get(fault_type, "")

        if fault_type == "selector":
            if hasattr(self, 'selector') and self.selector.enabled:
                self._plot_selector()
        else:
            for zone in self.zones:
                if not zone.enabled:
                    continue
                points = zone.get_polygon_points(fault_type)
                if points:
                    from matplotlib.patches import Polygon
                    points_array = np.array(points)
                    direction_symbol = {"forward": "↑", "reverse": "↓", "non-directional": "↕"}.get(zone.direction_mode,
                                                                                                    "")
                    poly = Polygon(points_array, closed=True, fill=None,
                                   edgecolor=zone.color, linestyle=zone.linestyle,
                                   linewidth=2.5, alpha=zone.opacity,
                                   label=f"Зона {zone.zone_id} {direction_symbol}")
                    self.ax.add_patch(poly)

        # Создаем новый менеджер маркеров (синглтон восстановит состояние)
        self.markers = MarkerManager(self.ax, self.canvas, self)

        # Восстанавливаем позиции основных линий
        self.markers.line_position_r = line_pos_r
        self.markers.line_position_x = line_pos_x
        self.markers.vertical_line.set_xdata([line_pos_r, line_pos_r])
        self.markers.horizontal_line.set_ydata([line_pos_x, line_pos_x])
        self.markers._update_measurement_text()

        # Настройка графика
        self.ax.set_xlabel('R (Ом) - Активное сопротивление', fontsize=11, fontweight='bold')
        self.ax.set_ylabel('X (Ом) - Реактивное сопротивление', fontsize=11, fontweight='bold')
        self.ax.set_title(f"{self.title} | {fault_type_name}", fontsize=14, fontweight='bold', pad=15, color='#2196F3')

        # Сетка
        self.ax.grid(True, alpha=0.7, linestyle='-', color='#AAAAAA', linewidth=0.8)
        self.ax.grid(True, which='minor', alpha=0.3, linestyle=':', color='#666666', linewidth=0.5)
        self.ax.minorticks_on()

        # Оси
        self.ax.axhline(y=0, color='#333333', linewidth=2, alpha=0.9)
        self.ax.axvline(x=0, color='#333333', linewidth=2, alpha=0.9)
        self.ax.set_facecolor('#fafafa')
        self.ax.set_aspect('equal', adjustable='box')

        # Масштаб
        xlim, ylim = self.calculate_optimal_bounds()
        self.ax.set_xlim(xlim)
        self.ax.set_ylim(ylim)

        # Легенда
        handles, labels = self.ax.get_legend_handles_labels()
        if handles:
            self.ax.legend(loc='upper right', fontsize=9, framealpha=0.9,
                           facecolor='white', edgecolor='#CCCCCC')

        self.canvas.draw_idle()
        self._update_zoom_level()

    def _plot_selector(self):
        """Построение фазового селектора"""
        if not hasattr(self, 'selector') or not self.selector.enabled:
            return

        points = self.selector.get_polygon_points()
        if len(points) < 3:
            return

        from matplotlib.patches import Polygon
        points_array = np.array(points)
        poly = Polygon(points_array, closed=True, fill=None,
                       edgecolor=self.selector.color, linestyle=self.selector.linestyle,
                       linewidth=3.0, alpha=self.selector.opacity,
                       label="Фазовый селектор")
        self.ax.add_patch(poly)

    def _update_zoom_level(self):
        if self.zoom_level and self.ax:
            xlim, ylim = self.calculate_optimal_bounds()
            current_xlim = self.ax.get_xlim()
            zoom_x = (xlim[1] - xlim[0]) / (current_xlim[1] - current_xlim[0])
            self.zoom_level.set(f"{zoom_x * 100:.0f}%")

    def _update_status(self):
        if not hasattr(self, 'status_bar'):
            return

        visible_zones = sum(1 for z in self.zones if z.enabled)
        fault_type_name = dict(self.FAULT_TYPES).get(self.fault_type.get(), "")
        stats = self.markers.get_stats() if self.markers else {'point': 0, 'r': 0, 'x': 0}

        info_text = (f"Зон: {visible_zones}/{len(self.zones)}  |  "
                     f"Маркеры: ●{stats['point']}  |  "
                     f"R↓{stats['r']}  |  "
                     f"X→{stats['x']}  |  "
                     f"Тип: {fault_type_name}")

        if hasattr(self, 'status_label'):
            self.status_label.config(text=info_text)
        else:
            self.status_label = ttk.Label(self.status_bar, text=info_text,
                                          font=('Segoe UI', 9), foreground='#666666')
            self.status_label.pack(side=tk.RIGHT)

    def enable_all_zones(self):
        for zone in self.zones:
            zone.enabled = True
            if zone.zone_id in self.zone_vars:
                self.zone_vars[zone.zone_id]["enabled"].set(True)
        self.plot_characteristics(keep_limits=False)
        self._update_status()

    def disable_all_zones(self):
        for zone in self.zones:
            zone.enabled = False
            if zone.zone_id in self.zone_vars:
                self.zone_vars[zone.zone_id]["enabled"].set(False)
        self.plot_characteristics(keep_limits=False)
        self._update_status()

    def save_as_png(self):
        from tkinter import filedialog
        from datetime import datetime
        default_name = f"rel670_{self.fault_type.get()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filename = filedialog.asksaveasfilename(defaultextension=".png", initialfile=default_name,
                                                filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
        if filename:
            self.figure.savefig(filename, dpi=300, bbox_inches='tight',
                                facecolor='white', edgecolor='none')
            self._show_notification(f"Сохранено: {filename}")

    def _show_notification(self, message):
        if not self.root:
            return
        notification = tk.Toplevel(self.root)
        notification.overrideredirect(True)
        notification.geometry("+{}+{}".format(
            self.root.winfo_rootx() + self.root.winfo_width() - 300,
            self.root.winfo_rooty() + 50))
        frame = tk.Frame(notification, bg='#333333', padx=20, pady=10, relief='flat')
        frame.pack()
        tk.Label(frame, text=message, bg='#333333', fg='white', font=('Segoe UI', 10)).pack()
        self.root.after(2000, notification.destroy)

    def show(self):
        if self.root is None:
            self.create_window()
            self.plot_characteristics(keep_limits=False)
        self.root.mainloop()