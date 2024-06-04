"""
Módulo para criar o grid do pcp
"""

import dash_ag_grid as dag
import dash_mantine_components as dmc
import pandas as pd


class ComponentsPcpBuilder:
    """
    Classe responsável por criar um grid do PCP.
    """

    def __init__(self):
        pass

    def create_grid_pcp(self, df: pd.DataFrame, grid_id: int, theme: bool) -> dag.AgGrid:
        """
        Cria uma instância de dag.AgGrid com base nos parâmetros fornecidos.

        Args:
            df (pd.DataFrame): O DataFrame contendo os dados a serem exibidos no grid.
            grid_id (int): O ID do grid.
            theme (bool): Indica se o tema do grid será claro (True) ou escuro (False).

        Returns:
            dag.AgGrid: A instância de dag.AgGrid criada.
        """

        column_defaults = {
            "resizable": True,
            "sortable": True,
            "filter": True,
            "filterParams": {"buttons": ["apply", "reset"], "closeOnApply": "true"},
        }

        cols_defs = [{"field": col, "headerTooltip": col} for col in df.columns]

        grid = dag.AgGrid(
            id=f"grid-pcp-{grid_id}",
            className="ag-theme-quartz" if theme else "ag-theme-alpine-dark",
            columnDefs=cols_defs,
            defaultColDef=column_defaults,
            rowData=df.to_dict("records"),
            columnSize="responsiveSizeToFit",
            dashGridOptions={"pagination": True, "paginationAutoPageSize": "true"},
            style={"height": "500px"},
        )

        return grid

    def generate_segmented_btn(self, btn_id: str, data: list, value: str) -> dmc.SegmentedControl:
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
            id=f"segmented-btn-{btn_id}",
            data=data,
            value=value,
            w="85%",
        )
