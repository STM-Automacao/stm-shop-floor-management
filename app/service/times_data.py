"""
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

    def __get_times_discount(
        self, info: pd.DataFrame, desc_pcp: dict[int, int]
    ) -> pd.DataFrame:
        """
        Método para calcular o tempo de eficiência e desconto.

        Este método recebe um DataFrame contendo informações maquina e
        outro com os descontos de parada
        e retorna um DataFrame com informações de tempo de eficiência e desconto.

        ### Parâmetros:
        info (pd.DataFrame): DataFrame contendo informações de tempo.

        ### Retorna:
        pd.DataFrame: DataFrame com informações de tempo de eficiência e desconto.

        ### Exemplo de uso:
        ```
        times_data = TimesData()
        df_info = pd.dataframe()
        df_result = times_data.get_times_eff_disc(df_info)
        ```
        """

        info_stops = info.copy()

        # Certificar que data_hora_registro é do tipo datetime
        info_stops["data_hora_registro"] = pd.to_datetime(
            info_stops["data_hora_registro"]
        )

        # Adicionar coluna com descontos de parada
        info_stops["desconto_min"] = info_stops["motivo_id"].map(desc_pcp)

        # Se houver desconto, subtrair do tempo de parada e arredondar para baixo
        info_stops["excedente"] = (
            info_stops["tempo_registro_min"] - info_stops["desconto_min"]
        ).clip(lower=0)

        # Se o desconto for maior que o tempo de parada, deve ser igual ao tempo de parada
        info_stops.loc[
            info_stops["desconto_min"] > info_stops["tempo_registro_min"],
            "desconto_min",
        ] = info_stops["tempo_registro_min"]

        # Criar coluna data_registro para agrupar por dia
        info_stops["data_registro"] = info_stops["data_hora_registro"].dt.date

        # Ordenar por maquina_id, data_hora_registro, turno
        info_stops.sort_values(
            by=["maquina_id", "data_hora_registro", "turno"], inplace=True
        )

        # Manter somente colunas necessárias
        info_stops = info_stops[
            [
                "maquina_id",
                "linha",
                "fabrica",
                "turno",
                "motivo_id",
                "motivo_nome",
                "problema",
                "solucao",
                "tempo_registro_min",
                "desconto_min",
                "excedente",
                "data_hora_registro",
                "data_hora_final",
                "usuario_id_maq_occ",
                "data_hora_registro_operador",
                "usuario_id_maq_cadastro",
                "data_registro",
            ]
        ]

        return info_stops

    def get_elapsed_time(self, turno):
        """
        Função para obter o tempo decorrido desde o início do turno atual.
        """
        now = datetime.now()
        if turno == "MAT" and 8 <= now.hour < 16:
            shift_start = now.replace(
                hour=8, minute=0, second=0, microsecond=0
            )
        elif turno == "VES" and 16 <= now.hour < 24:
            shift_start = now.replace(
                hour=16, minute=0, second=0, microsecond=0
            )
        elif turno == "NOT" and (now.hour < 8 or now.hour >= 24):
            shift_start = now.replace(
                hour=0, minute=0, second=0, microsecond=0
            )
        else:
            return 480  # retorna o tempo padrão se não estiver no turno atual

        elapsed_time = now - shift_start
        return (
            elapsed_time.total_seconds() / 60
        )  # retorna o tempo decorrido em minutos

    def get_eff_data(
        self, df_info: pd.DataFrame, df_prod: pd.DataFrame
    ) -> pd.DataFrame:
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

        df_eff_times_desc = self.__get_times_discount(df_info, self.desc_eff)
        df_prod_total = df_prod.copy()
        ciclo_ideal = 10.6

        # Descartar colunas desnecessárias de df_prod -> 'contagem_total_ciclos',
        # 'usuario_id_maq_cadastro', 'data_hora_registro'
        df_prod_total.drop(
            columns=[
                "contagem_total_ciclos",
                "data_hora_registro",
                "usuario_id_maq_cadastro",
            ],
            inplace=True,
        )

        # Renomear coluna contagem_total_produzido para producao_total
        df_prod_total.rename(
            columns={"contagem_total_produzido": "producao_total"},
            inplace=True,
        )

        # Agrupar por maquina_id, data_registro e turno e somar o tempo de parada,
        # o desconto e o excedente
        df_eff_times_desc = (
            df_eff_times_desc.groupby(
                ["maquina_id", "linha", "fabrica", "data_registro", "turno"]
            )
            .agg(
                {
                    "desconto_min": "sum",
                }
            )
            .reset_index()
        )

        # Converta a coluna "data_registro" para data em ambos os dataframes
        df_eff_times_desc["data_registro"] = pd.to_datetime(
            df_eff_times_desc["data_registro"]
        ).dt.date
        df_prod_total["data_registro"] = pd.to_datetime(
            df_prod_total["data_registro"]
        ).dt.date

        # Fazer merge com df_prod_total
        df_eff_times_desc = pd.merge(
            df_prod_total,
            df_eff_times_desc,
            on=["maquina_id", "linha", "fabrica", "turno", "data_registro"],
            how="left",
        )

        # Ajustar desc_min para 0 quando for nulo
        df_eff_times_desc.loc[
            df_eff_times_desc["desconto_min"].isnull(), "desconto_min"
        ] = 0

        # Criar coluna com tempo esperado de produção
        df_eff_times_desc["tempo_esperado_min"] = df_eff_times_desc.apply(
            lambda row: np.floor(
                self.get_elapsed_time(row["turno"]) - row["desconto_min"]
            )
            if row["data_registro"] == datetime.now().date()
            else 480 - row["desconto_min"],
            axis=1,
        )

        # Produção esperada por turno
        df_eff_times_desc["producao_esperada"] = (
            df_eff_times_desc["tempo_esperado_min"] * ciclo_ideal
        ) * 2

        # Calcular a eficiência
        df_eff_times_desc["eficiencia"] = (
            df_eff_times_desc["producao_total"]
            / df_eff_times_desc["producao_esperada"]
        )

        # Ajustar o index
        df_eff_times_desc.reset_index(drop=True, inplace=True)

        return df_eff_times_desc

    def get_perf_data(
        self, df_info: pd.DataFrame, df_prod: pd.DataFrame
    ) -> pd.DataFrame:
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

        df_perf_times_desc = self.__get_times_discount(df_info, self.desc_perf)
        df_prod_total = df_prod.copy()

        # Descartar colunas desnecessárias de df_prod
        df_prod_total.drop(
            columns=[
                "contagem_total_ciclos",
                "contagem_total_produzido",
                "data_hora_registro",
                "usuario_id_maq_cadastro",
            ],
            inplace=True,
        )

        # Remover as linhas que não afetam a performance
        df_perf_times_desc = df_perf_times_desc[
            ~df_perf_times_desc["motivo_id"].isin(self.not_af_perf)
        ]

        # Criar coluna 'afeta' para identificar as paradas que afetam a performance
        df_perf_times_desc["afeta"] = df_perf_times_desc["excedente"]

        # Se desconto for nulo, substituir afeta pelo valor de tempo_registro_min
        df_perf_times_desc.loc[
            df_perf_times_desc["desconto_min"].isnull(), "afeta"
        ] = df_perf_times_desc["tempo_registro_min"]

        # Agrupar por maquina_id, data_registro e turno e somar o tempo de
        # desconto e o afeta
        df_perf_times_desc = (
            df_perf_times_desc.groupby(
                ["maquina_id", "linha", "fabrica", "data_registro", "turno"]
            )
            .agg(
                {
                    "desconto_min": "sum",
                    "afeta": "sum",
                }
            )
            .reset_index()
        )

        # Converta a coluna "data_registro" para data em ambos os dataframes
        df_perf_times_desc["data_registro"] = pd.to_datetime(
            df_perf_times_desc["data_registro"]
        ).dt.date
        df_prod_total["data_registro"] = pd.to_datetime(
            df_prod_total["data_registro"]
        ).dt.date

        # Fazer merge com df_prod_total
        df_perf_times_desc = pd.merge(
            df_prod_total,
            df_perf_times_desc,
            on=["maquina_id", "linha", "fabrica", "turno", "data_registro"],
            how="left",
        )

        # Ajustar desconto_min para 0 quando for nulo
        df_perf_times_desc.loc[
            df_perf_times_desc["desconto_min"].isnull(), "desconto_min"
        ] = 0

        # Ajustar afeta para 0 quando for nulo
        df_perf_times_desc.loc[
            df_perf_times_desc["afeta"].isnull(), "afeta"
        ] = 0

        # Criar coluna com tempo esperado de produção
        df_perf_times_desc["tempo_esperado_min"] = df_perf_times_desc.apply(
            lambda row: np.floor(
                self.get_elapsed_time(row["turno"]) - row["desconto_min"]
            )
            if row["data_registro"] == datetime.now().date()
            else 480 - row["desconto_min"],
            axis=1,
        )

        # Calcular a performance
        df_perf_times_desc["performance"] = (
            df_perf_times_desc["afeta"]
            / df_perf_times_desc["tempo_esperado_min"]
        )

        return df_perf_times_desc

    def get_repair_data(
        self, df_info: pd.DataFrame, df_prod: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Método para calcular os dados de reparo.

        Este método recebe dois DataFrames, um contendo informações de máquina e
        e outro contendo informações de produção,
        e retorna um DataFrame com informações de Reparo.

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

        df_rep_times_desc = self.__get_times_discount(df_info, self.desc_rep)
        df_prod_total = df_prod.copy()

        # Descartar colunas desnecessárias de df_prod
        df_prod_total.drop(
            columns=[
                "contagem_total_ciclos",
                "contagem_total_produzido",
                "data_hora_registro",
                "usuario_id_maq_cadastro",
            ],
            inplace=True,
        )

        # Remover as linhas que não afetam o reparo
        df_rep_times_desc = df_rep_times_desc[
            df_rep_times_desc["motivo_id"].isin(self.af_rep)
        ]

        # Criar coluna 'afeta' para identificar as paradas que afetam o reparo
        df_rep_times_desc["afeta"] = df_rep_times_desc["excedente"]

        # Se desconto for nulo, substituir afeta pelo valor de tempo_registro_min
        df_rep_times_desc.loc[
            df_rep_times_desc["desconto_min"].isnull(), "afeta"
        ] = df_rep_times_desc["tempo_registro_min"]

        # Agrupar por maquina_id, data_registro e turno e somar o tempo de
        # desconto e o afeta
        df_rep_times_desc = (
            df_rep_times_desc.groupby(
                ["maquina_id", "linha", "fabrica", "data_registro", "turno"]
            )
            .agg(
                {
                    "desconto_min": "sum",
                    "afeta": "sum",
                }
            )
            .reset_index()
        )

        # Converta a coluna "data_registro" para data em ambos os dataframes
        df_rep_times_desc["data_registro"] = pd.to_datetime(
            df_rep_times_desc["data_registro"]
        ).dt.date
        df_prod_total["data_registro"] = pd.to_datetime(
            df_prod_total["data_registro"]
        ).dt.date

        # Fazer merge com df_prod_total
        df_rep_times_desc = pd.merge(
            df_prod_total,
            df_rep_times_desc,
            on=["maquina_id", "linha", "fabrica", "turno", "data_registro"],
            how="left",
        )

        # Ajustar desconto_min para 0 quando for nulo
        df_rep_times_desc.loc[
            df_rep_times_desc["desconto_min"].isnull(), "desconto_min"
        ] = 0

        # Ajustar afeta para 0 quando for nulo
        df_rep_times_desc.loc[df_rep_times_desc["afeta"].isnull(), "afeta"] = 0

        # Criar coluna com tempo esperado de produção
        df_rep_times_desc["tempo_esperado_min"] = df_rep_times_desc.apply(
            lambda row: np.floor(
                self.get_elapsed_time(row["turno"]) - row["desconto_min"]
            )
            if row["data_registro"] == datetime.now().date()
            else 480 - row["desconto_min"],
            axis=1,
        )

        # Calcular o reparo
        df_rep_times_desc["reparo"] = (
            df_rep_times_desc["afeta"]
            / df_rep_times_desc["tempo_esperado_min"]
        )

        return df_rep_times_desc
