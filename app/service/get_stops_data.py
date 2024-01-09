"""
    Arquivo com a classe GetStopsData
"""
import pandas as pd
import numpy as np
from fuzzywuzzy import process

# cSpell: words solucao, usuario, dayofweek


class GetStopsData:
    """
    Classe para consolidar os dados de paradas
    """

    def __init__(self):
        pass

    def get_stops_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Retorna um dataframe com os dados de paradas consolidados

        Args:
        -----
            df (pd.DataFrame): Dataframe com os dados de paradas

        Retorna:
        --------
            pd.DataFrame: Dataframe com os dados de paradas consolidados

        Exemplo:
        --------

            >>> from app.service.get_stops_data import GetStopsData
            >>> import pandas as pd
            >>> get_stops_data = GetStopsData()
            >>> df_stops = get_stops_data.get_stops_data(df)

        """

        # Se o motivo_id for nulo, preencher com 0
        df.loc[
            (df["motivo_id"].isnull()) & (df["status"] != "rodando"),
            "motivo_id",
        ] = 0

        # Transformar data e hora em datetime
        df["data_hora_registro_operador"] = pd.to_datetime(
            df["data_hora_registro_operador"]
        )
        df["data_hora_registro"] = pd.to_datetime(df["data_hora_registro"])
        df["data_hora_final"] = pd.to_datetime(df["data_hora_final"])

        # Ordenar por maquina_id, turno, data_hora_registro
        df.sort_values(
            by=["maquina_id", "turno", "data_hora_registro"], inplace=True
        )

        # Criar coluna data_hora_registro_turno para identificar onde está rodando
        df["rodando"] = df["motivo_id"].isnull()

        # Cria uma coluna grupo para identificar os grupos de paradas
        df["grupo"] = (
            (df["rodando"] != df["rodando"].shift())
            | (df["maquina_id"] != df["maquina_id"].shift())
            | (df["turno"] != df["turno"].shift())
            | (
                df["data_hora_registro"].dt.date
                != df["data_hora_registro"].shift().dt.date
            )
        )

        # Soma o tempo de parada por grupo
        df["grupo"] = df["grupo"].cumsum()

        # Agregar os dados por grupo
        df = (
            df.groupby("grupo")
            .agg(
                {
                    "maquina_id": "first",
                    "turno": "first",
                    "status": "first",
                    "motivo_id": "first",
                    "motivo_nome": "first",
                    "problema": "first",
                    "solucao": "first",
                    "tempo_registro_min": "sum",
                    "data_hora_registro": "first",
                    "data_hora_final": "last",
                    "data_hora_registro_operador": "first",
                    "usuario_id": "first",
                }
            )
            .reset_index(drop=True)
        )

        # Ordenar por maquina_id, data_hora_registro
        df.sort_values(by=["maquina_id", "data_hora_registro"], inplace=True)

        # Remover linhas onde a maquina está rodando
        df = df[df["status"] != "rodando"]

        # Substituir status in_test por parada
        df.loc[df["status"] == "in_test", "status"] = "parada"

        # Substituir valores nulos por np.nan
        df.fillna(np.nan, inplace=True)

        # Reiniciar o index
        df.reset_index(drop=True, inplace=True)

        return df

    def dayofweek_adjust(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Ajusta o dia da semana para incluir paradas programadas

        Args:
        -----
            df (pd.DataFrame): Dataframe com os dados de paradas

        Retorna:
        --------
            pd.DataFrame: Dataframe com os dados de paradas ajustados

        Exemplo:
        --------

            >>> from app.service.get_stops_data import GetStopsData
            >>> import pandas as pd
            >>> get_stops_data = GetStopsData()
            >>> df_stops = get_stops_data.dayofweek_adjust(df)

        """

        # Garantir que a coluna data_hora_registro é datetime
        df["data_hora_registro"] = pd.to_datetime(df["data_hora_registro"])

        # Identificar os domingos
        df["domingo"] = df["data_hora_registro"].dt.dayofweek == 6

        # Listar feriados
        feriados = pd.read_csv("../database/feriados.csv")

        # Converter a coluna data para datetime
        feriados["feriados"] = pd.to_datetime(feriados["feriados"])

        # Identificar os feriados
        df["feriado"] = df["data_hora_registro"].dt.date.isin(
            feriados["feriados"].dt.date
        )

        # Identificar os dias após os feriados
        feriados["dia_apos_feriado"] = feriados["feriados"] + pd.Timedelta(
            days=1
        )
        df["dia_apos_feriado"] = df["data_hora_registro"].dt.date.isin(
            feriados["dia_apos_feriado"].dt.date
        )

        # Criar nova coluna unindo domingo, feriado e dia após feriado e descartar
        # as colunas domingo, feriado e dia após feriado
        df["domingo_feriado_emenda"] = (
            df["domingo"] | df["feriado"] | df["dia_apos_feriado"]
        )
        df.drop(
            columns=["domingo", "feriado", "dia_apos_feriado"], inplace=True
        )

        # Definir o status como 12, motivo_nome "Parada Programada" e problema "Domingo/Feriado"
        # para os domingos e feriados onde o motivo_nome é nulo
        df.loc[
            (df["domingo_feriado_emenda"]) & (df["tempo_registro_min"] >= 478),
            ["status", "motivo_id", "motivo_nome", "problema"],
        ] = ["parada", 12, "Parada Programada", "Domingo/Feriado"]

        # Definir como motivo_id 12 e motivo_nome "Parada Programada" se o problema for
        # "Parada Programada"
        df.loc[
            df["problema"] == "Parada Programada",
            ["motivo_id", "motivo_nome"],
        ] = [12, "Parada Programada"]

        return df

    def problems_adjust(self, df: pd.DataFrame, threshold=88) -> pd.DataFrame:
        """
        Ajusta os problemas

        Args:
        -----
            df (pd.DataFrame): Dataframe com os dados de paradas
            threshold (int): Limiar de similaridade para identificar os problemas

        Retorna:
        --------
            pd.DataFrame: Dataframe com os dados de paradas ajustados

        Exemplo:
        --------
            >>> from app.service.get_stops_data import GetStopsData
            >>> import pandas as pd
            >>> get_stops_data = GetStopsData()
            >>> df_stops = get_stops_data.problems_adjust(df)
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

                matches = process.extract(
                    problem, unique_problems, limit=len(unique_problems)
                )

                # Encontrar os problemas com maior similaridade
                similar_problems = [
                    match[0] for match in matches if match[1] >= threshold
                ]

                # Criar um dicionário com os problemas similares
                for similar_problem in similar_problems:
                    problem_mapping[similar_problem] = problem

        # Mapear os problemas
        df["problema"] = df["problema"].map(problem_mapping)

        return df

    def get_stops_data_complete(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Retorna um dataframe com os dados de paradas consolidados

        Args:
        -----
            df (pd.DataFrame): Dataframe com os dados de paradas

        Retorna:
        --------
            pd.DataFrame: Dataframe com os dados de paradas consolidados

        Exemplo:
        --------

            >>> from app.service.get_stops_data import GetStopsData
            >>> import pandas as pd
            >>> get_stops_data = GetStopsData()
            >>> df_stops = get_stops_data.get_stops_data_complete(df)

        """

        # Consolidar os dados de paradas
        df = self.get_stops_data(df)

        # Ajustar o dia da semana
        df = self.dayofweek_adjust(df)

        # Ajustar os problemas
        df = self.problems_adjust(df)

        # Ajustar o index
        df.reset_index(drop=True, inplace=True)

        return df
