"""
Módulo para pegar dados do PCP
"""

import pandas as pd
from database.db_read import Read

# cSpell: words CYV_CDMQ CYB_DSMQ CYV_QTATRP CYV_DTRPBG CYV_HRRPBG CYV_CDUSRP X6_CONTEUD
# cSpell: words Codigo descricao usuario charindex usrf cdmq descr dtini hrini nrorpo fabr


class GetPcpData:
    """
    Classe responsável por obter os dados do PCP.

    Atributos:
        db_read (Read): Instância da classe Read para leitura do banco de dados.

    Métodos:
        get_massa_data(): Obtém os dados de massa do PCP.
    """

    def __init__(self) -> None:
        self.db_read = Read()

    def get_massa_data(self) -> pd.DataFrame:
        """
        Obtém os dados de massa do PCP.

        Retorna um DataFrame contendo os seguintes campos:
        - Codigo_Maquina: Código da máquina
        - Descricao_Maquina: Descrição da máquina
        - Quantidade_Atropelamento: Quantidade de atropelamentos
        - Produto: Produto
        - Data_Registro: Data do registro
        - Hora_Registro: Hora do registro
        - Usuario_Registro: Usuário do registro
        - Fabrica: Fábrica identificada

        Detalhes:
            Este método obtém os dados da massadas no sistema e
            retorna um DataFrame contendo as informações relevantes.
            Ele realiza as seguintes etapas:

            1. Define a data do primeiro dia do semestre atual ou do ano atual.
            2. Prepara a query para obter os dados da pasta.
            3. Executa a query e obtém os dados da pasta.
            4. Retorna os dados em um DataFrame.

        Retorno:
            DataFrame contendo os dados de massa do PCP.
        """
        # ================================== Definindo As Datas ================================== #
        # Obtendo a data do primeiro dia do semestre atual ou do ano atual
        today = pd.Timestamp.today()
        if today.month >= 6:
            first_day = today.replace(month=1, day=1).strftime("%Y%m%d")
        else:
            six_months_ago = today - pd.DateOffset(months=6)
            first_day = six_months_ago.replace(day=1).strftime("%Y%m%d")

        # ================================== Preparando A Query ================================== #
        select = (
            'T1.CYV_CDMQ AS "Codigo_Maquina"'
            ', T2.CYB_DSMQ AS "Descricao_Maquina"'
            ', T1.CYV_QTATRP AS "Quantidade_Atropelamento"'
            ', T6.OX_DESCR AS "Produto"'
            ', T1.CYV_DTRPBG AS "Data_Registro"'
            ', T1.CYV_HRRPBG AS "Hora_Registro"'
            ', T1.CYV_CDUSRP AS "Usuario_Registro"'
            ", COALESCE("
            "CASE WHEN CHARINDEX(T1.CYV_CDUSRP, T3.X6_CONTEUD) > 0 THEN 'Fab. 1' END,"
            "CASE WHEN CHARINDEX(T1.CYV_CDUSRP, T4.X6_CONTEUD) > 0 THEN 'Fab. 2' END,"
            "'Não identificado'"
            ') AS "Fabrica"'
        )

        table = "CYV000 (NOLOCK) AS T1"

        join = (
            "JOIN CYB000 (NOLOCK) AS T2 ON T1.CYV_FILIAL = T2.CYB_FILIAL "
            "AND T1.CYV_CDMQ = T2.CYB_CDMQ AND T2.D_E_L_E_T_ <> '*'"
            "LEFT JOIN SX6000 (NOLOCK) AS T3 ON T3.X6_VAR = 'MV_X_USRF1' "
            "LEFT JOIN SX6000 (NOLOCK) AS T4 ON T4.X6_VAR = 'MV_X_USRF2' "
            "JOIN V9_000 (NOLOCK) AS T5 ON T1.CYV_CDMQ = T5.V9__MAQ AND T1.CYV_NRORPO = T5.V9__OP "
            "AND T1.CYV_DTRPBG = T5.V9__DTINI AND T1.CYV_HRRPBG = T5.V9__HRINI "
            "AND T5.V9__STATUS = 1 AND T5.D_E_L_E_T_ <> '*' "
            "JOIN SOX000 (NOLOCK) AS T6 ON T5.V9__FORM = T6.OX_FORM AND T6.D_E_L_E_T_ <> '*'"
        )

        where = (
            "T1.D_E_L_E_T_ <> '*' AND T1.CYV_FILIAL = '0101' AND T1.CYV_CDMQ LIKE 'AMS%' "
            f"AND T1.CYV_DTRPBG >= '{first_day}'"
        )

        orderby = "T1.CYV_DTRPBG, T1.CYV_CDMQ, T1.CYV_HRRPBG"

        # ================================== Executando A Query ================================== #
        query_massadas = self.db_read.create_totvsdb_query(select, table, join, where, orderby)

        # ================================= Retornando Os Dados ================================== #
        df_massadas = self.db_read.get_totvsdb_data(query_massadas)

        return df_massadas

    def get_pasta_data(self) -> pd.DataFrame:
        """
        Obtém os dados da pasta no sistema e retorna um DataFrame contendo as informações.

        Retorna:
            pd.DataFrame: DataFrame contendo os dados da pasta.

        Colunas:
            - Codigo_Maquina: Código da máquina
            - Descricao_Maquina: Descrição da máquina
            - Quantidade_Atropelamento: Quantidade de atropelamentos
            - Produto: Produto
            - Data_Registro: Data do registro
            - Hora_Registro: Hora do registro
            - Usuario_Registro: Usuário do registro
            - Fabrica: Fábrica identificada

        Detalhes:
            Este método obtém os dados da pasta no sistema e retorna
            um DataFrame contendo as informações relevantes.
            Ele realiza as seguintes etapas:

            1. Define a data do primeiro dia do semestre atual ou do ano atual.
            2. Prepara a query para obter os dados da pasta.
            3. Executa a query e obtém os dados da pasta.
            4. Retorna os dados em um DataFrame.

        Exemplo:
            >>> pcp_data = get_pasta_data()
            >>> print(pcp_data.head())

        Observações:
            - Este método assume que as tabelas e colunas utilizadas na query
            estão corretamente definidas no sistema.
            - Certifique-se de ter as dependências necessárias importadas antes
            de chamar este método.
        """

        # ================================== Definindo As Datas ================================== #
        # Obtendo a data do primeiro dia do semestre atual ou do ano atual
        today = pd.Timestamp.today()
        if today.month >= 6:
            first_day = today.replace(month=1, day=1).strftime("%Y%m%d")
        else:
            six_months_ago = today - pd.DateOffset(months=6)
            first_day = six_months_ago.replace(day=1).strftime("%Y%m%d")

        # ================================== Preparando A Query ================================== #
        select = (
            'T1.CYV_CDMQ AS "Codigo_Maquina"'
            ', T2.CYB_DSMQ AS "Descricao_Maquina"'
            ', T1.CYV_QTATRP AS "Quantidade_Atropelamento"'
            ', T6.OX_DESCR AS "Produto"'
            ', T1.CYV_DTRPBG AS "Data_Registro"'
            ', T1.CYV_HRRPBG AS "Hora_Registro"'
            ', T1.CYV_CDUSRP AS "Usuario_Registro"'
            ", COALESCE("
            "CASE WHEN CHARINDEX('1', T2.CYB_X_FABR) > 0 THEN 'Fab. 1' END,"
            "CASE WHEN CHARINDEX('2', T2.CYB_X_FABR) > 0 THEN 'Fab. 2' END,"
            "'Não identificado'"
            ') AS "Fabrica"'
        )

        table = "CYV000 (NOLOCK) AS T1"

        join = (
            "JOIN CYB000 (NOLOCK) AS T2 ON T1.CYV_FILIAL = T2.CYB_FILIAL "
            "AND T1.CYV_CDMQ = T2.CYB_CDMQ AND T2.D_E_L_E_T_ <> '*'"
            "JOIN V9_000 (NOLOCK) AS T5 ON T1.CYV_CDMQ = T5.V9__MAQ AND T1.CYV_NRORPO = T5.V9__OP "
            "AND T1.CYV_DTRPBG = T5.V9__DTINI AND T1.CYV_HRRPBG = T5.V9__HRINI "
            "AND T5.V9__STATUS = 1 AND T5.D_E_L_E_T_ <> '*' "
            "JOIN SOX000 (NOLOCK) AS T6 ON T5.V9__FORM = T6.OX_FORM AND T6.D_E_L_E_T_ <> '*'"
        )

        where = (
            "T1.D_E_L_E_T_ <> '*' AND T1.CYV_FILIAL = '0101' AND T1.CYV_CDMQ LIKE 'RET%' "
            f"AND T1.CYV_DTRPBG >= '{first_day}'"
        )

        orderby = "T1.CYV_DTRPBG, T1.CYV_CDMQ, T1.CYV_HRRPBG"

        # ================================== Executando A Query ================================== #
        query_pasta = self.db_read.create_totvsdb_query(select, table, join, where, orderby)

        # ================================= Retornando Os Dados ================================== #
        df_pasta = self.db_read.get_totvsdb_data(query_pasta)

        return df_pasta
