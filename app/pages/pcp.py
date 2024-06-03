import dash_bootstrap_components as dbc
from dash import html

# ================================================================================================ #
#                                              LAYOUT                                              #
# ================================================================================================ #
layout = [
    dbc.Row(
        [
            dbc.Col(dbc.Card(html.H2("Dados de Massadas"), body=True), width=6),
            dbc.Col(dbc.Card(html.H2("Dados de Massadas por semana"), body=True), width=6),
        ],
        class_name="mt-3 mb-3",
    ),
    dbc.Row(html.H2("Trabalhando aqui")),
]
