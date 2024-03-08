"""
Module for creating a bar chart with details based on provided data.
"""

import pandas as pd
from dash import dcc
from helpers.types import BSColorsEnum, IndicatorType, TemplateType
from plotly import express as px
from service.times_data import TimesData


class BarChartDetails:
    """
    Represents a class for creating bar chart details based on provided data.
    """

    def __init__(self):
        self.times_data = TimesData()

    def create_bar_chart_details(
        self,
        dataframe: pd.DataFrame,
        indicator: IndicatorType,
        template: TemplateType,
        turn: str,
        selected_data,
        working: pd.DataFrame = None,
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
        df = self.times_data.adjust_df_for_bar_lost(dataframe, indicator, turn, working)

        # Garantis que data_registro tenha apenas o dia
        df["data_registro"] = pd.to_datetime(df["data_registro"]).dt.date

        # Filtro pelo dia, caso tenha sido selecionado
        df = (
            df[df["data_registro"] == pd.to_datetime(selected_data).date()] if selected_data else df
        )

        # Criar coluna sort para ordenar os dados
        df["sort"] = (
            df["motivo_nome"]
            .map({"Rodando": 0, "Parada Programada": 2, "Limpeza Industrial": 1})
            .fillna(9)
        )

        # Ordenar por sort e tempo_registro_min
        df = df.sort_values(
            by=["linha", "sort", "data_registro", "tempo_registro_min"],
            ascending=[True, True, True, False],
        )

        # Remover a coluna sort
        df = df.drop(columns=["sort"])

        # Mapear cores
        color_dict = {
            "5min ou menos": BSColorsEnum.GREY_500_COLOR.value,
            "Motivo não apontado": BSColorsEnum.GREY_600_COLOR.value,
            "Ajustes": BSColorsEnum.GREY_700_COLOR.value,
            "Troca de Bobina": BSColorsEnum.GREY_400_COLOR.value,
            "Reunião": BSColorsEnum.GREY_800_COLOR.value,
            "Limpeza": BSColorsEnum.ORANGE_COLOR.value,
            "Material em Falta": BSColorsEnum.GRAY_COLOR.value,
            "Linha Cheia": BSColorsEnum.TEAL_COLOR.value,
            "Refeição": BSColorsEnum.INFO_COLOR.value,
            "Café e Ginástica Laboral": BSColorsEnum.PRIMARY_COLOR.value,
            "Treinamento": BSColorsEnum.GREY_900_COLOR.value,
            "Troca de Filme": BSColorsEnum.SECONDARY_COLOR.value,
            "Setup de Sabor": BSColorsEnum.PURPLE_COLOR.value,
            "Setup de Tamanho": BSColorsEnum.INDIGO_COLOR.value,
            "Manutenção Elétrica": BSColorsEnum.BLUE_DELFT_COLOR.value,
            "Manutenção Mecânica": BSColorsEnum.SPACE_CADET_COLOR.value,
            "Intervenção de Qualidade": BSColorsEnum.PINK_COLOR.value,
            "Limpeza Industrial": BSColorsEnum.WARNING_COLOR.value,
            "Parada Programada": BSColorsEnum.DANGER_COLOR.value,
            "Rodando": BSColorsEnum.SUCCESS_COLOR.value,
        }

        # Criação do gráfico
        fig = px.bar(
            df,
            x="linha",
            y="tempo_registro_min",
            color="motivo_nome",
            barmode="stack",
            color_discrete_map=color_dict,
            title="Detalhes de Tempo",
            labels={
                "tempo_registro_min": "Tempo (min)",
                "linha": "Linha",
                "motivo_nome": "Motivo",
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
            legend_title="Motivos",
            plot_bgcolor="RGBA(0,0,0,0.01)",
            margin=dict(t=40, b=40, l=40, r=40),
        )

        return dcc.Graph(figure=fig)
