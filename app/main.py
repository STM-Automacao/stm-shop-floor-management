"""
    Autor: Bruno Tomaz
    Data: 15/01/2024
    Este módulo é o responsável por iniciar a aplicação Dash.
    A aplicação Dash é uma aplicação web que permite a criação de dashboards interativos.
    A aplicação Dash é baseada em Flask e React.
    Para mais informações, acesse: https://dash.plotly.com/
"""

import logging
import os
from threading import Lock

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from dash import callback, dcc, html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from dash_bootstrap_templates import ThemeSwitchAIO

# pylint: disable=E0401
from database.last_month_ind import LastMonthInd
from helpers.cache import MainDataCache
from helpers.path_config import UrlPath
from pages import grafana, hour_prod, main_page, management, pcp
from service.big_data import BigData
from waitress import serve

from app import app

# =========================================== Variáveis ========================================== #

lock = Lock()
last_month_ind = LastMonthInd()
cache = MainDataCache(app)
logging.basicConfig(
    filename="app.log", filemode="w", format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("apscheduler").setLevel(logging.DEBUG)

# Seleção de temas para o App - Variáveis:
URL_BOOTS = dbc.themes.BOOTSTRAP  # para o switch
URL_DARKY = dbc.themes.DARKLY


# ================================== Atualizações Em Background ================================== #
def get_current_time():
    """
    Returns the current timestamp.

    Returns:
        pd.Timestamp: The current timestamp.
    """
    return pd.Timestamp.now()


def update_last_month():
    """
    Função que salva imagens de gauge do mês anterior.
    """
    try:
        with lock:
            last_month_ind.save_last_month_data()
    # pylint: disable=W0718
    except Exception as err:
        logging.error("Erro ao executar update de last month: %s", err)


def update_big_data():
    """
    Atualiza os dados grandes.

    Esta função chama o método save_big_data para salvar os dados grandes.

    """
    logger = logging.getLogger("update_big_data")
    logger.setLevel(logging.INFO)

    logger.info("Iniciando update de big data")
    try:
        with lock:
            big_data = BigData()
            big_data.save_big_data()
        logger.info("Update bem sucedido")
    # pylint: disable=W0718
    except Exception as err:
        logger.error("Erro ao executar update de big data: %s", err)


def update_cache():
    """
    Atualiza cache
    """
    try:
        cache.update_cache()
    # pylint: disable=W0718
    except Exception as err:
        logging.error("Erro ao executar update de cache: %s", err)


def cache_daily_data():
    """
    Função que atualiza o cache diariamente.
    """
    try:
        cache.cache_daily_data()
    # pylint: disable=W0718
    except Exception as err:
        logging.error("Erro ao executar update daily data: %s", err)


scheduler = BackgroundScheduler()
scheduler.add_job(func=get_current_time, trigger="interval", minutes=1)
scheduler.add_job(func=update_cache, trigger="interval", minutes=5)
scheduler.add_job(func=update_big_data, trigger="cron", hour=5)
scheduler.add_job(func=cache_daily_data, trigger="cron", hour=0, minute=1)
scheduler.add_job(func=update_last_month, trigger="cron", hour=1)  # Atualiza a cada 24 horas

scheduler.start()

update_cache()

# ============================================ Layout ============================================ #

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
                        class_name="h-100 d-flex align-items-center justify-content-end mt-3 mr-3",
                    ),
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            html.H1("Shop Floor Management", className="text-center"),
                        ),
                        dcc.Location(id="url"),
                    ],
                ),
                dbc.Row(
                    id="tab-row",
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


# ================================================================================================ #
#                                            CALLBACK'S                                            #
# ================================================================================================ #


# ======================================== Caminhos E Abas ======================================= #
@callback(
    Output("tab-row", "children"),
    Input("url", "pathname"),
)
def update_tabs(pathname):
    """
    Função que atualiza o conteúdo da aba com base no pathname.

    Parâmetros:
    pathname (str): O pathname da URL.

    Retorna:
    list: A lista de componentes da aba.
    """
    # cSpell: words lider

    tabs_info = [
        (grafana.layout, "Ao Vivo", "tab-grafana"),
        (main_page.layout, "SFM Dashboard", "tab-sfm-dashboard"),
        (management.layout, "Gestão de Produção", "tab-management"),
        (hour_prod.layout, "Produção por Hora", "tab-hour-prod"),
        (pcp.layout, "PCP", "tab-pcp"),
    ]

    all_tabs = [dbc.Tab(layout, label=label, tab_id=tab_id) for layout, label, tab_id in tabs_info]

    tabs = {
        "/": all_tabs[:3],
        UrlPath.LIDER.value: all_tabs[:2],
        UrlPath.SUPERVISOR.value: all_tabs[:3],
        UrlPath.COORDENADOR.value: all_tabs[:4],
        UrlPath.PCP.value: [all_tabs[0], all_tabs[4]] + all_tabs[1:4],
        UrlPath.MAIN.value: all_tabs,
    }

    return dbc.Tabs(tabs.get(pathname, all_tabs), id="dbc-tabs")


@callback(
    Output("url", "hash"),
    Input("dbc-tabs", "active_tab"),
)
def update_hash(active_tab):
    """
    Função que atualiza o hash da URL com base na aba ativa.

    Parâmetros:
    active_tab (str): O ID da aba ativa.

    Retorna:
    str: O hash da URL.
    """

    return f"#{active_tab}"


# =================================== Switch De Cores Do Rodapé ================================== #
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


# ====================================== Tema Para Provider ====================================== #
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


# ===================================== Atualizações Do Store ==================================== #
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

    if cache.cache.get("df1") is None or cache.cache.get("df2") is None:
        raise PreventUpdate

    df_maq_info_cadastro = cache.cache.get("df1")
    df_maq_info_prod_cad = cache.cache.get("df2")
    df_eff = cache.cache.get("df_eff")
    df_perf = cache.cache.get("df_perf")
    df_repair = cache.cache.get("df_repair")
    df_eff_heatmap_tuple = cache.cache.get("df_eff_heatmap_tuple")
    annotations_eff_turn_list_tuple = cache.cache.get("annotations_eff_list_tuple")
    df_perf_heatmap_tuple = cache.cache.get("df_perf_heatmap_tuple")
    annotations_perf_turn_list_tuple = cache.cache.get("annotations_perf_list_tuple")
    df_repair_heatmap_tuple = cache.cache.get("df_repair_heatmap_tuple")
    annotations_repair_turn_list_tuple = cache.cache.get("annotations_repair_list_tuple")
    df_working_time = cache.cache.get("df_working_time")
    df_caixas_cf = cache.cache.get("df_caixas_cf")
    df_caixas_cf_tot = cache.cache.get("df_caixas_cf_tot")
    df_info_pure = cache.cache.get("df_info_pure")

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


# ================================================================================================ #
#                                                RUN                                               #
# ================================================================================================ #
# ============================================ Run App =========================================== #
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
