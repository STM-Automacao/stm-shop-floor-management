"""
Modal de Performance
Criado por: Bruno Tomaz
Data: 25/01/2024
"""

import json
from io import StringIO as stringIO

import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd

# pylint: disable=E0401
from components import btn_modal
from dash import callback, dcc, html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from graphics.indicators_turn import IndicatorsTurn
from helpers.types import IndicatorType
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
                        btn_modal.radio_btn_perf,
                        class_name="radio-group",
                        md=3,
                    ),
                ],
            ),
            dbc.Spinner(
                children=dcc.Graph(id="graph-performance-modal"),
                size="lg",
                color="danger",
            ),
            dcc.Graph(
                id="graph-line-modal-2",
                style={"height": "80px"},
            ),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(id="graph-performance-modal-2"), md=6),
                    dbc.Col(
                        [
                            dbc.Row(
                                [
                                    dbc.Switch(
                                        id="perdas-switch-performance",
                                        label="Agrupado",
                                        className="mb-1 inter",
                                        value=True,
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
            html.Hr(),
            dbc.Row(id="grid-performance-modal", children=[]),
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
        Input(f"radio-items-{IndicatorType.PERFORMANCE.value}", "value"),
        Input("store-df_perf_heatmap_tuple", "data"),
        Input("store-annotations_perf_list_tuple", "data"),
    ],
)
def update_graph_performance_modal(
    radio_items_value,
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
    noturno, matutino, vespertino, total, _ = tuple(df_list)
    ann_not, ann_mat, ann_ves, ann_total, _ = tuple(annotations_list_tuple)

    # Criar um dicionário com os DataFrames
    df_dict = {"NOT": noturno, "MAT": matutino, "VES": vespertino, "TOT": total}
    list_dict = {"NOT": ann_not, "MAT": ann_mat, "VES": ann_ves, "TOT": ann_total}

    # Selecionar o DataFrame correto
    df = df_dict[radio_items_value]
    annotations = list_dict[radio_items_value]

    fig = indicators.get_heat_turn(df, IndicatorType.PERFORMANCE, annotations)

    return fig


# ---------------------- Line Chart ---------------------- #
@callback(
    Output("graph-line-modal-2", "figure"),
    [
        Input("store-df-perf", "data"),
        Input(f"radio-items-{IndicatorType.PERFORMANCE.value}", "value"),
    ],
)
def update_graph_line_modal_1(data, turn):
    """
    Função que atualiza o gráfico de linha do modal.
    """
    if data is None:
        raise PreventUpdate

    df = pd.read_json(stringIO(data), orient="split")

    # figure = indicators_geral.plot_daily_efficiency(df, IndicatorType.PERFORMANCE, 4, turn)

    return "figure"


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
        Input("perdas-switch-performance", "value"),
        Input(f"radio-items-{IndicatorType.PERFORMANCE.value}", "value"),
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


@callback(
    Output("grid-performance-modal", "children"),
    [
        Input("store-info", "data"),
        Input(f"radio-items-{IndicatorType.PERFORMANCE.value}", "value"),
    ],
)
def update_grid_performance_modal(data_info, turn):
    """
    Função que atualiza o grid de eficiência do modal.
    """
    if data_info is None:
        raise PreventUpdate

    # Carregue a string JSON em um DataFrame
    df_maq_info_cadastro = pd.read_json(stringIO(data_info), orient="split")

    # Crie o DataFrame
    df = indicators.get_time_lost(df_maq_info_cadastro, IndicatorType.PERFORMANCE, turn)
    df = indicators.adjust_df_for_bar_lost(df, IndicatorType.PERFORMANCE)

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
        id="AgGrid-performance-modal",
        columnDefs=column_defs,
        rowData=df.to_dict("records"),
        columnSize="responsiveSizeToFit",
        dashGridOptions={"pagination": True, "paginationAutoPageSize": True},
        style={"height": "600px"},
    )

    return grid
