"""
Esta é a página de gestão da produção.
    - Autor: Bruno Tomaz
    - Data de criação: 13/03/2024
"""

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import Input, Output, State, callback, dcc
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from management.components import modal_estoque
from management.pages import dashboards_pg, history_pg, production_cards_pg, tables_management_pg

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
                    label=dmc.Text("Produção do Dia/Mês", size="xl"),
                    id="production-cards-navlink",
                    href="#production-cards",
                    leftSection=DashIconify(icon="solar:box-outline"),
                    active=True,
                    fz=30,
                ),
                dmc.NavLink(
                    label=dmc.Text("Dashboards", size="xl"),
                    id="dashboards-navlink-management",
                    href="#dashboards-management",
                    leftSection=DashIconify(icon="system-uicons:graph-bar"),
                    fz=30,
                ),
                dmc.NavLink(
                    label=dmc.Text("Tabelas", size="xl"),
                    id="tables-navlink",
                    href="#management-tables",
                    leftSection=DashIconify(icon="carbon:table"),
                    fz=30,
                ),
                dmc.NavLink(
                    label=dmc.Text("Histórico", size="xl"),
                    id="history-navlink",
                    href="#management-history",
                    leftSection=DashIconify(
                        icon="material-symbols-light:deployed-code-history-outline"
                    ),
                    fz=30,
                ),
                dmc.NavLink(
                    label=dmc.Text("Estoque", size="xl"),
                    description=dmc.Text("Atualizado às 00hs", size="sm"),
                    id="estoque-navlink",
                    leftSection=DashIconify(icon="maki:warehouse"),
                    fz=30,
                ),
            ],
        ),
        # ========================================= Body ========================================= #
        dbc.Row(
            id="management-main-content", children=production_cards_pg.layout, class_name="p-2"
        ),
        # =================================== Modal De Estoque =================================== #
        dbc.Modal(
            children=modal_estoque.layout,
            id="modal-estoque",
            size="xl",
            fullscreen="lg-down",
            scrollable=True,
            modal_class_name="inter",
            is_open=False,
        ),
    ]
)

# ================================================================================================ #
#                                             CALLBACKS                                            #
# ================================================================================================ #


# ============================================ Drawer ============================================ #
@callback(
    Output("management-drawer", "opened"),
    Input("management-drawer-btn", "n_clicks"),
    Input("modal-estoque", "is_open"),
    prevent_initial_call=True,
)
def management_toggle_drawer(_, estoque_is_open):
    """
    Abre ou fecha o drawer.

    Parâmetros:
    _ (qualquer): Parâmetro não utilizado.

    Retorno:
    bool: True se o drawer estiver aberto, False caso contrário.
    """
    if estoque_is_open:
        return False
    return True


# =========================================== Locations ========================================== #
@callback(
    Output("management-main-content", "children"),
    Output("production-cards-navlink", "active"),
    Output("dashboards-navlink-management", "active"),
    Output("history-navlink", "active"),
    Output("tables-navlink", "active"),
    Input("management-url", "hash"),
)
def management_content_navlink_update(hash_):
    """
    Renderiza a página de acordo com o hash.

    Parâmetros:
    hash_ (str): Hash da URL.

    Retorno:
    list: Layout da página.
    """

    # Dicionário de hash e layout
    hash_dict = {
        "#production-cards": production_cards_pg.layout,
        "#dashboards-management": dashboards_pg.layout,
        "#management-history": history_pg.layout,
        "#management-tables": tables_management_pg.layout,
    }

    # Verifica se o hash está no dicionário de hash, se não estiver, pega o primeiro hash
    if hash_ not in hash_dict:
        raise PreventUpdate

    # Pega o conteúdo e verifica qual NavLink está ativo
    content = hash_dict[hash_]
    active_navlinks = tuple(hash_ == hash_option for hash_option in hash_dict)

    return content, *active_navlinks


# ============================================= Modal ============================================ #
@callback(
    Output("modal-estoque", "is_open"),
    Input("estoque-navlink", "n_clicks"),
    State("modal-estoque", "is_open"),
    prevent_initial_call=True,
)
def toggle_modal_estoque(_, is_open):
    """
    Abre ou fecha o modal de estoque.

    Parâmetros:
    _ (int): Número de cliques no NavLink.
    is_open (bool): Estado atual do modal.

    Retorno:
    bool: True se o modal estiver aberto, False caso contrário.
    """
    return not is_open, False
