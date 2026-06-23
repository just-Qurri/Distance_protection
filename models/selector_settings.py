# -*- coding: utf-8 -*-
"""
Модель данных для фазового селектора FDPSPDIS с отстройкой от нагрузки
Согласно документации REL670
"""

from dataclasses import dataclass
from typing import List, Tuple

import numpy as np


@dataclass
class SelectorSettings:
    """
    Модель данных для фазового селектора FDPSPDIS
    """
    # ===== Параметры фазового селектора =====
    x1: float = 37.0
    x0: float = 43.0
    rfpp_forward: float = 164.0
    rfpp_reverse: float = 164.0
    rfpe_forward: float = 135.0
    rfpe_reverse: float = 135.0

    # ===== Параметры отстройки от нагрузки =====
    rld_forward: float = 96.0
    rld_reverse: float = 96.0
    arg_load: float = 35.0
    load_enabled: bool = True

    # ===== Параметры отображения =====
    enabled: bool = True
    color: str = '#9C27B0'
    linestyle: str = '-'
    opacity: float = 0.8
    direction_mode: str = "non-directional"

    def get_polygon_points(self, fault_type: str = "phph") -> List[Tuple[float, float]]:
        """
        Возвращает точки полигона фазового селектора.
        Фазовый селектор НЕ МЕНЯЕТСЯ от включения/выключения отстройки!
        """
        if fault_type == "phph":
            r_forward = self.rfpp_forward
            r_reverse = self.rfpp_reverse
        elif fault_type == "phe":
            r_forward = self.rfpe_forward
            r_reverse = self.rfpe_reverse
        else:
            K3 = 2 / np.sqrt(3)
            r_forward = K3 * self.rfpe_forward
            r_reverse = K3 * self.rfpe_reverse

        return self._build_selector(r_forward, r_reverse)

    def _build_selector(self, r_forward: float, r_reverse: float) -> List[Tuple[float, float]]:
        """6 точек фазового селектора (шестиугольник)"""
        x_reach = self.x1
        tan_60 = np.tan(np.radians(60.0))
        r_offset = x_reach / tan_60

        return [
            # ВЕРХНЯЯ ЧАСТЬ
            (-r_reverse / 2, x_reach),
            (r_forward / 2 + r_offset, x_reach),
            (r_forward / 2, 0),

            # НИЖНЯЯ ЧАСТЬ
            (r_forward / 2, -x_reach),
            (-r_reverse / 2 - r_offset, -x_reach),
            (-r_reverse / 2, 0),
        ]

    def get_load_encroachment_lines(self) -> List[Tuple[float, float, float, float]]:
        """
        Линии отстройки от нагрузки
        """
        if not self.load_enabled:
            return []

        tan_load = np.tan(np.radians(self.arg_load))
        max_r = max(self.rld_forward, self.rld_reverse) * 2.5

        r_fw = self.rld_forward
        r_rv = -self.rld_reverse

        return [
            # Лучи сектора (от начала координат)
            (0, 0, max_r, max_r * tan_load),  # Луч в I квадранте
            (0, 0, -max_r, max_r * tan_load),  # Луч в II квадранте
            (0, 0, -max_r, -max_r * tan_load),  # Луч в III квадранте
            (0, 0, max_r, -max_r * tan_load),  # Луч в IV квадранте

            # Перпендикуляры в точках RLdFw и RLdRv (границы сектора)
            (r_fw, -max_r * tan_load, r_fw, max_r * tan_load),  # Перпендикуляр в RLdFw
            (r_rv, -max_r * tan_load, r_rv, max_r * tan_load),  # Перпендикуляр в -RLdRv
        ]

    def get_load_encroachment_polygons(self) -> List[List[Tuple[float, float]]]:
        """
        Полигоны сектора нагрузки для заливки.
        """
        if not self.load_enabled:
            return []

        tan_load = np.tan(np.radians(self.arg_load))
        max_r = max(self.rld_forward, self.rld_reverse) * 2.5

        r_fw = self.rld_forward
        r_rv = -self.rld_reverse
        x_fw = r_fw * tan_load
        x_rv = abs(r_rv) * tan_load

        return [
            # I квадрант
            [(r_fw, 0), (r_fw, x_fw), (max_r, max_r * tan_load), (max_r, 0)],
            # II квадрант
            [(r_rv, 0), (r_rv, x_rv), (-max_r, max_r * tan_load), (-max_r, 0)],
            # III квадрант
            [(r_rv, 0), (r_rv, -x_rv), (-max_r, -max_r * tan_load), (-max_r, 0)],
            # IV квадрант
            [(r_fw, 0), (r_fw, -x_fw), (max_r, -max_r * tan_load), (max_r, 0)],
        ]

    """def get_selector_with_load_clipping(self, fault_type: str = "phph") -> Tuple[List[List[Tuple[float, float]]], List[List[Tuple[float, float]]]]:
        
        Обрезка фазового селектора нагрузкой
        
        if"""
