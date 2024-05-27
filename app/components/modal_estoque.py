"""
    Componente com as caixas do estoque
"""

from io import StringIO

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
from dash import Input, Output, callback, html

from app import app

# ================================================================================================ #
#                                              LAYOUT                                              #
# ================================================================================================ #
layout = [
    dbc.ModalHeader("Estoque"),
    dbc.ModalBody(
        [
            html.H5("Caixas em estoque - Atualizado 00HS", className="inter"),
            dbc.Row(
                id="table-estoque",
            ),
        ]
    ),
    dbc.ModalFooter(
        dmc.Image(
            # pylint: disable=E1101
            src=app.get_asset_url("Logo Horizontal_PXB.png"),
            w="125px",
        ),
    ),
]


# ================================================================================================ #
#                                             CALLBACKS                                            #
# ================================================================================================ #
@callback(Output("table-estoque", "children"), [Input("store-df-caixas-cf-tot", "data")])
def update_table_estoque(data):
    """
    Função que atualiza a tabela de estoque.

    Args:
        data (dict): Dados do estoque.

    Returns:
        dbc.Col: Tabela de estoque.
    """
    if data is None:
        return dbc.Col("Sem dados de estoque")

    df = pd.DataFrame(pd.read_json(StringIO(data), orient="split"))

    # Ordenar pela coluna QTD
    df = df.sort_values(by="QTD", ascending=False)

    # Adicionar uma linha no final com o total de caixas
    total = df["QTD"].sum()
    df = df.append(
        {"PRODUTO": "Total", "QTD": total},
        ignore_index=True,
    )

    table = dbc.Table.from_dataframe(
        df,
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
        className="inter",
    )

    return dbc.Col(table)
