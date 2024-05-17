"""
    Module for bar lost chart component.
    - Autor: Bruno Tomaz
    - Data de criação: 04/03/2024
"""

import textwrap

import pandas as pd
import plotly.graph_objects as go
from dash import dcc
from helpers.my_types import BSColorsEnum, IndicatorType, TemplateType
from service.df_for_indicators import DFIndicators


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

    def __init__(self, df_maq_stopped: pd.DataFrame, df_production: pd.DataFrame):
        self.indicator = DFIndicators(df_maq_stopped, df_production)
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
        df = self.indicator.adjust_df_for_bar_lost(dataframe, indicator, turn, working)

        # Turno Map
        turn_map = {"NOT": "Noturno", "MAT": "Matutino", "VES": "Vespertino", "TOT": "Total"}

        figure = go.Figure()

        if indicator != IndicatorType.REPAIR:
            # Agrupar por motivo e problema e somar o excedente
            df_grouped = df.groupby(["motivo", "problema"])["excedente"].sum().reset_index()

            # Ordenar por excedente
            df_grouped = df_grouped.sort_values(by="excedente", ascending=False).head(10)

            # Adicionar quebras de linha no texto do eixo x para melhor visualização
            df_grouped["motivo"] = df_grouped["motivo"].apply(
                lambda x: "<br>".join(textwrap.wrap(x, width=10))
            )

            figure = go.Figure(
                data=[
                    go.Bar(
                        name="Motivo/Problema",
                        x=df_grouped["motivo"],
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

        tick_color = "gray" if template == TemplateType.LIGHT else "lightgray"

        # Layout
        figure.update_layout(
            title=f"Top 10 Motivos/Problemas de Perda de Tempo - {turn_map[turn]}",
            title_x=0.5,
            xaxis_title="Motivo/Problema",
            yaxis_title="Tempo Perdido (min)",
            xaxis=dict(tickfont=dict(color=tick_color)),
            yaxis=dict(tickfont=dict(color=tick_color)),
            template=template.value,
            plot_bgcolor="RGBA(0,0,0,0.01)",
            font=dict(family="Inter"),
            margin=dict(l=40, r=10, t=80, b=40),
            showlegend=False,
        )

        return dcc.Graph(figure=figure)
