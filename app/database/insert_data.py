"""
Módulo responsável por inserir dados no banco de dados. Usa o db_insert.py
"""

from database.db_insert import Insert


class InsertData:
    """
    Class InsertData
    Insert data into the database
    """

    def __init__(self):
        """
        Constructor
        """
        self.insert = Insert()

    def _insert_data(self, table: str, columns: list, values: list) -> None:
        """
        Insert data into the database.

        Parameters
        ----------
        table : str
            Table name
        columns : list
            List of columns
        values : list
            List of values
        """
        query = self.insert.create_insert_query(table, columns, values)
        self.insert.insert_data(query)

    def insert_maq_ihm_data(self, values: list) -> None:
        """
        Insert data into the maq_ihm table.

        Parameters
        ----------
        columns : list
            List of columns
        values : list
            List of values
        """
        table = "[AUTOMACAO].dbo.[maquina_ihm]"

        columns = [
            "linha",
            "maquina_id",
            "motivo",
            "equipamento",
            "problema",
            "causa",
            "os_numero",
            "operador_id",
            "data_registro",
            "hora_registro",
        ]

        self._insert_data(table, columns, values)
