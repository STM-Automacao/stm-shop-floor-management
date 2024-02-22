"""
Modulo com tipos de dados utilizados na aplicação.
"""

# cSpell: words eficiencia cmap
from enum import Enum

import matplotlib.pyplot as plt


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


def get_color(value, max_value):
    # Cria um mapa de cores que vai do vermelho ao verde
    cmap = plt.get_cmap("RdYlGn")

    # Normaliza o valor para um número entre 0 e 1
    normalized_value = float(value) / max_value

    # Obtém a cor correspondente do mapa de cores
    rgba_color = cmap(normalized_value)

    # Converte a cor RGBA para uma string de cor hexadecimal
    hex_color = "#%02x%02x%02x" % (
        int(rgba_color[0] * 255),
        int(rgba_color[1] * 255),
        int(rgba_color[2] * 255),
    )

    return hex_color
