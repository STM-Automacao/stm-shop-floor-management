"""
    Este módulo é o responsável por criar o layout do modal de histórico.
"""

import textwrap

import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import matplotlib.colors as mcolors
import pandas as pd
import plotly.express as px
import seaborn as sns
from babel.dates import format_date
from dash import Input, Output, callback, dcc, html
from dash.exceptions import PreventUpdate
from dash_bootstrap_templates import ThemeSwitchAIO
from database.last_month_ind import LastMonthInd
from helpers.my_types import TemplateType

from app import app

last_month = LastMonthInd()

# ============================================ Layout =========================================== #
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
            w="125px",
        ),
    ),
]


# ========================================= Callbacks ========================================= #
@callback(
    [Output("graph-history-modal-perdas", "figure"), Output("table-history-modal", "children")],
    [Input("store-info", "data"), Input(ThemeSwitchAIO.ids.switch("theme"), "value")],
)
def update_graph_history_modal(_, light_theme):
    """
    Função que atualiza o gráfico de perdas do modal de histórico.
    """
    df_history, df_top_stops = last_month.get_historic_data()

    if df_top_stops.empty:
        raise PreventUpdate

    # -------------------- Gráfico de Perdas -------------------- #

    # Adiciona quebra de linha no eixo x para melhor visualização
    df_top_stops["motivo"] = df_top_stops["motivo"].apply(
        lambda x: "<br>".join(textwrap.wrap(x, width=10))
    )

    # Cria uma paleta de cores com os valores únicos na coluna 'problema'
    palette = (
        sns.dark_palette("gray", df_top_stops["problema"].nunique(), reverse=True)
        if light_theme
        else sns.light_palette("darkgray", df_top_stops["problema"].nunique(), reverse=True)
    )

    # Converte as cores RGB para hexadecimal
    palette_hex = [mcolors.to_hex(color) for color in palette]

    # Cria um dicionário que mapeia cada valor único na coluna 'problema' para uma cor na paleta
    color_map = dict(zip(df_top_stops["problema"].unique(), palette_hex))

    # Transforma 2024-01 em Jan/2024
    df_history["data_registro"] = pd.to_datetime(df_history["data_registro"], format="%Y-%m")
    df_history["data_registro"] = df_history["data_registro"].apply(
        lambda x: format_date(x, "MMM/yy", locale="pt_BR").replace(".", "").capitalize()
    )

    fig = px.bar(
        df_top_stops,
        x="motivo",
        y="tempo",
        color="problema",
        color_discrete_map=color_map,
        title=f"Principais Paradas de {df_history['data_registro'].iloc[-1]}",
        labels={"motivo": "Motivo", "tempo": "Tempo Perdido (min)"},
        template=TemplateType.LIGHT.value if light_theme else TemplateType.DARK.value,
        barmode="stack",
    )

    fig.update_layout(
        title_x=0.5,
        font=dict(family="Inter"),
        showlegend=True,
        plot_bgcolor="RGBA(0,0,0,0.01)",
        margin=dict({"t": 80, "b": 40, "l": 40, "r": 40}),
        legend=dict(title="Problema", orientation="v"),
    )

    # -------------------- Tabela de Desempenho Mensal -------------------- #

    # Transforma 415641 em 415.641
    df_history["total_caixas"] = df_history["total_caixas"].apply(
        lambda x: f"{x:,.0f} cxs".replace(",", ".")
    )
    # Transforma 0.56 em 56%
    df_history["eficiencia"] = df_history["eficiencia"] * 100
    df_history["performance"] = df_history["performance"] * 100
    df_history["reparo"] = df_history["reparo"] * 100
    # Transforma 56 em 56%
    df_history["eficiencia"] = df_history["eficiencia"].map(lambda x: f"{x:.0f}%")
    df_history["performance"] = df_history["performance"].map(lambda x: f"{x:.0f}%")
    df_history["reparo"] = df_history["reparo"].map(lambda x: f"{x:.0f}%")
    # Transforma 244502 em 244.502 min
    df_history["parada_programada"] = df_history["parada_programada"].apply(
        lambda x: f"{x:,.0f} min".replace(",", ".")
    )

    columns_def = [
        {"headerName": "Mês/Ano", "field": "data_registro"},
        {"headerName": "Produção Total", "field": "total_caixas"},
        {"headerName": "Eficiência", "field": "eficiencia"},
        {"headerName": "Performance", "field": "performance"},
        {"headerName": "Reparos", "field": "reparo"},
        {"headerName": "Parada Programada", "field": "parada_programada"},
    ]

    table = dag.AgGrid(
        id="table-history-modal",
        columnDefs=columns_def,
        rowData=df_history.to_dict("records"),
        columnSize="responsiveSizeToFit",
        dashGridOptions={"pagination": True, "paginationAutoPageSize": True},
        style={"height": "600px"},
        className="ag-theme-quartz" if light_theme else "ag-theme-alpine-dark",
    )
    return fig, table
