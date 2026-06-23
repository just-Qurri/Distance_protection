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
    Согласно документации REL670

    Параметры:
        X1: Положительная последовательность (Ом/фаза)
        X0: Нулевая последовательность (Ом/фаза)
        RFFwPP: Сопротивление дуги Ph-Ph прямое (Ом/петля)
        RFRvPP: Сопротивление дуги Ph-Ph обратное (Ом/петля)
        RFFwPE: Сопротивление дуги Ph-E прямое (Ом/петля)
        RFRvPE: Сопротивление дуги Ph-E обратное (Ом/петля)
        RLdFw: Резистивная досягаемость вперед (Ом)
        RLdRv: Резистивная досягаемость назад (Ом)
        ArgLd: Угол нагрузки (градусы) - откладывается от оси R
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
        if fault_type == "phph":
            r_forward = self.rfpp_forward
            r_reverse = self.rfpp_reverse
        else:
            r_forward = self.rfpe_forward
            r_reverse = self.rfpe_reverse

        points = self._get_selector_base_points(r_forward, r_reverse)

        if self.load_enabled:
            points = self._apply_load_encroachment(points)

        return points

    def _get_selector_base_points(self, r_forward: float, r_reverse: float) -> List[Tuple[float, float]]:
        x_reach = self.x1

        points = [
            (r_forward / 2, x_reach),
            (r_forward / 2, 0),
            (-r_reverse / 2, 0),
            (-r_reverse / 2, x_reach),
            (r_forward / 2, -x_reach),
            (r_forward / 2, 0),
            (-r_reverse / 2, 0),
            (-r_reverse / 2, -x_reach),
        ]

        return points

    def _apply_load_encroachment(self, points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        if not self.load_enabled:
            return points

        arg_load_rad = np.radians(self.arg_load)
        tan_load = np.tan(arg_load_rad)

        r_fw_intersect_pos = self.rld_forward
        x_fw_intersect_pos = r_fw_intersect_pos * tan_load

        r_fw_intersect_neg = self.rld_forward
        x_fw_intersect_neg = -r_fw_intersect_neg * tan_load

        r_rv_intersect_pos = -self.rld_reverse
        x_rv_intersect_pos = abs(r_rv_intersect_pos) * tan_load

        r_rv_intersect_neg = -self.rld_reverse
        x_rv_intersect_neg = -abs(r_rv_intersect_neg) * tan_load

        clipped_points = []

        for r, x in points:
            should_clip = False

            if r >= 0:
                if x >= 0:
                    if r > self.rld_forward and x < r * tan_load:
                        should_clip = True
                        clipped_points.append((r_fw_intersect_pos, x_fw_intersect_pos))
                else:
                    if r > self.rld_forward and x > -r * tan_load:
                        should_clip = True
                        clipped_points.append((r_fw_intersect_neg, x_fw_intersect_neg))

            elif r < 0:
                r_abs = abs(r)
                if x >= 0:
                    if r < -self.rld_reverse and x < r_abs * tan_load:
                        should_clip = True
                        clipped_points.append((r_rv_intersect_pos, x_rv_intersect_pos))
                else:
                    if r < -self.rld_reverse and x > -r_abs * tan_load:
                        should_clip = True
                        clipped_points.append((r_rv_intersect_neg, x_rv_intersect_neg))

            if not should_clip:
                clipped_points.append((r, x))

        clipped_points.append((self.rld_forward, 0))
        clipped_points.append((r_fw_intersect_pos, x_fw_intersect_pos))
        clipped_points.append((self.rld_forward, 0))
        clipped_points.append((r_fw_intersect_neg, x_fw_intersect_neg))
        clipped_points.append((-self.rld_reverse, 0))
        clipped_points.append((r_rv_intersect_pos, x_rv_intersect_pos))
        clipped_points.append((-self.rld_reverse, 0))
        clipped_points.append((r_rv_intersect_neg, x_rv_intersect_neg))

        return self._clean_polygon_points(clipped_points)

    def _clean_polygon_points(self, points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        if not points:
            return points

        unique_points = []
        for p in points:
            is_duplicate = False
            for existing in unique_points:
                if abs(p[0] - existing[0]) < 0.001 and abs(p[1] - existing[1]) < 0.001:
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique_points.append(p)

        if len(unique_points) >= 3:
            cx = sum(p[0] for p in unique_points) / len(unique_points)
            cy = sum(p[1] for p in unique_points) / len(unique_points)
            unique_points.sort(key=lambda p: np.arctan2(p[1] - cy, p[0] - cx))

        return unique_points

    def get_load_encroachment_lines(self) -> List[Tuple[float, float, float, float]]:
        lines = []
        if not self.load_enabled:
            return lines

        arg_load_rad = np.radians(self.arg_load)
        tan_load = np.tan(arg_load_rad)

        max_r = max(self.rld_forward, self.rld_reverse) * 2.5

        r_fw = self.rld_forward
        x_fw = r_fw * tan_load

        r_rv = -self.rld_reverse
        x_rv = abs(r_rv) * tan_load

        # Лучи от точки пересечения и дальше
        lines.append((r_fw, x_fw, max_r, max_r * tan_load))
        lines.append((r_rv, x_rv, -max_r, max_r * tan_load))
        lines.append((r_rv, -x_rv, -max_r, -max_r * tan_load))
        lines.append((r_fw, -x_fw, max_r, -max_r * tan_load))

        # Перпендикуляры от оси R до точки пересечения
        lines.append((r_fw, 0, r_fw, x_fw))
        lines.append((r_fw, 0, r_fw, -x_fw))
        lines.append((r_rv, 0, r_rv, x_rv))
        lines.append((r_rv, 0, r_rv, -x_rv))

        return lines

    def get_load_encroachment_polygons(self) -> List[List[Tuple[float, float]]]:
        """
        Возвращает список полигонов отстройки от нагрузки для отображения.
        Каждый квадрант - отдельный полигон.
        """
        if not self.load_enabled:
            return []

        arg_load_rad = np.radians(self.arg_load)
        tan_load = np.tan(arg_load_rad)

        max_r = max(self.rld_forward, self.rld_reverse) * 2.5

        r_fw = self.rld_forward
        r_rv = -self.rld_reverse

        x_fw = r_fw * tan_load
        x_rv = abs(r_rv) * tan_load

        polygons = []

        # I квадрант
        polygons.append([
            (r_fw, 0),
            (r_fw, x_fw),
            (max_r, max_r * tan_load),
            (max_r, 0)
        ])

        # IV квадрант
        polygons.append([
            (r_fw, 0),
            (r_fw, -x_fw),
            (max_r, -max_r * tan_load),
            (max_r, 0)
        ])

        # II квадрант
        polygons.append([
            (r_rv, 0),
            (r_rv, x_rv),
            (-max_r, max_r * tan_load),
            (-max_r, 0)
        ])

        # III квадрант
        polygons.append([
            (r_rv, 0),
            (r_rv, -x_rv),
            (-max_r, -max_r * tan_load),
            (-max_r, 0)
        ])

        return polygons

    def get_bounds(self) -> Tuple[float, float, float, float]:
        points = self.get_polygon_points()
        if not points:
            return (0, 0, 0, 0)

        min_r = min(p[0] for p in points)
        max_r = max(p[0] for p in points)
        min_x = min(p[1] for p in points)
        max_x = max(p[1] for p in points)

        if self.load_enabled:
            margin = max(self.rld_forward, self.rld_reverse) * 0.5
            min_r -= margin
            max_r += margin
            min_x -= margin
            max_x += margin

        return (min_r, max_r, min_x, max_x)
