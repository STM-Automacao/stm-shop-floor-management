"""
    Arquivo com a classe ProblemsChartAdjust
"""
import pandas as pd
from fuzzywuzzy import process


class ProblemsChartAdjust:
    """
    Classe para consolidar os dados de paradas
    """

    def __init__(self):
        pass

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
