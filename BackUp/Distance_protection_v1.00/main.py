import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.visualizer import REL670Visualizer


def create_demo_zones(visualizer):
    """Создание демонстрационных зон с правильными углами"""
    from models.zone_settings import ZoneSettings

    # Зона 1: Малая
    visualizer.add_zone(ZoneSettings(
        x1=3.0, r1=1.5, rfpp=4.0,
        x0=9.0, r0=4.5, rfpe=8.0,
        angle_quad2=115.0, angle_quad4=-15.0,  # Углы для зон защиты
        selector_angle=60.0,  # Угол для фазового селектора
        rffw_pp=5.0, rfrv_pp=2.5,
        rffw_pe=8.0, rfrv_pe=4.0,
        rca=75.0,
        direction_mode="forward",
        name="Малая", enabled=True,
        show_selector=True
    ))

    # Зона 2: Средняя
    visualizer.add_zone(ZoneSettings(
        x1=5.0, r1=2.5, rfpp=7.0,
        x0=15.0, r0=7.5, rfpe=12.0,
        angle_quad2=115.0, angle_quad4=-15.0,
        selector_angle=60.0,
        rffw_pp=8.0, rfrv_pp=4.0,
        rffw_pe=12.0, rfrv_pe=6.0,
        rca=75.0,
        direction_mode="forward",
        name="Средняя", enabled=True,
        show_selector=True
    ))

    # Зона 3: Большая ненаправленная
    visualizer.add_zone(ZoneSettings(
        x1=8.0, r1=4.0, rfpp=12.0,
        x0=24.0, r0=12.0, rfpe=18.0,
        angle_quad2=115.0, angle_quad4=-15.0,
        selector_angle=60.0,
        rffw_pp=12.0, rfrv_pp=6.0,
        rffw_pe=18.0, rfrv_pe=9.0,
        rca=75.0,
        direction_mode="non-directional",
        name="Большая", enabled=True,
        show_selector=True
    ))

    # Зона 4: Обратного направления
    visualizer.add_zone(ZoneSettings(
        x1=6.0, r1=3.0, rfpp=9.0,
        x0=18.0, r0=9.0, rfpe=15.0,
        angle_quad2=115.0, angle_quad4=-15.0,
        selector_angle=60.0,
        rffw_pp=10.0, rfrv_pp=5.0,
        rffw_pe=15.0, rfrv_pe=7.5,
        rca=75.0,
        direction_mode="reverse",
        name="Обратная", enabled=True,
        show_selector=True
    ))

    # Зона 5: Дальняя
    visualizer.add_zone(ZoneSettings(
        x1=10.0, r1=5.0, rfpp=15.0,
        x0=30.0, r0=15.0, rfpe=22.0,
        angle_quad2=115.0, angle_quad4=-15.0,
        selector_angle=60.0,
        rffw_pp=15.0, rfrv_pp=7.5,
        rffw_pe=22.0, rfrv_pe=11.0,
        rca=75.0,
        direction_mode="forward",
        name="Дальняя", enabled=True,
        show_selector=True
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
    print("╚" + "═" * 78 + "╝")


if __name__ == "__main__":
    print_header()
    visualizer = REL670Visualizer("REL670 - Дистанционная защита с фазовым селектором")
    create_demo_zones(visualizer)
    visualizer.show()