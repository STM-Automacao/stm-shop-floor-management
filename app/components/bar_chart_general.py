"""
Module for the bar chart general component.
@Author: Bruno Tomaz
@Date: 23/01/2024
"""

import pandas as pd
import plotly.express as px
from helpers.types import BSColorsEnum, IndicatorType, TemplateType


class BarChartGeneral:
    def __init__(self):
        self.grey_500_color = BSColorsEnum.GREY_500_COLOR.value
        self.grey_600_color = BSColorsEnum.GREY_600_COLOR.value
        self.grey_900_color = BSColorsEnum.GREY_900_COLOR.value

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
            template=template,
            hover_data=hover,
            color_discrete_map={
                "NOT": self.grey_500_color,
                "MAT": self.grey_600_color,
                "VES": self.grey_900_color,
            },
            labels=label,
        )
