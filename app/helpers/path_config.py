"""
Modulo para configurar os caminhos dos arquivos de dados (Gambiarra)
"""

# cSpell: words lider
import os
from enum import Enum

# Gambiarra para acessar arquivos
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
ASSETS_DIR = os.path.join(PARENT_DIR, "assets")

# Arquivos de dados
DF_CAIXAS = os.path.join(ASSETS_DIR, "df_caixas.csv")
DB_LOCAL = os.path.join(ASSETS_DIR, "db_for_historic.db")


# Urls
class UrlPath(Enum):
    """
    Enum class representing the URL paths for different roles.

    Attributes:
        LÍDER (int): The URL path for the role "LÍDER".
        SUPERVISOR (int): The URL path for the role "SUPERVISOR".
        COORDENADOR (int): The URL path for the role "COORDENADOR".
        PCP (str): The URL path for the role "PCP".
        MAIN (int): The URL path for the role "MAIN".
    """

    LIDER = 98334
    SUPERVISOR = 2703448294
    COORDENADOR = 39943361394
    PCP = "030"
    MAIN = 7186
