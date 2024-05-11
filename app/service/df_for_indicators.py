"""
Autor: Bruno Tomaz
Data: 31/01/2024
Este módulo é responsável por criar DataFrames para os indicadores.
"""

import numpy as np
import pandas as pd
from helpers.my_types import IndicatorType
from service.data_analysis import DataAnalysis

# cSpell: words eficiencia producao


class DFIndicators:
    """
    Classe que cria DataFrames para os indicadores.
    """

    def __init__(self, df_info_ihm: pd.DataFrame, df_prod: pd.DataFrame):
        self.df_info_ihm = df_info_ihm
        self.df_prod = df_prod
        self.data_analysis = DataAnalysis(self.df_info_ihm, self.df_prod)
        self.indicator_functions = {
            IndicatorType.EFFICIENCY: self.data_analysis.get_eff_data,
            IndicatorType.PERFORMANCE: self.data_analysis.get_perf_data,
            IndicatorType.REPAIR: self.data_analysis.get_repair_data,
        }
        self.indicator_descontos = {
            IndicatorType.EFFICIENCY: self.data_analysis.desc_eff,
            IndicatorType.PERFORMANCE: self.data_analysis.desc_perf,
            IndicatorType.REPAIR: self.data_analysis.desc_rep,
        }
        self.indicator_not_affect = {
            IndicatorType.EFFICIENCY: self.data_analysis.not_eff,
            IndicatorType.PERFORMANCE: self.data_analysis.not_perf,
            IndicatorType.REPAIR: self.data_analysis.afeta_rep,
        }

    def __adjust_heatmap_data(
        self, indicator: IndicatorType, turn: str = None, main: bool = False
    ) -> pd.DataFrame:
        """
        Adjusts the heatmap data based on the given indicator, turn, and main flag.

        Parameters:
            indicator (IndicatorType): The indicator type to adjust the data for.
            turn (str, optional): The turn to filter the data for. Defaults to None.
            main (bool, optional): Flag indicating whether the main grouping should be used.
            Defaults to False.

        Returns:
            pd.DataFrame: The adjusted dataframe with the heatmap data.
        """

        # Dataframe com os dados do indicador
        df = pd.DataFrame()

        # Busca o dataframe de acordo com o indicador
        df = self.indicator_functions[indicator]()

        # Se for indicado um turno, filtra o dataframe
        if turn:
            df = df[df["turno"] == turn]

        # Colunas para agrupar o dataframe
        group_cols = ["data_registro", "turno"] if main else ["data_registro", "linha"]

        # Agrupa o dataframe e calcula a média
        df = df.groupby(group_cols, observed=False)[indicator.value].mean().reset_index()

        # ====================== Garantir Que Todas Datas Estejam Presentes ====================== #

        # Obter a data do inicio e fim do mês atual
        start_date = pd.to_datetime("today").replace(day=1).date()
        end_date = (pd.to_datetime("today") + pd.offsets.MonthEnd(0)).date()

        # Lista com todas as datas do mês atual
        date_range = [date.date() for date in pd.date_range(start_date, end_date, freq="D")]

        # Encontra os valores únicos de turno ou linha e cria um novo index
        if main:
            unique_turnos = df["turno"].unique()
            df.set_index(["data_registro", "turno"], inplace=True)
            new_index = pd.MultiIndex.from_product(
                [date_range, unique_turnos], names=["data_registro", "turno"]
            )
        else:
            unique_lines = df["linha"].unique()
            df.set_index(["data_registro", "linha"], inplace=True)
            new_index = pd.MultiIndex.from_product(
                [date_range, unique_lines], names=["data_registro", "linha"]
            )

        # Reindexa o dataframe
        df = df.reindex(new_index).reset_index()

        # ================================== Pivotar O Dataframe ================================= #

        # Pivotar o dataframe
        if main:
            df = df.pivot(index="turno", columns="data_registro", values=indicator.value)
            df = df.reindex(["NOT", "MAT", "VES"])
        else:
            df = df.pivot(index="linha", columns="data_registro", values=indicator.value)

        return df

    def get_heatmap_data(self, indicator: IndicatorType) -> tuple:
        """
        Retrieves heatmap data for the given indicator.

        Args:
            indicator (IndicatorType): The indicator type to retrieve data for.

        Returns:
            tuple: A tuple containing the heatmap data for different shifts:
                - noturno: Heatmap data for the night shift.
                - matutino: Heatmap data for the morning shift.
                - vespertino: Heatmap data for the afternoon shift.
                - main: Heatmap data for the main shift.
        """

        noturno = self.__adjust_heatmap_data(indicator, "NOT")
        matutino = self.__adjust_heatmap_data(indicator, "MAT")
        vespertino = self.__adjust_heatmap_data(indicator, "VES")
        total = self.__adjust_heatmap_data(indicator)
        main = self.__adjust_heatmap_data(indicator, main=True)

        return noturno, matutino, vespertino, total, main

    @staticmethod
    def __annotations_list(df: pd.DataFrame) -> list:
        """
        Cria uma lista de anotações para o heatmap.

        Args:
            df (pd.DataFrame): O dataframe com os dados do heatmap.

        Returns:
            list: Uma lista de anotações para o heatmap.
        """

        # Inicializa a lista de anotações
        annotations = []

        # Define a coluna para dia apenas
        df.columns = pd.to_datetime(df.columns).day

        # Loop sobre as linhas do dataframe
        for (i, j), value in np.ndenumerate(df.values):
            # Se o valor for diferente de NaN
            if not np.isnan(value):
                # Adiciona a anotação
                annotations.append(
                    {
                        "x": df.columns[j],
                        "y": df.index[i],
                        "text": f"{value:.1%}",
                        "xref": "x",
                        "yref": "y",
                        "showarrow": False,
                        "font": {"size": 10, "color": "white"},
                    }
                )

        return annotations

    def get_annotations(self, indicator: IndicatorType) -> tuple:
        """
        Retrieves annotations for the heatmap data.

        Args:
            indicator (IndicatorType): The indicator type to retrieve annotations for.

        Returns:
            tuple: A tuple containing the annotations for different shifts:
                - noturno: Annotations for the night shift.
                - matutino: Annotations for the morning shift.
                - vespertino: Annotations for the afternoon shift.
                - main: Annotations for the main shift.
        """

        noturno, matutino, vespertino, total, main = self.get_heatmap_data(indicator)

        noturno_annotations = self.__annotations_list(noturno)
        matutino_annotations = self.__annotations_list(matutino)
        vespertino_annotations = self.__annotations_list(vespertino)
        total_annotations = self.__annotations_list(total)
        main_annotations = self.__annotations_list(main)

        return (
            noturno_annotations,
            matutino_annotations,
            vespertino_annotations,
            total_annotations,
            main_annotations,
        )

    def adjust_df_for_bar_lost(
        self,
        df: pd.DataFrame,
        indicator: IndicatorType,
        turn: str = "TOT",
        working_minutes: pd.DataFrame = None,
    ) -> pd.DataFrame:
        """
        Adjusts the given DataFrame for bar lost based on the specified indicator, turn,
        and working minutes.

        Args:
            df (pd.DataFrame): The DataFrame to be adjusted.
            indicator (IndicatorType): The indicator type for adjusting the DataFrame.
            turn (str, optional): The turn to filter the DataFrame. Defaults to "TOT".
            working_minutes (pd.DataFrame, optional): The DataFrame containing working minutes.
            Defaults to None.

        Returns:
            pd.DataFrame: The adjusted DataFrame.
        """

        # Cria dataframe com os tempos
        df = self.data_analysis.get_discount(
            df, self.indicator_descontos[indicator], self.indicator_not_affect[indicator], indicator
        )

        # Une com working_minutes
        if working_minutes is not None:
            df = pd.concat([df, working_minutes], ignore_index=True, sort=False)

        # Filtra por turno
        df = df[df["turno"] == turn] if turn != "TOT" else df

        # Lidando com paradas de  5 minutos ou menos
        mask = (df["motivo"].isnull()) & (df["tempo"] <= 5)
        columns_to_fill = ["motivo", "problema", "causa"]
        fill_value = "Parada de 5 minutos ou menos"

        for column in columns_to_fill:
            df.loc[mask, column] = fill_value

        # Lidando com motivo nulo
        mask = mask = df["motivo"].isnull()
        columns_to_fill = ["motivo", "problema", "causa"]
        fill_value = "Não apontado"

        for column in columns_to_fill:
            df.loc[mask, column] = fill_value

        return df
