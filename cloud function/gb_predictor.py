import json
import pickle
from datetime import timedelta, datetime

import joblib
import numpy as np
import pandas as pd


class Processor:
    def __init__(self, raw_data: dict):
        self.df = self.clean(raw_data)

    def clean(self, raw_data):
        df = pd.DataFrame()
        df["Confirmed"] = pd.DataFrame.from_dict(raw_data, orient="index")[
            "ConfirmedCases"
        ]
        df = df.loc[(df != 0).any(1)]  # Remove zeros
        df["Date"] = pd.to_datetime(df.index)
        return df


class GB_Predictor(Processor):
    """
    gradient boosting method that uses gradient boosting model  based learning algorithms.
    """

    DAYS_BATCH = 5
    COUNTRY_CODE = 71  # morocco id in training data set

    def __init__(self, raw_data: dict, model: str):
        super().__init__(raw_data)
        self.pred_steps = 28
        self.model = self.load(model)
        self.Last_day = self.df.iloc[-1]

    @staticmethod
    def roll_data(input, n, last_day):
        input[:n] = np.roll(input[:n], -1)
        input[n - 1] = last_day  # Lag
        return input

    def load(self, model):
        # with open(model, "rb") as f:
        #     return pickle.load(f)
        return joblib.load(open(model, "rb"))

    def _make_date_range(self, pred_steps=None):
        self.pred_steps = pred_steps or self.pred_steps
        return pd.to_datetime(
            pd.date_range(
                start=self.Last_day["Date"] + timedelta(days=1),
                end=self.Last_day["Date"] + timedelta(days=pred_steps),
                freq="D",
            ).values
        )

    def get_inits(self):
        pred_cat = [0, self.COUNTRY_CODE, 3, datetime.now().isocalendar()[1]]
        pred_lags = self.df["Confirmed"].copy().values[-5:]
        return pred_cat, pred_lags

    def get_ranges(self, pred_steps):
        dt_rng = self._make_date_range(pred_steps)
        pred_months = pd.Series(dt_rng).apply(lambda dt: dt.month)
        pred_weeks = pd.Series(dt_rng).apply(lambda dt: dt.week)
        return dt_rng, pred_weeks, pred_months

    def predict(self, pred_steps, enable_rounding=True, as_df=True):
        predictions = dict()
        dt_rng, pred_weeks, pred_months = self.get_ranges(pred_steps)
        pred_cat, pred_lags = self.get_inits()

        for d in range(pred_steps):
            pred_cat[1] = pred_months[d]
            pred_cat[2] = pred_weeks[d]
            y = self.model.predict(np.hstack([pred_cat, pred_lags]).reshape(1, -1))[0]

            if enable_rounding:
                # rounding the value
                y = round(y)

            pred_lags = self.roll_data(pred_lags, self.DAYS_BATCH, y)

            predictions[dt_rng[d].strftime("%Y-%m-%d")] = y

        return (
            pd.DataFrame.from_dict(predictions, orient="index", columns=["Confirmed"])
            if as_df
            else predictions
        )


if __name__ == "__main__":
    with open("Data/my_data2.json", "rb") as f:
        data = json.load(f)

    p = GB_Predictor(data["raw"], "model.pkl")
    r = p.predict(10)
    print(r)
