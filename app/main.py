"""
    Autor: Bruno Tomaz
    Data: 15/01/2024
    Este módulo é o responsável por iniciar a aplicação Dash.
    A aplicação Dash é uma aplicação web que permite a criação de dashboards interativos.
    A aplicação Dash é baseada em Flask e React.
    Para mais informações, acesse: https://dash.plotly.com/
"""


# cSpell: words apscheduler,
from threading import Lock

import dash_bootstrap_components as dbc
from apscheduler.schedulers.background import BackgroundScheduler
from dash import callback, dcc, html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

# pylint: disable=E0401
from graphics.last_month_ind import LastMonthInd
from helpers.cache import cache, update_cache
from pages import main_page

from app import app

# from dash_bootstrap_templates import ThemeChangerAIO


lock = Lock()
last_month_ind = LastMonthInd()


# ========================================= Background ========================================= #


def update_last_month_gauge():
    """
    Função que salva imagens de gauge do mês anterior.
    """
    with lock:
        last_month_ind.get_last_month_ind()


scheduler = BackgroundScheduler()
scheduler.add_job(func=update_cache, trigger="interval", seconds=120)  # Atualiza a cada 2 minutos
scheduler.add_job(func=update_last_month_gauge, trigger="cron", hour=1)  # Atualiza a cada 24 horas
scheduler.start()


# ========================================= Layout ========================================= #
content = html.Div(id="page-content")

app.layout = dbc.Container(
    children=[
        # ---------------------- Store ---------------------- #
        dcc.Store(id="store-info"),
        dcc.Store(id="store-prod"),
        dcc.Store(id="store-df-eff"),
        dcc.Store(id="store-df-perf"),
        dcc.Store(id="store-df-repair"),
        dcc.Store(id="store-df-eff-heatmap"),
        dcc.Store(id="store-df-eff-heatmap-tuple"),
        dcc.Store(id="store-annotations_eff_turn_list_tuple"),
        dcc.Store(id="store-df-perf_repair_heat_tuple"),
        dcc.Store(id="store-annotations_list_tuple"),
        dcc.Store(id="store-df_perf_heat_turn_tuple"),
        dcc.Store(id="store-df-repair_heat_turn_tuple"),
        dcc.Store(id="store-annotations_perf_turn_list_tuple"),
        dcc.Store(id="store-annotations_repair_turn_list_tuple"),
        dcc.Store(id="is-data-store", storage_type="session", data=False),
        # ---------------------- Main Layout ---------------------- #
        html.H1("Shop Floor Management", className="text-center"),
        html.Hr(),
        # dbc.Nav(
        #    ThemeChangerAIO(aio_id="theme", radio_props={"value": dbc.themes.BOOTSTRAP}),
        # ),
        dbc.Row(
            main_page.layout,
        ),
    ],
    fluid=True,
    style={"width": "100%"},
    className="dbc dbc-ag-grid",
)


# ========================================= Callbacks ========================================= #
@callback(
    [
        Output("store-info", "data"),
        Output("store-prod", "data"),
        Output("store-df-eff", "data"),
        Output("store-df-perf", "data"),
        Output("store-df-repair", "data"),
        Output("store-df-eff-heatmap", "data"),
        Output("store-df-eff-heatmap-tuple", "data"),
        Output("store-annotations_eff_turn_list_tuple", "data"),
        Output("store-df-perf_repair_heat_tuple", "data"),
        Output("store-annotations_list_tuple", "data"),
        Output("store-df_perf_heat_turn_tuple", "data"),
        Output("store-df-repair_heat_turn_tuple", "data"),
        Output("store-annotations_perf_turn_list_tuple", "data"),
        Output("store-annotations_repair_turn_list_tuple", "data"),
    ],
    Input("store-info", "data"),
)
def update_store(_data):
    """
    Função que atualiza o store com os dados do banco de dados.
    Utiliza dados do cache para agilizar o carregamento.
    """
    if cache.get("df1") is None or cache.get("df2") is None:
        raise PreventUpdate

    df_maq_info_cadastro = cache.get("df1")
    df_maq_info_prod_cad = cache.get("df2")
    df_eff = cache.get("df_eff")
    df_perf = cache.get("df_perf")
    df_repair = cache.get("df_repair")
    df_eff_heatmap = cache.get("df_eff_heatmap")
    df_eff_heatmap_tuple = cache.get("df_eff_heatmap_tuple")
    annotations_eff_turn_list_tuple = cache.get("annotations_eff_turn_list_tuple")
    df_perf_repair_heat_tuple = cache.get("df_perf_repair_heat_tuple")
    annotations_list_tuple = cache.get("annotations_list_tuple")
    df_perf_heat_turn_tuple = cache.get("df_perf_heat_turn_tuple")
    df_repair_heat_turn_tuple = cache.get("df_repair_heat_turn_tuple")
    annotations_perf_turn_list_tuple = cache.get("annotations_perf_turn_list_tuple")
    annotations_repair_turn_list_tuple = cache.get("annotations_repair_turn_list_tuple")

    print("========== Store atualizado ==========")
    return (
        df_maq_info_cadastro,
        df_maq_info_prod_cad,
        df_eff,
        df_perf,
        df_repair,
        df_eff_heatmap,
        df_eff_heatmap_tuple,
        annotations_eff_turn_list_tuple,
        df_perf_repair_heat_tuple,
        annotations_list_tuple,
        df_perf_heat_turn_tuple,
        df_repair_heat_turn_tuple,
        annotations_perf_turn_list_tuple,
        annotations_repair_turn_list_tuple,
    )


@callback(
    Output("is-data-store", "data"),
    [
        Input("store-info", "data"),
        Input("store-prod", "data"),
    ],
)
def update_is_data_store(data_info, data_prod):
    """
    Função que atualiza o store com os dados do banco de dados.
    Utiliza dados do cache para agilizar o carregamento.
    """
    if data_info is None or data_prod is None:
        return False

    return True


# ======================================== Run App ======================================== #
if __name__ == "__main__":
    app.run_server(debug=True, port=8050, host="0.0.0.0")
