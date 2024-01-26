"""
Modulo com tipos de dados utilizados na aplicação.
"""
from enum import Enum


class IndicatorType(Enum):
    """Indicator types"""

    PERFORMANCE = "performance"
    REPAIR = "reparos"
    EFFICIENCY = "eficiencia"


MODAL_RADIO = [
    ["NOT", "Noturno", "red"],
    ["MAT", "Matutino", "green"],
    ["VES", "Vespertino", "yellow"],
]
