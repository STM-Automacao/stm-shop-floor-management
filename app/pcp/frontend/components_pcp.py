"""
Módulo para criar o grid do pcp
"""

import dash_ag_grid as dag
import pandas as pd


class ComponentsPcpBuilder:
    """
    Classe responsável por criar um grid do PCP.
    """

    def __init__(self):
        pass

    def create_grid_pcp(
        self, df: pd.DataFrame, grid_id: int, theme: bool, defs: dict = None
    ) -> dag.AgGrid:
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

        cols_defs = (
            [{"field": col, "headerTooltip": col} for col in df.columns] if defs is None else defs
        )

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
