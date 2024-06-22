"""
Módulo para tratar e salvar no DB local os dados dos últimos 6 meses.
"""

import pandas as pd
from database.connection_local import ConnectionLocal
from database.get_data import GetData
from service.clean_data import CleanData
from service.join_data import JoinData
from service.service_info_ihm import ServiceInfoIHM


class BigData:
    """
    Classe responsável por lidar com os dados grandes.

    Essa classe possui métodos para análise, salvamento e obtenção de dados grandes.
    """

    def __init__(self) -> None:
        self._get_data = GetData()

    def _analysis_data(self) -> pd.Series:
        """
        Realiza a análise dos dados.

        Retorna um objeto pd.Series contendo os dados de paradas das máquinas.
        """

        # Leitura dos dados
        df_ihm, df_info = self._get_data.get_big_data()

        # Limpeza dos dados
        df_ihm, df_info, _, _ = CleanData(df_ihm, df_info).clean_data()

        # Une os DataFrames
        df = JoinData(df_ihm, df_info).join_data()

        service = ServiceInfoIHM(df)

        df = service.get_info_ihm_adjusted()

        df_stops = service.get_maq_stopped(df)

        return df_stops

    def save_big_data(self) -> None:
        """
        Salva os dados tratados em um banco de dados local.

        Return
            None
        """

        # Dataframe com os dados tratados
        df_stops = self._analysis_data()

        # Cria conexão com DB local. Se não existir cria um.
        with ConnectionLocal() as conn:
            # Salva os dados no DB
            conn.save_df(df_stops, "big_data")

    def get_big_data(self) -> pd.DataFrame:
        """
        Obtém os dados do banco de dados local.

        Retorna um DataFrame contendo os dados da tabela 'big_data'.

        Returns:
            pd.DataFrame: DataFrame contendo os dados da tabela 'big_data'.
        """

        # Cria conexão com DB local. Se não existir cria um.
        with ConnectionLocal() as conn:
            # Lê os dados do DB
            df = conn.get_query("SELECT * FROM big_data")

        return df
