""" Módulo para criar um seletor de data."""

import dash_mantine_components as dmc
from dash_iconify import DashIconify


class DatePickerDMC:
    """
    Classe responsável por criar um seletor de data.

    Métodos:
        create_date_picker: Cria um seletor de data.
    """

    def __init__(self) -> None:
        pass

    def create_date_picker(self, picker_id: str) -> dmc.DatePicker:
        """
        Cria um seletor de data.

        Args:
            picker_id (str): O ID do seletor de data.

        Returns:
            dmc.DatePicker: O seletor de data criado.
        """

        return dmc.DatesProvider(
            dmc.DatePicker(
                id=picker_id,
                placeholder="Selecione uma data",
                valueFormat="dddd - D MMM, YYYY",
                firstDayOfWeek=0,
                clearable=True,
                variant="filled",
                leftSection=DashIconify(icon="uiw:date"),
                w="85%",
            ),
            settings={"locale": "pt-br"},
        )
