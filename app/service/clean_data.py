"""
    Módulo para limpeza dos dados
"""

from datetime import time

# cSpell:words usuario, solucao, dayofweek, sabado
import numpy as np
import pandas as pd

# pylint: disable=E0401
from helpers.path_config import FERIADOS


class CleanData:
    """
    Classe para limpeza dos dados

    Métodos:
    --------
        clean_maq_cadastro: Limpa os dados de cadastro das máquinas
        clean_maq_info: Limpa os dados de status das máquinas
        clean_maq_occ: Limpa os dados de ocorrências das máquinas

    """

    def __init__(self):
        pass

    def clean_maq_cadastro(self, cadastro: pd.DataFrame) -> pd.DataFrame:
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

        # Remover linhas duplicadas (erros de cadastro)
        df_cadastro = cadastro.drop_duplicates(
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

    def maq_info(self, info: pd.DataFrame) -> pd.DataFrame:
        """
        Limpa os dados de info das máquinas para paradas

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
        df_info = info.sort_values(
            by=["maquina_id", "data_registro", "hora_registro"],
        )

        # Criar nova coluna combinando data e hora
        df_info["data_hora_registro"] = (
            df_info["data_registro"].astype(str)
            + " "
            + df_info["hora_registro"].astype(str).str.split(".").str[0]
        )

        # Reordenar colunas (descarta desnecessárias)
        df_info = df_info[
            [
                "maquina_id",
                "status",
                "turno",
                "data_hora_registro",
                "contagem_total_ciclos",
                "contagem_total_produzido",
            ]
        ]

        # Se for a primeira linha de cada máquina e o turno for VES, alterar para NOT
        df_info.loc[
            (df_info["turno"] == "VES")
            & (df_info["maquina_id"] != df_info["maquina_id"].shift()),
            "turno",
        ] = "NOT"

        # Se for a primeira linha de cada dia e o turno for VES, ajustar data_hora_registro
        df_info["data_hora_registro"] = pd.to_datetime(
            df_info["data_hora_registro"]
        )
        df_info.loc[
            (df_info["turno"] == "VES")
            & (
                df_info["data_hora_registro"]
                != df_info["data_hora_registro"].shift()
            )
            & (df_info["data_hora_registro"].dt.time > time(0, 0, 0))
            & (df_info["data_hora_registro"].dt.time < time(0, 5, 0)),
            "data_hora_registro",
        ] = (
            df_info["data_hora_registro"] - pd.Timedelta(days=1)
        ).dt.normalize() + pd.Timedelta(
            hours=23, minutes=59, seconds=59
        )  # normalize remove a hora(na verdade deixa 00:00:00) e timedelta altera p/ 23:59:59

        # Criar nova coluna status_change para identificar mudança de status
        df_info["status_change"] = df_info["status"].ne(
            df_info["status"].shift()
        )

        # Criar coluna para identificar a mudança de máquina
        df_info["maquina_change"] = df_info["maquina_id"].ne(
            df_info["maquina_id"].shift()
        )

        # Criar coluna para identificar a mudança de turno
        df_info["turno_change"] = df_info["turno"].ne(df_info["turno"].shift())

        # Atualizar coluna change para incluir mudança de turno
        df_info["change"] = (
            df_info["status_change"]
            | df_info["maquina_change"]
            | df_info["turno_change"]
        )

        # Agrupar por maquina e identificar data e hora da última mudança de status
        df_info["change_time"] = (
            df_info.groupby("maquina_id")["data_hora_registro"]
            .shift(0)
            .where(df_info["change"])
        )

        # Feito para agrupar por maquina_id e turno e manter o ultimo registro de cada grupo
        df_info = (
            df_info.groupby(["maquina_id", "change_time"])
            .agg(
                status_first=("status", "first"),
                turno_first=("turno", "first"),
                data_hora_registro_first=("data_hora_registro", "first"),
                contagem_total_ciclos_last=("contagem_total_ciclos", "last"),
                contagem_total_produzido_last=(
                    "contagem_total_produzido",
                    "last",
                ),
                change_first=("change", "first"),
                maquina_change_first=("maquina_change", "first"),
            )
            .reset_index()
        )

        # Renomear colunas
        df_info.rename(
            columns={
                "status_first": "status",
                "turno_first": "turno",
                "data_hora_registro_first": "data_hora_registro",
                "contagem_total_ciclos_last": "contagem_total_ciclos",
                "contagem_total_produzido_last": "contagem_total_produzido",
                "change_first": "change",
                "maquina_change_first": "maquina_change",
            },
            inplace=True,
        )

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
                "maquina_change",
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
            & (df_info["tempo_registro_min"] < 10),
            "status",
        ] = "in_test"

        # Ajustar nomenclatura dos status
        df_info.loc[df_info["status"] == "true", "status"] = "rodando"
        df_info.loc[df_info["status"] == "false", "status"] = "parada"

        # Remover colunas desnecessárias
        df_info.drop(
            columns=[
                "contagem_total_ciclos",
                "contagem_total_produzido",
            ],
            inplace=True,
        )

        # Ajustar o index
        df_info.reset_index(drop=True, inplace=True)

        return df_info

    def get_stops_data(self, info: pd.DataFrame) -> pd.DataFrame:
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

        # Copiar o dataframe
        df = info.copy()

        # Transformar data e hora em datetime
        df["data_hora_registro"] = pd.to_datetime(df["data_hora_registro"])
        df["data_hora_final"] = pd.to_datetime(df["data_hora_final"])

        # Ordenar por maquina_id, turno, data_hora_registro
        df.sort_values(
            by=["maquina_id", "turno", "data_hora_registro"], inplace=True
        )

        # Criar coluna data_hora_registro_turno para identificar onde está rodando
        df["rodando"] = df["status"] == "rodando"

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
                    "tempo_registro_min": "sum",
                    "data_hora_registro": "first",
                    "data_hora_final": "last",
                }
            )
            .reset_index(drop=True)
        )

        # Ordenar por maquina_id, data_hora_registro
        df.sort_values(by=["maquina_id", "data_hora_registro"], inplace=True)

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
        # feriados = pd.read_csv(file_path)
        feriados = pd.read_csv(FERIADOS)

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

        # Identificar sábados
        df["sabado"] = df["data_hora_registro"].dt.dayofweek == 5

        # Criar nova coluna unindo domingo, feriado e dia após feriado e descartar
        # as colunas domingo, feriado e dia após feriado
        df["domingo_feriado_emenda"] = (
            df["domingo"]
            | df["feriado"]
            | df["dia_apos_feriado"]
            | df["sabado"]
        )
        df.drop(
            columns=["domingo", "feriado", "dia_apos_feriado"], inplace=True
        )

        return df

    def clean_maq_info(self, info: pd.DataFrame) -> pd.DataFrame:
        """Agrupa funções de limpeza dos dados de info das máquinas para parada

        Funções:
            maq_info
            get_stops_data
            dayofweek_adjust

        Args:
            info (pd.DataFrame): Info das máquinas do Banco de Dados

        Returns:
            pd.DataFrame: Dataframe com os dados limpos
        """

        df_info = info.copy()

        df_clean = self.maq_info(df_info)
        df_clean = self.get_stops_data(df_clean)
        df_clean = self.dayofweek_adjust(df_clean)

        return df_clean

    def clean_maq_occ(self, occ: pd.DataFrame) -> pd.DataFrame:
        """
        Limpa os dados de ocorrências das máquinas

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

        # Modificar coluna motivo_id para int
        df_occ = occ.astype({"motivo_id": int})

        # Unir as colunas de data e hora
        df_occ["data_hora_registro"] = (
            df_occ["data_registro"].astype(str)
            + " "
            + df_occ["hora_registro"].astype(str).str.split(".").str[0]
        )

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

    def clean_maq_info_prod(self, info: pd.DataFrame) -> pd.DataFrame:
        """
        Limpa os dados de info das máquinas para produção
        """
        # Ordenar por maquina_id asc, turno asc, data_registro desc, hora_registro desc
        df_info = info.sort_values(
            by=["maquina_id", "turno", "data_registro", "hora_registro"],
            ascending=[True, True, False, False],
        )

        # Agrupar por maquina_id e turno e manter o ultimo registro de cada grupo
        df_info = (
            df_info.groupby(["maquina_id", "turno", "data_registro"])
            .first()
            .reset_index()
        )

        # Criar nova coluna combinando data e hora
        df_info["data_hora_registro"] = (
            df_info["data_registro"].astype(str)
            + " "
            + df_info["hora_registro"].astype(str).str.split(".").str[0]
        )

        # Converter coluna data_hora_registro para datetime
        df_info["data_hora_registro"] = pd.to_datetime(
            df_info["data_hora_registro"], format="%Y-%m-%d %H:%M:%S"
        )

        # Se o turno for VES, e a hora de data_hora_registro for entre 00:00:00 e 00:01:00, alterar
        # a data_registro para o dia anterior
        df_info.loc[
            (df_info["turno"] == "VES")
            & (time(0, 0, 0) < df_info["data_hora_registro"].dt.time)
            & (df_info["data_hora_registro"].dt.time < time(0, 5, 0)),
            "data_registro",
        ] = df_info["data_registro"] - pd.Timedelta(days=1)

        # Encontrar primeiro dia do mês atual
        first_day_this_month = pd.to_datetime("today").replace(day=1)

        # Remover datas do mês anterior
        df_info = df_info[
            df_info["data_registro"] >= first_day_this_month.date()
        ]

        # Remover duplicatas com base em 'maquina_id', 'turno' e 'data_registro', mantendo apenas
        # a entrada com a 'data_hora_registro' mais recente
        df_info = df_info.drop_duplicates(
            subset=["maquina_id", "turno", "data_registro"], keep="last"
        )

        # Remover colunas desnecessárias
        df_info.drop(
            columns=[
                "recno",
                "status",
                "ciclo_1_min",
                "ciclo_15_min",
                "tempo_parada",
                "tempo_rodando",
                "hora_registro",
            ],
            inplace=True,
        )

        # Reiniciar o index
        df_info.reset_index(drop=True, inplace=True)

        return df_info
