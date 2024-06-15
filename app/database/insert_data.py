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

    def insert_maq_ihm_data(self, values: list) -> None:
        """
        Insert data into the maq_ihm table.

        Parameters
        ----------
        values : list
            List of values
        """
        table = "maquina_ihm"

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

        data = dict(zip(columns, values))

        self.insert.insert_data(table, data)
