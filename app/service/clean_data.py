"""
    Autor: Bruno Tomaz
    Data: 06/01/2024
    Módulo para limpeza dos dados
"""

from datetime import time

# cSpell:words usuario, solucao, dayofweek, sabado
import numpy as np
import pandas as pd


class CleanData:
    """
    A class that provides methods to clean data.

    Args:
        df_ihm (pd.DataFrame): The DataFrame containing basic data.
        df_info (pd.DataFrame): The DataFrame containing information data.
        df_info_production (pd.DataFrame): The DataFrame containing production data.

    Returns:
        tuple: A tuple containing the cleaned DataFrames for basic data, information data,
        and production data.
    """

    def __init__(self, df_ihm: pd.DataFrame, df_info: pd.DataFrame, df_info_production):
        self.df_ihm = df_ihm
        self.df_info = df_info
        self.df_info_production = df_info_production

    @staticmethod
    def __clean_basics(df: pd.DataFrame) -> pd.DataFrame:
        """
        Cleans the basic data in the given DataFrame.

        Parameters:
        df (pd.DataFrame): The DataFrame containing the data to be cleaned.

        Returns:
        pd.DataFrame: The cleaned DataFrame.

        Steps:
        1. Remove duplicate values from the DataFrame.
        2. Remove rows with missing values in specific columns.
        3. Remove milliseconds from the 'hora_registro' column.
        4. Convert 'data_registro' and 'hora_registro' columns to the correct data types.
        5. Replace NaN values in the 'linha' column with 0 and convert it to integer.
        6. Remove rows where 'linha' is 0.

        """

        # Remove valores duplicados, caso existam
        df = df.drop_duplicates()

        # Remove as linha com valores nulos que não podem faltar
        df = df.dropna(subset=["maquina_id", "data_registro", "hora_registro"])

        # Remover os milissegundos da coluna hora_registro
        df["hora_registro"] = df["hora_registro"].astype(str).str.split(".").str[0]

        # Garantir que as colunas de data e hora sejam do tipo correto
        df["data_registro"] = pd.to_datetime(df["data_registro"])
        df["hora_registro"] = pd.to_datetime(df["hora_registro"], format="%H:%M:%S").dt.time

        # Substitui os valores NaN por 0 e depois converte para inteiro
        df["linha"] = df["linha"].fillna(0).astype(int)

        # Se existir remove a coluna recno
        if "recno" in df.columns:
            df = df.drop(columns=["recno"])

        # Remover onde a linha for 0
        df = df[df["linha"] != 0]

        return df

    @staticmethod
    def __clean_info(df: pd.DataFrame) -> pd.DataFrame:
        """
        Cleans the given DataFrame by performing the following operations:
        1. Sorts the DataFrame by "maquina_id", "data_registro", and "hora_registro".
        2. Removes rows where the first entry of "turno" is 'VES' and the "maquina_id" changes.
        3. Adjusts the date and time for rows where "turno" is 'VES' and "hora_registro" is
        between 00:00 and 00:05.
           The date is changed to the previous day and the time is set to 23:59:59.
        4. Sorts the DataFrame by "linha", "data_registro", and "hora_registro".
        5. Resets the index of the DataFrame.

        Parameters:
        - df (pd.DataFrame): The DataFrame to be cleaned.

        Returns:
        - pd.DataFrame: The cleaned DataFrame.
        """

        # Reordenar o dataframe
        df = df.sort_values(by=["maquina_id", "data_registro", "hora_registro"])

        # Correção caso a primeira entrada seja do turno 'VES'
        mask = (df["turno"] == "VES") & (df["maquina_id"] != df["maquina_id"].shift())
        df = df[~mask]

        # Ajustar caso o turno "VES" passe de 00:00, para o dia anterior 23:59
        mask = (
            (df["turno"] == "VES")
            & (df["hora_registro"] < time(0, 5, 0))
            & (df["hora_registro"] > time(0, 0, 0))
        )

        df.loc[mask, "data_registro"] = df.loc[mask, "data_registro"] - pd.Timedelta(days=1)
        df.loc[mask, "hora_registro"] = time(23, 59, 59)

        # Reordenar o dataframe
        df = df.sort_values(by=["linha", "data_registro", "hora_registro"])

        # Reiniciar o index
        df = df.reset_index(drop=True)

        return df

    @staticmethod
    def __clean_production(df: pd.DataFrame) -> pd.DataFrame:
        """
        Cleans the production data by performing the following steps:
        1. Creates a column to order the data by shifts.
        2. Sorts the dataframe by line, registration date, and shift order.
        3. Removes the created column.
        4. Resets the index of the dataframe.

        Parameters:
        - df (pd.DataFrame): The input dataframe containing the production data.

        Returns:
        - pd.DataFrame: The cleaned dataframe.
        """

        # Cria uma coluna para ordenar pelos turnos
        df["turno_order"] = df["turno"].map({"MAT": 2, "VES": 3, "NOT": 1})

        # Ordenar o dataframe
        df = df.sort_values(by=["linha", "data_registro", "turno_order"])

        # Remover a coluna criada
        df = df.drop(columns=["turno_order"])

        # Reiniciar o index
        df = df.reset_index(drop=True)

        return df

    def clean_data(self) -> tuple:
        """
        Cleans the data by performing various cleaning operations on different dataframes.

        Uses the private methods __clean_basics, __clean_info, and __clean_production.

        Returns:
            tuple: A tuple containing the cleaned dataframes - df_ihm, df_info, df_info_production.
        """

        # Limpar os dados básicos
        self.df_ihm = self.__clean_basics(self.df_ihm)
        self.df_info = self.__clean_basics(self.df_info)
        self.df_info_production = self.__clean_basics(self.df_info_production)

        # Ajustando a nomenclatura do status
        self.df_info["status"] = np.where(self.df_info["status"] == "true", "rodando", "parada")

        # Limpar os dados de informações
        self.df_info = self.__clean_info(self.df_info)

        # Limpar os dados de produção
        self.df_info_production = self.__clean_production(self.df_info_production)

        return self.df_ihm, self.df_info, self.df_info_production
