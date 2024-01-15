"""
    Esse módulo é responsável por realizar a leitura dos dados do banco de dados.
    É utilizada para fazer a leitura em segundo plano, sem que o usuário perceba.
"""
import pandas as pd
from database.db_read import Read


# cSpell: words automacao, ocorrencia
class GetData:
    """
    Essa classe é responsável por realizar a leitura dos dados do banco de dados.
    É utilizada para fazer a leitura em segundo plano, sem que o usuário perceba.
    """

    def __init__(self):
        self.db_read = Read()

    def get_data(self):
        """
        Realiza a leitura dos dados do banco de dados.
        """

        # Dia de hoje
        now = pd.to_datetime("today")

        # Encontrando primeiro dia do mês atual
        first_day = now.replace(day=1)

        # Mantendo apenas a data
        first_day = first_day.strftime("%Y-%m-%d")

        # Query para leitura dos dados de ocorrência
        query_occ = self.db_read.create_automacao_query(
            table="maquina_ocorrencia",
            where=f"data_registro >= '{first_day}'",
        )

        # Query para leitura dos dados de informações
        query_info = self.db_read.create_automacao_query(
            table="maquina_info",
            where=f"data_registro >= '{first_day}'",
        )

        # Query para leitura dos dados de cadastro de máquinas
        query_cadastro = self.db_read.create_automacao_query(
            table="maquina_cadastro",
            orderby="linha, data_registro DESC, hora_registro DESC",
        )

        print("========== Baixando dados do DB ==========")

        # Leitura dos dados
        df_occ = self.db_read.get_automacao_data(query_occ)
        df_info = self.db_read.get_automacao_data(query_info)
        df_cadastro = self.db_read.get_automacao_data(query_cadastro)

        # Verificando se os dados foram lidos corretamente
        if df_occ.empty or df_info.empty or df_cadastro.empty:
            print("====== Erro na leitura dos dados ======")
            return None

        print("Ok...")

        return df_occ, df_info, df_cadastro
