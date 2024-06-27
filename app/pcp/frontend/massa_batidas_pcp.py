"""
Módulo com dados de Batidas de massa.
"""

from io import StringIO

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
from components import segmented_btn
from components.grid_aggrid import GridAgGrid
from dash import Input, Output, callback, html
from dash_bootstrap_templates import ThemeSwitchAIO

# =========================================== Variáveis ========================================== #
pcp_builder = GridAgGrid()
seg_btn = segmented_btn.SegmentedBtn()

# ================================================================================================ #
#                                              LAYOUT                                              #
# ================================================================================================ #
layout = dbc.Stack(
    [
        # ========================================= Body ========================================= #
        html.H1("Batidas de Massa", className="text-center mt-3 mb-3"),
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
            dmc.Card(id="massadas", shadow="sm"),
            class_name="mb-3",
        ),
        dbc.Row(
            dmc.Card(id="massadas-week", shadow="sm"),
            class_name="mb-3",
        ),
    ]
)

# ================================================================================================ #
#                                            CALLBACK'S                                            #
# ================================================================================================ #


# ===================================== Atualização Dos Cards ==================================== #
@callback(
    Output("massadas", "children"),
    [
        Input("df_sum", "data"),
        Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
        Input("btn-pcp-batidas", "value"),
    ],
)
def update_massadas_card(data, theme, choice):
    """
    Atualiza o conteúdo do card de massadas.

    Args:
        data (str): Os dados no formato JSON para atualizar o card.

    Returns:
        dbc.Table: A tabela gerada a partir dos dados fornecidos.
        Retorna a mensagem "Sem dados disponíveis." se data for None.
    """

    if data is None:
        return "Sem dados disponíveis."

    # Carregar os dados
    # pylint: disable=no-member
    df = pd.read_json(StringIO(data), orient="split")

    # Renomear as colunas
    df.columns = [
        "Data",
        "Turno",
        "Fábrica",
        "Batidas Cheias(qtd)",
        "Batidas Cheias(Peso)",
        "Batidas Reprocesso(qtd)",
        "Batidas Reprocesso(Peso)",
        "Batidas Bolinha(qtd)",
        "Batidas Bolinha(peso)",
        "Baguete Total(un)",
        "Bolinha Total(un)",
    ]

    # ----------------------- Filtro ----------------------- #
    df_filter = {
        "Turno": df,
        "Total": df.groupby(["Data", "Fábrica"]).sum().drop(columns="Turno").reset_index(),
    }
    df = df_filter[choice]

    # Ajustar o formato da data
    df["Data"] = pd.to_datetime(df["Data"]).dt.strftime("%d/%m")

    table = pcp_builder.create_grid_ag(df, "grid-pcp-1", theme)

    title = html.H4(f"Batidas de Massa - {choice}", className="text-center")

    return [title, table]


@callback(
    Output("massadas-week", "children"),
    [
        Input("df_week", "data"),
        Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
        Input("btn-pcp-batidas", "value"),
    ],
)
def update_massadas_week_card(data, theme, choice):
    """
    Atualiza o cartão de semana de massadas com os dados fornecidos.

    Parâmetros:
    - data: str ou None. Os dados a serem exibidos no cartão.
        Se for None, exibe a mensagem "Sem dados disponíveis."

    Retorna:
    - table: dbc.Table. A tabela gerada a partir dos dados fornecidos.
    """

    if data is None:
        return "Sem dados disponíveis."

    df = pd.read_json(StringIO(data), orient="split")

    df.columns = [
        "Ano",
        "Semana",
        "Data Inicial",
        "Turno",
        "Fábrica",
        "Batidas Cheias(qtd)",
        "Batidas Cheias(Peso)",
        "Batidas Reprocesso(qtd)",
        "Batidas Reprocesso(Peso)",
        "Batidas Bolinha(qtd)",
        "Batidas Bolinha(peso)",
        "Baguete Total(un)",
        "Bolinha Total(un)",
    ]

    # ----------------------- Filtro ----------------------- #
    # pylint: disable=no-member
    df_filter = {
        "Turno": df,
        "Total": df.groupby(["Ano", "Semana", "Data Inicial", "Fábrica"])
        .sum()
        .drop(columns="Turno")
        .reset_index(),
    }
    df = df_filter[choice]

    # Ordenar por ano, semana e fábrica
    df = df.sort_values(["Ano", "Semana", "Fábrica"], ascending=[False, False, True])

    df["Data Inicial"] = pd.to_datetime(df["Data Inicial"]).dt.strftime("%d/%m")

    table = pcp_builder.create_grid_ag(df, "grid-pcp-2", theme)

    title = html.H4(f"Batidas de Massa - {choice} (Semana)", className="text-center")

    return [title, table]
