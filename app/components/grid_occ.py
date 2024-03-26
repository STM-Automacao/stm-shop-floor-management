"""
Module for creating a grid with occurrence data based on provided data.
"""

import dash_ag_grid as dag
import pandas as pd
from helpers.types import IndicatorType, TemplateType
from service.times_data import TimesData


class GridOcc:
    """
    Represents a grid for displaying occurrence data.

    Attributes:
        None

    Methods:
        create_grid_occ(df, indicator, turn, date_picker):
        Create an AgGrid object with specified columns and data.
    """

    def __init__(self):
        self.times_data = TimesData()

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

        work = pd.DataFrame() if selected_date else None

        # Ajustar dataframe
        df = self.times_data.adjust_df_for_bar_lost(dataframe, indicator, turn, work)

        # Filtrar pela data selecionada
        df = (
            df[df["data_registro"] == pd.to_datetime(selected_date).date()] if selected_date else df
        )

        # Ordenar por linha e data_hora_registro
        df = df.sort_values(by=["linha", "data_hora_registro"])

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
            {"field": "motivo_nome", "headerName": "Motivo", **filter_columns},
            {
                "field": "problema",
                "headerName": "Problema",
                "tooltipField": "problema",
                **filter_columns,
            },
            {"field": "tempo_registro_min", "headerName": "Tempo Parada", **number_columns},
            {"field": "desconto_min", "headerName": "Tempo descontado", **number_columns},
            {"field": "excedente", "headerName": "Tempo que afeta", **number_columns},
            {"field": "data_hora_registro", "headerName": "Início"},
            {"field": "data_hora_final", "headerName": "Fim"},
        ]

        return dag.AgGrid(
            id=f"grid-occ-{indicator.value}",
            defaultColDef=columns_defaults,
            columnDefs=columns_defs,
            rowData=df.to_dict("records"),
            columnSize="responsiveSizeToFit",
            dashGridOptions={"pagination": "true", "paginationAutoPageSize": "true"},
            style={"height": "600px"},
            className="ag-theme-quartz" if theme else "ag-theme-quartz-dark",
        )
