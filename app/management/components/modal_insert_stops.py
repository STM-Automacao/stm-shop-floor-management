"""This module contains the layout for the modal that allows the user to insert stops."""

import datetime

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import Input, Output, State, callback
from dash import callback_context as ctx
from dash import html
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from database.insert_data import InsertData

# cSpell:words termoformadoras lamecação kaizen

# =========================================== Variáveis ========================================== #
insert_data = InsertData().insert_maq_ihm_data

termoformadoras = [
    "TMF001",
    "TMF002",
    "TMF003",
    "TMF004",
    "TMF005",
    "TMF006",
    "TMF007",
    "TMF008",
    "TMF009",
    "TMF010",
    "TMF011",
    "TMF012",
    "TMF013",
    "TMF014",
    "TMF015",
]

options = {
    "Ajustes": {
        "Recheadora": {
            "Quantidade de Recheio não Conforme": [
                "Bico entupido",
                "Bomba com Falha",
                "Falha durante a dosagem",
                "Falha no sensor de posição",
                "Pão sem corte",
            ],
            "Pão amassado": ["Seleção de Pão com tamanho irregular"],
        },
        "Termoformadora": {
            "Bobina desenquadrando na vertical": ["Ajuste de Fotocélula", "Ajuste de Freio"],
            "Bobina desenquadrando na horizontal": ["Ajuste de posição da Bobina"],
            "Abrindo Bandejas": [
                "Limpeza de Placa",
                "Ajuste de ATM",
                "Ajuste no enquadramento do filme superior",
                "Análise de Formação",
                "Análise de falta de sr comprimido",
                "Ajuste de Temperatura",
                "Troca de Bobina",
                "Análise de corte da faca",
            ],
            "Bandeja Murcha ou Cheia": [
                "Ajuste na quantidade de gás",
                "Ajuste de vácuo",
                "Troca de Bobina",
            ],
            "Bandeja deformada ou manchada": [
                "Troca de Bobina",
                "Ajuste na temperatura de Formação",
            ],
            "Bobina inferior saindo da corrente": [
                "Troca de Bobina",
                "Ajuste na posição da Bobina",
            ],
            "Troca de Bobina": ["Troca de Bobina Inferior", "Troca de Bobina Superior"],
        },
        "Robô": {
            "Robô Travando": [
                "Rearme do Robô",
                "Ajuste nas Guias das Caixas",
                "Ajuste das Guias das Bandejas",
            ]
        },
        "Detector de Metais": {
            "Variação de Peso": ["Solicitado ajuste na dosagem do recheio"],
            "Falha no teste do corpo de prova": ["Reavaliar o último lote produzido"],
        },
        "Seladora de Caixas": {
            "Caixa Rasgada": ["Troca do Lote de Caixas", "Ajuste na Dimensão da Caixa"],
            "Caixa não Selando": [
                "Troca do Lote de Adesivos",
                "Ajuste na Dimensão da Caixa",
                "Troca do Lote de Caixas",
            ],
        },
        "Armadora de Caixas": {
            "Caixa Rasgada": ["Troca do Lote de Caixas", "Ajuste na Dimensão da Caixa"],
            "Caixa não Selando": [
                "Troca do Lote de Adesivos",
                "Ajuste na Dimensão da Caixa",
                "Troca do Lote de Caixas",
            ],
        },
    },
    "Manutenção": {
        "Recheadora": {
            "Quantidade de Recheio não Conforme": [
                "Caca não corta adequadamente",
                "Correção de falha no drive",
                "Falha na bobina do estator",
                "Necessidade de análise",
            ],
            "Pão amassado": [
                "Correção da altura do guia da faca",
                "Faca sem corte afiado",
                "Necessidade de análise",
            ],
            "Alarme constante ou não sai": [
                "Alarme de pressão",
                "Alarme de falha na bomba de dosagem",
                "Alarme de bomba de moega",
            ],
            "Parada de função da máquina": ["Esteira parou", "Rolete parou", "Berço parou"],
        },
        "Termoformadora": {
            "Falha no corte da bandeja": [
                "Ajuste ou troca da faca transversal",
                "Ajuste ou troca da faca longitudinal",
            ],
            "Abrindo Bandejas": ["Realizar análise da falha"],
            "Bandeja Murcha ou Cheia": ["Realizar análise da falha"],
            "Bandeja deformada ou manchada": ["Realizar análise da falha"],
            "Bobina inferior saindo da corrente": ["Realizar análise da falha"],
            "Bobina Desenquadrando": ["Realizar análise da falha"],
            "Alarme constante ou não sai": [
                "Alarme de fim de filme superior ou inferior",
                "Alarme referente ao gás",
                "Alarme referente ao vácuo",
                "Alarme de fluxo de água",
                "Alarme de falha nos motores",
                "Alarme de falha de avanço",
                "Alarme de falha de codificadores",
                "Alarme de não detecta conjunto acima",
                "Alarme de não detecta conjunto abaixo",
                "Alarme de falha na pressão do circuito pneumático",
                "Alarme de grade de segurança aberta",
                "Alarme de temperatura",
            ],
        },
        "Robô": {
            "Robô Travando": [
                "Rearme do Robô",
                "Ajuste nas Guias das Caixas",
                "Ajuste das Guias das Bandejas",
            ]
        },
        "Detector de Metais": {
            "Variação de Peso": ["Solicitado ajuste na dosagem do recheio"],
            "Falha no teste do corpo de prova": ["Reavaliar o último lote produzido"],
        },
        "Seladora de Caixas": {
            "Caixa Rasgada": ["Troca do Lote de Caixas", "Ajuste na Dimensão da Caixa"],
            "Caixa não Selando": [
                "Troca do Lote de Adesivos",
                "Ajuste na Dimensão da Caixa",
                "Troca do Lote de Caixas",
            ],
        },
        "Armadora de Caixas": {
            "Caixa Rasgada": ["Troca do Lote de Caixas", "Ajuste na Dimensão da Caixa"],
            "Caixa não Selando": [
                "Troca do Lote de Adesivos",
                "Ajuste na Dimensão da Caixa",
                "Troca do Lote de Caixas",
            ],
        },
    },
    "Setup": {
        "Recheadora": {
            "Troca de Produto": ["Troca de Faca", "Troca de Recheadora"],
            "Troca de Sabor": [
                "Troca para sabor Tradicional",
                "Troca para sabor Picante",
                "Troca para sabor Doce",
                "Troca para sabor Cebola",
            ],
        },
        "Termoformadora": {
            "Troca de Produto": [
                "Troca de molde para baguete 400g",
                "Troca de molde para baguete 240g",
                "Troca de molde para bolinha",
            ],
            "Troca de Sabor": [
                "Troca para bobina Tradicional 400g",
                "Troca para bobina Picante 400g",
                "Troca para bobina Doce Bolinha",
                "Troca para bobina Cebola 400g",
                "Troca para bobina Tradicional Bolinha",
                "Troca para bobina Doce Swift",
                "Troca para bobina Cebola Bolinha",
                "Troca para bobina Picante 240g",
                "Troca para bobina Tradicional 240g",
                "Troca para bobina Tradicional 400g Paraguai",
                "Troca para bobina Picante 400g Paraguai",
                "Troca para bobina Tradicional 240g Paraguai",
                "Troca para bobina Cebola 400g Paraguai",
                "Troca para bobina Picante 240g Paraguai",
            ],
        },
    },
    "Qualidade": {
        "Termoformadora": {
            "Risco de Contaminação": [
                "Elemento Mecânico",
                "Odor Diferente",
                "Pasta com Tempo ALto",
                "Limpeza da Esteira de Lamecação",
                "Limpeza de Placa",
            ]
        },
        "Recheadora": {
            "Parâmetros de Qualidade": [
                "Bandeja com formação não conforme",
                "Solda não conforme",
                "ATM fora do padrão",
                "Data manchado ou ilegível",
                "Data fora de posição",
                "Esquadro da bandeja inadequado",
                "Corte inadequado",
                "Rebarba no corte da bandeja",
            ]
        },
    },
    "Fluxo": {
        "Recheadora": {
            "Falta de Pão": [
                "Pão sem tamanho uniforme",
                "Temperatura do pão",
                "Panificação com máquina quebrada",
            ],
            "Falta de Pasta": [
                "Reator quebrado",
                "Bomba com problemas",
                "Batida de pasta interrompida pela qualidade",
            ],
        },
        "Termoformadora": {
            "Esteira Cheia": [
                "Robô parado",
                "Detector de metais com problema",
                "Problema com montagem de caixas",
            ],
        },
    },
    "Limpeza": {
        "Linha": {
            "Limpeza para parada de Fábrica": ["Limpeza para parada de Fábrica"],
        }
    },
    "Parada Programada": {
        "Linha": {
            "Parada Planejada": [
                "Refeição",
                "Café e Ginástica Laboral",
                "Reunião",
                "Backup",
                "Sem Produção",
            ],
            "Parada para Treinamento": [
                "Relacionado a Qualidade",
                "Relacionado a Melhoria",
                "Kaizen",
                "Solução de Problemas",
            ],
        },
    },
}


# ================================================================================================ #
#                                              LAYOUT                                              #
# ================================================================================================ #
layout = dmc.Stack(
    [
        dbc.Row(
            [
                dbc.Col(
                    dmc.NumberInput(
                        label="Linha",
                        placeholder="Digite a linha",
                        id="input-line",
                        min=1,
                        max=15,
                        step=1,
                    ),
                    md=3,
                ),
                dbc.Col(
                    dmc.Select(
                        label="Maquina ID",
                        placeholder="Nº da Termoformadora",
                        id="select-machine",
                        data=[*termoformadoras],
                    ),
                    md=4,
                ),
                dbc.Col(
                    dmc.Select(
                        label="Motivo da Parada",
                        data=[*options.keys()],
                        placeholder="Selecione Motivo",
                        id="select-reason",
                    ),
                    md=5,
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dmc.Select(
                        label="Equipamento",
                        placeholder="Selecione o Equipamento",
                        id="select-equipment",
                    ),
                    md=6,
                ),
                dbc.Col(
                    dmc.Select(
                        label="Problema",
                        placeholder="Selecione o Problema",
                        id="select-problem",
                    ),
                    md=6,
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dmc.Select(
                        label="Causa ou Solução",
                        placeholder="Selecione a Causa/Solução",
                        id="select-cause",
                    ),
                    md=6,
                ),
                dbc.Col(
                    dmc.TextInput(
                        label="Número da OS",
                        placeholder="P/ Manutenção",
                        id="input-os",
                    ),
                ),
                dbc.Col(
                    dmc.TextInput(
                        label="Operador",
                        placeholder="Matrícula do Operador",
                        id="input-operator",
                    ),
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dmc.DateInput(
                        label="Data da Parada",
                        placeholder="Insira a data",
                        id="input-stop-date",
                        maxDate=datetime.date.today(),
                    ),
                    md=3,
                ),
                dbc.Col(
                    dmc.TimeInput(
                        label="Hora da Parada",
                        placeholder="Insira a hora",
                        id="input-stop-time",
                    ),
                    md=3,
                ),
                dmc.NotificationProvider(position="top-right"),
                dbc.Col(
                    [
                        dmc.Button(
                            "Inserir Parada",
                            color="green",
                            variant="light",
                            id="button-insert-stop",
                        ),
                        html.Div(id="notification-insert-stop"),
                    ],
                    align="end",
                    class_name="d-flex justify-content-end",
                ),
            ]
        ),
    ],
)

# ================================================================================================ #
#                                             CALLBACKS                                            #
# ================================================================================================ #


# Equipamento
@callback(
    Output("select-equipment", "data"),
    Input("select-reason", "value"),
)
def update_equipment(reason):
    """
    Update the equipment based on the given reason.

    Args:
        reason (str): The reason for the equipment update.

    Returns:
        list: A list of equipment options based on the given reason.
    """
    if reason is None:
        return []

    return list(options[reason])


# Problema
@callback(
    Output("select-problem", "data"),
    Input("select-reason", "value"),
    Input("select-equipment", "value"),
)
def update_problem(reason, equipment):
    """
    Update the problem based on the given reason and equipment.

    Args:
        reason (str): The reason for the problem update.
        equipment (str): The equipment for the problem update.

    Returns:
        list: A list of problem options based on the given reason and equipment.
    """
    if reason is None or equipment is None:
        return []

    return list(options[reason][equipment])


# Causa ou Solução
@callback(
    Output("select-cause", "data"),
    Input("select-reason", "value"),
    Input("select-equipment", "value"),
    Input("select-problem", "value"),
)
def update_cause(reason, equipment, problem):
    """
    Update the cause based on the given reason, equipment and problem.

    Args:
        reason (str): The reason for the cause update.
        equipment (str): The equipment for the cause update.
        problem (str): The problem for the cause update.

    Returns:
        list: A list of cause options based on the given reason, equipment and problem.
    """
    if reason is None or equipment is None or problem is None:
        return []

    return list(options[reason][equipment][problem])


# ============================================ Button ============================================ #
@callback(
    Output("notification-insert-stop", "children"),
    Output("input-line", "value"),
    Output("select-machine", "value"),
    Output("select-reason", "value"),
    Output("select-equipment", "value"),
    Output("select-problem", "value"),
    Output("select-cause", "value"),
    Output("input-os", "value"),
    Output("input-operator", "value"),
    Output("input-stop-date", "value"),
    Output("input-stop-time", "value"),
    Input("button-insert-stop", "n_clicks"),
    State("input-line", "value"),
    State("select-machine", "value"),
    State("select-reason", "value"),
    State("select-equipment", "value"),
    State("select-problem", "value"),
    State("select-cause", "value"),
    State("input-os", "value"),
    State("input-operator", "value"),
    State("input-stop-date", "value"),
    State("input-stop-time", "value"),
    prevent_initial_call=True,
)
def insert_stop(
    _n_clicks, line, machine, reason, equipment, problem, cause, os, operator, date, time
):
    """
    Insert a stop based on the given information.

    Args:
        n_clicks (int): The number of times the button was clicked.

    Returns:
        str: A message indicating the success or failure of the operation.
    """
    if not ctx.triggered:
        raise PreventUpdate

    notification_ok = (
        dmc.Notification(
            title="Parada Inserida",
            message="A parada foi inserida com sucesso!",
            icon=DashIconify(icon="mdi:check-circle"),
            id="notification-insert",
            intent="show",
        ),
    )

    notification_nok = (
        dmc.Notification(
            title="Erro ao Inserir Parada",
            message="Preencha todos os campos!",
            icon=DashIconify(icon="mdi:alert-circle"),
            id="notification-insert",
            intent="show",
        ),
    )

    if not all([line, machine, reason, equipment, problem, cause, operator, date, time]):
        return (
            notification_nok,
            line,
            machine,
            reason,
            equipment,
            problem,
            cause,
            os,
            operator,
            date,
            time,
        )

    try:
        insert_data(
            [
                line,
                machine,
                reason,
                equipment,
                problem,
                cause,
                os,
                operator,
                date,
                time,
            ]
        )
    # pylint: disable=broad-except
    except Exception as e:
        print(f"Erro ao inserir parada: {e}")
        return (
            dmc.Notification(
                title="Erro ao Inserir Parada",
                message="Erro ao inserir a parada!",
                icon=DashIconify(icon="mdi:alert-circle"),
                id="notification-insert",
                intent="show",
            ),
            line,
            machine,
            reason,
            equipment,
            problem,
            cause,
            os,
            operator,
            date,
            time,
        )

    return notification_ok, "", None, None, None, None, None, "", "", None, ""


@callback(
    Output("notification-insert", "intent"),
    Input("insert-stop-modal", "opened"),
    prevent_initial_call=True,
)
def reset_notification(is_open):
    """
    Resets the notification based on the value of `is_open`.

    Args:
        is_open (bool): Indicates whether the notification is open or not.

    Returns:
        str: The result of the reset operation. Returns "clean" if `is_open` is False.

    """
    if not is_open:
        return "clean"
