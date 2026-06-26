"""
Модель для расчетных точек пересечений характеристик
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class CalculationPoint:
    """Модель расчетной точки пересечения"""
    name: str
    r: float
    x: float
    color: str = '#E91E63'
    enabled: bool = False
    description: str = ""


@dataclass
class CalculationPointsSettings:
    """
    Настройки расчетных точек пересечений
    """
    points: List[CalculationPoint] = field(default_factory=list)
    enabled: bool = True
    show_labels: bool = True
    marker_size: float = 8.0

    def add_point(self, name: str, r: float, x: float, description: str = "") -> None:
        """Добавить расчетную точку"""
        self.points.append(CalculationPoint(name, r, x, description=description))

    def remove_point(self, index: int) -> None:
        """Удалить расчетную точку"""
        if 0 <= index < len(self.points):
            del self.points[index]

    def get_point(self, index: int) -> Optional[CalculationPoint]:
        """Получить расчетную точку по индексу"""
        if 0 <= index < len(self.points):
            return self.points[index]
        return None
