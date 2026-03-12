# ui/visualizer/main_window.py
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from ui.visualizer.plot_manager import PlotManager
from ui.visualizer.zone_renderer import ZoneRenderer
from ui.visualizer.fault_renderer import FaultRenderer
from ui.top_panel import TopPanel
from ui.markers.marker_manager import MarkerManager
from ui.events.event_handler import EventHandler


class REL670Visualizer:
    """Главное окно визуализатора"""

    def __init__(self, title):
        self.title = title
        self.root = None
        self.figure = None
        self.ax = None
        self.canvas = None

        # Переменные состояния (будут созданы после создания root)
        self.fault_type = None
        self.zoom_level = None

        # Компоненты
        self.plot_manager = None
        self.zone_renderer = None
        self.fault_renderer = None
        self.markers = None
        self.events = None
        self.top_panel = None

        self._init_window(title)

    def _init_window(self, title):
        """Инициализация главного окна"""
        # Сначала создаем root
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry("1400x800")

        # Теперь можно создавать StringVar
        self.fault_type = tk.StringVar(value="phph")
        self.zoom_level = tk.StringVar(value="100%")

        # Создаем график
        self.figure, self.ax = plt.subplots(figsize=(10, 8))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)

        # Инициализируем компоненты
        self._init_components()

        # Создаем интерфейс
        self._create_ui()

    def _init_components(self):
        """Инициализация всех компонентов"""
        from ui.visualizer.plot_manager import PlotManager
        self.plot_manager = PlotManager(self)

        from ui.visualizer.zone_renderer import ZoneRenderer
        self.zone_renderer = ZoneRenderer(self)

        from ui.visualizer.fault_renderer import FaultRenderer
        self.fault_renderer = FaultRenderer(self)

        from ui.markers.marker_manager import MarkerManager
        self.markers = MarkerManager(self.ax, self.canvas, self)

        from ui.events.event_handler import EventHandler
        self.events = EventHandler(self, self.markers)

        # Сохраняем начальные пределы
        self.plot_manager.set_initial_limits(self.ax.get_xlim(), self.ax.get_ylim())

    def _create_ui(self):
        """Создание пользовательского интерфейса"""
        # Главный контейнер
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Верхняя панель
        from ui.top_panel import TopPanel
        self.top_panel = TopPanel(main_container, self)
        self.top_panel.pack(fill=tk.X, padx=5, pady=5)

        # Контейнер для графика
        plot_frame = ttk.Frame(main_container)
        plot_frame.pack(fill=tk.BOTH, expand=True)

        # Размещаем canvas
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Привязываем события
        self._bind_events()

        # Настраиваем оси
        self._setup_axes()

    def _setup_axes(self):
        """Настройка осей графика"""
        self.ax.set_xlabel('X (Реактанс), Ом')
        self.ax.set_ylabel('R (Сопротивление), Ом')
        self.ax.grid(True, alpha=0.3)
        self.ax.axhline(y=0, color='k', linewidth=0.5)
        self.ax.axvline(x=0, color='k', linewidth=0.5)
        self.ax.set_aspect('equal')

    def _bind_events(self):
        """Привязка событий"""
        self.canvas.mpl_connect('button_press_event', self.events.on_mouse_press)
        self.canvas.mpl_connect('button_release_event', self.events.on_mouse_release)
        self.canvas.mpl_connect('motion_notify_event', self.events.on_mouse_motion)
        self.canvas.mpl_connect('scroll_event', self.events.on_scroll)
        self.canvas.mpl_connect('pick_event', self.events.on_pick_event)

    def show(self):
        """Запуск главного цикла"""
        self.plot_characteristics()
        self.root.mainloop()

    def plot_characteristics(self, keep_limits=False):
        """Отрисовка характеристик"""
        self.zone_renderer.render_zones()
        self.fault_renderer.render_fault(self.fault_type.get())
        self.canvas.draw_idle()

    def _update_zoom_level(self):
        """Обновление уровня зума"""
        if self.plot_manager:
            self.plot_manager._update_zoom_level()

    def _show_notification(self, message: str):
        """Показать уведомление"""
        # Здесь можно добавить отображение уведомлений
        print(f"NOTIFICATION: {message}")

    # ========== Методы для работы с зонами ==========

    def add_zone(self, zone):
        """
        Добавление зоны защиты

        Args:
            zone: объект ZoneSettings с параметрами зоны
        """
        if self.zone_renderer:
            self.zone_renderer.add_zone(zone)
            # Перерисовываем после добавления
            self.plot_characteristics(keep_limits=True)
        else:
            print("Предупреждение: zone_renderer не инициализирован")

    def add_zones(self, zones):
        """
        Добавление нескольких зон

        Args:
            zones: список объектов ZoneSettings
        """
        for zone in zones:
            self.add_zone(zone)

    def clear_zones(self):
        """Очистка всех зон"""
        if self.zone_renderer:
            self.zone_renderer.zones.clear()
            self.plot_characteristics(keep_limits=True)