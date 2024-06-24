"""Módulo responsável por gerenciar os grandes dados e os dados históricos de paradas."""

from datetime import datetime, timedelta
from threading import Lock

from database.last_month_ind import LastMonthInd
from service.big_data import BigData


class BigStopsDataManager:
    """
    Classe responsável por gerenciar os grandes dados e os dados históricos de paradas.
    """

    def __init__(self):
        self.df_big = None
        self.df_stops = None
        self.last_update_time = datetime.min
        self.lock = Lock()
        self.lm = LastMonthInd()
        self.bg = BigData()
        self.get_big_stops_if_needed()

    def get_big_stops(self):
        """
        Função simulada que busca os grandes dados e os dados históricos de paradas.
        """

        big = self.bg.get_big_data()
        stops, _, _ = self.lm.get_historic_data_analysis()

        return big, stops

    def get_big_stops_if_needed(self):
        """
        Recupera os grandes dados e os dados históricos de paradas se
        a última atualização foi há mais de 24 horas.
        """
        with self.lock:
            if datetime.now() - self.last_update_time > timedelta(days=1):
                self.df_big, self.df_stops = self.get_big_stops()
                self.last_update_time = datetime.now()
