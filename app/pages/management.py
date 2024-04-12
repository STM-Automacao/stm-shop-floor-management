"""
    Esta é a página de gestão da produção.
    - Autor: Bruno Tomaz
    - Data de criação: 13/03/2024
"""

from io import StringIO

import dash_bootstrap_components as dbc
import pandas as pd
from components import btn_modal, modal_estoque, modal_history, production_cards
from dash import Input, Output, State, callback, html
from dash.exceptions import PreventUpdate

# ========================================== Layout ============================================ #
layout = html.Div(
    [
        dbc.Row(dbc.Col(btn_modal.btn_opt, md=3), className="mt-2"),
        dbc.Card(id="production-card", class_name="mb-3 mt-2"),
        # Incluir detalhes de produção
        # ---------------- Modal History ---------------- #
        dbc.Modal(
            children=modal_history.layout,
            id="modal-history-eff",
            size="xl",
            fullscreen="lg-down",
            scrollable=True,
            modal_class_name="inter",
            is_open=False,
        ),
        # ---------------- Modal Estoque ---------------- #
        dbc.Modal(
            children=modal_estoque.layout,
            id="modal-estoque",
            size="xl",
            fullscreen="lg-down",
            scrollable=True,
            modal_class_name="inter",
            is_open=False,
        ),
    ],
    id="management-content",
)


# --------------------- Modal History --------------------- #
@callback(
    Output("modal-history-eff", "is_open"),
    [Input("history-btn", "n_clicks")],
    [State("modal-history-eff", "is_open")],
)
def toggle_modal_history(n, is_open):
    """
    Toggles the history modal.

    Args:
        n (int): The number of clicks on the history button.
        is_open (bool): The current state of the modal.

    Returns:
        bool: The new state of the modal.
    """
    if n:
        return not is_open
    return is_open


@callback(
    Output("modal-estoque", "is_open"),
    [Input("estoque-btn", "n_clicks")],
    [State("modal-estoque", "is_open")],
)
def toggle_modal_estoque(n, is_open):
    """
    Toggles the estoque modal.

    Args:
        n (int): The number of clicks on the estoque button.
        is_open (bool): The current state of the modal.

    Returns:
        bool: The new state of the modal.
    """
    if n:
        return not is_open
    return is_open


# ========================================= Callbacks =========================================== #


# ---------------- Production Cards ---------------- #
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
        dbc.CardHeader("Produção"),
        dbc.CardBody(
            [
                dbc.Row(pcards.create_card(df_maq_info, df_maq_prod)),
                html.Hr(),
                dbc.Row(pcards.create_card(df_maq_info, df_maq_prod, today=True)),
                html.Hr(),
                dbc.Row(pcards.create_card(df_maq_info, df_caixas, cf=True, total=total_estoque)),
            ]
        ),
    ]
