"""
    Autor: Bruno Tomaz
    Data: 15/01/2024
    Este módulo é o responsável por iniciar a aplicação Dash.
    A aplicação Dash é uma aplicação web que permite a criação de dashboards interativos.
    A aplicação Dash é baseada em Flask e React.
    Para mais informações, acesse: https://dash.plotly.com/
"""

import json

# cSpell: words apscheduler,
from threading import Lock

import dash_bootstrap_components as dbc
import numpy as np
from apscheduler.schedulers.background import BackgroundScheduler
from dash import callback, dcc, html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

# pylint: disable=E0401
from database.get_data import GetData
from flask_caching import Cache
from graphics.last_month_ind import LastMonthInd
from pages import main_page
from service.df_for_indicators import DFIndicators

from app import app

# from dash_bootstrap_templates import ThemeChangerAIO


class MyEncoder(json.JSONEncoder):
    """
    Classe que codifica objetos para JSON.
    """

    def default(self, o):
        if isinstance(o, np.int64) or isinstance(o, np.int32):
            return int(o)
        return super(MyEncoder, self).default(o)


lock = Lock()
get_data = GetData()
last_month_ind = LastMonthInd()


# ========================================= Cache ========================================= #

cache = Cache(
    app.server,
    config={
        "CACHE_TYPE": "filesystem",
        "CACHE_DIR": "cache-directory",
        "CACHE_THRESHOLD": 50,
    },
)


def update_cache():
    """
    Função que atualiza o cache com os dados do banco de dados.
    Agiliza o carregamento dos dados na aplicação.
    """
    with lock:
        df1, df2 = get_data.get_cleaned_data()
        df_ind = DFIndicators(df1, df2)
        df_eff = df_ind.get_eff_data()
        df_eff_heatmap = df_ind.get_eff_data_heatmap()
        df_eff_heatmap_tuple = df_ind.get_eff_data_heatmap_turn()
        annotations_list_tuple = df_ind.get_eff_annotations_turn()

        cache.set("df1", df1.to_json(date_format="iso", orient="split"))
        cache.set("df2", df2.to_json(date_format="iso", orient="split"))
        cache.set("df_eff", df_eff.to_json(date_format="iso", orient="split"))
        cache.set("df_eff_heatmap", df_eff_heatmap.to_json(date_format="iso", orient="split"))
        cache.set(
            "df_eff_heatmap_tuple",
            json.dumps(
                [df.to_json(date_format="iso", orient="split") for df in df_eff_heatmap_tuple]
            ),
        )
        cache.set(
            "annotations_list_tuple",
            json.dumps([json.dumps(lst, cls=MyEncoder) for lst in annotations_list_tuple]),
        )


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

# dbc.Nav(
#    ThemeChangerAIO(aio_id="theme", radio_props={"value": dbc.themes.BOOTSTRAP}),
# ),

# ========================================= Layout ========================================= #
content = html.Div(id="page-content")

app.layout = dbc.Container(
    children=[
        dcc.Store(id="store-info"),
        dcc.Store(id="store-prod"),
        dcc.Store(id="store-df-eff"),
        dcc.Store(id="store-df-eff-heatmap"),
        dcc.Store(id="store-df-eff-heatmap-tuple"),
        dcc.Store(id="store-df-eff-annotations-tuple"),
        dcc.Store(id="is-data-store", storage_type="session", data=False),
        html.H1("Shop Floor Management", className="text-center"),
        html.Hr(),
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
        Output("store-df-eff-heatmap", "data"),
        Output("store-df-eff-heatmap-tuple", "data"),
        Output("store-df-eff-annotations-tuple", "data"),
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
    df_eff_heatmap = cache.get("df_eff_heatmap")
    df_eff_heatmap_tuple = cache.get("df_eff_heatmap_tuple")
    annotations_list_tuple = cache.get("annotations_list_tuple")

    print("========== Store atualizado ==========")
    return (
        df_maq_info_cadastro,
        df_maq_info_prod_cad,
        df_eff,
        df_eff_heatmap,
        df_eff_heatmap_tuple,
        annotations_list_tuple,
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
