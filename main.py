"""
Главный файл запуска приложения REL670 Visualizer
"""

from models.calculation_points import CalculationPointsSettings
from models.common_settings import CommonSettings
from models.swing_blocking import SwingBlockingSettings
from models.zone_default_parameters import RelaySettings
from ui.visualizer import Visualizer


def main():
    """Точка входа в приложение"""
    app = Visualizer("Дистанционная защита")

    # Создаем настройки
    RelaySettings.create_DZ_zones(app)
    CommonSettings.create_and_add(app)

    # Добавляем настройки блокировки от качаний
    app.swing_settings = SwingBlockingSettings()

    # Добавляем настройки расчетных точек
    app.points_settings = CalculationPointsSettings()

    # Запускаем приложение
    app.show()


if __name__ == "__main__":
    main()
