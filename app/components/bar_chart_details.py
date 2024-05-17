"""
Module for creating a bar chart with details based on provided data.
"""

import pandas as pd
from dash import dcc
from helpers.my_types import COLOR_DICT, IndicatorType, TemplateType
from plotly import express as px
from service.df_for_indicators import DFIndicators


class BarChartDetails:
    """
    Represents a class for creating bar chart details based on provided data.

    Args:
        df_maq_stopped (pd.DataFrame): The input dataframe containing the data.

    Attributes:
        df_maq_stopped (pd.DataFrame): The input dataframe containing the data.
        df_indicator (DFIndicators): The dataframe for indicators.
    """

    def __init__(self, df_maq_stopped: pd.DataFrame):
        self.df_maq_stopped = df_maq_stopped
        self.df_indicator = DFIndicators(self.df_maq_stopped)

    def create_bar_chart_details(
        self,
        indicator: IndicatorType,
        template: TemplateType,
        turn: str,
        selected_data: str = None,
        working: pd.DataFrame = None,
        choice: str = "motivo",
    ) -> dcc.Graph:
        """
        Creates a bar chart with details based on the provided data.

        Args:
            dataframe (pd.DataFrame): The input dataframe containing the data.
            indicator (IndicatorType): The type of indicator.
            template (TemplateType): The type of template.
            turn (str): The turn value.
            selected_data: The selected data.
            working (pd.DataFrame, optional): The working dataframe. Defaults to None.

        Returns:
            dcc.Graph: The bar chart as a Dash component.
        """
        df = self.df_indicator.adjust_df_for_bar_lost(
            self.df_maq_stopped, indicator, turn, working_minutes=working
        )

        # Garantis que data_registro tenha apenas o dia
        df["data_registro"] = pd.to_datetime(df["data_registro"]).dt.date

        # Filtro pelo dia, caso tenha sido selecionado
        df = (
            df[df["data_registro"] == pd.to_datetime(selected_data).date()]
            if selected_data is not None
            else df
        )

        if choice == "motivo":
            # Se motivo for Rodando, problema e causa são "Sem Problema" e "Sem Causa"
            df.loc[df["motivo"] == "Rodando", ["problema", "causa"]] = " "

            # Criar coluna sort para ordenar os dados
            df["sort"] = (
                df["motivo"].map({"Rodando": 0, "Parada Programada": 2, "Limpeza": 1}).fillna(9)
            )

            # Ordenar por sort e tempo_registro_min
            df = df.sort_values(
                by=["linha", "sort", "data_registro", "tempo"],
                ascending=[True, True, True, False],
            )

            # Ajustar a coluna data_registro para exibir apenas o dia
            df["data_registro"] = pd.to_datetime(df["data_registro"]).dt.strftime("%d/%m")

            # Ajustar a coluna data_hora para exibir apenas a hora e o minuto
            df["data_hora"] = pd.to_datetime(df["data_hora"]).dt.time

            # Ajustar data_hora qdo motivo é Rodando
            df.loc[df["motivo"] == "Rodando", "data_hora"] = " "

            # Remover a coluna sort
            df = df.drop(columns=["sort"])

        # Criação do gráfico
        fig = px.bar(
            df,
            x="linha",
            y="tempo",
            color=choice,
            barmode="stack",
            color_discrete_map=COLOR_DICT,
            title="Detalhes de Tempo",
            labels={
                "tempo": "Tempo (min)",
                "linha": "Linha",
                choice: choice.capitalize(),
            },
            template=template.value,
            custom_data=["problema", "causa", "data_registro", "data_hora"],
        )

        tick_color = "gray" if template == TemplateType.LIGHT else "lightgray"

        fig.update_traces(
            hovertemplate=(
                "Linha: %{x}<br>"
                "Tempo: %{y}<br>"
                "Problema: %{customdata[0]}<br>"
                "Causa: %{customdata[1]}<br>"
                "Dia: %{customdata[2]}<br>"
                "Hora: %{customdata[3]}"
            )
        )

        # Atualizar layout
        fig.update_layout(
            xaxis=dict(
                categoryorder="category ascending",
                tickvals=df["linha"].unique(),
                tickfont=dict(color=tick_color),
            ),
            yaxis=dict(tickfont=dict(color=tick_color)),
            title_x=0.5,
            xaxis_title="Linha",
            yaxis_title="Tempo (min)",
            legend_title=choice.capitalize(),
            plot_bgcolor="RGBA(0,0,0,0.01)",
            margin=dict(t=40, b=40, l=40, r=40),
        )

        return dcc.Graph(figure=fig)
