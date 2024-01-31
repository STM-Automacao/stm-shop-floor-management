"""
Autor: Bruno Tomaz
Data: 17/01/2024
Este módulo cria gauge do mês anterior.
"""
# pylint: disable=E0401
from database.get_data import GetData
from graphics.indicators import Indicators
from helpers.path_config import EFF_LAST, PERF_LAST, REPAIR_LAST
from service.times_data import TimesData


class LastMonthInd:
    """
    Essa classe é responsável por salvar imagens de gauge do mês anterior.
    """

    def __init__(self):
        self.times_data = TimesData()
        self.get_data = GetData()
        self.indicators = Indicators()

    def get_last_month_ind(self):
        """
        Salva imagens de gauge do mês anterior.
        """
        # Leitura dos dados
        df_info, df_prod = self.get_data.get_last_month_data()

        # Tratamento dos dados
        df_eff = self.times_data.get_eff_data(df_info, df_prod)
        df_perf = self.times_data.get_perf_data(df_info, df_prod)
        df_repair = self.times_data.get_repair_data(df_info, df_prod)

        print("========== Salvando dados Último Mês ==========")
        # Salva os dataframes em csv
        df_eff.to_csv(EFF_LAST)
        df_perf.to_csv(PERF_LAST)
        df_repair.to_csv(REPAIR_LAST)
