"""Módulo para criar botões segmentados."""

import dash_mantine_components as dmc


class SegmentedBtn:
    """
    Classe responsável por criar botões segmentados.

    Métodos:
        create_segmented_btn: Cria um botão segmentado.
    """

    def __init__(self) -> None:
        pass

    def create_segmented_btn(self, btn_id: str, data: list, value: str) -> dmc.SegmentedControl:
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
