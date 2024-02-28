"""
    Página Principal do dashboard
    @autor: Bruno Tomaz
    @data: 15/01/2024
"""

# cSpell: words eficiencia fullscreen

from io import StringIO

import dash_bootstrap_components as dbc
import pandas as pd
from components import gauge, modal_efficiency, modal_performance, modal_repair
from dash import Input, Output, State, callback, html
from dash.exceptions import PreventUpdate
from dash_bootstrap_templates import ThemeSwitchAIO
from helpers.types import IndicatorType, TemplateType

# ======================================== Layout ======================================== #

layout = dbc.Row(
    [
        dbc.Spinner(
            id="main-page-spinner",
            color="primary",
            size="lg",
            children=[
                dbc.Row(
                    [
                        dbc.Col(
                            id=f"last-gauge-{IndicatorType.EFFICIENCY.value}",
                            sm={"size": 4, "offset": 1, "order": 1},
                            md={"size": 2, "order": 1},
                            xxl={"size": 1, "order": 1},
                            class_name="p-1",
                        ),
                        dbc.Col(
                            id=f"heatmap-line-{IndicatorType.EFFICIENCY.value}",
                            sm={"size": 12, "offset": 1, "order": 1},
                            md={"size": 8, "order": 2},
                            xxl={"size": 10, "order": 2},
                            class_name="p-1",
                        ),
                        dbc.Col(
                            id=f"actual-gauge-{IndicatorType.EFFICIENCY.value}",
                            sm={"size": 4, "offset": 2, "order": 2},
                            md={"size": 2, "order": 3},
                            xxl={"size": 1, "order": 3},
                            class_name="p-1",
                        ),
                    ]
                ),
                html.Hr(),
                dbc.Row(
                    [
                        dbc.Col(
                            id=f"last-gauge-{IndicatorType.PERFORMANCE.value}",
                            sm={"size": 4, "offset": 1, "order": 1},
                            md={"size": 2, "order": 1},
                            xxl={"size": 1, "order": 1},
                            class_name="p-1",
                        ),
                        dbc.Col(
                            id=f"heatmap-line-{IndicatorType.PERFORMANCE.value}",
                            sm={"size": 12, "offset": 1, "order": 1},
                            md={"size": 8, "order": 2},
                            xxl={"size": 10, "order": 2},
                            class_name="p-1",
                        ),
                        dbc.Col(
                            id=f"actual-gauge-{IndicatorType.PERFORMANCE.value}",
                            sm={"size": 4, "offset": 2, "order": 2},
                            md={"size": 2, "order": 3},
                            xxl={"size": 1, "order": 3},
                            class_name="p-1",
                        ),
                    ]
                ),
                html.Hr(),
                dbc.Row(
                    [
                        dbc.Col(
                            id=f"last-gauge-{IndicatorType.REPAIR.value}",
                            sm={"size": 4, "offset": 1, "order": 1},
                            md={"size": 2, "order": 1},
                            xxl={"size": 1, "order": 1},
                            class_name="p-1",
                        ),
                        dbc.Col(
                            id=f"heatmap-line-{IndicatorType.REPAIR.value}",
                            sm={"size": 12, "offset": 1, "order": 1},
                            md={"size": 8, "order": 2},
                            xxl={"size": 10, "order": 2},
                            class_name="p-1",
                        ),
                        dbc.Col(
                            id=f"actual-gauge-{IndicatorType.REPAIR.value}",
                            sm={"size": 4, "offset": 2, "order": 2},
                            md={"size": 2, "order": 3},
                            xxl={"size": 1, "order": 3},
                            class_name="p-1",
                        ),
                    ]
                ),
            ],
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
)

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
