"""
Módulo com dados de Batidas de massa.
"""

from io import StringIO

import dash_bootstrap_components as dbc
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from dash import Input, Output, callback, html
from dash_bootstrap_templates import ThemeSwitchAIO
from pcp.frontend.components_pcp import ComponentsPcpBuilder
from pcp.helpers.cache_pcp import PcpDataCache

from app import app

# =========================================== Variáveis ========================================== #
pcp_data = PcpDataCache(app)
update_massa_cache = pcp_data.cache_massa_data
scheduler = BackgroundScheduler()
pcp_builder = ComponentsPcpBuilder()

# ================================================================================================ #
#                                              LAYOUT                                              #
# ================================================================================================ #
layout = [
    # =========================================== Body =========================================== #
    html.H1("Batidas de Massa", className="text-center mt-3 mb-3"),
    dbc.Row(
        dbc.Col(
            pcp_builder.generate_segmented_btn("batidas", ["Turno", "Total"], "Turno"),
            md=3,
            class_name="d-flex justify-content-center align-items-center",
        ),
        justify="end",
        align="center",
        class_name="mb-3",
    ),
    dbc.Row(
        dbc.Card(
            [
                dbc.CardHeader("Batidas por Dia"),
                dbc.CardBody(id="massadas"),
            ],
            class_name="p-0",
        ),
        class_name="mb-3",
    ),
    dbc.Row(
        dbc.Card(
            [
                dbc.CardHeader("Batidas por Semana"),
                dbc.CardBody(id="massadas-week"),
            ],
            class_name="p-0",
        ),
        class_name="mb-3",
    ),
]

# ================================================================================================ #
#                                            CALLBACK'S                                            #
# ================================================================================================ #


# ===================================== Atualização Dos Cards ==================================== #
@callback(
    Output("massadas", "children"),
    [
        Input("df_sum", "data"),
        Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
        Input("segmented-btn-pcp-batidas", "value"),
    ],
)
def update_massadas_card(data, theme, choice):
    """
    Atualiza o conteúdo do card de massadas.

    Args:
        data (str): Os dados no formato JSON para atualizar o card.

    Returns:
        dbc.Table: A tabela gerada a partir dos dados fornecidos.
        Retorna a mensagem "Sem dados disponíveis." se data for None.
    """

    if data is None:
        return "Sem dados disponíveis."

    # Carregar os dados
    # pylint: disable=no-member
    df = pd.read_json(StringIO(data), orient="split")

    # Renomear as colunas
    df.columns = [
        "Data",
        "Turno",
        "Fábrica",
        "Batidas Cheias(qtd)",
        "Batidas Cheias(Peso)",
        "Batidas Reprocesso(qtd)",
        "Batidas Reprocesso(Peso)",
        "Batidas Bolinha(qtd)",
        "Batidas Bolinha(peso)",
        "Baguete Total(un)",
        "Bolinha Total(un)",
    ]

    # ----------------------- Filtro ----------------------- #
    df_filter = {
        "Turno": df,
        "Total": df.groupby(["Data", "Fábrica"]).sum().drop(columns="Turno").reset_index(),
    }
    df = df_filter[choice]

    # Ajustar o formato da data
    df["Data"] = pd.to_datetime(df["Data"]).dt.strftime("%d/%m")

    table = pcp_builder.create_grid_pcp(df, 1, theme)

    return table


@callback(
    Output("massadas-week", "children"),
    [
        Input("df_week", "data"),
        Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
        Input("segmented-btn-pcp-batidas", "value"),
    ],
)
def update_massadas_week_card(data, theme, choice):
    """
    Atualiza o cartão de semana de massadas com os dados fornecidos.

    Parâmetros:
    - data: str ou None. Os dados a serem exibidos no cartão.
        Se for None, exibe a mensagem "Sem dados disponíveis."

    Retorna:
    - table: dbc.Table. A tabela gerada a partir dos dados fornecidos.
    """

    if data is None:
        return "Sem dados disponíveis."

    df = pd.read_json(StringIO(data), orient="split")

    df.columns = [
        "Ano",
        "Semana",
        "Data Inicial",
        "Turno",
        "Fábrica",
        "Batidas Cheias(qtd)",
        "Batidas Cheias(Peso)",
        "Batidas Reprocesso(qtd)",
        "Batidas Reprocesso(Peso)",
        "Batidas Bolinha(qtd)",
        "Batidas Bolinha(peso)",
        "Baguete Total(un)",
        "Bolinha Total(un)",
    ]

    # pylint: disable=no-member
    df.drop(columns=["Ano"], inplace=True)

    # ----------------------- Filtro ----------------------- #
    df_filter = {
        "Turno": df,
        "Total": df.groupby(["Semana", "Data Inicial", "Fábrica"])
        .sum()
        .drop(columns="Turno")
        .reset_index(),
    }
    df = df_filter[choice]

    df["Data Inicial"] = pd.to_datetime(df["Data Inicial"]).dt.strftime("%d/%m")

    table = pcp_builder.create_grid_pcp(df, 2, theme)

    return table
