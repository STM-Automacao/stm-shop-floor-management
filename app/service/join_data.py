"""
    Módulo para unir os dados de cadastro, info e ocorrência
"""

import pandas as pd


# cSpell: words solucao, usuario
class JoinData:
    """
    Classe para unir os dados de cadastro, info e ocorrência
    """

    def __init__(self):
        pass

    def join_info_occ(
        self, occ: pd.DataFrame, info: pd.DataFrame
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

        df_occ = occ.copy()
        df_info = info.copy()

        # Garantir que as colunas de data sejam do tipo datetime
        df_occ["data_hora_registro"] = pd.to_datetime(
            df_occ["data_hora_registro"]
        )
        df_info["data_hora_registro"] = pd.to_datetime(
            df_info["data_hora_registro"]
        )
        df_info["data_hora_final"] = pd.to_datetime(df_info["data_hora_final"])

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

        # Definir o status como 12, motivo_nome "Parada Programada" e problema "Domingo/Feriado"
        # para os domingos e feriados onde o motivo_nome é nulo
        df_info.loc[
            (df_info["domingo_feriado_emenda"])
            & (df_info["tempo_registro_min"] >= 478),
            ["status", "motivo_id", "motivo_nome", "problema"],
        ] = ["parada", 12, "Parada Programada", "Domingo/Feriado"]

        # Definir como motivo_id 12 e motivo_nome "Parada Programada"
        # se o problema for "Parada Programada"
        df_info.loc[
            df_info["problema"] == "Parada Programada",
            ["motivo_id", "motivo_nome"],
        ] = [12, "Parada Programada"]

        # Reordenar as colunas
        df_info = df_info[
            [
                "maquina_id",
                "turno",
                "status",
                "motivo_id",
                "motivo_nome",
                "problema",
                "solucao",
                "tempo_registro_min",
                "data_hora_registro",
                "data_hora_final",
                "usuario_id",
                "data_hora_registro_operador",
                "domingo_feriado_emenda",
            ]
        ]

        # Ajustar o index
        df_info.reset_index(drop=True, inplace=True)

        return df_info

    def adjust_position(self, info: pd.DataFrame) -> pd.DataFrame:
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

        df = info.copy()

        # Listar paradas que podem ter sido lançadas adiantadas
        paradas_adiantadas = [2, 3, 4, 5, 6, 10, 11, 13, 15, 17]

        # Se na linha anterior o motivo_id for uma parada adiantada,
        # e o status for rodando, copiar o motivo_id
        # e motivo_nome para a linha atual
        df.loc[
            (df["motivo_id"].shift(1).isin(paradas_adiantadas))
            & (df["status"].shift(1) == "rodando"),
            [
                "motivo_id",
                "motivo_nome",
                "problema",
                "solucao",
                "data_hora_registro_operador",
                "usuario_id",
            ],
        ] = df[
            [
                "motivo_id",
                "motivo_nome",
                "problema",
                "solucao",
                "data_hora_registro_operador",
                "usuario_id",
            ]
        ].shift(
            1
        )

        # Definir paradas marcadas atrasadas
        paradas_atrasadas = [1, 7, 8]

        # Corrigir paradas atrasadas
        df.loc[
            (df["motivo_id"].shift(-1).isin(paradas_atrasadas))
            & (df["status"].shift(-1) == "rodando")
            & (df["motivo_id"]),
            [
                "motivo_id",
                "motivo_nome",
                "problema",
                "solucao",
                "data_hora_registro_operador",
                "usuario_id",
            ],
        ] = df[
            [
                "motivo_id",
                "motivo_nome",
                "problema",
                "solucao",
                "data_hora_registro_operador",
                "usuario_id",
            ]
        ].shift(
            -1
        )

        return df

    def info_cadastro_combine(
        self, info: pd.DataFrame, cadastro: pd.DataFrame
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
        df_info = info.sort_values(by=["data_hora_registro"])
        df_cadastro = cadastro.sort_values(by=["data_hora_registro"])

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
            by=["maquina_id", "data_hora_registro", "turno"],
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
            by=["maquina_id", "data_hora_registro", "turno"],
            ascending=True,
            inplace=True,
        )

        # Renomear usuario id
        df_info_cad.rename(
            columns={"usuario_id": "usuario_id_maq_cadastro"}, inplace=True
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
