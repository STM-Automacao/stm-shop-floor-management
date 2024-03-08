"""
Autor: Bruno Tomaz
Data: 17/01/2024
Este módulo cria dados do mês anterior.
"""

# cSpell: words eficiencia

import numpy as np
import pandas as pd

# pylint: disable=E0401
from database.get_data import GetData
from helpers.path_config import DF_HISTORY, EFF_LAST, PERF_LAST, REPAIR_LAST, TOP_STOPS
from service.times_data import TimesData


class LastMonthInd:
    """
    Essa classe é responsável por salvar imagens de gauge do mês anterior.
    """

    def __init__(self):
        self.times_data = TimesData()
        self.get_data = GetData()

    def save_last_month_data(self):
        """
        Salva imagens de gauge do mês anterior.
        """
        # Leitura dos dados
        df_info, df_prod = self.get_data.get_last_month_data()

        # Tratamento dos dados
        df_eff = self.times_data.get_eff_data(df_info, df_prod)
        df_perf = self.times_data.get_perf_data(df_info, df_prod)
        df_repair = self.times_data.get_repair_data(df_info, df_prod)

        # Salva os dataframes em csv
        df_eff.to_csv(EFF_LAST)
        df_perf.to_csv(PERF_LAST)
        df_repair.to_csv(REPAIR_LAST)
        print("========== Salvo dados Último Mês ==========")

        # ---------- Histórico de Dados ---------- #
        try:
            df_history = pd.read_csv(DF_HISTORY)
        except FileNotFoundError:
            df_history = pd.DataFrame(
                columns=[
                    "data_registro",
                    "total_caixas",
                    "eficiencia_media",
                    "performance_media",
                    "reparos_media",
                    "parada_programada",
                ]
            )

        # Seleciona Mês passado
        last_month = (pd.Timestamp.now() - pd.DateOffset(months=1)).strftime("%Y-%m")

        # Verifica se já existe o mês no histórico
        if last_month in df_history["data_registro"].values:
            print("Mês já registrado")
        else:
            # Total de Caixas Produzidas
            total_caixas = int(np.floor((df_prod["total_produzido"].sum()) / 10))

            # Eficiência Média
            eff_media = round(df_eff["eficiencia"].mean() * 100)

            # Performance Média
            perf_media = round(df_perf["performance"].mean() * 100)

            # Reparos Média
            repair_media = round(df_repair["reparo"].mean() * 100)

            # Parada Programada - Tempo Total
            df_info_programada = df_info[df_info["motivo_id"] == 12]
            parada_programada = df_info_programada["tempo_registro_min"].sum()

            # Criação do DataFrame
            df_historic = pd.DataFrame(
                {
                    "data_registro": [last_month],
                    "total_caixas": [total_caixas],
                    "eficiencia_media": [eff_media],
                    "performance_media": [perf_media],
                    "reparos_media": [repair_media],
                    "parada_programada": [parada_programada],
                }
            )

            # Salva no histórico
            df_history = pd.concat([df_history, df_historic], ignore_index=True)

            # Salva o histórico
            df_history.to_csv(DF_HISTORY, index=False)

            print("========= Mês passado registrado no histórico =========")

        # ------- Top 5 motivos de paradas e seu tempo total ------ #
        # Se motivo nome for null, substitui por "Motivo não apontado"
        df_info["motivo_nome"] = df_info["motivo_nome"].fillna("Motivo não apontado")
        df_info["problema"] = df_info["problema"].fillna("Problema não apontado")
        df_info["problema"] = np.where(
            df_info["problema"] == "None", "Problema não apontado", df_info["problema"]
        )
        # Se o motivo_id for 12 e o problema for motivo não apontado, substitui "Parada Programada"
        df_info["problema"] = np.where(
            (df_info["motivo_id"] == 12) & (df_info["problema"] == "Problema não apontado"),
            "Parada Programada",
            df_info["problema"],
        )

        # Encontra o problema 'Parada programada' e substitui por 'Parada Programada'
        df_info["problema"] = np.where(
            df_info["problema"] == "Parada programada", "Parada Programada", df_info["problema"]
        )

        # Agrupa por motivo_nome e tempo_registro_min
        df_info_group = df_info.groupby(["motivo_nome", "problema"])["tempo_registro_min"].sum()
        df_info_group = df_info_group.sort_values(ascending=False).head(20)

        # Salva os top 10 motivos de paradas
        df_info_group.to_csv(TOP_STOPS)

        print("========= Top 10 motivos de paradas salvos =========")

    def get_last_month_saved_ind(self):
        """
        Retorna os dados do mês anterior.
        ```
        df_eff, df_perf, df_repair
        ```
        """
        # Leitura dos dados
        df_eff = pd.read_csv(EFF_LAST)
        df_perf = pd.read_csv(PERF_LAST)
        df_repair = pd.read_csv(REPAIR_LAST)

        return df_eff, df_perf, df_repair

    def get_historic_data(self):
        """
        Retorna o histórico de dados.
        ```
        df_history, top_tops
        ```
        """
        df_history = pd.read_csv(DF_HISTORY)
        top_tops = pd.read_csv(TOP_STOPS)

        return df_history, top_tops
