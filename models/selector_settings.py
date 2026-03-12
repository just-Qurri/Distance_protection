# -*- coding: utf-8 -*-
"""
Модель данных для фазового селектора FDPSPDIS
"""

import numpy as np
from dataclasses import dataclass


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

    def get_polygon_points(self):
        """
        Возвращает единую полигональную характеристику фазового селектора
        Объединяет все 6 измерительных контуров в одну фигуру
        """
        points = []

        # Угол характеристики (рекомендуемый 60°)
        angle_rad = np.radians(60)

        # Эффективное реактивное сопротивление
        x_effective = (2 * self.x1 + self.x0) / 3

        # 1. Верхняя часть (прямое направление, Ph-Ph)
        r1 = self.rffw_pp * np.cos(angle_rad)
        x1 = self.rffw_pp * np.sin(angle_rad)
        points.append([r1, x1])

        # 2. Верхняя часть (прямое направление, Ph-E)
        r2 = self.rffw_pe * np.cos(angle_rad)
        x2 = self.rffw_pe * np.sin(angle_rad)
        points.append([r2, x2])

        # 3. Точка на положительной оси X
        points.append([self.rld_fw, 0])

        # 4. Нижняя часть (обратное направление, Ph-E)
        r3 = self.rfrv_pe * np.cos(-angle_rad)
        x3 = self.rfrv_pe * np.sin(-angle_rad)
        points.append([r3, x3])

        # 5. Нижняя часть (обратное направление, Ph-Ph)
        r4 = self.rfrv_pp * np.cos(-angle_rad)
        x4 = self.rfrv_pp * np.sin(-angle_rad)
        points.append([r4, x4])

        # 6. Точка на отрицательной оси X
        points.append([self.rld_rv, 0])

        # Замыкаем полигон
        points.append(points[0])

        return points

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