"""
Modulo responsável por criar o layout da página de dashboards de management.
"""

from io import StringIO

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
from components import bar_chart_details, date_picker_dmc, segmented_btn
from dash import Input, Output, callback, html
from dash.exceptions import PreventUpdate
from dash_bootstrap_templates import ThemeSwitchAIO
from helpers.my_types import TURN_SEGMENTED_DICT, TemplateType

# =========================================== Variáveis ========================================== #
seg_btn = segmented_btn.SegmentedBtn()
dpd = date_picker_dmc.DatePickerDMC()

# ============================================ Layout ============================================ #
layout = (
    dmc.Card(
        [
            html.H1("Detalhes Tempos do Mês Corrente", className="text-center"),
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
    ),
)


# =========================================== Callbacks ========================================== #
@callback(
    [
        Output("date-picker", "minDate"),
        Output("date-picker", "maxDate"),
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

    return str(min_date), str(max_date)


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
