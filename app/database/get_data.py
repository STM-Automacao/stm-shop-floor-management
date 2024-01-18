"""
    Esse módulo é responsável por realizar a leitura dos dados do banco de dados.
    É utilizada para fazer a leitura em segundo plano, sem que o usuário perceba.
"""
import pandas as pd

# pylint: disable=E0401
from database.db_read import Read
from service.clean_data import CleanData
from service.join_data import JoinData
from service.problems_chart_adjust import ProblemsChartAdjust


# cSpell: words automacao, ocorrencia
class GetData:
    """
    Essa classe é responsável por realizar a leitura dos dados do banco de dados.
    É utilizada para fazer a leitura em segundo plano, sem que o usuário perceba.
    """

    def __init__(self):
        self.db_read = Read()
        self.clean_df = CleanData()
        self.join_df = JoinData()
        self.problems_chart_adjust = ProblemsChartAdjust()

    def get_data(self) -> tuple:
        """
        Realiza a leitura dos dados do banco de dados.
        Retorna na ordem: df_occ, df_info, df_cadastro
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

    def get_cleaned_data(self) -> tuple:
        """
        Recebe a leitura dos dados do banco de dados e faz a limpeza dos dados.
        Retorna na ordem: df_maq_info_cadastro, df_maq_info_prod_cad
        """
        data = self.get_data()
        # Dados do banco de dados (dataframe)
        df_occ, df_info, df_cadastro = data
        print("========== Limpando dados ==========")
        # Limpeza inicial dos dados
        df_occ = self.clean_df.clean_maq_occ(df_occ)
        df_info_cleaned = self.clean_df.clean_maq_info(df_info)
        df_info_prod = self.clean_df.clean_maq_info_prod(df_info)
        df_cadastro = self.clean_df.clean_maq_cadastro(df_cadastro)
        print("Ok...")
        print("========== Juntando dados ==========")
        # Junção dos dados
        df_info_occ = self.join_df.join_info_occ(df_occ, df_info_cleaned)
        df_info_occ = self.join_df.adjust_position(df_info_occ)
        df_info_occ = self.problems_chart_adjust.problems_adjust(df_info_occ)
        df_maq_info_cadastro = self.join_df.info_cadastro_combine(
            df_info_occ, df_cadastro
        )
        df_maq_info_prod_cad = self.join_df.join_info_prod_cad(
            df_info_prod, df_cadastro
        )
        print(f"Ok ás {pd.to_datetime('today')}")
        # Retorno dos dados
        return df_maq_info_cadastro, df_maq_info_prod_cad

    def get_last_month_data(self) -> tuple:
        """
        Recebe a leitura dos dados do banco de dados e faz a limpeza dos dados.
        Dados referentes ao mês anterior ao atual.
        Retorna na ordem: df_maq_info_cadastro, df_maq_info_prod_cad
        """

        # Dia de hoje
        now = pd.to_datetime("today")

        # Encontrando primeiro dia do mês atual
        first_day_this_month = now.replace(day=1)

        # Encontrando primeiro e último dia do mês anterior
        last_month = first_day_this_month - pd.DateOffset(months=1)
        first_day_last_month = last_month.replace(day=1)
        last_day_last_month = last_month.replace(day=last_month.days_in_month)

        # Mantendo apenas a data
        first_day = first_day_last_month.strftime("%Y-%m-%d")
        last_day = last_day_last_month.strftime("%Y-%m-%d")

        # Query para leitura dos dados de ocorrência
        query_occ = self.db_read.create_automacao_query(
            table="maquina_ocorrencia",
            where=f"data_registro >= '{first_day}' AND data_registro <= '{last_day}'",
        )

        # Query para leitura dos dados de informações
        query_info = self.db_read.create_automacao_query(
            table="maquina_info",
            where=f"data_registro >= '{first_day}' AND data_registro <= '{last_day}'",
        )

        # Query para leitura dos dados de cadastro de máquinas
        query_cadastro = self.db_read.create_automacao_query(
            table="maquina_cadastro",
            orderby="linha, data_registro DESC, hora_registro DESC",
        )

        # Leitura dos dados
        df_occ = self.db_read.get_automacao_data(query_occ)
        df_info = self.db_read.get_automacao_data(query_info)
        df_cadastro = self.db_read.get_automacao_data(query_cadastro)

        # Limpeza inicial dos dados
        df_occ = self.clean_df.clean_maq_occ(df_occ)
        df_info_cleaned = self.clean_df.clean_maq_info(df_info)
        df_info_prod = self.clean_df.clean_maq_info_prod(df_info)
        df_cadastro = self.clean_df.clean_maq_cadastro(df_cadastro)

        # Junção dos dados
        df_info_occ = self.join_df.join_info_occ(df_occ, df_info_cleaned)
        df_info_occ = self.join_df.adjust_position(df_info_occ)
        df_info_occ = self.problems_chart_adjust.problems_adjust(df_info_occ)
        df_maq_info_cadastro = self.join_df.info_cadastro_combine(
            df_info_occ, df_cadastro
        )
        df_maq_info_prod_cad = self.join_df.join_info_prod_cad(
            df_info_prod, df_cadastro
        )

        # Retorno dos dados
        return df_maq_info_cadastro, df_maq_info_prod_cad
