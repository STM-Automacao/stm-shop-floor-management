"""
Modulo com tipos de dados utilizados na aplicação.
"""
from enum import Enum


class IndicatorType(Enum):
    """Indicator types"""

    PERFORMANCE = "performance"
    REPAIR = "reparo"
    EFFICIENCY = "eficiencia"


MODAL_RADIO = [
    ["NOT", "Noturno", "--bs-gray-500"],
    ["MAT", "Matutino", "--bs-gray-600"],
    ["VES", "Vespertino", "--bs-gray-900"],
]
