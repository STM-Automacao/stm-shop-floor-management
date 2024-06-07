"""
Limpa os dados do PCP
"""

from datetime import datetime

import pandas as pd
from pcp.helpers.types_pcp import MASSADA_BOLINHA, MASSADA_CHEIA, MASSADA_REPROCESSO

# cSpell: words codigo descricao usuario


class CleanPcpData:
    """
    Classe responsável por limpar os dados relacionados ao PCP(Planejamento e Controle da Produção).

    Attributes:
        Nenhum atributo.

    Methods:
        __init__: Inicializa a classe CleanPcpData.
        __get_shift: Retorna o turno com base no horário fornecido.
        __total_mass: Calcula a massa total com base nos dados fornecidos.
        clean_massadas_data: Limpa os dados relacionados às massadas no dataframe fornecido.
    """

    def __init__(self) -> None:
        pass

    @staticmethod
    def __get_shift(time: str) -> str:
        """
        Retorna o turno com base no horário fornecido.

        Args:
            time (str): O horário no formato "HH:MM:SS".

        Returns:
            str: O turno correspondente ao horário fornecido.
        """
        if (
            time >= datetime.strptime("08:00:00", "%H:%M:%S").time()
            and time < datetime.strptime("16:00:00", "%H:%M:%S").time()
        ):
            return "MAT"
        elif (
            time >= datetime.strptime("16:00:00", "%H:%M:%S").time()
            and time < datetime.strptime("23:59:59", "%H:%M:%S").time()
        ):
            return "VES"
        else:
            return "NOT"

    @staticmethod
    def __total_mass(df: pd.DataFrame, position: int = None) -> pd.DataFrame:
        """
        Calcula a massa total com base nos dados fornecidos.

        Args:
            df (pd.DataFrame): O dataframe contendo os dados.
            position (int, optional): A posição dos dados. Padrão é None.

        Returns:
            pd.DataFrame: O dataframe com a massa total calculada.
        """
        df_massadas_total = (
            df.groupby(["Codigo_Maquina", "Descricao_Maquina", "Data_Registro", "Turno", "Fabrica"])
            .agg(
                Usuario_Registro=("Usuario_Registro", "first"),
                Batidas_Cheia=("Quantidade_Atropelamento", "count"),
                Peso_Massa_BC=("Quantidade_Atropelamento", "sum"),
            )
            .reset_index()
        )

        # Cria um dict para renomear colunas
        rename_columns = {
            1: {
                "Batidas_Cheia": "Batidas_Reprocesso",
                "Peso_Massa_BC": "Peso_Massa_BR",
            },
            2: {
                "Batidas_Cheia": "Batidas_Bolinha",
                "Peso_Massa_BC": "Peso_Massa_BB",
            },
        }

        # Renomeia as colunas
        if position is not None:
            df_massadas_total.rename(columns=rename_columns[position], inplace=True)

        return df_massadas_total

    def clean_massadas_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Limpa os dados relacionados às massadas no dataframe fornecido.

        Args:
            df (pd.DataFrame): O dataframe contendo os dados das massadas.

        Returns:
            pd.DataFrame: O dataframe com os dados das massadas limpos.
        """
        # Atribuir coluna turno com base no horário
        df["Hora_Registro"] = pd.to_datetime(df["Hora_Registro"], format="%H:%M:%S").dt.time
        df["Turno"] = df["Hora_Registro"].apply(self.__get_shift)

        # Separando o dataframe conforme a quantidade de atropelamentos
        df_massadas_cheias = df[df["Quantidade_Atropelamento"] == MASSADA_CHEIA]
        df_massadas_reprocesso = df[df["Quantidade_Atropelamento"] == MASSADA_REPROCESSO]
        df_massadas_bolinha = df[df["Quantidade_Atropelamento"] == MASSADA_BOLINHA]

        # Soma os valores por maquina, data e turno
        df_massadas_cheias = self.__total_mass(df_massadas_cheias)
        df_massadas_reprocesso = self.__total_mass(df_massadas_reprocesso, 1)
        df_massadas_bolinha = self.__total_mass(df_massadas_bolinha, 2)

        # Unir os dataframes de massadas cheias e reprocesso
        df_massadas = df_massadas_cheias.merge(
            df_massadas_reprocesso,
            how="outer",
            on=[
                "Codigo_Maquina",
                "Descricao_Maquina",
                "Data_Registro",
                "Turno",
                "Fabrica",
                "Usuario_Registro",
            ],
        )

        # Unir o dataframe de massadas com o dataframe de bolinha
        df_massadas = df_massadas.merge(
            df_massadas_bolinha,
            how="outer",
            on=[
                "Codigo_Maquina",
                "Descricao_Maquina",
                "Data_Registro",
                "Turno",
                "Fabrica",
                "Usuario_Registro",
            ],
        )

        # Transformar data_registro em datetime no formato ano-mes-dia
        df_massadas["Data_Registro"] = pd.to_datetime(df_massadas["Data_Registro"], format="%Y%m%d")

        return df_massadas
