"""This module contains the layout for the production cards page."""

from io import StringIO

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
from dash import Input, Output, callback, html
from dash.exceptions import PreventUpdate
from management.components import production_cards

# ============================================ Layout ============================================ #
layout = dmc.Card(id="production-card", shadow="md")


# =========================================== Callback =========================================== #
@callback(
    Output("production-card", "children"),
    [
        Input("store-info", "data"),
        Input("store-prod", "data"),
        Input("store-df-caixas-cf", "data"),
        Input("store-df-caixas-cf-tot", "data"),
    ],
)
def update_production_card(store_info, store_prod, store_caixas, caixas_cf_tot):
    """
    Update the production card based on the given store information and store production data.

    Args:
        store_info (str): JSON string containing store information.
        store_prod (str): JSON string containing store production data.

    Returns:
        list: A list containing the updated production card components.

    Raises:
        PreventUpdate: If either store_info or store_prod is empty or None.
    """
    if not store_info or not store_prod:
        raise PreventUpdate

    pcards = production_cards.ProductionCards()

    df_maq_info = pd.DataFrame(pd.read_json(StringIO(store_info), orient="split"))
    df_maq_prod = pd.DataFrame(pd.read_json(StringIO(store_prod), orient="split"))
    df_caixas = pd.DataFrame(pd.read_json(StringIO(store_caixas), orient="split"))
    df_caixas_cf_tot = (
        pd.DataFrame(pd.read_json(StringIO(caixas_cf_tot), orient="split"))
        if caixas_cf_tot
        else pd.DataFrame(columns=["QTD"])
    )

    total_estoque = df_caixas_cf_tot["QTD"].sum()

    return [
        dbc.Row(pcards.create_card(df_maq_info, df_maq_prod)),
        html.Hr(),
        dbc.Row(pcards.create_card(df_maq_info, df_maq_prod, today=True)),
        html.Hr(),
        dbc.Row(pcards.create_card(df_maq_info, df_caixas, cf=True, total=int(total_estoque))),
    ]
