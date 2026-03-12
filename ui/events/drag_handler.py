# ui/events/drag_handler.py
from typing import Optional, Tuple


class DragHandler:
    """Обработчик перетаскивания графика"""

    def __init__(self, visualizer):
        self.viz = visualizer
        self.drag_start: Optional[Tuple[int, int]] = None
        self.drag_start_xlim: Optional[Tuple[float, float]] = None
        self.drag_start_ylim: Optional[Tuple[float, float]] = None
        self.is_dragging = False

    def start_drag(self, event):
        """Начало перетаскивания"""
        if event.button == 1:
            self.drag_start = (event.x, event.y)
            self.drag_start_xlim = self.viz.ax.get_xlim()
            self.drag_start_ylim = self.viz.ax.get_ylim()
            self.is_dragging = True
            self.viz.canvas.get_tk_widget().configure(cursor="fleur")

    def on_mouse_motion(self, event) -> bool:
        """Обработка движения при перетаскивании"""
        if not self.is_dragging or not event.inaxes or event.button != 1:
            return False

        if not self.drag_start or event.x is None or event.y is None:
            return False

        x0, y0 = self.drag_start
        x1, y1 = event.x, event.y

        bbox = self.viz.ax.get_window_extent()
        if bbox.width <= 0 or bbox.height <= 0:
            return False

        # Вычисляем смещение
        dx_data = (x0 - x1) * (self.drag_start_xlim[1] - self.drag_start_xlim[0]) / bbox.width
        dy_data = (y0 - y1) * (self.drag_start_ylim[1] - self.drag_start_ylim[0]) / bbox.height

        # Применяем новое смещение
        self.viz.ax.set_xlim(
            self.drag_start_xlim[0] + dx_data,
            self.drag_start_xlim[1] + dx_data
        )
        self.viz.ax.set_ylim(
            self.drag_start_ylim[0] + dy_data,
            self.drag_start_ylim[1] + dy_data
        )

        return True

    def on_mouse_release(self, event) -> bool:
        """Обработка отпускания"""
        if self.is_dragging:
            self.drag_start = None
            self.drag_start_xlim = None
            self.drag_start_ylim = None
            self.is_dragging = False
            self.viz.canvas.get_tk_widget().configure(cursor="arrow")
            return True
        return False