"""
    Esta é a página de gestão da produção.
    - Autor: Bruno Tomaz
    - Data de criação: 13/03/2024
"""

from io import StringIO

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
from components import btn_modal, grid_eff, grid_occ, modal_estoque, modal_history
from dash import Input, Output, State, callback, html
from dash.exceptions import PreventUpdate
from dash_bootstrap_templates import ThemeSwitchAIO
from dash_iconify import DashIconify
from helpers.my_types import IndicatorType

radio_itens_turn = btn_modal.create_radio_btn_turn("management")

# ========================================== Layout ============================================ #
layout = html.Div(
    [
        dbc.Row(dbc.Col(btn_modal.btn_opt, md=3), className="mt-2"),
        dbc.Card(
            [
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
                                    id="dates-provider-1",
                                    children=dmc.DatePicker(
                                        id="date-picker-1",
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
                        dbc.Row(
                            dbc.Card(
                                id="grid-occ-modal",
                                className="mt-2 shadow-lg p-2 mb-2 rounded",
                            ),
                            className="p-2",
                        ),
                        html.Hr(),
                        dbc.Row(
                            dbc.Card(
                                id="grid-eff-modal-management",
                                className="mt-2 shadow-lg p-2 mb-2 rounded",
                            ),
                            className="p-2",
                        ),
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
# =================================== Details Of The Production ================================== #
@callback(
    [
        Output("date-picker-1", "minDate"),
        Output("date-picker-1", "maxDate"),
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


# ---------------------- Grid ---------------------- #
@callback(
    Output("grid-occ-modal", "children"),
    [
        Input("store-info", "data"),
        Input("store-prod", "data"),
        Input("radio-items-management", "value"),
        Input("date-picker-1", "value"),
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


@callback(
    Output("grid-eff-modal-management", "children"),
    [
        Input("store-df-eff", "data"),
        Input("radio-items-management", "value"),
        Input("date-picker-1", "value"),
        Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    ],
)
def update_grid_eff_modal_management(data, turn, data_picker, theme):
    """
    Função que atualiza o grid de eficiência do modal.
    """
    if data is None:
        raise PreventUpdate

    # Carregue a string JSON em um DataFrame
    df = pd.read_json(StringIO(data), orient="split")

    # Filtra pelo turno
    if turn != "TOT":
        df = df[df["turno"] == turn]

    # Se houver data, filtrar pelo dia selecionado
    if data_picker is not None:
        df["data_registro"] = pd.to_datetime(df["data_registro"]).dt.date
        df = df[(df["data_registro"]) == pd.to_datetime(data_picker).date()]

    ge = grid_eff.GridEff()

    return [
        html.H5("Eficiência", className="text-center"),
        ge.create_grid_eff(df, theme),
    ]
