"""
Esta é a página de gestão da produção.
    - Autor: Bruno Tomaz
    - Data de criação: 13/03/2024
"""

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import Input, Output, callback, dcc
from dash_iconify import DashIconify
from management.pages import dashboards_pg, production_cards_pg

# ================================================================================================ #
#                                              LAYOUT                                              #
# ================================================================================================ #
layout = dbc.Stack(
    [
        dcc.Location(id="management-url"),
        # ====================================== Drawer Btn ====================================== #
        dbc.Button(
            id="management-drawer-btn",
            color="secondary",
            outline=True,
            children=DashIconify(icon="mdi:menu"),
            style={"width": "50px"},
            class_name="d-flex justify-content-center align-items-center float-left mt-2 ml-2",
        ),
        # ======================================== Drawer ======================================== #
        dmc.Drawer(
            id="management-drawer",
            children=[
                dmc.NavLink(
                    label=dmc.Text("Produção Dia/Mês", size="xl"),
                    id="production-cards-navlink",
                    href="#production-cards",
                    leftSection=DashIconify(icon="fluent:box-24-filled"),
                    fz=30,
                ),
                dmc.NavLink(
                    label=dmc.Text("Dashboards", size="xl"),
                    id="dashboards-navlink-management",
                    href="#dashboards-management",
                    leftSection=DashIconify(icon="system-uicons:graph-bar"),
                    fz=30,
                ),
            ],
        ),
        # ========================================= Body ========================================= #
        dbc.Row(id="management-main-content", class_name="p-2"),
    ]
)

# ================================================================================================ #
#                                             CALLBACKS                                            #
# ================================================================================================ #


# ============================================ Drawer ============================================ #
@callback(
    Output("management-drawer", "opened"),
    Input("management-drawer-btn", "n_clicks"),
    prevent_initial_call=True,
)
def management_toggle_drawer(_):
    """
    Abre ou fecha o drawer.

    Parâmetros:
    _ (qualquer): Parâmetro não utilizado.

    Retorno:
    bool: True se o drawer estiver aberto, False caso contrário.
    """
    return True


# =========================================== Locations ========================================== #
@callback(
    Output("management-main-content", "children"),
    Input("management-url", "hash"),
)
def management_render_page(hash_):
    """
    Renderiza a página de acordo com o hash.

    Parâmetros:
    hash_ (str): Hash da URL.

    Retorno:
    list: Layout da página.
    """
    hash_dict = {
        "#production-cards": production_cards_pg.layout,
        "#dashboards-management": dashboards_pg.layout,
    }

    return hash_dict.get(hash_, production_cards_pg.layout)


# Atualizar hash da URL
@callback(
    Output("production-cards-navlink", "active"),
    Output("dashboards-navlink-management", "active"),
    Input("management-url", "hash"),
)
def update_active_navlink_management(hash_):
    """
    Atualiza o NavLink ativo.

    Parâmetros:
    hash_ (str): Hash da URL.

    Retorno:
    bool: True se o NavLink estiver ativo, False caso contrário.
    """
    return hash_ == "#production-cards", hash_ == "#dashboards-management"
