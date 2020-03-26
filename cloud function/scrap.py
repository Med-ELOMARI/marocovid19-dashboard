import json
from datetime import datetime

import pandas as pd
from bs4 import BeautifulSoup
from requests import get


class Scrapper:
    """
    Scrapper Class with  BeautifulSoup to parse the data from the specific url using the selectors
    """

    def __init__(
        self,
        url,
        headers,
        date_selector,
        Tested_selector,
        Infected_selector,
        Recovered_Died_selector,
        table_selector,
    ):
        self.table_selector = table_selector
        self.Recovered_Died_selector = Recovered_Died_selector
        self.Infected_selector = Infected_selector
        self.Tested_selector = Tested_selector
        self.date_selector = date_selector
        self.resp = get(url, headers=headers)
        if self.resp.status_code != 200:
            raise Exception("Request Error")

        self.soup = BeautifulSoup(
            self.resp.content, "html.parser", from_encoding="utf-8"
        )

    @staticmethod
    def parse_date(date):
        try:
            return datetime.strptime(date, "​ %HH%M​​  %d-%m-%Y").ctime()
        except:
            return date

    def get_table_as_json(self, tab):
        df = pd.read_html(str(tab), encoding="utf-8")[0]
        df = df.applymap(lambda x: self.clean(x.strip()))
        df.columns = [self.clean(col) for col in df.columns]
        return df.to_json(orient="records", force_ascii=False)

    def get_data(self):
        """
        :return: dict
        """
        date = self.parse_date(
            self.soup.select(self.date_selector)[0].getText().strip()
        )
        Tested = self.soup.select(self.Tested_selector)[0].getText()
        Infected = self.soup.select(self.Infected_selector)[0].getText()
        Recovered, Died = (
            self.soup.select(self.Recovered_Died_selector)[0].getText().split("\u200b")
        )
        tab = self.soup.find("table", self.table_selector)
        tab_json = self.get_table_as_json(tab)
        return dict(
            date=date,
            Tested=int(self.clean(Tested)),
            Infected=int(self.clean(Infected)),
            Recovered=int(self.clean(Recovered)),
            Died=int(self.clean(Died)),
            tab_json=json.loads(tab_json),
        )

    @staticmethod
    def clean(data):
        """
        just a work around to clean ascii left overs
        :param data:
        :return:
        """
        # Todo Fix encoding and remove clean function
        return data.replace("\u200b", "").replace("\n", "")


def convert_to_date(date, form="%Y-%m-%d"):
    """
    ctime to %Y-%m-%d
    :param date:
    :return: datetime object
    """
    return datetime.strptime(str(date), "%a %b %d %H:%M:%S %Y").strftime(form)
