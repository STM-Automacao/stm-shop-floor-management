"""
Módulo com a classe HistoryComponents, que é responsável por criar os componentes de histórico.
"""

import dash_mantine_components as dmc


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
