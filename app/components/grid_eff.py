"""
    Arquivo com a classe GridEff que cria o grid de eficiência
"""

import dash_ag_grid as dag
import pandas as pd
from helpers.my_types import TemplateType


class GridEff:
    """
    Classe responsável por criar uma grade de eficiência.

    Args:
        df (pd.DataFrame): O dataframe contendo os dados para exibir na grade.
        theme (TemplateType): O tema a ser aplicado na grade.

    Returns:
        dag.AgGrid: A grade de eficiência criada.
    """

    def __init__(self):
        pass

    def create_grid_eff(
        self,
        df: pd.DataFrame,
        theme: TemplateType,
    ) -> dag.AgGrid:
        """
        Cria uma grade de eficiência com base nos dados fornecidos.

        Args:
            df (pd.DataFrame): O dataframe contendo os dados para exibir na grade.
            theme (TemplateType): O tema a ser aplicado na grade.

        Returns:
            dag.AgGrid: A grade de eficiência criada.
        """

        # Defaults das colunas
        column_defaults = {"resizable": True, "sortable": True}

        # Colunas com números
        column_number = {
            "filter": "agNumberColumnFilter",
            "cellClass": "center-aligned-cell",
            "cellDataType": "number",
            "filterParams": {"buttons": ["apply", "reset"], "closeOnApply": "true"},
            "headerClass": "center-aligned-header",
        }

        # Garantir que data registro é pd.datetime apenas com a data
        df["data_registro"] = pd.to_datetime(df["data_registro"]).dt.date

        # Ajustar total produzido para int
        df.total_produzido = df.total_produzido.astype(int)

        # Ajustar eficiência
        df.eficiencia = (df.eficiencia * 100).round(2)

        # Definições de colunas
        columns_defs = [
            {"field": "fabrica", "headerName": "Fábrica", **column_number},
            {"field": "linha", "headerName": "Linha", **column_number},
            {"field": "maquina_id", "headerName": "Máquina", "cellDataType": "string"},
            {"field": "data_registro", "headerName": "Data", "cellDataType": "string"},
            {"field": "tempo", "headerName": "Tempo Parada", **column_number},
            {"field": "desconto", "headerName": "Tempo Descontado", **column_number},
            {"field": "tempo_esperado", "headerName": "Tempo Esperado", **column_number},
            {"field": "producao_esperada", "headerName": "Deveria Produzir", **column_number},
            {"field": "total_produzido", "headerName": "Produzido", **column_number},
            {"field": "eficiencia", "headerName": "Eficiência", **column_number},
        ]

        grid = dag.AgGrid(
            id="grid-eff-management",
            className="ag-theme-quartz" if theme else "ag-theme-alpine-dark",
            columnDefs=columns_defs,
            defaultColDef=column_defaults,
            rowData=df.to_dict("records"),
            columnSize="responsiveSizeToFit",
            dashGridOptions={"pagination": "true", "paginationAutoPageSize": "true"},
            style={"height": "700px"},
        )

        return grid

    def create_grid_history(self, df_history: pd.DataFrame, light_theme: bool) -> dag.AgGrid:

        # -------------------- Tabela de Desempenho Mensal -------------------- #

        # Transforma 415641 em 415.641
        df_history["total_caixas"] = df_history["total_caixas"].apply(
            lambda x: f"{x:,.0f} cxs".replace(",", ".")
        )
        # Transforma 0.56 em 56%
        df_history["eficiencia"] = df_history["eficiencia"] * 100
        df_history["performance"] = df_history["performance"] * 100
        df_history["reparo"] = df_history["reparo"] * 100
        # Transforma 56 em 56%
        df_history["eficiencia"] = df_history["eficiencia"].map(lambda x: f"{x:.0f}%")
        df_history["performance"] = df_history["performance"].map(lambda x: f"{x:.0f}%")
        df_history["reparo"] = df_history["reparo"].map(lambda x: f"{x:.0f}%")
        # Transforma 244502 em 244.502 min
        df_history["parada_programada"] = df_history["parada_programada"].apply(
            lambda x: f"{x:,.0f} min".replace(",", ".")
        )

        columns_def = [
            {"headerName": "Mês/Ano", "field": "data_registro"},
            {"headerName": "Produção Total", "field": "total_caixas"},
            {"headerName": "Eficiência", "field": "eficiencia"},
            {"headerName": "Performance", "field": "performance"},
            {"headerName": "Reparos", "field": "reparo"},
            {"headerName": "Parada Programada", "field": "parada_programada"},
        ]

        table = dag.AgGrid(
            className="ag-theme-quartz" if light_theme else "ag-theme-alpine-dark",
            columnDefs=columns_def,
            rowData=df_history.to_dict("records"),
            columnSize="responsiveSizeToFit",
            dashGridOptions={"pagination": True, "paginationAutoPageSize": True},
            style={"height": "600px"},
        )

        return table
