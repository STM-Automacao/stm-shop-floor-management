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
from service.service_info_ihm import ServiceInfoIHM


# cSpell: words automacao, ocorrencia dateadd datediff locpad
class GetData:
    """
    Essa classe é responsável por realizar a leitura dos dados do banco de dados.
    É utilizada para fazer a leitura em segundo plano, sem que o usuário perceba.
    """

    def __init__(self):
        self.db_read = Read()
        self.clean_data = CleanData
        self.join_data = JoinData
        self.service = ServiceInfoIHM

    def get_data(self) -> tuple:
        """
        Realiza a leitura dos dados do banco de dados.
        Retorna na ordem: df_ihm, df_info, df_info_production
        """

        # Dia de hoje
        now = pd.to_datetime("today")

        # Encontrando primeiro dia do mês atual
        first_day = now.replace(day=1)

        # Mantendo apenas a data
        first_day = first_day.strftime("%Y-%m-%d")

        # Query para leitura dos dados de IHM
        query_ihm = self.db_read.create_automacao_query(
            table="maquina_ihm",
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

        # Leitura dos dados
        df_ihm = self.db_read.get_automacao_data(query_ihm)
        df_info = self.db_read.get_automacao_data(query_info)
        df_info_production = self.db_read.get_automacao_data(query_production)

        # Verificando se os dados foram lidos corretamente
        if df_ihm.empty or df_info.empty or df_info_production.empty:
            raise ValueError("* --> Erro na leitura dos dados do DB Automação.")

        return df_ihm, df_info, df_info_production

    def get_cleaned_data(self) -> tuple:
        """
        Recebe a leitura dos dados do banco de dados e faz a limpeza dos dados.
        Retorna na ordem: df_stop_time, df_info_production, df_working_minutes, df_info
        """

        # Dados do banco de dados (dataframe)
        df_ihm, df_info, df_info_production = self.get_data()

        # Limpeza inicial dos dados
        df_ihm_cleaned, df_info_cleaned, df_info_production_cleaned = self.clean_data(
            df_ihm, df_info, df_info_production
        ).clean_data()

        # Junção dos dados
        df_joined = self.join_data(df_ihm_cleaned, df_info_cleaned).join_data()

        # Caso df_joined seja None, ou não tenha dados, lança erro personalizado
        if df_joined is None or df_joined.empty:
            raise ValueError("* --> Erro na leitura dos dados do DF Joined.")

        # Instanciando Service
        service = self.service(df_joined)

        # Info IHM ajustado
        df_info_ihm_adjusted = service.get_info_ihm_adjusted()

        # Tempo trabalhando
        df_working_minutes = service.get_time_working(df_info_ihm_adjusted)

        # Tempo Parada
        df_stop_time = service.get_maq_stopped(df_info_ihm_adjusted)

        # Retorno dos dados
        return df_stop_time, df_info_production_cleaned, df_working_minutes, df_info_cleaned

    def __get_last_month_data(self) -> tuple:
        """
        Retrieves data from the previous month.

        Returns:
            A tuple containing three pandas DataFrames:
            - df_ihm: Data from the 'maquina_ihm' table.
            - df_info: Data from the 'maquina_info' table.
            - df_info_production: Data from the 'maquina_info' table, aggregated by
            machine, date, and shift.
        """

        # Dia de hoje
        now = pd.to_datetime("today")

        # Encontrando primeiro dia do mês atual
        first_day_this_month = now.replace(day=1)

        # Encontrando primeiro e último dia do mês anterior
        last_month = first_day_this_month - pd.DateOffset(months=1)

        # Mantendo apenas a data
        first_day = last_month.replace(day=1).strftime("%Y-%m-%d")
        last_day = last_month.replace(day=last_month.days_in_month).strftime("%Y-%m-%d")

        # Query para leitura dos dados de ocorrência
        query_ihm = self.db_read.create_automacao_query(
            table="maquina_ihm",
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
            f"WHERE rn = 1 AND WHERE data_registro >= '{first_day}' "
            f"AND data_registro <= '{last_day}' AND hora_registro > '00:01' "
            "ORDER BY data_registro DESC, linha"
        )

        # Leitura dos dados
        df_ihm = self.db_read.get_automacao_data(query_ihm)
        df_info = self.db_read.get_automacao_data(query_info)
        df_info_production = self.db_read.get_automacao_data(query_production)

        return df_ihm, df_info, df_info_production

    def get_last_month_data_cleaned(self) -> tuple:
        """
        Retrieves the last month's data, cleans it, and returns the cleaned data.

        Returns:
            tuple: A tuple containing the cleaned dataframes for stop time and production
            information.
        """

        # Leitura dos dados
        df_ihm, df_info, df_info_production = self.__get_last_month_data()

        # Limpeza inicial dos dados
        df_ihm_cleaned, df_info_cleaned, df_info_production_cleaned = self.clean_data(
            df_ihm, df_info, df_info_production
        ).clean_data()

        # Junção dos dados
        df_joined = self.join_data(df_ihm_cleaned, df_info_cleaned).join_data()

        # Instanciando Service
        service = self.service(df_joined)

        # Info IHM ajustado
        df_info_ihm_adjusted = service.get_info_ihm_adjusted()

        # Tempo Parada
        df_stop_time = service.get_maq_stopped(df_info_ihm_adjusted)

        # Retorno dos dados
        return df_stop_time, df_info_production_cleaned

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

        df = self.db_read.get_totvsdb_data(query)

        if df.empty:
            raise ValueError("* --> Erro na leitura dos dados do DB TOTVSDB.")

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

        df = self.db_read.get_totvsdb_data(query)

        if df.empty:
            raise ValueError("* --> Erro na leitura dos dados do DB TOTVSDB.")

        return df
