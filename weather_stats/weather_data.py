import pandas as pd
import os
import sys
import requests


class weather_station:
    def __init__(self, station: str = "Essen"):
        self.station = station
        self.dir_path = os.path.dirname(os.path.realpath(__file__))

    def get_raw_staion_list(
        self, file_name: str = "weather_stats/data/raw_station_list.txt"
    ):
        self.station_description_url = "https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/daily/kl/historical/KL_Tageswerte_Beschreibung_Stationen.txt"
        r = requests.get(self.station_description_url, allow_redirects=True)
        open(file_name, "wb").write(r.content)

    def get_station_df(self, file_name: str = "weather_stats/data/station_list.csv"):
        self.df_stations = pd.read_csv(file_name, delimiter=";")
        return self.df_stations

    def check_station_downloaded(self, station_name: str = "Essen-Bredeney"):
        return True

    def get_station_data(self, station_name: str = "Essen-Bredeney"):
        pass

    def read_csv(self, file_name: str):
        self.df_weather_data = pd.read_csv(file_name, sep=";",)

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
        self.df_weather_data["period_int"] = pd.to_numeric(
            self.df_weather_data["MESS_DATUM"].dt.strftime("%m")
        )
        parameters = ["RSK", "SDK", "PM", "NM"]
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

    def create_weather_df(
        self, station_name: str = "Essen-Bredeney", testing: bool = False
    ):
        if not self.check_station_downloaded():
            self.get_station_data()
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
    # print(df_weather.head(40))
    # df_temp = ws.get_temp_df(testing=False)
    # print(df_temp.head(400))
    df_filtered = df_weather[(df_weather.year >= 1970) & (df_weather.year <= 1977)]
    df_filtered = df_weather[
        (df_weather.period_int >= 20000101) & (df_weather.period_int <= 20000305)
    ]
    # print(df_filtered)
    # print(df_weather["period_int"].min(), df_weather["period_int"].max())
    ws.get_raw_staion_list()
