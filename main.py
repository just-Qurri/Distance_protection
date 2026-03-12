"""
REL670 - Интерактивный визуализатор дистанционной защиты
"""

import sys
import os
from typing import List, Optional

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.visualizer import REL670Visualizer
from models.zone_settings import ZoneSettings


def create_demo_zones(visualizer: REL670Visualizer) -> None:
    """Создание демонстрационных зон с правильными параметрами"""

    # Конфигурация зон
    zone_configs: List[dict] = [
        {
            "name": "Малая",
            "params": {
                "x1": 3.0, "r1": 1.5, "rfpp": 4.0,
                "x0": 9.0, "r0": 4.5, "rfpe": 8.0,
                "phph_scale": 0.8, "phe_scale": 1.2,
                "direction_mode": "forward",
                "enabled": True,
                "color": '#2196F3'
            }
        },
        {
            "name": "Средняя",
            "params": {
                "x1": 5.0, "r1": 2.5, "rfpp": 7.0,
                "x0": 15.0, "r0": 7.5, "rfpe": 12.0,
                "phph_scale": 1.0, "phe_scale": 1.5,
                "direction_mode": "forward",
                "enabled": True,
                "color": '#4CAF50'
            }
        },
        {
            "name": "Большая",
            "params": {
                "x1": 8.0, "r1": 4.0, "rfpp": 12.0,
                "x0": 24.0, "r0": 12.0, "rfpe": 18.0,
                "phph_scale": 1.2, "phe_scale": 1.8,
                "direction_mode": "non-directional",
                "enabled": True,
                "color": '#FF9800'
            }
        },
        {
            "name": "Обратная",
            "params": {
                "x1": 6.0, "r1": 3.0, "rfpp": 9.0,
                "x0": 18.0, "r0": 9.0, "rfpe": 15.0,
                "phph_scale": 1.0, "phe_scale": 1.5,
                "direction_mode": "reverse",
                "enabled": True,
                "color": '#F44336'
            }
        },
        {
            "name": "Дальняя",
            "params": {
                "x1": 10.0, "r1": 5.0, "rfpp": 15.0,
                "x0": 30.0, "r0": 15.0, "rfpe": 22.0,
                "phph_scale": 1.3, "phe_scale": 2.0,
                "direction_mode": "forward",
                "enabled": True,
                "color": '#9C27B0'
            }
        }
    ]

    for config in zone_configs:
        visualizer.add_zone(ZoneSettings(
            name=config["name"],
            **config["params"]  # Распаковка параметров
        ))


if __name__ == "__main__":
    visualizer = REL670Visualizer("REL670 - Дистанционная защита")
    create_demo_zones(visualizer)
    visualizer.show()