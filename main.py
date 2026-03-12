#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REL670 - Интерактивный визуализатор дистанционной защиты
Основан на технической документации ABB REL670
"""

import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.visualizer import REL670Visualizer
from models.zone_settings import ZoneSettings


def create_demo_zones(visualizer):
    """Создание демонстрационных зон с правильными параметрами"""

    # Зона 1: Малая
    visualizer.add_zone(ZoneSettings(
        x1=3.0, r1=1.5, rfpp=4.0,
        x0=9.0, r0=4.5, rfpe=8.0,
        phph_scale=0.8,
        phe_scale=1.2,
        direction_mode="forward",
        name="Малая",
        enabled=True,
        color='#2196F3'
    ))

    # Зона 2: Средняя
    visualizer.add_zone(ZoneSettings(
        x1=5.0, r1=2.5, rfpp=7.0,
        x0=15.0, r0=7.5, rfpe=12.0,
        phph_scale=1.0,
        phe_scale=1.5,
        direction_mode="forward",
        name="Средняя",
        enabled=True,
        color='#4CAF50'
    ))

    # Зона 3: Большая ненаправленная
    visualizer.add_zone(ZoneSettings(
        x1=8.0, r1=4.0, rfpp=12.0,
        x0=24.0, r0=12.0, rfpe=18.0,
        phph_scale=1.2,
        phe_scale=1.8,
        direction_mode="non-directional",
        name="Большая",
        enabled=True,
        color='#FF9800'
    ))

    # Зона 4: Обратного направления
    visualizer.add_zone(ZoneSettings(
        x1=6.0, r1=3.0, rfpp=9.0,
        x0=18.0, r0=9.0, rfpe=15.0,
        phph_scale=1.0,
        phe_scale=1.5,
        direction_mode="reverse",
        name="Обратная",
        enabled=True,
        color='#F44336'
    ))

    # Зона 5: Дальняя
    visualizer.add_zone(ZoneSettings(
        x1=10.0, r1=5.0, rfpp=15.0,
        x0=30.0, r0=15.0, rfpe=22.0,
        phph_scale=1.3,
        phe_scale=2.0,
        direction_mode="forward",
        name="Дальняя",
        enabled=True,
        color='#9C27B0'
    ))


def print_header():
    """Вывод заголовка программы"""
    print("╔" + "═" * 78 + "╗")
    print("║" + "REL670 - Интерактивный визуализатор уставок".center(78) + "║")
    print("╠" + "═" * 78 + "╣")
    print("║ • 5 независимых зон с изменяемыми параметрами".ljust(79) + "║")
    print("║ • Параметры Ph-Ph: X₁, R₁, RFPP".ljust(79) + "║")
    print("║ • Параметры Ph-E: X₀, R₀, RFPE".ljust(79) + "║")
    print("║ • Углы для зон защиты: 115° (2-й кв.) и -15° (4-й кв.)".ljust(79) + "║")
    print("║ • Фазовый селектор: угол 60°, ненаправленная характеристика".ljust(79) + "║")
    print("║ • Направленность: Прямое ↑, Обратное ↓, Ненаправленное ↕".ljust(79) + "║")
    print("║ • Переключатель между Ph-Ph, Ph-E и фазовым селектором".ljust(79) + "║")
    print("║ • Масштабирование: колесо мыши / кнопки + -".ljust(79) + "║")
    print("║ • Перемещение: зажать левую кнопку мыши".ljust(79) + "║")
    print("║ • Маркеры: захват в радиусе 50px".ljust(79) + "║")
    print("╚" + "═" * 78 + "╝")


if __name__ == "__main__":
    print_header()
    visualizer = REL670Visualizer("REL670 - Дистанционная защита")
    create_demo_zones(visualizer)
    visualizer.show()