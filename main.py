"""
REL670 - Интерактивный визуализатор дистанционной защиты
Основан на технической документации ABB REL670
"""

import os
import sys

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.visualizer import REL670Visualizer
from ui.main_settings import RelaySettings

if __name__ == "__main__":
    visualizer = REL670Visualizer("REL670 - Дистанционная защита")
    RelaySettings.create_common_settings(visualizer)
    RelaySettings.create_DZ_zones(visualizer)
    RelaySettings.create_PHS(visualizer)

    visualizer.show()
