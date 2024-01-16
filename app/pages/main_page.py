"""
    Página principal do dashboard
    Criada por: Bruno Tomaz
    Data: 15/01/2024
"""
from io import StringIO

# cSpell: words eficiencia
import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import callback, dcc, html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

# pylint: disable=E0401
from graphics.indicators import Indicators
from service.times_data import TimesData

ind_graphics = Indicators()
times_data = TimesData()

# ========================================= Layout ========================================= #
layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.P("Anterior"),
                        html.P("Aqui vem a imagem"),
                    ],
                    md=1,
                    id="last-eficiencia-col",
                    style={"background-color": "red"},
                ),
                dbc.Col(
                    [
                        dcc.Graph(
                            figure={},
                            id="eficiencia-heat-graph",
                        ),
                        html.P("Aqui vem o gráfico de eficiência(linhas)"),
                    ],
                    md=10,
                    id="eficiencia-col",
                    style={"background-color": "green"},
                    class_name="p-0",
                ),
                dbc.Col(
                    [
                        html.P("Atual"),
                        html.P("Aqui vem a imagem"),
                    ],
                    md=1,
                    id="current-eficiencia-col",
                    style={"background-color": "blue"},
                ),
            ],
            id="eficiencia-row",
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.P("Anterior"),
                        html.P("Aqui vem a imagem"),
                    ],
                    md=1,
                    id="last-performance-col",
                ),
                dbc.Col(
                    [
                        dcc.Graph(
                            figure={},
                            id="performance-heat-graph",
                        ),
                        html.P("Aqui vem o gráfico de performance(linhas)"),
                    ],
                    md=10,
                    id="performance-col",
                ),
                dbc.Col(
                    [
                        html.P("Atual"),
                        html.P("Aqui vem a imagem"),
                    ],
                    md=1,
                    id="current-performance-col",
                ),
            ],
            id="performance-row",
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.P("Anterior"),
                        html.P("Aqui vem a imagem"),
                    ],
                    md=1,
                    id="last-reparos-col",
                ),
                dbc.Col(
                    [
                        dcc.Graph(
                            figure={},
                            id="reparos-heat-graph",
                        ),
                        html.P("Aqui vem o gráfico de reparos(linhas)"),
                    ],
                    md=10,
                    id="reparos-col",
                ),
                dbc.Col(
                    [
                        html.P("Atual"),
                        html.P("Aqui vem a imagem"),
                    ],
                    md=1,
                    id="current-reparos-col",
                ),
            ],
            id="reparos-row",
        ),
    ]
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
