"""
Модель данных для уставок зоны дистанционной защиты REL670
"""

from dataclasses import dataclass, field
from typing import List, Tuple

import numpy as np

from models.common_settings import CommonSettings


@dataclass
class DZSettings:
    """
    Уставки для зон дистанционной защиты REL670
    """
    # Основные параметры для Ph-Ph
    x1: float = 3.0
    r1: float = 1.5
    rfpp: float = 5.0

    # Параметры для Ph-E
    x0: float = 9.0
    r0: float = 4.5
    rfpe: float = 8.0

    # Направленность зоны
    direction_mode: str = "forward"

    # Параметры согласования
    phase_selector_enabled: bool = False
    load_enabled: bool = False

    # Дополнительные параметры
    name: str = "Zone"
    enabled: bool = True
    color: str = '#2196F3'
    color_name: str = "Синий"
    linestyle: str = '-'
    zone_id: int = 0
    opacity: float = 0.8
    show_selector: bool = False
    type: str = field(default="zone", init=False)

    def __post_init__(self):
        valid_modes = ["forward", "reverse", "non-directional"]
        if self.direction_mode not in valid_modes:
            raise ValueError(f"direction_mode должен быть одним из {valid_modes}")

    @property
    def angle_quad2(self) -> float:
        """Угол 2-го квадранта из общих настроек"""
        return CommonSettings().angle_quad2

    @property
    def angle_quad4(self) -> float:
        """Угол 4-го квадранта из общих настроек"""
        return CommonSettings().angle_quad4

    def get_polygon_points(self, fault_type: str) -> List[Tuple[float, float]]:
        """
        Возвращает точки полигона в зависимости от типа повреждения
        """
        if fault_type == "ph-e":
            rn = (self.r0 - self.r1) / 3
            xn = (self.x0 - self.x1) / 3
            r, x, r_p = self.r1 + rn, self.x1 + xn, self.rfpe
        else:
            r, x, r_p = self.r1, self.x1, self.rfpp / 2

        if self.direction_mode == "non-directional":
            return [
                (r, x), (r + r_p, x), (r_p, 0),
                (r_p, -x), (0, -x),
                (-(r + r_p), -x), (-r_p, 0),
                (-r_p, x), (0, x)
            ]

        elif self.direction_mode in ["forward", "reverse"]:
            points = self._get_directional_points(r, x, r_p)
            if self.direction_mode == "reverse":
                return [(-p[0], -p[1]) for p in points]
            return points

        return []

    def _get_directional_points(
            self,
            r: float,
            x: float,
            r_p: float
    ) -> List[Tuple[float, float]]:
        """Расчет точек для направленных зон"""
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

        return [
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

    def get_bounds(self, fault_type: str = "ph-ph") -> Tuple[float, float, float, float]:
        """Возвращает границы зоны (min_r, max_r, min_x, max_x)"""
        points = self.get_polygon_points(fault_type)

        if not points:
            return (0, 0, 0, 0)

        min_r = min(p[0] for p in points)
        max_r = max(p[0] for p in points)
        min_x = min(p[1] for p in points)
        max_x = max(p[1] for p in points)

        return min_r, max_r, min_x, max_x
