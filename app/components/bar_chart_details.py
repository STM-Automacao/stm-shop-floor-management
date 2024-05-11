"""
Module for creating a bar chart with details based on provided data.
"""

import pandas as pd
import seaborn as sns
from dash import dcc
from helpers.my_types import BSColorsEnum, IndicatorType, TemplateType
from plotly import express as px
from service.df_for_indicators import DFIndicators


class BarChartDetails:
    """
    Represents a class for creating bar chart details based on provided data.
    """

    def __init__(self, df_maq_stopped: pd.DataFrame, df_production: pd.DataFrame):
        self.df_indicator = DFIndicators(df_maq_stopped, df_production)

    def create_bar_chart_details(
        self,
        dataframe: pd.DataFrame,
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
            dataframe, indicator, turn, working_minutes=working
        )

        # Garantis que data_registro tenha apenas o dia
        df["data_registro"] = pd.to_datetime(df["data_registro"]).dt.date

        # Filtro pelo dia, caso tenha sido selecionado
        df = (
            df[df["data_registro"] == pd.to_datetime(selected_data).date()]
            if selected_data is not None
            else df
        )

        # Filtro pelo motivo, causa ou problema
        motivos = df[choice].unique()

        # Definir cores
        palette = sns.color_palette("tab20", len(motivos)).as_hex()

        color_dict = dict(zip(motivos, palette))

        if choice == "motivo":
            # Criar coluna sort para ordenar os dados
            df["sort"] = (
                df["motivo"].map({"Rodando": 0, "Parada Programada": 2, "Limpeza": 1}).fillna(9)
            )

            # Ordenar por sort e tempo_registro_min
            df = df.sort_values(
                by=["linha", "sort", "data_registro", "tempo"],
                ascending=[True, True, True, False],
            )

            # Remover a coluna sort
            df = df.drop(columns=["sort"])

            # Mapear cores
            color_dict = {
                "Parada de 5 minutos ou menos": BSColorsEnum.BLUE_DELFT_COLOR.value,
                "Não apontado": BSColorsEnum.GREY_600_COLOR.value,
                "Ajustes": BSColorsEnum.TEAL_COLOR.value,
                "Manutenção": BSColorsEnum.SPACE_CADET_COLOR.value,
                "Qualidade": BSColorsEnum.WARNING_COLOR.value,
                "Fluxo": BSColorsEnum.PINK_COLOR.value,
                "Parada Programada": BSColorsEnum.DANGER_COLOR.value,
                "Setup": BSColorsEnum.SECONDARY_COLOR.value,
                "Limpeza": BSColorsEnum.PRIMARY_COLOR.value,
                "Rodando": BSColorsEnum.SUCCESS_COLOR.value,
            }

        # Criação do gráfico
        fig = px.bar(
            df,
            x="linha",
            y="tempo",
            color=choice,
            barmode="stack",
            color_discrete_map=color_dict,
            title="Detalhes de Tempo",
            labels={
                "tempo": "Tempo (min)",
                "linha": "Linha",
                choice: choice.capitalize(),
            },
            template=template.value,
        )

        tick_color = "gray" if template == TemplateType.LIGHT else "lightgray"

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
