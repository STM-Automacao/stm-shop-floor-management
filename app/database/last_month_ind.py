"""
Autor: Bruno Tomaz
Data: 17/01/2024
Este módulo cria dados do mês anterior.
"""

# cSpell: words eficiencia

import numpy as np
import pandas as pd
from database.connection_local import ConnectionLocal
from database.get_data import GetData
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
        with ConnectionLocal() as conn:
            # Lê os dados do DB
            try:
                df_history = conn.get_query("SELECT * FROM ind_history")
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
            eff_media = round(df_eff["eficiencia"].mean(), 3)

            # Performance Média
            perf_media = round(df_perf["performance"].mean(), 3)

            # Reparos Média
            repair_media = round(df_repair["reparo"].mean(), 3)

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

            # Como curiosidade, posso adicionar estes dados sem criar um novo dataframe
            # e sim atualizando o existente, seria assim:
            # df_historic.loc[df_historic.shape[0]] = (
            #    [last_month, total_caixas, eff_media, perf_media, repair_media, parada_programada]
            #    )
            # Para isso eu preciso adicionar na ordem correta das colunas,
            # e o index será o shape[0] que é o último index.

            # Adiciona ao DB local
            with ConnectionLocal() as conn:
                conn.update_db(df_historic, "ind_history")

        # ====================== Top 5 Motivos De Paradas E Seu Tempo Total ====================== #

        # Se motivo nome for null, substitui por "Motivo não apontado"
        df_stops["motivo"] = df_stops["motivo"].fillna("Não apontado")
        df_stops["problema"] = df_stops["problema"].fillna("Não apontado")

        # Agrupa por motivo_nome e tempo_registro_min
        df_stops_group = df_stops.groupby(["motivo", "problema"])["tempo"].sum().reset_index()
        df_stops_group = df_stops_group.sort_values(by="tempo", ascending=False).head(20)

        # Salva no DB
        with ConnectionLocal() as conn:
            conn.save_df(df_stops_group, "top_stops")

    @staticmethod
    def get_historic_data():
        """
        Retorna o histórico de dados.

        Returns:
            df_history (pd.DataFrame): DataFrame com os dados do histórico.
            top_tops (pd.DataFrame): DataFrame com os top 5 motivos de paradas.
        """

        # Cria conexão com DB local
        with ConnectionLocal() as conn:
            # Lê os dados do DB
            df_history = conn.get_query("SELECT * FROM ind_history")
            top_tops = conn.get_query("SELECT * FROM top_stops")

        return df_history, top_tops

    @staticmethod
    def get_historic_data_analysis():
        """
        Retorna o histórico de dados.

        Returns:
            df_stops (pd.DataFrame): DataFrame com os dados de paradas.
            df_working (pd.DataFrame): DataFrame com os dados de tempo de trabalho.
            df_prod (pd.DataFrame): DataFrame com os dados de produção.
        """

        # Cria conexão com DB local
        with ConnectionLocal() as conn:
            # Lê os dados do DB
            df_stops = conn.get_query("SELECT * FROM maq_stopped")
            df_working = conn.get_query("SELECT * FROM time_working")
            df_prod = conn.get_query("SELECT * FROM info_production_cleaned")

        return df_stops, df_working, df_prod
