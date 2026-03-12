# ui/events/zoom_handler.py
from typing import Tuple


class ZoomHandler:
    """Обработчик масштабирования колесиком"""

    def __init__(self, visualizer):
        self.viz = visualizer
        self.scale_factor = 0.9  # для уменьшения, для увеличения 1/0.9 ≈ 1.11

    def on_scroll(self, event):
        """Масштабирование колесиком"""
        if not event.inaxes:
            return

        factor = self.scale_factor if event.button == 'up' else 1.0 / self.scale_factor

        # Получаем текущие границы
        xlim = self.viz.ax.get_xlim()
        ylim = self.viz.ax.get_ylim()

        # Центр масштабирования
        x_center = event.xdata if event.xdata else (xlim[0] + xlim[1]) / 2
        y_center = event.ydata if event.ydata else (ylim[0] + ylim[1]) / 2

        # Вычисляем новые границы
        new_xlim = self._calculate_zoomed_limits(xlim, x_center, factor)
        new_ylim = self._calculate_zoomed_limits(ylim, y_center, factor)

        # Применяем
        self.viz.ax.set_xlim(new_xlim)
        self.viz.ax.set_ylim(new_ylim)

        # Обновляем уровень зума
        self._update_zoom_level()

    def _calculate_zoomed_limits(self, limits: Tuple[float, float],
                                 center: float,
                                 factor: float) -> Tuple[float, float]:
        """Вычисление новых границ после масштабирования"""
        return (
            center - (center - limits[0]) * factor,
            center + (limits[1] - center) * factor
        )

    def _update_zoom_level(self):
        """Обновление отображения уровня зума"""
        if hasattr(self.viz, '_update_zoom_level'):
            self.viz._update_zoom_level()