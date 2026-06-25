# -*- coding: utf-8 -*-
"""
Модуль для управления интерактивными маркерами на графике
"""


class MarkerState:
    def __init__(self):
        self.axis_markers_r = []
        self.axis_markers_x = []
        self.point_markers = []
        self.line_position_r = 0.0
        self.line_position_x = 0.0


class MarkerManager:
    _instance = None
    _state = MarkerState()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, ax=None, canvas=None, visualizer=None):
        if hasattr(self, 'initialized') and self.initialized:
            if ax is not None:
                self.ax = ax
            if canvas is not None:
                self.canvas = canvas
            if visualizer is not None:
                self.viz = visualizer
            return

        self.ax = ax
        self.canvas = canvas
        self.viz = visualizer
        self.line_position_r = self._state.line_position_r
        self.line_position_x = self._state.line_position_x
        self.axis_markers_r = []
        self.axis_markers_x = []
        self.point_markers = []
        self.dragging_line = None
        self.dragging_axis_marker = None
        self.dragging_point_marker = None

        self._create_measurement_lines()
        self._restore_from_state()
        self.initialized = True

    def _create_measurement_lines(self):
        self.vertical_line = self.ax.axvline(x=0, color='red', linestyle='--',
                                             linewidth=2, alpha=0.7, picker=True, pickradius=10)
        self.horizontal_line = self.ax.axhline(y=0, color='blue', linestyle='--',
                                               linewidth=2, alpha=0.7, picker=True, pickradius=10)
        self.measure_text = self.ax.text(0.02, 0.98, 'R = 0.00 Ω\nX = 0.00 Ω',
                                         transform=self.ax.transAxes,
                                         fontsize=10, fontweight='bold',
                                         verticalalignment='top',
                                         bbox=dict(boxstyle='round', facecolor='white',
                                                   edgecolor='#cccccc', alpha=0.9),
                                         picker=True)
        self.measure_text.set_picker(10)
        self.vertical_line.set_xdata([self.line_position_r, self.line_position_r])
        self.horizontal_line.set_ydata([self.line_position_x, self.line_position_x])
        self._update_measurement_text()

    def _restore_from_state(self):
        for marker_data in self._state.axis_markers_r:
            self.add_axis_marker_r(marker_data['x'])
        for marker_data in self._state.axis_markers_x:
            self.add_axis_marker_x(marker_data['y'])
        for marker_data in self._state.point_markers:
            self.add_point_marker(marker_data['x'], marker_data['y'], marker_data['color'])

    def save_state(self):
        self._state.axis_markers_r = [{'x': m['x']} for m in self.axis_markers_r]
        self._state.axis_markers_x = [{'y': m['y']} for m in self.axis_markers_x]
        self._state.point_markers = [{'x': m['x'], 'y': m['y'], 'color': m['color']} for m in self.point_markers]
        self._state.line_position_r = self.line_position_r
        self._state.line_position_x = self.line_position_x

    def add_axis_marker_r(self, x):
        line = self.ax.axvline(x=x, color='orange', linestyle='-',
                               linewidth=2, alpha=0.8, picker=True, pickradius=10)
        y_top = self.ax.get_ylim()[1] * 0.95
        text = self.ax.text(x, y_top, f' {x:.2f}',
                            rotation=90, verticalalignment='top',
                            fontsize=8, color='orange', fontweight='bold',
                            bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7),
                            picker=True)
        text.set_picker(10)
        self.axis_markers_r.append({'line': line, 'text': text, 'x': x, 'type': 'r'})
        self.save_state()
        self.canvas.draw_idle()
        return line, text

    def add_axis_marker_x(self, y):
        line = self.ax.axhline(y=y, color='purple', linestyle='-',
                               linewidth=2, alpha=0.8, picker=True, pickradius=10)
        x_right = self.ax.get_xlim()[1] * 0.95
        text = self.ax.text(x_right, y, f'{y:.2f} ',
                            horizontalalignment='right', verticalalignment='center',
                            fontsize=8, color='purple', fontweight='bold',
                            bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7),
                            picker=True)
        text.set_picker(10)
        self.axis_markers_x.append({'line': line, 'text': text, 'y': y, 'type': 'x'})
        self.save_state()
        self.canvas.draw_idle()
        return line, text

    def add_point_marker(self, x, y, color='green'):
        if x is None or y is None:
            return None
        marker_line1 = self.ax.plot(x, y, 'x', color=color, markersize=12,
                                    markeredgewidth=2, picker=True, pickradius=10)[0]
        marker_line2 = self.ax.plot(x, y, 'o', color=color, markersize=6,
                                    markerfacecolor='none', markeredgewidth=1,
                                    picker=True, pickradius=10)[0]
        text = self.ax.text(x, y, f'({x:.2f}, {y:.2f})',
                            fontsize=8, color=color,
                            bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                                      edgecolor=color, alpha=0.7),
                            picker=True)
        text.set_picker(10)
        marker = {'lines': [marker_line1, marker_line2], 'text': text,
                  'x': x, 'y': y, 'color': color, 'type': 'point'}
        self.point_markers.append(marker)
        self.save_state()
        return marker

    def find_marker_at_position(self, x, y, tolerance=2.0):
        for i, marker in enumerate(self.axis_markers_r):
            if abs(marker['x'] - x) < tolerance:
                return ('r', i)
        for i, marker in enumerate(self.axis_markers_x):
            if abs(marker['y'] - y) < tolerance:
                return ('x', i)
        for i, marker in enumerate(self.point_markers):
            if abs(marker['x'] - x) < tolerance and abs(marker['y'] - y) < tolerance:
                return ('point', i)
        return None

    def delete_marker(self, marker_type, index):
        try:
            if marker_type == 'point' and index < len(self.point_markers):
                marker = self.point_markers[index]
                for line in marker['lines']:
                    if line in self.ax.lines:
                        line.remove()
                if marker['text'] in self.ax.texts:
                    marker['text'].remove()
                del self.point_markers[index]
                return True
            elif marker_type == 'r' and index < len(self.axis_markers_r):
                marker = self.axis_markers_r[index]
                if marker['line'] in self.ax.lines:
                    marker['line'].remove()
                if marker['text'] in self.ax.texts:
                    marker['text'].remove()
                del self.axis_markers_r[index]
                return True
            elif marker_type == 'x' and index < len(self.axis_markers_x):
                marker = self.axis_markers_x[index]
                if marker['line'] in self.ax.lines:
                    marker['line'].remove()
                if marker['text'] in self.ax.texts:
                    marker['text'].remove()
                del self.axis_markers_x[index]
                return True
        except Exception:
            return False
        return False

    def clear_all_markers(self):
        for marker in self.point_markers:
            for line in marker['lines']:
                if line in self.ax.lines:
                    line.remove()
            if marker['text'] in self.ax.texts:
                marker['text'].remove()
        self.point_markers = []

        for marker in self.axis_markers_r:
            if marker['line'] in self.ax.lines:
                marker['line'].remove()
            if marker['text'] in self.ax.texts:
                marker['text'].remove()
        self.axis_markers_r = []

        for marker in self.axis_markers_x:
            if marker['line'] in self.ax.lines:
                marker['line'].remove()
            if marker['text'] in self.ax.texts:
                marker['text'].remove()
        self.axis_markers_x = []

    def reset_measurement_lines(self):
        self.line_position_r = 0.0
        self.line_position_x = 0.0
        self.vertical_line.set_xdata([0, 0])
        self.horizontal_line.set_ydata([0, 0])
        self._update_measurement_text()

    def _update_measurement_text(self):
        if self.measure_text:
            self.measure_text.set_text(f'R = {self.line_position_r:.2f} Ω\nX = {self.line_position_x:.2f} Ω')

    def update_measurement_text(self):
        self._update_measurement_text()

    def handle_pick_event(self, event):
        if not hasattr(event, 'artist'):
            return False
        artist = event.artist

        if artist is self.vertical_line or artist is self.measure_text:
            self.dragging_line = 'v'
            self.canvas.get_tk_widget().configure(cursor="sb_h_double_arrow")
            return True
        if artist is self.horizontal_line:
            self.dragging_line = 'h'
            self.canvas.get_tk_widget().configure(cursor="sb_v_double_arrow")
            return True

        for i, marker in enumerate(self.axis_markers_r):
            if artist is marker['line'] or artist is marker['text']:
                self.dragging_axis_marker = ('r', i)
                self.canvas.get_tk_widget().configure(cursor="sb_h_double_arrow")
                return True

        for i, marker in enumerate(self.axis_markers_x):
            if artist is marker['line'] or artist is marker['text']:
                self.dragging_axis_marker = ('x', i)
                self.canvas.get_tk_widget().configure(cursor="sb_v_double_arrow")
                return True

        for i, marker in enumerate(self.point_markers):
            for line in marker['lines']:
                if artist is line:
                    self.dragging_point_marker = i
                    self.canvas.get_tk_widget().configure(cursor="fleur")
                    return True
            if artist is marker['text']:
                self.dragging_point_marker = i
                self.canvas.get_tk_widget().configure(cursor="fleur")
                return True

        return False

    def handle_mouse_motion(self, event):
        if not event.inaxes:
            return False

        if self.dragging_line == 'v' and event.xdata is not None:
            self.vertical_line.set_xdata([event.xdata, event.xdata])
            self.line_position_r = event.xdata
            self._update_measurement_text()
            self.save_state()
            self.canvas.draw_idle()
            return True
        if self.dragging_line == 'h' and event.ydata is not None:
            self.horizontal_line.set_ydata([event.ydata, event.ydata])
            self.line_position_x = event.ydata
            self._update_measurement_text()
            self.save_state()
            self.canvas.draw_idle()
            return True

        if self.dragging_axis_marker:
            axis, idx = self.dragging_axis_marker
            if axis == 'r' and event.xdata is not None:
                marker = self.axis_markers_r[idx]
                marker['line'].set_xdata([event.xdata, event.xdata])
                marker['x'] = event.xdata
                y_top = self.ax.get_ylim()[1] * 0.95
                marker['text'].set_position((event.xdata, y_top))
                marker['text'].set_text(f' {event.xdata:.2f}')
                self.save_state()
                self.canvas.draw_idle()
                return True
            if axis == 'x' and event.ydata is not None:
                marker = self.axis_markers_x[idx]
                marker['line'].set_ydata([event.ydata, event.ydata])
                marker['y'] = event.ydata
                x_right = self.ax.get_xlim()[1] * 0.95
                marker['text'].set_position((x_right, event.ydata))
                marker['text'].set_text(f'{event.ydata:.2f} ')
                self.save_state()
                self.canvas.draw_idle()
                return True

        if self.dragging_point_marker is not None:
            idx = self.dragging_point_marker
            if idx < len(self.point_markers) and event.xdata is not None and event.ydata is not None:
                marker = self.point_markers[idx]
                for line in marker['lines']:
                    line.set_data([event.xdata], [event.ydata])
                marker['text'].set_position((event.xdata, event.ydata))
                marker['text'].set_text(f'({event.xdata:.2f}, {event.ydata:.2f})')
                marker['x'] = event.xdata
                marker['y'] = event.ydata
                self.save_state()
                self.canvas.draw_idle()
                return True

        return False

    def handle_mouse_release(self, event):
        released = False
        if self.dragging_line:
            self.dragging_line = None
            released = True
        if self.dragging_axis_marker:
            self.dragging_axis_marker = None
            released = True
        if self.dragging_point_marker is not None:
            self.dragging_point_marker = None
            released = True

        if released:
            self.canvas.get_tk_widget().configure(cursor="arrow")
            self.canvas.draw_idle()
            return True
        return False

    def update_marker_positions(self):
        y_top = self.ax.get_ylim()[1] * 0.95
        for marker in self.axis_markers_r:
            marker['text'].set_position((marker['x'], y_top))

        x_right = self.ax.get_xlim()[1] * 0.95
        for marker in self.axis_markers_x:
            marker['text'].set_position((x_right, marker['y']))

        for marker in self.point_markers:
            marker['text'].set_position((marker['x'], marker['y']))

        self.canvas.draw_idle()

    def get_stats(self):
        return {'point': len(self.point_markers), 'r': len(self.axis_markers_r), 'x': len(self.axis_markers_x)}
