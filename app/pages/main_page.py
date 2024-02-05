"""
    Página principal do dashboard
    Criada por: Bruno Tomaz
    Data: 15/01/2024
"""

import json

# cSpell: words eficiencia fullscreen
from io import StringIO

import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd

# pylint: disable=E0401
from components import modal_efficiency, modal_performance, modal_repair
from dash import callback, dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

# from dash_bootstrap_templates import ThemeChangerAIO
from graphics.indicators import Indicators
from helpers.path_config import EFF_LAST, PERF_LAST, REPAIR_LAST
from helpers.types import IndicatorType
from service.times_data import TimesData

from app import app

ind_graphics = Indicators()
times_data = TimesData()

# ========================================= Layout ========================================= #

layout = [
    html.Div(
        [
            dbc.Spinner(
                id="loading-eff-1",
                # fullscreen=True,
                color="primary",
                size="md",
                children=[
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
                                md={"size": 2, "order": 1, "offset": 0},
                                xl={"size": 2, "order": 1, "offset": 0},
                                xxl={"size": 1, "order": 1, "offset": 0},
                                id="last-eficiencia-col",
                                class_name="p-1",
                            ),
                            dbc.Col(
                                [
                                    dbc.Button(
                                        id="eff_heat_btn",
                                        class_name="w-100 p-0 bg-transparent border-0",
                                        children=[
                                            dcc.Graph(
                                                figure={},
                                                id="eficiencia-heat-graph",
                                            ),
                                        ],
                                    ),
                                    dcc.Graph(
                                        figure={},
                                        id="eficiencia-line-graph",
                                        style={"height": "80px"},
                                    ),
                                ],
                                xs={"size": 12, "order": 1},
                                sm={"size": 12, "order": 1},
                                md={"size": 8, "order": 2},
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
                                md={"size": 2, "order": 3, "offset": 0},
                                xl={"size": 2, "order": 3, "offset": 0},
                                xxl={"size": 1, "order": 3, "offset": 0},
                                id="current-eficiencia-col",
                                class_name="p-1",
                            ),
                        ],
                        id="eficiencia-row",
                    ),
                ],
            ),
            html.Hr(),
            dbc.Spinner(
                id="loading-perf-1",
                # fullscreen=True,
                color="secondary",
                size="md",
                children=[
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dcc.Graph(
                                        figure={},
                                        id="performance-gauge-graph_last",
                                    ),
                                    html.H1(
                                        "D", className="text-center", style={"font-size": "4rem"}
                                    ),
                                ],
                                xs={"size": 6, "order": 2, "offset": 0},
                                sm={"size": 4, "order": 2, "offset": 1},
                                md={"size": 2, "order": 1, "offset": 0},
                                xl={"size": 2, "order": 1, "offset": 0},
                                xxl={"size": 1, "order": 1, "offset": 0},
                                id="last-performance-col",
                                class_name="p-1",
                            ),
                            dbc.Col(
                                [
                                    dbc.Button(
                                        id="perf_heat_btn",
                                        class_name="w-100 p-0 bg-transparent border-0",
                                        children=[
                                            dcc.Graph(
                                                figure={},
                                                id="performance-heat-graph",
                                            ),
                                        ],
                                    ),
                                    dcc.Graph(
                                        figure={},
                                        id="performance-line-graph",
                                        style={"height": "80px"},
                                    ),
                                ],
                                xs={"size": 12, "order": 1},
                                sm={"size": 12, "order": 1},
                                md={"size": 8, "order": 2},
                                xl={"size": 8, "order": 2},
                                xxl={"size": 10, "order": 2},
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
                                xs={"size": 6, "order": 2, "offset": 0},
                                sm={"size": 4, "order": 2, "offset": 2},
                                md={"size": 2, "order": 3, "offset": 0},
                                xl={"size": 2, "order": 3, "offset": 0},
                                xxl={"size": 1, "order": 3, "offset": 0},
                                id="current-performance-col",
                                class_name="p-1",
                            ),
                        ],
                        id="performance-row",
                    ),
                ],
            ),
            html.Hr(),
            dbc.Spinner(
                id="loading-rep-1",
                # fullscreen=True,
                color="info",
                size="md",
                children=[
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dcc.Graph(
                                        figure={},
                                        id="reparos-gauge-graph_last",
                                    ),
                                ],
                                xs={"size": 6, "order": 2, "offset": 0},
                                sm={"size": 4, "order": 2, "offset": 1},
                                md={"size": 2, "order": 1, "offset": 0},
                                xl={"size": 2, "order": 1, "offset": 0},
                                xxl={"size": 1, "order": 1, "offset": 0},
                                id="last-reparos-col",
                                class_name="p-1",
                            ),
                            dbc.Col(
                                [
                                    dbc.Button(
                                        id="reparos_heat_btn",
                                        class_name="w-100 p-0 bg-transparent border-0",
                                        children=[
                                            dcc.Graph(
                                                figure={},
                                                id="reparos-heat-graph",
                                            ),
                                        ],
                                    ),
                                    dcc.Graph(
                                        figure={},
                                        id="reparos-line-graph",
                                        style={"height": "80px"},
                                    ),
                                ],
                                xs={"size": 12, "order": 1},
                                sm={"size": 12, "order": 1},
                                md={"size": 8, "order": 2},
                                xl={"size": 8, "order": 2},
                                xxl={"size": 10, "order": 2},
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
                                xs={"size": 6, "order": 2, "offset": 0},
                                sm={"size": 4, "order": 2, "offset": 2},
                                md={"size": 2, "order": 3, "offset": 0},
                                xl={"size": 2, "order": 3, "offset": 0},
                                xxl={"size": 1, "order": 3, "offset": 0},
                                id="current-reparos-col",
                                class_name="p-1",
                            ),
                        ],
                        id="reparos-row",
                    ),
                ],
            ),
            html.Hr(),
            dmc.Center(
                children=dmc.Image(
                    # pylint: disable=E1101
                    src=app.get_asset_url("Logo Horizontal.png"),
                    width="125px",
                    withPlaceholder=True,
                ),
                p=2,
            ),
        ],
        id="main-page",
    ),
    # ------------------ Modal ------------------ #
    dbc.Modal(
        children=modal_efficiency.layout,
        id="modal_eff",
        size="xl",
        scrollable=True,
        fullscreen=True,
        modal_class_name="inter",
    ),
    dbc.Modal(
        children=modal_performance.layout,
        id="modal_perf",
        size="xl",
        scrollable=True,
        fullscreen=True,
        modal_class_name="inter",
    ),
    dbc.Modal(
        children=modal_repair.layout,
        id="modal_repair",
        size="xl",
        scrollable=True,
        fullscreen=True,
        modal_class_name="inter",
    ),
]

# ========================================= Callbacks ========================================= #


# --------- Gráficos de calor --------- #
@callback(
    Output("eficiencia-heat-graph", "figure"),
    [
        Input("store-df-eff-heatmap", "data"),
        Input("store-annotations_list_tuple", "data"),
        # Input(ThemeChangerAIO.ids.radio("theme"), "value"),
    ],
)
def update_eficiencia_graph(df, ann_tuple):  # theme se quiser mudar o tema
    """
    Função que atualiza o gráfico de eficiência.
    """
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate

    if df is None:
        raise PreventUpdate

    ann_tuple_json = json.loads(ann_tuple)

    df_eff = pd.read_json(StringIO(df), orient="split")
    annotations_list_tuple = [json.loads(lst_json) for lst_json in ann_tuple_json]

    ann_eff = annotations_list_tuple[0]

    fig = ind_graphics.efficiency_graphic(df_eff, ann_eff, 90)  # theme se quiser mudar o tema

    return fig


@callback(
    Output("performance-heat-graph", "figure"),
    [
        Input("store-df-perf_repair_heat_tuple", "data"),
        Input("store-annotations_list_tuple", "data"),
    ],
)
def update_performance_graph(df_perf, ann_tuple):
    """
    Função que atualiza o gráfico de eficiência.
    """
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate

    if df_perf is None:
        raise PreventUpdate

    df_perf_json = json.loads(df_perf)
    ann_tuple_json = json.loads(ann_tuple)

    df_tuple = [pd.read_json(StringIO(lst_json), orient="split") for lst_json in df_perf_json]
    annotations_list_tuple = [json.loads(lst_json) for lst_json in ann_tuple_json]

    ann_perf = annotations_list_tuple[1]
    df = df_tuple[0]

    fig = ind_graphics.performance_graphic(df, ann_perf, 4)

    return fig


@callback(
    Output("reparos-heat-graph", "figure"),
    [
        Input("store-df-perf_repair_heat_tuple", "data"),
        Input("store-annotations_list_tuple", "data"),
    ],
)
def update_reparos_graph(df_repair, ann_tuple):
    """
    Função que atualiza o gráfico de eficiência.
    """
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate

    if df_repair is None:
        raise PreventUpdate

    df_repair_json = json.loads(df_repair)
    ann_tuple_json = json.loads(ann_tuple)

    annotations_list_tuple = [json.loads(lst_json) for lst_json in ann_tuple_json]
    df_tuple = [pd.read_json(StringIO(lst_json), orient="split") for lst_json in df_repair_json]

    ann_repair = annotations_list_tuple[2]
    df = df_tuple[1]

    fig = ind_graphics.repair_graphic(df, ann_repair, 4)

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
        # Input("store-info", "data"),
        # Input("store-prod", "data"),
        Input("store-df-eff", "data"),
    ],
)
def update_eficiencia_line_graph(df):
    """
    Função que atualiza o gráfico de eficiência.
    """
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate

    if df is None:
        raise PreventUpdate
    # df_maq_info_cadastro = pd.read_json(StringIO(info), orient="split")
    # df_maq_info_prod_cad = pd.read_json(StringIO(prod), orient="split")
    df_eff_line = pd.read_json(StringIO(df), orient="split")

    # df = times_data.get_eff_data(df_maq_info_cadastro, df_maq_info_prod_cad)
    fig = ind_graphics.plot_daily_efficiency(df_eff_line, IndicatorType.EFFICIENCY, 90)

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
    fig = ind_graphics.plot_daily_efficiency(df, IndicatorType.PERFORMANCE, 4)

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
    fig = ind_graphics.plot_daily_efficiency(df, IndicatorType.REPAIR, 4)

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

    fig_eff = ind_graphics.draw_gauge_graphic(df_eff, IndicatorType.EFFICIENCY, 90)
    fig_perf = ind_graphics.draw_gauge_graphic(df_perf, IndicatorType.PERFORMANCE, 4)
    fig_repair = ind_graphics.draw_gauge_graphic(df_repair, IndicatorType.REPAIR, 4)

    return fig_eff, fig_perf, fig_repair


# ----------------------------- Modal ----------------------------- #
@callback(
    Output("modal_eff", "is_open"),
    [Input("eff_heat_btn", "n_clicks")],
    [State("modal_eff", "is_open")],
)
def toggle_modal(n1, is_open):
    """
    Função que abre o modal com o gráfico de eficiência.
    """
    if n1:
        return not is_open
    return is_open


@callback(
    Output("modal_perf", "is_open"),
    [Input("perf_heat_btn", "n_clicks")],
    [State("modal_perf", "is_open")],
)
def toggle_modal_performance(n1, is_open):
    """
    Função que abre o modal com o gráfico de performance.
    """
    if n1:
        return not is_open
    return is_open


@callback(
    Output("modal_repair", "is_open"),
    [Input("reparos_heat_btn", "n_clicks")],
    [State("modal_repair", "is_open")],
)
def toggle_modal_repair(n1, is_open):
    """
    Função que abre o modal com o gráfico de reparos.
    """
    if n1:
        return not is_open
    return is_open
