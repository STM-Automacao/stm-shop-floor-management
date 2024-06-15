"""
Módulo com dados de Batidas de massa.
"""

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from apscheduler.schedulers.background import BackgroundScheduler
from components.grid_aggrid import GridAgGrid
from dash import Input, Output, callback, dcc
from dash_iconify import DashIconify
from pcp.frontend import massa_analysis_pcp, massa_batidas_pcp, pasta_batidas_pcp, producao_pcp
from pcp.helpers.cache_pcp import PcpDataCache

from app import app

# =========================================== Variáveis ========================================== #
pcp_data = PcpDataCache(app)
update_massa_cache = pcp_data.cache_massa_data
scheduler = BackgroundScheduler()
pcp_builder = GridAgGrid()


# ====================================== Cache Em Background ===================================== #

scheduler.add_job(update_massa_cache, "interval", minutes=5)
scheduler.start()

# ================================================================================================ #
#                                              LAYOUT                                              #
# ================================================================================================ #
layout = [
    dcc.Store(id="df_sum", storage_type="local"),
    dcc.Store(id="df_week", storage_type="local"),
    dcc.Interval(id="interval-component-pcp", interval=1000 * 60 * 5, n_intervals=0),
    dcc.Location(id="pcp-url"),
    # ============================================ Btn =========================================== #
    dbc.Button(
        id="pcp-drawer-btn",
        color="secondary",
        outline=True,
        children=DashIconify(icon="mdi:menu"),
        style={"width": "50px"},
        class_name="d-flex justify-content-center align-items-center float-left mt-2 ml-2",
    ),
    # ========================================== Drawer ========================================== #
    dmc.Drawer(
        id="pcp-drawer",
        children=[
            dmc.NavLink(
                label=dmc.Text("Análise de Massa", size="xl"),
                id="massa-analysis-navlink",
                href="#massa-analysis",
                active=True,
                leftSection=DashIconify(icon="mdi:bread"),
                fz=30,
            ),
            dmc.NavLink(
                label=dmc.Text("Batidas de Massa", size="xl"),
                id="massa-batidas-navlink",
                href="#massa-batidas",
                leftSection=DashIconify(icon="game-icons:dough-roller"),
                fz=30,
            ),
            dmc.NavLink(
                label=dmc.Text("Batidas de Pasta", size="xl"),
                id="pasta-batidas-navlink",
                href="#pasta-batidas",
                leftSection=DashIconify(icon="arcticons:garlic-player"),
                fz=30,
            ),
            dmc.NavLink(
                label=dmc.Text("Produção Semanal", size="xl"),
                id="pcp-production-navlink",
                href="#pcp-production",
                leftSection=DashIconify(icon="mdi:calendar-week"),
                fz=30,
            ),
        ],
    ),
    # =========================================== Body =========================================== #
    dbc.Row(id="pcp-main-content", children=massa_analysis_pcp.layout, class_name="p-2"),
]

# ================================================================================================ #
#                                            CALLBACK'S                                            #
# ================================================================================================ #


# ===================================== Atualização Do Store ===================================== #
@callback(
    Output("df_sum", "data"),
    Output("df_week", "data"),
    Input("interval-component-pcp", "n_intervals"),
)
def update_store(_):
    """
    Atualiza o store.

    Retorna um tuple contendo os dados do cache "df_sum" e "df_week".

    Parâmetros:
    _ (qualquer): Parâmetro não utilizado.

    Retorno:
    tuple: Um tuple contendo os dados do cache "df_sum" e "df_week".
    """
    return (
        pcp_data.cache.get("df_sum"),
        pcp_data.cache.get("df_week"),
    )


# ============================================ Drawer ============================================ #
@callback(
    Output("pcp-drawer", "opened"), Input("pcp-drawer-btn", "n_clicks"), prevent_initial_call=True
)
def toggle_drawer(_):
    """
    Abre ou fecha o drawer.

    Parâmetros:
    _ (qualquer): Parâmetro não utilizado.

    Retorno:
    bool: True se o drawer estiver aberto, False caso contrário.
    """
    return True


# =========================================== Location =========================================== #
@callback(
    Output("pcp-main-content", "children"),
    Output("massa-analysis-navlink", "active"),
    Output("massa-batidas-navlink", "active"),
    Output("pcp-production-navlink", "active"),
    Output("pasta-batidas-navlink", "active"),
    Input("pcp-url", "hash"),
)
def update_content_and_navlink_active(hash_):
    """
    Atualiza o conteúdo principal e o NavLink ativo.

    Parâmetros:
    hash_ (str): O hash da URL.

    Retorno:
    tuple: Um tuple contendo a lista de componentes e o estado de ativação dos NavLink.
    """

    # Dicionário de hash e layout
    hash_dict = {
        "#massa-analysis": massa_analysis_pcp.layout,
        "#massa-batidas": massa_batidas_pcp.layout,
        "#pcp-production": producao_pcp.layout,
        "#pasta-batidas": pasta_batidas_pcp.layout,
    }

    # Verifica se o hash está no dicionário de hash, se não estiver, pega o primeiro hash
    if hash_ not in hash_dict:
        hash_ = list(hash_dict)[0]

    # Pega o conteúdo e verifica qual NavLink está ativo
    content = hash_dict.get(hash_, massa_analysis_pcp.layout)
    active_navlinks = tuple(hash_ == hash_option for hash_option in hash_dict)

    return content, *active_navlinks
