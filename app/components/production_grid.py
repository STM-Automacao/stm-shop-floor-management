"""
    Module for the production grid component
    - Autor: Bruno Tomaz
    - Data de criação: 23/01/2024
"""

import dash_ag_grid as dag
import pandas as pd


class ProductionGrid:
    """
    Represents a production grid.

    This class provides methods to create a production grid based on a given DataFrame and turn.

    Attributes:
        None

    Methods:
        create_production_grid: Creates a production grid based on the given DataFrame and turn.

    """

    def create_production_grid(self, df: pd.DataFrame, turn: str, theme) -> dag.AgGrid:
        """
        Creates a production grid based on the given DataFrame and turn.

        Args:
            df (pd.DataFrame): The DataFrame containing the production data.
            turn (str): The selected turn.

        Returns:
            ag.AgGrid: The created production grid.

        """
        # Selecionar o turno
        df = df[df["turno"] == turn] if turn != "TOT" else df

        # Altera a produção para caixas
        df.loc[:, "total_produzido"] = df["total_produzido"].apply(lambda x: x / 10).astype(int)

        # Ordenar por linha, data_registro
        df = df.sort_values(["linha", "data_registro"])

        # Manter apenas o dia da data_registro
        df["dia"] = pd.to_datetime(df["data_registro"], errors="coerce").dt.day

        # Pivotar a tabela
        df = df.pivot_table(
            index="dia",
            columns="linha",
            values="total_produzido",
            aggfunc="sum",
        )

        # Adicionar linha com o total
        df["Total"] = df.sum(axis=1)

        # Ajustar o index
        df = df.reset_index()

        # Definir lista de colunas
        columns = [
            {"field": str(x), "headerName": f"Linha {x}", "sortable": True, "resizable": True}
            for x in df.columns[1:-2]
        ]
        columns_def = [
            {
                "field": str(df.columns[0]),
                "headerName": df.columns[0].capitalize(),
                "sortable": True,
                "cellDataType": "number",
                "filter": "agNumberColumnFilter",
                # "floatingFilter": True,
            },
            *columns,
            {
                "field": str(df.columns[-1]),
                "headerName": "Total",
                "sortable": True,
                "resizable": True,
                "cellDataType": "number",
            },
        ]

        # Criar o grid
        grid = dag.AgGrid(
            id="production-grid",
            columnDefs=columns_def,
            rowData=df.to_dict("records"),
            columnSize="responsiveSizeToFit",
            dashGridOptions={"pagination": False, "domLayout": "autoHeight"},
            style={"height": None},
            className="ag-theme-quartz" if theme else "ag-theme-quartz-dark",
        )

        return grid
