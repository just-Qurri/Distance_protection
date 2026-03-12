# ui/markers/point_markers.py
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class PointMarker:
    x: float
    y: float
    color: str
    lines: List[object]
    text: object


class PointMarkers:
    """Точечные маркеры"""

    def __init__(self, ax, canvas):
        self.ax = ax
        self.canvas = canvas
        self.markers: List[PointMarker] = []
        self.dragging_index: Optional[int] = None

    def add(self, x: float, y: float, color: str = 'green'):
        """Добавить точечный маркер"""
        line1 = self.ax.plot(x, y, 'x', color=color, markersize=12, markeredgewidth=2)[0]
        line2 = self.ax.plot(x, y, 'o', color=color, markersize=6, markerfacecolor='none')[0]

        text = self.ax.text(x, y, f'({x:.2f}, {y:.2f})', fontsize=8, color=color,
                            bbox=dict(boxstyle='round', facecolor='white', edgecolor=color, alpha=0.7))

        marker = PointMarker(x=x, y=y, color=color, lines=[line1, line2], text=text)
        self.markers.append(marker)
        self.canvas.draw_idle()
        return marker

    def handle_drag(self, event) -> bool:
        """Обработка перетаскивания"""
        if self.dragging_index is None or not event.inaxes:
            return False

        idx = self.dragging_index
        if idx < len(self.markers) and event.xdata and event.ydata:
            self._update_position(idx, event.xdata, event.ydata)
            return True
        return False

    def _update_position(self, index: int, new_x: float, new_y: float):
        """Обновление позиции маркера"""
        marker = self.markers[index]
        marker.x = new_x
        marker.y = new_y

        for line in marker.lines:
            line.set_data([new_x], [new_y])

        marker.text.set_position((new_x, new_y))
        marker.text.set_text(f'({new_x:.2f}, {new_y:.2f})')

        self.canvas.draw_idle()

    def update_positions(self):
        """Обновление позиций текста после изменения масштаба"""
        for marker in self.markers:
            marker.text.set_position((marker.x, marker.y))