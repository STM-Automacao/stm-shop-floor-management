"""
    Este módulo é o responsável por criar o layout do modal de histórico.
"""

import dash_ag_grid as dag

# cSpell: words mcolors lightgray customdata eficiencia applymap
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import matplotlib.colors as mcolors
import pandas as pd
import plotly.express as px
import seaborn as sns
from dash import Input, Output, callback, dcc, html
from dash.exceptions import PreventUpdate

# pylint: disable=E0401
from database.last_month_ind import LastMonthInd

from app import app

last_month = LastMonthInd()

layout = [
    dbc.ModalHeader("Histórico"),
    dbc.ModalBody(
        [
            dbc.Row(dcc.Graph(id="graph-history-modal-perdas")),
            html.Hr(),
            html.H5("Desempenho Mensal", className="inter"),
            dbc.Row(id="table-history-modal"),
        ]
    ),
    dbc.ModalFooter(
        dmc.Image(
            # pylint: disable=E1101
            src=app.get_asset_url("Logo Horizontal_PXB.png"),
            width="125px",
            withPlaceholder=True,
        ),
    ),
]


@callback(
    [Output("graph-history-modal-perdas", "figure"), Output("table-history-modal", "children")],
    [Input("store-info", "data")],
)
def update_graph_history_modal(_):
    """
    Função que atualiza o gráfico de perdas do modal de histórico.
    """
    df_history, df_top_stops = last_month.get_historic_data()

    if df_top_stops.empty:
        raise PreventUpdate

    # -------------------- Gráfico de Perdas -------------------- #

    # Cria uma paleta de cores com os valores únicos na coluna 'problema'
    palette = sns.dark_palette("lightgray", df_top_stops["problema"].nunique())

    # Converte as cores RGB para hexadecimal
    palette_hex = [mcolors.to_hex(color) for color in palette]

    # Cria um dicionário que mapeia cada valor único na coluna 'problema' para uma cor na paleta
    color_map = dict(zip(df_top_stops["problema"].unique(), palette_hex))

    fig = px.bar(
        df_top_stops,
        x="motivo_nome",
        y="tempo_registro_min",
        color="problema",
        color_discrete_map=color_map,
        title="Principais Paradas",
        labels={"motivo_nome": "Motivo", "tempo_registro_min": "Tempo Perdido (min)"},
        template="plotly_white",
        barmode="stack",
    )

    fig.update_layout(
        title_x=0.5,
        font=dict(family="Inter"),
        showlegend=True,
    )

    # -------------------- Tabela de Desempenho Mensal -------------------- #

    # Transforma 2024-01 em Jan/2024
    df_history["data_registro"] = pd.to_datetime(df_history["data_registro"], format="%Y-%m")
    df_history["data_registro"] = df_history["data_registro"].dt.strftime("%b/%Y")
    # Transforma 415641 em 415.641
    df_history["total_caixas"] = df_history["total_caixas"].apply(
        lambda x: f"{x:,.0f} cxs".replace(",", ".")
    )
    # Transforma 56 em 56%
    df_history["eficiencia_media"] = df_history["eficiencia_media"].map(lambda x: f"{x:.0f}%")
    df_history["performance_media"] = df_history["performance_media"].map(lambda x: f"{x:.0f}%")
    df_history["reparos_media"] = df_history["reparos_media"].map(lambda x: f"{x:.0f}%")
    # Transforma 244502 em 244.502 min
    df_history["parada_programada"] = df_history["parada_programada"].apply(
        lambda x: f"{x:,.0f} min".replace(",", ".")
    )

    columns_def = [
        {"headerName": "Mês/Ano", "field": "data_registro"},
        {"headerName": "Produção Total", "field": "total_caixas"},
        {"headerName": "Eficiência", "field": "eficiencia_media"},
        {"headerName": "Performance", "field": "performance_media"},
        {"headerName": "Reparos", "field": "reparos_media"},
        {"headerName": "Parada Programada", "field": "parada_programada"},
    ]

    table = dag.AgGrid(
        id="table-history-modal",
        columnDefs=columns_def,
        rowData=df_history.to_dict("records"),
        columnSize="responsiveSizeToFit",
        dashGridOptions={"pagination": True, "paginationAutoPageSize": True},
        style={"height": "600px"},
    )
    return fig, table
