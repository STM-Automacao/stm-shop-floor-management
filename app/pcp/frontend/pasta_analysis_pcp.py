"""Módulo para Análise de Pasta."""

from io import StringIO

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
from components.grid_aggrid import GridAgGrid
from dash import Input, Output, callback, html
from dash_bootstrap_templates import ThemeSwitchAIO
from helpers.my_types import GRID_FORMAT_NUMBER_BR, GRID_NUMBER_COLS, GRID_STR_NUM_COLS
from pcp.helpers.functions_pcp import AuxFuncPcp
from pcp.helpers.types_pcp import RENDIMENTO_PASTA

# =========================================== Variáveis ========================================== #

pcp_builder = GridAgGrid()
afc = AuxFuncPcp()

# ================================================================================================ #
#                                              LAYOUT                                              #
# ================================================================================================ #

layout = dbc.Stack(
    [
        dbc.Row(dmc.Card(id="pcp-pasta-analysis", shadow="sm")),
    ]
)

# ================================================================================================ #
#                                             CALLBACKS                                            #
# ================================================================================================ #


@callback(
    Output("pcp-pasta-analysis", "children"),
    [
        Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
        Input("store-df-caixas-cf", "data"),
        Input("df_pasta_week", "data"),
    ],
)
def func_name(theme, prod_recheio, week_massa):
    """
    Atualiza o card análise de pasta.

    Args:
        theme (str): O tema atual do dashboard.
        data (str): Os dados no formato JSON para atualizar o card.

    Returns:
        dbc.Table: A tabela gerada a partir dos dados fornecidos.
        Retorna a mensagem "Sem dados disponíveis." se data for None.
    """

    if prod_recheio is None or week_massa is None:
        return "Sem dados disponíveis."

    # Carregar os dados
    # pylint: disable=no-member
    df_prod = pd.read_json(StringIO(prod_recheio), orient="split")
    df_week = pd.read_json(StringIO(week_massa), orient="split")

    # =============================== Lidando Com Dados Do Recheio =============================== #
    # Ajustar os dados de produção
    df_prod_recheio = afc.adjust_prod(df_prod)

    # Calcula quantidade de massa gasta por produto
    df_prod_recheio.QTD = df_prod_recheio.QTD * df_prod_recheio.PRODUTO.map(RENDIMENTO_PASTA)

    # Mapeamento de substituições
    prod_dict = {
        r".*TRD.*": "Tradicional",
        r".*CEB.*": "Cebola",
        r".*PIC.*": "Picante",
        r".*DOCE.*": "Doce",
    }

    # Usar expressão regular para substituir com base no mapeamento
    df_prod_recheio["PRODUTO"] = df_prod_recheio["PRODUTO"].replace(prod_dict, regex=True)

    print(df_prod_recheio)
