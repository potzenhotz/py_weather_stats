import pandas as pd
import os
import sys


class weather_station:
    def __init__(self, station: str = "Essen"):
        self.station = station
        self.dir_path = os.path.dirname(os.path.realpath(__file__))

    def read_csv(self):
        self.df_weather_data = pd.read_csv(
            f"{self.dir_path}/data/produkt_klima_tag_19350101_20191231_01303.txt",
            sep=";",
        )

    def transform_weather_data(self):
        # Remove whitespaces from header
        self.df_weather_data = self.df_weather_data.rename(columns=lambda x: x.strip())
        self.df_weather_data["MESS_DATUM"] = pd.to_datetime(
            self.df_weather_data["MESS_DATUM"], format="%Y%m%d"
        )
        self.df_weather_data["year"] = pd.DatetimeIndex(
            self.df_weather_data["MESS_DATUM"]
        ).year
        self.df_weather_data["month"] = pd.DatetimeIndex(
            self.df_weather_data["MESS_DATUM"]
        ).month
        self.df_weather_data["day"] = pd.DatetimeIndex(
            self.df_weather_data["MESS_DATUM"]
        ).day
        self.df_weather_data["period"] = "2000-" + self.df_weather_data[
            "MESS_DATUM"
        ].dt.strftime("%m-%d")
        parameters = ["RSK", "SDK", "PM"]
        for parameter in parameters:
            self.df_weather_data[parameter] = self.df_weather_data[parameter].apply(
                lambda x: x if x >= 0 else None
            )

    def create_temp_df(self):
        self.create_weather_df()
        self.df_temp = self.df_weather_data.pivot(
            index="period", columns="year", values="TMK"
        ).reset_index()
        self.df_temp_melt = pd.melt(
            self.df_weather_data, id_vars=["period", "year"], value_vars=["TMK"]
        )

    def create_weather_df(self, testing: bool = False):
        self.read_csv()
        self.transform_weather_data()

    def get_weather_df(self, testing: bool = False):
        self.create_weather_df()
        if testing:
            return self.df_weather_data[
                (self.df_weather_data["year"].astype(str).str.contains("197"))
            ]
        else:
            return self.df_weather_data

    def get_temp_df(self, testing: bool = False):
        self.create_temp_df()
        if testing:
            return self.df_temp[["period", 1970, 1971, 1950, 2010]].copy()
        else:
            return self.df_temp


if __name__ == "__main__":
    ws = weather_station()
    df_weather = ws.get_weather_df(testing=True)
    print(df_weather.head(40))
    df_temp = ws.get_temp_df(testing=False)
    print(df_temp.head(400))
