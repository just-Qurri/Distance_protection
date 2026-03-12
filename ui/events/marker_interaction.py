# ui/events/marker_interaction.py
import numpy as np
from typing import Optional, Tuple


class MarkerInteraction:
    """Обработчик взаимодействия с маркерами"""

    def __init__(self, visualizer, marker_manager):
        self.viz = visualizer
        self.markers = marker_manager
        self.captured_marker: Optional[Tuple[str, int]] = None
        self.capture_radius = 50  # пикселей

    def try_capture_marker(self, event) -> bool:
        """Попытка захватить маркер"""
        marker_info = self._find_marker_at_position(event)

        if marker_info:
            self._capture_marker(*marker_info)
            return True

        return False

    def _find_marker_at_position(self, event) -> Optional[Tuple[str, int]]:
        """Поиск маркера в позиции курсора"""
        screen_x, screen_y = event.x, event.y

        candidates = []

        # Проверяем маркеры на оси R
        for i, marker_data in enumerate(self.markers.axis_markers_r):
            line_screen_x, _ = self.viz.ax.transData.transform((marker_data['x'], 0))
            distance = abs(screen_x - line_screen_x)
            if distance < self.capture_radius:
                candidates.append((distance, ('r', i)))

        # Проверяем маркеры на оси X
        for i, marker_data in enumerate(self.markers.axis_markers_x):
            _, line_screen_y = self.viz.ax.transData.transform((0, marker_data['y']))
            distance = abs(screen_y - line_screen_y)
            if distance < self.capture_radius:
                candidates.append((distance, ('x', i)))

        # Проверяем точечные маркеры
        for i, marker_data in enumerate(self.markers.point_markers):
            point_screen_x, point_screen_y = self.viz.ax.transData.transform(
                (marker_data['x'], marker_data['y'])
            )
            distance = np.sqrt(
                (screen_x - point_screen_x) ** 2 +
                (screen_y - point_screen_y) ** 2
            )
            if distance < self.capture_radius:
                candidates.append((distance, ('point', i)))

        if candidates:
            candidates.sort(key=lambda x: x[0])
            return candidates[0][1]

        return None

    def _capture_marker(self, marker_type: str, index: int):
        """Захват маркера"""
        self.captured_marker = (marker_type, index)

        if marker_type == 'r':
            self.markers.dragging_axis_marker = ('r', index)
            self.viz.canvas.get_tk_widget().configure(cursor="sb_h_double_arrow")
        elif marker_type == 'x':
            self.markers.dragging_axis_marker = ('x', index)
            self.viz.canvas.get_tk_widget().configure(cursor="sb_v_double_arrow")
        elif marker_type == 'point':
            self.markers.dragging_point_marker = index
            self.viz.canvas.get_tk_widget().configure(cursor="fleur")