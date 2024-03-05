"""
Module for the bar chart general component.
@Author: Bruno Tomaz
@Date: 23/01/2024
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc
from helpers.types import BSColorsEnum, IndicatorType, TemplateType


class BarChartGeneral:
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
        # Ordem dos turnos
        turn_order = ["NOT", "MAT", "VES"]

        # Converter turno em categórico para ordenar
        df["turno"] = pd.Categorical(df["turno"], categories=turn_order, ordered=True)

        if indicator == IndicatorType.EFFICIENCY:
            # Agrupar, agregar e ajustar o dataframe
            df_grouped = (
                df.groupby(["linha", "turno"], observed=True)
                .agg({f"{indicator.value}": "mean", "total_produzido": "sum"})
                .sort_values(by=["linha", "turno"])
                .reset_index()
            )
            # Ajustar a produção para caixas
            df_grouped["total_produzido"] = (df_grouped["total_produzido"] / 10).round(0)
            hover = {"total_produzido": True, "linha": False, "eficiencia": False}

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

        # Ajustar o hover
        figure.update_traces(
            hovertemplate="<b>Linha:</b> %{y}<br>"
            f"<b>{indicator.value.capitalize()}:</b> %{{x:.1%}}<br>"
            "<b>Produção:</b> %{customdata[0]} caixas<extra></extra>",
        )

        # Definir o título do Gráfico
        figure.update_layout(
            title="Desempenho Total por Linha",
            title_x=0.5,
            yaxis=dict(
                title="Linha",
                autorange="reversed",
                tickvals=df_grouped["linha"].unique(),
                ticksuffix=" ",
            ),
            xaxis=dict(
                title=f"{indicator.value.capitalize()}",
                tickformat=".0%",
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

        return dcc.Graph(figure=figure)
