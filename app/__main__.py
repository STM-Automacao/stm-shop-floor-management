"""
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
from database.get_data import GetData
from flask_caching import Cache
from pages import main_page

from app import app

lock = Lock()
get_data = GetData()

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

        cache.set("df1", df1.to_json(date_format="iso", orient="split"))
        cache.set("df2", df2.to_json(date_format="iso", orient="split"))


scheduler = BackgroundScheduler()
scheduler.add_job(
    func=update_cache, trigger="interval", seconds=120
)  # Atualiza a cada 2 minutos
scheduler.start()


# ========================================= Layout ========================================= #
content = html.Div(id="page-content")

app.layout = dbc.Container(
    children=[
        dcc.Store(id="store-info"),
        dcc.Store(id="store-prod"),
        html.H1("Shop Floor Management", className="text-center"),
        html.Hr(),
        dbc.Row(
            main_page.layout,
        ),
    ],
    fluid=True,
    style={"width": "100%"},
    className="dbc",
)


# ========================================= Callbacks ========================================= #
@callback(
    [
        Output("store-info", "data"),
        Output("store-prod", "data"),
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
    print("========== Atualizando store ==========")

    return df_maq_info_cadastro, df_maq_info_prod_cad


# ======================================== Run App ======================================== #
if __name__ == "__main__":
    app.run_server(debug=True, port=8050, host="0.0.0.0")
