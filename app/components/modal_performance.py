"""
Modal de Performance
Criado por: Bruno Tomaz
Data: 25/01/2024
"""

import json
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
    dbc.ModalHeader("Performance por Turno", class_name="inter"),
    dbc.ModalBody(
        [
            dbc.Row(
                [
                    dbc.Col(
                        dmc.RadioGroup(
                            [dmc.Radio(l, value=v, color=c) for v, l, c in MODAL_RADIO],
                            id="radio-items-performance",
                            value="MAT",
                            className="inter",
                        ),
                        md=4,
                    ),
                    dbc.Col(
                        dmc.Switch(
                            id="annotations-switch-performance",
                            label="Anotações",
                            size="sm",
                            radius="lg",
                            className="mb-1 inter",
                            checked=True,
                        ),
                        md=2,
                    ),
                ],
                justify="between",
            ),
            dbc.Spinner(
                children=dcc.Graph(id="graph-performance-modal"),
                size="lg",
                color="danger",
            ),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(id="graph-performance-modal-2"), md=6),
                    dbc.Col(
                        [
                            dbc.Row(
                                [
                                    dmc.Switch(
                                        id="perdas-switch-performance",
                                        label="Agrupado",
                                        size="sm",
                                        radius="lg",
                                        className="mb-1 inter",
                                        checked=True,
                                    ),
                                    dcc.Graph(id="graph-performance-modal-perdas"),
                                ]
                            ),
                            dbc.Row(),  # Terá um input de ações aqui
                        ],
                        md=6,
                    ),
                ]
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

# ======================================== Modal Callback ======================================= #


@callback(
    Output("graph-performance-modal", "figure"),
    [
        Input("radio-items-performance", "value"),
        Input("annotations-switch-performance", "checked"),
        Input("store-df_perf_heat_turn_tuple", "data"),
        Input("store-annotations_perf_turn_list_tuple", "data"),
    ],
)
def update_graph_performance_modal(
    radio_items_value,
    checked,
    df_tuple,
    ann_tuple,
):
    """
    Callback do gráfico de performance do modal
    """
    if not df_tuple:
        raise PreventUpdate

    # Carregue a string JSON em uma lista
    df_list_json = json.loads(df_tuple)
    ann_tuple_json = json.loads(ann_tuple)

    # Converta cada elemento da lista de volta em um DataFrame
    df_list = [pd.read_json(stringIO(df_json), orient="split") for df_json in df_list_json]
    annotations_list_tuple = [json.loads(lst_json) for lst_json in ann_tuple_json]

    # Converta a lista em uma tupla e desempacote
    noturno, matutino, vespertino = tuple(df_list)
    ann_not, ann_mat, ann_ves = tuple(annotations_list_tuple)

    # Criar um dicionário com os DataFrames
    df_dict = {"NOT": noturno, "MAT": matutino, "VES": vespertino}
    list_dict = {"NOT": ann_not, "MAT": ann_mat, "VES": ann_ves}

    # Selecionar o DataFrame correto
    df = df_dict[radio_items_value]
    annotations = list_dict[radio_items_value]

    fig = indicators.get_heat_turn(
        df, IndicatorType.PERFORMANCE, annotations, annotations_check=checked
    )

    return fig


@callback(
    Output("graph-performance-modal-2", "figure"),
    [
        Input("store-info", "data"),
        Input("store-prod", "data"),
    ],
)
def update_graph_performance_modal_2(store_info, store_prod):
    """
    Callback do gráfico de barras de performance do modal
    """
    if not store_info or not store_prod:
        raise PreventUpdate

    df_maq_info_cadastro = pd.read_json(stringIO(store_info), orient="split")
    df_maq_info_prod_cad = pd.read_json(stringIO(store_prod), orient="split")

    df = times_data.get_perf_data(df_maq_info_cadastro, df_maq_info_prod_cad)

    fig = indicators.get_bar_turn(df, IndicatorType.PERFORMANCE)

    return fig


@callback(
    Output("graph-performance-modal-perdas", "figure"),
    [
        Input("store-info", "data"),
        Input("perdas-switch-performance", "checked"),
        Input("radio-items-performance", "value"),
    ],
)
def update_graph_performance_modal_perdas(store_info, checked, turn):
    """
    Callback do gráfico de perdas do modal
    """
    if not store_info:
        raise PreventUpdate

    df_maq_info_cadastro = pd.read_json(stringIO(store_info), orient="split")

    df = indicators.get_time_lost(df_maq_info_cadastro, IndicatorType.PERFORMANCE, turn)

    fig = indicators.get_bar_lost(df, turn, IndicatorType.PERFORMANCE, checked)

    return fig
