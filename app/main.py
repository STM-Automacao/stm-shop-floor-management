"""
    Autor: Bruno Tomaz
    Data: 15/01/2024
    Este módulo é o responsável por iniciar a aplicação Dash.
    A aplicação Dash é uma aplicação web que permite a criação de dashboards interativos.
    A aplicação Dash é baseada em Flask e React.
    Para mais informações, acesse: https://dash.plotly.com/
"""

import os
from threading import Lock

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from apscheduler.schedulers.background import BackgroundScheduler
from dash import callback, dcc, html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from dash_bootstrap_templates import ThemeSwitchAIO

# pylint: disable=E0401
from database.last_month_ind import LastMonthInd
from helpers.cache import cache, cache_daily_data, update_cache
from pages import grafana, hour_prod, main_page, management
from service.big_data import BigData
from waitress import serve

from app import app

lock = Lock()
last_month_ind = LastMonthInd()

# Seleção de temas para o App - Variáveis:
URL_BOOTS = dbc.themes.BOOTSTRAP  # para o switch
URL_DARKY = dbc.themes.DARKLY

update_cache()

# ========================================= Background ========================================= #


def update_last_month():
    """
    Função que salva imagens de gauge do mês anterior.
    """
    with lock:
        last_month_ind.save_last_month_data()


def update_big_data():
    """
    Atualiza os dados grandes.

    Esta função chama o método save_big_data para salvar os dados grandes.

    Parâmetros:
        Nenhum.

    Retorno:
        Nenhum.
    """
    big_data = BigData()
    big_data.save_big_data()


scheduler = BackgroundScheduler()
scheduler.add_job(func=update_cache, trigger="interval", seconds=600)  # Atualiza a cada 10 minutos
scheduler.add_job(func=update_big_data, trigger="cron", hour=0)
scheduler.add_job(func=cache_daily_data, trigger="cron", hour=0, minute=1)
scheduler.add_job(func=update_last_month, trigger="cron", hour=1)  # Atualiza a cada 24 horas

scheduler.start()


# ========================================= Layout ========================================= #
content = html.Div(id="page-content")

app.layout = dmc.MantineProvider(
    forceColorScheme="light",
    id="mantine-provider",
    children=[
        dbc.Container(
            children=[
                # ---------------------- Store ---------------------- #
                dcc.Store(id="store-info"),
                dcc.Store(id="store-prod"),
                dcc.Store(id="store-df-eff"),
                dcc.Store(id="store-df-perf"),
                dcc.Store(id="store-df-repair"),
                dcc.Store(id="store-df_eff_heatmap_tuple"),
                dcc.Store(id="store-annotations_eff_list_tuple"),
                dcc.Store(id="store-df_perf_heatmap_tuple"),
                dcc.Store(id="store-annotations_perf_list_tuple"),
                dcc.Store(id="store-df_repair_heatmap_tuple"),
                dcc.Store(id="store-annotations_repair_list_tuple"),
                dcc.Store(id="store-df_working_time"),
                dcc.Store(id="store-df-caixas-cf"),
                dcc.Store(id="store-df-caixas-cf-tot"),
                dcc.Store(id="store-df-info-pure"),
                dcc.Store(id="is-data-store", storage_type="session", data=False),
                # ---------------------- Main Layout ---------------------- #
                dbc.Row(
                    dbc.Col(
                        ThemeSwitchAIO(
                            aio_id="theme",
                            themes=[URL_BOOTS, URL_DARKY],
                        ),
                        class_name="h-100 d-flex align-items-center justify-content-end",
                    ),
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            html.H1("Shop Floor Management", className="text-center"),
                        ),
                    ],
                ),
                html.Hr(),
                dbc.Row(
                    dbc.Tabs(
                        [
                            dbc.Tab(grafana.layout, label="Ao Vivo"),
                            dbc.Tab(main_page.layout, label="SFM Dashboard"),
                            dbc.Tab(management.layout, label="Gestão de Produção"),
                            dbc.Tab(hour_prod.layout, label="Produção por Hora"),
                        ],
                    ),
                    class_name="mb-5",
                ),
                dmc.AppShell(
                    zIndex=1000,
                    children=[
                        dmc.AppShellFooter(
                            children=[
                                dmc.Center(
                                    children=dmc.Image(
                                        # pylint: disable=E1101
                                        src=app.get_asset_url("Logo Horizontal.png"),
                                        w="125px",
                                    ),
                                    p=5,
                                ),
                            ],
                            id="footer",
                            className="bg-dark",
                        )
                    ],
                ),
            ],
            fluid=True,
            style={"width": "100%"},
            className="dbc dbc-ag-grid",
        ),
    ],
)


# ========================================= Callbacks ========================================= #
@callback(
    Output("footer", "className"),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
)
def update_footer_class_name(light_theme):
    """
    Atualiza o nome da classe do rodapé com base no tema de cores.

    Parâmetros:
    light_theme (bool): Indica se o tema de cores é claro ou escuro.

    Retorna:
    str: O nome da classe do rodapé atualizado.
    """
    return "bg-dark" if not light_theme else "bg-light"


@callback(
    Output("mantine-provider", "forceColorScheme"),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
)
def update_mantine_color_schema(light_theme):
    """
    Atualiza o mantine provider com base no tema de cores.

    Parâmetros:
    light_theme (bool): Indica se o tema de cores é claro ou escuro.

    Retorna:
    str: O nome da classe do rodapé atualizado.
    """
    return "dark" if not light_theme else "light"


@callback(
    [
        Output("store-info", "data"),
        Output("store-prod", "data"),
        Output("store-df-eff", "data"),
        Output("store-df-perf", "data"),
        Output("store-df-repair", "data"),
        Output("store-df_eff_heatmap_tuple", "data"),
        Output("store-annotations_eff_list_tuple", "data"),
        Output("store-df_perf_heatmap_tuple", "data"),
        Output("store-annotations_perf_list_tuple", "data"),
        Output("store-df_repair_heatmap_tuple", "data"),
        Output("store-annotations_repair_list_tuple", "data"),
        Output("store-df_working_time", "data"),
        Output("store-df-caixas-cf", "data"),
        Output("store-df-caixas-cf-tot", "data"),
        Output("store-df-info-pure", "data"),
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
    df_eff_heatmap_tuple = cache.get("df_eff_heatmap_tuple")
    annotations_eff_turn_list_tuple = cache.get("annotations_eff_list_tuple")
    df_perf_heatmap_tuple = cache.get("df_perf_heatmap_tuple")
    annotations_perf_turn_list_tuple = cache.get("annotations_perf_list_tuple")
    df_repair_heatmap_tuple = cache.get("df_repair_heatmap_tuple")
    annotations_repair_turn_list_tuple = cache.get("annotations_repair_list_tuple")
    df_working_time = cache.get("df_working_time")
    df_caixas_cf = cache.get("df_caixas_cf")
    df_caixas_cf_tot = cache.get("df_caixas_cf_tot")
    df_info_pure = cache.get("df_info_pure")

    return (
        df_maq_info_cadastro,
        df_maq_info_prod_cad,
        df_eff,
        df_perf,
        df_repair,
        df_eff_heatmap_tuple,
        annotations_eff_turn_list_tuple,
        df_perf_heatmap_tuple,
        annotations_perf_turn_list_tuple,
        df_repair_heatmap_tuple,
        annotations_repair_turn_list_tuple,
        df_working_time,
        df_caixas_cf,
        df_caixas_cf_tot,
        df_info_pure,
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
    try:
        if os.getenv("APP_ENV") == "production":
            print("Starting the server on port 8080 in production mode...")
            serve(app.server, host="0.0.0.0", port=8080)
        else:
            print("Starting the server on port 8050 in development mode...")
            app.run_server(debug=True, port=8050)
    # pylint: disable=W0703
    except Exception as e:
        print(f"Failed to start the server: {e}")
