"""
Modal Module Efficiency
Criado por: Bruno Tomaz
Data: 23/01/2024
"""

import json
from io import StringIO

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
from components import (
    bar_chart_general,
    bar_chart_lost,
    btn_modal,
    grid_occ,
    heatmap,
    line_graph,
    production_grid,
)
from dash import Input, Output, callback, html
from dash.exceptions import PreventUpdate
from dash_bootstrap_templates import ThemeSwitchAIO
from helpers.my_types import IndicatorType, TemplateType

from app import app

# ======================================== Modal Layout ======================================== #

layout = [
    dbc.ModalHeader("Eficiência por Turno", class_name="inter"),
    dbc.ModalBody(
        [
            dbc.Row(
                id="buttons",
                children=[
                    dbc.Col(
                        btn_modal.radio_btn_eff,
                        class_name="radio-group",
                        md=4,
                        lg=5,
                        xl=4,
                        xxl=3,
                    ),
                    dbc.Col(
                        btn_modal.btn_opt_eff,
                        md={"offset": 2},
                        lg={"offset": 0},
                    ),
                ],
            ),
            dbc.Spinner(id="heatmap-line-spinner"),
            html.Hr(),
            dbc.Collapse(id="production-collapse-eff", class_name="mb-3"),
            dbc.Row(
                [
                    dbc.Col(dbc.Card(id="eff-general", class_name="p-1"), md=6),
                    dbc.Col(dbc.Card(id="eff-lost", class_name="p-1"), md=6),
                ],
                class_name="mb-3",
            ),
            dbc.Row(id="grid-occ-modal-eff"),
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

# ======================================= Modal Callbacks ======================================= #


# --------------------- Spinner --------------------- #
@callback(
    Output("heatmap-line-spinner", "children"),
    [
        Input(f"radio-items-{IndicatorType.EFFICIENCY.value}", "value"),
        Input("store-df_eff_heatmap_tuple", "data"),
        Input("store-annotations_eff_list_tuple", "data"),
        Input("store-df-eff", "data"),
        Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    ],
)
def spinner_efficiency(turn, df_heatmap, annotations, df_eff, toggle_theme):
    """
    Generates a card containing a heatmap and a line graph based on the provided data.

    Args:
        turn (str): The selected turn ('NOT', 'MAT', 'VES', 'TOT').
        df_heatmap (str): The JSON string representing the heatmap data.
        annotations (str): The JSON string representing the annotations data.
        df_eff (str): The JSON string representing the line graph data.
        toggle_theme (bool): A flag indicating whether to use a light or dark template.

    Returns:
        dbc.Card: A Bootstrap Card component containing the heatmap and line graph.
    """

    if not df_heatmap or not df_eff:
        raise PreventUpdate

    template = TemplateType.LIGHT if toggle_theme else TemplateType.DARK
    hm = heatmap.Heatmap()
    lg = line_graph.LineGraph()

    # ---------Heatmap--------- #
    # Carrega o string json em uma lista
    list_heat_json = json.loads(df_heatmap)
    list_ann_json = json.loads(annotations)

    # Converte o string json em um dataframe e um dicionário
    df_tuple = [pd.read_json(StringIO(x), orient="split") for x in list_heat_json]
    ann_tuple = [json.loads(x) for x in list_ann_json]

    # Converte em tuplas e desempacota
    noturno, matutino, vespertino, total, _ = tuple(df_tuple)
    ann_noturno, ann_matutino, ann_vespertino, ann_total, _ = tuple(ann_tuple)

    # Cria um dicionário com os dataframes e as anotações
    efficiency_heatmap_dict = {
        "NOT": (noturno, ann_noturno),
        "MAT": (matutino, ann_matutino),
        "VES": (vespertino, ann_vespertino),
        "TOT": (total, ann_total),
    }

    # Seleciona o dataframe e as anotações com base no turno
    df_heatmap, annotations = efficiency_heatmap_dict[turn]

    # ---------Line--------- #
    # Carrega o string json em um dataframe
    df_line = pd.read_json(StringIO(df_eff), orient="split")

    # Se df_line não tiver o turn na coluna turno, previne a atualização
    if turn not in df_line["turno"].unique():
        raise PreventUpdate

    return dbc.Card(
        [
            hm.create_heatmap(
                df_heatmap, annotations, IndicatorType.EFFICIENCY, 90, template, turn
            ),
            lg.create_line_graph(df_line, IndicatorType.EFFICIENCY, 90, template, turn),
        ],
        class_name="p-1",
    )


# --------------------- Production Collapse --------------------- #
# ------- Toggle Collapse ------- #
@callback(
    [
        Output("production-collapse-eff", "is_open"),
        Output(f"production-btn-{IndicatorType.EFFICIENCY.value}", "active"),
    ],
    [
        Input(f"production-btn-{IndicatorType.EFFICIENCY.value}", "n_clicks"),
        Input("production-collapse-eff", "is_open"),
    ],
)
def toggle_collapse(n_clicks, is_open):
    """
    Toggles the collapse of the production collapse.

    Args:
        n_clicks (int): The number of clicks on the production button.
        is_open (bool): The current state of the collapse.

    Returns:
        bool: The new state of the collapse.
    """
    if n_clicks:
        return not is_open, not is_open
    return is_open, is_open


# -------- Collapse Content -------- #
@callback(
    Output("production-collapse-eff", "children"),
    [
        Input("store-info", "data"),
        Input("store-prod", "data"),
        Input(f"radio-items-{IndicatorType.EFFICIENCY.value}", "value"),
        Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    ],
)
def collapse_content(info, prod, turn, toggle_theme):
    """
    Creates a collapsible content card for production information.

    Args:
        info (str): JSON string containing machine information.
        prod (str): JSON string containing production data.

    Returns:
        dbc.Card: Collapsible content card displaying production information.
    """
    if not info or not prod:
        raise PreventUpdate

    pgd = production_grid.ProductionGrid()

    maq_prod = pd.read_json(StringIO(prod), orient="split")

    df_prod = pd.DataFrame(maq_prod)

    turno = {
        "NOT": "Produção do Noturno",
        "MAT": "Produção do Matutino",
        "VES": "Produção do Vespertino",
        "TOT": "Produção Total",
    }

    # ------------- Grid ------------- #

    return dbc.Card(
        [
            dbc.CardHeader("Produção"),
            dbc.CardBody(
                [
                    html.H5(f"Tabela de {turno[turn]}", className="text-center"),
                    dbc.Row(pgd.create_production_grid(df_prod, turn, toggle_theme)),
                ]
            ),
        ],
        class_name="mb-3",
    )


# --------------------- Efficiency General --------------------- #
@callback(
    Output("eff-general", "children"),
    [
        Input("store-df-eff", "data"),
        Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    ],
)
def efficiency_general(df_eff, toggle_theme):
    """
    Calculates and returns a bar chart representing the efficiency of a process.

    Args:
        df_eff (str): A JSON string representing the efficiency data.
        toggle_theme (bool):
        A boolean indicating whether to use a light or dark template for the chart.

    Returns:
        dict: A dictionary representing the generated bar chart.

    Raises:
        PreventUpdate: If the `df_eff` parameter is empty or None.

    """
    if not df_eff:
        raise PreventUpdate

    template = TemplateType.LIGHT if toggle_theme else TemplateType.DARK
    bcg = bar_chart_general.BarChartGeneral()

    # Carrega o string json em um dataframe
    df = pd.read_json(StringIO(df_eff), orient="split")

    return bcg.create_bar_chart_gen(df, IndicatorType.EFFICIENCY, template, 90)


# --------------------- Efficiency Lost --------------------- #
@callback(
    Output("eff-lost", "children"),
    [
        Input("store-info", "data"),
        Input("store-prod", "data"),
        Input(f"radio-items-{IndicatorType.EFFICIENCY.value}", "value"),
        Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    ],
)
def efficiency_lost(info, prod, turn, toggle_theme):
    """
    Calculates the efficiency lost based on the provided information.

    Args:
        info (str): A JSON string containing the information.
        turn (int): The turn number.
        toggle_theme (bool): A flag indicating whether to use a light or dark template.

    Returns:
        dict: A dictionary containing the bar chart lost data.

    Raises:
        PreventUpdate: If the info parameter is empty.
    """

    if not info:
        raise PreventUpdate

    template = TemplateType.LIGHT if toggle_theme else TemplateType.DARK

    # Carrega o string json em um dataframe
    df_info = pd.read_json(StringIO(info), orient="split")
    df_prod = pd.read_json(StringIO(prod), orient="split")

    bcl = bar_chart_lost.BarChartLost(df_info, df_prod)

    return bcl.create_bar_chart_lost(df_info, IndicatorType.EFFICIENCY, template, turn)


# ________________________ Collapse Details Content ________________________ #


# ---------------------- Grid ---------------------- #
@callback(
    Output("grid-occ-modal-eff", "children"),
    [
        Input("store-info", "data"),
        Input("store-prod", "data"),
        Input(f"radio-items-{IndicatorType.EFFICIENCY.value}", "value"),
        Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    ],
)
def update_grid_occ_modal(info, prod, turn, theme):
    """
    Função que atualiza o grid de eficiência do modal.
    """
    if info is None:
        raise PreventUpdate

    # Carregue a string JSON em um DataFrame
    df_info = pd.read_json(StringIO(info), orient="split")
    df_prod = pd.read_json(StringIO(prod), orient="split")

    goe = grid_occ.GridOcc(df_info, df_prod)

    turns = {
        "NOT": "Noturno",
        "MAT": "Matutino",
        "VES": "Vespertino",
        "TOT": "Geral",
    }

    return [
        html.H5(f"Ocorrências - {turns[turn]}", className="text-center"),
        goe.create_grid_occ(df_info, IndicatorType.EFFICIENCY, turn, theme),
    ]
