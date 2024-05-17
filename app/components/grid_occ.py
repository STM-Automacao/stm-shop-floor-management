"""
Module for creating a grid with occurrence data based on provided data.
"""

import dash_ag_grid as dag
import pandas as pd
from helpers.my_types import IndicatorType, TemplateType
from service.df_for_indicators import DFIndicators


class GridOcc:
    """
    Represents a grid for displaying occurrence data.

    Attributes:
        None

    Methods:
        create_grid_occ(df, indicator, turn, date_picker):
        Create an AgGrid object with specified columns and data.
    """

    def __init__(self, df_maq_stopped: pd.DataFrame, df_production: pd.DataFrame):
        self.df_indicator = DFIndicators(df_maq_stopped, df_production)

    def create_grid_occ(
        self,
        dataframe: pd.DataFrame,
        indicator: IndicatorType,
        turn: str,
        theme: TemplateType,
        selected_date: str = None,
    ) -> dag.AgGrid:
        """
        Create an AgGrid object with specified data and column definitions.

        Args:
            dataframe (pd.Dataframe): The input dataframe containing the data.
            indicator (IndicatorType): The type of indicator.
            turn (str): The turn value.
            selected_date (str): The selected date.

        Returns:
            dag.AgGrid: The AgGrid object with the specified data and column definitions.
        """

        # Garantir que data registro é pd.datetime apenas com a data
        dataframe["data_registro"] = pd.to_datetime(dataframe["data_registro"]).dt.date

        # Filtrar pela data selecionada
        dataframe = (
            dataframe[(dataframe["data_registro"]) == pd.to_datetime(selected_date).date()]
            if selected_date
            else dataframe
        )

        # Ajustar dataframe
        df = self.df_indicator.adjust_df_for_bar_lost(dataframe, indicator, turn)

        # Ordenar por linha e data_hora_registro
        df = df.sort_values(by=["linha", "data_hora"])

        columns_defaults = {"sortable": True, "resizable": True, "flex": 1}

        number_columns = {
            "cellClass": "center-aligned-cell",
            "headerClass": "center-aligned-header",
            "cellDataType": "number",
            "filter": "agNumberColumnFilter",
            "filterParams": {"buttons": ["apply", "reset"], "closeOnApply": "true"},
        }

        filter_columns = {
            "cellDataType": "string",
            "filter": True,
            "filterParams": {"buttons": ["apply", "reset"], "closeOnApply": "true"},
        }

        columns_defs = [
            {"field": "fabrica", "headerName": "Fábrica", **number_columns},
            {"field": "linha", "headerName": "Linha", **number_columns},
            {"field": "maquina_id", "headerName": "Máquina", "cellDataType": "string"},
            {"field": "motivo", "headerName": "Motivo", **filter_columns},
            {"field": "equipamento", "headerName": "Equipamento", **filter_columns},
            {
                "field": "problema",
                "headerName": "Problema",
                "tooltipField": "problema",
                **filter_columns,
            },
            {
                "field": "causa",
                "headerName": "Causa",
                "tooltipField": "causa",
                **filter_columns,
            },
            {"field": "os_numero", "headerName": "Número OS", **filter_columns},
            {"field": "tempo", "headerName": "Tempo Parada", **number_columns},
            {"field": "desconto", "headerName": "Tempo descontado", **number_columns},
            {"field": "excedente", "headerName": "Tempo que afeta", **number_columns},
            {
                "field": "data_hora",
                "headerName": "Início",
                "tooltipField": "data_hora",
            },
            {
                "field": "data_hora_final",
                "headerName": "Fim",
                "tooltipField": "data_hora_final",
            },
        ]

        return dag.AgGrid(
            id=f"grid-occ-{indicator.value}",
            defaultColDef=columns_defaults,
            columnDefs=columns_defs,
            rowData=df.to_dict("records"),
            columnSize="responsiveSizeToFit",
            dashGridOptions={"pagination": "true", "paginationAutoPageSize": "true"},
            style={"height": "600px"},
            className="ag-theme-quartz" if theme else "ag-theme-alpine-dark",
        )
