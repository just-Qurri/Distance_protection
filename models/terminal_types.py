"""
Типы терминалов и их параметры
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class TerminalType:
    """Модель типа терминала"""
    name: str
    code: str
    description: str
    # Коэффициенты для расчета зон
    k_zin: float = 0.8  # Коэффициент для внутренней зоны качаний
    k_zout: float = 1.2  # Коэффициент для внешней зоны качаний
    # Параметры по умолчанию для блокировки от качаний
    default_x1: float = 37.0
    default_rfpp: float = 164.0
    default_rfpe: float = 135.0


# Предопределенные типы терминалов
TERMINAL_TYPES: Dict[str, TerminalType] = {
    "rel670": TerminalType(
        name="REL670/RED670",
        code="rel670",
        description="Дистанционная защита REL670/RED670",
        k_zin=0.8,
        k_zout=1.2,
        default_x1=37.0,
        default_rfpp=164.0,
        default_rfpe=135.0
    ),
    "mr771": TerminalType(
        name="МР771",
        code="mr771",
        description="Микропроцессорное реле МР771",
        k_zin=0.75,
        k_zout=1.25,
        default_x1=35.0,
        default_rfpp=150.0,
        default_rfpe=120.0
    ),
    "tor300": TerminalType(
        name="ТОР300",
        code="tor300",
        description="Терминал ТОР300",
        k_zin=0.82,
        k_zout=1.18,
        default_x1=40.0,
        default_rfpp=170.0,
        default_rfpe=140.0
    )
}


def get_terminal_type(code: str) -> Optional[TerminalType]:
    """Получить тип терминала по коду"""
    return TERMINAL_TYPES.get(code)


def get_terminal_names() -> List[str]:
    """Получить список имен терминалов"""
    return [t.name for t in TERMINAL_TYPES.values()]
