"""Módulo que contém as funções de inserção de dados no banco de dados."""

# cSpell: words automacao
from database.connection import Connection
from sqlalchemy.exc import DatabaseError


class Insert(Connection):
    """
    Class Insert
    Insert data into the database
    """

    # pylint: disable=useless-super-delegation
    def __init__(self):
        """
        Constructor
        """
        super().__init__()

    def insert_data(self, query: str) -> None:
        """
        Insert data into the database.

        Parameters
        ----------
        query : str
            Query to be executed in the database
        """
        connection = None
        try:
            connection = self.get_connection_automacao()
            connection.execute(query)
        except DatabaseError as e:
            print(f"Erro ao inserir dados: {e}")
        finally:
            if connection:
                connection.dispose()

    def create_insert_query(self, table: str, columns: list, values: list) -> str:
        """
        Create query to insert data into the database AUTOMACAO.

        Parameters
        ----------
        table : str
            Table name
        columns : list
            List of columns
        values : list
            List of values

        Returns
        -------
        str
            Query to be executed in the database
        """
        columns_str = ", ".join(columns)
        values_str = ", ".join([f"'{value}'" for value in values])
        query = f"INSERT INTO {table} ({columns_str}) VALUES ({values_str})"
        return query
