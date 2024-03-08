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
from dash import Input, Output, callback, dcc, html
from dash.exceptions import PreventUpdate
from dash_bootstrap_templates import ThemeSwitchAIO
from database.last_month_ind import LastMonthInd
from helpers.types import TemplateType

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
            width="125px",
            withPlaceholder=True,
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

    # Limita o problema a 5 palavras
    df_top_stops["problema"] = df_top_stops["problema"].apply(lambda x: " ".join(x.split()[:4]))

    # Adiciona quebra de linha no eixo x para melhor visualização
    df_top_stops["motivo_nome"] = df_top_stops["motivo_nome"].apply(
        lambda x: "<br>".join(textwrap.wrap(x, width=10))
    )

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
        template=TemplateType.LIGHT.value if light_theme else TemplateType.DARK.value,
        barmode="stack",
    )

    fig.update_layout(
        title_x=0.5,
        font=dict(family="Inter"),
        showlegend=True,
        plot_bgcolor="RGBA(0,0,0,0.01)",
        margin=dict({"t": 80, "b": 40, "l": 40, "r": 40}),
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
        className="ag-theme-quartz-dark" if light_theme is False else "ag-theme-quartz",
    )
    return fig, table
