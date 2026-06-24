"""
Модель данных для уставок зоны дистанционной защиты REL670
"""

from dataclasses import dataclass
from typing import Tuple

import numpy as np

from models.common_settings import Common_Settings


@dataclass
class DZ_Settings:
    """
    Уставки для зон дистанционной защиты REL670
    """
    # Основные параметры для Ph-Ph (фаза-фаза)
    x1: float = 3.0  # Реактивное сопротивление прямой последовательности (Ом/фаза)
    r1: float = 1.5  # Активно сопротивление прямой последовательности (Ом/фаза)
    rfpp: float = 5.0  # Переходное сопротивление при повреждении фаза-фаза (дуга) (Ом/петля)

    # Параметры для Ph-E (фаза-земля)
    x0: float = 9.0  # Реактивное сопротивление нулевой последовательности (Ом/фаза)
    r0: float = 4.5  # Активное сопротивление нулевой последовательности (Ом/фаза)
    rfpe: float = 8.0  # Переходное сопротивление при повреждении фаза-фаза (дуга, опора ЛЭП) (Ом/петля)

    # Направленность зоны
    direction_mode: str = "forward"  # прямая, обратная, ненаправленная защиты

    # Параметры согласования с фазовым селектором и отстройкой от нагрузки
    phase_selector_enabled: bool = False
    load__enabled: bool = False

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
        common = Common_Settings()
        return common.angle_quad2

    @property
    def angle_quad4(self):
        """Угол 4-го квадранта из общих настроек"""
        common = Common_Settings()
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

    def get_polygon_points(self, fault_type):
        """
        Возвращает точки полигона в зависимости от типа повреждения
        """
        if fault_type == "ph-e":
            rn = (self.r0 - self.r1) / 3
            xn = (self.x0 - self.x1) / 3
            r, x, r_p = self.r1 + rn, self.x1 + xn, self.rfpe
            print(r, x, r_p)
        else:
            r, x, r_p = self.r1, self.x1, self.rfpp / 2

        if self.direction_mode == "non-directional":
            return [
                (r, x),
                (r + r_p, x),
                (r_p, 0),
                (r_p, -x),
                (0, -x),
                (-(r + r_p), (-x)),
                (-r_p, 0),
                (-r_p, x),
                (0, x)
            ]

        elif self.direction_mode in ["forward", "reverse"]:
            # Расчет общих точек для forward
            tan_q2 = np.tan(np.radians(abs(self.angle_quad2)))
            tan_q4 = np.tan(np.radians(self.angle_quad4 - 90))

            # Точки для 2-го квадранта
            if x < tan_q2 * r_p:
                x_q2_1, r_q2_1 = -x, x / tan_q2
                x_q2_2, r_q2_2 = -x, r_p
            else:
                x_q2 = -tan_q2 * r_p
                x_q2_1 = x_q2_2 = x_q2
                r_q2_1 = r_q2_2 = r_p

            # Точки для 4-го квадранта
            if r_p < tan_q4 * x:
                r_q4_1, x_q4_1 = -r_p, tan_q4 * r_p
                r_q4_2, x_q4_2 = -r_p, x
            else:
                r_q4 = -tan_q4 * x
                r_q4_1 = r_q4_2 = r_q4
                x_q4_1 = x_q4_2 = x

            forward_points = [
                (r, x),
                (r + r_p, x),
                (r_p, 0),
                (r_q2_2, x_q2_2),
                (r_q2_1, x_q2_1),
                (0, 0),
                (r_q4_1, x_q4_1),
                (r_q4_2, x_q4_2),
                (0, x)
            ]

            # Для reverse - зеркальное отражение
            if self.direction_mode == "reverse":
                return [(-r, -x) for r, x in forward_points]
            return forward_points

        return []

    def get_zone_bounds(self, fault_type: str = "ph-ph") -> Tuple[float, float, float, float]:
        """Возвращает границы зоны"""
        points = self.get_polygon_points(fault_type)

        if not points:
            return (0, 0, 0, 0)

        min_r = min(p[0] for p in points)
        max_r = max(p[0] for p in points)
        min_x = min(p[1] for p in points)
        max_x = max(p[1] for p in points)

        return min_r, max_r, min_x, max_x
