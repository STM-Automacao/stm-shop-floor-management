"""
    Esta é a página de gestão da produção.
    - Autor: Bruno Tomaz
    - Data de criação: 13/03/2024
"""

from io import StringIO

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
from components import (
    bar_chart_details,
    btn_modal,
    grid_occ,
    modal_estoque,
    modal_history,
    production_cards,
)
from dash import Input, Output, State, callback, html
from dash.exceptions import PreventUpdate
from dash_bootstrap_templates import ThemeSwitchAIO
from dash_iconify import DashIconify
from helpers.my_types import IndicatorType, TemplateType

radio_itens_turn = btn_modal.create_radio_btn_turn("management")

# ========================================== Layout ============================================ #
layout = html.Div(
    [
        dbc.Row(dbc.Col(btn_modal.btn_opt, md=3), className="mt-2"),
        dbc.Card(id="production-card", class_name="mb-3 mt-2"),
        dbc.Card(
            [
                dbc.CardHeader("Detalhes da Produção do Mês Corrente"),
                dbc.CardBody(
                    [
                        dbc.Row(
                            dbc.Col(
                                radio_itens_turn,
                                class_name="radio-group",
                                md=4,
                                xl=4,
                            ),
                        ),
                        dbc.Row(
                            dbc.Col(
                                dmc.DatesProvider(
                                    id="dates-provider",
                                    children=dmc.DatePicker(
                                        id="date-picker",
                                        label="Data",
                                        placeholder="Selecione uma data",
                                        valueFormat="dddd - D MMM, YYYY",
                                        firstDayOfWeek=0,
                                        clearable=True,
                                        variant="filled",
                                        leftSection=DashIconify(icon="uiw:date"),
                                    ),
                                    settings={"locale": "pt-br"},
                                ),
                                md=4,
                                xl=2,
                            ),
                            className="inter",
                            justify="center",
                        ),
                        dbc.Row(id="bar-chart-details"),
                        dbc.Row(id="grid-occ-modal"),
                    ]
                ),
            ],
        ),
        # Incluir detalhes de produção
        # ---------------- Modal History ---------------- #
        dmc.Modal(
            children=modal_history.layout,
            id="modal-history-eff",
            fullScreen=True,
            title="Histórico",
            opened=False,
            className="inter",
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
    Output("modal-history-eff", "opened"),
    [Input("history-btn", "n_clicks")],
    [State("modal-history-eff", "opened")],
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
                dbc.Row(
                    pcards.create_card(df_maq_info, df_caixas, cf=True, total=int(total_estoque))
                ),
            ]
        ),
    ]


# =================================== Details Of The Production ================================== #
@callback(
    [
        Output("date-picker", "minDate"),
        Output("date-picker", "maxDate"),
    ],
    Input("store-info", "data"),
)
def details_picker(info):
    """
    Creates and returns a date picker component for efficiency indicator.

    Args:
        info: The information to be used for creating the date picker component.

    Returns:
        The created date picker component.

    Raises:
        PreventUpdate: If the info parameter is None.
    """

    if info is None:
        raise PreventUpdate

    df = pd.read_json(StringIO(info), orient="split")

    min_date = pd.to_datetime(df["data_registro"]).min().date()
    max_date = pd.to_datetime(df["data_registro"]).max().date()

    return str(min_date), str(max_date)


@callback(
    Output("bar-chart-details", "children"),
    [
        Input("store-info", "data"),
        Input("radio-items-management", "value"),
        Input("date-picker", "value"),
        Input("store-df_working_time", "data"),
        Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    ],
)
def details_bar_chart(info, turn, data_picker, working, toggle_theme):
    """
    Creates a collapsed bar chart details based on the provided information.

    Args:
        info (str): The JSON string containing the information for the bar chart.
        turn (str): The turn value for the bar chart.
        data_picker (str): The data picker value for the bar chart.
        working (bool): Indicates whether the bar chart is in working mode or not.
        toggle_theme (bool): Indicates whether the bar chart should use a light or dark template.

    Returns:
        dict: The collapsed bar chart details.

    Raises:
        PreventUpdate: If the info parameter is None.
    """

    if info is None:
        raise PreventUpdate

    template = TemplateType.LIGHT if toggle_theme else TemplateType.DARK

    # Carrega o string json em um dataframe
    df_info = pd.read_json(StringIO(info), orient="split")
    df_working = pd.read_json(StringIO(working), orient="split")

    bcd = bar_chart_details.BarChartDetails(df_info)

    return bcd.create_bar_chart_details(
        IndicatorType.EFFICIENCY, template, turn, data_picker, df_working
    )


# ---------------------- Grid ---------------------- #
@callback(
    Output("grid-occ-modal", "children"),
    [
        Input("store-info", "data"),
        Input("store-prod", "data"),
        Input("radio-items-management", "value"),
        Input("date-picker", "value"),
        Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    ],
)
def update_grid_occ_modal(info, prod, turn, data_picker, theme):
    """
    Função que atualiza o grid de eficiência do modal.
    """
    if info is None:
        raise PreventUpdate

    # Carregue a string JSON em um DataFrame
    df_info = pd.read_json(StringIO(info), orient="split")
    df_prod = pd.read_json(StringIO(prod), orient="split")

    goe = grid_occ.GridOcc(df_info, df_prod)

    turns = {
        "NOT": "Noturno",
        "MAT": "Matutino",
        "VES": "Vespertino",
        "TOT": "Geral",
    }

    return [
        html.H5(f"Ocorrências - {turns[turn]}", className="text-center"),
        goe.create_grid_occ(df_info, IndicatorType.EFFICIENCY, turn, theme, data_picker),
    ]
