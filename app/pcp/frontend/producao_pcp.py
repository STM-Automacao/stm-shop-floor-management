"""
Módulo para Análise de Massadas e pães e suas perdas ou sobras
"""

from io import StringIO

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
from components.grid_aggrid import GridAgGrid
from dash import Input, Output, callback, html
from dash_bootstrap_templates import ThemeSwitchAIO
from pcp.helpers.functions_pcp import AuxFuncPcp

# =========================================== Variáveis ========================================== #
pcp_builder = GridAgGrid()
afc = AuxFuncPcp()

# ================================================================================================ #
#                                              LAYOUT                                              #
# ================================================================================================ #
layout = dbc.Stack(
    [
        html.H1("Produção de Pães por Semana e Produto", className="text-center mt-3 mb-3"),
        dbc.Row(
            dmc.Card(id="pcp-paes-prod", shadow="sm"),
        ),
    ]
)


# ================================================================================================ #
#                                             CALLBACKS                                            #
# ================================================================================================ #


# ========================================= Pães ======================================== #
@callback(
    Output("pcp-paes-prod", "children"),
    [Input(ThemeSwitchAIO.ids.switch("theme"), "value"), Input("store-df-caixas-cf", "data")],
)
def update_paes(theme, data):
    """
    Atualiza o card de teste de pães.

    Args:
        theme (str): O tema atual do dashboard.
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

    # Limpar os dados
    df_cleaned = afc.adjust_prod(df)

    # Cria coluna com caixas de pães
    df_cleaned["Pães(cx)"] = df_cleaned.QTD / 10

    # Ajustar a data para o formato dd/mm
    df_cleaned.Data_Semana = df_cleaned.Data_Semana.dt.strftime("%d/%m")

    # Ajustar QTD de xxxxx para xx.xxx
    df_cleaned.QTD = df_cleaned.QTD.apply(lambda x: f"{x:,.0f}".replace(",", "."))
    df_cleaned["Pães(cx)"] = df_cleaned["Pães(cx)"].apply(lambda x: f"{x:,.0f}".replace(",", "."))

    # Renomear colunas
    df_cleaned.columns = [
        "Ano",
        "Semana",
        "Data Inicial",
        "Produto",
        "Fábrica",
        "Pães(un)",
        "Pães(cx)",
    ]

    # Ordenar as colunas
    df_cleaned = df_cleaned.sort_values(
        by=["Ano", "Semana", "Fábrica", "Produto"], ascending=[False, False, True, True]
    )

    table = pcp_builder.create_grid_ag(df_cleaned, "grid-pcp-3", theme)

    return table
