"""
Модель данных для фазового селектора FDPSPDIS
"""

from dataclasses import dataclass, field


@dataclass
class SelectorSettings:
    """
    Модель данных для фазового селектора FDPSPDIS
    """
    # Параметры фазового селектора
    x1: float = 37.0
    x0: float = 43.0
    rfpp_forward: float = 164.0
    rfpp_reverse: float = 164.0
    rfpe_forward: float = 135.0
    rfpe_reverse: float = 135.0

    # Параметры отстройки от нагрузки
    rld_forward: float = 96.0
    rld_reverse: float = 96.0
    arg_load: float = 35.0
    arg_load_phph: float = 30.0
    arg_load_3ph: float = 30.0
    load_enabled: bool = True

    # Параметры отображения
    enabled: bool = True
    color: str = '#9C27B0'
    linestyle: str = '-'
    opacity: float = 0.8
    direction_mode: str = "non-directional"
    type: str = field(default="selector", init=False)
