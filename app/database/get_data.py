"""
    Autor: Bruno Tomaz
    Data: 15/01/2024
    Esse módulo é responsável por realizar a leitura dos dados do banco de dados.
    É utilizada para fazer a leitura em segundo plano, sem que o usuário perceba.
"""

import pandas as pd
from database.db_read import Read
from service.clean_data import CleanData
from service.join_data import JoinData


# cSpell: words automacao, ocorrencia dateadd datediff locpad
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
            "SELECT * "
            "FROM ( "
            "SELECT "
            "(SELECT TOP 1 t2.fabrica FROM AUTOMACAO.dbo.maquina_cadastro t2 "
            "WHERE t2.maquina_id = t1.maquina_id AND t2.data_registro <= t1.data_registro "
            "ORDER BY t2.data_registro DESC, t2.hora_registro DESC) as fabrica, "
            "(SELECT TOP 1 t2.linha FROM AUTOMACAO.dbo.maquina_cadastro t2 "
            "WHERE t2.maquina_id = t1.maquina_id AND t2.data_registro <= t1.data_registro "
            "ORDER BY t2.data_registro DESC, t2.hora_registro DESC) as linha, "
            "t1.maquina_id, "
            "t1.turno, "
            "t1.status, "
            "t1.contagem_total_ciclos as total_ciclos, "
            "t1.contagem_total_produzido as total_produzido, "
            "t1.data_registro, "
            "t1.hora_registro, "
            "ROW_NUMBER() OVER ( "
            "PARTITION BY t1.data_registro, t1.turno, t1.maquina_id "
            "ORDER BY t1.data_registro DESC, t1.hora_registro DESC"
            ") AS rn "
            "FROM AUTOMACAO.dbo.maquina_info t1 "
            ") AS t "
            f" WHERE rn = 1 AND data_registro >= '{first_day}' AND hora_registro > '00:01'"
            " ORDER BY data_registro DESC, linha"
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
        return df_maq_info_cadastro, df_maq_info_prod_cad_cleaned, df_working_minutes, df_info

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

    def get_maq_tela(self) -> pd.DataFrame:
        """
        Retrieves data from the 'maquina_tela' table in the AUTOMACAO database.

        Returns:
            DataFrame: A pandas DataFrame containing the retrieved data.
        """
        query = "SELECT * FROM AUTOMACAO.dbo.maquina_tela"

        df = self.db_read.get_automacao_data(query)

        return df

    # cSpell: words fabr emissao hrrpbg ccca nrrpet cdmq codbem
    def get_protheus_caixas_data(self) -> pd.DataFrame:
        """
        Retrieves data from the Protheus system for caixas.

        Returns:
            pandas.DataFrame: The retrieved data from the Protheus system.
        """

        # Dia de hoje
        now = pd.to_datetime("today")

        # Encontrando primeiro dia do mês atual
        first_day = now.replace(day=1)

        # Mantendo apenas a data
        first_day = first_day.strftime("%Y-%m-%d")

        query = self.db_read.create_totvsdb_query(
            select=(
                "CYB_X_FABR AS FABRICA, "
                "T9_NOME AS MAQUINA, "
                "B1_DESC AS PRODUTO, "
                "D3_QUANT AS QTD, "
                "D3_UM AS UNIDADE, "
                "D3_EMISSAO AS EMISSAO, "
                "CYV_HRRPBG AS HORA, "
                "CYV_CCCA05 AS LOTE "
            ),
            table="SD3000 SD3 WITH (NOLOCK)",
            join=(
                "LEFT JOIN SB1000 SB1 WITH (NOLOCK) "
                "ON B1_FILIAL='01' and B1_COD=D3_COD AND SB1.D_E_L_E_T_<>'*' "
                "LEFT JOIN CYV000 CYV WITH (NOLOCK) "
                "ON CYV_FILIAL=D3_FILIAL and CYV_NRRPET=D3_IDENT and CYV.D_E_L_E_T_<>'*' "
                "LEFT JOIN CYB000 CYB WITH (NOLOCK) "
                "ON CYB_FILIAL=D3_FILIAL and CYB_CDMQ=CYV_CDMQ and CYB.D_E_L_E_T_<>'*' "
                "LEFT JOIN ST9000 ST9 WITH (NOLOCK) "
                "ON CYV_CDMQ=T9_CODBEM and ST9.D_E_L_E_T_<>'*'"
            ),
            where=(
                "D3_FILIAL = '0101' AND D3_LOCAL='CF' AND B1_TIPO = 'PA' AND D3_CF = 'PR0' "
                f"AND D3_ESTORNO <> 'S' AND D3_EMISSAO >= '{first_day}' AND SD3.D_E_L_E_T_<>'*'"
            ),
            orderby="D3_EMISSAO DESC, CYV_HRRPBG DESC",
        )

        print("=============== Baixando dados TOTVSDB ===============")
        df = self.db_read.get_totvsdb_data(query)

        if df.empty:
            print("=============== TOTVSDB ERRO ===============")
        else:
            print("Ok...")

        return df

    def get_protheus_total_caixas(self) -> pd.DataFrame:
        """
        Retrieves the total number of boxes from the Protheus database.

        Returns:
            pd.DataFrame: A DataFrame containing the product name and the total quantity of boxes.
        """
        query = self.db_read.create_totvsdb_query(
            select="B1_DESC AS PRODUTO, B2_QATU AS QTD",
            table="SB2000 SB2 WITH (NOLOCK)",
            join=(
                "INNER JOIN SB1000 SB1 WITH (NOLOCK) "
                "ON B1_FILIAL='01' AND B1_COD=B2_COD AND SB1.D_E_L_E_T_<>'*'"
            ),
            where=(
                "B2_FILIAL='0101' AND B2_LOCAL='CF' AND B1_TIPO='PA' "
                "AND B1_LOCPAD='CF' AND SB2.D_E_L_E_T_<>'*'"
            ),
            orderby="B2_COD",
        )

        print("=============== Baixando dados TOTVSDB ===============")
        df = self.db_read.get_totvsdb_data(query)

        if df.empty:
            print("=============== TOTVSDB ERRO ===============")
        else:
            print("Ok...")

        return df
