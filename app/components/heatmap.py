"""
@Docstring: A class representing a heatmap chart.
@Author: Bruno D. Tomaz
@Date: 28/02/2024
"""

import pandas as pd
import plotly.graph_objs as go
from dash import dcc
from helpers.types import BSColorsEnum, IndicatorType, TemplateType


class Heatmap:
    """
    A class representing a heatmap graph.

    Attributes:
        danger (str): The color value for the danger indicator.
        success (str): The color value for the success indicator.

    Methods:
        create_heatmap: Create a heatmap graph based on the provided data.
    """

    def __init__(self):
        self.danger = BSColorsEnum.DANGER_COLOR.value
        self.success = BSColorsEnum.SUCCESS_COLOR.value

    def create_heatmap(
        self,
        dataframe: pd.DataFrame,
        annotations: list,
        indicator: IndicatorType,
        meta: int,
        template: str = None,
        turn: str = False,
    ) -> dcc.Graph:
        """
        Create a heatmap graph based on the provided data.

        Args:
            dataframe (pd.DataFrame): The data to be visualized in the heatmap.
            annotations (list): List of annotations to be displayed on the heatmap.
            indicator (IndicatorType): The type of indicator to be visualized.
            meta (int): The meta value for the indicator.
            template (str, optional): The template to be used for the graph. Defaults to None.
            turn (str, optional): Whether to display the heatmap by turn or not. Defaults to False.

        Returns:
            dcc.Graph: The heatmap graph.
        """

        # Meta p/ uso em cores
        color_meta = meta / 100

        # Cria escala de cores
        color_scale = {
            IndicatorType.EFFICIENCY: [
                [0, self.danger],
                [color_meta, self.danger],
                [color_meta, self.success],
                [1, self.success],
            ],
            IndicatorType.PERFORMANCE: [
                [0, self.success],
                [color_meta, self.success],
                [color_meta, self.danger],
                [1, self.danger],
            ],
            IndicatorType.REPAIR: [
                [0, self.success],
                [color_meta, self.success],
                [color_meta, self.danger],
                [1, self.danger],
            ],
        }

        # Extrai apenas o dia da data
        dataframe.columns = pd.to_datetime(dataframe.columns).day

        # Cria o hover data
        hover_data = (
            f"Turno: %{{y}}<br>Dia: %{{x}}<br>{indicator.value.capitalize()}: %{{z:.1%}}"
            if not turn
            else f"Linha: %{{y}}<br>Dia: %{{x}}<br>{indicator.value.capitalize()}: %{{z:.1%}}"
        )

        # Cria o heatmap
        figure = go.Figure(
            data=go.Heatmap(
                z=dataframe.values,
                x=dataframe.columns,
                y=dataframe.index,
                colorscale=color_scale[indicator],
                name=indicator.value.capitalize(),
                zmin=0,
                zmax=1,
                hoverongaps=False,
                hovertemplate=hover_data,
                showscale=False,
                xgap=1,
                ygap=1,
            ),
            layout=go.Layout(
                title=f"{indicator.value.capitalize()} - Meta: {meta}%",
                title_x=0.5,
                xaxis=dict(
                    title="Dia do Mês",
                    tickfont=dict(color="lightgray"),
                    tickmode="linear",
                    nticks=31,
                    tickvals=list(range(1, 32)),
                    ticktext=list(range(1, 32)),
                    tickangle=0,
                ),
                yaxis=dict(title="Turno", tickfont=dict(color="lightgray"), ticksuffix=" "),
                font=dict(family="Inter"),
                margin=dict(t=40, b=40, l=40, r=40),
                annotations=annotations,
                template=TemplateType.LIGHT.value if not template else template.value,
                plot_bgcolor="RGBA(0,0,0,0.01)",
            ),
        )

        if turn:
            figure.update_layout(
                yaxis=dict(
                    title="Linha",
                    autorange="reversed",
                )
            )

        return dcc.Graph(figure=figure)
