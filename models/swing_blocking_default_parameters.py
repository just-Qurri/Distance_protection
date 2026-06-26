"""
Модель данных для блокировки от качаний ZMRPSB
"""

from dataclasses import dataclass


@dataclass
class SwingBlockingSettings:
    """
    Настройки блокировки от качаний
    """
    # Внутренняя зона качаний (ZIN)
    x1_zin: float = 37.0
    rfpp_zin: float = 164.0
    rfpe_zin: float = 135.0

    # Внешняя зона качаний (ZOUT)
    x1_zout: float = 55.0
    rfpp_zout: float = 200.0
    rfpe_zout: float = 180.0

    # Отстройка от нагрузки для ZIN
    rld_forward_zin: float = 96.0
    rld_reverse_zin: float = 96.0
    arg_load_zin: float = 35.0

    # Отстройка от нагрузки для ZOUT
    rld_forward_zout: float = 80.0
    rld_reverse_zout: float = 80.0
    arg_load_zout: float = 30.0

    # Общие параметры
    load_enabled: bool = True
    enabled: bool = True
    color_zin: str = '#FF5722'
    color_zout: str = '#FF9800'
    linestyle_zin: str = '-'
    linestyle_zout: str = '-'
    opacity_zin: float = 0.6
    opacity_zout: float = 0.4
    show_zin: bool = True
    show_zout: bool = True
