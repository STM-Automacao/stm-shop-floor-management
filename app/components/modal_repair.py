"""
Autor: Bruno Tomaz
Data: 25/01/2024
Módulo que contém o layout e as funções de callback do Modal de Reparos.
"""

import json
from io import StringIO as stringIO

import dash_ag_grid as dag
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
                            [dmc.Radio(l, value=v, color=c) for v, l, c in MODAL_RADIO],
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
                            checked=True,
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
            html.Hr(),
            dbc.Row(id="grid-repair-modal", children=[]),
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
        Input("store-df-repair_heat_turn_tuple", "data"),
        Input("store-annotations_repair_turn_list_tuple", "data"),
    ],
)
def update_graph_repair_modal(value, checked, df_tuple, ann_tuple):
    """
    Função que atualiza o gráfico de reparos por turno.
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
    df = df_dict[value]
    annotations = list_dict[value]

    fig = indicators.get_heat_turn(df, IndicatorType.REPAIR, annotations, annotations_check=checked)

    return fig


@callback(
    Output("graph-repair-modal-2", "figure"),
    [
        Input("store-info", "data"),
        Input("store-prod", "data"),
    ],
)
def update_graph_repair_modal_2(info, prod):
    """
    Função que atualiza o gráfico de reparos por turno.
    """
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
    """
    Função que atualiza o gráfico de perdas por turno.
    """
    if not info:
        raise PreventUpdate

    df_maq_info_cadastro = pd.read_json(stringIO(info), orient="split")

    df = indicators.get_time_lost(df_maq_info_cadastro, IndicatorType.REPAIR, turn)

    fig = indicators.get_bar_lost(df, turn, IndicatorType.REPAIR, checked)

    return fig


@callback(
    Output("grid-repair-modal", "children"),
    [
        Input("store-info", "data"),
        Input("radio-items", "value"),
    ],
)
def update_grid_repair_modal(data_info, turn):
    """
    Função que atualiza o grid de eficiência do modal.
    """
    if data_info is None:
        raise PreventUpdate

    # Carregue a string JSON em um DataFrame
    df_maq_info_cadastro = pd.read_json(stringIO(data_info), orient="split")

    # Crie o DataFrame
    df = indicators.get_time_lost(df_maq_info_cadastro, IndicatorType.REPAIR, turn)
    df = indicators.adjust_df_for_bar_lost(df, IndicatorType.REPAIR)

    # Ordenar por linha, data_hora_registro
    df = df.sort_values(by=["linha", "data_hora_registro"])

    column_defs = [
        {
            "field": "fabrica",
            "sortable": True,
            "resizable": True,
            "cellClass": "center-aligned-cell",
            "headerClass": "center-aligned-header",
            "flex": 1,
        },
        {
            "field": "linha",
            "filter": True,
            "sortable": True,
            "resizable": True,
            "cellClass": "center-aligned-cell",
            "headerClass": "center-aligned-header",
            "flex": 1,
        },
        {
            "field": "maquina_id",
            "filter": True,
            "sortable": True,
            "resizable": True,
            "cellClass": "center-aligned-cell",
            "headerClass": "center-aligned-header",
            "flex": 1,
        },
        {
            "field": "motivo_nome",
            "headerName": "Motivo",
            "filter": True,
            "resizable": True,
            "sortable": True,
            "flex": 2,
        },
        {
            "field": "problema",
            "sortable": True,
            "resizable": True,
            "tooltipField": "problema",
            "flex": 2,
        },
        {
            "field": "tempo_registro_min",
            "headerName": "Tempo Parada",
            "sortable": True,
            "resizable": True,
            "flex": 1,
        },
        {
            "field": "desconto_min",
            "headerName": "Tempo descontado",
            "sortable": True,
            "resizable": True,
            "cellClass": "center-aligned-cell",
            "headerClass": "center-aligned-header",
            "flex": 1,
        },
        {
            "field": "excedente",
            "headerName": "Tempo que afeta",
            "sortable": True,
            "resizable": True,
            "cellClass": "center-aligned-cell",
            "headerClass": "center-aligned-header",
            "flex": 1,
        },
        {
            "field": "data_hora_registro",
            "headerName": "Inicio Parada",
            "sortable": True,
            "resizable": True,
            "flex": 2,
        },
        {
            "field": "data_hora_final",
            "headerName": "Fim Parada",
            "sortable": True,
            "resizable": True,
            "flex": 2,
        },
    ]
    grid = dag.AgGrid(
        id="AgGrid-repair-modal",
        columnDefs=column_defs,
        rowData=df.to_dict("records"),
        columnSize="responsiveSizeToFit",
        dashGridOptions={"pagination": True, "paginationAutoPageSize": True},
        style={"height": "600px"},
    )

    return grid
