"""
Author: Bruno Tomaz
Date: 06/01/2024
Módulo que contém a classe Read.
Responsável por ler os dados do banco de dados e retornar um dataframe pandas.
"""

# cSpell: words automacao
import pandas as pd

# pylint: disable=import-error
from database.connection import Connection


class Read(Connection):
    """
    Class Read
    Read data from the database and return a pandas dataframe
    Create query to be executed in the database
    """

    # pylint: disable=useless-super-delegation
    def __init__(self):
        """
        Constructor
        """
        super().__init__()

    def get_automacao_data(self, query: str) -> pd.DataFrame:
        """
        Get data from database AUTOMACAO and return a pandas dataframe.

        Parameters
        ----------
        query : str
            Query to be executed in the database

        Returns
        -------
        pandas dataframe
            Dataframe with the query result
        """
        connection = None
        try:
            connection = self.get_connection_automacao()
            data = pd.read_sql(query, connection)
            return data
        # pylint: disable=broad-except
        except Exception as e:
            print(f"Erro ao buscar dados: {e}")
            return None
        finally:
            if connection:
                connection.dispose()

    def create_automacao_query(self, table: str, where: str = None, orderby: str = None) -> str:
        """
        Create query to be executed in the database AUTOMACAO.

        Parameters
        ----------
        table : str
            Table name
        where : str
            Where clause (optional)
        orderby : str
            Order by clause (optional)

        Returns
        -------
        str
            Query to be executed in the database
        """
        query = f"SELECT * FROM AUTOMACAO.dbo.{table}"

        if where:
            query += f" WHERE {where}"

        if orderby:
            query += f" ORDER BY {orderby}"

        return query

    def get_totvsdb_data(self, query: str) -> pd.DataFrame:
        """
        Retrieves data from the TotvsDB database using the provided SQL query.

        Args:
            query (str): The SQL query to execute.

        Returns:
            pd.DataFrame: A pandas DataFrame containing the retrieved data.

        Raises:
            Exception: If an error occurs while retrieving the data.

        """
        connection = None
        try:
            connection = self.get_connection_totvsdb()
            data = pd.read_sql(query, connection)
            return data
        # pylint: disable=broad-except
        except Exception as e:
            print(f"Erro ao buscar dados: {e}")
            return None
        finally:
            if connection:
                connection.dispose()

    def create_totvsdb_query(
        self, select: str, table: str, join: str = None, where: str = None, orderby: str = None
    ) -> str:
        """
        Creates a SQL query string for querying the TOTVS database.

        Args:
            select (str): The SELECT clause of the query.
            table (str): The table name to query.
            join (str, optional): The JOIN clause of the query. Defaults to None.
            where (str, optional): The WHERE clause of the query. Defaults to None.
            orderby (str, optional): The ORDER BY clause of the query. Defaults to None.

        Returns:
            str: The SQL query string.
        """
        query = f"SELECT {select} FROM {table}"

        if join:
            query += f" {join}"

        if where:
            query += f" WHERE {where}"

        if orderby:
            query += f" ORDER BY {orderby}"

        return query
