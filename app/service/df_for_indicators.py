"""
Autor: Bruno Tomaz
Data: 31/01/2024
Este módulo é responsável por criar DataFrames para os indicadores.
"""

# pylint: disable=import-error
from datetime import datetime
from itertools import product

import numpy as np
import pandas as pd
from service.times_data import TimesData

# cSpell: words eficiencia


class DFIndicators:
    """
    Classe que cria DataFrames para os indicadores.
    """

    def __init__(self, df_info, df_prod):
        self.times_data = TimesData()
        self.df_info = df_info
        self.df_prod = df_prod

        # df_perf_data = self.times_data.get_perf_data(df_info, df_prod)
        # df_repair_data = self.times_data.get_repair_data(df_info, df_prod)

    # ---------------------------- Indicadores de Eficiência ---------------------------- #
    def get_eff_data(self):
        """
        Função que retorna um DataFrame com os dados de eficiência.
        """
        return self.times_data.get_eff_data(self.df_info, self.df_prod)

    def get_eff_data_heatmap(self):
        """
        Função que retorna um DataFrame com os dados de eficiência para o heatmap.
        """
        df_eff = self.get_eff_data()

        # Converter 'data_registro' para datetime e criar uma nova coluna 'data_turno'
        df_eff["data_registro"] = pd.to_datetime(df_eff["data_registro"])
        df_eff["data_turno"] = df_eff["data_registro"].dt.strftime("%Y-%m-%d")

        # Agrupar por 'data_turno' e 'turno' e calcular a média da eficiência
        df_grouped = (
            df_eff.groupby(["data_turno", "turno"], observed=False)["eficiencia"]
            .mean()
            .reset_index()
        )

        # Encontra a data de hoje e o primeiro e último dia do mês
        today = datetime.now()
        start_date = today.replace(day=1).strftime("%Y-%m-%d")
        end_date = (
            today.replace(month=today.month % 12 + 1, day=1) - pd.Timedelta(days=1)
        ).strftime("%Y-%m-%d")

        # Cria um DataFrame com todas as datas possíveis
        all_dates = pd.date_range(start=start_date, end=end_date).strftime("%Y-%m-%d")
        all_turns = df_eff["turno"].unique()
        all_dates_df = pd.DataFrame(
            list(product(all_dates, all_turns)), columns=["data_turno", "turno"]
        )

        # Mescla com o DataFrame original
        df_grouped = df_grouped.merge(all_dates_df, on=["data_turno", "turno"], how="right")

        # Se a data é no futuro, definir a eficiência como NaN
        df_grouped.loc[df_grouped["data_turno"] > today.strftime("%Y-%m-%d"), "eficiencia"] = np.nan

        # Remodelar os dados para o formato de heatmap
        df_pivot = df_grouped.pivot(index="turno", columns="data_turno", values="eficiencia")

        # Reordenar o índice do DataFrame
        df_pivot = df_pivot.reindex(["VES", "MAT", "NOT"])

        return df_pivot
