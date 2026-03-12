# ui/markers/measurement_lines.py
class MeasurementLines:
    """Основные измерительные линии"""

    def __init__(self, ax, canvas):
        self.ax = ax
        self.canvas = canvas

        self._line_position_r = 0.0
        self._line_position_x = 0.0

        # Создаем линии
        self.vertical_line = self.ax.axvline(x=0, color='red', linestyle='--',
                                             linewidth=2, alpha=0.7, picker=True)
        self.horizontal_line = self.ax.axhline(y=0, color='blue', linestyle='--',
                                               linewidth=2, alpha=0.7, picker=True)

        # Текст с измерениями
        self.measure_text = self.ax.text(0.02, 0.98, 'R = 0.00 Ω\nX = 0.00 Ω',
                                         transform=self.ax.transAxes,
                                         fontsize=10, fontweight='bold',
                                         verticalalignment='top',
                                         bbox=dict(boxstyle='round', facecolor='white',
                                                   edgecolor='#cccccc', alpha=0.9))

    @property
    def line_position_r(self):
        return self._line_position_r

    @line_position_r.setter
    def line_position_r(self, value):
        self._line_position_r = value
        self.vertical_line.set_xdata([value, value])
        self._update_text()

    @property
    def line_position_x(self):
        return self._line_position_x

    @line_position_x.setter
    def line_position_x(self, value):
        self._line_position_x = value
        self.horizontal_line.set_ydata([value, value])
        self._update_text()

    def _update_text(self):
        """Обновление текста измерений"""
        self.measure_text.set_text(f'R = {self._line_position_r:.2f} Ω\nX = {self._line_position_x:.2f} Ω')
        self.canvas.draw_idle()

    def update_position(self, r: float, x: float):
        """Обновление позиций обеих линий"""
        self._line_position_r = r
        self._line_position_x = x
        self.vertical_line.set_xdata([r, r])
        self.horizontal_line.set_ydata([x, x])
        self._update_text()