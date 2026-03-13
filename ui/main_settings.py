"""
Настройки реле - конфигурация демо-зон для REL670
"""
from models.zone_settings import DZ_Settings, PHS_Settings, Common_Settings


class RelaySettings:

    @staticmethod
    def create_DZ_zones(visualizer):
        """Создание зон с правильными параметрами"""
        # Зона 1:
        visualizer.add_zone(DZ_Settings(
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
        ))

        # Зона 2:
        visualizer.add_zone(DZ_Settings(
            x1=5.0,
            r1=2.5,
            rfpp=7.0,
            x0=15.0,
            r0=7.5,
            rfpe=12.0,
            direction_mode="forward",
            name="Вторая зона",
            enabled=True,
            color='#4CAF50'
        ))

        # Зона 3:
        visualizer.add_zone(DZ_Settings(
            x1=8.0,
            r1=4.0,
            rfpp=12.0,
            x0=24.0,
            r0=12.0,
            rfpe=18.0,
            direction_mode="non-directional",
            name="Третья зона",
            enabled=True,
            color='#FF9800'
        ))

        # Зона 4:
        visualizer.add_zone(DZ_Settings(
            x1=6.0,
            r1=3.0,
            rfpp=9.0,
            x0=18.0,
            r0=9.0,
            rfpe=15.0,
            direction_mode="reverse",
            name="Четвертая зона",
            enabled=True,
            color='#F44336'
        ))

        # Зона 5:
        visualizer.add_zone(DZ_Settings(
            x1=10.0,
            r1=5.0,
            rfpp=15.0,
            x0=30.0,
            r0=15.0,
            rfpe=22.0,
            direction_mode="forward",
            name="Пятая зона",
            enabled=True,
            color='#9C27B0'
        ))

    @staticmethod
    def create_PHS(visualizer):
        visualizer.add_phs(PHS_Settings(
            rld_forward=96,
            rld_reverse=96,
            angle_load=35,
            x1=10.0,
            x0=30.0,
            rfpp_forward=5.0,
            rfpp_reverse=5.0,
            rfpe_forward=6.0,
            rfpe_reverse=6.0,
            direction_mode="forward",
            name="Фазовый селектор (PHS)",
            load_enabled=True,
            enabled=True,
            color='#9C27B0'
        ))

    @staticmethod
    def create_common_settings(visualizer):
        visualizer.add_common_settings(Common_Settings(
            u_base=115000,
            i_base=600,
            i_secondary=5.0,
            u_secondary=100.0,
            angle_quad2=-15.0,
            angle_quad4=115.0,
            angle_phs=60.0,
            name="Общие настройки (U, I, angles)",
            color='#9C27B0'
        ))
