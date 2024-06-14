"""This module contains the layout for the modal that allows the user to insert stops."""

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

# cSpell:words termoformadoras

# =========================================== Variáveis ========================================== #
termoformadoras = [
    "TMF001",
    "TMF002",
    "TMF003",
    "TMF004",
    "TMF005",
    "TMF006",
    "TMF007",
    "TMF008",
    "TMF009",
    "TMF010",
    "TMF011",
    "TMF012",
    "TMF013",
    "TMF014",
    "TMF015",
]

options = {
    "Ajustes": {
        "Termoformadora": {
            "": ["", ""],
            "": ["", ""],
            "": ["", ""],
        },
        "Recheadora": {
            "": ["", ""],
            "": ["", ""],
        },
    }
}

# ================================================================================================ #
#                                              LAYOUT                                              #
# ================================================================================================ #
layout = dmc.Stack(
    [
        dbc.Row(
            [
                dbc.Col(
                    dmc.NumberInput(
                        label="Linha",
                        placeholder="Digite a linha",
                        min=1,
                        max=15,
                        step=1,
                    ),
                    md=3,
                ),
                dbc.Col(
                    dmc.Select(
                        label="Maquina ID",
                        placeholder="Nº da Termoformadora",
                        data=[*termoformadoras],
                    ),
                    md=4,
                ),
                dbc.Col(
                    dmc.Select(
                        label="Tipo de Parada",
                        data=["Manutenção", "Parada Programada", "Ajustes"],
                        placeholder="Selecione o tipo de parada",
                    ),
                    md=5,
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(),
                dbc.Col(),
                dbc.Col(),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(),
                dbc.Col(),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(),
                dbc.Col(),
            ]
        ),
        dbc.Row(),
    ],
)
