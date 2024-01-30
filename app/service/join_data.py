"""
    Módulo para unir os dados de cadastro, info e ocorrência
"""

import numpy as np
import pandas as pd
from fuzzywuzzy import process


# cSpell: words solucao, usuario, sabado, idxmin, skipna
class JoinData:
    """
    Classe para unir os dados de cadastro, info e ocorrência
    """

    # Função Auxiliar
    def move_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Move as colunas para a posição desejada.
        """

        # Adiciona uma verificação para garantir que não haja valores nulos
        mask = (
            df[["data_hora_registro_occ", "data_hora_registro", "data_hora_final"]]
            .notna()
            .all(axis=1)
        )

        df["data_hora_registro_occ"] = df["data_hora_registro_occ"].replace(np.nan, pd.NaT)
        df = df.astype({"data_hora_registro_occ": "datetime64[ns]"})

        # Calcula a diferença de data_hora_registro_occ e data_hora_registro e data_hora_final
        df["diff_registro"] = np.where(
            mask,
            (df["data_hora_registro_occ"] - df["data_hora_registro"]).dt.total_seconds().abs(),
            np.nan,
        )
        df["diff_final"] = np.where(
            mask,
            (df["data_hora_registro_occ"] - df["data_hora_final"]).dt.total_seconds().abs(),
            np.nan,
        )

        # Encontra qual das duas diferenças é menor
        mask_idxmin = df[["diff_registro", "diff_final"]].notna().any(axis=1)
        df.loc[mask & mask_idxmin, "closest"] = df.loc[
            mask & mask_idxmin, ["diff_registro", "diff_final"]
        ].idxmin(
            axis=1
        )  # removendo erro:
        # FutureWarning: The behavior of DataFrame.idxmin with all-NA values,
        # or any-NA and skipna=False, is deprecated.
        # In a future version this will raise ValueError

        columns = [
            "motivo_id",
            "motivo_nome",
            "problema",
            "solucao",
            "data_hora_registro_occ",
            "usuario_id_occ",
        ]

        # Move a ocorrência para a linha anterior se a data_hora_registro for mais próxima
        mask = (
            (df["closest"].shift(-1) == "diff_registro")
            & (df["status"].shift(-1) == "rodando")
            & df["motivo_id"].isnull()
        )
        for column in columns:
            df[column] = np.where(mask, df[column].shift(-1), df[column])
            df[column] = np.where(mask.shift(1), pd.NaT, df[column])

        # Move a ocorrência para a linha seguinte se a data_hora_final for mais próxima
        mask = (
            (df["closest"].shift(1) == "diff_final")
            & (df["status"].shift(1) == "rodando")
            & df["motivo_id"].isnull()
        )
        for column in columns:
            df[column] = np.where(mask, df[column].shift(1), df[column])
            df[column] = np.where(mask.shift(-1), pd.NaT, df[column])

        return df

    def join_info_occ(self, df_occ: pd.DataFrame, df_info: pd.DataFrame) -> pd.DataFrame:
        """
        Junta os dados de ocorrências e paradas.

        Args:
            df_occ (pd.DataFrame): DataFrame com os dados de ocorrências.
            df_info (pd.DataFrame): DataFrame com os dados de paradas.

        Returns:
            pd.DataFrame: DataFrame com os dados de ocorrências e paradas juntos.
        """

        # Garantir que as colunas com datas sejam datetime
        df_occ["data_hora_registro"] = pd.to_datetime(df_occ["data_hora_registro"])
        df_info["data_hora_registro"] = pd.to_datetime(df_info["data_hora_registro"])
        df_info["data_hora_final"] = pd.to_datetime(df_info["data_hora_final"])

        # Juntar os dados de ocorrências e paradas
        def merge_rows(row):
            """
            Função para juntar os dados de ocorrências e paradas.
            """
            mask = (
                (df_occ["maquina_id"] == row["maquina_id"])
                & (df_occ["data_hora_registro"] >= row["data_hora_registro"])
                & (df_occ["data_hora_registro"] <= row["data_hora_final"])
            )  # mask para identificar as paradas que ocorreram durante a ocorrência

            # Criar dataframe com as paradas que ocorreram durante a ocorrência
            if df_occ[mask].shape[0] > 0:
                return pd.Series(
                    [
                        df_occ[mask]["motivo_id"].values[0],
                        df_occ[mask]["motivo_nome"].values[0],
                        df_occ[mask]["problema"].values[0],
                        df_occ[mask]["solucao"].values[0],
                        df_occ[mask]["data_hora_registro"].values[0],
                        df_occ[mask]["usuario_id"].values[0],
                    ],
                )

            return pd.Series([np.nan, np.nan, np.nan, np.nan, np.nan, np.nan])

        # Aplicar a função merge_rows
        df_info[
            [
                "motivo_id",
                "motivo_nome",
                "problema",
                "solucao",
                "data_hora_registro_occ",
                "usuario_id_occ",
            ]
        ] = df_info.apply(merge_rows, axis=1)

        # Reordenar colunas
        df_info = df_info.reindex(
            columns=[
                "maquina_id",
                "linha",
                "fabrica",
                "turno",
                "data_hora_registro",
                "tempo_registro_min",
                "data_hora_final",
                "status",
                "motivo_id",
                "data_hora_registro_occ",
                "motivo_nome",
                "problema",
                "solucao",
                "usuario_id_occ",
                "contagem_total_ciclos",
                "contagem_total_produzido",
                "sabado",
                "domingo",
                "feriado",
            ]
        )

        # Ajustar problema e solução caso seja "nan"
        df_info["problema"] = np.where(df_info["problema"] == "nan", np.nan, df_info["problema"])
        df_info["solucao"] = np.where(df_info["solucao"] == "nan", np.nan, df_info["solucao"])

        # Remove a linha com tempo_registro_min negativo ou 0
        df_info = df_info[df_info["tempo_registro_min"] > 0]

        df_info = self.move_columns(df_info)

        # Remove colunas desnecessárias
        df_info.drop(
            columns=[
                "diff_registro",
                "diff_final",
                "closest",
            ],
            inplace=True,
        )

        # Ajustar motivo id
        df_info["motivo_id"] = df_info["motivo_id"].fillna(np.nan).round(0).astype(float)

        # Ajustar em problema, solucao, usuario_id_occ e motivo_nome
        df_info["problema"] = df_info["problema"].fillna("")
        df_info["solucao"] = df_info["solucao"].fillna("")
        df_info["usuario_id_occ"] = np.where(
            df_info["usuario_id_occ"] == pd.NaT, np.nan, df_info["usuario_id_occ"]
        )
        df_info["motivo_nome"] = np.where(
            df_info["motivo_nome"] == pd.NaT, np.nan, df_info["motivo_nome"]
        )
        # Mudar de np.nan para pd.NaT em data_hora_registro_occ
        df_info["data_hora_registro_occ"] = np.where(
            df_info["data_hora_registro_occ"].isnull(), pd.NaT, df_info["data_hora_registro_occ"]
        )

        # Corrigir os formatos das colunas
        df_info = df_info.astype(
            {
                "data_hora_registro_occ": "datetime64[ns]",
                "motivo_nome": "category",
                "problema": str,
                "solucao": str,
                "usuario_id_occ": "category",
            }
        )

        # Ajustar problema para Domingo, Sábado e Feriado se motivo_id for 12
        df_info["problema"] = np.where(
            (df_info["motivo_id"] == 12) & (df_info["domingo"] == 1),
            "Domingo",
            df_info["problema"],
        )
        df_info["problema"] = np.where(
            (df_info["motivo_id"] == 12) & (df_info["sabado"] == 1),
            "Sábado",
            df_info["problema"],
        )
        df_info["problema"] = np.where(
            (df_info["motivo_id"] == 12) & (df_info["feriado"] == 1),
            "Feriado",
            df_info["problema"],
        )

        # Ajustar motivo 12 para Sábado, Domingo e Feriado
        condition = (
            (df_info["motivo_id"].isnull())
            & (df_info["status"] == "parada")
            & (df_info["tempo_registro_min"] > 475)
        )
        condition_sabado = condition & (df_info["sabado"] == 1)
        df_info["motivo_id"] = np.where(condition_sabado, 12, df_info["motivo_id"])
        df_info["motivo_nome"] = np.where(
            condition_sabado, "Parada Programada", df_info["motivo_nome"]
        )
        df_info["problema"] = np.where(condition_sabado, "Sábado", df_info["problema"])

        condition_domingo = condition & (df_info["domingo"] == 1)
        df_info["motivo_id"] = np.where(condition_domingo, 12, df_info["motivo_id"])
        df_info["motivo_nome"] = np.where(
            condition_domingo, "Parada Programada", df_info["motivo_nome"]
        )
        df_info["problema"] = np.where(condition_domingo, "Domingo", df_info["problema"])

        condition_feriado = condition & (df_info["feriado"] == 1)
        df_info["motivo_id"] = np.where(condition_feriado, 12, df_info["motivo_id"])
        df_info["motivo_nome"] = np.where(
            condition_feriado, "Parada Programada", df_info["motivo_nome"]
        )
        df_info["problema"] = np.where(condition_feriado, "Feriado", df_info["problema"])

        # Cria a máscara para as linhas que atendem às condições
        mask = (df_info["tempo_registro_min"] > 475) & df_info["motivo_id"].isnull()

        # Cria colunas temporárias com os valores preenchidos
        df_info["motivo_id_filled"] = df_info["motivo_id"].ffill()
        df_info["motivo_nome_filled"] = df_info["motivo_nome"].ffill()
        df_info["problema_filled"] = df_info["problema"].ffill()
        df_info["solucao_filled"] = df_info["solucao"].ffill()

        # Aplica a máscara e substitui os valores nas colunas originais
        df_info.loc[mask, "motivo_id"] = df_info.loc[mask, "motivo_id_filled"]
        df_info.loc[mask, "motivo_nome"] = df_info.loc[mask, "motivo_nome_filled"]
        df_info.loc[mask, "problema"] = df_info.loc[mask, "problema_filled"]
        df_info.loc[mask, "solucao"] = df_info.loc[mask, "solucao_filled"]

        # Remove as colunas temporárias
        df_info = df_info.drop(
            columns=["motivo_id_filled", "motivo_nome_filled", "problema_filled", "solucao_filled"]
        )

        # Se o tempo de registro for maior que 480 mudar para 480
        df_info["tempo_registro_min"] = np.where(
            df_info["tempo_registro_min"] > 480, 480, df_info["tempo_registro_min"]
        )

        # Remover as linhas onde a linha é 0
        df_info = df_info[df_info["linha"] != 0]

        # Remover as linhas onde status é rodando
        df_info = df_info[df_info["status"] != "rodando"]

        # Ajustar o index
        df_info.reset_index(drop=True, inplace=True)

        return df_info

    def problems_adjust(self, df: pd.DataFrame, threshold=88) -> pd.DataFrame:
        """
        Ajusta os problemas no DataFrame fornecido,
        mapeando problemas semelhantes para um nome comum.

        Args:
            df (pd.DataFrame): O DataFrame contendo os problemas a serem ajustados.
            threshold (int, opcional): O limite de similaridade para combinar problemas.
            Por padrão é 88.

        Returns:
            pd.DataFrame: O DataFrame com problemas ajustados.
        """
        # Encontrar problemas únicos
        unique_problems = df["problema"].unique()
        problem_mapping = {}

        # Criar um dicionário para mapear os problemas
        for problem in unique_problems:
            if problem and problem not in problem_mapping:
                problem = str(problem).capitalize()

                # Corrigir erros básicos de digitação
                problem = problem.replace("Beckup", "Backup")
                problem = problem.replace("Becukp", "Backup")
                problem = problem.replace("Stm", "Atm")

                matches = process.extract(problem, unique_problems, limit=len(unique_problems))

                # Encontrar os problemas com maior similaridade
                similar_problems = [match[0] for match in matches if match[1] >= threshold]

                # Criar um dicionário com os problemas similares
                for similar_problem in similar_problems:
                    problem_mapping[similar_problem] = problem

        # Mapear os problemas
        df["problema"] = df["problema"].map(problem_mapping)

        return df
