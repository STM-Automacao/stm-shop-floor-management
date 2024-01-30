"""
Class Connection
"""
# cSpell: words automacao, conexao
import urllib
from os import getenv

from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()


class Connection:
    """
    Class Connection
    """

    def __init__(self):
        """
        Constructor

        Args:
            user (str): user
            password (str): password
            database (str): database
            driver (str): driver
            server (str): server

        Usage:
            >>> from connection import Connection
            >>> connection = Connection()
            >>> connection.get_connection()
        """
        self.__user = getenv("PYMSSQL_USER")
        self.__password = getenv("PYMSSQL_PASSWORD")
        self.__database = getenv("PYMSSQL_DATABASE_AUTOMACAO")
        self.__driver = "{ODBC Driver 17 for SQL Server}"
        self.__server = getenv("PYMSSQL_SERVER")

    def get_connection_automacao(self):
        """
        Get connection

        Returns:
            object: connection

        Usage:
            >>> from connection import Connection
            >>> connection = Connection()
            >>> connection.get_connection()
        """
        try:
            params = urllib.parse.quote_plus(
                f"DRIVER={self.__driver};"
                f"SERVER={self.__server};"
                f"DATABASE={self.__database};"
                f"UID={self.__user};"
                f"PWD={self.__password};"
            )
            # pylint: disable=consider-using-f-string
            conexao_automacao = create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)
            return conexao_automacao
        # pylint: disable=broad-except
        except Exception as error:
            print(f"Error: {error}")
            return None
