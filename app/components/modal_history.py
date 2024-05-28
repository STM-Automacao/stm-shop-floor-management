"""
    Este módulo é o responsável por criar o layout do modal de histórico.
"""

import textwrap

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import matplotlib.colors as mcolors
import pandas as pd
import plotly.express as px
import seaborn as sns
from babel.dates import format_date
from components import chart_history, grid_eff, history_components
from dash import Input, Output, callback, dcc, html
from dash.exceptions import PreventUpdate
from dash_bootstrap_templates import ThemeSwitchAIO
from database.last_month_ind import LastMonthInd
from helpers.my_types import TemplateType
from service.big_data import BigData

last_month = LastMonthInd()
hc = history_components.HistoryComponents()
ge = grid_eff.GridEff()

# ============================================ Layout =========================================== #
layout = [
    dcc.Interval(id="interval-component", interval=24 * 60 * 60 * 1000),
    dbc.Row(dbc.Card(dcc.Graph(id="graph-history-modal-perdas"), className="p-2")),
    html.Hr(),
    html.H4("Desempenho Mensal", className="inter"),
    dbc.Row(dbc.Card(id="table-history-modal", className="p-2")),
    html.Hr(),
    html.H4("Dados de Paradas", className="inter"),
    dbc.Card(
        [
            dbc.Row(
                [
                    dbc.Col(
                        hc.create_btn_segmented(
                            "segmented_btn_general",
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
                        dmc.DatesProvider(
                            id="dates-provider-history",
                            children=hc.create_date_picker("date-picker-general", 4),
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
    html.Hr(),
    html.H4("Dados de Paradas por blocos", className="inter"),
    dbc.Card(
        [
            dbc.Row(
                [
                    dbc.Col(
                        hc.create_btn_segmented(
                            "segmented_btn_block",
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
                        dmc.DatesProvider(
                            id="dates-provider-block",
                            children=hc.create_date_picker("date-picker-block", 4),
                            settings={"locale": "pt-br"},
                        ),
                        md=3,
                        class_name="p-2",
                        align="center",
                    ),
                    dbc.Col(
                        dmc.Switch(
                            id="switch-block",
                            description="Mostrar não apontado",
                            radius="md",
                            checked=False,
                            size="lg",
                            color="grey",
                            onLabel="ON",
                            offLabel="OFF",
                        ),
                        md=2,
                        class_name="p-2",
                        align="center",
                    ),
                ],
                justify="evenly",
            ),
            dbc.Row(
                id="icicle-chart-block",
                class_name="inter",
            ),
        ],
        outline=True,
        class_name="p-2 mb-5 shadow-lg",
    ),
]


# ========================================= Callbacks ========================================= #
@callback(
    Output("graph-history-modal-perdas", "figure"),
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

    return fig


@callback(
    Output("table-history-modal", "children"),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
)
def update_table_history_modal(light_theme):
    """
    Função que atualiza a tabela de desempenho mensal do modal de histórico.
    """
    df_history, _ = last_month.get_historic_data()

    if df_history.empty:
        raise PreventUpdate

    # Transforma 2024-01 em Jan/2024
    df_history["data_registro"] = pd.to_datetime(df_history["data_registro"], format="%Y-%m")
    df_history["data_registro"] = df_history["data_registro"].apply(
        lambda x: format_date(x, "MMM/yy", locale="pt_BR").replace(".", "").capitalize()
    )

    table = ge.create_grid_history(df_history, light_theme)

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


# ===================================== Variáveis De Ambiente ==================================== #

# Ler os dados de big data
bg = BigData()
df_big = bg.get_big_data()
df_stops, _, _ = last_month.get_historic_data_analysis()

# Ajuste de turno
turn_options = {
    "Noturno": "NOT",
    "Matutino": "MAT",
    "Vespertino": "VES",
    "Total": "TOT",
}


def adjust_df(date: list[str], line: list[str], turn: str = None) -> pd.DataFrame:
    """
    Ajusta o DataFrame de acordo com os filtros de data, turno e linha.

    Parâmetros:
    - date (list[str]): Lista de datas a serem filtradas.
    - turn (str): Turno a ser filtrado.
    - line (list[str]): Lista de linhas a serem filtradas.

    Retorna:
    - pd.DataFrame: DataFrame ajustado de acordo com os filtros aplicados.
    """

    # Filtrar os dados de acordo com a data
    df, date = date_filter(date, df_big.copy(), df_stops.copy())

    if turn is not None:
        turn = turn_options[turn]

        # Filtrar os dados de acordo com o turno
        if turn != "TOT":
            df = df[df["turno"] == turn]

    # Filtrar os dados de acordo com a linha
    df = line_filter(line, df)

    return df


@callback(
    Output("bar-chart-geral-history", "children"),
    [
        Input("segmented_btn_general", "value"),
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

    # Ajustes no dataframe
    df = adjust_df(date, line, turn)

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
    ch = chart_history.ChartHistory()

    return ch.create_bar_chart_details(df, template)


@callback(
    Output("icicle-chart-block", "children"),
    [
        Input("segmented_btn_block", "value"),
        Input("multi-select-block", "value"),
        Input("date-picker-block", "value"),
        Input("switch-block", "checked"),
        Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    ],
)
def update_icicle(path, line, date, switch, toggle_theme):
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

    # Ajustes no dataframe
    df = adjust_df(date, line)

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
    ch = chart_history.ChartHistory()

    return ch.create_icicle_chart(df, path, switch, template)


# ================================================================================================ #
#                                     CORREÇÃO PARA DATE PICKER                                    #
# ================================================================================================ #


@callback(
    [
        Output("dates-provider-block", "children"),
        Output("dates-provider-history", "children"),
    ],
    Input("interval-component", "n_intervals"),
)
def update_dates(_):
    """
    Atualiza as datas dos seletores de data.

    Retorna dois seletores de data criados usando a função `hc.create_date_picker`.

    Parâmetros:
    - _: Parâmetro não utilizado.

    Retorno:
    - date_picker_block: Seletor de data para o bloco.
    - date_picker_general: Seletor de data geral.
    """
    return hc.create_date_picker("date-picker-block", 4), hc.create_date_picker(
        "date-picker-general", 4
    )
