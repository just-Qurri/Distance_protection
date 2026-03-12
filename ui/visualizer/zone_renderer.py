# ui/visualizer/zone_renderer.py
from models.zone_settings import ZoneSettings  # Добавляем импорт
from typing import List, Optional

class ZoneRenderer:
    def __init__(self, visualizer):
        self.viz = visualizer
        self.zones: List[ZoneSettings] = []
    
    def add_zone(self, zone: ZoneSettings):
        """Добавление зоны"""
        self.zones.append(zone)
    
    def render_zones(self):
        """Отрисовка всех зон"""
        for zone in self.zones:
            self._render_single_zone(zone)
    
    def _render_single_zone(self, zone: ZoneSettings):
        """Отрисовка одной зоны"""
        # Здесь логика отрисовки зоны
        pass