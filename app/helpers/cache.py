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
from helpers.types import IndicatorType
from service.df_for_indicators import DFIndicators
from service.times_data import TimesData

from app import app

get_data = GetData()
lock = Lock()


class MyEncoder(json.JSONEncoder):
    """
    Classe que codifica objetos para JSON.
    """

    def default(self, o):
        if isinstance(o, np.int64) or isinstance(o, np.int32):
            return int(o)
        return super(MyEncoder, self).default(o)


cache = Cache(
    app.server,
    config={
        "CACHE_TYPE": "filesystem",
        "CACHE_DIR": "cache-directory",
        "CACHE_THRESHOLD": 50,
    },
)


def tuple_to_list(df_tuple: tuple) -> list:
    """
    Função que transforma um tuple de DataFrames em uma lista de strings JSON.
    """
    return [df.to_json(date_format="iso", orient="split") for df in df_tuple]


def tuple_list_to_list(tuple_list: tuple) -> list[str]:
    """
    Função que transforma um tuple de listas de Dict em uma lista de strings JSON.
    """
    return [json.dumps(lst, cls=MyEncoder) for lst in tuple_list]


def cache_daily_data():
    with lock:
        df_caixas_cf_tot = get_data.get_protheus_total_caixas()

        cache.set("df_caixas_cf_tot", df_caixas_cf_tot.to_json(date_format="iso", orient="split"))


def update_cache():
    """
    Função que atualiza o cache com os dados do banco de dados.
    Agiliza o carregamento dos dados na aplicação.
    """
    with lock:
        # Carregar os dados do banco de dados e criar os DataFrames
        df1, df2, df_working_time = get_data.get_cleaned_data()
        df_caixas_cf = get_data.get_protheus_caixas_data()
        df_ind = DFIndicators(df1, df2)
        times_data = TimesData()
        df_eff = times_data.get_eff_data(df1, df2)
        df_perf = times_data.get_perf_data(df1, df2)
        df_repair = times_data.get_repair_data(df1, df2)
        df_eff_heatmap_tuple = df_ind.get_heatmap_data(IndicatorType.EFFICIENCY)
        annotations_eff_list_tuple = df_ind.get_annotations(IndicatorType.EFFICIENCY)
        df_perf_heatmap_tuple = df_ind.get_heatmap_data(IndicatorType.PERFORMANCE)
        annotations_perf_list_tuple = df_ind.get_annotations(IndicatorType.PERFORMANCE)
        df_repair_heatmap_tuple = df_ind.get_heatmap_data(IndicatorType.REPAIR)
        annotations_repair_list_tuple = df_ind.get_annotations(IndicatorType.REPAIR)

        # Atualizar o cache
        cache.set("df1", df1.to_json(date_format="iso", orient="split"))
        cache.set("df2", df2.to_json(date_format="iso", orient="split"))

        cache.set("df_working_time", df_working_time.to_json(date_format="iso", orient="split"))
        cache.set("df_caixas_cf", df_caixas_cf.to_json(date_format="iso", orient="split"))

        cache.set("df_eff", df_eff.to_json(date_format="iso", orient="split"))
        cache.set("df_perf", df_perf.to_json(date_format="iso", orient="split"))
        cache.set("df_repair", df_repair.to_json(date_format="iso", orient="split"))

        cache.set("df_eff_heatmap_tuple", json.dumps(tuple_to_list(df_eff_heatmap_tuple)))
        cache.set(
            "annotations_eff_list_tuple",
            json.dumps(tuple_list_to_list(annotations_eff_list_tuple)),
        )
        cache.set("df_perf_heatmap_tuple", json.dumps(tuple_to_list(df_perf_heatmap_tuple)))
        cache.set(
            "annotations_perf_list_tuple",
            json.dumps(tuple_list_to_list(annotations_perf_list_tuple)),
        )
        cache.set("df_repair_heatmap_tuple", json.dumps(tuple_to_list(df_repair_heatmap_tuple)))
        cache.set(
            "annotations_repair_list_tuple",
            json.dumps(tuple_list_to_list(annotations_repair_list_tuple)),
        )

        print(f"========== Cache atualizado ==========  {pd.to_datetime('today')}")
