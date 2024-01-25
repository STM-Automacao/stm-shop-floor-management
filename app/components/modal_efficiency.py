"""
Modal Module
"""
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
from helpers.types import IndicatorType
from service.times_data import TimesData

times_data = TimesData()
indicators = IndicatorsTurn()

# ========================================= Modal Layout ======================================== #
layout = [
    dbc.ModalHeader("Eficiência por Turno"),
    dbc.ModalBody(
        [
            dbc.Row(
                [
                    dbc.Col(
                        dcc.RadioItems(
                            id="radio-items",
                            options=[
                                {"label": "Noturno", "value": "NOT"},
                                {"label": "Matutino", "value": "MAT"},
                                {"label": "Vespertino", "value": "VES"},
                            ],
                            value="MAT",
                            inputClassName="form-check-input me-2 mb-1",
                            labelClassName="form-check-label me-5 mb-1",
                            inline=True,
                        ),
                        md=4,
                    ),
                    dbc.Col(
                        dmc.Switch(
                            id="annotations-switch-eficiencia",
                            label="Anotações",
                            size="sm",
                            radius="lg",
                            className="mb-1",
                            checked=False,
                        ),
                        md=2,
                    ),
                ],
                justify="between",
            ),
            dcc.Loading(dcc.Graph(id="graph-eficiencia-modal")),
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
                                        className="mb-1",
                                        checked=False,
                                    ),
                                    dcc.Graph(
                                        id="graph-eficiencia-modal-perdas"
                                    ),
                                ]
                            ),
                            dbc.Row(html.P("Aqui Input da ações")),
                        ],
                        md=6,
                    ),
                ]
            ),
        ]
    ),
    dbc.ModalFooter("Modal footer"),
]


# ======================================= Modal Callbacks ======================================== #
@callback(
    Output("graph-eficiencia-modal", "figure"),
    [
        Input("radio-items", "value"),
        Input("store-info", "data"),
        Input("store-prod", "data"),
        Input("annotations-switch-eficiencia", "checked"),
    ],
)
def update_graph_eficiencia_modal(value, data_info, data_prod, checked):
    """
    Função que atualiza o gráfico de eficiência do modal.
    """
    if data_info is None or data_prod is None:
        raise PreventUpdate

    df_maq_info_cadastro = pd.read_json(stringIO(data_info), orient="split")
    df_maq_info_prod_cad = pd.read_json(stringIO(data_prod), orient="split")

    df = times_data.get_eff_data(df_maq_info_cadastro, df_maq_info_prod_cad)
    df = df[df["turno"] == value]

    figure = indicators.get_eff_heat_turn(df, annotations=checked)

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

    df = indicators.get_time_lost(
        df_maq_info_cadastro, IndicatorType.EFFICIENCY, turn
    )

    figure = indicators.get_eff_bar_lost(df, turn, checked)

    return figure
