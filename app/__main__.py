"""
    Este módulo é o responsável por iniciar a aplicação Dash.
    A aplicação Dash é uma aplicação web que permite a criação de dashboards interativos.
    A aplicação Dash é baseada em Flask e React.
    Para mais informações, acesse: https://dash.plotly.com/
"""
from threading import Lock

import dash_bootstrap_components as dbc
from apscheduler.schedulers.background import BackgroundScheduler
from dash import callback, dcc, html
from dash.dependencies import Input, Output

# pylint: disable=E0401
from database import get_data
from flask_caching import Cache
from pages import main_page

from app import app

# ========================================= Cache ========================================= #
lock = Lock()
cache = Cache(
    app.server,
    config={
        "CACHE_TYPE": "filesystem",
        "CACHE_DIR": "cache-directory",
        "CACHE_THRESHOLD": 200,
    },
)


# @cache.memoize(timeout=60)  # Cache por 1 hora
def get_df():
    data = get_data.GetData()
    df1, df2, df3 = data.get_data()
    return df1, df2, df3


def update_cache():
    with lock:
        df1, df2, df3 = get_df()
        cache.set("df1", df1.to_json(date_format="iso", orient="split"))
        cache.set("df2", df2.to_json(date_format="iso", orient="split"))
        cache.set("df3", df3.to_json(date_format="iso", orient="split"))


scheduler = BackgroundScheduler()
scheduler.add_job(func=update_cache, trigger="interval", seconds=60)
scheduler.start()


# ========================================= Layout ========================================= #
content = html.Div(id="page-content")

app.layout = dbc.Container(
    children=[
        dcc.Store(id="store-info"),
        dcc.Store(id="store-occ"),
        dcc.Store(id="store-cadastro"),
        html.H1("Shop Floor Management", className="text-center"),
        html.Hr(),
        dbc.Row(
            main_page.layout,
        ),
    ],
    fluid=True,
    style={"padding": "5px"},
    className="dbc",
)


@callback(
    [
        Output("store-info", "data"),
        Output("store-occ", "data"),
        Output("store-cadastro", "data"),
    ],
    Input("store-info", "data"),
)
def update_store(_data):
    print("Updating store...")
    df1 = cache.get("df1")
    df2 = cache.get("df2")
    df3 = cache.get("df3")

    return df1, df2, df3


# ======================================== Run App ======================================== #
if __name__ == "__main__":
    app.run_server(debug=True, port=8050, host="0.0.0.0")
