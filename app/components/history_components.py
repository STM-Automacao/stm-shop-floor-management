"""
Módulo com a classe HistoryComponents, que é responsável por criar os componentes de histórico.
"""

import dash_mantine_components as dmc
import pandas as pd
from dash_iconify import DashIconify


class HistoryComponents:
    """
    Classe responsável por criar componentes relacionados ao histórico.

    Métodos:
        create_btn_segmented: Cria um botão segmentado.
        create_date_picker: Cria um componente de seleção de data.
        create_multiselect: Cria um componente de seleção múltipla.
    """

    def __init__(self) -> None:
        pass

    def create_btn_segmented(self, btn_id: str, data: list, value: str) -> dmc.SegmentedControl:
        """
        Cria um botão segmentado.

        Args:
            btn_id (str): O ID do botão segmentado.
            data (list): Os dados para preencher o botão segmentado.
            value (str): O valor inicial do botão segmentado.

        Returns:
            dmc.SegmentedControl: O botão segmentado criado.
        """

        return dmc.SegmentedControl(
            id=btn_id,
            data=data,
            value=value,
            w="85%",
        )

    def create_date_picker(self, picker_id: str, months: int = 6) -> dmc.DatePicker:
        """
        Cria um componente de seleção de data. Múltiplos dias podem ser selecionados.

        Args:
            picker_id (str): O ID do componente.
            months (int, optional): O número de meses para retroceder a data mínima. O padrão é 6.

        Returns:
            dmc.DatePicker: O componente de seleção de data criado.
        """

        now = pd.Timestamp.now()

        return dmc.DatePicker(
            id=picker_id,
            placeholder="Selecione a(s) data(s)",
            valueFormat="dddd - D MMM, YYYY",
            firstDayOfWeek=0,
            clearable=True,
            variant="filled",
            leftSection=DashIconify(icon="uiw:date"),
            minDate=now.replace(day=1) - pd.DateOffset(months=months),
            maxDate=pd.to_datetime(now - pd.DateOffset(days=1)).date(),
            type="multiple",
            w="85%",
        )

    def create_multiselect(self, select_id: str) -> dmc.MultiSelect:
        """
        Cria um componente de seleção múltipla. Contém as linhas das fábricas 1 e 2.

        Args:
            select_id (str): O ID do componente de seleção múltipla.

        Returns:
            dmc.MultiSelect: O componente de seleção múltipla criado.
        """

        return dmc.MultiSelect(
            id=select_id,
            data=[
                {
                    "group": "Fabrica 1",
                    "items": [
                        {"label": f"Linha {line}", "value": str(line)}
                        for line in list(range(1, 10))
                    ],
                },
                {
                    "group": "Fabrica 2",
                    "items": [
                        {"label": f"Linha {line}", "value": str(line)}
                        for line in list(range(10, 15))
                    ],
                },
            ],
            hidePickedOptions=True,
            clearable=True,
            placeholder="Selecione a(s) linha(s)",
            w="85%",
        )
