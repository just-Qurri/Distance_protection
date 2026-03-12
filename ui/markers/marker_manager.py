# ui/markers/marker_manager.py
from typing import Optional, List, Dict, Any, Tuple
from ui.markers.axis_markers import AxisRMarkers, AxisXMarkers
from ui.markers.point_markers import PointMarkers
from ui.markers.measurement_lines import MeasurementLines


class MarkerState:
    """Состояние маркеров для сохранения"""

    def __init__(self):
        self.axis_markers_r = []
        self.axis_markers_x = []
        self.point_markers = []
        self.line_position_r = 0.0
        self.line_position_x = 0.0


class MarkerManager:
    """Менеджер для управления всеми маркерами"""

    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, ax=None, canvas=None, visualizer=None):
        if MarkerManager._initialized:
            return

        self.ax = ax
        self.canvas = canvas
        self.viz = visualizer

        # Состояние
        self._state = MarkerState()

        # Инициализируем компоненты
        self.axis_r = AxisRMarkers(ax, canvas)
        self.axis_x = AxisXMarkers(ax, canvas)
        self.points = PointMarkers(ax, canvas)
        self.measurement = MeasurementLines(ax, canvas)

        # Состояние перетаскивания
        self.dragging_axis_marker = None
        self.dragging_point_marker = None

        MarkerManager._initialized = True

    def add_axis_marker_r(self, x: float):
        """Добавление маркера на ось R"""
        return self.axis_r.add(x)

    def add_axis_marker_x(self, y: float):
        """Добавление маркера на ось X"""
        return self.axis_x.add(y)

    def add_point_marker(self, x: float, y: float, color: str = 'green'):
        """Добавление точечного маркера"""
        return self.points.add(x, y, color)

    def handle_mouse_motion(self, event) -> bool:
        """Обработка движения мыши"""
        if self.axis_r.handle_drag(event):
            return True
        if self.axis_x.handle_drag(event):
            return True
        if self.points.handle_drag(event):
            return True
        return False

    def handle_mouse_release(self, event) -> bool:
        """Обработка отпускания мыши"""
        released = False
        if self.dragging_axis_marker:
            self.dragging_axis_marker = None
            released = True
        if self.dragging_point_marker is not None:
            self.dragging_point_marker = None
            released = True

        if released and self.canvas:
            self.canvas.get_tk_widget().configure(cursor="arrow")
            self.canvas.draw_idle()
        return released

    def handle_pick_event(self, event) -> bool:
        """Обработка выбора объекта"""
        # Здесь логика pick событий
        return False

    def update_marker_positions(self):
        """Обновление позиций маркеров после изменения масштаба"""
        self.axis_r.update_positions()
        self.axis_x.update_positions()
        self.points.update_positions()

    def find_marker_at_position(self, x: float, y: float, tolerance: float = 2.0):
        """Поиск маркера по координатам"""
        # Поиск в маркерах на осях
        for i, marker in enumerate(self.axis_r.markers):
            if abs(marker.x - x) < tolerance:
                return ('r', i)

        for i, marker in enumerate(self.axis_x.markers):
            if abs(marker.y - y) < tolerance:
                return ('x', i)

        # Поиск в точечных маркерах
        for i, marker in enumerate(self.points.markers):
            if abs(marker.x - x) < tolerance and abs(marker.y - y) < tolerance:
                return ('point', i)

        return None

    def save_state(self):
        """Сохранение состояния"""
        self._state.axis_markers_r = [{'x': m.x} for m in self.axis_r.markers]
        self._state.axis_markers_x = [{'y': m.y} for m in self.axis_x.markers]
        self._state.point_markers = [{'x': m.x, 'y': m.y, 'color': m.color} for m in self.points.markers]
        self._state.line_position_r = self.measurement.line_position_r
        self._state.line_position_x = self.measurement.line_position_x

    @property
    def axis_markers_r(self):
        return [{'x': m.x} for m in self.axis_r.markers]

    @property
    def axis_markers_x(self):
        return [{'y': m.y} for m in self.axis_x.markers]

    @property
    def point_markers(self):
        return [{'x': m.x, 'y': m.y, 'color': m.color} for m in self.points.markers]

    @property
    def vertical_line(self):
        return self.measurement.vertical_line

    @property
    def horizontal_line(self):
        return self.measurement.horizontal_line

    @property
    def measure_text(self):
        return self.measurement.measure_text

    @property
    def line_position_r(self):
        return self.measurement.line_position_r

    @line_position_r.setter
    def line_position_r(self, value):
        self.measurement.line_position_r = value

    @property
    def line_position_x(self):
        return self.measurement.line_position_x

    @line_position_x.setter
    def line_position_x(self, value):
        self.measurement.line_position_x = value