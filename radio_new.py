import glob
import json
import os
import random
from functools import partial
from threading import Timer

import customtkinter as ctk
import vlc
from PIL import Image, ImageTk
from screeninfo import get_monitors
import platform
import sys
import time

from radio_config import Config
from station_logos import LogoDist
from timer_interval import Interval

_kiosk_screen_size = (1280, 400)
_check_inactivity_ms = 1000
_update_meta_info_s = 3

_check_config_is_dirty_s = 4

_config_json_path       = "config.json"
_station_btn_size       = 190
_logo_size              = _station_btn_size - 40

_favorites_path         = "favorites"
_stations_logos_path    = "logos"
_stations_logos_glob    = os.path.join(_stations_logos_path, "*.??g")

_img_ext = ['.png', '.jpg', '.jpeg']

_dummy_logo_fn          = "dummy.jpg"
_station_default_logo_path = os.path.join(_stations_logos_path, _dummy_logo_fn)
_station_empty_logo_fn  = "empty.png"

_station_empty          = "empty"

_image_path = "gallery/private/"

_str_stop       = "stop"
_str_play       = "play"
_str_stopped    = "Stopped"
_str_no_info    = "no info"
_str_mute       = "mute"
_str_unmute     = "unmute"


ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"

class CTaFont(ctk.CTkFont):

    def __init__(self):
        super().__init__(size=20, weight="normal")



# --- Helper Classes




# class MyConfig:
#
#     is_dirty = False
#
#     def __init__(self, check_interval_s):
#         self.load_config()
#         self.check_is_dirty_timer = Interval(check_interval_s, self.save_if_dirty)
#
#         if self.get("auto_save_config"):
#             self.start_is_dirty_check()
#             print("Config autosave started")
#         else:
#             print("Config autosave auto_save_config is false")
#
#     def get(self, key):
#         return self.my_config[key]
#
#     def change(self, key, new_value):
#         self.my_config[key] = new_value
#         self.is_dirty = True
#
#     def start_is_dirty_check(self):
#         self.check_is_dirty_timer.start()
#
#     def stop_is_dirty_check(self):
#         self.check_is_dirty_timer.stop()
#
#     def save_if_dirty(self):
#         if self.is_dirty:
#             self.save_config()
#
#     def load_config(self):
#         '''read config from JSON file'''
#
#         with open(_config_json_path) as json_file:
#             self.my_config = json.load(json_file)
#
#         # Print the type of data variable
#         print(f"Loaded config {self.my_config} from {_config_json_path}")
#
#     def save_config(self):
#         with open(_config_json_path, "w") as outfile:
#             json.dump(self.my_config, outfile, indent=8)
#         print(f"Config saved to {_config_json_path}")
#         self.is_dirty = False



class FrameStations(ctk.CTkScrollableFrame):

    def __init__(self, parent, controller):
        super().__init__(parent, orientation='horizontal')
        self.parent = parent
        self.controller = controller
        self.logos = {}
        self.favorite_data = []
        self.btn_station_slot = []
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid(row=0, column=0, sticky="news")
        self.setup_station_slots(self.controller.config.get_favlist_by_idx(self.controller.config.last_favlist)) # TODO change last_fav from idx to name

    def setup_station_slots(self, favlist_name):
        """create station slot buttons"""

        for i, station in enumerate(self.controller.config.favorites_dict[favlist_name].stations):
            logo_fn = station.logo
            logo_img = self.controller.logos.get_image_as_ctk(logo_fn, _logo_size)
            btn_text = station.name

            btn_station_slot = ctk.CTkButton(master=self, compound="top", text=btn_text, image=logo_img, command=partial(self.btn_play_station_cb, i))
            btn_station_slot.grid(row=0, column=i, padx=5, pady=7)

            if logo_fn == _station_empty_logo_fn:
                btn_station_slot.configure(state = "disabled")

            self.btn_station_slot.append(btn_station_slot)

    #TODO mark selected station slot
    def select_and_play_station(self, station_idx):
        current_fav_list = self.controller.config.favorites_dict[self.controller.current_favlist_name]
        new_station_data = current_fav_list.stations[station_idx]
        print(f'selected station_idx={station_idx}, station={new_station_data} from fav_list {self.controller.current_favlist_name}')
        if _station_empty != new_station_data.name:
            self.controller.play_station(new_station_data, station_idx)

    def btn_play_station_cb(self, i):
        #self.controller.reset_timestamp()
        self.select_and_play_station(i)

    def playing(self):
        None

    def stopped(self):
        None

class FrameFavs(ctk.CTkFrame):

    def __init__(self, parent, controller):
        super().__init__(parent)

        self.parent = parent
        self.controller = controller
        self.favorite_btns = []
        self.radio_var = ctk.IntVar(value=self.controller.config.last_favlist)

        for i, fav_list_name in enumerate(self.controller.config.favorites_dict.keys()):
            self.grid_columnconfigure(i, weight=1)
            btn = ctk.CTkRadioButton(master=self, text=fav_list_name,
                                      font=ctk.CTkFont(size=20, weight="bold"),
                                      height=35, radiobutton_width=12, radiobutton_height=12, border_width_unchecked=2,
                                      value=i, command=self.select_fav, variable=self.radio_var)
            btn.grid(row=0, column=i, padx=3, pady=0, sticky="news")
            self.favorite_btns.append(btn)

    def select_fav(self):
        new_favlist_name = self.favorite_btns[self.radio_var.get()].cget('text')
        print(f"Click on favorite list item {self.radio_var.get()}, {new_favlist_name}")
        self.controller.change_to_favlist(new_favlist_name)
        #self.master.master.reset_timestamp()


class FrameVolume(ctk.CTkFrame):

    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller

        self.grid(row=3, column=0, padx=0, pady=0, sticky="esw")
        self.grid_columnconfigure((0,1,2), weight=1)
        self.grid_rowconfigure(0, weight=1)

        # create mute button
        self.btn_mute = ctk.CTkButton(master=self, text=_str_mute, width=_station_btn_size, height=40,
                                       command=self.btn_mute_cb, state='disabled',
                                       font=ctk.CTkFont(size=18, weight="bold"))
        self.btn_mute.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        # create volume slider
        self.sl_volume = (ctk.CTkSlider(master=self, from_=0, to=100, width=250, command=self.volume_slider_event_cb))
        self.sl_volume.configure(number_of_steps=25)
        self.sl_volume.set(self.controller.config.last_volume)
        self.sl_volume.grid(row=0, column=1, padx=0, pady=0, sticky="ew")

        # create stop button
        self.btn_play_stop = ctk.CTkButton(master=self, text=_str_play, width=_station_btn_size, height=40,
                                            command=self.btn_play_stop_cb, font=ctk.CTkFont(size=18, weight="bold"))
        self.btn_play_stop.grid(row=0, column=3, padx=5, pady=5, sticky="e")

    def btn_play_stop_cb(self):
        self.controller.toggle_playing()

    def btn_mute_cb(self):
        self.controller.toggle_mute()

    def playing(self):
        self.btn_mute.configure(state='enabled')
        self.btn_play_stop.configure(text=_str_stop)

    def stopped(self):
        self.btn_mute.configure(state='normal')
        self.btn_play_stop.configure(text=_str_play)

    def update_volume_slider_mute_btn(self, volume):
        if self.controller.is_muted:
            self.btn_mute.configure(text=_str_unmute)
        else:
            self.btn_mute.configure(text=_str_mute)

        self.sl_volume.set(volume)

    def volume_slider_event_cb(self, value):
        self.controller.change_volume(value)


class FrameInfo(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent)

        self.grid_columnconfigure(0, weight=1)

        # create station-title-meta-data label
        self.la_title = ctk.CTkLabel(master=self, text=_str_stopped, fg_color="transparent", font= ctk.CTkFont(size=20, weight="bold"))
        self.la_title.grid(row=0, column=0, sticky="w")

        # create date-time label
        self.la_datetime = ctk.CTkLabel(master=self, text="Datetime", fg_color="transparent", font= ctk.CTkFont(size=20, weight="bold"))
        self.la_datetime.grid(row=0, column=1)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.datetime_tid = None

        #TODO config last_station
        self.station_name = ""
        self.title = ""

        self.update_datetime()

    def stopped(self):
        self.update_media(self.station_name, _str_stopped)

    def playing(self):
        self.update_media(self.station_name, _str_no_info)

    def update_media(self, station_name, title):
        self.station_name = station_name
        self.title = title
        self.la_title.configure(text=f"{station_name}: {title}")

    def update_datetime(self):
        self.datetime_tid = self.la_datetime.configure(text=time.asctime())
        self.after(ms=1000, func=self.update_datetime)

    def stop_datetime(self):
        self.after_cancel(self.datetime_tid)


class Controller:
    def __init__(self, config):
        self.fr_info = None
        self.fr_volume = None
        self.fr_stations = None
        self.fr_favs = None
        self.config = config
        self.logos = LogoDist(img_ext=_img_ext, directory=_stations_logos_path, default_logo_name=_dummy_logo_fn)
        self.config = config
        print(self.config.get_all_stations_dict())

        self.vlc_instance = vlc.Instance()
        self.media_player = self.vlc_instance.media_player_new()
        self.Media = None
        self.is_muted = False
        self.is_playing = False
        self.prev = ""
        self.current_station_idx = self.config.last_station
        self.current_favlist_name = self.config.last_favlist_name

        self.update_timer = Interval(_update_meta_info_s, self.update_meta_info)
        self.update_timer.start()

    def change_to_favlist(self, new_favlist_name):
        self.current_favlist_name = new_favlist_name
        self.fr_stations.setup_station_slots(self.current_favlist_name)
        self.config.change_property("last_favlist_name", new_favlist_name)
        # self.config.change_property("last_favlist", idx)

    def toggle_playing(self ):
        if self.is_playing:
            self.stop_playing()
        else:
            self.play_last_station()

    def stop_playing(self):
        self.media_player.stop()
        self.is_playing=False
        self.fr_volume.stopped()
        self.fr_info.stopped()

    def play_last_station(self):
        station_data = self.config.get_last_station_data()
        self.play_station(station_data, self.config.last_station)

    #TODO get rid of idx
    def play_station(self, new_station_data, new_station_idx):

        if new_station_data and new_station_data.url and new_station_data.name:
            self.media_player.stop()
            self.Media = self.vlc_instance.media_new(new_station_data.url)
            self.Media.get_mrl()
            self.media_player.set_media(self.Media)
            self.media_player.play()
            self.is_playing=True
            self.fr_volume.playing()
            self.config.change_property("last_station", self.current_station_idx)
            self.config.change_property("last_favlist_name", self.config.last_favlist_name)
            self.config.change_property("last_station_url", new_station_data.url)
            self.config.change_property("last_station_logo", new_station_data.logo)
            self.config.change_property("last_station_name", new_station_data.name)
            self.current_station_idx = new_station_idx
            self.fr_stations.playing()
            self.fr_info.playing()
            self.prev = ""
            self.update_meta_info()
        else:
            print(f"new_station_data = {new_station_data} is empty!")

    # https://stackoverflow.com/questions/70509728/how-to-get-audiostream-metadata-using-vlc-py
    def update_meta_info(self):
        """Update GUI meta data (e.g. title-info) that comes with the stream"""

        if self.Media is not None:
            meta = self.Media.get_meta(12) # vlc.Meta 12: 'NowPlaying',
            if meta != self.prev:
                self.prev = meta
                station_name = self.get_station_data(favlist_name=self.current_favlist_name, station_idx=self.current_station_idx).name
                if meta is None:
                    print("if meta is None:")
                    meta = _str_no_info

                if not self.media_player.is_playing():
                    print("if not self.media_player.is_playing():")
                    meta = _str_stopped

                print(f"Now playing {station_name}: {meta}")
                self.fr_info.update_media(station_name, meta)
                #self.func_update_screensaver(station_name, meta, self.get_station_data()[self.now_playing_idx]["logo"])

    def get_station_data(self, favlist_name, station_idx):
        fav_list = self.config.favorites_dict[favlist_name]
        return fav_list.stations[station_idx]

    def change_volume(self, volume: int):
        if volume == 0 and not self.is_muted:
            self.mute()
        else:
            self.unmute(volume)

    def unmute(self, volume: int):
        self.is_muted = False
        self.media_player.audio_set_volume(int(volume))
        self.config.change_property("last_volume", self.media_player.audio_get_volume())
        self.fr_volume.update_volume_slider_mute_btn(volume)

    def mute(self):
        if not self.is_muted:
            self.config.change_property("last_volume", self.media_player.audio_get_volume())
            self.is_muted = True
            self.media_player.audio_set_volume(0)
            self.fr_volume.update_volume_slider_mute_btn(0)

    def toggle_mute(self):
        if self.is_muted:
            self.unmute(self.config.last_volume)
        else:
            self.mute()
        #self.master.master.reset_timestamp()

    def close_app(self):
        self.stop_playing()

    def up_and_running(self):
        self.is_playing=False
        self.change_to_favlist(self.config.last_favlist_name)
        self.current_station_idx = self.config.last_station
        self.change_volume(self.config.last_volume)
        self.prev = ""
        self.update_meta_info()
        self.fr_volume.stopped()
        station_data = self.config.get_last_station_data()
        self.fr_info.update_media(station_data.name, "")
        self.fr_info.stopped()

class RadioFrame(ctk.CTkFrame):

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.controller = Controller(Config.from_json(_config_json_path))
        self.grid_columnconfigure(0, weight=1)
        #self.grid_rowconfigure((0,1,2,3), weight=1)
        self.controller.fr_info = FrameInfo(self)
        self.controller.fr_volume = FrameVolume(self, controller = self.controller)
        self.controller.fr_stations = FrameStations(self, controller = self.controller)
        self.controller.fr_favs = FrameFavs(self, controller = self.controller)

        self.controller.fr_favs.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        self.controller.fr_stations.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.controller.fr_volume.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        self.controller.fr_info.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        self.controller.up_and_running()

class App(ctk.CTk):
    def __init__(self, kiosk_mode):
        super().__init__()

        self.kiosk_mode = kiosk_mode
        self.is_screensaver_on = False
        self.attributes("-fullscreen", kiosk_mode) # run fullscreen
        self.wm_attributes("-topmost", kiosk_mode) # keep on top

        #self.my_config = MyConfig(_check_config_is_dirty_s)

        self.last_activity_time = time.time()
        self.inactivity_period_s = 5  # in seconds
        self.title("Screensaver")
        self.geometry(f"{_kiosk_screen_size[0]}x{_kiosk_screen_size[1]}")

        print(f"App Window Size start ({self.winfo_width()}, {self.winfo_height()})")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.radio_frame = RadioFrame(self, width=_kiosk_screen_size[0], height=_kiosk_screen_size[1])
        self.radio_frame.grid(row=0, column=0, padx=0, pady=0, sticky="news")

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        # Your custom code here
        print("App is closing...")

        self.radio_frame.controller.close_app()

        self.destroy()


print(f"sys.argv={sys.argv}, len(sys.argv)={len(sys.argv)}")
_kiosk_mode = False

if len(sys.argv) > 1:
    if sys.argv[1]== 'kiosk':
        _kiosk_mode = True

if os.environ.get('DISPLAY','') == '':
    print('no display found. Using :0.0')
    os.environ.__setitem__('DISPLAY', ':0.0')

print(f"Running Env {platform.system()}")

print("_kiosk_mode=",_kiosk_mode)

if __name__ == "__main__":
    #    try:
    monitor = get_monitors()

    print(f"Monitor List: {monitor}")

    app = App(_kiosk_mode)

    screen_width = app.winfo_screenwidth()
    screen_height = app.winfo_screenheight()
    print(f"app.winfo_screenwidth() x  app.winfo_screenheight() = {screen_width}x{screen_height}")

    app.mainloop()

#    except Exception as e:
#        print(f"An error occurred: {e}")
#        input("Press Enter to exit...")