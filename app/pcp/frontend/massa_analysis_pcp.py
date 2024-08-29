"""
Módulo para Análise de Massadas e pães e suas perdas ou sobras
"""

from io import StringIO

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from components.grid_aggrid import GridAgGrid
from dash import Input, Output, callback, dcc, html
from dash_bootstrap_templates import ThemeSwitchAIO
from helpers.my_types import (
    GRID_FORMAT_NUMBER_BR,
    GRID_NUMBER_COLS,
    GRID_STR_NUM_COLS,
    TemplateType,
)
from pcp.helpers.functions_pcp import AuxFuncPcp

# =========================================== Variáveis ========================================== #
pcp_builder = GridAgGrid()
afc = AuxFuncPcp()

# ================================================================================================ #
#                                              LAYOUT                                              #
# ================================================================================================ #
layout = dbc.Stack(
    [
        dbc.Row(dmc.Card(id="pcp-graph-analysis", shadow="sm", className="mb-3")),
        dbc.Row(dmc.Card(id="pcp-paes-analysis", shadow="sm")),
    ]
)


# ================================================================================================ #
#                                             CALLBACKS                                            #
# ================================================================================================ #
@callback(
    Output("pcp-paes-analysis", "children"),
    [
        Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
        Input("store-df-caixas-cf", "data"),
        Input("df_week", "data"),
    ],
)
def update_paes(theme, prod_recheio, week_massa):
    """
    Atualiza o card análise de pães.

    Args:
        theme (str): O tema atual do dashboard.
        data (str): Os dados no formato JSON para atualizar o card.

    Returns:
        dbc.Table: A tabela gerada a partir dos dados fornecidos.
        Retorna a mensagem "Sem dados disponíveis." se data for None.
    """

    if prod_recheio is None or week_massa is None:
        return "Sem dados disponíveis."

    # Carregar os dados
    # pylint: disable=no-member
    df = pd.read_json(StringIO(prod_recheio), orient="split")
    df_week = pd.read_json(StringIO(week_massa), orient="split")

    # =============================== Lidando Com Dados Do Recheio =============================== #
    # Ajustar os dados
    df_prod_recheio = afc.adjust_prod(df)

    # Cria uma coluna para a quantidade caso o produto contenha "BOL", e a coluna QTD passa a ser 0
    mask = df_prod_recheio["PRODUTO"].str.contains("BOL ")
    df_prod_recheio["QTD_BOL"] = mask.astype(int) * df_prod_recheio["QTD"]  # True = 1, False = 0
    df_prod_recheio["QTD"] = (1 - mask.astype(int)) * df_prod_recheio["QTD"]

    # Agrupar por semana, fabrica
    df_prod_recheio = (
        df_prod_recheio.groupby(["year", "week", "Data_Semana", "FABRICA"])
        .sum()
        .drop(columns="PRODUTO")
        .reset_index()
    )

    # Renomear as colunas
    df_prod_recheio = df_prod_recheio.rename(columns={"FABRICA": "Fabrica"})

    # =============================== Lidando Com Dados Das Massas =============================== #
    df_week = (
        df_week.groupby(["year", "week", "Data_Semana", "Fabrica"])
        .sum()
        .drop(columns="Turno")
        .reset_index()
    )

    # Reordenar colunas
    cols = df_week.columns.tolist()
    cols = cols[:4] + cols[-2:]
    df_week = df_week[cols]

    # =================================== Unir As Duas Tabelas =================================== #
    # Garantir que as duas datas sejam datetime
    df_prod_recheio["Data_Semana"] = pd.to_datetime(df_prod_recheio["Data_Semana"])
    df_week["Data_Semana"] = pd.to_datetime(df_week["Data_Semana"])

    df_prod_recheio = df_prod_recheio.merge(
        df_week, on=["year", "week", "Data_Semana", "Fabrica"], how="outer"
    )

    # Cria coluna com a diferença entre as quantidades entre baguete e QTD
    df_prod_recheio["baguete_sobra"] = df_prod_recheio["Baguete_Total"] - df_prod_recheio["QTD"]
    df_prod_recheio["bolinha_sobra"] = df_prod_recheio["Bolinha_Total"] - df_prod_recheio["QTD_BOL"]

    # Ordenar a tabela
    df_prod_recheio = df_prod_recheio.sort_values(
        ["year", "week", "Fabrica"], ascending=[False, False, True]
    )

    # Formatar a data para dd/mm
    df_prod_recheio.Data_Semana = df_prod_recheio.Data_Semana.dt.strftime("%d/%m")

    # ============================== Definições De Estilo E Colunas ============================== #
    class_rules = {"cellClassRules": {"text-light bg-danger": "params.value > 0"}}

    # Definições personalizadas
    defs = [
        {
            "headerName": "Ano",
            "headerTooltip": "Ano da semana",
            "field": "year",
            **GRID_NUMBER_COLS,
            "maxWidth": 125,
        },
        {
            "headerName": "Semana",
            "headerTooltip": "Número da semana",
            "field": "week",
            **GRID_NUMBER_COLS,
            "maxWidth": 125,
        },
        {
            "headerName": "Data Inicial",
            "headerTooltip": "Data de início da semana",
            "field": "Data_Semana",
            "maxWidth": 125,
        },
        {"headerName": "Fábrica", "headerTooltip": "Fábrica", "field": "Fabrica", "maxWidth": 125},
        {
            "headerName": "Baguetes",
            "headerClass": "center-aligned-group-header",
            "children": [
                {
                    "headerName": "Produzida",
                    "headerTooltip": "Quantidade de baguetes produzidas (unidades)",
                    "field": "Baguete_Total",
                    **GRID_FORMAT_NUMBER_BR,
                    **GRID_STR_NUM_COLS,
                },
                {
                    "headerName": "Consumida",
                    "headerTooltip": "Quantidade de baguetes consumidas (unidades)",
                    "field": "QTD",
                    **GRID_FORMAT_NUMBER_BR,
                    **GRID_STR_NUM_COLS,
                },
                {
                    "headerName": "Diferença",
                    "headerTooltip": "Diferença de baguetes produzidas e consumidas (unidades)",
                    "field": "baguete_sobra",
                    **GRID_FORMAT_NUMBER_BR,
                    **class_rules,
                    **GRID_STR_NUM_COLS,
                },
            ],
        },
        {
            "headerName": "Bolinhas",
            "headerClass": "center-aligned-group-header",
            "children": [
                {
                    "headerName": "Produzida",
                    "headerTooltip": "Quantidade de bolinhas produzidas (unidades)",
                    "field": "Bolinha_Total",
                    **GRID_FORMAT_NUMBER_BR,
                    **GRID_STR_NUM_COLS,
                },
                {
                    "headerName": "Consumida",
                    "headerTooltip": "Quantidade de bolinhas consumidas (unidades)",
                    "field": "QTD_BOL",
                    **GRID_FORMAT_NUMBER_BR,
                    **GRID_STR_NUM_COLS,
                },
                {
                    "headerName": "Diferença",
                    "headerTooltip": "Diferença de bolinhas produzidas e consumidas (unidades)",
                    "field": "bolinha_sobra",
                    **GRID_FORMAT_NUMBER_BR,
                    **class_rules,
                    **GRID_STR_NUM_COLS,
                },
            ],
        },
    ]

    title = html.H1("Análise Massa Batida vs Consumo de Pães", className="text-center mt-3 mb-3")

    table = pcp_builder.create_grid_ag(df_prod_recheio, "grid-pcp-4", theme, defs)

    return [title, table]


@callback(
    Output("pcp-graph-analysis", "children"),
    [
        Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
        Input("store-df-caixas-cf", "data"),
        Input("df_week", "data"),
    ],
)
def graph_paes(theme, prod_recheio, week_massa):
    """
    Atualiza o card análise de pães.

    Args:
        theme (str): O tema atual do dashboard.
        data (str): Os dados no formato JSON para atualizar o card.

    Returns:
        dbc.Table: A tabela gerada a partir dos dados fornecidos.
        Retorna a mensagem "Sem dados disponíveis." se data for None.
    """

    if prod_recheio is None or week_massa is None:
        return "Sem dados disponíveis."

    template = TemplateType.LIGHT if theme else TemplateType.DARK

    # Carregar os dados
    # pylint: disable=no-member
    df = pd.read_json(StringIO(prod_recheio), orient="split")
    df_week = pd.read_json(StringIO(week_massa), orient="split")

    # =============================== Lidando Com Dados Do Recheio =============================== #
    # Ajustar os dados
    df_prod_recheio = afc.adjust_prod(df)

    # Cria uma coluna para a quantidade caso o produto contenha "BOL", e a coluna QTD passa a ser 0
    mask = df_prod_recheio["PRODUTO"].str.contains("BOL ")
    df_prod_recheio["QTD_BOL"] = mask.astype(int) * df_prod_recheio["QTD"]  # True = 1, False = 0
    df_prod_recheio["QTD"] = (1 - mask.astype(int)) * df_prod_recheio["QTD"]

    # Agrupar por semana, fabrica
    df_prod_recheio = (
        df_prod_recheio.groupby(["year", "week", "Data_Semana", "FABRICA"])
        .sum()
        .drop(columns="PRODUTO")
        .reset_index()
    )

    # Renomear as colunas
    df_prod_recheio = df_prod_recheio.rename(columns={"FABRICA": "Fabrica"})

    # =============================== Lidando Com Dados Das Massas =============================== #
    df_week = (
        df_week.groupby(["year", "week", "Data_Semana", "Fabrica"])
        .sum()
        .drop(columns="Turno")
        .reset_index()
    )

    # =================================== Unir As Duas Tabelas =================================== #
    # Garantir que as duas datas sejam datetime
    df_prod_recheio["Data_Semana"] = pd.to_datetime(df_prod_recheio["Data_Semana"])
    df_week["Data_Semana"] = pd.to_datetime(df_week["Data_Semana"])

    df_prod_recheio = df_prod_recheio.merge(
        df_week, on=["year", "week", "Data_Semana", "Fabrica"], how="outer"
    )

    # Cria coluna com a diferença entre as quantidades entre baguete e QTD
    df_prod_recheio["baguete_sobra"] = df_prod_recheio["Baguete_Total"] - df_prod_recheio["QTD"]
    df_prod_recheio["bolinha_sobra"] = df_prod_recheio["Bolinha_Total"] - df_prod_recheio["QTD_BOL"]

    df_prod_recheio["perda_bag"] = (
        df_prod_recheio.baguete_sobra / df_prod_recheio.Baguete_Total * 100
    )
    df_prod_recheio["perda_bol"] = (
        df_prod_recheio.bolinha_sobra / df_prod_recheio.Bolinha_Total * 100
    )

    # Separar a perda de baguete da fábrica 1 e 2
    df_prod_recheio["perda_bag_fab1"] = np.where(
        df_prod_recheio["Fabrica"] == "Fab. 1", df_prod_recheio["perda_bag"], 0
    )
    df_prod_recheio["perda_bag_fab2"] = np.where(
        df_prod_recheio["Fabrica"] == "Fab. 2", df_prod_recheio["perda_bag"], 0
    )

    # Preencher os valores nulos com 0
    df_prod_recheio["perda_bol"] = df_prod_recheio["perda_bol"].fillna(0)

    # Em perda_bol, lidar com valores -inf
    df_prod_recheio["perda_bol"] = df_prod_recheio["perda_bol"].replace(-np.inf, 0)

    # Ordenar a tabela
    df_prod_recheio = df_prod_recheio.sort_values(
        ["year", "week", "Fabrica"], ascending=[False, False, True]
    )

    # Filtrar os dados mantendo apenas os últimos 3 meses
    df_prod_recheio = df_prod_recheio[
        df_prod_recheio["Data_Semana"] >= pd.Timestamp.now() - pd.DateOffset(months=3)
    ]

    # Formatar a data para dd/mm
    df_prod_recheio.Data_Semana = df_prod_recheio.Data_Semana.dt.strftime("%d/%m")

    # Criar gráfico de barras, com os valores de perda de baguete e bolinha por semana
    fig = px.bar(
        df_prod_recheio,
        x="Data_Semana",
        y=["perda_bag_fab1", "perda_bag_fab2", "perda_bol"],
        title="Perda de Pães por Semana",
        barmode="group",
        labels={"value": "Perda (%)", "variable": "Tipo de Pão"},
        template=template.value,
        # facet_col="Fabrica",
    )

    fig.update_layout(
        xaxis_title="Semana",
        yaxis_title="Perda (%)",
        legend_title="Tipo de Pão",
        legend=dict(title_font=dict(size=12)),
    )

    # Ajustar o nome das colunas para o gráfico pra perda_bag_fab1 seja "Baguete Fab. 1"
    fig.for_each_trace(
        lambda t: t.update(name=t.name.replace("perda_bag_", "Baguete ").replace("fab", "Fab. "))
    )
    fig.for_each_trace(lambda t: t.update(name=t.name.replace("perda_bol", "Bolinha")))

    # Configurar o hover com o nome da fábrica, tipo de pão e perda
    fig.update_traces(
        hovertemplate="<br>".join(
            [
                "Semana: %{x}",
                "Tipo de Pão: %{fullData.name}",
                "Perda: %{y:.2f}%",
            ]
        )
    )

    lost_mean = df_prod_recheio["perda_bag"].mean()
    lost_mean_bol = df_prod_recheio["perda_bol"].mean()
    lost_mean = (lost_mean + lost_mean_bol) / 2

    # Adicionar traço com a média de perda
    fig.add_trace(
        go.Scatter(
            x=df_prod_recheio["Data_Semana"],
            y=[lost_mean] * len(df_prod_recheio),
            mode="lines",
            name="Média de Perda",
            line=dict(color="gold", width=1),
        )
    )

    return [dcc.Graph(figure=fig)]
