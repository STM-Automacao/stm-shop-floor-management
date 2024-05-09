"""
    Autor: Bruno Tomaz
    Data: 08/01/2024
    Módulo para unir os dados de cadastro, info e ocorrência
"""

import pandas as pd


class JoinData:
    """
    Class for joining two dataframes based on the 'data_hora' column.

    Args:
        df_ihm (pd.DataFrame): The first dataframe to be joined.
        df_info (pd.DataFrame): The second dataframe to be joined.

    Returns:
        pd.DataFrame: The merged and processed dataframe.
    """

    def __init__(self, df_ihm: pd.DataFrame, df_info: pd.DataFrame) -> None:
        self.df_ihm = df_ihm
        self.df_info = df_info

    def join_data(self) -> pd.DataFrame:
        """
        Joins two dataframes, df_info and df_ihm, based on the 'data_hora' column.
        The dataframes are sorted by 'data_hora' before merging.
        The merge is performed using the 'maquina_id' column as the key.
        The merge is done using the nearest timestamp within a tolerance of 1 minute and 10 seconds.
        The resulting dataframe is then reordered and renamed to match the desired column names.
        Finally, the index is reset and the resulting dataframe is returned.

        Returns:
            pd.DataFrame: The merged and processed dataframe.
        """

        # Cria coluna com união de data e hora para df_ihm
        self.df_ihm["data_hora"] = pd.to_datetime(
            self.df_ihm["data_registro"].astype(str) + " " + self.df_ihm["hora"].astype(str)
        )

        # Cria coluna com união de data e hora para df_info
        self.df_info["data_hora"] = pd.to_datetime(
            self.df_info["data_registro"].astype(str) + " " + self.df_info["hora"].astype(str)
        )

        # Classifica os dataframes por data_hora
        self.df_ihm = self.df_ihm.sort_values(by="data_hora")
        self.df_info = self.df_info.sort_values(by="data_hora")

        # Realiza o merge dos dataframes
        df = pd.merge_asof(
            self.df_info,
            self.df_ihm,
            on="data_hora",
            by="maquina_id",
            direction="nearest",
            tolerance=pd.Timedelta("1 min 10 s"),
        )

        # Define o tipo para colunas de ciclos e produção
        df["contagem_total_ciclos"] = df["contagem_total_ciclos"].astype("Int64")
        df["contagem_total_produzido"] = df["contagem_total_produzido"].astype("Int64")

        # Reordenar as colunas, mantendo só as necessárias
        df = df[
            [
                "fabrica",
                "linha_x",
                "maquina_id",
                "turno",
                "status",
                "contagem_total_ciclos",
                "contagem_total_produzido",
                "data_registro_x",
                "hora_registro_x",
                "motivo",
                "equipamento",
                "problema",
                "causa",
                "os_numero",
                "operador_id",
                "data_registro_y",
                "hora_registro_y",
            ]
        ]

        # Renomear as colunas
        df = df.rename(
            columns={
                "linha_x": "linha",
                "daa_registro_x": "data_registro",
                "hora_registro_x": "hora_registro",
                "data_registro_y": "data_registro_ihm",
                "hora_registro_y": "hora_registro_ihm",
            }
        )

        # Reordenar o dataframe
        df = df.sort_values(by=["linha", "data_registro", "hora_registro"])

        # Reiniciar o index
        df = df.reset_index(drop=True)

        return df
