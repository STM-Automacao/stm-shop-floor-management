"""Módulo para Análise de Pasta."""

import time
from io import StringIO

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
from components.grid_aggrid import GridAgGrid
from dash import Input, Output, callback, html
from dash_bootstrap_templates import ThemeSwitchAIO
from helpers.my_types import GRID_FORMAT_NUMBER_BR, GRID_NUMBER_COLS, GRID_STR_NUM_COLS
from pcp.helpers.functions_pcp import AuxFuncPcp
from pcp.helpers.types_pcp import RENDIMENTO_PASTA_PAO

# =========================================== Variáveis ========================================== #

pcp_builder = GridAgGrid()
afc = AuxFuncPcp()

# ================================================================================================ #
#                                              LAYOUT                                              #
# ================================================================================================ #

layout = dbc.Stack(
    [
        dbc.Row(dmc.Card(id="pcp-pasta-analysis", shadow="sm")),
    ]
)

# ================================================================================================ #
#                                             CALLBACKS                                            #
# ================================================================================================ #


@callback(
    Output("pcp-pasta-analysis", "children"),
    [
        Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
        Input("store-df-caixas-cf", "data"),
        Input("df_pasta_week", "data"),
    ],
)
def func_name(theme, prod_recheio, week_massa):
    """
    Atualiza o card análise de pasta.

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
    df_prod = pd.read_json(StringIO(prod_recheio), orient="split")
    df_week = pd.read_json(StringIO(week_massa), orient="split")

    # =============================== Lidando Com Dados Do Recheio =============================== #
    # Ajustar os dados de produção
    df_prod_recheio = afc.adjust_prod(df_prod)

    # Calcula quantidade de massa gasta por produto
    df_prod_recheio.QTD = df_prod_recheio.QTD * df_prod_recheio.PRODUTO.map(RENDIMENTO_PASTA_PAO)

    # Mapeamento de substituições
    prod_dict = {
        r".*TRD.*": "Tradicional",
        r".*CEB.*": "Cebola",
        r".*PIC.*": "Picante",
        r".*DOCE.*": "Doce",
    }

    # Usar expressão regular para substituir com base no mapeamento
    df_prod_recheio.PRODUTO = df_prod_recheio.PRODUTO.replace(prod_dict, regex=True)

    # Agrupar por semana, fabrica, dia, produto
    df_prod_recheio = (
        df_prod_recheio.groupby(["year", "week", "Data_Semana", "FABRICA", "PRODUTO"])
        .sum()
        .reset_index()
    )

    # Transformar coluna QTD em inteiro
    df_prod_recheio.QTD = df_prod_recheio.QTD.astype(int)

    # Transformar os produtos em colunas
    df_prod_recheio = df_prod_recheio.pivot_table(
        index=["year", "week", "Data_Semana", "FABRICA"],
        columns="PRODUTO",
        values="QTD",
        fill_value=0,
    ).reset_index()

    # Renomear colunas com capitalização
    df_prod_recheio.columns = df_prod_recheio.columns.str.title()

    # =================================== Lidando Com Bisnagas =================================== #

    # ================================= Dados De Batidas De Pasta ================================ #
    df_week = (
        df_week.groupby(["year", "week", "Data_Semana", "Fabrica"])
        .sum()
        .drop(columns="Turno")
        .reset_index()
    )

    df_week.columns = df_week.columns.str.title()

    # ==================================== Junção Das Tabelas ==================================== #
    # Garantir que as duas datas sejam datetime
    df_prod_recheio.Data_Semana = pd.to_datetime(df_prod_recheio.Data_Semana)
    df_week.Data_Semana = pd.to_datetime(df_week.Data_Semana)

    # Unir as duas tabelas
    df_prod_recheio = df_prod_recheio.merge(
        df_week, on=["Year", "Week", "Data_Semana", "Fabrica"], how="outer"
    )

    time.sleep(1)

    # ============================ Diferença Entre Produção E Consumo ============================ #
    # Cria coluna com a diferença entre as quantidades produzidas e consumidas
    for col in df_prod_recheio.columns[4:8]:
        df_prod_recheio[f"{col} Sobra"] = df_prod_recheio[f"{col}_Peso"] - df_prod_recheio[col]

    # Ordenar a tabela
    df_prod_recheio = df_prod_recheio.sort_values(
        ["Year", "Week", "Fabrica"], ascending=[False, False, True]
    )

    # ============================== Definições De Estilo E Colunas ============================== #
    # Ajustar a data para dd/mm
    df_prod_recheio.Data_Semana = df_prod_recheio.Data_Semana.dt.strftime("%d/%m")

    # Regras de estilo para células
    class_rules = {"cellClassRules": {"text-light bg-danger": "params.value > 0"}}

    # Definições personalizadas
    defs = [
        {
            "headerName": "Ano",
            "headerTooltip": "Ano da semana",
            "field": "Year",
            **GRID_NUMBER_COLS,
            "maxWidth": 125,
            "minWidth": 80,
        },
        {
            "headerName": "Semana",
            "headerTooltip": "Número da semana",
            "field": "Week",
            **GRID_NUMBER_COLS,
            "maxWidth": 125,
            "minWidth": 100,
        },
        {
            "headerName": "Data Inicial",
            "headerTooltip": "Data de início da semana",
            "field": "Data_Semana",
            "maxWidth": 125,
            "minWidth": 97,
        },
        {
            "headerName": "Fábrica",
            "headerTooltip": "Fábrica",
            "field": "Fabrica",
            "maxWidth": 125,
            "minWidth": 100,
        },
        {
            "headerName": "Tradicional",
            "headerTooltip": "Produção de pasta tradicional",
            "headerClass": "center-aligned-group-header",
            "children": [
                {
                    "headerName": "Produzido",
                    "field": "Tradicional_Peso",
                    "headerTooltip": "Produção de pasta tradicional(kg)",
                    **GRID_FORMAT_NUMBER_BR,
                    **GRID_STR_NUM_COLS,
                },
                {
                    "headerName": "Consumido",
                    "field": "Tradicional",
                    "headerTooltip": "Consumo de pasta tradicional(kg)",
                    **GRID_FORMAT_NUMBER_BR,
                    **GRID_STR_NUM_COLS,
                },
                {
                    "headerName": "Diferença",
                    "field": "Tradicional Sobra",
                    "headerTooltip": "Diferença de pasta tradicional(kg)",
                    **GRID_FORMAT_NUMBER_BR,
                    **GRID_STR_NUM_COLS,
                    **class_rules,
                },
            ],
        },
        {
            "headerName": "Picante",
            "headerTooltip": "Produção de pasta picante",
            "headerClass": "center-aligned-group-header",
            "children": [
                {
                    "headerName": "Produzido",
                    "field": "Picante_Peso",
                    "headerTooltip": "Produção de pasta picante(kg)",
                    **GRID_FORMAT_NUMBER_BR,
                    **GRID_STR_NUM_COLS,
                },
                {
                    "headerName": "Consumido",
                    "field": "Picante",
                    "headerTooltip": "Consumo de pasta picante(kg)",
                    **GRID_FORMAT_NUMBER_BR,
                    **GRID_STR_NUM_COLS,
                },
                {
                    "headerName": "Diferença",
                    "field": "Picante Sobra",
                    "headerTooltip": "Diferença de pasta picante(kg)",
                    **GRID_FORMAT_NUMBER_BR,
                    **GRID_STR_NUM_COLS,
                    **class_rules,
                },
            ],
        },
        {
            "headerName": "Cebola",
            "headerTooltip": "Produção de pasta de cebola",
            "headerClass": "center-aligned-group-header",
            "children": [
                {
                    "headerName": "Produzido",
                    "field": "Cebola_Peso",
                    "headerTooltip": "Produção de pasta de cebola(kg)",
                    **GRID_FORMAT_NUMBER_BR,
                    **GRID_STR_NUM_COLS,
                },
                {
                    "headerName": "Consumido",
                    "field": "Cebola",
                    "headerTooltip": "Consumo de pasta de cebola(kg)",
                    **GRID_FORMAT_NUMBER_BR,
                    **GRID_STR_NUM_COLS,
                },
                {
                    "headerName": "Diferença",
                    "field": "Cebola Sobra",
                    "headerTooltip": "Diferença de pasta de cebola(kg)",
                    **GRID_FORMAT_NUMBER_BR,
                    **GRID_STR_NUM_COLS,
                    **class_rules,
                },
            ],
        },
        {
            "headerName": "Doce",
            "headerTooltip": "Produção de pasta doce",
            "headerClass": "center-aligned-group-header",
            "children": [
                {
                    "headerName": "Produzido",
                    "field": "Doce_Peso",
                    "headerTooltip": "Produção de pasta doce(kg)",
                    **GRID_FORMAT_NUMBER_BR,
                    **GRID_STR_NUM_COLS,
                },
                {
                    "headerName": "Consumido",
                    "field": "Doce",
                    "headerTooltip": "Consumo de pasta doce(kg)",
                    **GRID_FORMAT_NUMBER_BR,
                    **GRID_STR_NUM_COLS,
                },
                {
                    "headerName": "Diferença",
                    "field": "Doce Sobra",
                    "headerTooltip": "Diferença de pasta doce(kg)",
                    **GRID_FORMAT_NUMBER_BR,
                    **GRID_STR_NUM_COLS,
                    **class_rules,
                },
            ],
        },
    ]

    # Título da tabela
    title = html.H1(
        "Análise de Pasta Produzida vs Pasta Consumida nos Pães", className="text-center"
    )

    table = pcp_builder.create_grid_ag(df_prod_recheio, "pcp-pasta-analysis-grid", theme, defs)

    return [title, table]
