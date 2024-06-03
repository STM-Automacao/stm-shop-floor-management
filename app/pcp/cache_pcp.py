"""
Este módulo cria uma classe para armazenar os dados de massa do PCP.
"""

from helpers.cache import CacheManager
from pcp.analysis_pcp_data import AnalysisPcpData
from pcp.clean_pcp_data import CleanPcpData
from pcp.get_pcp_data import GetPcpData


class PcpDataCache(CacheManager):
    def __init__(self, app) -> None:
        self.__get_data = GetPcpData().get_massa_data
        self.__get_analysis = AnalysisPcpData()
        self.__clean_data = CleanPcpData().clean_massadas_data
        super().__init__(app)

    def cache_massa_data(self) -> None:

        # Lê os dados do banco de dados
        data = self.__get_data()

        # Limpa os dados
        data_cleaned = self.__clean_data(data)

        # Analisa os dados
        df_sum = self.__get_analysis.get_massa_sum(data_cleaned)
        df_week = self.__get_analysis.get_week_data(df_sum)

        # Salva os dados no cache
        self.cache.set("df_sum", df_sum.to_json(date_format="iso", orient="split"))
        self.cache.set("df_week", df_week.to_json(date_format="iso", orient="split"))
