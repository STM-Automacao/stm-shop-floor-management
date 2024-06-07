"""
Módulo para Análise de Massadas e pães e suas perdas ou sobras
"""

from io import StringIO

import dash_bootstrap_components as dbc
import pandas as pd
from dash import Input, Output, callback, html
from dash_bootstrap_templates import ThemeSwitchAIO
from pcp.frontend.components_pcp import ComponentsPcpBuilder
from pcp.helpers.functions_pcp import AuxFuncPcp
from pcp.helpers.types_pcp import GRID_NUMBER_COLS

# =========================================== Variáveis ========================================== #
pcp_builder = ComponentsPcpBuilder()
afc = AuxFuncPcp()

# ================================================================================================ #
#                                              LAYOUT                                              #
# ================================================================================================ #
layout = dbc.Stack(
    [
        dbc.Row(dbc.Card(id="pcp-paes-analysis", class_name="p-0 shadow-sm", body=True)),
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

    if prod_recheio is None:
        return "Sem dados disponíveis."

    # Carregar os dados
    # pylint: disable=no-member
    df = pd.read_json(StringIO(prod_recheio), orient="split")
    df_week = pd.read_json(StringIO(week_massa), orient="split")

    # =============================== Lidando Com Dados Do Recheio =============================== #
    # Ajustar os dados
    df_prod_recheio = afc.adjust_prod(df)

    # Cria uma coluna para a quantidade caso o produto contenha "BOL", e a coluna QTD passa a ser 0
    mask = df_prod_recheio["PRODUTO"].str.contains("BOL")
    df_prod_recheio["QTD_BOL"] = mask.astype(int) * df_prod_recheio["QTD"]  # True = 1, False = 0
    df_prod_recheio["QTD"] = (1 - mask.astype(int)) * df_prod_recheio["QTD"]

    # Agrupar por semana, fabrica
    df_prod_recheio = (
        df_prod_recheio.groupby(["week", "Data_Semana", "FABRICA"])
        .sum()
        .drop(columns="PRODUTO")
        .reset_index()
    )

    # Renomear as colunas
    df_prod_recheio = df_prod_recheio.rename(columns={"FABRICA": "Fabrica"})

    # =============================== Lidando Com Dados Das Massas =============================== #
    df_week = (
        df_week.groupby(["week", "Data_Semana", "Fabrica"])
        .sum()
        .drop(columns="Turno")
        .reset_index()
    )

    # Reordenar colunas
    cols = df_week.columns.tolist()
    cols = cols[:3] + cols[-2:]
    df_week = df_week[cols]

    # =================================== Unir As Duas Tabelas =================================== #
    # Garantir que as duas datas sejam datetime
    df_prod_recheio["Data_Semana"] = pd.to_datetime(df_prod_recheio["Data_Semana"])
    df_week["Data_Semana"] = pd.to_datetime(df_week["Data_Semana"])

    df_prod_recheio = df_prod_recheio.merge(
        df_week, on=["week", "Data_Semana", "Fabrica"], how="outer"
    )

    # Cria coluna com a diferença entre as quantidades entre baguete e QTD
    df_prod_recheio["baguete_sobra"] = df_prod_recheio["Baguete_Total"] - df_prod_recheio["QTD"]
    df_prod_recheio["bolinha_sobra"] = df_prod_recheio["Bolinha_Total"] - df_prod_recheio["QTD_BOL"]

    # ============================== Definições De Estilo E Colunas ============================== #
    class_rules = {"cellClassRules": {"text-light bg-danger": "params.value < 0"}}

    # Definições personalizadas
    defs = [
        {
            "headerName": "Semana",
            "headerTooltip": "Número da semana",
            "field": "week",
            **GRID_NUMBER_COLS,
        },
        {
            "headerName": "Data Inicial",
            "headerTooltip": "Data de início da semana",
            "field": "Data_Semana",
        },
        {"headerName": "Fábrica", "headerTooltip": "Fábrica", "field": "Fabrica"},
        {
            "headerName": "Baguetes",
            "headerClass": "center-aligned-group-header",
            "children": [
                {
                    "headerName": "Baguete Produzida",
                    "headerTooltip": "Quantidade de baguetes produzidas (unidades)",
                    "field": "Baguete_Total",
                    **GRID_NUMBER_COLS,
                },
                {
                    "headerName": "Baguete Consumida",
                    "headerTooltip": "Quantidade de baguetes consumidas (unidades)",
                    "field": "QTD",
                    **GRID_NUMBER_COLS,
                },
                {
                    "headerName": "Baguete Sobra",
                    "headerTooltip": "Diferença de baguetes produzidas e consumidas (unidades)",
                    "field": "baguete_sobra",
                    **class_rules,
                    **GRID_NUMBER_COLS,
                },
            ],
        },
        {
            "headerName": "Bolinhas",
            "headerClass": "center-aligned-group-header",
            "children": [
                {
                    "headerName": "Bolinha Produzida",
                    "headerTooltip": "Quantidade de bolinhas produzidas (unidades)",
                    "field": "Bolinha_Total",
                    **GRID_NUMBER_COLS,
                },
                {
                    "headerName": "Bolinha Consumida",
                    "headerTooltip": "Quantidade de bolinhas consumidas (unidades)",
                    "field": "QTD_BOL",
                    **GRID_NUMBER_COLS,
                },
                {
                    "headerName": "Bolinha Sobra",
                    "headerTooltip": "Diferença de bolinhas produzidas e consumidas (unidades)",
                    "field": "bolinha_sobra",
                    **class_rules,
                    **GRID_NUMBER_COLS,
                },
            ],
        },
    ]

    title = html.H1("Pães - Análise", className="text-center mt-3 mb-3")

    table = pcp_builder.create_grid_pcp(df_prod_recheio, 4, theme, defs)

    return [title, table]
