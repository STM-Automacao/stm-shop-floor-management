"""
Autor: Bruno Tomaz
Data: 25/01/2024
Módulo que contém o layout e as funções de callback do Modal de Reparos.
"""

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

# pylint: disable=E0401
from service.times_data import TimesData

times_data = TimesData()

from app import app

# ========================================= Modal Layout ======================================== #

layout = [
    dbc.ModalHeader("Reparos por Turno", class_name="inter"),
    dbc.ModalBody(),
    dbc.ModalFooter(
        dmc.Image(
            # pylint: disable=E1101
            src=app.get_asset_url("Logo Horizontal_PXB.png"),
            width="125px",
            withPlaceholder=True,
        ),
    ),
]
