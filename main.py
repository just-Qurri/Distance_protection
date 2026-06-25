"""
Главный файл запуска приложения REL670 Visualizer
"""

from models.calculation_points import CalculationPointsSettings
from models.swing_blocking import SwingBlockingSettings
from ui.main_settings import RelaySettings
from ui.visualizer import REL670Visualizer


def main():
    """Точка входа в приложение"""
    app = REL670Visualizer("REL670 - Дистанционная защита")

    # Создаем настройки
    RelaySettings.create_common_settings(app)
    RelaySettings.create_DZ_zones(app)

    # Добавляем настройки блокировки от качаний
    app.swing_settings = SwingBlockingSettings()

    # Добавляем настройки расчетных точек
    app.points_settings = CalculationPointsSettings()

    # Запускаем приложение
    app.show()


if __name__ == "__main__":
    main()
