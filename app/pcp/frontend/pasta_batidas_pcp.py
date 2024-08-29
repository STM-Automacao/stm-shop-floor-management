"""Módulo com dados de Batidas de Pasta."""

from io import StringIO

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
from components import segmented_btn
from components.grid_aggrid import GridAgGrid
from dash import Input, Output, callback, html
from dash_bootstrap_templates import ThemeSwitchAIO

# =========================================== Variáveis ========================================== #
create_grid = GridAgGrid()
seg_btn = segmented_btn.SegmentedBtn()

# ================================================================================================ #
#                                              LAYOUT                                              #
# ================================================================================================ #

layout = dmc.Stack(
    [
        html.H1("Batidas de Pasta", className="text-center mt-3 mb-3"),
        dbc.Row(
            dbc.Col(
                seg_btn.create_segmented_btn("btn-pcp-batidas", ["Turno", "Total"], "Total"),
                md=3,
                class_name="d-flex justify-content-center align-items-center",
            ),
            justify="end",
            align="center",
            class_name="mb-3",
        ),
        dbc.Row(
            dmc.Card(id="batidas-pasta", shadow="sm"),
            class_name="mb-3",
        ),
        dbc.Row(
            dmc.Card(id="batidas-pasta-week", shadow="sm"),
            class_name="mb-3",
        ),
    ]
)

# ================================================================================================ #
#                                             CALLBACKS                                            #
# ================================================================================================ #


@callback(
    Output("batidas-pasta", "children"),
    [
        Input("df_pasta", "data"),
        Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
        Input("btn-pcp-batidas", "value"),
    ],
)
def update_batidas_pasta(data, theme, choice):
    """
    Atualiza o conteúdo do card de batidas de pasta.
    """
    if data is None:
        return "Sem dados disponíveis"

    # pylint: disable=no-member
    df = pd.read_json(StringIO(data), orient="split")

    # Renomear colunas
    df.columns = [
        "Data",
        "Turno",
        "Fabrica",
        "Cebola Batidas",
        "Doce Batidas",
        "Picante Batidas",
        "Tradicional Batidas",
        "Cebola Peso",
        "Doce Peso",
        "Picante Peso",
        "Tradicional Peso",
    ]

    # Filtrar por escolha
    filter_choice = {
        "Turno": df,
        "Total": df.groupby(["Data", "Fabrica"]).sum().drop(columns="Turno").reset_index(),
    }
    df = filter_choice[choice]

    # Ajustar o formato da data
    df["Data"] = pd.to_datetime(df["Data"]).dt.strftime("%d/%m")

    # Criar a tabela
    table = create_grid.create_grid_ag(df, "grid-pasta", theme)

    # Título
    title = html.H4(f"Batidas de Pasta - {choice}", className="text-center")

    return [title, table]


@callback(
    Output("batidas-pasta-week", "children"),
    [
        Input("df_pasta_week", "data"),
        Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
        Input("btn-pcp-batidas", "value"),
    ],
)
def update_pasta_week(data, theme, choice):
    """
    Atualiza o conteúdo do card de batidas de pasta semanal.
    """
    if data is None:
        return "Sem dados disponíveis"

    # pylint: disable=no-member
    df = pd.read_json(StringIO(data), orient="split")

    # Renomear colunas substituindo _ por espaço
    df.columns = [column.replace("_", " ") for column in df.columns]

    # Renomear colunas year e week para Ano e Semana e Fabrica para Fábrica
    df.rename(
        columns={
            "year": "Ano",
            "week": "Semana",
            "Fabrica": "Fábrica",
            "Data Semana": "Data Inicial",
        },
        inplace=True,
    )

    # Filtrar por escolha
    filter_choice = {
        "Turno": df,
        "Total": df.groupby(["Ano", "Semana", "Data Inicial", "Fábrica"])
        .sum()
        .drop(columns="Turno")
        .reset_index(),
    }

    df = filter_choice[choice]

    # Ordenar por Ano e Semana e Fábrica
    df = df.sort_values(["Ano", "Semana", "Fábrica"], ascending=[False, False, True])

    # Ajustar o formato da data
    df["Data Inicial"] = pd.to_datetime(df["Data Inicial"]).dt.strftime("%d/%m")

    # Criar a tabela
    table = create_grid.create_grid_ag(df, "grid-pasta-week", theme)

    # Título
    title = html.H4(f"Batidas de Pasta - {choice} (Semana)", className="text-center")

    return [title, table]
