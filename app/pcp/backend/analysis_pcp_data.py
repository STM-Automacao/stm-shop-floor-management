"""
Módulo de análise dos dados do PCP
"""

import pandas as pd
from pcp.helpers.types_pcp import (
    RENDIMENTO_BOLINHA,
    RENDIMENTO_BOLINHA_ATUALIZADO,
    RENDIMENTO_CHEIA,
    RENDIMENTO_REPROCESSO,
)


class AnalysisPcpData:
    """
    Classe para análise dos dados do PCP.

    Métodos:
    - get_massa_sum: Calcula a soma da massa batida a partir de um DataFrame fornecido.
    - get_week_data: Retorna os dados agrupados por semana, fabrica e turno.
    """

    def __init__(self) -> None:
        pass

    def get_massa_sum(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula a soma da massa de cada tipo de batida a partir de um DataFrame fornecido.

        Parâmetros:
        - df: pd.DataFrame: O DataFrame contendo os dados das batidas.

        Retorna:
        - pd.DataFrame: O DataFrame resultante com a soma da massa de cada tipo de batida.

        Estrutura do DataFrame de retorno:
        - Data_Registro: Data do registro.
        - Turno: Turno da batida.
        - Fabrica: Fábrica da batida.
        - Qtd_Batidas_Cheias: Quantidade de batidas cheias.
        - Peso_Batidas_Cheias: Peso total das batidas cheias.
        - Qtd_Batidas_Reprocesso: Quantidade de batidas de reprocesso.
        - Peso_Batidas_Reprocesso: Peso total das batidas de reprocesso.
        - Qtd_Batidas_Bolinha: Quantidade de batidas de bolinha.
        - Peso_Batidas_Bolinha: Peso total das batidas de bolinha.
        - Baguete_Total: Total de pães baguete produzidos.
        - Bolinha_Total: Total de pães bolinha produzidos.
        """

        # Soma da massa de cada tipo
        df_massa_agg = (
            df.groupby(["Data_Registro", "Turno", "Fabrica"])
            .agg(
                Qtd_Batidas_Cheias=("Batidas_Cheia", "sum"),
                Peso_Batidas_Cheias=("Peso_Massa_BC", "sum"),
                Qtd_Batidas_Reprocesso=("Batidas_Reprocesso", "sum"),
                Peso_Batidas_Reprocesso=("Peso_Massa_BR", "sum"),
                Qtd_Batidas_Bolinha=("Batidas_Bolinha", "sum"),
                Peso_Batidas_Bolinha=("Peso_Massa_BB", "sum"),
            )
            .reset_index()
        )

        # Cálculo de pães baguete produzidos
        df_massa_agg["Baguete_Total"] = (
            df_massa_agg["Qtd_Batidas_Cheias"] * RENDIMENTO_CHEIA
            + df_massa_agg["Qtd_Batidas_Reprocesso"] * RENDIMENTO_REPROCESSO
        )

        # Cálculo de pães bolinha produzidos
        # Garantir datas no mesmo formato
        data_corte = pd.to_datetime("2024-08-01")
        df_massa_agg["Data_Registro"] = pd.to_datetime(df_massa_agg["Data_Registro"])

        # Atualizar rendimento de bolinha
        df_massa_agg["Bolinha_Total"] = 0
        df_massa_agg.loc[df_massa_agg["Data_Registro"] < data_corte, "Bolinha_Total"] = (
            df_massa_agg["Qtd_Batidas_Bolinha"] * RENDIMENTO_BOLINHA
        )
        df_massa_agg.loc[df_massa_agg["Data_Registro"] >= data_corte, "Bolinha_Total"] = (
            df_massa_agg["Qtd_Batidas_Bolinha"] * RENDIMENTO_BOLINHA_ATUALIZADO
        )

        # Converter colunas que não são peso para inteiro
        cols = [
            "Qtd_Batidas_Cheias",
            "Qtd_Batidas_Reprocesso",
            "Qtd_Batidas_Bolinha",
            "Baguete_Total",
            "Bolinha_Total",
        ]

        df_massa_agg[cols] = df_massa_agg[cols].astype(int)

        return df_massa_agg

    def get_week_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Retorna os dados agrupados por semana, fabrica e turno.

        Parâmetros:
        - df: DataFrame contendo os dados de registro somados.

        Retorno:
        - DataFrame contendo os dados agrupados por semana, fabrica e turno.

        Estrutura do DataFrame de retorno:
        - Data_Semana: Data da semana.
        - Turno: Turno da batida.
        - Fabrica: Fábrica da batida.
        - Qtd_Batidas_Cheias: Quantidade de batidas cheias.
        - Peso_Batidas_Cheias: Peso total das batidas cheias.
        - Qtd_Batidas_Reprocesso: Quantidade de batidas de reprocesso.
        - Peso_Batidas_Reprocesso: Peso total das batidas de reprocesso.
        - Qtd_Batidas_Bolinha: Quantidade de batidas de bolinha.
        - Peso_Batidas_Bolinha: Peso total das batidas de bolinha.
        - Baguete_Total: Total de pães baguete produzidos.
        - Bolinha_Total: Total de pães bolinha produzidos.
        """

        df = df.copy()

        # Ajustar o dia da semana para começar no domingo
        df["Dia_Semana"] = df["Data_Registro"].dt.weekday
        df["Dia_Semana"] = (df["Dia_Semana"] + 1) % 7

        # Criar uma nova coluna com a data da semana
        df["Data_Semana"] = df["Data_Registro"] - pd.to_timedelta(df["Dia_Semana"], unit="d")

        # Criar uma nova tabela com os dados agrupados por semana, fabrica e turno
        df_paes = (
            df.groupby(
                [
                    df["Data_Semana"].dt.isocalendar().year,
                    df["Data_Semana"].dt.isocalendar().week,
                    "Data_Semana",
                    "Turno",
                    "Fabrica",
                ]
            )
            .agg(
                Qtd_Batidas_Cheias=("Qtd_Batidas_Cheias", "sum"),
                Peso_Batidas_Cheias=("Peso_Batidas_Cheias", "sum"),
                Qtd_Batidas_Reprocesso=("Qtd_Batidas_Reprocesso", "sum"),
                Peso_Batidas_Reprocesso=("Peso_Batidas_Reprocesso", "sum"),
                Qtd_Batidas_Bolinha=("Qtd_Batidas_Bolinha", "sum"),
                Peso_Batidas_Bolinha=("Peso_Batidas_Bolinha", "sum"),
                Baguete_Total=("Baguete_Total", "sum"),
                Bolinha_Total=("Bolinha_Total", "sum"),
            )
            .reset_index()
        )

        return df_paes

    def get_pasta_analysis(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Realiza a análise dos dados de pasta.

        Args:
            df (pd.DataFrame): O DataFrame contendo os dados de pasta.

        Returns:
            pd.DataFrame: O DataFrame resultante da análise dos dados de pasta.
        """

        # Remove espaço em branco do Produto
        df.Produto = df.Produto.str.strip()

        # Substitui o espaço por _
        df.Produto = df.Produto.str.replace(" ", "_")

        # Cria colunas auxiliares para pivotar
        df["Produto_Batidas"] = df.Produto.str.title() + "_Batidas"
        df["Produto_Peso"] = df.Produto.str.title() + "_Peso"

        # Pivotar Produto Batidas
        df_pivot_batidas = df.pivot_table(
            index=["Data_Registro", "Turno", "Fabrica"],
            columns="Produto_Batidas",
            values="Batidas_Pasta",
            aggfunc="sum",
            fill_value=0,
        )

        # Pivotar Produto Peso
        df_pivot_peso = df.pivot_table(
            index=["Data_Registro", "Turno", "Fabrica"],
            columns="Produto_Peso",
            values="Peso_Pasta",
            aggfunc="sum",
            fill_value=0,
        )

        # Merge dos DataFrames
        df_pasta = pd.concat([df_pivot_batidas, df_pivot_peso], axis=1).reset_index()

        return df_pasta

    def get_pasta_week_analysis(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Retorna uma tabela com os dados de análise semanal das pastas.

        Args:
            df (pd.DataFrame): O dataframe contendo os dados de registro das pastas.

        Returns:
            pd.DataFrame: Um dataframe contendo os dados agrupados por semana, fabrica e turno,
            com as seguintes colunas:

            - Tradicional_Peso: Soma dos pesos das pastas tradicionais.
            - Tradicional_Batidas: Soma das batidas das pastas tradicionais.
            - Picante_Batidas: Soma das batidas das pastas picantes.
            - Picante_Peso: Soma dos pesos das pastas picantes.
            - Cebola_Batidas: Soma das batidas das pastas de cebola.
            - Cebola_Peso: Soma dos pesos das pastas de cebola.
            - Pasta_Doce_Batidas: Soma das batidas das pastas doces.
            - Pasta_Doce_Peso: Soma dos pesos das pastas doces.
        """

        df = df.copy()

        # Ajustar o dia da semana para começar no domingo
        df["Dia_Semana"] = df["Data_Registro"].dt.weekday
        df["Dia_Semana"] = (df["Dia_Semana"] + 1) % 7

        # Criar uma nova coluna com a data da semana
        df["Data_Semana"] = df["Data_Registro"] - pd.to_timedelta(df["Dia_Semana"], unit="d")

        # Criar uma nova tabela com os dados agrupados por semana, fabrica e turno
        df_pasta = (
            df.groupby(
                [
                    df["Data_Semana"].dt.isocalendar().year,
                    df["Data_Semana"].dt.isocalendar().week,
                    "Data_Semana",
                    "Turno",
                    "Fabrica",
                ]
            )
            .agg(
                Tradicional_Peso=("Tradicional_Peso", "sum"),
                Tradicional_Batidas=("Tradicional_Batidas", "sum"),
                Picante_Batidas=("Picante_Batidas", "sum"),
                Picante_Peso=("Picante_Peso", "sum"),
                Cebola_Batidas=("Cebola_Batidas", "sum"),
                Cebola_Peso=("Cebola_Peso", "sum"),
                Doce_Batidas=("Pasta_Doce_Batidas", "sum"),
                Doce_Peso=("Pasta_Doce_Peso", "sum"),
            )
            .reset_index()
        )

        return df_pasta
