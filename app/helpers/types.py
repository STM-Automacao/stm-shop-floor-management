"""
Modulo com tipos de dados utilizados na aplicação.
"""

# cSpell: words eficiencia
from enum import Enum


class IndicatorType(Enum):
    """Indicator types"""

    PERFORMANCE = "performance"
    REPAIR = "reparo"
    EFFICIENCY = "eficiencia"


class BSColorsEnum(Enum):
    """Bootstrap colors"""

    PRIMARY_COLOR = "#0d6efd"
    SECONDARY_COLOR = "#6c757d"
    SUCCESS_COLOR = "#198754"
    WARNING_COLOR = "#ffc107"
    DANGER_COLOR = "#dc3545"
    INFO_COLOR = "#0dcaf0"
    TEAL_COLOR = "#20c997"
    INDIGO_COLOR = "#6610f2"
    GRAY_COLOR = "#adb5bd"
    GREY_400_COLOR = "#ced4da"
    GREY_500_COLOR = "#adb5bd"
    GREY_600_COLOR = "#6c757d"
    GREY_700_COLOR = "#495057"
    GREY_800_COLOR = "#343a40"
    GREY_900_COLOR = "#212529"
    ORANGE_COLOR = "#fd7e14"
    PINK_COLOR = "#d63384"
    PURPLE_COLOR = "#6f42c1"
    SPACE_CADET_COLOR = "#282f44"
    BLUE_DELFT_COLOR = "#353e5a"


MODAL_RADIO = [
    ["NOT", "Noturno", "red"],
    ["MAT", "Matutino", "red"],
    ["VES", "Vespertino", "red"],
    ["TOT", "Total", "orange"],
]
