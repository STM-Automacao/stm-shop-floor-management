"""
Modulo com tipos de dados utilizados na aplicação.
"""
from enum import Enum


class IndicatorType(Enum):
    """Indicator types"""

    PERFORMANCE = "performance"
    REPAIR = "reparos"
    EFFICIENCY = "eficiencia"
