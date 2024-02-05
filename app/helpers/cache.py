import json
from threading import Lock

import numpy as np
import pandas as pd

# pylint: disable=E0401
from database.get_data import GetData
from flask_caching import Cache
from service.df_for_indicators import DFIndicators

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


def update_cache():
    """
    Função que atualiza o cache com os dados do banco de dados.
    Agiliza o carregamento dos dados na aplicação.
    """
    with lock:
        # Carregar os dados do banco de dados e criar os DataFrames
        df1, df2 = get_data.get_cleaned_data()
        df_ind = DFIndicators(df1, df2)
        df_eff = df_ind.get_eff_data()
        df_perf = df_ind.get_perf_data()
        df_repair = df_ind.get_repair_data()
        df_eff_heatmap = df_ind.get_eff_data_heatmap()
        df_eff_heatmap_tuple = df_ind.get_eff_data_heatmap_turn()
        annotations_eff_turn_list_tuple = df_ind.get_eff_annotations_turn()
        df_perf_repair_heat_tuple = df_ind.get_perf_repair_heatmap()
        annotations_list_tuple = df_ind.get_annotations()
        df_perf_heat_turn_tuple = df_ind.get_perf_heatmap_turn()
        df_repair_heat_turn_tuple = df_ind.get_repair_heatmap_turn()
        annotations_perf_turn_list_tuple = df_ind.get_perf_annotations_turn()
        annotations_repair_turn_list_tuple = df_ind.get_repair_annotations_turn()

        # Atualizar o cache
        cache.set("df1", df1.to_json(date_format="iso", orient="split"))
        cache.set("df2", df2.to_json(date_format="iso", orient="split"))
        cache.set("df_eff", df_eff.to_json(date_format="iso", orient="split"))
        cache.set("df_perf", df_perf.to_json(date_format="iso", orient="split"))
        cache.set("df_repair", df_repair.to_json(date_format="iso", orient="split"))
        cache.set("df_eff_heatmap", df_eff_heatmap.to_json(date_format="iso", orient="split"))
        cache.set("df_eff_heatmap_tuple", json.dumps(tuple_to_list(df_eff_heatmap_tuple)))
        cache.set(
            "annotations_eff_turn_list_tuple",
            json.dumps(tuple_list_to_list(annotations_eff_turn_list_tuple)),
        )
        cache.set("df_perf_repair_heat_tuple", json.dumps(tuple_to_list(df_perf_repair_heat_tuple)))
        cache.set("annotations_list_tuple", json.dumps(tuple_list_to_list(annotations_list_tuple)))
        cache.set(
            "df_perf_heat_turn_tuple",
            json.dumps(tuple_to_list(df_perf_heat_turn_tuple)),
        )
        cache.set(
            "df_repair_heat_turn_tuple",
            json.dumps(tuple_to_list(df_repair_heat_turn_tuple)),
        )
        cache.set(
            "annotations_perf_turn_list_tuple",
            json.dumps(tuple_list_to_list(annotations_perf_turn_list_tuple)),
        )
        cache.set(
            "annotations_repair_turn_list_tuple",
            json.dumps(tuple_list_to_list(annotations_repair_turn_list_tuple)),
        )

        print(f"========== Cache atualizado ==========  {pd.to_datetime('today')}")
