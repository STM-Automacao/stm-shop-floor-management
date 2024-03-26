"""
    Esta é a página de gestão da produção.
    - Autor: Bruno Tomaz
    - Data de criação: 13/03/2024
"""

from io import StringIO

import dash_bootstrap_components as dbc
import pandas as pd
from components import production_cards
from dash import Input, Output, callback, html
from dash.exceptions import PreventUpdate

# ========================================== Layout ============================================ #
layout = html.Div(
    [
        dbc.Card(id="production-card", class_name="mb-3 mt-2"),
    ],
    id="management-content",
)

# ========================================= Callbacks =========================================== #


# ---------------- Production Cards ---------------- #
@callback(
    Output("production-card", "children"),
    [
        Input("store-info", "data"),
        Input("store-prod", "data"),
        Input("store-df-caixas-cf", "data"),
    ],
)
def update_production_card(store_info, store_prod, store_caixas):
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

    return [
        dbc.CardHeader("Produção"),
        dbc.CardBody(
            [
                dbc.Row(pcards.create_card(df_maq_info, df_maq_prod.copy())),
                html.Hr(),
                dbc.Row(pcards.create_card(df_maq_info, df_maq_prod, today=True)),
                html.Hr(),
                dbc.Row(pcards.create_card(df_maq_info, df_caixas, cf=True)),
            ]
        ),
    ]
