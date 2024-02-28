"""
Modal Module
Criado por: Bruno Tomaz
Data: 23/01/2024
"""

import json
from io import StringIO as stringIO

# cSpell: words eficiencia fullscreen sunday producao idxmax
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import numpy as np
import pandas as pd

# pylint: disable=E0401
from components import btn_modal, modal_history
from dash import callback, dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from graphics.indicators import Indicators
from graphics.indicators_turn import IndicatorsTurn
from helpers.types import IndicatorType
from service.times_data import TimesData

from app import app

times_data = TimesData()
indicators = IndicatorsTurn()
indicators_geral = Indicators()
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
                        btn_modal.radio_btn_eff,
                        class_name="radio-group",
                        md=3,
                    ),
                    dbc.Col(
                        btn_modal.btn_opt_eff,
                    ),
                ],
            ),
            dbc.Spinner(
                children=dcc.Graph(id="graph-eficiencia-modal"),
                size="lg",
                color="danger",
            ),
            dcc.Graph(
                id="graph-line-modal-1",
                style={"height": "80px"},
            ),
            html.Hr(),
            dbc.Collapse(
                [
                    dbc.Card(
                        [
                            dbc.CardHeader("Produção"),
                            dbc.CardBody(id="card-body-eff-production-totais-modal"),
                        ],
                        class_name="mb-3",
                    ),
                    dbc.Card(dbc.CardBody(id="card-body-eff-production-modal")),
                ],
                id="production-collapse",
                class_name="mb-3",
            ),
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(id="graph-eficiencia-modal-2"), md=6),
                    dbc.Col(
                        [
                            dbc.Row(
                                [
                                    dbc.Switch(
                                        id="perdas-switch-eficiencia",
                                        label="Agrupado",
                                        className="mb-1 inter",
                                        value=True,
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
            html.Hr(),
            dbc.Row(
                [
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
    # ---------------- Modal History ---------------- #
    dbc.Modal(
        children=modal_history.layout,
        id="modal_history",
        size="xl",
        scrollable=True,
        # fullscreen=True,
        modal_class_name="inter",
        is_open=False,
    ),
]


# ======================================= Modal Callbacks ======================================== #


@callback(
    Output("modal_history", "is_open"),
    [Input(f"history-button-{IndicatorType.EFFICIENCY.value}", "n_clicks")],
    [State("modal_history", "is_open")],
)
def toggle_modal_history(n, is_open):
    """
    Função que abre e fecha o modal do histórico.
    """
    if n:
        return not is_open
    return is_open


# ---------------------- Heatmap ---------------------- #
@callback(
    Output("graph-eficiencia-modal", "figure"),
    [
        Input(f"radio-items-{IndicatorType.EFFICIENCY.value}", "value"),
        Input("store-df_eff_heatmap_tuple", "data"),
        Input("store-annotations_eff_list_tuple", "data"),
    ],
)
def update_graph_eficiencia_modal(value, df_tuple, ann_tuple):
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
    noturno, matutino, vespertino, total, _ = tuple(df_list)
    ann_not, ann_mat, ann_ves, ann_total, _ = tuple(annotations_list_tuple)

    # Criar um dicionário com os DataFrames
    df_dict = {"NOT": noturno, "MAT": matutino, "VES": vespertino, "TOT": total}
    list_dict = {"NOT": ann_not, "MAT": ann_mat, "VES": ann_ves, "TOT": ann_total}

    # Selecionar o DataFrame correto
    df = df_dict[value]
    annotations = list_dict[value]

    figure = indicators.get_eff_heat_turn(df, annotations)

    return figure


# ---------------------- Line Chart ---------------------- #
@callback(
    Output("graph-line-modal-1", "figure"),
    [
        Input("store-df-eff", "data"),
        Input(f"radio-items-{IndicatorType.EFFICIENCY.value}", "value"),
    ],
)
def update_graph_line_modal_1(data, turn):
    """
    Função que atualiza o gráfico de linha do modal.
    """
    if data is None:
        raise PreventUpdate

    df = pd.read_json(stringIO(data), orient="split")

    figure = indicators_geral.plot_daily_efficiency(df, IndicatorType.EFFICIENCY, 90, turn)

    return figure


# ---------------------- Bar Totais ---------------------- #
@callback(
    Output("graph-eficiencia-modal-2", "figure"),
    Input("store-df-eff", "data"),
)
def update_graph_eficiencia_modal_2(df_eff):
    """
    Função que atualiza o gráfico de barras de eficiência do modal.
    """
    if df_eff is None:
        raise PreventUpdate

    df_eff_cad = pd.read_json(stringIO(df_eff), orient="split")

    figure = indicators.get_eff_bar_turn(df_eff_cad)

    return figure


# ---------------------- Perdas ---------------------- #
@callback(
    Output("graph-eficiencia-modal-perdas", "figure"),
    [
        Input("store-info", "data"),
        Input("perdas-switch-eficiencia", "value"),
        Input(f"radio-items-{IndicatorType.EFFICIENCY.value}", "value"),
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


# ---------------------- Grid ---------------------- #
@callback(
    Output("grid-eficiencia-modal", "children"),
    [
        Input("store-info", "data"),
        Input(f"radio-items-{IndicatorType.EFFICIENCY.value}", "value"),
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


# ---------------------- Collapse Btn ---------------------- #
@callback(
    [
        Output("detalhes-bar-collapse", "is_open"),
        Output(f"detalhes-button-{IndicatorType.EFFICIENCY.value}", "active"),
    ],
    [Input(f"detalhes-button-{IndicatorType.EFFICIENCY.value}", "n_clicks")],
    [Input("detalhes-bar-collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    """
    Função que abre e fecha o collapse do detalhes.
    """
    if n:
        return not is_open, not is_open
    return is_open, is_open


# ---------------------- Bar Stacked ---------------------- #
@callback(
    Output("every-stop-graph", "figure"),
    [
        Input("date-picker-eficiencia", "value"),
        Input("store-info", "data"),
        Input(f"radio-items-{IndicatorType.EFFICIENCY.value}", "value"),
        Input("store-df_working_time", "data"),
    ],
)
def update_every_stop_graph(date, data_info, turn, data_working_time):
    """
    Função que atualiza o gráfico de paradas do modal.
    """

    if data_info is None:
        raise PreventUpdate

    # Carregue a string JSON em um DataFrame
    df_maq_info_cadastro = pd.read_json(stringIO(data_info), orient="split")
    df_working_time = pd.read_json(stringIO(data_working_time), orient="split")

    # Crie o DataFrame
    df = indicators.get_time_lost(
        df_maq_info_cadastro, IndicatorType.EFFICIENCY, turn, df_working_time
    )

    figure = indicators.get_bar_stack_stops(df, date)

    return figure


# ---------------------- Collapse Production ---------------------- #
@callback(
    [
        Output("production-collapse", "is_open"),
        Output(f"production-btn-{IndicatorType.EFFICIENCY.value}", "active"),
    ],
    [
        Input(f"production-btn-{IndicatorType.EFFICIENCY.value}", "n_clicks"),
        Input("production-collapse", "is_open"),
    ],
)
def toggle_collapse_production(n, is_open):
    """
    Função que abre e fecha o collapse de produção.
    """
    if n:
        return not is_open, not is_open
    return is_open, is_open


# ---------------------- Table Production ---------------------- #
@callback(
    Output("card-body-eff-production-modal", "children"),
    [
        Input("store-prod", "data"),
        Input(f"radio-items-{IndicatorType.EFFICIENCY.value}", "value"),
    ],
)
def update_card_body_production(data_prod, turn):
    """
    Função que atualiza o card body da produção.
    """
    if data_prod is None:
        raise PreventUpdate

    df_maq_info_prod_cad = pd.read_json(stringIO(data_prod), orient="split")

    # Selecionar apenas o turno escolhido
    df_maq_info_prod = (
        df_maq_info_prod_cad[df_maq_info_prod_cad["turno"] == turn]
        if turn != "TOT"
        else df_maq_info_prod_cad
    )

    df_maq_info_prod.loc[:, "total_produzido"] = np.floor(
        df_maq_info_prod["total_produzido"] / 10
    ).astype(int)

    df = indicators.get_production_pivot(df_maq_info_prod)

    df_reset = df.reset_index()
    df_reset.columns = [str(column) for column in df_reset.columns]

    df_columns = df_reset.columns

    column_defs = [
        {
            "field": df_columns[0],
            "headerName": df_columns[0].capitalize(),
            "sortable": True,
            "flex": 1,
        },
        *[
            {
                "field": column,
                "headerName": f"Linha {column}",
                "sortable": True,
                "flex": 1,
            }
            for column in df_columns[1:15]
        ],
        {
            "field": df_columns[15],
            "headerName": df_columns[15].capitalize(),
            "sortable": True,
            "resizable": True,
            "flex": 1,
        },
    ]

    table = dag.AgGrid(
        id="AgGrid-eff-production-modal",
        columnDefs=column_defs,
        rowData=df_reset.to_dict("records"),
        columnSize="responsiveSizeToFit",
        dashGridOptions={"pagination": False, "domLayout": "autoHeight"},
        style={"height": None},
    )

    return table


# ---------------------- Cards ---------------------- #
@callback(
    Output("card-body-eff-production-totais-modal", "children"),
    Input("store-prod", "data"),
    Input("store-info", "data"),
)
def update_card_body_production_totais(data_prod, data_info):
    """
    Função que atualiza o card body da produção.
    """
    if data_prod is None:
        raise PreventUpdate

    df_maq_info_prod_cad = pd.read_json(stringIO(data_prod), orient="split")
    df_maq_info_cadastro = pd.read_json(stringIO(data_info), orient="split")

    df = pd.DataFrame(df_maq_info_prod_cad)
    df_info = pd.DataFrame(df_maq_info_cadastro)

    # Soma da Produção
    df["total_produzido"] = np.floor(df["total_produzido"] / 10)  # transforma em caixas
    df["total_produzido"] = df["total_produzido"].astype(int)
    producao_total = f"{df['total_produzido'].sum():,}".replace(",", ".")  # total produzido

    # Produção por turno
    # MAT
    df_mat = df[df["turno"] == "MAT"]
    producao_mat = f"{df_mat['total_produzido'].sum():,}".replace(",", ".")
    # VES
    df_ves = df[df["turno"] == "VES"]
    producao_ves = f"{df_ves['total_produzido'].sum():,}".replace(",", ".")
    # NOT
    df_not = df[df["turno"] == "NOT"]
    producao_not = f"{df_not['total_produzido'].sum():,}".replace(",", ".")

    # Soma do total minutos de parada programada
    df_info = df_info[df_info["motivo_id"] == 12]
    total_minutos_programada = f"{df_info['tempo_registro_min'].sum():,}".replace(",", ".")
    caixas_nao_produzidas = np.floor(df_info["tempo_registro_min"].sum() * (10.6 * 2) / 10)

    return [
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader("Produção Total"),
                            dbc.CardBody(
                                f"{producao_total} caixas", class_name="card-body-modal-style fs-3"
                            ),
                        ],
                        class_name="h-100 inter",
                    ),
                    md=2,
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader("Noturno Total"),
                            dbc.CardBody(
                                f"{producao_not} caixas", class_name="card-body-modal-style fs-3"
                            ),
                        ],
                        class_name="h-100 inter",
                    ),
                    md=2,
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader("Matutino Total"),
                            dbc.CardBody(
                                f"{producao_mat} caixas", class_name="card-body-modal-style fs-3"
                            ),
                        ],
                        class_name="h-100 inter",
                    ),
                    md=2,
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader("Vespertino Total"),
                            dbc.CardBody(
                                f"{producao_ves} caixas", class_name="card-body-modal-style fs-3"
                            ),
                        ],
                        class_name="h-100 inter",
                    ),
                    md=2,
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader("Total de Parada Programada"),
                            dbc.CardBody(
                                [
                                    html.P(
                                        f"Parada Programada --> "
                                        f"{total_minutos_programada} minutos",
                                        className="fs-5 align-self-center",
                                    ),
                                    html.P(
                                        f"Potencial não produzido --> "
                                        f"{caixas_nao_produzidas:,.0f}".replace(",", ".") + " cxs",
                                        className="fs-5 align-self-center",
                                    ),
                                ],
                                class_name="d-flex flex-column justify-content-center",
                            ),
                        ],
                        class_name="h-100 inter",
                    ),
                    md=4,
                ),
            ]
        ),
    ]
