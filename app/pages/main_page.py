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
                    md=2,
                    id="last-eficiencia-col",
                ),
                dbc.Col(
                    [
                        html.H3("Eficiência"),
                        dcc.Graph(
                            figure={},
                            id="eficiencia-graph",
                        ),
                        html.P("Aqui vem o gráfico de eficiência(linhas)"),
                    ],
                    md=8,
                    id="eficiencia-col",
                ),
                dbc.Col(
                    [
                        html.P("Atual"),
                        html.P("Aqui vem a imagem"),
                    ],
                    md=2,
                    id="current-eficiencia-col",
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
                    md=2,
                    id="last-performance-col",
                ),
                dbc.Col(
                    [
                        html.H3("Performance"),
                        html.P("Aqui vem o gráfico de performance"),
                        html.P("Aqui vem o gráfico de performance(linhas)"),
                    ],
                    md=8,
                    id="performance-col",
                ),
                dbc.Col(
                    [
                        html.P("Atual"),
                        html.P("Aqui vem a imagem"),
                    ],
                    md=2,
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
                    md=2,
                    id="last-reparos-col",
                ),
                dbc.Col(
                    [
                        html.H3("Reparos"),
                        html.P("Aqui vem o gráfico de reparos"),
                        html.P("Aqui vem o gráfico de reparos(linhas)"),
                    ],
                    md=8,
                    id="reparos-col",
                ),
                dbc.Col(
                    [
                        html.P("Atual"),
                        html.P("Aqui vem a imagem"),
                    ],
                    md=2,
                    id="current-reparos-col",
                ),
            ],
            id="reparos-row",
        ),
    ]
)


# ========================================= Callbacks ========================================= #


@callback(
    Output("eficiencia-graph", "figure"),
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
