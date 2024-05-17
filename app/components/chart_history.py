"""
    Este módulo contém a classe ChartHistory que é responsável por criar gráficos de barras
"""

import pandas as pd
from dash import dcc
from helpers.my_types import COLOR_DICT, IndicatorType, TemplateType
from plotly import express as px
from service.df_for_indicators import DFIndicators


class ChartHistory:
    """
    Classe responsável por criar gráficos de barras para exibir os detalhes de tempo das paradas.

    Attributes:
        df_indicator (DFIndicators): A instância da classe DFIndicators.

    Methods:
        create_bar_chart_details(df, template, working=None):
            Cria um gráfico de barras com os detalhes de tempo das paradas.
    """

    def __init__(self):
        self.df_indicator = DFIndicators

    def create_bar_chart_details(
        self,
        df: pd.DataFrame,
        template: TemplateType,
        working: pd.DataFrame = None,
    ) -> dcc.Graph:
        """
        Cria um gráfico de barras para exibir os detalhes de tempo das paradas.

        Args:
            df (pd.DataFrame): O DataFrame contendo os dados das paradas.
            template (TemplateType): O tipo de template a ser utilizado no gráfico.
            working (pd.DataFrame, optional): O DataFrame contendo os dados de trabalho.
                Defaults to None.

        Returns:
            dcc.Graph: O gráfico de barras com os detalhes de tempo das paradas.
        """

        # Instanciar DFIndicators
        class_indicators = DFIndicators(df)

        # Ajustar df para indicador de eficiência
        df = class_indicators.adjust_df_for_bar_lost(
            df, IndicatorType.EFFICIENCY, working_minutes=working
        )

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

        # Ajustar a coluna data_registro para exibir apenas o dia e mês
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
            x="motivo",
            y="tempo",
            color="motivo",
            barmode="stack",
            color_discrete_map=COLOR_DICT,
            title="Paradas de Produção",
            labels={
                "tempo": "Tempo (min)",
                "motivo": "Motivo",
            },
            template=template.value,
            custom_data=["problema", "causa", "data_registro", "data_hora", "linha"],
        )

        tick_color = "gray" if template == TemplateType.LIGHT else "lightgray"

        fig.update_traces(
            hovertemplate=(
                "Tempo: %{y}<br>"
                "Problema: %{customdata[0]}<br>"
                "Causa: %{customdata[1]}<br>"
                "Linha: %{customdata[4]}<br>"
                "Dia: %{customdata[2]}<br>"
                "Hora: %{customdata[3]}"
            )
        )

        # Atualizar layout
        fig.update_layout(
            xaxis=dict(
                categoryorder="category ascending",
                tickvals=df["motivo"].unique(),
                tickfont=dict(color=tick_color),
            ),
            yaxis=dict(tickfont=dict(color=tick_color)),
            title_x=0.5,
            xaxis_title="Motivo",
            yaxis_title="Tempo (min)",
            legend_title="Paradas",
            plot_bgcolor="RGBA(0,0,0,0.01)",
            margin=dict(t=40, b=40, l=40, r=40),
        )

        return dcc.Graph(figure=fig)

    def create_icicle_chart(
        self,
        df: pd.DataFrame,
        path_choice: str,
        template: TemplateType,
    ) -> dcc.Graph:
        """
        Cria um gráfico de icicle para visualizar as paradas de produção.

        Args:
            df (pd.DataFrame): O dataframe contendo os dados das paradas de produção.
            path_choice (str): A opção de caminho para o gráfico (Motivo, Equipamento ou Turno).
            template (TemplateType): O template do gráfico.

        Returns:
            dcc.Graph: O gráfico de icicle das paradas de produção.
        """

        # Instanciar DFIndicators
        class_indicators = DFIndicators(df)

        # Ajustar df para indicador de eficiência
        df = class_indicators.adjust_df_for_bar_lost(df, IndicatorType.EFFICIENCY)

        # Remove onde não há motivo informado
        df = df[df["motivo"] != "Não apontado"].reset_index(drop=True)

        # Preenche equipamentos nulos
        df["equipamento"] = df["equipamento"].fillna("Sem Equipamento")

        # Se path_choice for equipamento, remove linhas sem equipamento
        if path_choice == "Equipamento":
            df = df[df["equipamento"] != "Sem Equipamento"].reset_index(drop=True)

        # Se motivo for limpeza, causa deve ser igual ao problema
        df.loc[df["motivo"] == "Limpeza", "causa"] = df["problema"]

        # Criar uma string contendo cada linha única
        linhas = df["linha"].unique()
        linhas = [f"Linha {linha}<br>" for linha in linhas]
        linhas = "".join(linhas) if len(linhas) > 1 else linhas[0]

        path_dict = {
            "Motivo": [px.Constant(linhas), "motivo", "turno", "equipamento", "problema", "causa"],
            "Equipamento": [
                px.Constant(linhas),
                "equipamento",
                "turno",
                "motivo",
                "problema",
                "causa",
            ],
            "Turno": [px.Constant(linhas), "turno", "motivo", "equipamento", "problema", "causa"],
        }

        # Criação do gráfico
        fig = px.icicle(
            df,
            path=path_dict[path_choice],
            values="tempo",
            color="motivo",
            color_discrete_map=COLOR_DICT,
            title="Paradas de Produção",
            height=800,
            template=template.value,
        )

        # Atualizar layout
        fig.update_layout(
            plot_bgcolor="RGBA(0,0,0,0.01)",
        )

        # Adicionar a porcentagem
        fig.update_traces(textinfo="label+percent parent")

        fig.update_traces(
            hovertemplate="Label: %{label}<br>Tempo: %{value}<br>Percentual: %{percentParent:.2%}"
        )

        return dcc.Graph(figure=fig)
