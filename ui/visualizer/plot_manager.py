# ui/visualizer/plot_manager.py
import tkinter as tk
from typing import Optional, Tuple


class PlotManager:
    """Управление масштабированием и отображением графика"""

    def __init__(self, visualizer):
        self.viz = visualizer
        self.zoom_level = tk.StringVar(value="100%")
        self.initial_limits = None

    def zoom_in(self):
        """Увеличить масштаб"""
        self._zoom(0.8)

    def zoom_out(self):
        """Уменьшить масштаб"""
        self._zoom(1.25)

    def reset_to_initial_scale(self):
        """Сброс к начальному масштабу"""
        if self.initial_limits:
            xlim, ylim = self.initial_limits
            self.viz.ax.set_xlim(xlim)
            self.viz.ax.set_ylim(ylim)

            # Обновляем позиции маркеров
            if hasattr(self.viz, 'markers') and self.viz.markers:
                self.viz.markers.update_marker_positions()

            self.viz.canvas.draw_idle()
            self._update_zoom_level()

    def fit_to_view(self):
        """Подогнать под экран (автомасштабирование)"""
        if hasattr(self.viz, 'zone_renderer') and self.viz.zone_renderer.zones:
            # Находим минимальные и максимальные значения зон
            all_x = []
            all_y = []

            for zone in self.viz.zone_renderer.zones:
                # Добавляем координаты зоны
                all_x.extend([zone.x1 * 0.8, zone.x1 * 1.2])
                all_y.extend([zone.r1 * 0.8, zone.r1 * 1.2])

            if all_x and all_y:
                x_min, x_max = min(all_x), max(all_x)
                y_min, y_max = min(all_y), max(all_y)

                # Добавляем отступы
                x_padding = (x_max - x_min) * 0.1
                y_padding = (y_max - y_min) * 0.1

                self.viz.ax.set_xlim(x_min - x_padding, x_max + x_padding)
                self.viz.ax.set_ylim(y_min - y_padding, y_max + y_padding)

                # Обновляем маркеры
                if hasattr(self.viz, 'markers') and self.viz.markers:
                    self.viz.markers.update_marker_positions()

                self.viz.canvas.draw_idle()
                self._update_zoom_level()

    def _zoom(self, factor: float):
        """Внутренний метод масштабирования"""
        xlim = self.viz.ax.get_xlim()
        ylim = self.viz.ax.get_ylim()

        x_center = (xlim[0] + xlim[1]) / 2
        y_center = (ylim[0] + ylim[1]) / 2

        new_xlim = (
            x_center - (x_center - xlim[0]) * factor,
            x_center + (xlim[1] - x_center) * factor
        )
        new_ylim = (
            y_center - (y_center - ylim[0]) * factor,
            y_center + (ylim[1] - y_center) * factor
        )

        self.viz.ax.set_xlim(new_xlim)
        self.viz.ax.set_ylim(new_ylim)

        # Обновляем позиции маркеров
        if hasattr(self.viz, 'markers') and self.viz.markers:
            self.viz.markers.update_marker_positions()

        self.viz.canvas.draw_idle()
        self._update_zoom_level()

    def _update_zoom_level(self):
        """Обновление отображения уровня зума"""
        xlim = self.viz.ax.get_xlim()
        x_range = xlim[1] - xlim[0]

        # Вычисляем процент относительно начального масштаба
        if self.initial_limits:
            initial_range = self.initial_limits[0][1] - self.initial_limits[0][0]
            if initial_range > 0:
                percent = (initial_range / x_range) * 100
                self.zoom_level.set(f"{percent:.0f}%")

    def set_initial_limits(self, xlim: Tuple[float, float], ylim: Tuple[float, float]):
        """Установка начальных границ"""
        self.initial_limits = (xlim, ylim)
        self._update_zoom_level()