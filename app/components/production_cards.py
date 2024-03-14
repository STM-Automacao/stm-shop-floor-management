"""
    Module for production cards
    - Autor: Bruno Tomaz
    - Data de criação: 01/03/2024
"""

# cSpell: words producao

import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
from dash import html
from helpers.types import CICLOS_ESPERADOS

pd.options.mode.copy_on_write = True


class ProductionCards:
    """
    A class representing production cards.
    """

    def create_card(
        self, df_info: pd.DataFrame, df_prod: pd.DataFrame, today: bool = False
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

        if today:
            df_prod = df_prod[pd.to_datetime(df_prod["data_registro"]) == date_today]
            df_info = df_info[
                pd.to_datetime(df_info["data_hora_registro"]).dt.strftime("%Y-%m-%d") == date_today
            ]

        # Produção total
        df_prod.loc[:, "total_produzido"] = np.floor(df_prod["total_produzido"] / 10)  # caixas
        df_prod.loc[:, "total_produzido"] = df_prod["total_produzido"].astype(int)

        # Produção por turno
        df_prod_mat = df_prod[df_prod["turno"] == "MAT"]
        df_prod_ves = df_prod[df_prod["turno"] == "VES"]
        df_prod_not = df_prod[df_prod["turno"] == "NOT"]

        # Tempo total de parada programada
        df_info = df_info[df_info["motivo_id"] == 12]

        # Potencial de Produção
        potencial = np.floor(df_info["tempo_registro_min"].sum() * (CICLOS_ESPERADOS * 2) / 10)

        # Strings
        producao_total = f"{df_prod['total_produzido'].sum():,} caixas".replace(",", ".")
        producao_mat = f"{df_prod_mat['total_produzido'].sum():,} caixas".replace(",", ".")
        producao_ves = f"{df_prod_ves['total_produzido'].sum():,} caixas".replace(",", ".")
        producao_not = f"{df_prod_not['total_produzido'].sum():,} caixas".replace(",", ".")
        total_programada = f"{df_info['tempo_registro_min'].sum():,} min".replace(",", ".")
        caixas_potencial = f"{potencial:,.0f} cxs".replace(",", ".")

        # Cards
        all_production = [
            (producao_total, "Produção Total"),
            (producao_not, "Produção Noturno"),
            (producao_mat, "Produção Matutino"),
            (producao_ves, "Produção Vespertino"),
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

        return [
            dbc.Row(
                html.H5(
                    "Produção Total" if not today else "Produção de Hoje",
                    className="text-center inter",
                ),
                class_name="p-1",
            ),
            dbc.Row(
                [
                    *cols,
                    dbc.Col(
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
                    ),
                ]
            ),
        ]
