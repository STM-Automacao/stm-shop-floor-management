"""
Módulo para criar o grid do pcp
"""

import dash_ag_grid as dag
import pandas as pd


class GridAgGrid:
    """
    Classe responsável por criar um grid do AgGrid.
    """

    def __init__(self):
        pass

    def create_grid_ag(
        self, df: pd.DataFrame, grid_id: int, theme: bool, defs: dict = None, hei: int = 500
    ) -> dag.AgGrid:
        """
        Cria uma instância de dag.AgGrid com base nos parâmetros fornecidos.

        Args:
            df (pd.DataFrame): O DataFrame contendo os dados a serem exibidos no grid.
            grid_id (int): O ID do grid.
            theme (bool): Indica se o tema do grid será claro (True) ou escuro (False).
            defs (dict, optional): As definições das colunas do grid. Defaults to None.
            hei (int, optional): A altura do grid. Defaults to 500.

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
            id=grid_id,
            className="ag-theme-quartz" if theme else "ag-theme-alpine-dark",
            columnDefs=cols_defs,
            defaultColDef=column_defaults,
            rowData=df.to_dict("records"),
            columnSize="responsiveSizeToFit",
            dashGridOptions={"pagination": True, "paginationAutoPageSize": "true"},
            style={"height": f"{hei}px"},
        )

        return grid
