# -*- coding: utf-8 -*-
"""
Модель данных для уставок зоны дистанционной защиты REL670
Основано на технической документации ABB REL670
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Callable
import numpy as np


@dataclass
class ZoneSettings:
    """
    Уставки зоны дистанционной защиты REL670 согласно технической документации
    """
    # Основные параметры для Ph-Ph (фаза-фаза)
    x1: float = 5.0  # Positive sequence reactance reach (Ом/фаза)
    r1: float = 2.5  # Positive seq. resistance (Ом/фаза)
    rfpp: float = 7.0  # Fault resistance reach for Ph-Ph (Ом/петля)

    # Параметры для Ph-E (фаза-земля)
    x0: float = 15.0  # Zero sequence reactance (Ом/фаза)
    r0: float = 7.5  # Zero sequence resistance (Ом/фаза)
    rfpe: float = 10.0  # Fault resistance reach for Ph-E (Ом/петля)

    rca: float = 75.0  # Relay characteristic angle (градусы)
    angle: float = 75.0  # Угол наклона верхней границы

    # Углы для зон дистанционной защиты (Ph-Ph и Ph-E)
    angle_quad2: float = 115.0  # Угол для 2-го квадранта (прямое направление)
    angle_quad4: float = -15.0  # Угол для 4-го квадранта (обратное направление)

    # Направленность зоны
    direction_mode: str = "forward"  # forward, reverse, non-directional

    # Параметры фазового селектора (FDPSPDIS)
    selector_angle: float = 60.0  # Угол для фазового селектора (рекомендуемый 60°)
    rffw_pp: float = 8.0  # RFFwPP - сопротивление для Ph-Ph, прямое
    rfrv_pp: float = 4.0  # RFRvPP - сопротивление для Ph-Ph, обратное
    rffw_pe: float = 12.0  # RFFwPE - сопротивление для Ph-E, прямое
    rfrv_pe: float = 6.0  # RFRvPE - сопротивление для Ph-E, обратное

    # Параметры нагрузки
    rld_fw: float = 8.0  # RLdFw - резистивная досягаемость вперед
    rld_rv: float = -3.0  # RLdRv - резистивная досягаемость назад
    arg_ld: float = 30.0  # ArgLd - угол нагрузки

    # Параметры исключения нагрузки (Load encroachment)
    load_encroachment_enabled: bool = False
    r_load_forward: float = 8.0
    r_load_reverse: float = -3.0
    x_load: float = 6.0

    # Координаты характерных точек полигона
    polygon_points_phph: List[Tuple[float, float]] = None  # Для Ph-Ph
    polygon_points_phe: List[Tuple[float, float]] = None  # Для Ph-E
    polygon_points_selector: List[Tuple[float, float]] = None  # Для фазового селектора

    # Дополнительные параметры
    name: str = "Zone"
    enabled: bool = True
    color: str = '#2196F3'
    color_name: str = "Синий"
    linestyle: str = '-'
    zone_id: int = 0
    opacity: float = 0.8
    show_selector: bool = False  # Отображение фазового селектора

    def __post_init__(self):
        self.update_angles()

        valid_modes = ["forward", "reverse", "non-directional"]
        if self.direction_mode not in valid_modes:
            raise ValueError(f"direction_mode должен быть одним из {valid_modes}")

        if self.polygon_points_phph is None:
            self.polygon_points_phph = self._create_phph_points()
        if self.polygon_points_phe is None:
            self.polygon_points_phe = self._create_phe_points()
        if self.polygon_points_selector is None:
            self.polygon_points_selector = self._create_selector_points()

    def update_angles(self):
        """Обновление углов в радианах"""
        self.rca_rad = np.radians(self.rca)
        self.angle_rad = np.radians(self.angle)
        self.angle_quad2_rad = np.radians(self.angle_quad2)
        self.angle_quad4_rad = np.radians(self.angle_quad4)
        self.selector_angle_rad = np.radians(self.selector_angle)
        self.arg_ld_rad = np.radians(self.arg_ld)

    def _create_phph_points(self) -> List[Tuple[float, float]]:
        """Создание точек полигона для Ph-Ph (фаза-фаза) с учетом углов для зон"""
        points = []

        # Точка в 4-м квадранте (обратное направление) - угол -15°
        r_quad4 = self.rfrv_pp * np.cos(self.angle_quad4_rad)
        x_quad4 = self.rfrv_pp * np.sin(self.angle_quad4_rad)
        points.append([r_quad4, x_quad4])

        # Точка на отрицательной оси X
        points.append([0, -self.x1 * 0.8])

        # Точка в начале координат
        points.append([0, 0])

        # Точка на положительной оси X
        points.append([self.rfpp, 0])

        # Точка во 2-м квадранте (прямое направление) - угол 115°
        r_quad2 = self.rffw_pp * np.cos(self.angle_quad2_rad)
        x_quad2 = self.rffw_pp * np.sin(self.angle_quad2_rad)
        points.append([r_quad2, x_quad2])

        # Точка на положительной оси X (верхняя)
        points.append([self.rfpp * 0.7, self.x1])

        # Замыкаем полигон
        points.append(points[0])

        return points

    def _create_phe_points(self) -> List[Tuple[float, float]]:
        """Создание точек полигона для Ph-E (фаза-земля) с учетом углов для зон"""
        x_effective = (2 * self.x1 + self.x0) / 3

        points = []

        # Точка в 4-м квадранте (обратное направление) - угол -15°
        r_quad4 = self.rfrv_pe * np.cos(self.angle_quad4_rad)
        x_quad4 = self.rfrv_pe * np.sin(self.angle_quad4_rad)
        points.append([r_quad4, x_quad4])

        # Точка на отрицательной оси X
        points.append([0, -x_effective * 0.8])

        # Точка в начале координат
        points.append([0, 0])

        # Точка на положительной оси X
        points.append([self.rfpe, 0])

        # Точка во 2-м квадранте (прямое направление) - угол 115°
        r_quad2 = self.rffw_pe * np.cos(self.angle_quad2_rad)
        x_quad2 = self.rffw_pe * np.sin(self.angle_quad2_rad)
        points.append([r_quad2, x_quad2])

        # Точка на положительной оси X (верхняя)
        points.append([self.rfpe * 0.7, x_effective])

        # Замыкаем полигон
        points.append(points[0])

        return points

    def _create_selector_points(self) -> List[Tuple[float, float]]:
        """
        Создание точек для фазового селектора
        Угол 60°, НЕНАПРАВЛЕННАЯ характеристика
        """
        points = []

        # Эффективное реактивное сопротивление
        x_effective = (2 * self.x1 + self.x0) / 3

        # Точка в верхней полуплоскости (под углом 60°)
        r_up = self.rffw_pe * np.cos(self.selector_angle_rad)
        x_up = self.rffw_pe * np.sin(self.selector_angle_rad)
        points.append([r_up, x_up])

        # Точка на положительной оси X
        points.append([self.rld_fw, 0])

        # Точка в нижней полуплоскости (под углом -60°)
        r_down = self.rfrv_pe * np.cos(-self.selector_angle_rad)
        x_down = self.rfrv_pe * np.sin(-self.selector_angle_rad)
        points.append([r_down, x_down])

        # Точка на отрицательной оси X
        points.append([self.rld_rv, 0])

        # Замыкаем полигон
        points.append(points[0])

        return points

    def get_polygon_points(self, fault_type: str = "phph") -> List[Tuple[float, float]]:
        """Возвращает точки полигона в зависимости от типа"""
        if fault_type == "selector" and self.show_selector:
            return self.polygon_points_selector
        elif fault_type == "phe":
            return self.polygon_points_phe
        else:
            return self.polygon_points_phph

    def update_polygon_points(self):
        """Обновление точек полигона"""
        self.polygon_points_phph = self._create_phph_points()
        self.polygon_points_phe = self._create_phe_points()
        self.polygon_points_selector = self._create_selector_points()

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