"""
Modulo com tipos de dados utilizados na aplicação.
"""

# cSpell: words eficiencia cmap
from enum import Enum

import matplotlib.pyplot as plt

CICLOS_ESPERADOS = 10.6


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


class TemplateType(Enum):
    """Template types"""

    LIGHT = "bootstrap"
    DARK = "darkly"


# Usado nos dados ao vivo do 'grafana'
def get_color(value, max_value):
    """
    Retorna uma cor hexadecimal com base no valor fornecido e no valor máximo.
        Cor varia do vermelho ao verde.

    Parâmetros:
    value (float): O valor para o qual a cor será calculada.
    max_value (float): O valor máximo possível.

    Retorna:
    str: Uma cor hexadecimal correspondente ao valor fornecido.
    """

    # Cria um mapa de cores que vai do vermelho ao verde
    cmap = plt.get_cmap("RdYlGn")

    # Normaliza o valor para um número entre 0 e 1
    normalized_value = float(value) / max_value

    # Obtém a cor correspondente do mapa de cores
    rgba_color = cmap(normalized_value)

    # Converte a cor RGBA para uma string de cor hexadecimal
    hex_color = (
        f"#{int(rgba_color[0]*255):02x}{int(rgba_color[1]*255):02x}{int(rgba_color[2]*255):02x}"
    )

    return hex_color


COLOR_DICT = {
    "Parada de 5 minutos ou menos": BSColorsEnum.GREY_600_COLOR.value,
    "Não apontado": BSColorsEnum.WARNING_COLOR.value,
    "Ajustes": BSColorsEnum.TEAL_COLOR.value,
    "Manutenção": BSColorsEnum.SPACE_CADET_COLOR.value,
    "Qualidade": BSColorsEnum.INFO_COLOR.value,
    "Fluxo": BSColorsEnum.PINK_COLOR.value,
    "Parada Programada": BSColorsEnum.DANGER_COLOR.value,
    "Setup": BSColorsEnum.BLUE_DELFT_COLOR.value,
    "Limpeza": BSColorsEnum.PRIMARY_COLOR.value,
    "Rodando": BSColorsEnum.SUCCESS_COLOR.value,
}
