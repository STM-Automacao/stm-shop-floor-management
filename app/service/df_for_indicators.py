"""
Autor: Bruno Tomaz
Data: 31/01/2024
Este módulo é responsável por criar DataFrames para os indicadores.
"""

from datetime import datetime, timedelta
from itertools import product

import numpy as np
import pandas as pd
from helpers.types import IndicatorType
from service.times_data import TimesData

# cSpell: words eficiencia producao


class DFIndicators:
    """
    Classe que cria DataFrames para os indicadores.
    """

    def __init__(self, df_info, df_prod):
        self.times_data = TimesData()
        self.df_info = df_info
        self.df_prod = df_prod
        self.indicator_functions = {
            IndicatorType.EFFICIENCY: self.times_data.get_eff_data,
            IndicatorType.PERFORMANCE: self.times_data.get_perf_data,
            IndicatorType.REPAIR: self.times_data.get_repair_data,
        }

    # ---------------------------------- HEATMAP ---------------------------------- #

    def __adjust_heatmap_data(
        self, indicator: IndicatorType, turn: str = None, main: bool = False
    ) -> pd.DataFrame:

        # Cria um dataframe vazio
        dataframe = pd.DataFrame()

        # Verifica se o indicador está no dicionário, se sim, chama a função do indicador
        if indicator in self.indicator_functions:
            dataframe = self.indicator_functions[indicator](self.df_info, self.df_prod)

        # Se o turno for diferente de nulo, filtra o dataframe
        if turn:
            dataframe = dataframe[dataframe["turno"] == turn]

        # Converter 'data_registro' para datetime
        dataframe["data_registro"] = pd.to_datetime(dataframe["data_registro"])

        # Criar coluna 'data_turno' para agrupar por dia e turno
        dataframe["data_turno"] = dataframe["data_registro"].dt.strftime("%Y-%m-%d")

        # Coluna para agrupar por linha ou turno
        group_col = ["data_turno", "linha"] if not main else ["data_turno", "turno"]

        # Agrupar por data_turno e turno e calcular a média do indicador
        df_grouped = (
            dataframe.groupby(group_col, observed=False)[indicator.value].mean().reset_index()
        )

        # ------------ dataframe com datas possíveis ------------ #
        # Obter a data de início e fim do mês
        today = datetime.now()
        start_date = today.replace(day=1).strftime("%Y-%m-%d")
        end_date = (today.replace(month=today.month % 12 + 1, day=1) - timedelta(days=1)).strftime(
            "%Y-%m-%d"
        )

        # Criar um dataframe com as datas possíveis
        all_dates = pd.date_range(start=start_date, end=end_date).strftime("%Y-%m-%d")
        all_lines = dataframe["linha"].unique() if not main else dataframe["turno"].unique()
        all_dates_lines = pd.DataFrame(list(product(all_dates, all_lines)), columns=group_col)

        # Merge com o dataframe agrupado
        df_grouped = pd.merge(all_dates_lines, df_grouped, on=group_col, how="left")

        # Se a data é futura, o indicador é np.nan
        df_grouped.loc[df_grouped["data_turno"] > today.strftime("%Y-%m-%d"), indicator.value] = (
            np.nan
        )

        # Pivotar o dataframe
        if main:
            df_pivot = df_grouped.pivot(index="turno", columns="data_turno", values=indicator.value)
            df_pivot = df_pivot.reindex(["VES", "MAT", "NOT"])
        else:
            df_grouped = df_grouped.sort_values(by=["linha", "data_turno"], ascending=True)
            df_pivot = df_grouped.pivot(index="linha", columns="data_turno", values=indicator.value)

        # Remover a linha 0
        df_pivot = df_pivot[df_pivot.index != 0]

        return df_pivot

    def get_heatmap_data(self, indicator: IndicatorType) -> tuple:
        """
        Função que retorna um DataFrame com os dados de eficiência para o heatmap.
        Filtrado por turno.
        """

        noturno = self.__adjust_heatmap_data(indicator, turn="NOT")
        matutino = self.__adjust_heatmap_data(indicator, turn="MAT")
        vespertino = self.__adjust_heatmap_data(indicator, turn="VES")
        total = self.__adjust_heatmap_data(indicator)
        main = self.__adjust_heatmap_data(indicator, main=True)

        return noturno, matutino, vespertino, total, main

    # ---------------------------------------- Anotações ---------------------------------------- #

    def __annotations_list(self, df_pivot: pd.DataFrame) -> list:
        annotations = []
        df_pivot.columns = pd.to_datetime(df_pivot.columns).day
        for (i, j), value in np.ndenumerate(df_pivot.values):
            annotations.append(
                dict(
                    x=df_pivot.columns[j],
                    y=df_pivot.index[i],
                    text=f"{value:.1%}",
                    showarrow=False,
                    font=dict({"color": "white", "size": 8}),
                )
            )

        # Remover a anotação com texto "nan%"
        annotations = [annotation for annotation in annotations if "nan%" not in annotation["text"]]

        return annotations

    def get_annotations(self, indicator: IndicatorType) -> tuple:
        """
        Função que retorna um DataFrame com as anotações de eficiência.
        Filtrado por turno.
        """
        noturno, matutino, vespertino, total, main = self.get_heatmap_data(indicator)

        return (
            self.__annotations_list(noturno),
            self.__annotations_list(matutino),
            self.__annotations_list(vespertino),
            self.__annotations_list(total),
            self.__annotations_list(main),
        )
