# -*- coding: utf-8 -*-
"""
Модель данных для уставок зоны дистанционной защиты REL670
"""

from dataclasses import dataclass
from typing import List, Tuple

import numpy as np


@dataclass
class DZ_Settings:
    """
    Уставки для зон дистанционной защиты REL670
    """
    # Основные параметры для Ph-Ph (фаза-фаза)
    x1: float = 7.0  # Реактивное сопротивление прямой последовательности (Ом/фаза)
    r1: float = 2.5  # Активно сопротивление прямой последовательности (Ом/фаза)
    rfpp: float = 7.0  # Переходное сопротивление при повреждении фаза-фаза (дуга) (Ом/петля)

    # Параметры для Ph-E (фаза-земля)
    x0: float = 15.0  # Реактивное сопротивление нулевой последовательности (Ом/фаза)
    r0: float = 7.5  # Активное сопротивление нулевой последовательности (Ом/фаза)
    rfpe: float = 10.0  # Переходное сопротивление при повреждении фаза-фаза (дуга, опора ЛЭП) (Ом/петля)

    # Направленность зоны
    direction_mode: str = "forward"  # прямая, обратная, ненаправленная защиты

    # Параметры исключения нагрузки
    load_encroachment_enabled: bool = False
    r_load_forward: float = 8.0
    r_load_reverse: float = -3.0
    x_load: float = 6.0

    # Дополнительные параметры
    name: str = "Zone"
    enabled: bool = True
    color: str = '#2196F3'
    color_name: str = "Синий"
    linestyle: str = '-'
    zone_id: int = 0
    opacity: float = 0.8
    show_selector: bool = False

    def __post_init__(self):
        valid_modes = ["forward", "reverse", "non-directional"]
        if self.direction_mode not in valid_modes:
            raise ValueError(f"direction_mode должен быть одним из {valid_modes}")

    @property
    def angle_quad2(self):
        """Угол 2-го квадранта из общих настроек"""
        from models.zone_settings import get_common_settings
        common = get_common_settings()
        return common.angle_quad2

    @property
    def angle_quad4(self):
        """Угол 4-го квадранта из общих настроек"""
        from models.zone_settings import get_common_settings
        common = get_common_settings()
        return common.angle_quad4

    @property
    def rca_phph(self) -> float:
        """Угол линии для повреждения фаза-фаза (arctan X1/R1) в градусах"""
        if self.r1 == 0:
            return 90.0
        return np.degrees(np.arctan(self.x1 / self.r1))

    @property
    def rca_phe(self) -> float:
        """Угол линии для повреждения фаза-земля (arctan X0/R0) в градусах"""
        if self.r0 == 0:
            return 90.0
        return np.degrees(np.arctan(self.x0 / self.r0))

    def get_polygon_points(self, fault_type: str = "phph") -> List[Tuple[float, float]]:
        """
        Возвращает точки полигона в зависимости от типа повреждения
        """
        if fault_type != "phph":
            return []

        r1, x1, rfpp = self.r1, self.x1, self.rfpp

        from models.zone_settings import get_common_settings
        common = get_common_settings()

        if self.direction_mode == "non-directional":
            return [
                (r1, x1),
                (r1 + rfpp / 2, x1),
                (rfpp / 2, 0),
                (rfpp / 2, -x1),
                (0, -x1),
                (-(r1 + rfpp / 2), (-x1)),
                (-rfpp / 2, 0),
                (-rfpp / 2, x1),
                (0, x1)
            ]

        elif self.direction_mode in ["forward", "reverse"]:
            # Расчет общих точек для forward
            tan_q2 = np.tan(np.radians(abs(common.angle_quad2)))
            tan_q4 = np.tan(np.radians(common.angle_quad4 - 90))

            # Точки для 2-го квадранта
            if x1 < tan_q2 * rfpp / 2:
                x_q2_1, r_q2_1 = -x1, x1 / tan_q2
                x_q2_2, r_q2_2 = -x1, rfpp / 2
            else:
                x_q2 = -tan_q2 * rfpp / 2
                x_q2_1 = x_q2_2 = x_q2
                r_q2_1 = r_q2_2 = rfpp / 2

            # Точки для 4-го квадранта
            if rfpp / 2 < tan_q4 * x1:
                r_q4_1, x_q4_1 = -rfpp / 2, tan_q4 / rfpp / 2
                r_q4_2, x_q4_2 = -rfpp / 2, x1
                print(tan_q4 * x1)
            else:
                r_q4 = -tan_q4 * x1
                r_q4_1 = r_q4_2 = r_q4
                x_q4_1 = x_q4_2 = x1

            forward_points = [
                (r1, x1),
                (r1 + rfpp / 2, x1),
                (rfpp / 2, 0),
                (r_q2_2, x_q2_2),
                (r_q2_1, x_q2_1),
                (0, 0),
                (r_q4_1, x_q4_1),
                (r_q4_2, x_q4_2),
                (0, x1)
            ]

            # Для reverse - зеркальное отражение
            if self.direction_mode == "reverse":
                return [(-r, -x) for r, x in forward_points]
            return forward_points

        return []

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


@dataclass
class PHS_Settings:
    """
    Настройки для фазного селектора PHS
    """
    # Параметры из вашего примера
    rld_forward: float = 96.0
    rld_reverse: float = 96.0
    angle_load: float = 35.0
    x1: float = 10.0
    x0: float = 30.0
    rfpp_forward: float = 5.0
    rfpp_reverse: float = 5.0
    rfpe_forward: float = 6.0
    rfpe_reverse: float = 6.0
    direction_mode: str = "forward"
    load_enabled: bool = True

    # Дополнительные параметры
    name: str = "Фазовый селектор (PHS)"
    enabled: bool = True
    color: str = '#9C27B0'
    color_name: str = "Фиолетовый"
    linestyle: str = '-'
    opacity: float = 0.8

    def get_polygon_points(self) -> List[Tuple[float, float]]:
        """Возвращает точки полигона для PHS"""
        # Здесь логика построения полигона PHS на основе параметров
        return [
            (0, 0),
            (self.rld_forward, self.x1),
            (self.rld_reverse, -self.x1)
        ]


@dataclass
class Common_Settings:
    """
    Настройки для общих параметров
    """
    _instance = None

    # Параметры из вашего примера
    u_base: float = 115000.0  # Базовое напряжение (В)
    i_base: float = 600.0  # Базовый ток (А)
    i_secondary: float = 5.0  # Вторичный ток (А)
    u_secondary: float = 100.0  # Вторичное напряжение (В)
    angle_quad2: float = -15.0  # Угол 2-го квадранта
    angle_quad4: float = 115.0  # Угол 4-го квадранта
    angle_phs: float = 60.0  # Угол PHS

    # Дополнительные параметры
    name: str = "Общие настройки (U, I)"
    enabled: bool = True
    color: str = '#FF9800'
    color_name: str = "Оранжевый"
    linestyle: str = '--'
    opacity: float = 0.6

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if not hasattr(self, '_initialized'):
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            self._initialized = True


_common_instance = None


def set_common_settings(settings):
    """Установить глобальные общие настройки"""
    global _common_instance
    _common_instance = settings


def get_common_settings():
    """Получить глобальные общие настройки"""
    return _common_instance
