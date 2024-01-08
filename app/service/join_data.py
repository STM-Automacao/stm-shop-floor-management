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
        self.df_info = pd.DataFrame()
        self.df_cadastro = pd.DataFrame()
        self.df_occ = pd.DataFrame()
        self.df_join = pd.DataFrame()

    def join_info_occ(
        self, occ: pd.DataFrame, info: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Une os dados de info e ocorrência
        """

        self.df_info = info.copy()
        self.df_occ = occ.copy()

        # Criar uma função para ser usada em cada linha do dataframe
        def merge_rows(row):
            # Selecionar rows onde a data_hora_registro de occ está entre
            # data_hora_registro e data_hora_final de info
            mask = (
                (
                    self.df_occ["data_hora_registro"]
                    >= row["data_hora_registro"]
                )
                & (self.df_occ["data_hora_registro"] <= row["data_hora_final"])
                & (self.df_occ["maquina_id"] == row["maquina_id"])
            )

            # Se houver rows selecionadas, retornar uma serie contendo os valores
            if self.df_occ.loc[mask].shape[0] > 0:
                return pd.Series(
                    [
                        self.df_occ.loc[mask, "motivo_id"].values[0],
                        self.df_occ.loc[mask, "motivo_nome"].values[0],
                        self.df_occ.loc[mask, "problema"].values[0],
                        self.df_occ.loc[mask, "solucao"].values[0],
                        self.df_occ.loc[mask, "data_hora_registro"].values[0],
                        self.df_occ.loc[mask, "usuario_id"].values[0],
                    ]
                )
            else:
                return pd.Series([None, None, None, None, None, None])

        # Aplicar a função merge_rows em cada linha do dataframe
        self.df_info[
            [
                "motivo_id",
                "motivo_nome",
                "problema",
                "solucao",
                "data_hora_registro_operador",
                "usuario_id",
            ]
        ] = self.df_info.apply(merge_rows, axis=1)

        # Ajustar para sempre que estiver parada por motivo
        # 3, 4, 5, 12, 15, 16, o status será rodando
        self.df_info.loc[
            (self.df_info["status"] == "in_test")
            & (self.df_info["motivo_id"].shift(1).isin([3, 4, 5, 12, 15, 16])),
            "status",
        ] = "rodando"

        # Ajustar o index
        self.df_info.reset_index(drop=True, inplace=True)

        return self.df_info
