"""
Modulo responsável por criar o layout da página de dashboards de management.
"""

from io import StringIO

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
from components import bar_chart_details, date_picker_dmc, icicle_chart, segmented_btn
from dash import Input, Output, callback, html
from dash.exceptions import PreventUpdate
from dash_bootstrap_templates import ThemeSwitchAIO
from helpers.my_types import TURN_SEGMENTED_DICT, TemplateType

# =========================================== Variáveis ========================================== #
seg_btn = segmented_btn.SegmentedBtn()
dpd = date_picker_dmc.DatePickerDMC()
ice = icicle_chart.IcicleChart()

# ============================================ Layout ============================================ #
layout = [
    dmc.Card(
        [
            html.H3("Detalhes Tempos do Mês Corrente", className="text-center"),
            dbc.Row(
                dbc.Col(
                    seg_btn.create_segmented_btn(
                        "dashboard-management-turno-btn",
                        ["Noturno", "Matutino", "Vespertino", "Total"],
                        "Total",
                    ),
                    md=4,
                    xl=4,
                ),
            ),
            dbc.Row(
                dbc.Col(
                    dpd.create_date_picker("date-picker"),
                    md=4,
                    xl=2,
                ),
                className="inter",
                justify="center",
                class_name="mb-2",
            ),
            dbc.Row(id="bar-chart-details"),
        ],
        shadow="md",
        className="mb-2",
    ),
    dmc.Card(
        [
            html.H3("Análise de Paradas do Mês Corrente", className="text-center inter"),
            dbc.Row(
                [
                    dbc.Col(
                        seg_btn.create_segmented_btn(
                            "dashboard-stops-analysis-path-btn",
                            ["Manutenção", "Equipamento", "Turno", "Motivo"],
                            "Motivo",
                        ),
                        class_name="d-flex justify-content-center align-items-center p-2",
                        md=3,
                        align="center",
                    ),
                    dbc.Col(
                        dmc.MultiSelect(
                            id="dashboard-stops-analysis-multiselect",
                            data=[
                                {"value": "1", "label": "Fabrica 1"},
                                {"value": "2", "label": "Fabrica 2"},
                            ],
                            hidePickedOptions=True,
                            clearable=True,
                            placeholder="Selecione a(s) fábrica(s)",
                            w="85%",
                        ),
                        md=3,
                        xl=2,
                        align="center",
                        class_name="p-2",
                    ),
                    dbc.Col(
                        dpd.create_date_picker("date-picker-stops-dashboard"),
                        md=3,
                        xl=2,
                        align="center",
                        class_name="p-2",
                    ),
                    dbc.Col(
                        dmc.Stack(
                            [
                                dmc.Switch(
                                    id="switch-dashboard-stops-analysis",
                                    description="Mostrar não apontado",
                                    radius="md",
                                    checked=False,
                                    size="sm",
                                    color="grey",
                                    onLabel="ON",
                                    offLabel="OFF",
                                ),
                                dmc.Switch(
                                    id="switch-dashboard-stops-programada",
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
                        align="center",
                        class_name="p-2",
                    ),
                ],
                justify="evenly",
            ),
            dbc.Row(id="stops-analysis-icicle", class_name="inter"),
        ],
        shadow="md",
    ),
]


# =========================================== Callbacks ========================================== #
@callback(
    [
        Output("date-picker", "minDate"),
        Output("date-picker", "maxDate"),
        Output("date-picker-stops-dashboard", "minDate"),
        Output("date-picker-stops-dashboard", "maxDate"),
    ],
    Input("store-info", "data"),
)
def details_picker(info):
    """
    Creates and returns a date picker component for efficiency indicator.

    Args:
        info: The information to be used for creating the date picker component.

    Returns:
        The created date picker component.

    Raises:
        PreventUpdate: If the info parameter is None.
    """

    if info is None:
        raise PreventUpdate

    df = pd.read_json(StringIO(info), orient="split")

    min_date = pd.to_datetime(df["data_registro"]).min().date()
    max_date = pd.to_datetime(df["data_registro"]).max().date()

    return str(min_date), str(max_date), str(min_date), str(max_date)


@callback(
    Output("bar-chart-details", "children"),
    [
        Input("store-info", "data"),
        Input("dashboard-management-turno-btn", "value"),
        Input("date-picker", "value"),
        Input("store-df_working_time", "data"),
        Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    ],
)
def details_bar_chart(info, turn, data_picker, working, toggle_theme):
    """
    Creates a collapsed bar chart details based on the provided information.

    Args:
        info (str): The JSON string containing the information for the bar chart.
        turn (str): The turn value for the bar chart.
        data_picker (str): The data picker value for the bar chart.
        working (bool): Indicates whether the bar chart is in working mode or not.
        toggle_theme (bool): Indicates whether the bar chart should use a light or dark template.

    Returns:
        dict: The collapsed bar chart details.

    Raises:
        PreventUpdate: If the info parameter is None.
    """

    if info is None:
        raise PreventUpdate

    template = TemplateType.LIGHT if toggle_theme else TemplateType.DARK

    turn = TURN_SEGMENTED_DICT[turn]

    # Carrega o string json em um dataframe
    df_info = pd.read_json(StringIO(info), orient="split")
    df_working = pd.read_json(StringIO(working), orient="split")

    bcd = bar_chart_details.BarChartDetails()

    return bcd.create_bar_chart_details(df_info, template, turn, data_picker, df_working)


@callback(
    Output("stops-analysis-icicle", "children"),
    [
        Input("store-info", "data"),
        Input("dashboard-stops-analysis-path-btn", "value"),
        Input("date-picker-stops-dashboard", "value"),
        Input("dashboard-stops-analysis-multiselect", "value"),
        Input("switch-dashboard-stops-analysis", "checked"),
        Input("switch-dashboard-stops-programada", "checked"),
        Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    ],
)
def update_analysis_icicle(
    data, path, date_picker, select, switch_analysis, switch_programada, toggle_theme
):
    """
    Atualiza o gráfico de icicle com base nos parâmetros fornecidos.

    Args:
        data (str): String JSON contendo os dados para o gráfico.
        path (str): Caminho para salvar o gráfico.
        date_picker (str): Data selecionada para filtrar os dados.
        switch_analysis (bool): Indica se falta de apontamento está ativada ou desativada.
        switch_programada (bool): Indica se a parada programada está ativada ou desativada.
        toggle_theme (bool): Indica se o tema claro ou escuro está ativado.

    Returns:
        dcc.Graph: Gráfico de icicle atualizado com base nos parâmetros fornecidos.
        dbc.Alert: Alerta exibido quando não há dados para a data selecionada.
    """
    if data is None:
        raise PreventUpdate

    # Carregar o string json do store em um dataframe
    df = pd.read_json(StringIO(data), orient="split")

    # Ajustar o template do gráfico
    template = TemplateType.LIGHT if toggle_theme else TemplateType.DARK

    # Filtrar pela data selecionada
    if date_picker is not None:
        df = df[pd.to_datetime(df["data_registro"]).dt.date == pd.to_datetime(date_picker).date()]

    # Filtrar pela fábrica selecionada
    if select is not None and select != []:
        df = df[df["fabrica"].isin(list(map(int, select)))]

    # Verificar se há dados para a data selecionada
    if df is None:
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

    # Criar o gráfico de icicle
    return ice.create_icicle_chart(df, path, switch_analysis, switch_programada, template)
