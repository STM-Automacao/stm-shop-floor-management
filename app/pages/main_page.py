"""
    Página Principal do dashboard
    - Autor: Bruno Tomaz
    - Data de Criação: 15/01/2024
"""

import json
from io import StringIO

import dash_bootstrap_components as dbc
import pandas as pd
from components import gauge, heatmap, line_graph, modal_efficiency, modal_performance, modal_repair
from dash import Input, Output, State, callback, html
from dash.exceptions import PreventUpdate
from dash_bootstrap_templates import ThemeSwitchAIO
from database.last_month_ind import LastMonthInd
from helpers.my_types import IndicatorType, TemplateType

# ======================================== Layout ======================================== #

layout = [
    html.Div(
        [
            dbc.Spinner(
                id="main-page-spinner",
                color="primary",
                size="lg",
                children=[
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Card(
                                    id=f"last-gauge-{IndicatorType.EFFICIENCY.value}",
                                    class_name="p-1",
                                ),
                                sm={"size": 4, "offset": 1, "order": 1},
                                lg={"size": 2, "offset": 0, "order": 1},
                                xxl={"size": 1, "order": 1},
                                class_name="p-1",
                            ),
                            dbc.Col(
                                [
                                    dbc.Card(
                                        id=f"heatmap-{IndicatorType.EFFICIENCY.value}",
                                        class_name="p-1 mb-1",
                                    ),
                                    dbc.Card(
                                        id=f"line-chart-{IndicatorType.EFFICIENCY.value}",
                                        class_name="p-1",
                                    ),
                                ],
                                sm={"size": 12, "offset": 0, "order": 3},
                                lg={"size": 8, "offset": 0, "order": 2},
                                xxl={"size": 10, "order": 2},
                                class_name="p-1",
                            ),
                            dbc.Col(
                                dbc.Card(
                                    id=f"actual-gauge-{IndicatorType.EFFICIENCY.value}",
                                    class_name="p-1",
                                ),
                                sm={"size": 4, "offset": 2, "order": 2},
                                lg={"size": 2, "offset": 0, "order": 3},
                                xxl={"size": 1, "order": 3},
                                class_name="p-1",
                            ),
                        ]
                    ),
                    html.Hr(),
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Card(
                                        id=f"last-gauge-{IndicatorType.PERFORMANCE.value}",
                                        class_name="p-1",
                                    ),
                                    html.H1(
                                        "D", className="text-center", style={"font-size": "4rem"}
                                    ),
                                ],
                                sm={"size": 4, "offset": 1, "order": 1},
                                lg={"size": 2, "offset": 0, "order": 1},
                                xxl={"size": 1, "order": 1},
                                class_name="p-1",
                            ),
                            dbc.Col(
                                [
                                    dbc.Card(
                                        id=f"heatmap-{IndicatorType.PERFORMANCE.value}",
                                        class_name="p-1 mb-1",
                                    ),
                                    dbc.Card(
                                        id=f"line-chart-{IndicatorType.PERFORMANCE.value}",
                                        class_name="p-1",
                                    ),
                                ],
                                sm={"size": 12, "offset": 0, "order": 3},
                                lg={"size": 8, "offset": 0, "order": 2},
                                xxl={"size": 10, "order": 2},
                                class_name="p-1",
                            ),
                            dbc.Col(
                                dbc.Card(
                                    id=f"actual-gauge-{IndicatorType.PERFORMANCE.value}",
                                    class_name="p-1",
                                ),
                                sm={"size": 4, "offset": 2, "order": 2},
                                lg={"size": 2, "offset": 0, "order": 3},
                                xxl={"size": 1, "order": 3},
                                class_name="p-1",
                            ),
                        ]
                    ),
                    html.Hr(),
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Card(
                                    id=f"last-gauge-{IndicatorType.REPAIR.value}", class_name="p-1"
                                ),
                                sm={"size": 4, "offset": 1, "order": 1},
                                lg={"size": 2, "offset": 0, "order": 1},
                                xxl={"size": 1, "order": 1},
                                class_name="p-1",
                            ),
                            dbc.Col(
                                [
                                    dbc.Card(
                                        id=f"heatmap-{IndicatorType.REPAIR.value}",
                                        class_name="p-1 mb-1",
                                    ),
                                    dbc.Card(
                                        id=f"line-chart-{IndicatorType.REPAIR.value}",
                                        class_name="p-1",
                                    ),
                                ],
                                sm={"size": 12, "offset": 0, "order": 3},
                                lg={"size": 8, "offset": 0, "order": 2},
                                xxl={"size": 10, "order": 2},
                                class_name="p-1",
                            ),
                            dbc.Col(
                                dbc.Card(
                                    id=f"actual-gauge-{IndicatorType.REPAIR.value}",
                                    class_name="p-1",
                                ),
                                sm={"size": 4, "offset": 2, "order": 2},
                                lg={"size": 2, "offset": 0, "order": 3},
                                xxl={"size": 1, "order": 3},
                                class_name="p-1",
                            ),
                        ]
                    ),
                ],
            ),
        ],
        id="main-page",
    ),
    # ------------------------- Modal ------------------------- #
    dbc.Modal(
        children=modal_efficiency.layout,
        id="modal_eff",
        size="xl",
        scrollable=True,
        fullscreen=True,
        modal_class_name="inter",
    ),
    dbc.Modal(
        children=modal_performance.layout,
        id="modal_perf",
        size="xl",
        scrollable=True,
        fullscreen=True,
        modal_class_name="inter",
    ),
    dbc.Modal(
        children=modal_repair.layout,
        id="modal_repair",
        size="xl",
        scrollable=True,
        fullscreen=True,
        modal_class_name="inter",
    ),
]

# ========================================= Callbacks ========================================= #


# ------------------------- Modal ------------------------- #
@callback(
    Output("modal_eff", "is_open"),
    Input("efficiency-button", "n_clicks"),
    State("modal_eff", "is_open"),
)
def open_efficiency_modal(n, is_open):
    """
    Opens or closes the efficiency modal based on the value of n.

    Parameters:
    - n (bool): Determines whether to open or close the efficiency modal.
    - is_open (bool): Current state of the efficiency modal.

    Returns:
    - bool: Updated state of the efficiency modal.
    """
    if n:
        return not is_open
    return is_open


@callback(
    Output("modal_perf", "is_open"),
    Input("performance-button", "n_clicks"),
    State("modal_perf", "is_open"),
)
def open_performance_modal(n, is_open):
    """
    Abre ou fecha o modal de desempenho.

    Args:
        n (bool): Indica se o modal deve ser aberto.
        is_open (bool): Indica se o modal está aberto.

    Returns:
        bool: Indica se o modal foi aberto ou fechado.
    """
    if n:
        return not is_open
    return is_open


@callback(
    Output("modal_repair", "is_open"),
    Input("repair-button", "n_clicks"),
    State("modal_repair", "is_open"),
)
def open_repair_modal(n, is_open):
    """
    Opens or closes the repair modal based on the value of `n`.

    Args:
        n (bool): Indicates whether to open or close the repair modal.
        is_open (bool): Current state of the repair modal.

    Returns:
        bool: Updated state of the repair modal.
    """
    if n:
        return not is_open
    return is_open


# ------------------------- Main Page ------------------------- #


# ---------- Gauges Actual ---------- #
@callback(
    [
        Output(f"actual-gauge-{IndicatorType.EFFICIENCY.value}", "children"),
        Output(f"actual-gauge-{IndicatorType.PERFORMANCE.value}", "children"),
        Output(f"actual-gauge-{IndicatorType.REPAIR.value}", "children"),
    ],
    [
        Input("store-df-eff", "data"),
        Input("store-df-perf", "data"),
        Input("store-df-repair", "data"),
        Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    ],
)
def update_actual_gauge(df_1, df_2, df_3, toggle_theme):
    """
    Update the actual gauge with the given dataframes and toggle theme.

    Args:
        df_1 (str): JSON string representing the first dataframe.
        df_2 (str): JSON string representing the second dataframe.
        df_3 (str): JSON string representing the third dataframe.
        toggle_theme (bool): Flag indicating whether to use the light or dark template.

    Returns:
        tuple: A tuple containing three gauges created using the given dataframes and template.
    """
    if df_1 is None:
        raise PreventUpdate
    gg = gauge.Gauge()
    template = TemplateType.LIGHT if toggle_theme else TemplateType.DARK

    df_eff = pd.read_json(StringIO(df_1), orient="split")
    df_perf = pd.read_json(StringIO(df_2), orient="split")
    df_repair = pd.read_json(StringIO(df_3), orient="split")

    return (
        gg.create_gauge(df_eff, IndicatorType.EFFICIENCY, 90, template),
        gg.create_gauge(df_perf, IndicatorType.PERFORMANCE, 4, template),
        gg.create_gauge(df_repair, IndicatorType.REPAIR, 4, template),
    )


# ---------- Gauges Last ---------- #
@callback(
    [
        Output(f"last-gauge-{IndicatorType.EFFICIENCY.value}", "children"),
        Output(f"last-gauge-{IndicatorType.PERFORMANCE.value}", "children"),
        Output(f"last-gauge-{IndicatorType.REPAIR.value}", "children"),
    ],
    [
        Input("store-df-eff", "data"),
        Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    ],
)
def update_last_gauge(df_1, toggle_theme):
    """
    Update the last gauge values based on the given data frame and theme toggle.

    Args:
        df_1 (pandas.DataFrame): The data frame containing the gauge values.
        toggle_theme (bool): A boolean indicating whether the theme is toggled.

    Returns:
        tuple: A tuple containing the updated gauge values for efficiency, performance, and repair.

    Raises:
        PreventUpdate: If the given data frame is None.

    """
    if df_1 is None:
        raise PreventUpdate

    gg = gauge.Gauge()
    last_month = LastMonthInd()
    template = TemplateType.LIGHT if toggle_theme else TemplateType.DARK

    df_last_month, _ = last_month.get_historic_data()

    return (
        gg.create_gauge(df_last_month, IndicatorType.EFFICIENCY, 90, template, this_month=False),
        gg.create_gauge(df_last_month, IndicatorType.PERFORMANCE, 4, template, this_month=False),
        gg.create_gauge(df_last_month, IndicatorType.REPAIR, 4, template, this_month=False),
    )


# ---------- Heatmap ---------- #
@callback(
    [
        Output(f"heatmap-{IndicatorType.EFFICIENCY.value}", "children"),
        Output(f"heatmap-{IndicatorType.PERFORMANCE.value}", "children"),
        Output(f"heatmap-{IndicatorType.REPAIR.value}", "children"),
    ],
    [
        Input("store-df_eff_heatmap_tuple", "data"),
        Input("store-df_perf_heatmap_tuple", "data"),
        Input("store-df_repair_heatmap_tuple", "data"),
        Input("store-annotations_eff_list_tuple", "data"),
        Input("store-annotations_perf_list_tuple", "data"),
        Input("store-annotations_repair_list_tuple", "data"),
        Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    ],
)
def update_heatmap(
    df_eff, df_perf, df_repair, annotations_eff, annotations_perf, annotations_repair, toggle_theme
):
    """
    Update the heatmap based on the provided data and annotations.

    Args:
        df_eff (str): JSON string representing the efficiency data.
        df_perf (str): JSON string representing the performance data.
        df_repair (str): JSON string representing the repair data.
        annotations_eff (str): JSON string representing the annotations for efficiency data.
        annotations_perf (str): JSON string representing the annotations for performance data.
        annotations_repair (str): JSON string representing the annotations for repair data.
        toggle_theme (bool): Flag indicating whether to use a light or dark template.

    Returns:
        None
    """

    if df_eff is None or df_perf is None or df_repair is None:
        raise PreventUpdate

    template = TemplateType.LIGHT if toggle_theme else TemplateType.DARK

    df_eff_json = json.loads(df_eff)
    df_perf_json = json.loads(df_perf)
    df_repair_json = json.loads(df_repair)

    annotations_eff_json = json.loads(annotations_eff)
    annotations_perf_json = json.loads(annotations_perf)
    annotations_repair_json = json.loads(annotations_repair)

    df_eff_heat = [pd.read_json(StringIO(df), orient="split") for df in df_eff_json]
    df_perf_heat = [pd.read_json(StringIO(df), orient="split") for df in df_perf_json]
    df_repair_heat = [pd.read_json(StringIO(df), orient="split") for df in df_repair_json]

    annotations_eff_heat = [json.loads(annotations) for annotations in annotations_eff_json]
    annotations_perf_heat = [json.loads(annotations) for annotations in annotations_perf_json]
    annotations_repair_heat = [json.loads(annotations) for annotations in annotations_repair_json]

    hm = heatmap.Heatmap()

    heatmap_eff = hm.create_heatmap(
        df_eff_heat[-1], annotations_eff_heat[-1], IndicatorType.EFFICIENCY, 90, template
    )
    heatmap_perf = hm.create_heatmap(
        df_perf_heat[-1], annotations_perf_heat[-1], IndicatorType.PERFORMANCE, 4, template
    )
    heatmap_repair = hm.create_heatmap(
        df_repair_heat[-1], annotations_repair_heat[-1], IndicatorType.REPAIR, 4, template
    )

    return (
        dbc.Button(
            class_name="w-100 p-0 bg-transparent border-0",
            id="efficiency-button",
            children=heatmap_eff,
        ),
        dbc.Button(
            class_name="w-100 p-0 bg-transparent border-0",
            id="performance-button",
            children=heatmap_perf,
        ),
        dbc.Button(
            class_name="w-100 p-0 bg-transparent border-0",
            id="repair-button",
            children=heatmap_repair,
        ),
    )


# ---------- Line Chart ---------- #


@callback(
    [
        Output(f"line-chart-{IndicatorType.EFFICIENCY.value}", "children"),
        Output(f"line-chart-{IndicatorType.PERFORMANCE.value}", "children"),
        Output(f"line-chart-{IndicatorType.REPAIR.value}", "children"),
    ],
    [
        Input("store-df-eff", "data"),
        Input("store-df-perf", "data"),
        Input("store-df-repair", "data"),
        Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    ],
)
def update_line_chart(df_1, df_2, df_3, toggle_theme):
    """
    Update the line chart with the given dataframes and theme.

    Args:
        df_1 (str): The first dataframe in JSON format.
        df_2 (str): The second dataframe in JSON format.
        df_3 (str): The third dataframe in JSON format.
        toggle_theme (bool): A boolean indicating whether to toggle the theme.

    Returns:
        tuple: A tuple containing three line graphs created from the dataframes.
    """
    if df_1 is None:
        raise PreventUpdate

    lg = line_graph.LineGraph()

    template = TemplateType.LIGHT if toggle_theme else TemplateType.DARK

    df_eff = pd.read_json(StringIO(df_1), orient="split")
    df_perf = pd.read_json(StringIO(df_2), orient="split")
    df_repair = pd.read_json(StringIO(df_3), orient="split")

    return (
        lg.create_line_graph(df_eff, IndicatorType.EFFICIENCY, 90, template),
        lg.create_line_graph(df_perf, IndicatorType.PERFORMANCE, 4, template),
        lg.create_line_graph(df_repair, IndicatorType.REPAIR, 4, template),
    )
