"""
Módulo com a aba do PCP.
"""

from io import StringIO

import dash_bootstrap_components as dbc
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from dash import Input, Output, callback, dcc
from pcp.cache_pcp import PcpDataCache

from app import app

# =========================================== Variáveis ========================================== #
pcp_data = PcpDataCache(app)
update_massa_cache = pcp_data.cache_massa_data
scheduler = BackgroundScheduler()

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
    return (
        pcp_data.cache.get("df_sum"),
        pcp_data.cache.get("df_week"),
    )


# ===================================== Atualização Dos Cards ==================================== #
@callback(
    Output("massadas", "children"),
    Input("df_sum", "data"),
)
def update_massadas_card(data):
    if data is None:
        return "Sem dados disponíveis."

    df = pd.read_json(StringIO(data), orient="split")

    table = dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True)

    return table


@callback(
    Output("massadas-week", "children"),
    Input("df_week", "data"),
)
def update_massadas_week_card(data):
    if data is None:
        return "Sem dados disponíveis."

    df = pd.read_json(StringIO(data), orient="split")

    table = dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True)

    return table
