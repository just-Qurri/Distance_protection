"""
Настройки реле - конфигурация демо-зон для REL670
"""
from models.zone_calculation import DZSettings


class RelaySettings:

    @staticmethod
    def create_DZ_zones(visualizer):
        """Создание зон с правильными параметрами"""
        # Зона 1:
        visualizer.add_zone(DZSettings(
            x1=3.0,
            r1=1.5,
            rfpp=5.0,
            x0=9.0,
            r0=4.5,
            rfpe=8.0,
            direction_mode="forward",
            name="Первая зона",
            enabled=True,
            color='#000000',
            phase_selector_enabled=False,
            load_enabled=False
        ))

        # Зона 2:
        visualizer.add_zone(DZSettings(
            x1=5.0,
            r1=2.5,
            rfpp=7.0,
            x0=15.0,
            r0=7.5,
            rfpe=12.0,
            direction_mode="forward",
            name="Вторая зона",
            enabled=True,
            color='#4CAF50',
            phase_selector_enabled=False,
            load_enabled=False

        ))

        # Зона 3:
        visualizer.add_zone(DZSettings(
            x1=8.0,
            r1=4.0,
            rfpp=12.0,
            x0=24.0,
            r0=12.0,
            rfpe=18.0,
            direction_mode="non-directional",
            name="Третья зона",
            enabled=True,
            color='#FF9800',
            phase_selector_enabled=False,
            load_enabled=False
        ))

        # Зона 4:
        visualizer.add_zone(DZSettings(
            x1=6.0,
            r1=3.0,
            rfpp=9.0,
            x0=18.0,
            r0=9.0,
            rfpe=15.0,
            direction_mode="reverse",
            name="Четвертая зона",
            enabled=True,
            color='#F44336',
            phase_selector_enabled=False,
            load_enabled=False
        ))

        # Зона 5:
        visualizer.add_zone(DZSettings(
            x1=10.0,
            r1=5.0,
            rfpp=15.0,
            x0=30.0,
            r0=15.0,
            rfpe=22.0,
            direction_mode="forward",
            name="Пятая зона",
            enabled=True,
            color='#9C27B0',
            phase_selector_enabled=False,
            load_enabled=False
        ))
