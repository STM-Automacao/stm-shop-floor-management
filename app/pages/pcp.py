"""
Módulo com dados de Batidas de massa.
"""

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from apscheduler.schedulers.background import BackgroundScheduler
from dash import Input, Output, callback, dcc
from dash_iconify import DashIconify
from pcp.frontend import massa_analysis_pcp, massa_batidas_pcp
from pcp.frontend.components_pcp import ComponentsPcpBuilder
from pcp.helpers.cache_pcp import PcpDataCache

from app import app

# =========================================== Variáveis ========================================== #
pcp_data = PcpDataCache(app)
update_massa_cache = pcp_data.cache_massa_data
scheduler = BackgroundScheduler()
pcp_builder = ComponentsPcpBuilder()
layout_pcp_massa_analysis = massa_analysis_pcp.layout
layout_pcp_massa_batidas = massa_batidas_pcp.layout


# ====================================== Cache Em Background ===================================== #

scheduler.add_job(update_massa_cache, "interval", minutes=5)
scheduler.start()

# ================================================================================================ #
#                                              LAYOUT                                              #
# ================================================================================================ #
layout = [
    dcc.Store(id="df_sum"),
    dcc.Store(id="df_week"),
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
                label="Análise de Massa",
                id="massa-analysis-navlink",
                href="#massa-analysis",
                leftSection=DashIconify(icon="mdi:bread"),
            ),
            dmc.NavLink(
                label="Batidas de Massa",
                id="massa-batidas-navlink",
                href="#massa-batidas",
                leftSection=DashIconify(icon="game-icons:dough-roller"),
            ),
        ],
    ),
    # =========================================== Body =========================================== #
    dbc.Row(id="pcp-main-content", children=layout_pcp_massa_analysis, class_name="p-2"),
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
@callback(Output("pcp-main-content", "children"), Input("pcp-url", "hash"))
def update_content(hash_):
    """
    Atualiza o conteúdo principal.

    Parâmetros:
    hash_ (str): O hash da URL.

    Retorno:
    list: A lista de componentes a serem exibidos.
    """
    hash_dict = {
        "#massa-analysis": layout_pcp_massa_analysis,
        "#massa-batidas": layout_pcp_massa_batidas,
    }

    return hash_dict.get(hash_, layout_pcp_massa_analysis)


@callback(
    Output("massa-analysis-navlink", "active"),
    Output("massa-batidas-navlink", "active"),
    Input("pcp-url", "hash"),
)
def update_navlink_active(hash_):
    """
    Atualiza o NavLink ativo.

    Parâmetros:
    hash_ (str): O hash da URL.

    Retorno:
    tuple: Um tuple contendo o estado de ativação dos NavLink.
    """
    return hash_ == "#massa-analysis", hash_ == "#massa-batidas"
