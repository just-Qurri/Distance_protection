# -*- coding: utf-8 -*-
"""
Модель данных для уставок зоны дистанционной защиты REL670
"""

from dataclasses import dataclass, field
from typing import List, Tuple

import numpy as np


@dataclass
class Poligon_Settings:
    """
    Уставки зоны дистанционной защиты REL670
    """
    # Основные параметры для Ph-Ph (фаза-фаза)
    x1: float = 7  # Positive sequence reactance reach (Ом/фаза)
    r1: float = 2.5  # Positive seq. resistance (Ом/фаза)
    rfpp: float = 7.0  # Fault resistance reach for Ph-Ph (Ом/петля)

    # Параметры для Ph-E (фаза-земля)
    x0: float = 15.0  # Zero sequence reactance (Ом/фаза)
    r0: float = 7.5  # Zero sequence resistance (Ом/фаза)
    rfpe: float = 10.0  # Fault resistance reach for Ph-E (Ом/петля)

    rca: float = 75.0  # Relay characteristic angle (градусы)
    angle: float = 75.0  # Угол наклона верхней границы

    # Углы для зон дистанционной защиты
    angle_quad2: float = 115.0  # Угол для 2-го квадранта
    angle_quad4: float = -15.0  # Угол для 4-го квадранта

    # Направленность зоны
    direction_mode: str = "forward"  # forward, reverse, non-directional

    # Параметры исключения нагрузки
    load_encroachment_enabled: bool = False
    r_load_forward: float = 8.0
    r_load_reverse: float = -3.0
    x_load: float = 6.0

    # Координаты характерных точек полигона (6 точек A-F)
    # Базовые точки согласно вашему описанию: (0,0), (-2,5), (0,5), (7,5), (5,0), (5,-2)
    base_points: List[Tuple[float, float]] = field(default_factory=lambda: [
        (0, 0),  # A - начало координат
        (-2, 5),  # B - левый верхний изгиб
        (0, 5),  # C - верхний левый угол
        (7, 5),  # D - верхний правый угол
        (5, 0),  # E - правый нижний изгиб
        (5, -2)  # F - нижняя точка
    ])

    # Дополнительные параметры
    name: str = "Zone"
    enabled: bool = True
    color: str = '#2196F3'
    color_name: str = "Синий"
    linestyle: str = '-'
    zone_id: int = 0
    phs_id: int = 0
    opacity: float = 0.8
    show_selector: bool = False

    def __post_init__(self):
        self.update_angles()

        valid_modes = ["forward", "reverse", "non-directional"]
        if self.direction_mode not in valid_modes:
            raise ValueError(f"direction_mode должен быть одним из {valid_modes}")

    def update_angles(self):
        """Обновление углов в радианах"""
        self.rca_rad = np.radians(self.rca)
        self.angle_rad = np.radians(self.angle)
        self.angle_quad2_rad = np.radians(self.angle_quad2)
        self.angle_quad4_rad = np.radians(self.angle_quad4)

    def get_polygon_points(self, fault_type: str = "phph") -> List[Tuple[float, float]]:
        """
        Возвращает точки полигона в зависимости от типа повреждения
        С масштабированием для разных типов
        """
        scale = 1
        # Масштабируем базовые точки
        scaled_points = [(r * scale, x * scale) for r, x in self.base_points]

        # Применяем направленность
        if self.direction_mode == "reverse":
            # Обратное направление - инвертируем X
            scaled_points = [(r, -x) for r, x in scaled_points]
        elif self.direction_mode == "non-directional":
            # Для ненаправленной создаем симметричную относительно оси R
            points = []
            # Верхняя часть
            for r, x in scaled_points:
                if x >= 0:
                    points.append([r, x])
            # Нижняя часть (зеркально)
            for r, x in reversed(scaled_points):
                if x > 0:  # избегаем дублирования нулевых точек
                    points.append([r, -x])
            return points

        return scaled_points

    def get_zone_bounds(self, fault_type: str = "phph") -> Tuple[float, float, float, float]:
        """Возвращает границы зоны"""
        points = self.get_polygon_points(fault_type)

        min_r = float('inf')
        max_r = float('-inf')
        min_x = float('inf')
        max_x = float('-inf')

        for r, x in points:
            min_r = min(min_r, r)
            max_r = max(max_r, r)
            min_x = min(min_x, x)
            max_x = max(max_x, x)

        return min_r, max_r, min_x, max_x
