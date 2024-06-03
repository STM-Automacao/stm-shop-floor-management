"""
@Author: Bruno Tomaz
@Data: 31/01/2024

Este módulo cria um cache para armazenar os dados do banco de dados.
"""

import json
from threading import Lock

import numpy as np
import pandas as pd
from database.get_data import GetData
from flask_caching import Cache
from helpers.my_types import IndicatorType
from helpers.path_config import DF_CAIXAS
from service.data_analysis import DataAnalysis
from service.df_for_indicators import DFIndicators


class MyEncoder(json.JSONEncoder):
    """
    Classe que codifica objetos para JSON.
    """

    def default(self, o):
        # if isinstance(o, np.int64) or isinstance(o, np.int32):
        if isinstance(o, (np.int64, np.int32)):
            return int(o)
        return super(MyEncoder, self).default(o)


class CacheManager:
    """
    Classe responsável por gerenciar o cache da aplicação.
    """

    def __init__(self, app):
        self.cache = Cache(
            app.server,
            config={
                "CACHE_TYPE": "filesystem",
                "CACHE_DIR": "cache-directory",
                "CACHE_THRESHOLD": 50,
                "CACHE_DEFAULT_TIMEOUT": 610,
            },
        )

    def _tuple_to_list(self, df_tuple: tuple) -> list:
        """
        Função que transforma um tuple de DataFrames em uma lista de strings JSON.

        Args:
            df_tuple (tuple): O tuple contendo os DataFrames a serem transformados.

        Returns:
            list: A lista de strings JSON resultante da transformação.
        """
        return [df.to_json(date_format="iso", orient="split") for df in df_tuple]

    def _tuple_list_to_list(self, tuple_list: tuple) -> list[str]:
        """
        Função que transforma um tuple de listas de Dict em uma lista de strings JSON.

        Args:
            tuple_list (tuple): O tuple contendo as listas de Dict a serem transformadas.

        Returns:
            list[str]: A lista de strings JSON resultante da transformação.
        """
        return [json.dumps(lst, cls=MyEncoder) for lst in tuple_list]


class MainDataCache(CacheManager):
    """
    Classe responsável por gerenciar o cache dos dados principais da aplicação.

    Attributes:
        app: Instância da aplicação Flask.

    Methods:
        __init__(self, app): Construtor da classe MainDataCache.
        cache_daily_data(self): Salva o total de caixas à 00:00 em um arquivo CSV.
        update_cache(self): Atualiza o cache com os dados do banco de dados.
    """

    def __init__(self, app):
        """
        Construtor da classe MainDataCache.

        Args:
            app: Instância da aplicação Flask.
        """
        self.__get_data = GetData()
        self.__lock = Lock()
        super().__init__(app)

    def cache_daily_data(self):
        """
        Salva o total de caixas à 00:00 em um arquivo CSV.
        """
        with self.__lock:
            df_caixas_cf_tot = self.__get_data.get_protheus_total_caixas()
            df_caixas_cf_tot["QTD"] = df_caixas_cf_tot["QTD"].astype(int)
            df_caixas_cf_tot.to_csv(DF_CAIXAS, index=True)

    def update_cache(self):
        """
        Função que atualiza o cache com os dados do banco de dados.
        Agiliza o carregamento dos dados na aplicação.
        """
        with self.__lock:
            df1, df2, df_working_time, df_info_pure = self.__get_data.get_cleaned_data()
            df_caixas_cf = self.__get_data.get_protheus_caixas_data()
            df_caixas_cf_tot = pd.read_csv(DF_CAIXAS, index_col=0)

            # Criar dataframes auxiliares com os df do banco de dados
            df_ind = DFIndicators(df1, df2)
            analysis = DataAnalysis(df1, df2)
            df_eff = analysis.get_eff_data()
            df_perf = analysis.get_perf_data()
            df_repair = analysis.get_repair_data()
            df_eff_heatmap_tuple = df_ind.get_heatmap_data(IndicatorType.EFFICIENCY)
            annotations_eff_list_tuple = df_ind.get_annotations(IndicatorType.EFFICIENCY)
            df_perf_heatmap_tuple = df_ind.get_heatmap_data(IndicatorType.PERFORMANCE)
            annotations_perf_list_tuple = df_ind.get_annotations(IndicatorType.PERFORMANCE)
            df_repair_heatmap_tuple = df_ind.get_heatmap_data(IndicatorType.REPAIR)
            annotations_repair_list_tuple = df_ind.get_annotations(IndicatorType.REPAIR)

            # Atualizar o cache
            self.cache.set("df1", df1.to_json(date_format="iso", orient="split"))
            self.cache.set("df2", df2.to_json(date_format="iso", orient="split"))
            self.cache.set("df_info_pure", df_info_pure.to_json(date_format="iso", orient="split"))

            self.cache.set(
                "df_working_time", df_working_time.to_json(date_format="iso", orient="split")
            )
            self.cache.set("df_caixas_cf", df_caixas_cf.to_json(date_format="iso", orient="split"))
            self.cache.set(
                "df_caixas_cf_tot", df_caixas_cf_tot.to_json(date_format="iso", orient="split")
            )

            self.cache.set("df_eff", df_eff.to_json(date_format="iso", orient="split"))
            self.cache.set("df_perf", df_perf.to_json(date_format="iso", orient="split"))
            self.cache.set("df_repair", df_repair.to_json(date_format="iso", orient="split"))

            self.cache.set(
                "df_eff_heatmap_tuple", json.dumps(self._tuple_to_list(df_eff_heatmap_tuple))
            )
            self.cache.set(
                "annotations_eff_list_tuple",
                json.dumps(self._tuple_list_to_list(annotations_eff_list_tuple)),
            )
            self.cache.set(
                "df_perf_heatmap_tuple", json.dumps(self._tuple_to_list(df_perf_heatmap_tuple))
            )
            self.cache.set(
                "annotations_perf_list_tuple",
                json.dumps(self._tuple_list_to_list(annotations_perf_list_tuple)),
            )
            self.cache.set(
                "df_repair_heatmap_tuple", json.dumps(self._tuple_to_list(df_repair_heatmap_tuple))
            )
            self.cache.set(
                "annotations_repair_list_tuple",
                json.dumps(self._tuple_list_to_list(annotations_repair_list_tuple)),
            )
