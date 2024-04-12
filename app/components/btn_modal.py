"""
Este módulo cria um grupo de botões para girar o modal.
"""

import dash_bootstrap_components as dbc

# pylint: disable=E0401
from helpers.types import MODAL_RADIO, IndicatorType

# cSpell: words eficiencia


def create_btn_opt_modal(modal):
    """
    Cria um grupo de botões para girar o modal.

    Parâmetros:
    - modal: O identificador do modal.

    Retorna:
    - dbc.ButtonGroup: O componente de grupo de botões.
    """
    return dbc.ButtonGroup(
        [
            dbc.Button(
                "Histórico",
                id=f"history-button-{modal}",
                className="mb-3",
                outline=True,
                color="secondary",
                n_clicks=0,
            ),
            dbc.Button(
                "Produção",
                id=f"production-btn-{modal}",
                className="mb-3",
                outline=True,
                active=False,
                color="secondary",
                n_clicks=0,
            ),
            dbc.Button(
                "Detalhes",
                id=f"details-button-{modal}",
                className="mb-3",
                outline=True,
                active=False,
                color="secondary",
                n_clicks=0,
            ),
        ]
    )


btn_opt_eff = create_btn_opt_modal(IndicatorType.EFFICIENCY.value)
btn_opt_perf = create_btn_opt_modal(IndicatorType.PERFORMANCE.value)
btn_opt_repair = create_btn_opt_modal(IndicatorType.REPAIR.value)


def create_btn_opt():
    """
    Creates a button group with two buttons: "Histórico" and "Estoque".

    Returns:
        dbc.ButtonGroup: A button group containing the two buttons.
    """
    return dbc.ButtonGroup(
        [
            dbc.Button(
                "Histórico",
                id="history-btn",
                className="mb-3",
                outline=True,
                color="secondary",
                n_clicks=0,
            ),
            dbc.Button(
                "Estoque",
                id="estoque-btn",
                className="mb-3",
                outline=True,
                active=False,
                color="secondary",
                n_clicks=0,
            ),
        ]
    )


btn_opt = create_btn_opt()


def create_radio_btn_turn(modal):
    """
    Cria um grupo de botões de rádio para selecionar o turno.

    Retorna:
    - dbc.RadioItems: O componente de grupo de botões de rádio.
    """
    return (
        dbc.RadioItems(
            id=f"radio-items-{modal}",
            options=[{"label": l, "value": v} for v, l, _ in MODAL_RADIO],
            value="MAT",
            className="inter btn-group",
            inputClassName="btn-check",
            labelClassName="btn btn-outline-secondary",
            labelCheckedClassName="active",
        ),
    )


radio_btn_eff = create_radio_btn_turn(IndicatorType.EFFICIENCY.value)
radio_btn_perf = create_radio_btn_turn(IndicatorType.PERFORMANCE.value)
radio_btn_repair = create_radio_btn_turn(IndicatorType.REPAIR.value)
