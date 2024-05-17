"""
Modulo que faz a conexão com o banco de dados local e executa consultas SQL.
Usa sqlite3 para se conectar ao banco de dados e pandas para manipular os dados.
"""

import sqlite3

import pandas as pd
from helpers.path_config import DB_LOCAL


class ConnectionLocal:
    def __init__(self):
        self._db = DB_LOCAL
        self._conn = None

    def __enter__(self):
        self._conn = sqlite3.connect(self._db)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._conn.close()

    def get_query(self, query: str):
        """
        Executa a consulta SQL fornecida e retorna o resultado como um pandas DataFrame.

        Args:
            query (str): A consulta SQL a ser executada.

        Returns:
            pandas.DataFrame: O resultado da consulta como um DataFrame.
        """
        return pd.read_sql_query(query, self._conn)

    def save_df(self, df: pd.DataFrame, table_name: str):
        """
        Salva um DataFrame em uma tabela do banco de dados.

        Parâmetros:
        - df: DataFrame a ser salvo.
        - table_name: Nome da tabela onde o DataFrame será salvo.
        """
        df.to_sql(table_name, self._conn, if_exists="replace", index=False)

    def update_db(self, df: pd.DataFrame, table_name: str):
        """
        Atualiza o banco de dados com os dados do DataFrame fornecido.
        Atualiza por fazer append dos dados. Não substitui os dados existentes.

        Args:
            df (pd.DataFrame): O DataFrame contendo os dados a serem atualizados no banco de dados.
            table_name (str): O nome da tabela no banco de dados onde os dados serão atualizados.

        Returns:
            None
        """
        df.to_sql(table_name, self._conn, if_exists="append", index=False)
