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
from graphics.indicators_turn import IndicatorsTurn
from helpers.types import IndicatorType
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





