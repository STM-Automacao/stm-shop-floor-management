"""
    Autor: Bruno Tomaz
    Data: 15/01/2024
    Esse módulo é responsável por realizar a leitura dos dados do banco de dados.
    É utilizada para fazer a leitura em segundo plano, sem que o usuário perceba.
"""

import pandas as pd

# pylint: disable=E0401
from database.db_read import Read
from service.clean_data import CleanData
from service.join_data import JoinData


# cSpell: words automacao, ocorrencia dateadd datediff
class GetData:
    """
    Essa classe é responsável por realizar a leitura dos dados do banco de dados.
    É utilizada para fazer a leitura em segundo plano, sem que o usuário perceba.
    """

    def __init__(self):
        self.db_read = Read()
        self.clean_df = CleanData()
        self.join_df = JoinData()

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
        query_info = (
            "SELECT"
            " t1.maquina_id,"
            " (SELECT TOP 1 t2.linha FROM AUTOMACAO.dbo.maquina_cadastro t2"
            " WHERE t2.maquina_id = t1.maquina_id AND t2.data_registro <= t1.data_registro"
            " ORDER BY t2.data_registro DESC, t2.hora_registro DESC) as linha,"
            " (SELECT TOP 1 t2.fabrica FROM AUTOMACAO.dbo.maquina_cadastro t2"
            " WHERE t2.maquina_id = t1.maquina_id AND t2.data_registro <= t1.data_registro"
            " ORDER BY t2.data_registro DESC, t2.hora_registro DESC) as fabrica,"
            " t1.status,"
            " t1.turno,"
            " t1.contagem_total_ciclos,"
            " t1.contagem_total_produzido,"
            " t1.data_registro,"
            " t1.hora_registro"
            " FROM "
            " AUTOMACAO.dbo.maquina_info t1"
            f" WHERE data_registro >= '{first_day}'"
            " ORDER BY t1.data_registro DESC, t1.hora_registro DESC"
        )

        # Query para leitura dos dados de de produção
        query_production = (
            "WITH aux AS ("
            " SELECT"
            " t1.maquina_id,"
            " t1.turno,"
            " t1.contagem_total_ciclos,"
            " t1.contagem_total_produzido,"
            " (SELECT TOP 1 t2.linha FROM AUTOMACAO.dbo.maquina_cadastro t2"
            " WHERE t2.maquina_id = t1.maquina_id AND"
            " DATEADD(minute, -1, CAST(t2.data_registro AS DATETIME) +"
            " CAST(t2.hora_registro AS DATETIME)) <="
            " CAST(t1.data_registro AS DATETIME) + CAST(t1.hora_registro AS DATETIME)"
            " ORDER BY t2.data_registro DESC, t2.hora_registro desc) as linha,"
            " CASE"
            " WHEN CAST(t1.hora_registro AS TIME) <= '00:01'"
            " THEN DATEADD(day, -1, CAST(t1.data_registro AS DATETIME))"
            " ELSE CAST(t1.data_registro AS DATETIME)"
            " END as data_registro_aux,"
            " CAST(t1.hora_registro AS TIME) as hora_registro"
            " FROM"
            " AUTOMACAO.dbo.maquina_info t1"
            " ), aux2 AS ("
            " SELECT *,"
            " ROW_NUMBER() OVER (PARTITION BY maquina_id, turno, CAST(data_registro_aux AS DATE)"
            " ORDER BY ABS(DATEDIFF(minute, hora_registro,"
            " CASE turno WHEN 'NOT' THEN '07:59:59'"
            " WHEN 'MAT' THEN '15:59:59'"
            " WHEN 'VES' THEN '23:59:59' END))) as rn"
            " FROM aux"
            " )"
            " SELECT"
            " maquina_id,"
            " linha,"
            " turno,"
            " contagem_total_ciclos as total_ciclos,"
            " contagem_total_produzido as total_produzido,"
            " CAST(data_registro_aux AS DATE) as data_registro,"
            " hora_registro"
            " FROM"
            " aux2"
            f" WHERE rn = 1 AND data_registro_aux >= '{first_day}'  "
            " ORDER BY data_registro DESC, maquina_id, turno"
        )

        print("========== Baixando dados do DB ==========")

        # Leitura dos dados
        df_occ = self.db_read.get_automacao_data(query_occ)
        df_info = self.db_read.get_automacao_data(query_info)
        df_info_production = self.db_read.get_automacao_data(query_production)

        # Verificando se os dados foram lidos corretamente
        if df_occ.empty or df_info.empty or df_info_production.empty:
            print("====== Erro na leitura dos dados ======")
            return None, None, None

        print("Ok...")

        return df_occ, df_info, df_info_production

    def get_cleaned_data(self) -> tuple:
        """
        Recebe a leitura dos dados do banco de dados e faz a limpeza dos dados.
        Retorna na ordem: df_maq_info_cadastro, df_maq_info_prod_cad
        """
        data = self.get_data()
        # Dados do banco de dados (dataframe)
        df_occ, df_info, df_info_production = data
        print("========== Limpando dados ==========")
        # Limpeza inicial dos dados
        df_occ_cleaned = self.clean_df.get_maq_occ_cleaned(df_occ)
        df_info_cleaned = self.clean_df.get_maq_info_cleaned(df_info)
        df_maq_info_prod_cad_cleaned = self.clean_df.get_maq_production_cleaned(df_info_production)
        df_working_minutes = self.clean_df.get_time_working(df_info)
        print("Ok...")
        print("========== Juntando dados ==========")
        # Junção dos dados
        df_info_occ = self.join_df.join_info_occ(df_occ_cleaned, df_info_cleaned)
        df_maq_info_cadastro = self.join_df.problems_adjust(df_info_occ)
        print("Ok...")
        # Retorno dos dados
        return df_maq_info_cadastro, df_maq_info_prod_cad_cleaned, df_working_minutes

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
        query_info = (
            "SELECT"
            " t1.maquina_id,"
            " (SELECT TOP 1 t2.linha FROM AUTOMACAO.dbo.maquina_cadastro t2"
            " WHERE t2.maquina_id = t1.maquina_id AND t2.data_registro <= t1.data_registro"
            " ORDER BY t2.data_registro DESC, t2.hora_registro DESC) as linha,"
            " (SELECT TOP 1 t2.fabrica FROM AUTOMACAO.dbo.maquina_cadastro t2"
            " WHERE t2.maquina_id = t1.maquina_id AND t2.data_registro <= t1.data_registro"
            " ORDER BY t2.data_registro DESC, t2.hora_registro DESC) as fabrica,"
            " t1.status,"
            " t1.turno,"
            " t1.contagem_total_ciclos,"
            " t1.contagem_total_produzido,"
            " t1.data_registro,"
            " t1.hora_registro"
            " FROM "
            " AUTOMACAO.dbo.maquina_info t1"
            f" WHERE data_registro >= '{first_day}' AND data_registro <= '{last_day}'"
            " ORDER BY t1.data_registro DESC, t1.hora_registro DESC"
        )

        # Query para leitura dos dados de de produção
        query_production = (
            "SELECT"
            " t1.maquina_id,"
            " (SELECT TOP 1 t2.linha FROM AUTOMACAO.dbo.maquina_cadastro t2"
            " WHERE t2.maquina_id = t1.maquina_id AND t2.data_registro <= t1.data_registro"
            " ORDER BY t2.data_registro DESC, t2.hora_registro desc) as linha,"
            " t1.turno,"
            " MAX(t1.contagem_total_ciclos) total_ciclos,"
            " MAX(t1.contagem_total_produzido) total_produzido,"
            " t1.data_registro"
            " FROM"
            " AUTOMACAO.dbo.maquina_info t1"
            f" WHERE data_registro >= '{first_day}' AND data_registro <= '{last_day}'"
            " GROUP BY t1.maquina_id, t1.data_registro, t1.turno"
            " ORDER BY data_registro DESC, maquina_id, turno"
        )

        # Leitura dos dados
        df_occ = self.db_read.get_automacao_data(query_occ)
        df_info = self.db_read.get_automacao_data(query_info)
        df_info_production = self.db_read.get_automacao_data(query_production)

        # Limpeza inicial dos dados
        df_occ_cleaned = self.clean_df.get_maq_occ_cleaned(df_occ)
        df_info_cleaned = self.clean_df.get_maq_info_cleaned(df_info)
        df_maq_info_prod_cad_cleaned = self.clean_df.get_maq_production_cleaned(df_info_production)

        # Junção dos dados
        df_info_occ = self.join_df.join_info_occ(df_occ_cleaned, df_info_cleaned)
        df_maq_info_cadastro = self.join_df.problems_adjust(df_info_occ)
        print(f"Ok ás {pd.to_datetime('today')}")
        # Retorno dos dados
        return df_maq_info_cadastro, df_maq_info_prod_cad_cleaned

    def get_maq_tela(self):
        """
        Retorna os dados da tabela maquina_tela
        """
        query = "SELECT * FROM AUTOMACAO.dbo.maquina_tela"

        df = self.db_read.get_automacao_data(query)

        return df
