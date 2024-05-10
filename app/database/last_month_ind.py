"""
Autor: Bruno Tomaz
Data: 17/01/2024
Este módulo cria dados do mês anterior.
"""

# cSpell: words eficiencia

import sqlite3

import numpy as np
import pandas as pd
from database.get_data import GetData
from helpers.path_config import DB_LOCAL
from service.data_analysis import DataAnalysis


class LastMonthInd:
    """
    Essa classe é responsável por salvar imagens de gauge do mês anterior.
    """

    def __init__(self):
        self.get_data = GetData()
        self.data_analysis = DataAnalysis

    def save_last_month_data(self):
        """
        Salva imagens de gauge do mês anterior.
        """
        # Leitura dos dados
        df_stops, df_prod = self.get_data.get_last_month_data_cleaned()

        # Instancia de analise de dados
        data_analysis = self.data_analysis(df_stops, df_prod)

        # Tratamento dos dados
        df_eff = data_analysis.get_eff_data()
        df_perf = data_analysis.get_perf_data()
        df_repair = data_analysis.get_repair_data()

        # ================================= Conexão Com DB Local ================================= #
        # Cria conexão com DB local. Se não existir cria um.
        conn = sqlite3.connect(DB_LOCAL)

        # Lê os dados do DB
        try:
            df_history = pd.read_sql_query("SELECT * FROM ind_history", conn)
        except pd.io.sql.DatabaseError:
            df_history = pd.DataFrame(
                columns=[
                    "data_registro",
                    "total_caixas",
                    "eficiencia",
                    "performance",
                    "reparo",
                    "parada_programada",
                ]
            )

        # =================== Verifica Se O Mês Já Está No DB, Se Não Adiciona =================== #

        # Seleciona Mês passado
        last_month = (pd.Timestamp.now() - pd.DateOffset(months=1)).strftime("%Y-%m")

        # Verifica se já existe o mês no histórico
        if last_month not in df_history["data_registro"].values:

            # Total de Caixas Produzidas
            total_caixas = int(np.floor((df_prod["total_produzido"].sum()) / 10))

            # Eficiência Média
            eff_media = round(df_eff["eficiencia"].mean())

            # Performance Média
            perf_media = round(df_perf["performance"].mean())

            # Reparos Média
            repair_media = round(df_repair["reparo"].mean())

            # Parada Programada - Tempo Total
            df_info_programada = df_stops[df_stops["causa"].isin(["Sem Produção", "Backup"])]
            parada_programada = df_info_programada["tempo"].sum()

            # Criação do DataFrame
            df_historic = pd.DataFrame(
                {
                    "data_registro": [last_month],
                    "total_caixas": [total_caixas],
                    "eficiencia": [eff_media],
                    "performance": [perf_media],
                    "reparo": [repair_media],
                    "parada_programada": [parada_programada],
                }
            )

            # Adiciona ao DB local
            df_historic.to_sql("ind_history", conn, if_exists="append", index=False)

        # ====================== Top 5 Motivos De Paradas E Seu Tempo Total ====================== #

        # Se motivo nome for null, substitui por "Motivo não apontado"
        df_stops["motivo"] = df_stops["motivo"].fillna("Não apontado")
        df_stops["problema"] = df_stops["problema"].fillna("Não apontado")

        # Agrupa por motivo_nome e tempo_registro_min
        df_stops_group = df_stops.groupby(["motivo", "problema"])["tempo"].sum()
        df_stops_group = df_stops_group.sort_values(ascending=False).head(20)

        # Salva no DB
        df_stops_group.to_sql("top_stops", conn, if_exists="replace", index=True)

        # Fecha conexão
        conn.close()

    @staticmethod
    def get_historic_data():
        """
        Retorna o histórico de dados.

        Returns:
            df_history (pd.DataFrame): DataFrame com os dados do histórico.
            top_tops (pd.DataFrame): DataFrame com os top 5 motivos de paradas.
        """

        # Cria conexão com DB local
        conn = sqlite3.connect(DB_LOCAL)

        # Lê os dados do DB
        df_history = pd.read_sql_query("SELECT * FROM ind_history", conn)
        top_tops = pd.read_sql_query("SELECT * FROM top_stops", conn)

        return df_history, top_tops
