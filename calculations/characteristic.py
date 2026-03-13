# -*- coding: utf-8 -*-
"""
Класс для расчета полигональной характеристики REL670
"""

from typing import Tuple

import numpy as np

from models.zone_settings import Poligon_Settings


class REL670PolygonalCharacteristic:
    """Класс для построения характеристик REL670"""

    def __init__(self, settings: Poligon_Settings, fault_type: str = "phph"):
        """
        Инициализация характеристики

        Args:
            settings: Объект с уставками зоны
            fault_type: Тип повреждения ("phph", "phe", "selector")
        """
        self.settings = settings
        self.fault_type = fault_type

    def calculate_polygon_points(self) -> np.ndarray:
        """Возвращает точки полигона"""
        points = self.settings.get_polygon_points(self.fault_type)
        return np.array(points)

    def get_direction_symbol(self) -> str:
        """Возвращает символ направления"""
        direction_symbols = {
            "forward": "↑",
            "reverse": "↓",
            "non-directional": "↕"
        }
        return direction_symbols.get(self.settings.direction_mode, "")

    def get_fault_type_symbol(self) -> str:
        """Возвращает символ типа повреждения"""
        symbols = {
            "phph": "∿",
            "phe": "⏚",
            "selector": "⚡"
        }
        return symbols.get(self.fault_type, "")

    def get_rca_line(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Возвращает точки для построения линии RCA

        Returns:
            (x_coords, y_coords) для линии RCA
        """
        rca_length = max(abs(self.settings.x1), abs(self.settings.rfpp)) * 0.3
        rca_x = np.array([0, rca_length * np.cos(self.settings.rca_rad)])

        y_multiplier = -1 if self.settings.direction_mode == "reverse" else 1
        rca_y = np.array([0, rca_length * np.sin(self.settings.rca_rad) * y_multiplier])

        return rca_x, rca_y
