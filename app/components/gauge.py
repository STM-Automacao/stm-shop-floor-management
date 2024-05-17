"""
@Docstring: A class representing a gauge chart.
@Author: Bruno D. Tomaz
@Date: 28/02/2024
"""

import pandas as pd
import plotly.graph_objs as go
from dash import dcc
from helpers.my_types import BSColorsEnum, IndicatorType, TemplateType


class Gauge:
    """
    A class representing a gauge chart.

    Attributes:
        danger (str): The color for danger level.
        success (str): The color for success level.

    Methods:
        create_gauge(df, indicator, meta, template=None):
        Creates a gauge chart based on the given parameters.

    """

    def __init__(self):
        self.danger = BSColorsEnum.DANGER_COLOR.value
        self.success = BSColorsEnum.SUCCESS_COLOR.value

    def create_gauge(
        self,
        df: pd.DataFrame,
        indicator: IndicatorType,
        meta: int,
        template: str = None,
        this_month: bool = True,
    ) -> dcc.Graph:
        """
        Creates a gauge chart based on the given parameters.

        Args:
            df (pd.DataFrame): The DataFrame containing the data.
            indicator (IndicatorType): The type of indicator to be displayed.
            meta (int): The target value for the indicator.
            template (str, optional): The template to be used for the chart. Defaults to None.
            this_month (bool, optional): Whether the chart is for the current month or the
            previous month. Defaults to True.

        Returns:
            dcc.Graph: The gauge chart as a Dash component.

        """

        # Verificar se é mês atual ou mês anterior
        month = "Mês Atual" if this_month else "Mês Anterior"

        # Calcula a porcentagem de acordo com o indicador
        percentage = df[indicator.value].mean() if this_month else df[indicator.value].iloc[-1]
        percentage = percentage if percentage is not None else 0

        # Arredonda o valor da porcentagem
        percentage = round(percentage, 2)

        # Define a cor de acordo com a porcentagem
        color = self.danger if percentage > (meta / 100) else self.success

        if indicator == IndicatorType.EFFICIENCY:
            color = self.success if percentage >= (meta / 100) else self.danger

        # Definis a escala
        axis_range = [0, 100] if indicator == IndicatorType.EFFICIENCY else [40, 0]

        # Definir o tema
        template = template.value if template else TemplateType.LIGHT.value

        # Criar o gráfico
        figure = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=percentage * 100,
                number={"suffix": "%"},
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": f"{month}", "font": {"size": 14}},
                gauge={
                    "axis": {
                        "range": axis_range,
                        "tickfont": {"size": 8},
                    },
                    "bar": {"color": color},
                    "steps": [
                        {"range": [0, 100], "color": "lightgray"},
                    ],
                    "threshold": {
                        "line": {"color": "black", "width": 2},
                        "thickness": 0.75,
                        "value": meta,
                    },
                },
            )
        )

        figure.update_layout(
            autosize=True,
            margin=dict(t=30, b=30, l=30, r=30),
            plot_bgcolor="white",
            height=250,
            font=dict({"family": "Inter"}),
            template=template,
        )

        return dcc.Graph(figure=figure)
