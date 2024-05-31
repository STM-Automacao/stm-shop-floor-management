"""
Este módulo ajusta os dados do dataframe unido de info e ihm, identificando mudanças de status,
preenchendo valores nulos de paradas, agrupando e calculando o tempo de cada status.
"""

import warnings

import numpy as np
import pandas as pd

warnings.simplefilter(action="ignore", category=FutureWarning)


class ServiceInfoIHM:
    """
    Service class for retrieving adjusted information from the IHM (Interface Homem-Máquina).

    Args:
        df (pd.DataFrame): The input DataFrame containing machine information.
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df

    @staticmethod
    def __identify_changes(df: pd.DataFrame, column: str) -> pd.Series:
        return df[column].ne(df[column].shift())

    def __status_change(self, df: pd.DataFrame) -> pd.DataFrame:
        # Checa se houve mudança de status, maquina_id e turno
        columns_to_check = ["status", "maquina_id", "turno"]
        for column in columns_to_check:
            df[f"{column}_change"] = self.__identify_changes(df, column)

        # Coluna auxiliar que identifica se houve alguma mudança
        df["change"] = df[["status_change", "maquina_id_change", "turno_change"]].any(axis=1)

        return df

    @staticmethod
    def __fill_occ(df: pd.DataFrame) -> pd.DataFrame:
        # Preenche os valores nulos de paradas
        df["motivo"] = df.groupby("group")["motivo"].transform(lambda x: x.ffill().bfill())
        df["equipamento"] = df.groupby("group")["equipamento"].transform(
            lambda x: x.ffill().bfill()
        )
        df["problema"] = df.groupby("group")["problema"].transform(lambda x: x.ffill().bfill())
        df["causa"] = df.groupby("group")["causa"].transform(lambda x: x.ffill().bfill())
        df["os_numero"] = df.groupby("group")["os_numero"].transform(lambda x: x.ffill().bfill())
        df["operador_id"] = df.groupby("group")["operador_id"].transform(
            lambda x: x.ffill().bfill()
        )
        df["data_registro_ihm"] = df.groupby("group")["data_registro_ihm"].transform(
            lambda x: x.ffill().bfill()
        )
        df["hora_registro_ihm"] = df.groupby("group")["hora_registro_ihm"].transform(
            lambda x: x.ffill().bfill()
        )

        # Se os dado de uma coluna for '' ou ' ', substituir por NaN
        df = df.replace(r"^s*$", None, regex=True)
        # O ^ indica o início de uma string, o $ indica o fim de uma string,
        # e s* zero ou mais espaços em branco

        return df

    @staticmethod
    def __group_and_calc_time(df: pd.DataFrame) -> pd.DataFrame:
        # Agrupa as mudanças
        df = (
            df.groupby(["group"])
            .agg(
                fabrica=("fabrica", "first"),
                linha=("linha", "first"),
                maquina_id=("maquina_id", "first"),
                turno=("turno", "first"),
                status=("status", "first"),
                data_registro=("data_registro", "first"),
                hora_registro=("hora_registro", "first"),
                motivo=("motivo", "first"),
                equipamento=("equipamento", "first"),
                problema=("problema", "first"),
                causa=("causa", "first"),
                os_numero=("os_numero", "first"),
                operador_id=("operador_id", "first"),
                data_registro_ihm=("data_registro_ihm", "first"),
                hora_registro_ihm=("hora_registro_ihm", "first"),
                data_hora=("data_hora", "first"),
                change=("change", "first"),
                maquina_id_change=("maquina_id_change", "first"),
                change_date=("change_date", "first"),
                motivo_change=("motivo_change", "first"),
            )
            .reset_index()
        )

        # Nova coluna com a data_hora_final do status/parada
        df["data_hora_final"] = (
            df.groupby("maquina_id")["data_hora"].shift(-1).where(~df["maquina_id_change"])
        )

        # Atualiza a hora final caso mude a máquina
        mask = df["maquina_id_change"]
        df["data_hora_final"] = np.where(
            mask,
            df["change_date"].shift(-1),
            df["data_hora_final"],
        )

        # =============== Atualização Para Hora Final No Caso De Mudança De Turno =============== #
        # Dicionário com o horário de término de cada turno
        turno_end_time = {
            "NOT": pd.to_timedelta("08:01:00"),
            "MAT": pd.to_timedelta("16:01:00"),
            "VES": pd.to_timedelta("00:01:00"),
        }

        # Nova coluna com o horário de término do turno
        df["turno_end_time"] = df["turno"].map(turno_end_time)

        # Atualiza a hora final caso haja mudança de turno
        mask = df["turno"] != df["turno"].shift(-1)
        df["data_hora_final"] = np.where(
            mask & (df["turno"] == "VES"),
            (df["data_hora"].dt.normalize() + pd.DateOffset(days=1)) + df["turno_end_time"],
            np.where(
                mask,
                df["data_hora"].dt.normalize() + df["turno_end_time"],
                df["data_hora_final"],
            ),
        )

        # Remove coluna auxiliar
        df = df.drop(columns=["turno_end_time"])

        # Caso a data_hora_final seja nula, remove a linha
        df = df.dropna(subset=["data_hora_final"]).reset_index(drop=True)

        # Calcula o tempo de cada status
        df["tempo"] = (
            pd.to_datetime(df["data_hora_final"]) - pd.to_datetime(df["data_hora"])
        ).dt.total_seconds() / 60

        # Arredondar e converter para inteiro
        df["tempo"] = df["tempo"].round().astype(int)

        # Se o tempo for maior que 478, e o motivo for parada programada ou limpeza ajustar para 480
        mask = (df["tempo"] > 478) & (df["motivo"].isin(["Parada Programada", "Limpeza"]))
        df["tempo"] = np.where(mask, 480, df["tempo"])

        return df

    def get_info_ihm_adjusted(self) -> pd.DataFrame:
        """
        Retrieves adjusted information from the IHM (Interface Homem-Máquina).

        This method performs data reading, cleaning, and joining operations to retrieve adjusted
        information from the IHM.
        It identifies status changes, fills null values for stops, calculates stop or running times,
        and performs other adjustments.

        Returns:
            pd.DataFrame: The adjusted information from the IHM.
        """

        # Realiza a leitura, limpeza e junção dos dados
        df_joined = self.df

        # ========================= Identifica Onde Há Mudança De Status ========================= #

        df_joined = self.__status_change(df_joined)

        # ========================= Preenchendo Valores Nulos De Paradas ========================= #

        # Cria um grupo para cada mudança de status
        df_joined["group"] = df_joined["change"].cumsum()

        # Preenche os valores nulos de paradas
        df_joined = self.__fill_occ(df_joined)

        # Coluna auxiliar para identificar mudança na coluna motivo, se não for nula
        mask = (df_joined["motivo"].ne(df_joined["motivo"].shift())) | (
            df_joined["causa"].ne(df_joined["causa"].shift())
        )
        df_joined["motivo_change"] = mask & df_joined["motivo"].notnull()

        # Atualiza o change
        df_joined["change"] = df_joined["change"] | df_joined["motivo_change"]

        # Refaz o grupo para considerar a mudança na coluna motivo
        df_joined["group"] = df_joined["change"].cumsum()

        # Coluna auxiliar para unir data e hora
        df_joined["data_hora"] = pd.to_datetime(
            df_joined["data_registro"].astype(str) + " " + df_joined["hora_registro"].astype(str)
        )

        # Coluna auxiliar para identificar a data/hora da mudança
        df_joined["change_date"] = (
            df_joined.groupby("maquina_id")["data_hora"].shift(0).where(df_joined["change"])
        )

        # =========================== Calcula O Tempo Parada Ou Rodando ========================== #

        # Calcula os tempos
        df_joined = self.__group_and_calc_time(df_joined)

        # Ajustar status para levar em conta testes
        mask = (
            (df_joined["status"] == "rodando")
            & (df_joined["tempo"] < 10)
            & (df_joined["turno"].eq(df_joined["turno"].shift(-1)))
            & (df_joined["motivo"].shift() != "Parada Programada")
        )

        df_joined["status"] = np.where(mask, "parada", df_joined["status"])

        mask = (
            (df_joined["status"] == "rodando")
            & (df_joined["tempo"] < 5)
            & (df_joined["turno"].eq(df_joined["turno"].shift(-1)))
        )

        df_joined["status"] = np.where(mask, "parada", df_joined["status"])

        # Ajuste em change para refletir alterações
        df_joined = self.__status_change(df_joined)
        df_joined["change"] = df_joined["change"] | df_joined["motivo_change"]

        # Refaz o group
        df_joined["group"] = df_joined["change"].cumsum()

        # Preenche os valores nulos de paradas
        df_joined = self.__fill_occ(df_joined)

        # Recalcula os tempos
        df_joined = self.__group_and_calc_time(df_joined)

        # Se o tempo for negativo, ajustar para 0
        df_joined["tempo"] = df_joined["tempo"].clip(lower=0)

        # Se o tempo for maior que 480 minutos, ajustar para 480
        df_joined["tempo"] = df_joined["tempo"].clip(upper=480)

        # Remove colunas auxiliares
        df_joined = df_joined.drop(
            columns=[
                "maquina_id_change",
                "change",
                "maquina_id_change",
                "change_date",
                "motivo_change",
                "group",
            ]
        )

        return df_joined

    def get_time_working(self, df: pd.DataFrame) -> pd.Series:
        """
        Calculates the total working time for each machine/line.

        Args:
            df (pd.DataFrame): The input DataFrame containing machine information.

        Returns:
            pd.Series: A Series with the total working time for each machine.
        """

        # Filtra apenas as máquinas que estão rodando
        df = df[df["status"] == "rodando"]

        # Agrupa por máquina e turno
        df = (
            df.groupby(["maquina_id", "linha", "turno", "data_registro", "status"], observed=False)[
                "tempo"
            ]
            .sum()
            .reset_index()
        )

        # Renomear coluna
        df = df.rename(columns={"status": "motivo"})

        # Capitaliza o motivo
        df["motivo"] = df["motivo"].str.capitalize()

        return df

    def get_maq_stopped(self, df: pd.DataFrame) -> pd.Series:
        """
        Filters the DataFrame to only include machines that are stopped.

        Parameters:
        df (pd.DataFrame): The input DataFrame containing machine information.

        Returns:
        pd.Series: The filtered DataFrame with only stopped machines.
        """

        # Filtra apenas as máquinas que estão paradas
        df = df[df["status"] == "parada"]

        # Reinicia o índice
        df = df.reset_index(drop=True)

        return df
