"""
Module for bar lost chart component.
@Author: Bruno Tomaz
@Date: 04/03/2024
"""

import textwrap

import pandas as pd
import plotly.graph_objects as go
from dash import dcc
from helpers.types import BSColorsEnum, IndicatorType, TemplateType
from service.times_data import TimesData


class BarChartLost:
    """
    Represents a bar chart for the top 10 reasons/problems causing time loss.

    Attributes:
        times_data (TimesData): An instance of the TimesData class.
        grey_500_color (str): The color value for the bar chart.

    Methods:
        create_bar_chart_lost: Creates a bar chart for the
        top 10 reasons/problems causing time loss.

    """

    def __init__(self):
        self.times_data = TimesData()
        self.grey_500_color = BSColorsEnum.GREY_500_COLOR.value

    def create_bar_chart_lost(
        self,
        dataframe: pd.DataFrame,
        indicator: IndicatorType,
        template: TemplateType,
        turn: str,
        working: pd.DataFrame = None,
    ) -> go.Figure:
        """
        Creates a bar chart for the top 10 reasons/problems causing time loss.

        Args:
            dataframe (pd.DataFrame): The input dataframe containing the data.
            indicator (IndicatorType): The type of indicator to consider.
            template (TemplateType): The template type for the chart.
            turn (str): The type of shift (e.g., "MAT" for morning shift).
            working (pd.DataFrame, optional): The working dataframe. Defaults to None.

        Returns:
            go.Figure: The bar chart figure.

        Raises:
            None

        """

        # Ajustar o dataframe
        df = self.times_data.adjust_df_for_bar_lost(dataframe, indicator, turn, working)

        # Turno Map
        turn_map = {"NOT": "Noturno", "MAT": "Matutino", "VES": "Vespertino", "TOT": "Total"}

        # Se motivo id for 3 e problema for nulo, preencher o problema
        df.loc[(df["motivo_id"] == 3) & (df["problema"].isnull()), "problema"] = "Refeição"

        # Preencher onde o problema é nulo
        df.loc[df["problema"].isnull(), "problema"] = "Problema não informado"

        figure = go.Figure()

        if indicator != IndicatorType.REPAIR:
            # Agrupar por motivo e problema e somar o excedente
            df_grouped = df.groupby(["motivo_nome", "problema"])["excedente"].sum().reset_index()

            # Ordenar por excedente
            df_grouped = df_grouped.sort_values(by="excedente", ascending=False).head(10)

            # Adicionar quebras de linha no texto do eixo x para melhor visualização
            df_grouped["motivo_nome"] = df_grouped["motivo_nome"].apply(
                lambda x: "<br>".join(textwrap.wrap(x, width=10))
            )

            figure = go.Figure(
                data=[
                    go.Bar(
                        name="Motivo/Problema",
                        x=df_grouped["motivo_nome"],
                        y=df_grouped["excedente"],
                        customdata=df_grouped["problema"],
                        marker_color=self.grey_500_color,
                        hovertemplate="<b>Motivo</b>: %{customdata}<br>"
                        "<b>Tempo Perdido</b>: %{y:.0f} min<br>",
                    )
                ]
            )
        else:
            # Agrupar por problema e somar o excedente
            df_problems = df.groupby("problema")["excedente"].sum().reset_index()

            # Ordenar por excedente
            df_problems = df_problems.sort_values(by="excedente", ascending=False).head(10)

            figure = go.Figure(
                data=[
                    go.Bar(
                        name="Problema",
                        x=df_problems["problema"],
                        y=df_problems["excedente"],
                        marker_color=self.grey_500_color,
                        hovertemplate="<b>Problema</b>: %{x}<br>"
                        "<b>Tempo Perdido</b>: %{y:.0f} min<br>",
                    )
                ]
            )

        # Layout
        figure.update_layout(
            title=f"Top 10 Motivos/Problemas de Perda de Tempo - {turn_map[turn]}",
            title_x=0.5,
            xaxis_title="Motivo/Problema",
            yaxis_title="Tempo Perdido (min)",
            template=template.value,
            plot_bgcolor="RGBA(0,0,0,0.01)",
            font=dict(family="Inter"),
            margin=dict(l=40, r=40, t=40, b=40),
            showlegend=False,
        )

        return dcc.Graph(figure=figure)
