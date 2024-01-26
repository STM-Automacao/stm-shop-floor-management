"""
Modal de Reparos
"""

from io import StringIO as stringIO

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
from dash import callback, dcc, html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

# pylint: disable=E0401
from graphics.indicators_turn import IndicatorsTurn
from helpers.types import MODAL_RADIO, IndicatorType
from service.times_data import TimesData

from app import app

times_data = TimesData()
indicators = IndicatorsTurn()

# ========================================= Modal Layout ======================================== #

layout = [
    dbc.ModalHeader("Reparos por Turno", class_name="inter"),
    dbc.ModalBody(
        [
            dbc.Row(
                [
                    dbc.Col(
                        dmc.RadioGroup(
                            [
                                dmc.Radio(l, value=v, color=c)
                                for v, l, c in MODAL_RADIO
                            ],
                            id="radio-items-repair",
                            value="MAT",
                            className="inter",
                        ),
                        md=4,
                    ),
                    dbc.Col(
                        dmc.Switch(
                            id="annotations-switch-repair",
                            label="Anotações",
                            size="sm",
                            radius="lg",
                            className="mb-1 inter",
                            checked=False,
                        ),
                        md=2,
                    ),
                ],
                justify="between",
            ),
            # dcc.Loading(dcc.Graph(id="graph-repair-modal")),
            dbc.Spinner(
                children=dcc.Graph(id="graph-repair-modal"),
                color="danger",
                size="lg",
            ),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(id="graph-repair-modal-2"), md=6),
                    dbc.Col(
                        [
                            dbc.Row(
                                [
                                    dmc.Switch(
                                        id="perdas-switch-repair",
                                        label="Agrupado",
                                        size="sm",
                                        radius="lg",
                                        className="mb-1 inter",
                                        checked=False,
                                    ),
                                    dcc.Graph(id="graph-repair-modal-perdas"),
                                ]
                            ),
                            dbc.Row(),  # Terá um input de ações
                        ],
                        md=6,
                    ),
                ],
            ),
        ]
    ),
    dbc.ModalFooter(
        dmc.Image(
            # pylint: disable=E1101
            src=app.get_asset_url("Logo Horizontal_PXB.png"),
            width="125px",
            withPlaceholder=True,
        ),
    ),
]

# ======================================== Modal Callbacks ======================================= #


@callback(
    Output("graph-repair-modal", "figure"),
    [
        Input("radio-items-repair", "value"),
        Input("annotations-switch-repair", "checked"),
        Input("store-info", "data"),
        Input("store-prod", "data"),
    ],
)
def update_graph_repair_modal(radio_value, checked, info, prod):
    if not info or not prod:
        raise PreventUpdate

    df_maq_info_cadastro = pd.read_json(stringIO(info), orient="split")
    df_maq_info_prod_cad = pd.read_json(stringIO(prod), orient="split")

    df = times_data.get_repair_data(df_maq_info_cadastro, df_maq_info_prod_cad)
    df = df[df["turno"] == radio_value]

    fig = indicators.get_heat_turn(
        df, IndicatorType.REPAIR, annotations=checked
    )

    return fig


@callback(
    Output("graph-repair-modal-2", "figure"),
    [
        Input("store-info", "data"),
        Input("store-prod", "data"),
    ],
)
def update_graph_repair_modal_2(info, prod):
    if not info or not prod:
        raise PreventUpdate

    df_maq_info_cadastro = pd.read_json(stringIO(info), orient="split")
    df_maq_info_prod_cad = pd.read_json(stringIO(prod), orient="split")

    df = times_data.get_repair_data(df_maq_info_cadastro, df_maq_info_prod_cad)

    fig = indicators.get_bar_turn(df, IndicatorType.REPAIR)

    return fig


@callback(
    Output("graph-repair-modal-perdas", "figure"),
    [
        Input("store-info", "data"),
        Input("perdas-switch-repair", "checked"),
        Input("radio-items-repair", "value"),
    ],
)
def update_graph_repair_modal_perdas(info, checked, turn):
    if not info:
        raise PreventUpdate

    df_maq_info_cadastro = pd.read_json(stringIO(info), orient="split")

    df = indicators.get_time_lost(
        df_maq_info_cadastro, IndicatorType.REPAIR, turn
    )

    fig = indicators.get_bar_lost(df, turn, IndicatorType.REPAIR, checked)

    return fig
