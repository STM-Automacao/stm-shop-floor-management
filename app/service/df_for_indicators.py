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
from helpers.types import IndicatorType
from service.times_data import TimesData

# cSpell: words eficiencia ndenumerate producao


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

    def get_eff_data_heatmap(self) -> pd.DataFrame:
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

    def __adjust_eff_data_heatmap_turn(self, turn: str = None) -> pd.DataFrame:
        """
        Função que retorna um DataFrame com os dados de eficiência para o heatmap.
        """
        df_eff = self.get_eff_data()

        if turn:
            df_eff = df_eff[df_eff["turno"] == turn]

        # Converter 'data_registro' para datetime e criar uma nova coluna 'data_turno'
        df_eff["data_registro"] = pd.to_datetime(df_eff["data_registro"])
        df_eff["data_turno"] = df_eff["data_registro"].dt.strftime("%Y-%m-%d")

        # Agrupar por 'data_turno' e 'turno' e calcular a média da eficiência
        df_grouped = (
            df_eff.groupby(["data_turno", "linha"], observed=False)["eficiencia"]
            .mean()
            .reset_index()
        )

        # Encontra a data de hoje e o primeiro e último dia do mês
        today = datetime.now()
        start_date = today.replace(day=1).strftime("%Y-%m-%d")
        end_date = (
            today.replace(month=today.month % 12 + 1, day=1) - pd.Timedelta(days=1)
        ).strftime("%Y-%m-%d")

        # Cria um dataframe com todas as datas possíveis
        all_dates = pd.date_range(start=start_date, end=end_date).strftime("%Y-%m-%d")
        all_lines = df_eff["linha"].unique()
        all_dates_df = pd.DataFrame(
            list(product(all_dates, all_lines)), columns=["data_turno", "linha"]
        )

        # Mescla com o DataFrame original
        df_grouped = df_grouped.merge(all_dates_df, on=["data_turno", "linha"], how="right")

        # Se a data é no futuro, definir a eficiência como NaN
        df_grouped.loc[df_grouped["data_turno"] > today.strftime("%Y-%m-%d"), "eficiencia"] = np.nan

        # Ordenar por linha e data
        df_grouped = df_grouped.sort_values(["linha", "data_turno"], ascending=[True, True])

        # Remodelar os dados para o formato de heatmap
        df_pivot = df_grouped.pivot(index="linha", columns="data_turno", values="eficiencia")

        return df_pivot

    def get_eff_data_heatmap_turn(self) -> tuple:
        """
        Função que retorna um DataFrame com os dados de eficiência para o heatmap.
        Filtrado por turno.
        """

        noturno = self.__adjust_eff_data_heatmap_turn(turn="NOT")
        matutino = self.__adjust_eff_data_heatmap_turn(turn="MAT")
        vespertino = self.__adjust_eff_data_heatmap_turn(turn="VES")

        return noturno, matutino, vespertino

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

        return annotations

    def get_eff_annotations_turn(self) -> tuple:
        """
        Função que retorna um DataFrame com as anotações de eficiência.
        Filtrado por turno.
        """
        noturno, matutino, vespertino = self.get_eff_data_heatmap_turn()

        return (
            self.__annotations_list(noturno),
            self.__annotations_list(matutino),
            self.__annotations_list(vespertino),
        )

    # -------------------------- Indicadores de Performance e Reparos --------------------------- #

    def get_perf_data(self) -> pd.DataFrame:
        """
        Função que retorna um DataFrame com os dados de performance.
        """
        return self.times_data.get_perf_data(self.df_info, self.df_prod)

    def get_repair_data(self) -> pd.DataFrame:
        """
        Função que retorna um DataFrame com os dados de reparo.
        """
        return self.times_data.get_repair_data(self.df_info, self.df_prod)

    def __heatmap_perf_repair(self, indicador: IndicatorType) -> pd.DataFrame:
        """
        Função que retorna o DataFrame de reparo e performance para o heatmap.
        """
        dataframe = pd.DataFrame()

        if indicador == IndicatorType.PERFORMANCE:
            dataframe = self.get_perf_data()

        if indicador == IndicatorType.REPAIR:
            dataframe = self.get_repair_data()

        # Converter 'data_registro' para datetime e criar uma nova coluna 'data_turno'
        dataframe["data_registro"] = pd.to_datetime(dataframe["data_registro"])
        dataframe["data_turno"] = dataframe["data_registro"].dt.strftime("%Y-%m-%d")

        # Agrupar por 'data_turno' e 'turno' e calcular a média da eficiência
        df_grouped = (
            dataframe.groupby(["data_turno", "turno"], observed=False)[indicador.value]
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
        all_turns = dataframe["turno"].unique()
        all_dates_df = pd.DataFrame(
            list(product(all_dates, all_turns)), columns=["data_turno", "turno"]
        )

        # Mescla com o DataFrame original
        df_grouped = df_grouped.merge(all_dates_df, on=["data_turno", "turno"], how="right")

        # Se a data é no futuro, definir a eficiência como NaN
        df_grouped.loc[df_grouped["data_turno"] > today.strftime("%Y-%m-%d"), indicador.value] = (
            np.nan
        )

        # Remodelar os dados para o formato de heatmap
        df_pivot = df_grouped.pivot(index="turno", columns="data_turno", values=indicador.value)

        # Reordenar o índice do DataFrame
        df_pivot = df_pivot.reindex(["VES", "MAT", "NOT"])

        return df_pivot

    def get_perf_repair_heatmap(self) -> tuple:
        """
        Função que retorna um DataFrame com os dados de performance e reparo para o heatmap.
        """
        return (
            self.__heatmap_perf_repair(IndicatorType.PERFORMANCE),
            self.__heatmap_perf_repair(IndicatorType.REPAIR),
        )

    # ---------------------------------------- Anotações ---------------------------------------- #

    def get_annotations(self) -> tuple:
        """
        Função que retorna um DataFrame com as anotações de performance e reparo.
        """
        perf, repair = self.get_perf_repair_heatmap()
        eff = self.get_eff_data_heatmap()

        return (
            self.__annotations_list(eff),
            self.__annotations_list(perf),
            self.__annotations_list(repair),
        )

    # -------------------------- Heatmap Performance e Repair by turn -------------------------- #

    def __heatmap_perf_repair_turn(self, indicador: IndicatorType, turn: str) -> pd.DataFrame:
        """
        Função que retorna um DataFrame com os dados de performance e reparo para o heatmap.
        Filtrado por turno.
        """

        dataframe = pd.DataFrame()

        if indicador == IndicatorType.PERFORMANCE:
            dataframe = self.get_perf_data()

        if indicador == IndicatorType.REPAIR:
            dataframe = self.get_repair_data()

        dataframe = dataframe[dataframe["turno"] == turn]

        indicator = indicador.value

        # Converter 'data_registro' para datetime e criar uma nova coluna 'data_turno'
        dataframe["data_registro"] = pd.to_datetime(dataframe["data_registro"])
        dataframe["data_turno"] = dataframe["data_registro"].dt.strftime("%Y-%m-%d")

        # Agrupar por 'data_turno' e 'turno' e calcular a média
        df_grouped = (
            dataframe.groupby(["data_turno", "linha"], observed=False)[indicator]
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
        all_lines = dataframe["linha"].unique()
        all_dates_df = pd.DataFrame(
            list(product(all_dates, all_lines)), columns=["data_turno", "linha"]
        )

        # Mescla com o DataFrame original
        df_grouped = df_grouped.merge(all_dates_df, on=["data_turno", "linha"], how="right")

        # Se a data é no futuro, definir a eficiência como NaN
        df_grouped.loc[df_grouped["data_turno"] > today.strftime("%Y-%m-%d"), indicator] = np.nan

        # Ordenar por linha e data
        df_grouped = df_grouped.sort_values(["linha", "data_turno"], ascending=[True, True])

        # Remodelar os dados para o formato de heatmap
        df_pivot = df_grouped.pivot(index="linha", columns="data_turno", values=indicator)

        return df_pivot

    def get_perf_heatmap_turn(self) -> tuple:
        """
        Função que retorna um DataFrame com os dados de performance para o heatmap.
        Filtrado por turno.
        """
        noturno = self.__heatmap_perf_repair_turn(IndicatorType.PERFORMANCE, turn="NOT")
        matutino = self.__heatmap_perf_repair_turn(IndicatorType.PERFORMANCE, turn="MAT")
        vespertino = self.__heatmap_perf_repair_turn(IndicatorType.PERFORMANCE, turn="VES")

        return noturno, matutino, vespertino

    def get_repair_heatmap_turn(self) -> tuple:
        """
        Função que retorna um DataFrame com os dados de reparo para o heatmap.
        Filtrado por turno.
        """
        noturno = self.__heatmap_perf_repair_turn(IndicatorType.REPAIR, turn="NOT")
        matutino = self.__heatmap_perf_repair_turn(IndicatorType.REPAIR, turn="MAT")
        vespertino = self.__heatmap_perf_repair_turn(IndicatorType.REPAIR, turn="VES")

        return noturno, matutino, vespertino

    # ---------------------------------------- Anotações ---------------------------------------- #

    def get_perf_annotations_turn(self):
        """
        Função que retorna um DataFrame com as anotações de performance.
        Filtrado por turno.
        """

        noturno, matutino, vespertino = self.get_perf_heatmap_turn()

        return (
            self.__annotations_list(noturno),
            self.__annotations_list(matutino),
            self.__annotations_list(vespertino),
        )

    def get_repair_annotations_turn(self):
        """
        Função que retorna um DataFrame com as anotações de reparo.
        Filtrado por turno.
        """

        noturno, matutino, vespertino = self.get_repair_heatmap_turn()

        return (
            self.__annotations_list(noturno),
            self.__annotations_list(matutino),
            self.__annotations_list(vespertino),
        )
