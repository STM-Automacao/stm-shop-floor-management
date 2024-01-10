"""
    Módulo para unir os dados de cadastro, info e ocorrência
"""

import pandas as pd
import numpy as np


# cSpell: words solucao, usuario
class JoinData:
    """
    Classe para unir os dados de cadastro, info e ocorrência
    """

    def __init__(self):
        pass

    def join_info_occ(
        self, df_occ: pd.DataFrame, df_info: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Une os dados de info e ocorrência

        Args:
            df_occ (pd.DataFrame): Dataframe com os dados de ocorrência
            df_info (pd.DataFrame): Dataframe com os dados de info

        Returns:
            pd.DataFrame: Dataframe com os dados de info e ocorrência unidos

        Examples:
            >>> join_data = JoinData()
            >>> df_info_occ = join_data.join_info_occ(df_occ, df_info)
        """

        # Criar uma função para ser usada em cada linha do dataframe
        def merge_rows(row):
            # Selecionar rows onde a data_hora_registro de occ está entre
            # data_hora_registro e data_hora_final de info
            mask = (
                (df_occ["data_hora_registro"] >= row["data_hora_registro"])
                & (df_occ["data_hora_registro"] <= row["data_hora_final"])
                & (df_occ["maquina_id"] == row["maquina_id"])
            )

            # Se houver rows selecionadas, retornar uma serie contendo os valores
            if df_occ.loc[mask].shape[0] > 0:
                return pd.Series(
                    [
                        df_occ.loc[mask, "motivo_id"].values[0],
                        df_occ.loc[mask, "motivo_nome"].values[0],
                        df_occ.loc[mask, "problema"].values[0],
                        df_occ.loc[mask, "solucao"].values[0],
                        df_occ.loc[mask, "data_hora_registro"].values[0],
                        df_occ.loc[mask, "usuario_id"].values[0],
                    ]
                )
            else:
                return pd.Series([None, None, None, None, None, None])

        # Aplicar a função merge_rows em cada linha do dataframe
        df_info[
            [
                "motivo_id",
                "motivo_nome",
                "problema",
                "solucao",
                "data_hora_registro_operador",
                "usuario_id",
            ]
        ] = df_info.apply(merge_rows, axis=1)

        # Ajustar para sempre que estiver parada por motivo
        # 3, 4, 5, 12, 15, 16, o status será rodando
        df_info.loc[
            (df_info["status"] == "in_test")
            & (df_info["motivo_id"].shift(1).isin([3, 4, 5, 12, 15, 16])),
            "status",
        ] = "rodando"

        # Ajustar o index
        df_info.reset_index(drop=True, inplace=True)

        return df_info

    def adjust_position(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Ajusta a posição das colunas

        Args:
            df (pd.DataFrame): Dataframe com os dados

        Returns:
            pd.DataFrame: Dataframe com os dados ajustados

        Examples:
            >>> join_data = JoinData()
            >>> df = join_data.adjust_position(df)
        """

        # Criar uma coluna parada_inicio como bool para identificar o início de uma parada
        df["parada_inicio"] = df["status"].eq("parada") & df[
            "status"
        ].shift().eq("rodando")

        # Criar uma coluna parada_anterior como bool para identificar a parada anterior
        df["parada_anterior"] = (
            df.groupby("maquina_id")
            .apply(
                lambda group: group.apply(
                    lambda row: row.name if row["parada_inicio"] else np.nan,
                    axis=1,
                )
            )
            .reset_index(level=0, drop=True)
        )

        # Preencher os valores nulos de parada_anterior com o último valor válido
        df["parada_anterior"] = df.groupby("maquina_id")[
            ["parada_anterior"]
        ].ffill()

        # Criar colunas para preparar o movimento das linhas para correção
        df["motivo_id_moved"] = df.groupby("parada_anterior")[
            ["motivo_id"]
        ].transform("first")
        df["motivo_nome_moved"] = df.groupby("parada_anterior")[
            ["motivo_nome"]
        ].transform("first")
        df["problema_moved"] = df.groupby("parada_anterior")[
            ["problema"]
        ].transform("first")
        df["solucao_moved"] = df.groupby("parada_anterior")[
            ["solucao"]
        ].transform("first")
        df["data_hora_registro_operador_moved"] = df.groupby(
            "parada_anterior"
        )[["data_hora_registro_operador"]].transform("first")
        df["usuario_id_moved"] = df.groupby("parada_anterior")[
            ["usuario_id"]
        ].transform("first")

        # Preencher valores nulos com os valores movidos
        df["motivo_id"] = df["motivo_id"].fillna(df["motivo_id_moved"])
        df["motivo_nome"] = df["motivo_nome"].fillna(df["motivo_nome_moved"])
        df["problema"] = df["problema"].fillna(df["problema_moved"])
        df["solucao"] = df["solucao"].fillna(df["solucao_moved"])
        df["data_hora_registro_operador"] = df[
            "data_hora_registro_operador"
        ].fillna(df["data_hora_registro_operador_moved"])
        df["usuario_id"] = df["usuario_id"].fillna(df["usuario_id_moved"])

        # Remover o motivo_id, motivo_nome e problema caso o status seja rodando
        df.loc[
            df["status"] == "rodando",
            [
                "motivo_id",
                "motivo_nome",
                "problema",
                "data_hora_registro_operador",
                "usuario_id",
            ],
        ] = np.nan

        # Preencher os valores nulos com np.nan
        df.fillna(np.nan, inplace=True)

        # Remover as colunas desnecessárias
        df.drop(
            columns=[
                "parada_inicio",
                "parada_anterior",
                "motivo_id_moved",
                "motivo_nome_moved",
                "problema_moved",
                "solucao_moved",
                "data_hora_registro_operador_moved",
                "usuario_id_moved",
            ],
            inplace=True,
        )

        return df

    def info_cadastro_combine(
        self, df_info: pd.DataFrame, df_cadastro: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Une os dados de info e cadastro

        Args:
        -----
            df_info (pd.DataFrame): Dataframe com os dados de info
            df_cadastro (pd.DataFrame): Dataframe com os dados de cadastro

        Retorna:
        --------
            pd.DataFrame: Dataframe com os dados combinados
        """

        # Ordenar os dataframes
        df_info.sort_values(by=["data_hora_registro"], inplace=True)
        df_cadastro.sort_values(by=["data_hora_registro"], inplace=True)

        # Renomear usuario id
        df_cadastro.rename(
            columns={"usuario_id": "usuario_id_maq_cadastro"}, inplace=True
        )
        df_info.rename(
            columns={"usuario_id": "usuario_id_maq_occ"}, inplace=True
        )

        # Merge asof para unir os dataframes baseado na coluna data_hora_registro
        df_info = pd.merge_asof(
            df_info,
            df_cadastro,
            on="data_hora_registro",
            by="maquina_id",
            direction="backward",
        )

        # Reordenar as colunas
        df_info = df_info[
            [
                "maquina_id",
                "linha",
                "fabrica",
                "turno",
                "status",
                "motivo_id",
                "motivo_nome",
                "problema",
                "solucao",
                "tempo_registro_min",
                "data_hora_registro",
                "data_hora_final",
                "usuario_id_maq_occ",
                "data_hora_registro_operador",
                "usuario_id_maq_cadastro",
                "domingo_feriado_emenda",
            ]
        ]

        # Ordenar pela maquina e hora
        df_info.sort_values(
            by=["maquina_id", "data_hora_registro"],
            ascending=[True, False],
            inplace=True,
        )

        # Ajustar o index
        df_info.reset_index(drop=True, inplace=True)

        return df_info

    def join_info_prod_cad(
        self, info: pd.DataFrame, cad: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Une os dados de info e prod
        """

        # Ordenar os dataframes
        df_info = info.sort_values(by=["data_hora_registro"])
        df_cad = cad.sort_values(by=["data_hora_registro"])

        # Unir baseado na coluna data_hora_registro
        df_info_cad = pd.merge_asof(
            df_info,
            df_cad,
            on="data_hora_registro",
            by="maquina_id",
            direction="backward",
        )

        # Ordenar pela maquina e hora
        df_info_cad.sort_values(
            by=["maquina_id", "data_hora_registro"],
            ascending=[True, False],
            inplace=True,
        )

        # Reordenar as colunas
        df_info_cad = df_info_cad[
            [
                "maquina_id",
                "linha",
                "fabrica",
                "turno",
                "contagem_total_ciclos",
                "contagem_total_produzido",
                "data_registro",
                "usuario_id_maq_cadastro",
                "data_hora_registro",
            ]
        ]

        # Ajustar o index
        df_info_cad.reset_index(drop=True, inplace=True)

        return df_info_cad
