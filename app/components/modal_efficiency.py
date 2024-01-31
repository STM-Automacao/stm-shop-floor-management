"""
Modal Module
Criado por: Bruno Tomaz
Data: 23/01/2024
"""
import ast
import json
from io import StringIO as stringIO

# cSpell: words eficiencia fullscreen
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
    dbc.ModalHeader(
        "Eficiência por Turno",
        class_name="inter",
    ),
    dbc.ModalBody(
        [
            dbc.Row(
                [
                    dbc.Col(
                        dmc.RadioGroup(
                            [dmc.Radio(l, value=v, color=c) for v, l, c in MODAL_RADIO],
                            id="radio-items",
                            value="MAT",
                            className="inter",
                        ),
                        md=4,
                    ),
                    dbc.Col(
                        [
                            dmc.Switch(
                                id="annotations-switch-eficiencia",
                                label="Anotações",
                                size="sm",
                                radius="lg",
                                className="mb-1 inter",
                                checked=False,
                            ),
                            dmc.Switch(
                                id="colors-switch-eficiencia",
                                label="Mais Cores",
                                size="sm",
                                radius="lg",
                                className="mb-1 inter",
                                checked=False,
                            ),
                        ],
                        md=2,
                    ),
                ],
                justify="between",
            ),
            # dcc.Loading(dcc.Graph(id="graph-eficiencia-modal")),
            dbc.Spinner(
                children=dcc.Graph(id="graph-eficiencia-modal"),
                size="lg",
                color="danger",
            ),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(id="graph-eficiencia-modal-2"), md=6),
                    dbc.Col(
                        [
                            dbc.Row(
                                [
                                    dmc.Switch(
                                        id="perdas-switch-eficiencia",
                                        label="Agrupado",
                                        size="sm",
                                        radius="lg",
                                        className="mb-1 inter",
                                        checked=True,
                                    ),
                                    dcc.Graph(id="graph-eficiencia-modal-perdas"),
                                ]
                            ),
                            dbc.Row(),  # Input de ações
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


# ======================================= Modal Callbacks ======================================== #
@callback(
    Output("graph-eficiencia-modal", "figure"),
    [
        Input("radio-items", "value"),
        Input("store-df-eff-heatmap-tuple", "data"),
        Input("store-df-eff-annotations-tuple", "data"),
        Input("annotations-switch-eficiencia", "checked"),
        Input("colors-switch-eficiencia", "checked"),
    ],
)
def update_graph_eficiencia_modal(value, df_tuple, ann_tuple, checked, colors):
    """
    Função que atualiza o gráfico de eficiência do modal.
    """
    if df_tuple is None:
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
    df = df_dict[value]
    annotations = list_dict[value]

    figure = indicators.get_eff_heat_turn(
        df, annotations, annotations_check=checked, more_colors=colors
    )

    return figure


@callback(
    Output("graph-eficiencia-modal-2", "figure"),
    [
        Input("store-info", "data"),
        Input("store-prod", "data"),
    ],
)
def update_graph_eficiencia_modal_2(data_info, data_prod):
    """
    Função que atualiza o gráfico de barras de eficiência do modal.
    """
    if data_info is None or data_prod is None:
        raise PreventUpdate

    df_maq_info_cadastro = pd.read_json(stringIO(data_info), orient="split")
    df_maq_info_prod_cad = pd.read_json(stringIO(data_prod), orient="split")

    df = times_data.get_eff_data(df_maq_info_cadastro, df_maq_info_prod_cad)

    figure = indicators.get_eff_bar_turn(df)

    return figure


@callback(
    Output("graph-eficiencia-modal-perdas", "figure"),
    [
        Input("store-info", "data"),
        Input("perdas-switch-eficiencia", "checked"),
        Input("radio-items", "value"),
    ],
)
def update_graph_eficiencia_modal_perdas(data_info, checked, turn):
    """
    Função que atualiza o gráfico de barras de eficiência do modal.
    """
    if data_info is None:
        raise PreventUpdate

    df_maq_info_cadastro = pd.read_json(stringIO(data_info), orient="split")

    df = indicators.get_time_lost(df_maq_info_cadastro, IndicatorType.EFFICIENCY, turn)

    figure = indicators.get_eff_bar_lost(df, turn, checked)

    return figure
