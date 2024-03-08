"""
    Este módulo é o responsável por trazer dados do grafana(maquina_tela) para a aplicação Dash.
"""

# cSpell:words grafana eficiencia
import dash_bootstrap_components as dbc
from dash import callback, dcc, html
from dash.dependencies import Input, Output

# pylint: disable=E0401
from database.get_data import GetData
from helpers.types import get_color

get_data = GetData()

# ========================================= Layout ========================================= #

layout = html.Div(
    [
        html.H1("Dados do Grafana", className="text-center"),
        html.Div(id="grafana-content"),
        dcc.Interval(id="grafana-interval", interval=1000 * 60 * 2, n_intervals=0),
    ]
)

# ========================================= Callbacks ========================================= #


@callback(
    Output("grafana-content", "children"),
    [Input("grafana-content", "children"), Input("grafana-interval", "n_intervals")],
)
def update_grafana(_n, _n_intervals):
    """
    Função que atualiza o conteúdo do grafana.
    """

    # Busca os dados do grafana no banco de dados maquina_tela
    grafana_content = get_data.get_maq_tela()

    # Ordenar por linha
    grafana_content = grafana_content.sort_values(by="linha")

    # Remove a linha 0
    grafana_content = grafana_content[grafana_content.linha != 0]

    cards = []

    # Cria uma row para cada linha e um card para as colunas linha, status e Produto
    for row in grafana_content.iterrows():
        eff_15_min = round((float(row[1]["ciclo_15_min"]) / float(150)) * 100)
        ciclo = round(float(row[1]["ciclo_1_min"]) * 10)

        cards.append(
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Linha", class_name="truncate"),
                                dbc.CardBody(
                                    f"{row[1]['linha']}",
                                    class_name="card-body-modal-style fs-3",
                                ),
                            ],
                            class_name="h-100",
                        ),
                        md=1,
                        class_name="p-1",
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Status"),
                                dbc.CardBody(
                                    "Rodando" if row[1]["status"] == "true" else "Parada",
                                    style={
                                        "color": ("green" if row[1]["status"] == "true" else "red")
                                    },
                                    class_name="card-body-modal-style fs-3",
                                ),
                            ],
                            class_name="h-100",
                        ),
                        md=2,
                        class_name="p-1",
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Produto"),
                                dbc.CardBody(
                                    html.Div(
                                        f"{row[1]['produto_nome']}",
                                        className="truncate",
                                        id=f"produto-{row[1]['linha']}",
                                    ),
                                    class_name="card-body-modal-style fs-6",
                                ),
                            ],
                            class_name="h-100",
                        ),
                        md=2,
                        class_name="p-1",
                    ),
                    dbc.Tooltip(
                        f"{row[1]['produto_nome']}",
                        target=f"produto-{row[1]['linha']}",
                        placement="top",
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Eficiência 15min", class_name="truncate"),
                                dbc.CardBody(
                                    f"{eff_15_min}%",
                                    style=({"color": get_color(eff_15_min, 100)}),
                                    class_name="card-body-modal-style fs-4",
                                ),
                            ],
                            class_name="h-100",
                            id=f"eficiencia-15min-{row[1]['linha']}",
                        ),
                        md=1,
                        class_name="p-1",
                    ),
                    dbc.Tooltip(
                        "Eficiência 15min",
                        target=f"eficiencia-15min-{row[1]['linha']}",
                        placement="top",
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Ciclos", class_name="truncate"),
                                dbc.CardBody(
                                    f"{ciclo}%",
                                    style=({"color": get_color(ciclo, 100)}),
                                    class_name="card-body-modal-style fs-4",
                                ),
                            ],
                            class_name="h-100",
                        ),
                        md=1,
                        class_name="p-1",
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Produção", class_name="truncate"),
                                dbc.CardBody(
                                    f"{round(float(row[1]['total_produzido']))}",
                                    style=(
                                        {"color": get_color(float(row[1]["total_produzido"]), 7200)}
                                    ),
                                    class_name="card-body-modal-style fs-4",
                                ),
                            ],
                            class_name="h-100",
                        ),
                        md=1,
                        class_name="p-1",
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Eficiência", class_name="truncate"),
                                dbc.CardBody(
                                    f"{round(float(row[1]['eficiencia']))}%",
                                    style=({"color": get_color(float(row[1]["eficiencia"]), 100)}),
                                    class_name="card-body-modal-style fs-4",
                                ),
                            ],
                            class_name="h-100",
                            id=f"eficiencia-{row[1]['linha']}",
                        ),
                        md=1,
                        class_name="p-1",
                    ),
                    dbc.Tooltip(
                        "Eficiência",
                        target=f"eficiencia-{row[1]['linha']}",
                        placement="top",
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Tempo Parada", class_name="truncate"),
                                dbc.CardBody(
                                    f"{round(float(row[1]['tempo_parada']))}",
                                    style=(
                                        {
                                            "color": (
                                                "green" if row[1]["tempo_parada"] < 20 else "red"
                                            )
                                        }
                                    ),
                                    class_name="card-body-modal-style fs-4",
                                ),
                            ],
                            class_name="h-100",
                            id=f"tempo_parada-{row[1]['linha']}",
                        ),
                        md=1,
                        class_name="p-1",
                    ),
                    dbc.Tooltip(
                        "Tempo Parada",
                        target=f"tempo_parada-{row[1]['linha']}",
                        placement="top",
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Motivo da Parada", class_name="truncate"),
                                dbc.CardBody(
                                    html.Div(f"{row[1]['parada_nome']}", className="truncate"),
                                    class_name="card-body-modal-style fs-4",
                                    id=f"parada_nome-{row[1]['linha']}",
                                ),
                            ],
                            class_name="h-100",
                        ),
                        md=2,
                        class_name="p-1",
                    ),
                    dbc.Tooltip(
                        f"{row[1]['parada_nome']}",
                        target=f"parada_nome-{row[1]['linha']}",
                        placement="top",
                    ),
                ],
                className="mb-0 p-0",
            ),
        )

    return cards
