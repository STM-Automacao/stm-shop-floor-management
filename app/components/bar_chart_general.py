"""
    Module for the bar chart general component.
    - Autor: Bruno Tomaz
    - Data de criação: 23/01/2024
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc
from helpers.types import BSColorsEnum, IndicatorType, TemplateType


class BarChartGeneral:
    """
    A class representing a bar chart visualization.

    Attributes:
        grey_500_color (str): The color code for the grey 500 color.
        grey_600_color (str): The color code for the grey 600 color.
        grey_700_color (str): The color code for the grey 700 color.
        grey_900_color (str): The color code for the grey 900 color.
        success_color (str): The color code for the success color.
        warning_color (str): The color code for the warning color.
    """

    def __init__(self):
        self.grey_500_color = BSColorsEnum.GREY_500_COLOR.value
        self.grey_600_color = BSColorsEnum.GREY_600_COLOR.value
        self.grey_700_color = BSColorsEnum.GREY_700_COLOR.value
        self.grey_900_color = BSColorsEnum.GREY_900_COLOR.value
        self.success_color = BSColorsEnum.SUCCESS_COLOR.value
        self.warning_color = BSColorsEnum.WARNING_COLOR.value

    def create_bar_chart_gen(
        self, df: pd.DataFrame, indicator: IndicatorType, template: TemplateType, meta: int = 90
    ):
        """
        Creates a bar chart visualization based on the provided DataFrame.

        Args:
            df (pd.DataFrame): The DataFrame containing the data for the chart.
            indicator (IndicatorType): The type of indicator to display on the chart.
            template (TemplateType): The type of template to use for the chart.
            meta (int, optional): The target value for the indicator. Defaults to 90.

        Returns:
            dcc.Graph: The generated bar chart as a Dash component.
        """

        # Ordem dos turnos
        turn_order = ["NOT", "MAT", "VES"]

        # Converter turno em categórico para ordenar
        df["turno"] = pd.Categorical(df["turno"], categories=turn_order, ordered=True)

        # Agregador conforme indicador:
        aggregate = "total_produzido" if indicator == IndicatorType.EFFICIENCY else "afeta"

        # Agrupar, agregar e ajustar o dataframe
        df_grouped = (
            df.groupby(["linha", "turno"], observed=True)
            .agg({f"{indicator.value}": "mean", f"{aggregate}": "sum"})
            .sort_values(by=["linha", "turno"])
            .reset_index()
        )

        if indicator == IndicatorType.EFFICIENCY:
            # Ajustar a produção para caixas
            df_grouped["total_produzido"] = (df_grouped["total_produzido"] / 10).round(0)
            hover = {"total_produzido": True, "linha": False, "eficiencia": False}
        else:
            hover = {"afeta": True, "linha": False, f"{indicator.value}": False}

        label = {f"{indicator.value}": f"{indicator.value.capitalize()}"}

        # Criar o gráfico de barras
        figure = px.bar(
            df_grouped,
            orientation="h",
            x=f"{indicator.value}",
            y="linha",
            color="turno",
            barmode="group",
            hover_data=hover,
            color_discrete_map={
                "NOT": self.grey_500_color,
                "MAT": self.grey_600_color,
                "VES": (
                    self.grey_900_color if template == TemplateType.LIGHT else self.grey_700_color
                ),
            },
            labels=label,
        )

        custom_hover = (
            "<b>Produção:</b> %{customdata[0]} caixas<extra></extra>"
            if indicator == IndicatorType.EFFICIENCY
            else "<b>Tempo:</b> %{customdata[0]} min<extra></extra>"
        )

        # Ajustar o hover
        figure.update_traces(
            hovertemplate="<b>Linha:</b> %{y}<br>"
            f"<b>{indicator.value.capitalize()}:</b> %{{x:.1%}}<br>"
            f"{custom_hover}",
        )

        tick_color = "gray" if template == TemplateType.LIGHT else "lightgray"

        # Ajustar o layout
        figure.update_layout(
            title=f"{indicator.value.capitalize()} Total por Linha",
            title_x=0.5,
            yaxis=dict(
                title="Linha",
                autorange="reversed",
                tickvals=df_grouped["linha"].unique(),
                ticksuffix=" ",
                tickfont=dict(color=tick_color),
            ),
            xaxis=dict(
                title=f"{indicator.value.capitalize()}",
                tickformat=".0%",
                tickfont=dict(color=tick_color),
            ),
            legend=dict(
                title_text="Turno",
                traceorder="normal",
            ),
            margin=dict(t=80, b=40, l=40, r=40),
            font=dict(family="Inter"),
            template=template.value,
            plot_bgcolor="RGBA(0,0,0,0.01)",
        )

        if indicator != IndicatorType.EFFICIENCY:
            figure.update_layout(legend=dict(x=0, y=1))
            figure.update_xaxes(autorange="reversed")
            figure.update_yaxes(side="right")

        # Calcula a média do indicador
        mean = df_grouped[indicator.value].mean()

        # Adiciona a linha de média
        figure.add_trace(
            go.Scatter(
                x=[mean] * len(df_grouped["linha"]),
                y=df_grouped["linha"],
                name="Média Geral",
                mode="lines",
                line=dict(dash="dash", color="gold"),
                hovertemplate=f"Média: {mean:.1%}<extra></extra>",
            )
        )

        # Adiciona a meta
        figure.add_trace(
            go.Scatter(
                x=[meta / 100] * len(df_grouped["linha"]),
                y=df_grouped["linha"],
                name=f"Meta {meta}%",
                mode="lines",
                line=dict(dash="dash", color=self.success_color),
                hovertemplate=f"Meta: {meta}%<extra></extra>",
            )
        )

        # Adiciona uma anotação
        if indicator != IndicatorType.EFFICIENCY:
            figure.add_annotation(
                x=0.15,  # Posição x da anotação
                y=0.95,  # Posição y da anotação
                xref="paper",
                yref="paper",
                text=f"Meta: Abaixo de {meta}%",  # Texto da anotação
                showarrow=False,
                font=dict(size=12, color="black", family="Inter"),
                align="left",
                ax=20,
                ay=-30,
                bordercolor="#c7c7c7",
                borderwidth=2,
                borderpad=4,
                bgcolor="#ff7f0e",
                opacity=0.6,
            )

        return dcc.Graph(figure=figure)
