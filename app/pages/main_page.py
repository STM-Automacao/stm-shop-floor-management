"""
    Página principal do dashboard
    Criada por: Bruno Tomaz
    Data: 15/01/2024
"""
# cSpell: words eficiencia fullscreen
from io import StringIO

import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import callback, dcc, html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
# pylint: disable=E0401
from graphics.indicators import Indicators
from helpers.path_config import EFF_LAST, PERF_LAST, REPAIR_LAST
from helpers.types import IndicatorType
from service.times_data import TimesData

ind_graphics = Indicators()
times_data = TimesData()

# ========================================= Layout ========================================= #
layout = dcc.Loading(
    id="loading",
    type="circle",
    fullscreen=True,
    children=[
        html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dcc.Graph(
                                    figure={},
                                    id="eficiencia-gauge-graph_last",
                                ),
                            ],
                            xs={"size": 6, "order": 2, "offset": 0},
                            sm={"size": 4, "order": 2, "offset": 1},
                            md={"size": 4, "order": 2, "offset": 1},
                            xl={"size": 2, "order": 1, "offset": 0},
                            xxl={"size": 1, "order": 1, "offset": 0},
                            id="last-eficiencia-col",
                            class_name="p-1",
                        ),
                        dbc.Col(
                            [
                                dcc.Graph(
                                    figure={},
                                    id="eficiencia-heat-graph",
                                ),
                                dcc.Graph(
                                    figure={},
                                    id="eficiencia-line-graph",
                                    style={"height": "80px"},
                                ),
                            ],
                            xs={"size": 12, "order": 1},
                            sm={"size": 12, "order": 1},
                            md={"size": 12, "order": 1},
                            xl={"size": 8, "order": 2},
                            xxl={"size": 10, "order": 2},
                            id="eficiencia-col",
                            class_name="p-1",
                        ),
                        dbc.Col(
                            [
                                dcc.Graph(
                                    figure={},
                                    id="eficiencia-gauge-graph_actual",
                                ),
                            ],
                            xs={"size": 6, "order": 2, "offset": 0},
                            sm={"size": 4, "order": 2, "offset": 2},
                            md={"size": 4, "order": 2, "offset": 2},
                            xl={"size": 2, "order": 3, "offset": 0},
                            xxl={"size": 1, "order": 3, "offset": 0},
                            id="current-eficiencia-col",
                            class_name="p-1",
                        ),
                    ],
                    id="eficiencia-row",
                ),
                html.Hr(),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dcc.Graph(
                                    figure={},
                                    id="performance-gauge-graph_last",
                                ),
                            ],
                            sm={"size": 4, "order": 2, "offset": 1},
                            md={"size": 2, "order": 1, "offset": 0},
                            xl={"size": 1, "order": 1, "offset": 0},
                            id="last-performance-col",
                            class_name="p-1",
                        ),
                        dbc.Col(
                            [
                                dcc.Graph(
                                    figure={},
                                    id="performance-heat-graph",
                                ),
                                dcc.Graph(
                                    figure={},
                                    id="performance-line-graph",
                                    style={"height": "80px"},
                                ),
                            ],
                            sm={"size": 12, "order": 1},
                            md={"size": 8, "order": 2},
                            xl={"size": 10, "order": 2},
                            id="performance-col",
                            class_name="p-1",
                        ),
                        dbc.Col(
                            [
                                dcc.Graph(
                                    figure={},
                                    id="performance-gauge-graph_actual",
                                ),
                            ],
                            sm={"size": 4, "order": 3, "offset": 2},
                            md={"size": 2, "order": 3, "offset": 0},
                            xl={"size": 1, "order": 3, "offset": 0},
                            id="current-performance-col",
                            class_name="p-1",
                        ),
                    ],
                    id="performance-row",
                ),
                html.Hr(),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dcc.Graph(
                                    figure={},
                                    id="reparos-gauge-graph_last",
                                ),
                            ],
                            sm={"size": 4, "order": 2, "offset": 1},
                            md={"size": 2, "order": 1, "offset": 0},
                            xl={"size": 1, "order": 1, "offset": 0},
                            id="last-reparos-col",
                            class_name="p-1",
                        ),
                        dbc.Col(
                            [
                                dcc.Graph(
                                    figure={},
                                    id="reparos-heat-graph",
                                ),
                                dcc.Graph(
                                    figure={},
                                    id="reparos-line-graph",
                                    style={"height": "80px"},
                                ),
                            ],
                            sm={"size": 12, "order": 1},
                            md={"size": 8, "order": 2},
                            xl={"size": 10, "order": 2},
                            id="reparos-col",
                            class_name="p-1",
                        ),
                        dbc.Col(
                            [
                                dcc.Graph(
                                    figure={},
                                    id="reparos-gauge-graph_actual",
                                ),
                            ],
                            sm={"size": 4, "order": 3, "offset": 2},
                            md={"size": 2, "order": 3, "offset": 0},
                            xl={"size": 1, "order": 3, "offset": 0},
                            id="current-reparos-col",
                            class_name="p-1",
                        ),
                    ],
                    id="reparos-row",
                ),
            ],
            id="main-page",
        )
    ],
)


# ========================================= Callbacks ========================================= #


# --------- Gráficos de calor --------- #
@callback(
    Output("eficiencia-heat-graph", "figure"),
    [
        Input("store-info", "data"),
        Input("store-prod", "data"),
    ],
)
def update_eficiencia_graph(info, prod):
    """
    Função que atualiza o gráfico de eficiência.
    """
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate

    if info is None:
        raise PreventUpdate
    df_maq_info_cadastro = pd.read_json(StringIO(info), orient="split")
    df_maq_info_prod_cad = pd.read_json(StringIO(prod), orient="split")

    df = times_data.get_eff_data(df_maq_info_cadastro, df_maq_info_prod_cad)
    fig = ind_graphics.efficiency_graphic(df, 90)

    return fig


@callback(
    Output("performance-heat-graph", "figure"),
    [
        Input("store-info", "data"),
        Input("store-prod", "data"),
    ],
)
def update_performance_graph(info, prod):
    """
    Função que atualiza o gráfico de eficiência.
    """
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate

    if info is None:
        raise PreventUpdate
    df_maq_info_cadastro = pd.read_json(StringIO(info), orient="split")
    df_maq_info_prod_cad = pd.read_json(StringIO(prod), orient="split")

    df = times_data.get_perf_data(df_maq_info_cadastro, df_maq_info_prod_cad)
    fig = ind_graphics.performance_graphic(df, 4)

    return fig


@callback(
    Output("reparos-heat-graph", "figure"),
    [
        Input("store-info", "data"),
        Input("store-prod", "data"),
    ],
)
def update_reparos_graph(info, prod):
    """
    Função que atualiza o gráfico de eficiência.
    """
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate

    if info is None:
        raise PreventUpdate
    df_maq_info_cadastro = pd.read_json(StringIO(info), orient="split")
    df_maq_info_prod_cad = pd.read_json(StringIO(prod), orient="split")

    df = times_data.get_repair_data(df_maq_info_cadastro, df_maq_info_prod_cad)
    fig = ind_graphics.repair_graphic(df, 4)

    return fig


# --------- Gráficos de Gauge --------- #
@callback(
    Output("eficiencia-gauge-graph_actual", "figure"),
    [
        Input("store-info", "data"),
        Input("store-prod", "data"),
    ],
)
def update_eficiencia_gauge_graph_actual(info, prod):
    """
    Função que atualiza o gráfico de eficiência.
    """
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate

    if info is None:
        raise PreventUpdate
    df_maq_info_cadastro = pd.read_json(StringIO(info), orient="split")
    df_maq_info_prod_cad = pd.read_json(StringIO(prod), orient="split")

    df = times_data.get_eff_data(df_maq_info_cadastro, df_maq_info_prod_cad)
    fig = ind_graphics.draw_gauge_graphic(df, IndicatorType.EFFICIENCY, 90)

    return fig


@callback(
    Output("performance-gauge-graph_actual", "figure"),
    [
        Input("store-info", "data"),
        Input("store-prod", "data"),
    ],
)
def update_performance_gauge_graph_actual(info, prod):
    """
    Função que atualiza o gráfico de eficiência.
    """
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate

    if info is None:
        raise PreventUpdate
    df_maq_info_cadastro = pd.read_json(StringIO(info), orient="split")
    df_maq_info_prod_cad = pd.read_json(StringIO(prod), orient="split")

    df = times_data.get_perf_data(df_maq_info_cadastro, df_maq_info_prod_cad)
    fig = ind_graphics.draw_gauge_graphic(df, IndicatorType.PERFORMANCE, 4)

    return fig


@callback(
    Output("reparos-gauge-graph_actual", "figure"),
    [
        Input("store-info", "data"),
        Input("store-prod", "data"),
    ],
)
def update_reparos_gauge_graph_actual(info, prod):
    """
    Função que atualiza o gráfico de eficiência.
    """
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate

    if info is None:
        raise PreventUpdate
    df_maq_info_cadastro = pd.read_json(StringIO(info), orient="split")
    df_maq_info_prod_cad = pd.read_json(StringIO(prod), orient="split")

    df = times_data.get_repair_data(df_maq_info_cadastro, df_maq_info_prod_cad)
    fig = ind_graphics.draw_gauge_graphic(df, IndicatorType.REPAIR, 4)

    return fig


# --------- Gráficos de linha --------- #
@callback(
    Output("eficiencia-line-graph", "figure"),
    [
        Input("store-info", "data"),
        Input("store-prod", "data"),
    ],
)
def update_eficiencia_line_graph(info, prod):
    """
    Função que atualiza o gráfico de eficiência.
    """
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate

    if info is None:
        raise PreventUpdate
    df_maq_info_cadastro = pd.read_json(StringIO(info), orient="split")
    df_maq_info_prod_cad = pd.read_json(StringIO(prod), orient="split")

    df = times_data.get_eff_data(df_maq_info_cadastro, df_maq_info_prod_cad)
    fig = ind_graphics.plot_daily_efficiency(df, IndicatorType.EFFICIENCY)

    return fig


@callback(
    Output("performance-line-graph", "figure"),
    [
        Input("store-info", "data"),
        Input("store-prod", "data"),
    ],
)
def update_performance_line_graph(info, prod):
    """
    Função que atualiza o gráfico de eficiência.
    """
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate

    if info is None:
        raise PreventUpdate
    df_maq_info_cadastro = pd.read_json(StringIO(info), orient="split")
    df_maq_info_prod_cad = pd.read_json(StringIO(prod), orient="split")

    df = times_data.get_perf_data(df_maq_info_cadastro, df_maq_info_prod_cad)
    fig = ind_graphics.plot_daily_efficiency(df, IndicatorType.PERFORMANCE)

    return fig


@callback(
    Output("reparos-line-graph", "figure"),
    [
        Input("store-info", "data"),
        Input("store-prod", "data"),
    ],
)
def update_reparos_line_graph(info, prod):
    """
    Função que atualiza o gráfico de eficiência.
    """
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate

    if info is None:
        raise PreventUpdate
    df_maq_info_cadastro = pd.read_json(StringIO(info), orient="split")
    df_maq_info_prod_cad = pd.read_json(StringIO(prod), orient="split")

    df = times_data.get_repair_data(df_maq_info_cadastro, df_maq_info_prod_cad)
    fig = ind_graphics.plot_daily_efficiency(df, IndicatorType.REPAIR)

    return fig


# --------- Gráficos de Gauge do mês anterior --------- #
# callback que atualiza os 3 quando renderiza a página
@callback(
    [
        Output("eficiencia-gauge-graph_last", "figure"),
        Output("performance-gauge-graph_last", "figure"),
        Output("reparos-gauge-graph_last", "figure"),
    ],
    [
        Input("store-info", "data"),
        Input("store-prod", "data"),
    ],
)
def update_last_month_gauge_graphs(info, prod):
    """
    Função que atualiza os gráficos de gauge do mês anterior.
    """
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate

    if info is None or prod is None:
        raise PreventUpdate

    # Leitura dos dados de assets (salvos em csv)
    # pylint: disable=E1101
    df_eff = pd.read_csv((EFF_LAST))
    df_perf = pd.read_csv((PERF_LAST))
    df_repair = pd.read_csv((REPAIR_LAST))

    fig_eff = ind_graphics.draw_gauge_graphic(
        df_eff, IndicatorType.EFFICIENCY, 90
    )
    fig_perf = ind_graphics.draw_gauge_graphic(
        df_perf, IndicatorType.PERFORMANCE, 4
    )
    fig_repair = ind_graphics.draw_gauge_graphic(
        df_repair, IndicatorType.REPAIR, 4
    )

    return fig_eff, fig_perf, fig_repair
