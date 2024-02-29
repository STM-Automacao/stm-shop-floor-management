"""
@Docstring: A class representing a line chart.
@Author: Bruno D. Tomaz
@Date: 28/02/2024
"""

import pandas as pd
import plotly.graph_objs as go
from dash import dcc
from helpers.types import BSColorsEnum, IndicatorType, TemplateType
from pandas.tseries.offsets import MonthEnd


class LineGraph:
    """
    A class representing a line graph.

    Attributes:
        secondary (str): The secondary color for the graph.
        primary (str): The primary color for the graph.
        danger (str): The danger color for the graph.

    Methods:
        create_line_graph(dataframe, indicator, meta, template, turn=None):
            Create a line graph based on the provided data.

    """

    def __init__(self):
        self.secondary = BSColorsEnum.SECONDARY_COLOR.value
        self.primary = BSColorsEnum.PRIMARY_COLOR.value
        self.danger = BSColorsEnum.DANGER_COLOR.value

    def create_line_graph(
        self,
        dataframe: pd.DataFrame,
        indicator: IndicatorType,
        meta: int,
        template: TemplateType,
        turn: str = None,
    ) -> dcc.Graph:
        """
        Create a line graph based on the provided data.

        Args:
            dataframe (pd.DataFrame): The input data containing the indicator values.
            indicator (IndicatorType): The type of indicator to be plotted.
            meta (int): The target value for the indicator.
            template (TemplateType): The template type for the graph.
            turn (str, optional): The specific turn to filter the data. Defaults to None.

        Returns:
            dcc.Graph: The line graph visualizing the indicator values.

        """

        # Pegar o valor do indicador
        indicator = indicator.value

        # Converter 'data_registro' para datetime e criar uma nova coluna 'data_turno'
        dataframe["data_registro"] = pd.to_datetime(dataframe["data_registro"])
        dataframe["data_turno"] = dataframe["data_registro"].dt.strftime("%Y-%m-%d")

        # Filtrar por turno
        dataframe = dataframe[dataframe["turno"] == turn] if turn else dataframe

        # Agrupar por 'data_turno' e 'turno' e calcular a média do indicador
        df_grouped = dataframe.groupby(["data_turno"])[indicator].mean().reset_index()

        # Multiplicar por 100 para converter para porcentagem
        df_grouped[indicator] = df_grouped[indicator] * 100

        # Criação de um DataFrame com todas as datas do mês atual
        start_date = dataframe["data_registro"].min()
        end_date = start_date + MonthEnd(1)
        all_dates = pd.date_range(start_date, end_date).strftime("%Y-%m-%d")
        dataframe_all_dates = pd.DataFrame(all_dates, columns=["data_turno"])

        # Mesclar o DataFrame original com o DataFrame de todas as datas
        df_grouped = pd.merge(dataframe_all_dates, df_grouped, on="data_turno", how="left")

        # Substituir valores nulos por 0
        df_grouped[indicator] = df_grouped[indicator].fillna(0)

        # Criação do gráfico
        fig = go.Figure(
            data=[
                go.Scatter(
                    x=df_grouped["data_turno"],
                    y=df_grouped[indicator],
                    mode="lines+markers",
                    marker=dict(color=self.primary),
                    line=dict(color=self.primary),
                    hovertemplate=f"<i>Dia</i>: %{{x}}"
                    f"<br><b>{indicator.capitalize()}</b>: %{{y:.1f}}<br>",
                    hoverinfo="skip",
                )
            ],
            layout=go.Layout(
                showlegend=False,
                xaxis=dict(showticklabels=False),
                yaxis=dict(showticklabels=False, autorange=True),
                margin=dict(l=40, r=30, t=10, b=10),
                height=None,
                autosize=True,
                font=dict(family="Inter"),
                template=TemplateType.LIGHT.value if not template else template.value,
                plot_bgcolor="RGBA(0,0,0,0.001)",
            ),
        )

        # Linha de meta
        fig.add_trace(
            go.Scatter(
                x=df_grouped["data_turno"],
                y=[meta] * len(df_grouped),
                mode="lines",
                name="Meta",
                line=dict(color=self.danger, dash="dash"),
                hovertemplate="<b>Meta</b>: %{y:.0f}%<extra></extra>",
            )
        )

        return dcc.Graph(figure=fig, style={"height": "80px"})
