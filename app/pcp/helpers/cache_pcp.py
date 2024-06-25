"""
Este módulo cria uma classe para armazenar os dados de massa do PCP.
"""

from helpers.cache import CacheManager
from pcp.backend.analysis_pcp_data import AnalysisPcpData
from pcp.backend.clean_pcp_data import CleanPcpData
from pcp.backend.get_pcp_data import GetPcpData


class PcpDataCache(CacheManager):
    """
    Classe responsável por gerenciar o cache dos dados do PCP.

    Args:
        app: Instância da aplicação Flask.

    Attributes:
        __get_data: Método para obter os dados do PCP.
        __get_analysis: Instância da classe AnalysisPcpData para análise dos dados.
        __clean_data: Método para limpar os dados do PCP.

    Methods:
        cache_massa_data: Método para armazenar os dados do PCP no cache.
    """

    def __init__(self, app) -> None:
        self.__get_data = GetPcpData().get_massa_data
        self.__get_pasta_data = GetPcpData().get_pasta_data
        self.__get_analysis = AnalysisPcpData()
        self.__clean_data = CleanPcpData().clean_massadas_data
        self.__clean_pasta_data = CleanPcpData().clean_pasta_data
        super().__init__(app)

    def cache_massa_data(self) -> None:
        """
        Armazena os dados do PCP no cache.

        Steps:
        1. Obtém os dados do banco de dados.
        2. Limpa os dados obtidos.
        3. Realiza a análise dos dados.
        4. Salva os dados no cache.

        Returns:
            None
        """
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

    def cache_pasta_data(self) -> None:
        """
        Realiza o cache dos dados relacionados à pasta.

        Lê os dados do banco de dados, limpa os dados, analisa os dados e salva os dados no cache.

        Parâmetros:
        - self: A instância do objeto.

        Retorno:
        - None
        """

        # Lê os dados do banco de dados
        data = self.__get_pasta_data()

        # Limpa os dados
        data_cleaned = self.__clean_pasta_data(data)

        # Analisa os dados
        df_pasta = self.__get_analysis.get_pasta_analysis(data_cleaned)
        df_pasta_week = self.__get_analysis.get_pasta_week_analysis(df_pasta)

        # Salva os dados no cache
        self.cache.set("df_pasta", df_pasta.to_json(date_format="iso", orient="split"))
        self.cache.set("df_pasta_week", df_pasta_week.to_json(date_format="iso", orient="split"))
