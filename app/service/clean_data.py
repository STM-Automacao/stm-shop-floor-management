"""
    Módulo para limpeza dos dados
"""

from datetime import time

# cSpell:words usuario, solucao, dayofweek, sabado
import numpy as np
import pandas as pd

# pylint: disable=E0401
from helpers.path_config import FERIADOS


class CleanData:
    """
    Classe para limpeza dos dados

    Métodos:
    --------
        clean_maq_info: Limpa os dados de status das máquinas
        clean_maq_occ: Limpa os dados de ocorrências das máquinas

    """

    def maq_info(self, info: pd.DataFrame) -> pd.DataFrame:
        """
        Processa as informações de uma máquina e retorna um DataFrame com os dados ajustados.

        Args:
            info (pd.DataFrame): DataFrame contendo as informações da máquina.

        Returns:
            pd.DataFrame: DataFrame com os dados ajustados da máquina.
        """

        # Ordenar dataframe
        df_info = info.sort_values(by=["maquina_id", "data_registro", "hora_registro", "turno"])

        # Criar coluna com data e hora unidos
        df_info["data_hora_registro"] = (
            df_info["data_registro"].astype(str)
            + " "
            + df_info["hora_registro"].astype(str).str.split(".").str[0]
        )

        # Ajustar primeira entrada se for VES
        mask = (df_info["turno"] == "VES") & (
            df_info["maquina_id"] != df_info["maquina_id"].shift()
        )
        df_info["turno"] = np.where(mask, "NOT", df_info["turno"])

        # Ajustar data_hora para pd.datetime
        df_info["data_hora_registro"] = pd.to_datetime(df_info["data_hora_registro"])

        # Ajustar horário se turno for VES - ajusta para dia anterior e horário 23:59:59
        mask = (
            (df_info["turno"] == "VES")
            & (df_info["data_hora_registro"] != df_info["data_hora_registro"].shift())
            & (df_info["data_hora_registro"].dt.time > time(0, 0, 0))
            & (df_info["data_hora_registro"].dt.time < time(0, 5, 0))
        )
        df_info["data_hora_registro"] = np.where(
            mask,
            (df_info["data_hora_registro"] - pd.Timedelta(days=1)).dt.normalize()
            + pd.Timedelta(hours=23, minutes=59, seconds=59),
            df_info["data_hora_registro"],
        )

        # Criar nova coluna status_change para identificar mudança de status
        df_info["status_change"] = df_info["status"].ne(df_info["status"].shift())

        # Criar coluna para identificar a mudança de máquina
        df_info["maquina_change"] = df_info["maquina_id"].ne(df_info["maquina_id"].shift())

        # Criar coluna para identificar a mudança de turno
        df_info["turno_change"] = df_info["turno"].ne(df_info["turno"].shift())

        # Atualizar coluna change para incluir mudança de turno
        df_info["change"] = (
            df_info["status_change"] | df_info["maquina_change"] | df_info["turno_change"]
        )

        # Agrupar por maquina e identificar data e hora da última mudança de status
        df_info["change_time"] = (
            df_info.groupby("maquina_id")["data_hora_registro"].shift(0).where(df_info["change"])
        )

        # Feito para agrupar por maquina_id e turno e manter o ultimo registro de cada grupo
        df_info = (
            df_info.groupby(["maquina_id", "change_time"], observed=False)
            .agg(
                status=("status", "first"),
                turno=("turno", "first"),
                linha=("linha", "first"),
                fabrica=("fabrica", "first"),
                data_hora_registro=("data_hora_registro", "first"),
                contagem_total_ciclos=("contagem_total_ciclos", "last"),
                contagem_total_produzido=(
                    "contagem_total_produzido",
                    "last",
                ),
                change=("change", "first"),
                maquina_change=("maquina_change", "first"),
            )
            .reset_index()
        )

        # Criar nova coluna com a data_hora_final do status
        df_info["data_hora_final"] = (
            df_info.groupby("maquina_id", observed=False)["data_hora_registro"]
            .shift(-1)
            .where(~df_info["maquina_change"])
        )

        # Atualizar coluna data_hora_final onde maquina_change é True
        mask = df_info["maquina_change"]
        df_info["data_hora_final"] = np.where(
            mask, df_info["change_time"].shift(-1), df_info["data_hora_final"]
        )

        # Remover colunas desnecessárias
        df_info.drop(
            columns=[
                "maquina_change",
                "change",
                "change_time",
            ],
            inplace=True,
        )

        # Remover linhas onde data_hora_final é nulo
        df_info.dropna(subset=["data_hora_final"], inplace=True)

        # Cria nova coluna tempo_registro_min para calcular o tempo de registro em minutos
        df_info["tempo_registro_min"] = (
            pd.to_datetime(df_info["data_hora_final"])
            - pd.to_datetime(df_info["data_hora_registro"])
        ).dt.total_seconds() / 60

        # Arredondar tempo_registro_min e converter para inteiro
        df_info["tempo_registro_min"] = df_info["tempo_registro_min"].round(0).astype(int)

        # Ajustar tipos
        df_info = df_info.astype(
            {
                "maquina_id": "category",
                "status": "category",
                "turno": "category",
                "linha": "category",
                "fabrica": "category",
                "tempo_registro_min": int,
                "contagem_total_ciclos": int,
                "contagem_total_produzido": int,
            }
        )

        # Ajustar nomenclatura dos status
        df_info["status"] = np.where(
            (df_info["status"] == "true") & (df_info["tempo_registro_min"] < 10),
            "in_test",
            df_info["status"],
        )
        df_info["status"] = np.where(df_info["status"] == "true", "rodando", df_info["status"])
        df_info["status"] = np.where(df_info["status"] == "false", "parada", df_info["status"])

        # Ajustar tipo do status
        df_info["status"] = df_info["status"].astype("category")

        # Ajustar o index
        df_info.reset_index(drop=True, inplace=True)

        return df_info

    def get_adjusted_stops_data(self, info: pd.DataFrame) -> pd.DataFrame:
        """
        Retorna os dados de paradas ajustados de acordo com as regras definidas.

        Args:
            info (pd.DataFrame): O dataframe contendo os dados de paradas.

        Returns:
            pd.DataFrame: O dataframe com os dados de paradas ajustados.
        """
        # Certificar que data_hora_registro e data_hora_final são do tipo datetime
        info["data_hora_registro"] = pd.to_datetime(info["data_hora_registro"])
        info["data_hora_final"] = pd.to_datetime(info["data_hora_final"])

        # Ordenar por maquina_id e data_hora_registro
        df_info = info.sort_values(by=["maquina_id", "data_hora_registro"])

        # Criar coluna auxiliar para identificar a maquina rodando
        df_info["rodando"] = np.where(df_info["status"] == "rodando", 1, 0)

        # Unir grupos de paradas, levando em conta mudança de maquina e turno
        df_info["group"] = (
            (df_info["rodando"] != df_info["rodando"].shift())
            | (df_info["maquina_id"] != df_info["maquina_id"].shift())
            | (df_info["turno"] != df_info["turno"].shift())
            | (
                df_info["data_hora_registro"].dt.date
                != df_info["data_hora_registro"].shift().dt.date
            )
        ).cumsum()

        # Agregar por grupo
        df_info = (
            df_info.groupby(["group"], observed=False)
            .agg(
                maquina_id=("maquina_id", "first"),
                status=("status", "first"),
                turno=("turno", "first"),
                linha=("linha", "first"),
                fabrica=("fabrica", "first"),
                data_hora_registro=("data_hora_registro", "first"),
                data_hora_final=("data_hora_final", "last"),
                tempo_registro_min=("tempo_registro_min", "sum"),
                contagem_total_ciclos=("contagem_total_ciclos", "last"),
                contagem_total_produzido=("contagem_total_produzido", "last"),
            )
            .reset_index(drop=True)
        )

        # Alterar in_test para parada
        df_info["status"] = np.where(df_info["status"] == "in_test", "parada", df_info["status"])

        # Substituir valores nulos por np.nan
        df_info.fillna(value=np.nan, inplace=True)

        return df_info

    def dayofweek_adjust(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Incluir colunas para identificar sábados, domingos e feriados.

        Args:
            df (pd.DataFrame): DataFrame com os dados de paradas.

        Returns:
            pd.DataFrame: DataFrame com as colunas adicionadas.
        """

        # Garantir que data_hora_registro é do tipo datetime
        df["data_hora_registro"] = pd.to_datetime(df["data_hora_registro"])

        # Identificar sábados
        df["sabado"] = np.where(df["data_hora_registro"].dt.dayofweek == 5, 1, 0)

        # Identificar domingos
        df["domingo"] = np.where(df["data_hora_registro"].dt.dayofweek == 6, 1, 0)

        # Listar feriados
        # feriados = pd.read_csv(file_path)
        holidays = pd.read_csv(FERIADOS)

        # Converter para datetime
        holidays["feriados"] = pd.to_datetime(holidays["feriados"])

        # Identificar feriados
        df["feriado"] = (
            df["data_hora_registro"]
            .dt.date.isin(pd.to_datetime(holidays["feriados"]).dt.date)
            .astype(int)
        )

        return df

    def get_maq_info_cleaned(self, df_info: pd.DataFrame) -> pd.DataFrame:
        """
        Retorna os dados de paradas ajustados de acordo com as regras definidas.

        Args:
            df_info (pd.DataFrame): O dataframe contendo os dados de paradas.

        Returns:
            pd.DataFrame: O dataframe com os dados de paradas ajustados.
        """

        # Ajustar dados de maquina_info
        df_info = self.maq_info(df_info)

        # Ajustar dados de paradas
        df_info = self.get_adjusted_stops_data(df_info)

        # Incluir colunas para identificar sábados, domingos e feriados
        df_info = self.dayofweek_adjust(df_info)

        return df_info

    def get_maq_occ_cleaned(self, df_occ: pd.DataFrame) -> pd.DataFrame:
        """
        Retorna os dados de ocorrências ajustados de acordo com as regras definidas.

        Args:
            df_occ (pd.DataFrame): O dataframe contendo os dados de ocorrências.

        Returns:
            pd.DataFrame: O dataframe com os dados de ocorrências ajustados.
        """

        # Motivos de Parada
        motivos = {
            1: "Ajustes",
            2: "Troca de Bobina",
            3: "Refeição",
            4: "Reunião",
            5: "Café e Ginástica Laboral",
            6: "Limpeza",
            7: "Manutenção Elétrica",
            8: "Manutenção Mecânica",
            9: "Material em Falta",
            10: "Setup de Sabor",
            11: "Setup de Tamanho",
            12: "Parada Programada",
            13: "Intervenção de Qualidade",
            14: "Linha Cheia",
            15: "Treinamento",
            16: "Limpeza Industrial",
            17: "Troca de Filme",
        }

        # Ajustar coluna motivo_id para int
        df_occ = df_occ.astype({"motivo_id": int})

        # Unir data_registro e hora_registro
        df_occ["data_hora_registro"] = (
            df_occ["data_registro"].astype(str)
            + " "
            + df_occ["hora_registro"].astype(str).str.split(".").str[0]
        )

        # Ajustar data_hora_registro para datetime
        df_occ["data_hora_registro"] = pd.to_datetime(df_occ["data_hora_registro"])

        # Criar coluna com motivo_nome com base no dicionário motivos
        df_occ["motivo_nome"] = df_occ["motivo_id"].map(motivos)

        # Ajustar "problema" e "solucao" se a string estiver vazia
        df_occ["problema"] = np.where(df_occ["problema"] == "", np.nan, df_occ["problema"])
        df_occ["solucao"] = np.where(df_occ["solucao"] == "", np.nan, df_occ["solucao"])

        # Copiar motivo_nome para problema caso problema seja nulo e motivo_id não seja 1,7,8,9,14
        df_occ["problema"] = np.where(
            (df_occ["problema"].isnull())
            & (
                ~df_occ["motivo_id"].isin(
                    [
                        1,
                        7,
                        8,
                        9,
                        14,
                    ]
                )
            ),
            df_occ["motivo_nome"],
            df_occ["problema"],
        )

        # Ajustar ordem das colunas e seus tipos
        df_occ = df_occ.reindex(
            columns=[
                "maquina_id",
                "motivo_id",
                "motivo_nome",
                "problema",
                "solucao",
                "data_hora_registro",
                "usuario_id",
            ]
        )
        df_occ = df_occ.astype(
            {
                "maquina_id": "category",
                "motivo_id": int,
                "motivo_nome": "category",
                "problema": str,
                "solucao": "category",
                "data_hora_registro": "datetime64[ns]",
                "usuario_id": "category",
            }
        )

        return df_occ

    def get_maq_production_cleaned(self, df_production: pd.DataFrame) -> pd.DataFrame:
        """
        Retorna os dados de produção ajustados de acordo com as regras definidas.

        Args:
            df_production (pd.DataFrame): O dataframe contendo os dados de produção.

        Returns:
            pd.DataFrame: O dataframe com os dados de produção ajustados.
        """

        # Incluir coluna turno_number para ordenar os turnos
        df_production["turno_number"] = df_production["turno"].map({"MAT": 2, "VES": 3, "NOT": 1})

        # Ordenar por maquina_id, data_registro e turno_number
        df_production.sort_values(by=["maquina_id", "data_registro", "turno_number"], inplace=True)

        # Remover coluna turno_number
        df_production.drop(columns=["turno_number"], inplace=True)

        # Ajustar tipos
        df_production = df_production.astype(
            {
                "maquina_id": "category",
                "linha": "category",
                "turno": "category",
                "total_ciclos": int,
                "total_produzido": int,
                "data_registro": "datetime64[ns]",
            }
        )

        # Ajustar o index
        df_production.reset_index(drop=True, inplace=True)

        return df_production
