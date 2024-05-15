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
from components import bar_chart_details, btn_modal
from dash import Input, Output, callback, dcc, html
from dash.exceptions import PreventUpdate
from dash_bootstrap_templates import ThemeSwitchAIO
from dash_iconify import DashIconify
from database.last_month_ind import LastMonthInd
from helpers.my_types import IndicatorType, TemplateType
from service.big_data import BigData

last_month = LastMonthInd()

lines_number = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14"]

# ============================================ Layout =========================================== #
layout = [
    dbc.Row(dcc.Graph(id="graph-history-modal-perdas")),
    html.Hr(),
    html.H4("Desempenho Mensal", className="inter"),
    dbc.Row(id="table-history-modal"),
    html.Hr(),
    html.H4("Dados de Paradas", className="inter"),
    dbc.Card(
        [
            dbc.Row(
                [
                    dbc.Col(
                        btn_modal.create_radio_btn_turn("history"),
                        class_name=(
                            "radio-group d-flex justify-content-center align-items-center p-2"
                        ),
                        md=3,
                        align="center",
                    ),
                    dbc.Col(
                        dmc.MultiSelect(
                            data=[
                                {
                                    "group": "Fabrica 1",
                                    "items": [
                                        {"label": f"Linha {line}", "value": line}
                                        for line in lines_number[:8]
                                    ],
                                },
                                {
                                    "group": "Fabrica 2",
                                    "items": [
                                        {"label": f"Linha {line}", "value": line}
                                        for line in lines_number[8:]
                                    ],
                                },
                            ],
                            className="p-2",
                            hidePickedOptions=True,
                            clearable=True,
                            placeholder="Selecione as linhas",
                            w="80%",
                            id="multi-select-history",
                        ),
                        md=3,
                        class_name="p-2",
                        align="center",
                    ),
                    dbc.Col(
                        dmc.DatesProvider(
                            id="dates-provider-history",
                            children=dmc.DatePicker(
                                id="date-picker-history",
                                placeholder="Selecione uma data",
                                valueFormat="dddd - D MMM, YYYY",
                                firstDayOfWeek=0,
                                clearable=True,
                                variant="filled",
                                leftSection=DashIconify(icon="uiw:date"),
                                w="80%",
                            ),
                            settings={"locale": "pt-br"},
                        ),
                        md=3,
                        class_name="p-2",
                        align="center",
                    ),
                ],
                justify="evenly",
            ),
            dbc.Row(
                id="bar-chart-geral-history",
            ),
        ],
        outline=True,
        class_name="p-2 mb-5 shadow-lg",
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


@callback(
    Output("bar-chart-geral-history", "children"),
    [
        Input("radio-items-history", "value"),
        Input("multi-select-history", "value"),
        Input("date-picker-history", "value"),
        Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    ],
)
def update_general_chart(turn, line, date, toggle_theme):

    # Verificar se o tema está em modo claro ou escuro
    template = TemplateType.LIGHT if toggle_theme else TemplateType.DARK

    # Ler os dados de big data
    bg = BigData()
    df_big = bg.get_big_data()
    df_stops, _, _ = last_month.get_historic_data_analysis()
    if date is not None:
        # Seleciona os dados de acordo com a data
        df = df_big if pd.to_datetime(date) > pd.to_datetime("2024-05-01") else df_stops
        # Filtrar os dados de acordo com a data
        df["data_registro"] = pd.to_datetime(df["data_registro"]).dt.date
        df = df[df["data_registro"] == pd.to_datetime(date).date()]

    else:
        df = df_big

    # Filtrar os dados de acordo com o turno
    df = df[df["turno"] == turn]

    # Transformar a linha em uma lista de inteiros
    line_n = [int(i) for i in line] if line else line

    # Filtrar os dados de acordo com a linha
    if line_n is not None and len(line_n) > 0:
        df = df[df["linha"].isin(line_n)]

    # NOTE: Criar novo gráfico ao invés de reaproveitar este

    chart = bar_chart_details.BarChartDetails(df)

    return chart.create_bar_chart_details(IndicatorType.EFFICIENCY, template, turn, date)
