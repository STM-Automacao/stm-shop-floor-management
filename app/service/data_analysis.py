"""
Modulo que faz a análise dos dados de paradas e produção.
"""

from datetime import datetime

import numpy as np
import pandas as pd
from helpers.my_types import IndicatorType


class DataAnalysis:
    """
    Class for performing data analysis on stops and production data.

    Attributes:
    df_stops (pd.DataFrame): DataFrame with stops data.
    df_prod (pd.DataFrame): DataFrame with production data.
    """

    def __init__(self, df_stops: pd.DataFrame, df_prod: pd.DataFrame):
        self.df_stops = df_stops
        self.df_prod = df_prod

        # Dicionário com descontos de Eficiência
        self.desc_eff = {
            "Troca de Sabor": 15,
            "Troca de Produto": 35,
            "Refeição": 60,
            "Café e Ginástica Laboral": 10,
            "Treinamento": 60,
        }

        # Dicionário com descontos de Performance
        self.desc_perf = {
            "Troca de Sabor": 15,
            "Refeição": 60,
            "Café e Ginástica Laboral": 10,
            "Treinamento": 60,
        }

        # Dicionário com descontos de Reparo
        self.desc_rep = {"Troca de Produto": 35}

        # Dicionário com o que não afeta a eficiência
        self.not_eff = ["Sem Produção", "Backup"]

        # Dicionário com o que não afeta a performance
        self.not_perf = [
            "Sem Produção",
            "Backup",
            "Limpeza para parada de Fábrica",
            "Risco de Contaminação",
            "Parâmetros de Qualidade",
            "Manutenção",
        ]

        # Dicionário com o que afeta o reparo
        self.afeta_rep = ["Manutenção", "Troca de Produtos"]

    def get_discount(
        self,
        df: pd.DataFrame,
        desc_dict: dict[str, int],
        not_dict: list[str],
        indicator: IndicatorType,
    ) -> pd.DataFrame:
        """
        Calcula o desconto de eficiência, performance ou reparo.
        """

        # Cria uma coluna com o desconto padrão
        df = df.copy()
        df["desconto"] = 0

        # Caso o motivo, problema ou causa não afete o indicador, o desconto é igual a tempo
        mask = (
            df[["motivo", "problema", "causa"]]
            .apply(lambda x: x.str.contains("|".join(not_dict), case=False, na=False))
            .any(axis=1)
        )
        df.loc[mask, "desconto"] = 0 if indicator == IndicatorType.REPAIR else df["tempo"]

        # Cria um dict para indicadores
        indicator_dict = {
            IndicatorType.EFFICIENCY: df,
            IndicatorType.PERFORMANCE: df[~mask],
            IndicatorType.REPAIR: df[mask],
        }

        df = indicator_dict[indicator].reset_index(drop=True)

        # Aplica o desconto de acordo com as colunas "motivo" ou "problema" ou "causa"
        for key, value in desc_dict.items():
            mask = (
                df[["motivo", "problema", "causa"]]
                .apply(lambda x, key=key: x.str.contains(key, case=False, na=False))
                .any(axis=1)
            )
            df.loc[mask, "desconto"] = value

        # Caso o desconto seja maior que o tempo, o desconto deve ser igual ao tempo
        df.loc[:, "desconto"] = df[["desconto", "tempo"]].min(axis=1)

        # Calcula o excedente
        df.loc[:, "excedente"] = (df["tempo"] - df["desconto"]).clip(lower=0)

        return df

    def __get_elapsed_time(self, turno: str) -> int:
        """
        Calcula o tempo decorrido do turno.
        """

        # Agora
        now = datetime.now()

        if turno == "MAT" and 8 <= now.hour < 16:
            elapsed_time = now - datetime(now.year, now.month, now.day, 8, 0, 0)
        elif turno == "VES" and 16 <= now.hour < 24:
            elapsed_time = now - datetime(now.year, now.month, now.day, 16, 0, 0)
        elif turno == "NOT" and 0 <= now.hour < 8:
            elapsed_time = now - datetime(now.year, now.month, now.day, 0, 0, 0)
        else:
            return 480

        return elapsed_time.total_seconds() / 60

    def __get_expected_production_time(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula o tempo esperado de produção.
        """

        df["tempo_esperado"] = df.apply(
            lambda row: (
                np.floor(self.__get_elapsed_time(row["turno"]) - row["desconto"])
                if row["data_registro"].date() == pd.to_datetime("today").date()
                else 480 - row["desconto"]
            ),
            axis=1,
        )

        return df

    def get_eff_data(self) -> pd.DataFrame:
        """
        Calcula o desconto de eficiência.
        """

        df = self.df_stops
        df_prod = self.df_prod

        # Calcula o desconto de eficiência
        df = self.get_discount(df, self.desc_eff, self.not_eff, IndicatorType.EFFICIENCY)
        ciclo_ideal = 10.6

        # Agrupa para ter o valor total de desconto
        df = (
            df.groupby(["maquina_id", "linha", "data_registro", "turno"], observed=False)
            .agg(
                tempo=("tempo", "sum"),
                desconto=("desconto", "sum"),
                excedente=("excedente", "sum"),
            )
            .reset_index()
        )

        # Une os dois dataframes
        df = pd.merge(df_prod, df, on=["maquina_id", "linha", "data_registro", "turno"], how="left")

        # Lida com valores nulos
        df = df.fillna(0)

        # Nova coluna para tempo esperado de produção
        df = self.__get_expected_production_time(df)

        # Nova coluna para produção esperada
        df["producao_esperada"] = (df["tempo_esperado"] * ciclo_ideal) * 2

        # Nova coluna para eficiência
        df["eficiencia"] = (df["total_produzido"] / df["producao_esperada"]).round(3)

        # Corrige valores nulos ou inf de eficiência
        df["eficiencia"] = df["eficiencia"].replace([np.inf, -np.inf], np.nan).fillna(0)

        # Se a produção esperada for 0 e a eficiência for 0, tornar a eficiência np.nan
        mask = (df["producao_esperada"] == 0) & (df["eficiencia"] == 0)
        df.loc[mask, "eficiencia"] = np.nan

        # Ordenar as colunas
        df = df[
            [
                "fabrica",
                "linha",
                "maquina_id",
                "turno",
                "data_registro",
                "hora_registro",
                "tempo",
                "total_produzido",
                "producao_esperada",
                "tempo_esperado",
                "desconto",
                "excedente",
                "eficiencia",
            ]
        ]

        return df

    def get_perf_data(self) -> pd.DataFrame:
        """
        Calcula o desconto de performance.
        """

        df = self.df_stops
        df_prod = self.df_prod

        # Dataframe com datas e turnos onde a causa está em not_eff e o tempo é igual a 480
        mask = (df["causa"].isin(self.not_perf)) & (df["tempo"] == 480)
        paradas_programadas = df[mask][["data_registro", "turno"]]  # Para performance ser np.nan

        # Calcula o desconto de performance e filtra linhas que não afetam a performance
        df = self.get_discount(df, self.desc_perf, self.not_perf, IndicatorType.PERFORMANCE)

        # Agrupa para ter o valor total de desconto
        df = (
            df.groupby(["maquina_id", "linha", "data_registro", "turno"], observed=False)
            .agg(
                tempo=("tempo", "sum"),
                desconto=("desconto", "sum"),
                afeta=("excedente", "sum"),
            )
            .reset_index()
        )

        # Une os dois dataframes
        df = pd.merge(df_prod, df, on=["maquina_id", "linha", "data_registro", "turno"], how="left")

        # Lida com valores nulos
        df = df.fillna(0)

        # Coluna com tempo esperado de produção
        df = self.__get_expected_production_time(df)

        # Coluna de Performance
        df["performance"] = (df["afeta"] / df["tempo_esperado"]).round(2)

        # Corrige valores nulos ou inf de performance
        df["performance"] = df["performance"].replace([np.inf, -np.inf], np.nan).fillna(0)

        # Ajuste para paradas_programadas, performance é np.nan e o tempo esperado é igual a 0
        mask = df["data_registro"].isin(paradas_programadas["data_registro"]) & df["turno"].isin(
            paradas_programadas["turno"]
        )
        df.loc[mask, "performance"] = np.nan
        df.loc[mask, "tempo_esperado"] = 0

        # Ordenar as colunas
        df = df[
            [
                "fabrica",
                "linha",
                "maquina_id",
                "turno",
                "data_registro",
                "hora_registro",
                "tempo",
                "tempo_esperado",
                "desconto",
                "afeta",
                "performance",
            ]
        ]

        return df

    def get_repair_data(self) -> pd.DataFrame:
        """
        Calcula o desconto de reparo.
        """

        df = self.df_stops
        df_prod = self.df_prod

        # Dataframe com datas e turnos onde a causa está em not_eff e o tempo é igual a 480
        mask = (df["causa"].isin(self.not_perf)) & (df["tempo"] == 480)
        paradas_programadas = df[mask][["data_registro", "turno"]]  # Para performance ser np.nan

        # Calcula o desconto de reparo
        df = self.get_discount(df, self.desc_rep, self.afeta_rep, IndicatorType.REPAIR)

        # Agrupa para ter o valor total de desconto
        df = (
            df.groupby(["maquina_id", "linha", "data_registro", "turno"], observed=False)
            .agg(
                tempo=("tempo", "sum"),
                desconto=("desconto", "sum"),
                afeta=("excedente", "sum"),
            )
            .reset_index()
        )

        # Une os dois dataframes
        df = pd.merge(df_prod, df, on=["maquina_id", "linha", "data_registro", "turno"], how="left")

        # Lida com valores nulos
        df = df.fillna(0)

        # Coluna com tempo esperado de produção
        df = self.__get_expected_production_time(df)

        # Coluna de Reparo
        df["reparo"] = (df["afeta"] / df["tempo_esperado"]).round(2)

        # Corrige valores nulos ou inf de reparo
        df["reparo"] = df["reparo"].replace([np.inf, -np.inf], np.nan).fillna(0)

        # Ajuste p/ paradas_programadas, performance é np.nan e o tempo esperado é igual a 0
        mask = df["data_registro"].isin(paradas_programadas["data_registro"]) & df["turno"].isin(
            paradas_programadas["turno"]
        )
        df.loc[mask, "reparo"] = np.nan
        df.loc[mask, "tempo_esperado"] = 0

        # Ordenar as colunas
        df = df[
            [
                "fabrica",
                "linha",
                "maquina_id",
                "turno",
                "data_registro",
                "hora_registro",
                "tempo",
                "tempo_esperado",
                "desconto",
                "afeta",
                "reparo",
            ]
        ]

        return df
