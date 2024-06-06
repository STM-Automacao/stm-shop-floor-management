"""
Módulo para Análise de Massadas e pães e suas perdas ou sobras
"""

from io import StringIO

import dash_bootstrap_components as dbc
import pandas as pd
from dash import Input, Output, callback, html
from dash_bootstrap_templates import ThemeSwitchAIO
from pcp.frontend.components_pcp import ComponentsPcpBuilder
from pcp.helpers.types_pcp import PAO_POR_BANDEJA

# =========================================== Variáveis ========================================== #
pcp_builder = ComponentsPcpBuilder()

# ================================================================================================ #
#                                              LAYOUT                                              #
# ================================================================================================ #
layout = [
    html.H1("Pães", className="text-center mt-3 mb-3"),
    dbc.Row(id="pcp-paes-analysis"),
]

# ================================================================================================ #
#                                             CALLBACKS                                            #
# ================================================================================================ #


# ========================================= Pães ======================================== #
def clean_prod(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpa os dados de produção.

    Args:
        df (pd.DataFrame): O DataFrame contendo os dados de produção.

    Returns:
        pd.DataFrame: O DataFrame limpo.
    """
    # cSpell: words usuario
    # Remover colunas desnecessárias
    df = df.drop(columns=["MAQUINA", "UNIDADE", "LOTE", "USUARIO"])
    df.PRODUTO = df.PRODUTO.str.strip()

    # ==================================== Quantidade De Pães ==================================== #
    # Transforma caixas em bandejas
    df.QTD = df.QTD * 10

    # Transforma bandejas em pães
    df.QTD = df.QTD * df.PRODUTO.map(PAO_POR_BANDEJA)

    return df


@callback(
    Output("pcp-paes-analysis", "children"),
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
    df_cleaned = clean_prod(df)

    table = pcp_builder.create_grid_pcp(df_cleaned, 3, theme)

    return table
