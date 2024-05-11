"""
Modulo para configurar os caminhos dos arquivos de dados (Gambiarra)
"""

import os

# Gambiarra para acessar arquivos
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
ASSETS_DIR = os.path.join(PARENT_DIR, "assets")

# Arquivos de dados
DF_CAIXAS = os.path.join(ASSETS_DIR, "df_caixas.csv")
DB_LOCAL = os.path.join(ASSETS_DIR, "db_for_historic.db")
