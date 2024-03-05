"""
Module for bar lost chart component.
@Author: Bruno Tomaz
@Date: 04/03/2024
"""

import pandas as pd
from helpers.types import IndicatorType, TemplateType
from service.times_data import TimesData


class BarChartLost:

    def __init__(self):
        self.times_data = TimesData()

    def create_bar_chart_lost(self, dataframe: pd.DataFrame, indicator: IndicatorType, template: TemplateType, turn: str, working: pd.DataFrame = None):

        # Ajustar o dataframe
        df = self.times_data.adjust_df_for_bar_lost(dataframe, indicator, turn, working)

        # Turno Map
        turn_map = {
            "NOT": "Noturno",
            "MAT": "Matutino",
            "VES": "Vespertino",
            "TOT": "Total"
        }

        # Se motivo id for 3 e problema for nulo, preencher o problema
        df.loc[(df["motivo_id"] == 3) & (df["problema"].isnull()), "problema"] = "Refeição"

        # Preencher onde o problema é nulo
        df.loc[df["problema"].isnull(), "problema"] = "Problema não informado"

