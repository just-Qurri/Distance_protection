# -*- coding: utf-8 -*-
"""
Модель данных для фазового селектора FDPSPDIS
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class SelectorSettings:
    """
    Модель данных для фазового селектора FDPSPDIS
    Согласно документации REL670
    """
    # Основные параметры
    x1: float = 5.0  # Positive sequence reactance reach (Ом/фаза)
    x0: float = 15.0  # Zero sequence reactance (Ом/фаза)

    # Сопротивления повреждений для Ph-Ph
    rffw_pp: float = 8.0  # RFFwPP - прямое направление
    rfrv_pp: float = 4.0  # RFRvPP - обратное направление

    # Сопротивления повреждений для Ph-E
    rffw_pe: float = 12.0  # RFFwPE - прямое направление
    rfrv_pe: float = 6.0  # RFRvPE - обратное направление

    # Параметры нагрузки
    rld_fw: float = 8.0  # RLdFw - резистивная досягаемость вперед
    rld_rv: float = -3.0  # RLdRv - резистивная досягаемость назад
    arg_ld: float = 30.0  # ArgLd - угол нагрузки

    # Минимальные токи срабатывания
    imin_op_pp: float = 10  # IMinOpPP - для Ph-Ph (% от IBase)
    imin_op_pe: float = 5  # IMinOpPE - для Ph-E (% от IBase)

    # Блокировка по току нулевой последовательности
    in_block_pp: float = 40  # INBlockPP - блокировка Ph-Ph (% от IPh)
    in_release_pe: float = 20  # INReleasePE - разрешение Ph-E (% от IPh)

    # Оформление
    enabled: bool = True
    color: str = '#9C27B0'  # Фиолетовый
    linestyle: str = '-'
    opacity: float = 0.8

    def get_polygon_points(self, fault_type: str = "phph") -> List[Tuple[float, float]]:
        """
        Возвращает точки полигона в зависимости от типа повреждения
        """
        if fault_type == "phph":
            # Используем параметры для междуфазных КЗ
            r_reach = self.r1 + self.rfpp / 2  # Активная составляющая
            x_reach = self.x1  # Реактивная составляющая
        else:  # "phe"
            # Используем параметры для однофазных КЗ
            r_reach = self.r0 + self.rfpe / 2
            x_reach = self.x0

        # Базовая форма полигона (в относительных координатах)
        # Точки: (R, X) в порядке обхода
        base_shape = [
            (0, 0),  # A - начало координат
            (-0.3, 1.0),  # B - левый верхний изгиб
            (0, 1.0),  # C - верхний левый угол
            (1.0, 1.0),  # D - верхний правый угол
            (0.8, 0),  # E - правый нижний изгиб
            (0.8, -0.3)  # F - нижняя точка
        ]

        # Масштабируем базовую форму до реальных размеров зоны
        scaled_points = [(r * r_reach, x * x_reach) for r, x in base_shape]

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

    def get_bounds(self):
        """Возвращает границы характеристики"""
        points = self.get_polygon_points()

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