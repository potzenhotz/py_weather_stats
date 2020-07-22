import pandas as pd
import os
import sys
import requests
from bs4 import BeautifulSoup
import zipfile


class weather_station:
    def __init__(self, station_name: str = "Essen-Bredeney"):
        self.station_name = station_name
        self.data_dir = f"weather_stats{os.sep}data{os.sep}"
        self.dwd_url_body = "https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/daily/kl/historical/"
        self.dwd_url_file_prefix = "tageswerte_KL_"
        self.dwd_url_station_info = (
            f"{self.dwd_url_body}KL_Tageswerte_Beschreibung_Stationen.txt"
        )
        self.station_list_file_name = "station_list.csv"
        self.station_list_file_path = f"{self.data_dir}{self.station_list_file_name}"
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.station_is_downloaded = False
        self.station_file_dir = f"{self.data_dir}{self.station_name}"
        self.station_file_path_zip = f"{self.data_dir}{self.station_name}.zip"
        self.station_file_prefix = "produkt_klima_tag_"
        self.station_file_suffix = ".txt"
        self.define_core_station_info()
        self.check_station_exists()
        if not self.station_exists:
            print("Station does not exist")
            sys.exit()
        self.create_weather_df(station_name=self.station_name)

    def get_raw_staion_list(
        self, file_name: str = "weather_stats/data/raw_station_list.txt"
    ):
        """This function downloads the raw station names file.
        
        The file needs to be transformed to csv manually, due to lack of sufficient delimiter.

        Args:
            file_name: Output file name

        Returns:
           None
        """
        r = requests.get(self.dwd_url_station_info, allow_redirects=True)
        open(file_name, "wb").write(r.content)

    def create_stations_info(self):
        self.df_stations_info = pd.read_csv(self.station_list_file_path, delimiter=";")

    def change_station_df(self, station_name: str):
        self.station_name = station_name
        self.check_station_exists()
        if not self.station_exists:
            print("Station does not exist")
            sys.exit()
        create_weather_df()

    def check_station_downloaded(self):
        self.station_file_downloaded = False
        if os.path.isdir(self.station_file_dir):
            print(f"Station directory is available: {self.station_file_dir}")
            for file_name in os.listdir(self.station_file_dir):
                if file_name.startswith(
                    self.station_file_prefix
                ) and file_name.endswith(self.station_file_suffix):
                    print(f"Station file is available: {file_name}")
                    self.station_file_downloaded = True

    def check_station_exists(self):
        if self.station_name in self.df_stations_info.values:
            print(f"Station {self.station_name} exists")
            self.station_exists = True
        else:
            print(f"Station {self.station_name} does not exist")
            self.station_exists = False

    def define_core_station_info(self):
        # dwd station description bis_datum does not match bis_datum in file name :(
        if not hasattr(self, "df_station_info"):
            self.create_stations_info()
        self.df_station_info = self.df_stations_info[
            self.df_stations_info["Stationsname"] == self.station_name
        ]
        self.station_id = f"{self.df_station_info['Stations_id'].item():05}"
        self.station_start_date = self.df_station_info["von_datum"].item()
        dwd_link_list = "https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/daily/kl/historical/"
        dwd_list = requests.get(dwd_link_list)
        self.dwd_url_station_part = (
            f"{self.dwd_url_file_prefix}{self.station_id}_{self.station_start_date}"
        )
        soup = BeautifulSoup(dwd_list.text, "html.parser")
        for link in soup.findAll("a"):
            file_name = str(link.get("href"))
            if self.dwd_url_station_part in file_name:
                self.dwd_file_name = file_name
        if not hasattr(self, "dwd_file_name"):
            print(f"Station {self.station_name} file on dwd server not found")
            sys.exit()

    def define_station_url(self):
        self.dwd_url_station = f"{self.dwd_url_body}{self.dwd_file_name}"

    def define_station_file_name(self):
        for file_name in os.listdir(self.station_file_dir):
            if file_name.startswith(self.station_file_prefix) and file_name.endswith(
                self.station_file_suffix
            ):
                station_file_name = file_name
        self.station_file_path = f"{self.station_file_dir}{os.sep}{station_file_name}"

    def download_station_file(self):
        self.define_station_url()
        r = requests.get(self.dwd_url_station, allow_redirects=True)
        open(self.station_file_path_zip, "wb").write(r.content)

    def unzip_station_file(self):
        with zipfile.ZipFile(self.station_file_path_zip, "r") as zip_ref:
            zip_ref.extractall(self.station_file_dir)

    def get_station_data(self):
        self.check_station_downloaded()
        if not self.station_file_downloaded:
            self.download_station_file()
            self.unzip_station_file()
        self.define_station_file_name()

    def read_station_csv(self):
        self.df_weather_data = pd.read_csv(self.station_file_path, sep=";",)

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

    def create_weather_df(self):
        self.download_station_data()
        self.read_station_csv()
        self.transform_weather_data()

    def shrink_weather_df(self, testing: bool = False):
        if not self.df_weather_data:
            self.create_weather_df()
        self.df_weather_data = (
            self.df_weather_data["year"].astype(str).str.contains("197")
        )

    def create_temp_df(self):
        self.create_weather_df()
        self.df_temp = self.df_weather_data.pivot(
            index="period", columns="year", values="TMK"
        ).reset_index()
        self.df_temp_melt = pd.melt(
            self.df_weather_data, id_vars=["period", "year"], value_vars=["TMK"]
        )

    def get_temp_df(self, testing: bool = False):
        self.create_temp_df()
        if testing:
            return self.df_temp[["period", 1970, 1971, 1950, 2010]].copy()
        else:
            return self.df_temp


if __name__ == "__main__":
    ws = weather_station()
    # ws.download_station_file()
    # ws.define_station_file_name()
    # ws.check_station_downloaded()
    ws.check_station_exists()
