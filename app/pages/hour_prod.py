"""
Módulo que contém a página de produção por hora.
"""

from io import StringIO

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import numpy as np
import pandas as pd
from components import grid_aggrid
from dash import Input, Output, callback, html
from dash_bootstrap_templates import ThemeSwitchAIO

gag = grid_aggrid.GridAgGrid()

# ================================================================================================ #
#                                              LAYOUT                                              #
# ================================================================================================ #
layout = dbc.Row(
    [
        dmc.Card(
            id="hour-prod-table",
            shadow="sm",
        )
    ],
)


# ================================================================================================ #
#                                             CALLBACKS                                            #
# ================================================================================================ #
@callback(
    Output("hour-prod-table", "children"),
    Input("store-df-info-pure", "data"),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
)
def update_hour_prod_table(data, theme):
    """
    Função que atualiza a tabela de produção por hora.

    Args:
        data (dict): Dados de produção.

    Returns:
        dbc.Col: Tabela de produção por hora.
    """
    if data is None:
        return dbc.Col("Sem dados de produção")

    today = pd.to_datetime("today").date()

    # Filtra pela data de hoje
    df = pd.DataFrame(pd.read_json(StringIO(data), orient="split"))

    # Transforma a data de registro em datetime
    df["data_registro"] = pd.to_datetime(df["data_registro"])

    # Filtra a data
    df = df[df["data_registro"].dt.date == today]

    # Remove a linha 0
    df = df[df["linha"] != 0]

    # Concatena a data e hora
    df["data_hora"] = (
        df["data_registro"].astype(str)
        + " "
        + df["hora_registro"].astype(str).str.split(".").str[0]
    )

    df["data_hora"] = pd.to_datetime(df["data_hora"])

    # Defina 'linha' e 'data_hora' como índices
    df.set_index(["linha", "data_hora"], inplace=True)

    # Agregue os dados por hora e aplique funções diferentes para diferentes colunas
    df_resampled = (
        df.groupby("linha")
        .resample("h", level="data_hora")
        .agg(
            {
                "contagem_total_produzido": ["first", "last"],
                "contagem_total_ciclos": ["first", "last"],
            }
        )
    )

    # Calcule a diferença entre o primeiro e o último registro de cada hora
    df_resampled["total_produzido"] = (
        df_resampled["contagem_total_produzido"]["last"]
        - df_resampled["contagem_total_produzido"]["first"]
    )

    df_resampled["total_ciclos"] = (
        df_resampled["contagem_total_ciclos"]["last"]
        - df_resampled["contagem_total_ciclos"]["first"]
    )

    # Reiniciar o índice do DataFrame
    df_resampled.reset_index(inplace=True)

    # Ajusta a produção
    mask = df_resampled["total_ciclos"] - df_resampled["total_produzido"] <= 60
    df_resampled["total_produzido"] = np.where(
        mask, df_resampled["total_produzido"], df_resampled["total_ciclos"]
    )

    # Selecionar apenas as colunas necessárias
    df_final = df_resampled[["linha", "data_hora", "total_produzido"]]

    # Preenchendo valores ausentes com 0
    df_final.loc[:, "total_produzido"] = df_final["total_produzido"].fillna(0)

    # Dividir o total produzido por 10 para ter o número de caixas
    df_final.loc[:, "total_produzido"] = np.floor(df_final["total_produzido"] / 10).astype(int)

    # Pivotar a tabela
    df_pivot = df_final.pivot(index="data_hora", columns="linha", values="total_produzido")

    # Cria uma nova coluna que representa o intervalo de tempo
    df_pivot["Intervalo"] = (
        df_pivot.index.hour.astype(str) + "hs à " + (df_pivot.index.hour + 1).astype(str) + "hs"
    )

    # Reordena as colunas para que 'Intervalo' seja a primeira coluna
    df_pivot = df_pivot[["Intervalo"] + [col for col in df_pivot.columns if col != "Intervalo"]]

    # Renomeia as colunas para que sejam mais legíveis
    df_pivot.columns = [col if col == "Intervalo" else f"Linha {col}" for col in df_pivot.columns]

    table = gag.create_grid_ag(df_pivot, "hour-prod-table", theme, hei="1100px")

    title = html.H3("Produção de caixas por hora", className="text-center mb-3")

    return [title, table]
