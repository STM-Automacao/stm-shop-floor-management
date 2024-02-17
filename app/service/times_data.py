"""
Autor: Bruno Tomaz
Data: 11/01/2024
Módulo que prepara dados para os indicadores
"""

from datetime import datetime

import numpy as np
import pandas as pd

# cSpell: words solucao, usuario, producao, eficiencia


class TimesData:
    """
    Classe TimesData para manipulação de dados de tempo e eficiência.

    Esta classe contém métodos para manipulação de dados de tempo e eficiência.

    Para conseguir a Eficiência é possível chamar apenas o método:
    >>> get_eff_data

    Este método já chama o método get_times_disc.
    """

    def __init__(self):
        # Dicionário com os descontos de parada para Eficiência
        self.desc_eff = {
            3: 60,
            5: 10,
            10: 15,
            11: 35,
            15: 60,
            17: 15,
        }
        # Dicionário com os descontos de parada para Performance
        self.desc_perf = {
            3: 60,
            5: 10,
            10: 15,
            15: 60,
            17: 15,
        }
        # Lista com os motivos de parada que não são considerados para Performance
        self.not_af_perf = [7, 8, 11, 12, 13, 16]
        # Dicionário com os descontos de parada para Reparos
        self.desc_rep = {11: 35}
        # Lista com os motivos de parada que são considerados para Reparos
        self.af_rep = [7, 8, 11]
        # Lista de Motivos que não afetam a eficiência
        self.not_af_eff = [12]
        # Lista de Motivos que não afetam a eficiência, performance e reparos
        self.not_af_all = [12]

    def get_times_discount(self, info: pd.DataFrame, desc_pcp: dict[int, int]) -> pd.DataFrame:
        """
        Método para calcular o tempo de eficiência e desconto.

        Este método recebe um DataFrame contendo informações maquina e
        outro com os descontos de parada
        e retorna um DataFrame com informações de tempo de eficiência e desconto.

        Args:
            info (pd.DataFrame): DataFrame com os dados de parada
            desc_pcp (dict[int, int]): Dicionário com os descontos de parada

        Returns:
            pd.DataFrame: DataFrame com os descontos de parada


        Exemplo:
        ```
        times_data = TimesData()
        df_info = pd.dataframe()
        df_result = get_times_data.get_times_discount(df_times_desc, desc_pcp)
        ```
        """

        info_stops = info.copy()

        # Adicionar coluna com descontos de parada
        info_stops["desconto_min"] = info_stops["motivo_id"].map(desc_pcp)

        # Se o motivo_id não afetar ninguém, desconto_min deve ser igual ao tempo_registro_min
        info_stops.loc[info_stops["motivo_id"].isin(self.not_af_all), "desconto_min"] = info_stops[
            "tempo_registro_min"
        ]

        # Se houver desconto, subtrair e arredondar em uma nova coluna chamada excedente
        info_stops["excedente"] = (
            info_stops["tempo_registro_min"] - info_stops["desconto_min"]
        ).clip(lower=0)

        # Se o desconto for maior que tempo de parada, o desconto deve ser igual ao tempo de parada
        info_stops.loc[
            info_stops["desconto_min"] > info_stops["tempo_registro_min"],
            "desconto_min",
        ] = info_stops["tempo_registro_min"]

        # Ajustar data_hora_registro para datetime
        info_stops["data_hora_registro"] = pd.to_datetime(info_stops["data_hora_registro"])

        # Criar coluna data_registro para agrupar por dia
        info_stops["data_registro"] = info_stops["data_hora_registro"].dt.date
        # Ordenar por maquina_id, data_hora_registro, turno
        info_stops.sort_values(by=["maquina_id", "data_hora_registro", "turno"], inplace=True)

        return info_stops

    def get_elapsed_time(self, turno):
        """
        Método para calcular o tempo decorrido no turno atual.

        Este método recebe o turno atual e retorna o tempo decorrido em minutos.

        Args:
            turno (str): Turno atual

        Returns:
            float: Tempo decorrido em minutos


        Exemplo:
            >>> from app.service.get_times_data import GetTimesData
            >>> import pandas as pd
            >>> get_times_data = GetTimesData()
            >>> turno = 'MAT'
            >>> tempo_decorrido = get_times_data.get_elapsed_time(turno)
        """
        now = datetime.now()

        if turno == "MAT" and 8 <= now.hour < 16:
            shift_start = now.replace(hour=8, minute=0, second=0, microsecond=0)

        elif turno == "VES" and 16 <= now.hour < 24:
            shift_start = now.replace(hour=16, minute=0, second=0, microsecond=0)

        elif turno == "NOT" and (now.hour < 8 or now.hour >= 24):
            shift_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        else:
            return 480  # retorna o tempo padrão se não estiver no turno atual

        elapsed_time = now - shift_start

        return elapsed_time.total_seconds() / 60  # retorna o tempo decorrido em minutos

    def get_eff_data(self, df_info: pd.DataFrame, df_prod: pd.DataFrame) -> pd.DataFrame:
        """
        Método para calcular os dados de eficiência.

        Este método recebe dois DataFrames, um contendo informações maquina
        e outro contendo informações de produção,
        e retorna um DataFrame com informações de eficiência.

        ### Parâmetros:
        df_info (pd.DataFrame): DataFrame contendo informações de maquina

        df_prod (pd.DataFrame): DataFrame contendo informações de produção.

        ### Retorna:
        pd.DataFrame: DataFrame com informações de eficiência.

        ### Exemplo de uso:
        ```
        times_data = TimesData()
        df_info = pd.dataframe()
        df_prod = pd.dataframe()
        df_result = times_data.get_eff_data(df_info, df_prod)
        ```
        """

        df_eff_times_desc = self.get_times_discount(df_info, self.desc_eff)
        df_prod_total = df_prod.copy()
        ciclo_ideal = 10.6

        # Descartar colunas desnecessárias de df_prod
        df_prod_total.drop(columns=["total_ciclos"], inplace=True)

        # Se o motivo id não afeta a eficiência, desconto_min deve ser igual ao tempo_registro_min
        df_eff_times_desc.loc[
            df_eff_times_desc["motivo_id"].isin(self.not_af_eff), "desconto_min"
        ] = df_eff_times_desc["tempo_registro_min"]

        # Agrupar por maquina_id, data_registro e turno e somar o desconto
        df_eff_times_desc = (
            df_eff_times_desc.groupby(
                ["maquina_id", "linha", "data_registro", "turno"], observed=False
            )
            .agg(
                {
                    "desconto_min": "sum",
                }
            )
            .reset_index()
        )

        # Garantir que a coluna data_registro é datetime em ambos os dataframes
        df_eff_times_desc["data_registro"] = pd.to_datetime(
            df_eff_times_desc["data_registro"]
        ).dt.date

        df_prod_total["data_registro"] = pd.to_datetime(df_prod_total["data_registro"]).dt.date

        # Fazer merge com df_prod_total
        df_eff_times_desc = pd.merge(
            df_prod_total,
            df_eff_times_desc,
            on=["maquina_id", "linha", "turno", "data_registro"],
            how="left",
            validate="one_to_one",
        )

        # Ajustar desc_min para 0 quando for nulo
        df_eff_times_desc.loc[df_eff_times_desc["desconto_min"].isnull(), "desconto_min"] = 0

        # Criar coluna com tempo esperado de produção
        df_eff_times_desc["tempo_esperado_min"] = df_eff_times_desc.apply(
            lambda row: (
                np.floor(self.get_elapsed_time(row["turno"]) - row["desconto_min"])
                if row["data_registro"] == datetime.now().date()
                else 480 - row["desconto_min"]
            ),
            axis=1,
        )

        # Produção esperada por turno
        df_eff_times_desc["producao_esperada"] = (
            df_eff_times_desc["tempo_esperado_min"] * ciclo_ideal
        ) * 2

        # Calcular a eficiência
        df_eff_times_desc["eficiencia"] = (
            df_eff_times_desc["total_produzido"] / df_eff_times_desc["producao_esperada"]
        )

        # Ordenar pela linha e data_registro
        df_eff_times_desc = df_eff_times_desc.sort_values(
            by=["linha", "data_registro"], ascending=True
        )

        # Remover as linhas onde a linha é 0
        df_eff_times_desc = df_eff_times_desc[df_eff_times_desc["linha"] != 0]

        # Se eficiencia for nula, substituir por 0
        df_eff_times_desc.loc[df_eff_times_desc["eficiencia"].isnull(), "eficiencia"] = 0

        # Se a produção esperada for 0 e a eficiência for 0, substituir por 1
        df_eff_times_desc.loc[
            (df_eff_times_desc["producao_esperada"] == 0),
            "eficiencia",
        ] = np.nan

        # Ajustar o index
        df_eff_times_desc.reset_index(drop=True, inplace=True)

        return df_eff_times_desc

    def get_perf_data(self, df_info: pd.DataFrame, df_prod: pd.DataFrame) -> pd.DataFrame:
        """
        Método para calcular os dados de performance.

        Este método recebe dois DataFrames, um contendo informações de máquina e
        e outro contendo informações de produção,
        e retorna um DataFrame com informações de Performance.

        ### Parâmetros:
        df_info (pd.DataFrame): DataFrame contendo informações de maquina

        df_prod (pd.DataFrame): DataFrame contendo informações de produção.

        ### Retorna:
        pd.DataFrame: DataFrame com informações de performance.

        ### Exemplo de uso:
        ```
        times_data = TimesData()
        df_info = pd.dataframe()
        df_prod = pd.dataframe()
        df_result = times_data.get_perf_data(df_info, df_prod)
        ```
        """

        df_perf_times_desc = self.get_times_discount(df_info, self.desc_perf)
        df_prod_total = df_prod.copy()

        # Descartar colunas desnecessárias de df_prod
        df_prod_total.drop(
            columns=[
                "total_ciclos",
                "total_produzido",
            ],
            inplace=True,
        )

        # Conseguir apenas as datas que o motivo_id = 12 e o tempo de registro for maior que 480
        datas_programadas = df_perf_times_desc[
            (df_perf_times_desc["motivo_id"] == 12)
            & (df_perf_times_desc["tempo_registro_min"] == 480)
        ][["linha", "data_registro", "turno"]]

        # Remover as linhas que não afetam a performance
        df_perf_times_desc = df_perf_times_desc[
            ~df_perf_times_desc["motivo_id"].isin(self.not_af_perf)
        ]

        # Criar coluna 'afeta' para identificar as paradas que afetam a performance
        df_perf_times_desc["afeta"] = df_perf_times_desc["excedente"]

        # Se desconto for nulo, substituir afeta pelo valor de tempo_registro_min
        df_perf_times_desc.loc[df_perf_times_desc["desconto_min"].isnull(), "afeta"] = (
            df_perf_times_desc["tempo_registro_min"]
        )

        # Agrupar por maquina_id, data_registro e turno e somar o tempo de
        # desconto e o afeta
        df_perf_times_desc = (
            df_perf_times_desc.groupby(
                ["maquina_id", "linha", "data_registro", "turno"], observed=False
            )
            .agg(
                {
                    "desconto_min": "sum",
                    "afeta": "sum",
                }
            )
            .reset_index()
        )

        # Garantir que a coluna data_registro é datetime em ambos os dataframes
        df_perf_times_desc["data_registro"] = pd.to_datetime(
            df_perf_times_desc["data_registro"]
        ).dt.date

        df_prod_total["data_registro"] = pd.to_datetime(df_prod_total["data_registro"]).dt.date
        # Fazer merge com df_prod_total

        df_perf_times_desc = pd.merge(
            df_prod_total,
            df_perf_times_desc,
            on=["maquina_id", "linha", "turno", "data_registro"],
            how="left",
            validate="one_to_one",
        )

        # Ajustar desconto_min para 0 quando for nulo
        df_perf_times_desc.loc[df_perf_times_desc["desconto_min"].isnull(), "desconto_min"] = 0

        # Ajustar afeta para 0 quando for nulo
        df_perf_times_desc.loc[df_perf_times_desc["afeta"].isnull(), "afeta"] = 0

        # Criar coluna com tempo esperado de produção
        df_perf_times_desc["tempo_esperado_min"] = df_perf_times_desc.apply(
            lambda row: (
                np.floor(self.get_elapsed_time(row["turno"]) - row["desconto_min"])
                if row["data_registro"] == datetime.now().date()
                else 480 - row["desconto_min"]
            ),
            axis=1,
        )

        # Calcular a performance
        df_perf_times_desc["performance"] = (
            df_perf_times_desc["afeta"] / df_perf_times_desc["tempo_esperado_min"]
        )

        # Ordenar pela linha e data_registro
        df_perf_times_desc = df_perf_times_desc.sort_values(
            by=["linha", "data_registro"], ascending=True
        )

        # Remover as linhas onde a linha é 0
        df_perf_times_desc = df_perf_times_desc[df_perf_times_desc["linha"] != 0]

        # Se a data e o turno coincidem com datas_programadas, a performance é np.nan
        # Converter 'data_registro' para datetime
        df_perf_times_desc["data_registro"] = pd.to_datetime(df_perf_times_desc["data_registro"])
        datas_programadas["data_registro"] = pd.to_datetime(datas_programadas["data_registro"])

        # Criar uma chave única em ambos os DataFrames
        df_perf_times_desc["key"] = (
            df_perf_times_desc["linha"].astype(str)
            + df_perf_times_desc["data_registro"].dt.strftime("%Y-%m-%d")
            + df_perf_times_desc["turno"].astype(str)
        )
        datas_programadas["key"] = (
            datas_programadas["linha"].astype(str)
            + datas_programadas["data_registro"].dt.strftime("%Y-%m-%d")
            + datas_programadas["turno"].astype(str)
        )

        # Se a chave coincide com datas_programadas, a performance é np.nan
        df_perf_times_desc.loc[
            df_perf_times_desc["key"].isin(datas_programadas["key"]),
            "performance",
        ] = np.nan

        # Remover a coluna 'key'
        df_perf_times_desc.drop(columns=["key"], inplace=True)
        datas_programadas.drop(columns=["key"], inplace=True)

        # Ajustar o index
        df_perf_times_desc.reset_index(drop=True, inplace=True)

        return df_perf_times_desc

    def get_repair_data(self, df_info: pd.DataFrame, df_prod: pd.DataFrame) -> pd.DataFrame:
        """
        Método para calcular os dados de reparos.

        Este método recebe dois DataFrames, um contendo informações de máquina e
        e outro contendo informações de produção,
        e retorna um DataFrame com informações de Reparos.

        ### Parâmetros:
        df_info (pd.DataFrame): DataFrame contendo informações de maquina

        df_prod (pd.DataFrame): DataFrame contendo informações de produção.

        ### Retorna:
        pd.DataFrame: DataFrame com informações de performance.

        ### Exemplo de uso:
        ```
        times_data = TimesData()
        df_info = pd.dataframe()
        df_prod = pd.dataframe()
        df_result = times_data.get_reparos_data(df_info, df_prod)
        ```
        """

        df_rep_times_desc = self.get_times_discount(df_info, self.desc_rep)
        df_prod_total = df_prod.copy()

        # Descartar colunas desnecessárias de df_prod
        df_prod_total.drop(
            columns=[
                "total_ciclos",
                "total_produzido",
            ],
            inplace=True,
        )

        # Conseguir apenas as datas que o motivo_id = 12 e o tempo de registro for maior que 480
        datas_programadas = df_rep_times_desc[
            (df_rep_times_desc["motivo_id"] == 12)
            & (df_rep_times_desc["tempo_registro_min"] == 480)
        ][["linha", "data_registro", "turno"]]

        # Remover as linhas que não afetam o reparo
        df_rep_times_desc = df_rep_times_desc[df_rep_times_desc["motivo_id"].isin(self.af_rep)]

        # Criar coluna 'afeta' para identificar as paradas que afetam o reparo
        df_rep_times_desc["afeta"] = df_rep_times_desc["excedente"]

        # Se desconto for nulo, substituir afeta pelo valor de tempo_registro_min
        df_rep_times_desc.loc[df_rep_times_desc["desconto_min"].isnull(), "afeta"] = (
            df_rep_times_desc["tempo_registro_min"]
        )

        # Agrupar por maquina_id, data_registro e turno e somar o tempo de
        # desconto e o afeta
        df_rep_times_desc = (
            df_rep_times_desc.groupby(
                ["maquina_id", "linha", "data_registro", "turno"], observed=False
            )
            .agg(
                {
                    "desconto_min": "sum",
                    "afeta": "sum",
                }
            )
            .reset_index()
        )

        # Garantir que a coluna data_registro é datetime em ambos os dataframes
        df_rep_times_desc["data_registro"] = pd.to_datetime(
            df_rep_times_desc["data_registro"]
        ).dt.date
        df_prod_total["data_registro"] = pd.to_datetime(df_prod_total["data_registro"]).dt.date

        # Fazer merge com df_prod_total
        df_rep_times_desc = pd.merge(
            df_prod_total,
            df_rep_times_desc,
            on=["maquina_id", "linha", "turno", "data_registro"],
            how="left",
            validate="one_to_one",
        )

        # Ajustar desconto_min para 0 quando for nulo
        df_rep_times_desc.loc[df_rep_times_desc["desconto_min"].isnull(), "desconto_min"] = 0

        # Ajustar afeta para 0 quando for nulo
        df_rep_times_desc.loc[df_rep_times_desc["afeta"].isnull(), "afeta"] = 0

        # Criar coluna com tempo esperado de produção
        df_rep_times_desc["tempo_esperado_min"] = df_rep_times_desc.apply(
            lambda row: (
                np.floor(self.get_elapsed_time(row["turno"]) - row["desconto_min"])
                if row["data_registro"] == datetime.now().date()
                else 480 - row["desconto_min"]
            ),
            axis=1,
        )

        # Calcular o reparo
        df_rep_times_desc["reparo"] = (
            df_rep_times_desc["afeta"] / df_rep_times_desc["tempo_esperado_min"]
        )

        # Ordenar pela linha e data_registro
        df_rep_times_desc = df_rep_times_desc.sort_values(
            by=["linha", "data_registro"], ascending=True
        )

        # Remover as linhas onde a linha é 0
        df_rep_times_desc = df_rep_times_desc[df_rep_times_desc["linha"] != 0]

        # Se a data e o turno coincidem com datas_programadas, a performance é np.nan
        # Converter 'data_registro' para datetime
        df_rep_times_desc["data_registro"] = pd.to_datetime(df_rep_times_desc["data_registro"])
        datas_programadas["data_registro"] = pd.to_datetime(datas_programadas["data_registro"])

        # Criar uma chave única em ambos os DataFrames
        df_rep_times_desc["key"] = (
            df_rep_times_desc["linha"].astype(str)
            + df_rep_times_desc["data_registro"].dt.strftime("%Y-%m-%d")
            + df_rep_times_desc["turno"].astype(str)
        )
        datas_programadas["key"] = (
            datas_programadas["linha"].astype(str)
            + datas_programadas["data_registro"].dt.strftime("%Y-%m-%d")
            + datas_programadas["turno"].astype(str)
        )

        # Se a chave coincide com datas_programadas, a performance é np.nan
        df_rep_times_desc.loc[
            df_rep_times_desc["key"].isin(datas_programadas["key"]),
            "reparo",
        ] = np.nan

        # Remover a coluna 'key'
        df_rep_times_desc.drop(columns=["key"], inplace=True)
        datas_programadas.drop(columns=["key"], inplace=True)

        # Ajustar o index
        df_rep_times_desc.reset_index(drop=True, inplace=True)

        return df_rep_times_desc
