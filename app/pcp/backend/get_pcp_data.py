"""
Módulo para pegar dados do PCP
"""

import pandas as pd
from database.db_read import Read

# cSpell: words CYV_CDMQ CYB_DSMQ CYV_QTATRP CYV_DTRPBG CYV_HRRPBG CYV_CDUSRP X6_CONTEUD
# cSpell: words Codigo descricao usuario charindex usrf cdmq


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
        - Data_Registro: Data do registro
        - Hora_Registro: Hora do registro
        - Usuario_Registro: Usuário do registro
        - Fabrica: Fábrica identificada

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
