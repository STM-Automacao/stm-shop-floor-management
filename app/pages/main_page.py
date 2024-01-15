"""
    Página principal do dashboard
    Criada por: Bruno Tomaz
    Data: 15/01/2024
"""
# cSpell: words eficiencia

import dash_bootstrap_components as dbc
from dash import html

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
                        html.P("Aqui vem o gráfico de eficiência"),
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
