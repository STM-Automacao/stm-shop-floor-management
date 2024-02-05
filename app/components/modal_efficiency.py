"""
Modal Module
Criado por: Bruno Tomaz
Data: 23/01/2024
"""

import json
from io import StringIO as stringIO

import dash_ag_grid as dag

# cSpell: words eficiencia fullscreen sunday
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
from dash import callback, dcc, html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify

# pylint: disable=E0401
from graphics.indicators_turn import IndicatorsTurn
from helpers.types import MODAL_RADIO, IndicatorType
from service.times_data import TimesData

from app import app

times_data = TimesData()
indicators = IndicatorsTurn()
today = pd.Timestamp.now().date()
first_day = pd.Timestamp(today.year, today.month, 1).date()

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
                                checked=True,
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
                    dbc.Row(
                        dbc.Col(
                            dmc.Switch(
                                id="perdas-switch-eficiencia",
                                label="Agrupado",
                                size="sm",
                                radius="lg",
                                className="mb-1 inter",
                                checked=True,
                            ),
                            md=6,
                        ),
                        justify="end",
                    ),
                    dbc.Col(dcc.Graph(id="graph-eficiencia-modal-2"), md=6),
                    dbc.Col(
                        [
                            dbc.Row(
                                [
                                    dcc.Graph(id="graph-eficiencia-modal-perdas"),
                                ]
                            ),
                            dbc.Row(),  # Input de ações
                        ],
                        md=6,
                    ),
                ]
            ),
            html.Hr(),
            html.Div(
                [
                    dbc.Button(
                        "Detalhes",
                        id="detalhes-button",
                        className="mb-3",
                        color="secondary",
                        n_clicks=0,
                    ),
                    dbc.Collapse(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    dbc.Row(
                                        dbc.Col(
                                            dmc.DatePicker(
                                                id="date-picker-eficiencia",
                                                label="Data",
                                                placeholder="Selecione uma data",
                                                inputFormat="dddd - D MMM, YYYY",
                                                locale="pt-br",
                                                firstDayOfWeek="sunday",
                                                minDate=first_day,
                                                maxDate=today,
                                                clearable=True,
                                                className="inter",
                                                icon=DashIconify(icon="clarity:date-line"),
                                            ),
                                            md=4,
                                            xl=2,
                                        ),
                                        class_name="inter",
                                        justify="center",
                                    ),
                                    dbc.Row(
                                        dcc.Graph(id="every-stop-graph"),
                                        class_name="inter",
                                    ),
                                ]
                            ),
                        ),
                        id="detalhes-bar-collapse",
                        is_open=False,
                    ),
                ],
                className="mb-3",
            ),
            dbc.Row(id="grid-eficiencia-modal", children=[]),
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
        Input("store-annotations_eff_turn_list_tuple", "data"),
        Input("annotations-switch-eficiencia", "checked"),
    ],
)
def update_graph_eficiencia_modal(value, df_tuple, ann_tuple, checked):
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

    figure = indicators.get_eff_heat_turn(df, annotations, annotations_check=checked)

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


@callback(
    Output("grid-eficiencia-modal", "children"),
    [
        Input("store-info", "data"),
        Input("radio-items", "value"),
        Input("date-picker-eficiencia", "value"),
        Input("detalhes-bar-collapse", "is_open"),
    ],
)
def update_grid_eficiencia_modal(data_info, turn, data_picker, open_btn):
    """
    Função que atualiza o grid de eficiência do modal.
    """
    if data_info is None:
        raise PreventUpdate

    # Carregue a string JSON em um DataFrame
    df_maq_info_cadastro = pd.read_json(stringIO(data_info), orient="split")

    # Crie o DataFrame
    df = indicators.get_time_lost(df_maq_info_cadastro, IndicatorType.EFFICIENCY, turn)

    # Ordenar por linha, data_hora_registro
    df = df.sort_values(by=["linha", "data_hora_registro"])

    if not open_btn:
        data_picker = None

    # Filtrar por data
    if data_picker is not None:
        df = df[df["data_registro"] == pd.to_datetime(data_picker).date()]

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
            "cellClass": "center-aligned-cell",
            "headerClass": "center-aligned-header",
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
        id="AgGrid-eficiencia-modal",
        columnDefs=column_defs,
        rowData=df.to_dict("records"),
        columnSize="responsiveSizeToFit",
        dashGridOptions={"pagination": True, "paginationAutoPageSize": True},
        style={"height": "600px"},
    )

    return grid


@callback(
    Output("detalhes-bar-collapse", "is_open"),
    [Input("detalhes-button", "n_clicks")],
    [Input("detalhes-bar-collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    """
    Função que abre e fecha o collapse do detalhes.
    """
    if n:
        return not is_open
    return is_open


@callback(
    Output("every-stop-graph", "figure"),
    [
        Input("date-picker-eficiencia", "value"),
        Input("store-info", "data"),
        Input("radio-items", "value"),
    ],
)
def update_every_stop_graph(date, data_info, turn):
    """
    Função que atualiza o gráfico de paradas do modal.
    """

    if data_info is None:
        raise PreventUpdate

    # Carregue a string JSON em um DataFrame
    df_maq_info_cadastro = pd.read_json(stringIO(data_info), orient="split")

    # Crie o DataFrame
    df = indicators.get_time_lost(df_maq_info_cadastro, IndicatorType.EFFICIENCY, turn)

    figure = indicators.get_bar_stack_stops(df, date)

    return figure
