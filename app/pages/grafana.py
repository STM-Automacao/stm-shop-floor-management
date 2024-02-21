"""
    Este módulo é o responsável por trazer dados do grafana(maquina_tela) para a aplicação Dash.
"""

# cSpell:words grafana eficiencia
import dash_bootstrap_components as dbc
from dash import callback, html
from dash.dependencies import Input, Output

# pylint: disable=E0401
from database.get_data import GetData

get_data = GetData()

# ========================================= Layout ========================================= #

layout = html.Div(
    [
        html.H1("Grafana", className="text-center"),
        html.Div(id="grafana-content"),
    ]
)

# ========================================= Callbacks ========================================= #


@callback(
    Output("grafana-content", "children"),
    Input("grafana-content", "children"),
)
def update_grafana(_n):
    """
    Função que atualiza o conteúdo do grafana.
    """

    # Busca os dados do grafana no banco de dados maquina_tela
    grafana_content = get_data.get_maq_tela()

    # Ordenar por linha
    grafana_content = grafana_content.sort_values(by="linha")

    # Remove a linha 0
    grafana_content = grafana_content[grafana_content.linha != 0]

    test = []

    # Cria uma row para cada linha e um card para as colunas linha, status e Produto
    for row in grafana_content.iterrows():
        test.append(
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Linha"),
                                dbc.CardBody(
                                    f"{row[1]['linha']}",
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
                                    f"{row[1]['produto_nome']}",
                                    class_name="card-body-modal-style fs-4 truncate",
                                ),
                            ],
                            class_name="h-100",
                        ),
                        md=3,
                        class_name="p-1",
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Eficiência 15min", class_name="truncate"),
                                dbc.CardBody(
                                    f"{round(float(row[1]['eficiencia']))}%",
                                    style=(
                                        {"color": "green"}
                                        if float(row[1]["eficiencia"]) > 90
                                        else {"color": "red"}
                                    ),
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
                ],
                className="mb-0 p-0",
            ),
        )

    print(grafana_content.info())

    return test
