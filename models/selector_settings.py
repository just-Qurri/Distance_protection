# -*- coding: utf-8 -*-
"""
Модель данных для фазового селектора FDPSPDIS с отстройкой от нагрузки
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
        ArgLd: Угол нагрузки (градусы)
    """
    # ===== Параметры фазового селектора =====
    x1: float = 5.0  # X₁ - Положительная последовательность (Ом/фаза)
    x0: float = 15.0  # X₀ - Нулевая последовательность (Ом/фаза)

    # Сопротивления дуги для Ph-Ph
    rfpp_forward: float = 8.0  # RFFwPP - прямое направление (Ом/петля)
    rfpp_reverse: float = 4.0  # RFRvPP - обратное направление (Ом/петля)

    # Сопротивления дуги для Ph-E
    rfpe_forward: float = 12.0  # RFFwPE - прямое направление (Ом/петля)
    rfpe_reverse: float = 6.0  # RFRvPE - обратное направление (Ом/петля)

    # ===== Параметры отстройки от нагрузки (Load Encroachment) =====
    rld_forward: float = 8.0  # RLdFw - резистивная досягаемость вперед (Ом)
    rld_reverse: float = 3.0  # RLdRv - резистивная досягаемость назад (Ом)
    arg_load: float = 30.0  # ArgLd - угол нагрузки (градусы)
    load_enabled: bool = True  # Включить отстройку от нагрузки

    # ===== Параметры отображения =====
    enabled: bool = True
    color: str = '#9C27B0'
    linestyle: str = '-'
    opacity: float = 0.8
    direction_mode: str = "forward"

    def get_polygon_points(self, fault_type: str = "phph") -> List[Tuple[float, float]]:
        """Возвращает точки полигона фазового селектора"""
        # Определяем параметры в зависимости от типа КЗ
        if fault_type == "phph":
            r_forward = self.rfpp_forward
            r_reverse = self.rfpp_reverse
        else:  # phe
            r_forward = self.rfpe_forward
            r_reverse = self.rfpe_reverse

        # Базовая форма
        points = self._get_selector_base_points(r_forward, r_reverse)

        # Добавляем отстройку от нагрузки
        if self.load_enabled:
            points = self._apply_load_encroachment(points)

        return points

    def _get_selector_base_points(self, r_forward: float, r_reverse: float) -> List[Tuple[float, float]]:
        """Базовая форма фазового селектора (четырехугольник)"""
        x_reach = self.x1

        # Базовый четырехугольник
        points = [
            (r_forward / 2, x_reach),  # Верхний правый
            (r_forward / 2, 0),  # Нижний правый
            (-r_reverse / 2, 0),  # Нижний левый
            (-r_reverse / 2, x_reach),  # Верхний левый
        ]

        # Для ненаправленного - зеркальное отражение по оси R
        if self.direction_mode == "non-directional":
            mirrored = [(r, -x) for r, x in points if x > 0]
            points.extend(mirrored)

        return points

    def _apply_load_encroachment(self, points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """
        Применение отстройки от нагрузки.

        Отстройка от нагрузки работает следующим образом:
        1. Определяется линия нагрузки под углом ArgLd
        2. Все точки, попадающие в зону нагрузки, сдвигаются к границе
        """
        if not self.load_enabled:
            return points

        arg_load_rad = np.radians(self.arg_load)
        tan_load = np.tan(arg_load_rad)

        # Коэффициент запаса (чтобы зона нагрузки была немного меньше)
        margin = 0.95

        new_points = []
        for r, x in points:
            # Определяем, в каком квадранте находится точка
            if r >= 0 and x >= 0:  # I квадрант (прямое направление)
                if self.direction_mode in ["forward", "non-directional"]:
                    # Проверяем, не находится ли точка в зоне нагрузки
                    if x < r * tan_load * margin:
                        # Точка в зоне нагрузки - сдвигаем к границе
                        r_new = self.rld_forward * margin
                        x_new = r_new * tan_load * margin
                        new_points.append((r_new, x_new))
                    else:
                        new_points.append((r, x))
                else:
                    new_points.append((r, x))

            elif r < 0 and x >= 0:  # II квадрант (обратное направление)
                if self.direction_mode in ["reverse", "non-directional"]:
                    r_abs = abs(r)
                    if x < r_abs * tan_load * margin:
                        r_new = -self.rld_reverse * margin
                        x_new = abs(r_new) * tan_load * margin
                        new_points.append((r_new, x_new))
                    else:
                        new_points.append((r, x))
                else:
                    new_points.append((r, x))

            elif r < 0 and x < 0:  # III квадрант
                if self.direction_mode == "non-directional":
                    r_abs = abs(r)
                    if abs(x) < r_abs * tan_load * margin:
                        r_new = -self.rld_reverse * margin
                        x_new = -abs(r_new) * tan_load * margin
                        new_points.append((r_new, x_new))
                    else:
                        new_points.append((r, x))
                else:
                    new_points.append((r, x))

            else:  # IV квадрант (r >= 0, x < 0)
                if self.direction_mode == "non-directional":
                    if abs(x) < r * tan_load * margin:
                        r_new = self.rld_forward * margin
                        x_new = -r_new * tan_load * margin
                        new_points.append((r_new, x_new))
                    else:
                        new_points.append((r, x))
                else:
                    new_points.append((r, x))

        return new_points

    def get_load_encroachment_lines(self) -> List[Tuple[float, float, float, float]]:
        """Возвращает линии отстройки от нагрузки"""
        lines = []
        if not self.load_enabled:
            return lines

        arg_load_rad = np.radians(self.arg_load)
        max_r = max(self.rld_forward, self.rld_reverse) * 1.5
        max_x = max_r * np.tan(arg_load_rad)

        # Линия в прямом направлении (I квадрант)
        if self.direction_mode in ["forward", "non-directional"]:
            lines.append((0, 0, self.rld_forward * 1.2, self.rld_forward * 1.2 * np.tan(arg_load_rad)))

        # Линия в обратном направлении (II квадрант)
        if self.direction_mode in ["reverse", "non-directional"]:
            lines.append((0, 0, -self.rld_reverse * 1.2, self.rld_reverse * 1.2 * np.tan(arg_load_rad)))

        # Для ненаправленного - линии в III и IV квадрантах
        if self.direction_mode == "non-directional":
            lines.append((0, 0, -self.rld_reverse * 1.2, -self.rld_reverse * 1.2 * np.tan(arg_load_rad)))
            lines.append((0, 0, self.rld_forward * 1.2, -self.rld_forward * 1.2 * np.tan(arg_load_rad)))

        return lines

    def get_load_encroachment_polygon(self) -> List[Tuple[float, float]]:
        """Возвращает полигон отстройки от нагрузки для отображения"""
        if not self.load_enabled:
            return []

        arg_load_rad = np.radians(self.arg_load)
        max_r = max(self.rld_forward, self.rld_reverse) * 1.2
        max_x = max_r * np.tan(arg_load_rad)

        points = []

        # Прямое направление (I квадрант)
        if self.direction_mode in ["forward", "non-directional"]:
            r = self.rld_forward * 1.2
            x = r * np.tan(arg_load_rad)
            points.extend([
                (0, 0),
                (r, x),
                (r, 0)
            ])

        # Обратное направление (II квадрант)
        if self.direction_mode in ["reverse", "non-directional"]:
            r = -self.rld_reverse * 1.2
            x = abs(r) * np.tan(arg_load_rad)
            points.extend([
                (0, 0),
                (r, x),
                (r, 0)
            ])

        # III квадрант (для ненаправленного)
        if self.direction_mode == "non-directional":
            r = -self.rld_reverse * 1.2
            x = -abs(r) * np.tan(arg_load_rad)
            points.extend([
                (0, 0),
                (r, x),
                (r, 0)
            ])

        # IV квадрант (для ненаправленного)
        if self.direction_mode == "non-directional":
            r = self.rld_forward * 1.2
            x = -r * np.tan(arg_load_rad)
            points.extend([
                (0, 0),
                (r, x),
                (r, 0)
            ])

        return points

    def get_bounds(self) -> Tuple[float, float, float, float]:
        """Возвращает границы характеристики"""
        points = self.get_polygon_points()
        if not points:
            return (0, 0, 0, 0)

        min_r = min(p[0] for p in points)
        max_r = max(p[0] for p in points)
        min_x = min(p[1] for p in points)
        max_x = max(p[1] for p in points)

        if self.load_enabled:
            margin = max(self.rld_forward, self.rld_reverse) * 0.3
            min_r -= margin
            max_r += margin

        return (min_r, max_r, min_x, max_x)
