"""
    Este modulo contém a página de gerenciamento de eficiência e ocorrências.
"""

from io import StringIO

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
from components import grid_aggrid
from dash import Input, Output, callback, html
from dash.exceptions import PreventUpdate
from dash_bootstrap_templates import ThemeSwitchAIO
from helpers.my_types import (
    GRID_FORMAT_NUMBER_BR,
    GRID_NUMBER_COLS,
    GRID_STR_NUM_COLS,
    IndicatorType,
)
from service.df_for_indicators import DFIndicators

# =========================================== Variáveis ========================================== #
gag = grid_aggrid.GridAgGrid()

# ================================================================================================ #
#                                              LAYOUT                                              #
# ================================================================================================ #
layout = dmc.Stack(
    [
        dmc.Card(
            [
                html.H3("Tabela de Eficiência", className="text-center mb-3"),
                dbc.Row(id="eficiencia-table-management"),
            ],
            shadow="sm",
        ),
        dmc.Card(
            [
                html.H3("Ocorrências da Produção", className="text-center mb-3"),
                dbc.Row(
                    id="grid-occ-modal",
                ),
            ],
            shadow="sm",
        ),
    ],
)


# ================================================================================================ #
#                                             CALLBACKS                                            #
# ================================================================================================ #


# ======================================= Eficiencia Table ======================================= #
@callback(
    Output("eficiencia-table-management", "children"),
    [
        Input("store-df-eff", "data"),
        Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    ],
)
def update_eficiencia_table(data, theme):
    """
    Função que atualiza a tabela de eficiência.
    """
    if data is None:
        raise PreventUpdate

    # Carregue a string JSON em um DataFrame
    df = pd.read_json(StringIO(data), orient="split")

    # Garantir que data registro é pd.datetime apenas com a data
    df.data_registro = pd.to_datetime(df.data_registro).dt.strftime("%d/%m")

    # Ajustar eficiência
    df.eficiencia = (df.eficiencia * 100).round(2)

    # Ajustar produção esperada para int
    df.producao_esperada = df.producao_esperada.astype(int)

    defs = [
        {"field": "fabrica", "headerName": "Fábrica", "maxWidth": 150, **GRID_NUMBER_COLS},
        {"field": "linha", "headerName": "Linha", "maxWidth": 150, **GRID_NUMBER_COLS},
        {"field": "maquina_id", "headerName": "Máquina"},
        {"field": "data_registro", "headerName": "Data", "maxWidth": 150},
        {"field": "turno", "headerName": "Turno", "maxWidth": 150},
        {"field": "tempo", "headerName": "Tempo Parada", **GRID_NUMBER_COLS},
        {"field": "desconto", "headerName": "Tempo Descontado", **GRID_NUMBER_COLS},
        {"field": "tempo_esperado", "headerName": "Tempo Esperado", **GRID_NUMBER_COLS},
        {
            "field": "producao_esperada",
            "headerName": "Deveria Produzir",
            **GRID_STR_NUM_COLS,
            **GRID_FORMAT_NUMBER_BR,
        },
        {
            "field": "total_produzido",
            "headerName": "Produzido",
            **GRID_STR_NUM_COLS,
            **GRID_FORMAT_NUMBER_BR,
        },
        {"field": "eficiencia", "headerName": "Eficiência %", **GRID_NUMBER_COLS},
    ]

    return gag.create_grid_ag(df, "eff-table-management", theme, defs)


# =================================== Details Of The Production ================================== #


# ---------------------- Grid ---------------------- #
@callback(
    Output("grid-occ-modal", "children"),
    [
        Input("store-info", "data"),
        Input("store-prod", "data"),
        Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    ],
)
def update_grid_occ_modal(info, prod, theme):
    """
    Função que atualiza o grid de eficiência do modal.
    """
    if info is None:
        raise PreventUpdate

    # Carregue a string JSON em um DataFrame
    df_info = pd.read_json(StringIO(info), orient="split")
    df_prod = pd.read_json(StringIO(prod), orient="split")

    # Ajustar os dados para a tabela
    df_info = DFIndicators(df_info, df_prod).adjust_df_for_bar_lost(
        df_info, IndicatorType.EFFICIENCY
    )

    # Ajustar data_registro para dd/mm
    df_info.data_registro = pd.to_datetime(df_info.data_registro).dt.strftime("%d/%m")

    # Ajustar data_hora para hh:mm
    df_info.data_hora = pd.to_datetime(df_info.data_hora).dt.strftime("%H:%M")
    df_info.data_hora_final = pd.to_datetime(df_info.data_hora_final).dt.strftime("%H:%M")

    defs = [
        {"field": "fabrica", "headerName": "Fábrica", "maxWidth": 150, **GRID_NUMBER_COLS},
        {"field": "linha", "headerName": "Linha", "maxWidth": 150, **GRID_NUMBER_COLS},
        {"field": "maquina_id", "headerName": "Máquina"},
        {"field": "data_registro", "headerName": "Data", "maxWidth": 150},
        {"field": "turno", "headerName": "Turno", "maxWidth": 150},
        {"field": "motivo", "headerName": "Motivo", "tooltipField": "motivo"},
        {"field": "equipamento", "headerName": "Equipamento", "tooltipField": "equipamento"},
        {"field": "problema", "headerName": "Problema", "tooltipField": "problema"},
        {"field": "causa", "headerName": "Causa", "tooltipField": "causa"},
        {"field": "s_backup", "headerName": "Saída p/ Linha", **GRID_NUMBER_COLS},
        {"field": "os_numero", "headerName": "Número OS", **GRID_STR_NUM_COLS},
        {"field": "operador_id", "headerName": "Operador", **GRID_STR_NUM_COLS},
        {"field": "tempo", "headerName": "Tempo Parada", **GRID_NUMBER_COLS},
        {"field": "excedente", "headerName": "Afeta Eficiência", **GRID_NUMBER_COLS},
        {"field": "desconto", "headerName": "Não afeta Eficiência", **GRID_NUMBER_COLS},
        {"field": "data_hora", "headerName": "Hora Início"},
        {"field": "data_hora_final", "headerName": "Hora Fim"},
    ]

    col_deft = {
        "wrapHeaderText": True,
        "autoHeight": True,
    }

    return gag.create_grid_ag(df_info, "grid-occ-modal", theme, defs, col_deft)
