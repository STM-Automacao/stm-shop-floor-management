"""
    Módulo para limpeza dos dados
"""

import pandas as pd


class CleanData:
    """
    Classe para limpeza dos dados

    Atributos:
        df (pd.DataFrame): Dataframe com os dados a serem limpos

    Métodos:
        clean_maq_cadastro: Limpa os dados de cadastro das máquinas

    """

    def __init__(self):
        self.df = pd.DataFrame()

    def clean_maq_cadastro(self, data: pd.DataFrame) -> pd.DataFrame:
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
        self.df = data.copy()

        # Remover rows onde a linha é 0
        self.df = self.df[self.df["linha"] != 0]

        # Remover linhas duplicadas (erros de cadastro)
        self.df = self.df.drop_duplicates(
            subset=["data_registro", "linha"], keep="first"
        )

        # Criar nova coluna combinando data e hora
        self.df["data_hora_registro"] = (
            self.df["data_registro"].astype(str)
            + " "
            + self.df["hora_registro"].astype(str).str.split(".").str[0]
        )

        # Converter coluna data_hora_registro para datetime
        self.df["data_hora_registro"] = pd.to_datetime(
            self.df["data_hora_registro"], format="%Y-%m-%d %H:%M:%S"
        )

        # Remover colunas desnecessárias
        self.df = self.df.drop(
            columns=["recno", "data_registro", "hora_registro"]
        )

        # Ordenar dataframe para facilitar trabalho futuro
        self.df = self.df.sort_values(
            by=["maquina_id", "data_hora_registro"], ascending=[True, False]
        )

        # reiniciar o index
        self.df = self.df.reset_index(drop=True)

        return self.df
