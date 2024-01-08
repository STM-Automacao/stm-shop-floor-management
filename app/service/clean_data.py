"""
    Módulo para limpeza dos dados
"""

# desabilitar o cSpell nas palavras entre aspas abaixo
# cSpell:words usuario, solucao

import pandas as pd
import numpy as np


class CleanData:
    """
    Classe para limpeza dos dados

    Atributos:
        df (pd.DataFrame): Dataframe com os dados a serem limpos

    Métodos:
        clean_maq_cadastro: Limpa os dados de cadastro das máquinas

    """

    def __init__(self):
        pass

    def clean_maq_cadastro(self, df_cadastro: pd.DataFrame) -> pd.DataFrame:
        """
        Limpa os dados de cadastro das máquinas

        Args:
        -----
            data (pd.DataFrame): Dataframe com os dados a serem limpos

        Retorna:
        --------
            pd.DataFrame: Dataframe com os dados limpos

        Exemplo:
        --------

            >>> from app.service.clean_data import CleanData
            >>> import pandas as pd
            >>> df = pd.DataFrame({'maquina_id': [TMF001, TMF002, TMF003], 'linha': [1, 2, 3],
            'fabrica': [1, 2, 2], 'data_registro': ['2021-01-01', '2021-01-01', '2021-01-01'],
            'hora_registro': ['00:00:00.000', '00:00:00.000', '00:00:00.000'],
            'recno': [1, 2, 3], usuario_id: [00532, 00533, 00534]})
            >>> clean_data = CleanData()
            >>> df_clean = clean_data.clean_maq_cadastro(df)
            >>> df_clean
                maquina_id  linha  fabrica data_hora_registro       usuario_id
            0     TMF001      1        1    2021-01-01 00:00:00      532
            1     TMF002      2        2    2021-01-01 00:00:00      533
            2     TMF003      3        2    2021-01-01 00:00:00      534


        """
        # Remover rows onde a linha é 0
        df_cadastro = df_cadastro[df_cadastro["linha"] != 0]

        # Remover linhas duplicadas (erros de cadastro)
        df_cadastro = df_cadastro.drop_duplicates(
            subset=["data_registro", "linha"], keep="first"
        )

        # Criar nova coluna combinando data e hora
        df_cadastro["data_hora_registro"] = (
            df_cadastro["data_registro"].astype(str)
            + " "
            + df_cadastro["hora_registro"].astype(str).str.split(".").str[0]
        )

        # Converter coluna data_hora_registro para datetime
        df_cadastro["data_hora_registro"] = pd.to_datetime(
            df_cadastro["data_hora_registro"], format="%Y-%m-%d %H:%M:%S"
        )

        # Remover colunas desnecessárias
        df_cadastro = df_cadastro.drop(
            columns=["recno", "data_registro", "hora_registro"]
        )

        # Ordenar dataframe para facilitar trabalho futuro
        df_cadastro = df_cadastro.sort_values(
            by=["maquina_id", "data_hora_registro"], ascending=[True, False]
        )

        # reiniciar o index
        df_cadastro = df_cadastro.reset_index(drop=True)

        return df_cadastro

    def clean_maq_info(self, df_info: pd.DataFrame) -> pd.DataFrame:
        """
        Limpa os dados de cadastro das máquinas

        Args:
        -----
            data (pd.DataFrame): Dataframe com os dados a serem limpos

        Retorna:
        --------
            pd.DataFrame: Dataframe com os dados limpos

        Exemplo:
        --------

            >>> from app.service.clean_data import CleanData
            >>> import pandas as pd
            >>> df = pd.DataFrame({'maquina_id': [TMF001, TMF002, TMF003],
            'status'[False, True, True], 'turno'[MAT, VES, NOT],
            'data_registro': ['2021-01-01', '2021-01-01', '2021-01-01'],
            'hora_registro': ['00:00:00.000', '00:00:00.000', '00:00:00.000'], 'recno': [1, 2, 3],
            })
            >>> clean_data = CleanData()
            >>> df_clean = clean_data.clean_maq_info(df)
            >>> df_clean
                maquina_id  status  turno   data_hora_registro      data_hora_final
                tempo_registro_min
            0     TMF001    parada    MAT   2021-01-01 00:00:00     2021-01-01 00:01:00
            480
            1     TMF002    rodando   VES   2021-01-01 00:00:00     2021-01-01 00:01:00
            10
            2     TMF003    rodando   NOT   2021-01-01 00:00:00     2021-01-01 00:01:00
            10

        """

        # Ordenar por maquina_id e data_registro, hora_registro
        df_info.sort_values(
            by=["maquina_id", "data_registro", "hora_registro"], inplace=True
        )

        # Criar nova coluna combinando data e hora
        df_info["data_hora_registro"] = (
            df_info["data_registro"].astype(str)
            + " "
            + df_info["hora_registro"].astype(str).str.split(".").str[0]
        )

        # Descartar colunas desnecessárias
        df_info = df_info.drop(
            columns=["recno", "data_registro", "hora_registro"]
        )

        # Corrigindo erros da DB (horário dos turnos) - vai se tornar obsoleto à partir de Fev/24
        df_info.sort_values(
            by=["maquina_id", "data_hora_registro"], inplace=True
        )
        df_info = df_info[
            ~(
                (df_info["turno"] == "VES")
                & (df_info["maquina_id"] != df_info["maquina_id"].shift())
            )
        ]  # descarta a primeira linha se o turno for VES

        # Criar nova coluna status_change para identificar mudança de status
        df_info["status_change"] = df_info["status"].ne(
            df_info["status"].shift()
        )

        # Criar coluna para identificar a mudança de máquina
        df_info["maquina_change"] = df_info["maquina_id"].ne(
            df_info["maquina_id"].shift()
        )

        # criar coluna para consolidar mudança de status e de máquina
        df_info["change"] = (
            df_info["status_change"] | df_info["maquina_change"]
        )

        # Criar coluna para identificar a mudança de turno
        df_info["turno_change"] = df_info["turno"].ne(df_info["turno"].shift())

        # Atualizar coluna change para incluir mudança de turno
        df_info["change"] = df_info["change"] | df_info["turno_change"]

        # Agrupar por maquina e identificar data e hora da última mudança de status
        df_info["change_time"] = (
            df_info.groupby("maquina_id")["data_hora_registro"]
            .shift(0)
            .where(df_info["change"])
        )

        # Remover as linhas onde change_time é nulo
        df_info.dropna(subset=["change_time"], inplace=True)

        # Criar nova coluna com a data_hora_final do status
        df_info["data_hora_final"] = (
            df_info.groupby("maquina_id")["data_hora_registro"]
            .shift(-1)
            .where(~df_info["maquina_change"])
        )

        # Atualizar coluna data_hora_final onde maquina_change é True
        df_info.loc[df_info["maquina_change"], "data_hora_final"] = df_info[
            "change_time"
        ].shift(-1)

        # Remover colunas desnecessárias
        df_info.drop(
            columns=[
                "status_change",
                "maquina_change",
                "turno_change",
                "change",
                "change_time",
            ],
            inplace=True,
        )

        # Remover linhas onde data_hora_final é nulo
        df_info.dropna(subset=["data_hora_final"], inplace=True)

        # Cria nova coluna tempo_registro_min para calcular o tempo de registro em minutos
        df_info["tempo_registro_min"] = (
            pd.to_datetime(df_info["data_hora_final"])
            - pd.to_datetime(df_info["data_hora_registro"])
        ).dt.total_seconds() / 60

        # Arredondar tempo_registro_min e converter para inteiro
        df_info["tempo_registro_min"] = (
            df_info["tempo_registro_min"].round(0).astype(int)
        )

        # Incluir um status in_test para os casos onde o status true é menor que 10 minutos
        df_info = df_info.astype(
            {"status": str}
        )  # para evitar erros de comparação
        df_info.loc[
            (df_info["status"] == "true")
            & (df_info["tempo_registro_min"] <= 10),
            "status",
        ] = "in_test"

        # Ajustar nomenclatura dos status
        df_info.loc[df_info["status"] == "true", "status"] = "rodando"
        df_info.loc[df_info["status"] == "false", "status"] = "parada"

        # Remover colunas desnecessárias
        df_info.drop(
            columns=[
                "ciclo_1_min",
                "ciclo_15_min",
                "contagem_total_ciclos",
                "contagem_total_produzido",
                "tempo_parada",
                "tempo_rodando",
            ],
            inplace=True,
        )

        # Ajustar o index
        df_info.reset_index(drop=True, inplace=True)

        return df_info

    def clean_maq_occ(self, df_occ: pd.DataFrame) -> pd.DataFrame:
        """
        Limpa os dados de cadastro das máquinas

        Args:
        -----
            data (pd.DataFrame): Dataframe com os dados a serem limpos

        Retorna:
        --------
            pd.DataFrame: Dataframe com os dados limpos

        Exemplo:
        --------
            >>> from app.service.clean_data import CleanData
            >>> import pandas as pd
            >>> df = pd.DataFrame({'maquina_id': [TMF001, TMF002, TMF003], 'motivo_id': [1, 2, 3],
            'problema': ['Ajuste', 'Troca de Bobina', 'Refeição'],
            'solucao': ['Ajuste', 'Troca de Bobina', 'Refeição'],
            'data_registro': ['2021-01-01', '2021-01-01', '2021-01-01'],
            'hora_registro': ['00:00:00.000', '00:00:00.000', '00:00:00.000'],
            'recno': [1, 2, 3], 'usuario_id': [00532, 00533, 00534]})
            >>> clean_data = CleanData()
            >>> df_clean = clean_data.clean_maq_occ(df)
            >>> df_clean
                maquina_id  motivo_id  motivo_nome        problema  solucao     data_hora_registro
                usuario_id
            0     TMF001      1        Ajustes            Ajustes               2021-01-01 00:00:00
            532
            1     TMF002      2        Troca de Bobina    Troca de Bobina       2021-01-01 00:00:00
            533
            2     TMF003      3        Refeição           Refeição              2021-01-01 00:00:00
            534

        """

        # Motivos de Parada
        motivos = {
            1: "Ajustes",
            2: "Troca de Bobina",
            3: "Refeição",
            4: "Reunião",
            5: "Café e Ginástica Laboral",
            6: "Limpeza",
            7: "Manutenção Elétrica",
            8: "Manutenção Mecânica",
            9: "Material em Falta",
            10: "Setup de Sabor",
            11: "Setup de Tamanho",
            12: "Parada Programada",
            13: "Intervenção de Qualidade",
            14: "Linha Cheia",
            15: "Treinamento",
            16: "Limpeza Industrial",
        }

        # Unir as colunas de data e hora
        df_occ["data_hora_registro"] = (
            df_occ["data_registro"].astype(str)
            + " "
            + df_occ["hora_registro"].astype(str).str.split(".").str[0]
        )

        # Modificar coluna motivo_id para int
        df_occ = df_occ.astype({"motivo_id": int})

        # Criar coluna motivo_nome com base no dicionário motivos
        df_occ["motivo_nome"] = df_occ["motivo_id"].map(motivos)

        # Ajustar problema se a string estiver vazia
        df_occ["problema"] = df_occ["problema"].replace("", np.nan)
        df_occ["solucao"] = df_occ["solucao"].replace("", np.nan)

        # Se o problema for nulo, copiar o motivo_nome para o problema,
        # exceto para os motivos 1, 7, 8, 9, 14,
        df_occ.loc[
            df_occ["problema"].isnull()
            & ~df_occ["motivo_id"].isin([1, 7, 8, 9, 14]),
            "problema",
        ] = df_occ["motivo_nome"]

        # Definir ordem das colunas
        df_occ = df_occ[
            [
                "maquina_id",
                "motivo_id",
                "motivo_nome",
                "problema",
                "solucao",
                "data_hora_registro",
                "usuario_id",
            ]
        ]

        return df_occ
