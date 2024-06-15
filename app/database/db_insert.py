"""Módulo que contém as funções de inserção de dados no banco de dados."""

# cSpell: words automacao autoload
from database.connection import Connection
from sqlalchemy import MetaData, Table, insert
from sqlalchemy.exc import DatabaseError


class Insert(Connection):
    """
    Class Insert
    Insert data into the database
    """

    # pylint: disable=useless-super-delegation
    def __init__(self):
        super().__init__()

    def insert_data(self, table: str, data: dict) -> None:
        """
        Insert data into the database.

        Parameters
        ----------
        table : str
            Table name
        data : dict
        """
        engine = None
        connection = None
        try:
            engine = self.get_connection_automacao()
            metadata = MetaData(schema="dbo")
            table = Table(table, metadata, autoload_with=engine)
            stmt = insert(table).values(**data)
            with engine.begin() as connection:
                connection.execute(stmt)
                connection.commit()
        except DatabaseError as e:
            print(f"Erro ao inserir dados: {e}")
        finally:
            if engine:
                engine.dispose()
