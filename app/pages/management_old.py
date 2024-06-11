"""
    Esta é a página de gestão da produção.
    - Autor: Bruno Tomaz
    - Data de criação: 13/03/2024
"""

from io import StringIO

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
from components import btn_modal, grid_aggrid, grid_occ
from dash import Input, Output, callback, html
from dash.exceptions import PreventUpdate
from dash_bootstrap_templates import ThemeSwitchAIO
from dash_iconify import DashIconify
from helpers.my_types import (
    GRID_FORMAT_NUMBER_BR,
    GRID_NUMBER_COLS,
    GRID_STR_NUM_COLS,
    IndicatorType,
)

# =========================================== Variáveis ========================================== #
gag = grid_aggrid.GridAgGrid()
radio_itens_turn = btn_modal.create_radio_btn_turn("management")

# ================================================================================================ #
#                                              LAYOUT                                              #
# ================================================================================================ #
layout = dmc.Stack(
    [
        dmc.Card(
            [
                html.H3("Tabela de Eficiência", className="text-center mb-3"),
                dbc.Row(id="eficiencia-table-management"),
            ],
            shadow="sm",
        ),
        # NOTE: Formatar daqui em diante
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
                    ]
                ),
            ],
        ),
    ],
    id="management-content",
)


# ================================================================================================ #
#                                             CALLBACKS                                            #
# ================================================================================================ #


# ======================================= Eficiencia Table ======================================= #
@callback(
    Output("eficiencia-table-management", "children"),
    [
        Input("store-df-eff", "data"),
        Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    ],
)
def update_eficiencia_table(data, theme):
    """
    Função que atualiza a tabela de eficiência.
    """
    if data is None:
        raise PreventUpdate

    # Carregue a string JSON em um DataFrame
    df = pd.read_json(StringIO(data), orient="split")

    # Garantir que data registro é pd.datetime apenas com a data
    df.data_registro = pd.to_datetime(df.data_registro).dt.strftime("%d/%m")

    # Ajustar eficiência
    df.eficiencia = (df.eficiencia * 100).round(2)

    # Ajustar produção esperada para int
    df.producao_esperada = df.producao_esperada.astype(int)

    defs = [
        {"field": "fabrica", "headerName": "Fábrica", "maxWidth": 150, **GRID_NUMBER_COLS},
        {"field": "linha", "headerName": "Linha", "maxWidth": 150, **GRID_NUMBER_COLS},
        {"field": "maquina_id", "headerName": "Máquina"},
        {"field": "data_registro", "headerName": "Data", "maxWidth": 150},
        {"field": "turno", "headerName": "Turno", "maxWidth": 150},
        {"field": "tempo", "headerName": "Tempo Parada", **GRID_NUMBER_COLS},
        {"field": "desconto", "headerName": "Tempo Descontado", **GRID_NUMBER_COLS},
        {"field": "tempo_esperado", "headerName": "Tempo Esperado", **GRID_NUMBER_COLS},
        {
            "field": "producao_esperada",
            "headerName": "Deveria Produzir",
            **GRID_STR_NUM_COLS,
            **GRID_FORMAT_NUMBER_BR,
        },
        {
            "field": "total_produzido",
            "headerName": "Produzido",
            **GRID_STR_NUM_COLS,
            **GRID_FORMAT_NUMBER_BR,
        },
        {"field": "eficiencia", "headerName": "Eficiência %", **GRID_NUMBER_COLS},
    ]

    return gag.create_grid_ag(df, "eff-table-management", theme, defs)


# NOTE: Formatar daqui pra baixo


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
