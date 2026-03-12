# ui/markers/axis_markers.py
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class AxisMarker:
    x: float
    y: float
    line: object
    text: object
    type: str


class AxisRMarkers:
    """Маркеры на оси R (вертикальные линии)"""
    
    def __init__(self, ax, canvas):
        self.ax = ax
        self.canvas = canvas
        self.markers: List[AxisMarker] = []
        self.dragging_index: Optional[int] = None
    
    def add(self, x: float):
        """Добавить маркер"""
        line = self.ax.axvline(x=x, color='orange', linestyle='-', linewidth=2, alpha=0.8)
        y_top = self.ax.get_ylim()[1] * 0.95
        text = self.ax.text(x, y_top, f' {x:.2f}', rotation=90, verticalalignment='top',
                           fontsize=8, color='orange', fontweight='bold')
        
        marker = AxisMarker(x=x, y=y_top, line=line, text=text, type='r')
        self.markers.append(marker)
        self.canvas.draw_idle()
        return marker
    
    def handle_drag(self, event) -> bool:
        """Обработка перетаскивания"""
        if self.dragging_index is None or not event.inaxes or not event.xdata:
            return False
        
        idx = self.dragging_index
        if idx < len(self.markers):
            self._update_position(idx, event.xdata)
            return True
        return False
    
    def _update_position(self, index: int, new_x: float):
        """Обновление позиции маркера"""
        marker = self.markers[index]
        marker.x = new_x
        marker.line.set_xdata([new_x, new_x])
        
        y_top = self.ax.get_ylim()[1] * 0.95
        marker.text.set_position((new_x, y_top))
        marker.text.set_text(f' {new_x:.2f}')
        
        self.canvas.draw_idle()
    
    def update_positions(self):
        """Обновление позиций текста после изменения масштаба"""
        y_top = self.ax.get_ylim()[1] * 0.95
        for marker in self.markers:
            marker.text.set_position((marker.x, y_top))


class AxisXMarkers:
    """Маркеры на оси X (горизонтальные линии)"""
    
    def __init__(self, ax, canvas):
        self.ax = ax
        self.canvas = canvas
        self.markers: List[AxisMarker] = []
        self.dragging_index: Optional[int] = None
    
    def add(self, y: float):
        """Добавить маркер"""
        line = self.ax.axhline(y=y, color='purple', linestyle='-', linewidth=2, alpha=0.8)
        x_right = self.ax.get_xlim()[1] * 0.95
        text = self.ax.text(x_right, y, f'{y:.2f} ', horizontalalignment='right',
                           fontsize=8, color='purple', fontweight='bold')
        
        marker = AxisMarker(x=x_right, y=y, line=line, text=text, type='x')
        self.markers.append(marker)
        self.canvas.draw_idle()
        return marker
    
    def handle_drag(self, event) -> bool:
        """Обработка перетаскивания"""
        if self.dragging_index is None or not event.inaxes or not event.ydata:
            return False
        
        idx = self.dragging_index
        if idx < len(self.markers):
            self._update_position(idx, event.ydata)
            return True
        return False
    
    def _update_position(self, index: int, new_y: float):
        """Обновление позиции маркера"""
        marker = self.markers[index]
        marker.y = new_y
        marker.line.set_ydata([new_y, new_y])
        
        x_right = self.ax.get_xlim()[1] * 0.95
        marker.text.set_position((x_right, new_y))
        marker.text.set_text(f'{new_y:.2f} ')
        
        self.canvas.draw_idle()
    
    def update_positions(self):
        """Обновление позиций текста после изменения масштаба"""
        x_right = self.ax.get_xlim()[1] * 0.95
        for marker in self.markers:
            marker.text.set_position((x_right, marker.y))