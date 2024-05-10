"""
Modulo para configurar os caminhos dos arquivos de dados (Gambiarra)
"""

import os

# Gambiarra para acessar arquivos
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
ASSETS_DIR = os.path.join(PARENT_DIR, "assets")

# Arquivos de dados
EFF_LAST = os.path.join(ASSETS_DIR, "df_eff_last_month.csv")
PERF_LAST = os.path.join(ASSETS_DIR, "df_perf_last_month.csv")
REPAIR_LAST = os.path.join(ASSETS_DIR, "df_repair_last_month.csv")
FERIADOS = os.path.join(ASSETS_DIR, "feriados.csv")
TOP_STOPS = os.path.join(ASSETS_DIR, "top_stops.csv")
DF_HISTORY = os.path.join(ASSETS_DIR, "df_history.csv")
DF_CAIXAS = os.path.join(ASSETS_DIR, "df_caixas.csv")
DB_LOCAL = os.path.join(ASSETS_DIR, "db_for_historic.db")
