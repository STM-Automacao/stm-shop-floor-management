"""
    Este módulo é o responsável por criar o layout da página de histórico.
"""

import textwrap

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import matplotlib.colors as mcolors
import pandas as pd
import plotly.express as px
import seaborn as sns
from babel.dates import format_date
from components import bar_chart_details, date_picker_dmc, grid_aggrid, icicle_chart, segmented_btn
from dash import Input, Output, callback, dcc, html
from dash.exceptions import PreventUpdate
from dash_bootstrap_templates import ThemeSwitchAIO
from database.last_month_ind import LastMonthInd
from helpers.my_types import (
    GRID_FORMAT_NUMBER_BR,
    GRID_STR_NUM_COLS,
    TURN_SEGMENTED_DICT,
    TemplateType,
)
from management.components import history_components
from management.helpers import big_stops_data_manager as bsdm

# =========================================== Variáveis ========================================== #

last_month = LastMonthInd()
hc = history_components.HistoryComponents()
seg_btn = segmented_btn.SegmentedBtn()
gag = grid_aggrid.GridAgGrid()
dpd = date_picker_dmc.DatePickerDMC()
bcd = bar_chart_details.BarChartDetails()
big_data_manager = bsdm.BigStopsDataManager()

# ============================================ Layout =========================================== #
layout = dmc.Stack(
    [
        dcc.Interval(id="interval-component", interval=60 * 1000),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dcc.Graph(id="graph-history-pg-perdas"),
                        className="p-2",
                    ),
                    xl=6,
                    md=12,
                    class_name="p-2",
                ),
                dbc.Col(
                    dbc.Card(
                        children=[
                            html.H6("Desempenho Mensal", className="inter text-center mb-3 mt-3"),
                            dbc.Row(id="table-history-pg"),
                        ],
                        className="p-2",
                    ),
                    xl=6,
                    md=12,
                    class_name="p-2",
                ),
            ],
            justify="between",
            align="center",
        ),
        html.Hr(),
        html.H5("Apontamentos de Paradas dos Últimos 4 meses", className="inter"),
        dbc.Card(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            seg_btn.create_segmented_btn(
                                "segmented_btn_general-history",
                                ["Noturno", "Matutino", "Vespertino", "Total"],
                                "Matutino",
                            ),
                            class_name=("d-flex justify-content-center align-items-center p-2"),
                            md=3,
                            align="center",
                        ),
                        dbc.Col(
                            hc.create_multiselect("multi-select-general"),
                            md=3,
                            class_name="p-2",
                            align="center",
                        ),
                        dbc.Col(
                            dpd.create_date_picker("date-picker-general"),
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
            class_name="p-2 mb-5 shadow-sm",
        ),
        html.Hr(),
        html.H4("Análise das paradas dos Últimos 4 meses", className="inter"),
        dbc.Card(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            seg_btn.create_segmented_btn(
                                "segmented_btn_block-history",
                                ["Manutenção", "Equipamento", "Turno", "Motivo"],
                                "Turno",
                            ),
                            class_name=("d-flex justify-content-center align-items-center p-2"),
                            md=3,
                            align="center",
                        ),
                        dbc.Col(
                            hc.create_multiselect("multi-select-block"),
                            md=3,
                            class_name="p-2",
                            align="center",
                        ),
                        dbc.Col(
                            dpd.create_date_picker("date-picker-block"),
                            md=3,
                            class_name="p-2",
                            align="center",
                        ),
                        dbc.Col(
                            dmc.Stack(
                                children=[
                                    dmc.Switch(
                                        id="switch-block",
                                        description="Mostrar não apontado",
                                        radius="md",
                                        checked=False,
                                        size="sm",
                                        color="grey",
                                        onLabel="ON",
                                        offLabel="OFF",
                                    ),
                                    dmc.Switch(
                                        id="switch-Programada-block",
                                        description="Mostrar parada programada",
                                        radius="md",
                                        checked=True,
                                        size="sm",
                                        color="grey",
                                        onLabel="ON",
                                        offLabel="OFF",
                                    ),
                                ],
                                gap="xs",
                            ),
                            md=2,
                            class_name="p-2",
                            align="center",
                        ),
                    ],
                    justify="evenly",
                ),
                dbc.Row(id="icicle-chart-block", class_name="inter"),
            ],
            outline=True,
            class_name="p-2 mb-5 shadow-sm",
        ),
    ]
)


# ========================================= Callbacks ========================================= #
@callback(
    [
        Output("date-picker-general", "minDate"),
        Output("date-picker-general", "maxDate"),
        Output("date-picker-general", "type"),
        Output("date-picker-general", "placeholder"),
    ],
    Input("interval-component", "n_intervals"),
)
def date_picker_general_update(__n_int):
    """
    Atualiza as datas mínima e máxima do seletor de data da pg de histórico.

    Args:
        _: O número de intervalos.

    Returns:
        tuple: Uma tupla contendo a data mínima, a data máxima e o tipo de seleção de data.
    """

    now = pd.Timestamp.now()
    placeholder = ("Selecione a(s) data(s)",)
    select_type = "multiple"
    min_date = pd.to_datetime(now.replace(day=1) - pd.DateOffset(months=4))
    max_date = pd.to_datetime(now - pd.DateOffset(days=1)).date()

    return str(min_date), str(max_date), select_type, placeholder


@callback(
    [
        Output("date-picker-block", "minDate"),
        Output("date-picker-block", "maxDate"),
        Output("date-picker-block", "type"),
        Output("date-picker-block", "placeholder"),
    ],
    Input("interval-component", "n_intervals"),
)
def date_picker_block_update(_):
    """
    Atualiza as datas mínima e máxima do seletor de data da pg de histórico.

    Args:
        _: O número de intervalos.

    Returns:
        tuple: Uma tupla contendo a data mínima, a data máxima e o tipo de seleção de data.
    """

    now = pd.Timestamp.now()

    placeholder = ("Selecione a(s) data(s)",)
    select_type = "multiple"
    min_date = now.replace(day=1) - pd.DateOffset(months=4)
    max_date = pd.to_datetime(now - pd.DateOffset(days=1)).date()

    return str(min_date), str(max_date), select_type, placeholder


@callback(
    Output("graph-history-pg-perdas", "figure"),
    [Input("store-info", "data"), Input(ThemeSwitchAIO.ids.switch("theme"), "value")],
)
def update_graph_history_pg(_, light_theme):
    """
    Função que atualiza o gráfico de perdas do pg de histórico.
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

    return fig


@callback(
    Output("table-history-pg", "children"),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
)
def update_table_history_pg(light_theme):
    """
    Função que atualiza a tabela de desempenho mensal da pg de histórico.
    """
    df_history, _ = last_month.get_historic_data()

    if df_history.empty:
        raise PreventUpdate

    # Transforma 2024-01 em Jan/2024
    df_history["data_registro"] = pd.to_datetime(df_history["data_registro"], format="%Y-%m")
    df_history["data_registro"] = df_history["data_registro"].apply(
        lambda x: format_date(x, "MMM/yy", locale="pt_BR").replace(".", "").capitalize()
    )

    df_history.eficiencia = (df_history.eficiencia * 100).map(lambda x: f"{x:.0f}%")
    df_history.performance = (df_history.performance * 100).map(lambda x: f"{x:.0f}%")
    df_history.reparo = (df_history.reparo * 100).map(lambda x: f"{x:.0f}%")
    df_history.parada_programada = df_history.parada_programada.map(
        lambda x: f"{x:,.0f} min".replace(",", ".")
    )

    defs = [
        {"headerName": "Mês/Ano", "field": "data_registro", "maxWidth": 150},
        {
            "headerName": "Produção Total",
            "field": "total_caixas",
            **GRID_STR_NUM_COLS,
            **GRID_FORMAT_NUMBER_BR,
        },
        {"headerName": "Eficiência", "field": "eficiencia", "maxWidth": 150},
        {"headerName": "Performance", "field": "performance", "maxWidth": 150},
        {"headerName": "Reparos", "field": "reparo", "maxWidth": 150},
        {"headerName": "Parada Programada", "field": "parada_programada"},
    ]

    table = gag.create_grid_ag(df_history, "table-history-ag", light_theme, defs, hei="400px")

    return table


def date_filter(date: list[str], big: pd.DataFrame, stops: pd.DataFrame) -> tuple:
    """
    Filtra os dados de acordo com a data fornecida.

    Args:
        date (list[str]): Lista de datas no formato "YYYY-MM-DD".
        big (pd.DataFrame): DataFrame contendo os dados principais.
        stops (pd.DataFrame): DataFrame contendo os dados de paradas.

    Returns:
        tuple: Uma tupla contendo o DataFrame filtrado e a lista de datas fornecida.
    """

    if date is not None and len(date) > 0:
        # Seleciona os dados de acordo com a data. Date é uma lista.
        date = [pd.to_datetime(d).date() for d in date]
        if (
            date[0] < pd.Timestamp("2024-05-01").date()
            and date[-1] < pd.Timestamp("2024-05-01").date()
        ):
            df = stops
        else:
            df = big

        # Filtrar os dados de acordo com a data, date é uma lista
        df["data_registro"] = pd.to_datetime(df["data_registro"]).dt.date
        df = df[df["data_registro"].isin(date)]

    else:
        df = big

    return df, date


def line_filter(line: list[str], df: pd.DataFrame) -> pd.DataFrame:
    """
    Filtra um DataFrame de acordo com uma lista de linhas.

    Parâmetros:
    line (list[str]): A lista de linhas a serem filtradas.
    df (pd.DataFrame): O DataFrame a ser filtrado.

    Retorna:
    pd.DataFrame: O DataFrame filtrado de acordo com as linhas especificadas.
    """

    # Transformar a linha em uma lista de inteiros
    line_n = [int(i) for i in line] if line else line

    # Filtrar os dados de acordo com a linha
    if line_n is not None and len(line_n) > 0:
        df = df[df["linha"].isin(line_n)]

    return df


def adjust_df(
    date: list[str], line: list[str], big: pd.DataFrame, stops: pd.DataFrame
) -> pd.DataFrame:
    """
    Ajusta o DataFrame de acordo com os filtros de data, turno e linha.

    Parâmetros:
    - date (list[str]): Lista de datas a serem filtradas.
    - line (list[str]): Lista de linhas a serem filtradas.

    Retorna:
    - pd.DataFrame: DataFrame ajustado de acordo com os filtros aplicados.
    """

    # Filtrar os dados de acordo com a data
    df, date = date_filter(date, big, stops)

    # Filtrar os dados de acordo com a linha
    df = line_filter(line, df)

    return df


@callback(
    Output("bar-chart-geral-history", "children"),
    [
        Input("segmented_btn_general-history", "value"),
        Input("multi-select-general", "value"),
        Input("date-picker-general", "value"),
        Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    ],
)
def update_general_chart(turn, line, date, toggle_theme):
    """
    Atualiza o gráfico geral com base nos parâmetros fornecidos.

    Args:
        turn (str): O turno a ser filtrado.
        line (List[str]): A(s) linha(s) a ser(em) filtrada(s).
        date (List[str]): A(s) data(s) a ser(em) filtrada(s).
        toggle_theme (bool): Indica se o tema está em modo claro ou escuro.

    Returns:
        Bar Chart: O gráfico atualizado.

    """
    # Verificar se o tema está em modo claro ou escuro
    template = TemplateType.LIGHT if toggle_theme else TemplateType.DARK

    big_data_manager.get_big_stops_if_needed()
    df_big = big_data_manager.df_big
    df_stops = big_data_manager.df_stops

    # Ajustes no dataframe
    df = adjust_df(date, line, df_big, df_stops)

    # Se selecionar apenas uma data e ela não estiver no df devolver texto de aviso
    if (
        date is not None
        and len(date) == 1
        and pd.to_datetime(date[0]).date() not in df["data_registro"].unique()
    ):
        return dbc.Alert(
            "Não há dados para a data selecionada.",
            color="warning",
            style={
                "width": "80%",
                "textAlign": "center",
                "margin-left": "auto",
                "margin-right": "auto",
            },
        )

    turn = TURN_SEGMENTED_DICT[turn]

    return bcd.create_bar_chart_details(df, template, turn, alt=True)


@callback(
    Output("icicle-chart-block", "children"),
    [
        Input("segmented_btn_block-history", "value"),
        Input("multi-select-block", "value"),
        Input("date-picker-block", "value"),
        Input("switch-block", "checked"),
        Input("switch-Programada-block", "checked"),
        Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    ],
)
def update_icicle(path, line, date, switch, switch_programada, toggle_theme):
    """
    Atualiza o gráfico geral com base nos parâmetros fornecidos.

    Args:
        path (str): O caminho dos blocos.
        line (List[str]): A(s) linha(s) a ser(em) filtrada(s).
        date (List[str]): A(s) data(s) a ser(em) filtrada(s).
        toggle_theme (bool): Indica se o tema está em modo claro ou escuro.

    Returns:
        Bar Chart: O gráfico atualizado.

    """
    # Verificar se o tema está em modo claro ou escuro
    template = TemplateType.LIGHT if toggle_theme else TemplateType.DARK

    big_data_manager.get_big_stops_if_needed()
    df_big = big_data_manager.df_big
    df_stops = big_data_manager.df_stops

    # Ajustes no dataframe
    df = adjust_df(date, line, df_big, df_stops)

    # Se selecionar apenas uma data e ela não estiver no df devolver texto de aviso
    if (
        date is not None
        and len(date) == 1
        and pd.to_datetime(date[0]).date() not in df["data_registro"].unique()
    ):
        return dbc.Alert(
            "Não há dados para a data selecionada.",
            color="warning",
            style={
                "width": "80%",
                "textAlign": "center",
                "margin-left": "auto",
                "margin-right": "auto",
            },
        )

    # Instanciar chart
    ch = icicle_chart.IcicleChart()

    return ch.create_icicle_chart(df, path, switch, switch_programada, template)
