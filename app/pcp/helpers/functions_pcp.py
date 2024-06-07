"""
Funções que pode ser reaproveitadas em outros módulos.
"""

import pandas as pd
from pcp.helpers.types_pcp import PAO_POR_BANDEJA


class AuxFuncPcp:
    """
    Funções auxiliares para o módulo PCP.
    """

    def __init__(self) -> None:
        pass

    @staticmethod
    def adjust_prod(df: pd.DataFrame) -> pd.DataFrame:
        """
        Limpa os dados de produção.

        Args:
            df (pd.DataFrame): O DataFrame contendo os dados de produção.

        Returns:
            pd.DataFrame: O DataFrame limpo.
        """
        # cSpell: words usuario emissao
        # Remover colunas desnecessárias
        df = df.drop(columns=["MAQUINA", "UNIDADE", "LOTE", "USUARIO"])
        df.PRODUTO = df.PRODUTO.str.strip()

        # ============================== Calcula Quantidade De Pães ============================== #
        # Transforma caixas em bandejas
        df.QTD = df.QTD * 10

        # Transforma bandejas em pães
        df.QTD = df.QTD * df.PRODUTO.map(PAO_POR_BANDEJA)

        # ======================================== Agrupa ======================================== #
        df = df.groupby(["FABRICA", "PRODUTO", "EMISSAO"]).QTD.sum().reset_index()

        # Ajustar a data de yyyymmdd para o formato yyyy-mm-dd
        df.EMISSAO = pd.to_datetime(df.EMISSAO, format="%Y%m%d")

        # Nova coluna dia_semana, ajustando para começar no domingo
        df["Data_Semana"] = (df.EMISSAO.dt.weekday + 1) % 7

        # Nova coluna com a data da semana
        df["Data_Semana"] = df.EMISSAO - pd.to_timedelta(df.Data_Semana, unit="d")

        # Agrupar por semana, fabrica e produto
        df = (
            df.groupby(
                [
                    df.Data_Semana.dt.isocalendar().year,
                    df.Data_Semana.dt.isocalendar().week,
                    "Data_Semana",
                    "PRODUTO",
                    "FABRICA",
                ]
            )
            .QTD.sum()
            .reset_index()
        )

        return df
