"""
Módulo com a aba do PCP.
"""

from io import StringIO

import dash_bootstrap_components as dbc
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from dash import Input, Output, callback, dcc
from dash_bootstrap_templates import ThemeSwitchAIO
from pcp.cache_pcp import PcpDataCache
from pcp.grid_pcp import GridPcp

from app import app

# =========================================== Variáveis ========================================== #
pcp_data = PcpDataCache(app)
update_massa_cache = pcp_data.cache_massa_data
scheduler = BackgroundScheduler()
grid_pcp = GridPcp()

# ====================================== Cache Em Background ===================================== #

scheduler.add_job(update_massa_cache, "interval", minutes=5)
scheduler.start()

# ================================================================================================ #
#                                              LAYOUT                                              #
# ================================================================================================ #
layout = [
    dcc.Store(id="df_sum"),
    dcc.Store(id="df_week"),
    dcc.Interval(id="interval-component", interval=1000 * 60 * 5, n_intervals=0),
    # =========================================== Body =========================================== #
    dbc.Row(
        dbc.Card(id="massadas", body=True),
        class_name="p-2",
    ),
    dbc.Row(dbc.Card(id="massadas-week", body=True), class_name="p-2"),
]

# ================================================================================================ #
#                                            CALLBACK'S                                            #
# ================================================================================================ #


# ===================================== Atualização Do Store ===================================== #
@callback(
    Output("df_sum", "data"),
    Output("df_week", "data"),
    Input("interval-component", "n_intervals"),
)
def update_store(_):
    """
    Atualiza o store.

    Retorna um tuple contendo os dados do cache "df_sum" e "df_week".

    Parâmetros:
    _ (qualquer): Parâmetro não utilizado.

    Retorno:
    tuple: Um tuple contendo os dados do cache "df_sum" e "df_week".
    """
    return (
        pcp_data.cache.get("df_sum"),
        pcp_data.cache.get("df_week"),
    )


# ===================================== Atualização Dos Cards ==================================== #
@callback(
    Output("massadas", "children"),
    [Input("df_sum", "data"), Input(ThemeSwitchAIO.ids.switch("theme"), "value")],
)
def update_massadas_card(data, theme):
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

    # Ajustar o formato da data
    df["Data"] = pd.to_datetime(df["Data"]).dt.strftime("%d/%m")

    table = grid_pcp.create_grid_pcp(df, 1, theme)

    return table


@callback(
    Output("massadas-week", "children"),
    [Input("df_week", "data"), Input(ThemeSwitchAIO.ids.switch("theme"), "value")],
)
def update_massadas_week_card(data, theme):
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

    df["Data Inicial"] = pd.to_datetime(df["Data Inicial"]).dt.strftime("%d/%m")

    table = grid_pcp.create_grid_pcp(df, 2, theme)

    return table
