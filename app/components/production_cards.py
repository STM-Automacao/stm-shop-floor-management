"""
    Module for production cards
    - Autor: Bruno Tomaz
    - Data de criação: 01/03/2024
"""

# cSpell: words producao emissao

import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
from dash import html
from helpers.types import CICLOS_ESPERADOS


class ProductionCards:
    """
    A class representing production cards.
    """

    def __strings(self, df_prod: pd.DataFrame) -> tuple:
        """
        Returns a tuple of production strings for different shifts.

        Args:
            df_prod (pd.DataFrame): DataFrame containing production data.

        Returns:
            tuple: A tuple of production strings for total,
            morning shift, afternoon shift, and night shift.
        """

        df_prod_mat = df_prod[df_prod["turno"] == "MAT"]
        df_prod_ves = df_prod[df_prod["turno"] == "VES"]
        df_prod_not = df_prod[df_prod["turno"] == "NOT"]

        producao_total = f"{df_prod['total_produzido'].sum():,} caixas".replace(",", ".")
        producao_mat = f"{df_prod_mat['total_produzido'].sum():,} caixas".replace(",", ".")
        producao_ves = f"{df_prod_ves['total_produzido'].sum():,} caixas".replace(",", ".")
        producao_not = f"{df_prod_not['total_produzido'].sum():,} caixas".replace(",", ".")

        return producao_total, producao_mat, producao_ves, producao_not

    def prepare_prod_data(self, df_prod: pd.DataFrame) -> tuple:
        """
        Prepare production data for display.

        Args:
            df_prod (pd.DataFrame): The input DataFrame containing production data.

        Returns:
            tuple: A tuple containing the following production information:
                - producao_total (str): Total production in boxes.
                - producao_mat (str): Production in the morning shift in boxes.
                - producao_ves (str): Production in the afternoon shift in boxes.
                - producao_not (str): Production in the night shift in boxes.
        """

        # Produção total
        df_prod.loc[:, "total_produzido"] = np.floor(df_prod["total_produzido"] / 10)  # caixas
        df_prod.loc[:, "total_produzido"] = df_prod["total_produzido"].astype(int)

        # Strings
        producao_total, producao_mat, producao_ves, producao_not = self.__strings(df_prod)

        return producao_total, producao_mat, producao_ves, producao_not

    def prepare_cxs_data(self, df_cxs: pd.DataFrame) -> tuple:
        """
        Prepares the data for CXS (Card X System) production cards.

        Args:
            df_cxs (pd.DataFrame): The input DataFrame containing the production data.

        Returns:
            tuple: A tuple containing the following production values:
                - producao_total (str): The total production value.
                - producao_mat (str): The production value for the morning shift.
                - producao_ves (str): The production value for the afternoon shift.
                - producao_not (str): The production value for the night shift.
        """

        # Identifica o turno
        # df_cxs.loc[:, "HORA"] = pd.to_datetime(df_cxs["HORA"], format="%H:%M:%S").dt.hour
        # df_cxs.loc[:, "TURNO"] = pd.cut(
        #     df_cxs["HORA"],
        #     bins=[0, 8, 16, 24],
        #     labels=["NOT", "MAT", "VES"],
        #     right=False,
        # )

        df_cxs = df_cxs.assign(
            HORA=pd.to_datetime(df_cxs["HORA"], format="%H:%M:%S").dt.hour,
            TURNO=pd.cut(
                pd.to_datetime(df_cxs["HORA"], format="%H:%M:%S").dt.hour,
                bins=[0, 8, 16, 24],
                labels=["NOT", "MAT", "VES"],
                right=False,
            ),
        )

        # Agrupa a produção por turno
        df_cxs = (
            df_cxs.groupby(["EMISSAO", "TURNO"], observed=False).agg({"QTD": "sum"}).reset_index()
        )

        # Ajuste no nome das colunas
        df_cxs.columns = ["EMISSAO", "turno", "total_produzido"]

        # Strings
        producao_total, producao_mat, producao_ves, producao_not = self.__strings(df_cxs)

        return producao_total, producao_mat, producao_ves, producao_not

    def create_card(
        self,
        df_info: pd.DataFrame,
        dataframe: pd.DataFrame,
        today: bool = False,
        cf: bool = False,
        total: int = 0,
    ) -> list:
        """
        Creates production cards based on the provided dataframes.

        Args:
            df_info (pd.DataFrame): DataFrame containing information about production.
            df_prod (pd.DataFrame): DataFrame containing production data.
            today (bool, optional): Flag indicating whether to filter data for
            today's production. Defaults to False.

        Returns:
            list: List of production cards in the form of HTML elements.
        """

        # Conseguir a data de hoje
        date_today = pd.to_datetime("today").strftime("%Y-%m-%d")

        # Criar df_prod
        df_prod = dataframe.copy() if not cf else None

        if today:
            df_prod = (
                dataframe[pd.to_datetime(dataframe["data_registro"]) == date_today]
                if not cf
                else None
            )
            df_info = df_info[
                pd.to_datetime(df_info["data_hora_registro"]).dt.strftime("%Y-%m-%d") == date_today
            ]

        if cf:
            dataframe["EMISSAO"] = dataframe["EMISSAO"].astype(str)
            dataframe.loc[:, "EMISSAO"] = pd.to_datetime(dataframe["EMISSAO"], format="%Y%m%d")

        # Incluir só as caixas que entram na câmara fria hoje
        df_cxs = dataframe[pd.to_datetime(dataframe["EMISSAO"]) == date_today] if cf else None

        # Encontra os valores de produção
        if not cf:
            prod_total, prod_mat, prod_ves, prod_not = self.prepare_prod_data(df_prod)
        else:
            prod_total, prod_mat, prod_ves, prod_not = self.prepare_cxs_data(df_cxs)

        # Tempo total de parada programada
        df_info = df_info[df_info["motivo_id"] == 12]

        # Potencial de Produção
        potencial = np.floor(df_info["tempo_registro_min"].sum() * (CICLOS_ESPERADOS * 2) / 10)

        # Strings
        total_programada = f"{df_info['tempo_registro_min'].sum():,} min".replace(",", ".")
        caixas_potencial = f"{potencial:,.0f} cxs".replace(",", ".")
        total = f"{total:,}".replace(",", ".")

        # Cards
        all_production = [
            (prod_total, "Produção Total"),
            (prod_not, "Produção Noturno"),
            (prod_mat, "Produção Matutino"),
            (prod_ves, "Produção Vespertino"),
        ]
        cols = [
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader(title),
                        dbc.CardBody(
                            prod,
                            className="card-body-modal-style fs-3",
                        ),
                    ],
                    class_name="h-100 inter",
                ),
                md=2,
            )
            for prod, title in all_production
        ]

        title = "Produção do Mês Atual" if not today else "Produção de Hoje"

        total_cxs = dbc.Col(
            dbc.Card(
                [
                    dbc.CardHeader("Total de Caixas"),
                    dbc.CardBody(
                        [
                            html.P(
                                "Caixas na Câmara Fria às 00hs", className="fs-5 align-self-center"
                            ),
                            html.P(
                                f"Total de Caixas --> {total} cxs",
                                className="fs-5 align-self-center",
                            ),
                        ],
                        class_name="d-flex flex-column justify-content-center",
                    ),
                ],
                class_name="h-100 inter",
            ),
        )

        return [
            dbc.Row(
                html.H5(
                    "Entradas na Câmara Fria de Hoje" if cf else title,
                    className="text-center inter",
                ),
                class_name="p-1",
            ),
            dbc.Row(
                [
                    *cols,
                    (
                        total_cxs
                        if cf
                        else dbc.Col(
                            dbc.Card(
                                [
                                    dbc.CardHeader("Parada Programada"),
                                    dbc.CardBody(
                                        [
                                            html.P(
                                                f"Parada Programada --> {total_programada}",
                                                className="fs-5 align-self-center",
                                            ),
                                            html.P(
                                                f"Potencial de Produção --> {caixas_potencial}",
                                                className="fs-5 align-self-center",
                                            ),
                                        ],
                                        class_name="d-flex flex-column justify-content-center",
                                    ),
                                ],
                                class_name="h-100 inter",
                            ),
                            md=4,
                        )
                    ),
                ]
            ),
        ]
