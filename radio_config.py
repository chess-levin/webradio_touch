import json
import os

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class RadioStation:
    name: str
    url: str
    logo: str

@dataclass
class FavoritesList:
    filename: str
    stations: List[RadioStation] = field(default_factory=list)

    def __init__(self, favorites_dir, file_name: str):
        self.stations = self.load_stations_from_json(os.path.join(favorites_dir, file_name))
        self.filename = file_name

    @classmethod
    def load_stations_from_json(cls, file_path: str) -> List[RadioStation]:
        with open(file_path, 'r') as file:
            data = json.load(file)
            stations = [RadioStation(**station) for station in data]
        return stations

@dataclass
class Config:
    favorites_dict: Dict[str, FavoritesList]
    favorites_dir: str
    last_favlist: int
    last_favlist_name: str
    last_station: int
    last_station_name: str
    last_station_url:str
    last_station_logo: str
    last_volume: int
    screensaver_after_s: int
    auto_save_config: bool
    is_dirty: bool = False
    filepath: str = None
    all_stations_dict = {}

    @staticmethod
    def from_json(config_filepath: str) -> 'Config':
        with open(config_filepath, 'r') as file:
            data = json.load(file)
            favorites_dict = {}
            for favorite in data['favorites']:
                favorites_dict[favorite['name']] = FavoritesList(favorites_dir=data['favorites_dir'], file_name=favorite['file'])
            return Config(
                favorites_dict=favorites_dict,
                favorites_dir=data['favorites_dir'],
                last_favlist=data['last_favlist'],
                last_favlist_name=data['last_favlist_name'],
                last_station=data['last_station'],
                last_station_name=data['last_station_name'],
                last_station_url=data['last_station_url'],
                last_station_logo=data['last_station_logo'],
                last_volume=data['last_volume'],
                screensaver_after_s=data['screensaver_after_s'],
                auto_save_config=data['auto_save_config'],
                filepath = config_filepath
            )

    def to_json(self):
        data = {
            'favorites': [{'name': fav_list[0], 'file': fav_list[1].filename} for fav_list in self.favorites_dict.items()],
            'favorites_dir': self.favorites_dir,
            'last_favlist': self.last_favlist,
            'last_favlist_name': self.last_favlist_name,
            'last_station': self.last_station,
            'last_station_name': self.last_station_name,
            'last_station_url': self.last_station_url,
            'last_station_logo': self.last_station_logo,
            'last_volume': self.last_volume,
            'screensaver_after_s': self.screensaver_after_s,
            'auto_save_config': self.auto_save_config
        }
        with open(self.filepath, 'w') as file:
            json.dump(data, file, indent=4)

    def get_last_station_data(self):
        return RadioStation(name=self.last_station_name, url=self.last_station_url, logo=self.last_station_logo)

    def get_favlist_by_idx(self, idx):
        for i, name in enumerate(self.favorites_dict.keys()):
            if i == 0:
                fallback = name
            if i == idx:
                return name
        return fallback

    def change_property(self, prop_name, prop_value):
        if hasattr(self, prop_name):
            self.__setattr__(prop_name, prop_value)
            self.is_dirty = True
        else:
            print(f"Error: Config property '{prop_name}' does not exist.")

    def __post_init__(self):
        self.all_stations_dict = self.get_all_stations_dict()
        print(f"all {len(self.all_stations_dict)} stations:  {self.all_stations_dict} ")

    def get_all_stations_dict(self):
        all_stations = {}
        for i, name in enumerate(self.favorites_dict.keys()):
            for station in self.favorites_dict[name].stations:
                if all_stations.get(station.name) is not None:
                    print(f"station data {all_stations.get(station.name)} already exists. Skipping new {station}")
                else:
                    all_stations[station.name] = station

        return all_stations

    def get_station_data_by_name(self, name):
        data = self.all_stations_dict.get(name)
        if data is None:
            print(f"Station data for '{name}' does not exist.")
        return data


#_favorites_path = 'favorites'
# = Config.from_json('config.json')
#print(config)
#config.to_json()

#favorites_list = FavoritesList('favorites/fav_news.json')
#for station in favorites_list.stations:
#    print(f"Name: {station.name}, URL: {station.url}, Logo: {station.logo}")