"""
Модель данных для блокировки от качаний ZMRPSB
"""

from dataclasses import dataclass


@dataclass
class SwingBlockingSettings:
    """
    Уставки блокировки от качаний
    """
    # Внутренняя зона качаний (ZIN)
    x1_in_fw: float = 37.0
    r1_li_n: float = 37.0
    r1_f_in_fw: float = 37.0
    x1_in_rv: float = 37.0
    r1_f_in_rv: float = 37.0

    # Внешняя зона качаний (ZOUT)
    rld_out_fw: float = 55.0
    rld_out_rv: float = 200.0

    # Параметры нагрузки
    operation_ld_ch: bool = False
    arg_ld: float = 25.0

    # Коэффициенты для определения границ
    k_Ld_r_fw: float = 0.8
    k_ld_r_rv: float = 0.75

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
