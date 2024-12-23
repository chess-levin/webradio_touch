import customtkinter as ctki
import tkinter as tk 
from PIL import Image, ImageTk
from functools import partial
from threading import Timer
import vlc
import json
import time
import glob
import platform
import sys
import os
import random

from diashow_saver import DiaShowCanvas


ctki.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
ctki.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"

_win_width  = 1280
_win_height = 400

_icon_path              = "icons/radio_icon.png"
_config_json_path       = "config.json"
_favorites_path         = "favorites"
_stations_logos_path    = "logos"
_stations_logos_glob    = os.path.join(_stations_logos_path, "*.??g")


_dummy_logo_fn          = "dummy.jpg"
_station_default_logo_path = os.path.join(_stations_logos_path, _dummy_logo_fn)
_station_empty_logo_fn  = "empty.png"

_station_empty          = "empty"

_screensaver_jump_ms    = 15000

_station_btn_size       = 190
_logo_size              = _station_btn_size - 40

_check_for_screensaver_ms = 5000
_check_config_is_dirty_s = 4

_min_brightness = 25
_max_brightness = 200

_str_stop       = "stop"
_str_play       = "play"
_str_stopped    = "Stopped"
_str_no_info    = "no info"
_str_mute       = "mute"
_str_unmute     = "unmute"

# --- Helper Functions --------

def state_by_bool(state):
    if state:
        return 'normal'
    else:
        return 'disabled'

def rgb2hex(r, g, b):
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)

class CTaFont(ctki.CTkFont):

    def __init__(self):
        super().__init__(size=20, weight="normal")


# --- Helper Classes
        
class Interval(object):

    def __init__(self, interval, function, args=[], kwargs={}):
        """
        Runs the function at a specified interval with given arguments.
        """
        self.interval = interval
        self.function = partial(function, *args, **kwargs)
        self.running  = False 
        self._timer   = None 

    def __call__(self):
        """
        Handler function for calling the partial and continuting. 
        """
        self.running = False  # mark not running
        self.start()          # reset the timer for the next go 
        self.function()       # call the partial function 

    def start(self):
        """
        Starts the interval and lets it run. 
        """
        if self.running:
            # Don't start if we're running! 
            return 
            
        # Create the timer object, start and set state. 
        self._timer = Timer(self.interval, self)
        self._timer.start() 
        self.running = True

    def stop(self):
        """
        Cancel the interval (no more function calls).
        """
        if self._timer:
            self._timer.cancel() 
        self.running = False 
        self._timer  = None
       

class MyConfig:

    is_dirty = False

    def __init__(self, check_interval_s):
        self.load_config()
        self.check_is_dirty_timer = Interval(check_interval_s, self.save_if_dirty)

        if self.get("auto_save_config"):
            self.start_is_dirty_check()
            print("Config autosave started")
        else:
            print("Config autosave auto_save_config is false")

    def get(self, key):
        return self.my_config[key]

    def change(self, key, new_value):
        self.my_config[key] = new_value
        self.is_dirty = True

    def start_is_dirty_check(self):
        self.check_is_dirty_timer.start()
       
    def stop_is_dirty_check(self):
        self.check_is_dirty_timer.stop()

    def save_if_dirty(self):
        if self.is_dirty:
            self.save_config()

    def load_config(self):
        '''read config from JSON file'''

        with open(_config_json_path) as json_file:
            self.my_config = json.load(json_file)
        
        # Print the type of data variable
        print(f"Loaded config {self.my_config} from {_config_json_path}")

    def save_config(self):
        with open(_config_json_path, "w") as outfile: 
            json.dump(self.my_config, outfile, indent=8)
        print(f"Config saved to {_config_json_path}")
        self.is_dirty = False


# ---- Screensaver classes

# https://www.tutorialspoint.com/how-to-set-the-canvas-size-properly-in-tkinter



class FrameScreensaverDigiClockContent(ctki.CTkFrame):

    def __init__(self, parent, return_to_radio_func):
        super().__init__(parent)
        self.return_to_radio_func = return_to_radio_func
        
        self.brightness = _max_brightness
        self.conuter = -1
        self.timer = 0
        self.la_clock = ctki.CTkLabel(master=self, text="HH:MM:SS", font=ctki.CTkFont(size=300, weight="normal"))
        self.la_clock.grid(row=0, column=0, sticky="news")
        self.grid_columnconfigure((0), weight=1)
        self.grid_rowconfigure((0), weight=1)
        self.la_clock.bind(sequence="<Button-1>", command=self.stop, add='+')

    def stop(self, event):
        print("Stop Screensaver")
        self.after_cancel(self.tid_update_time)
        self.return_to_radio_func()

    def new_color(self):
        if self.brightness < _min_brightness:
            self.conuter = +1
        if self.brightness > _max_brightness:
            self.conuter = -1

        self.brightness = self.brightness + self.conuter

        return rgb2hex(self.brightness, self.brightness, self.brightness)

    def update_time(self):
        c = self.new_color()
        self.la_clock.configure(text_color = c)

        if self.timer < 5:
            current_datetime = time.strftime('%H:%M:%S')
            self.la_clock.configure(font=ctki.CTkFont(size=300, weight="normal"))
        else:
            current_datetime = time.strftime("%A,\n %B %d")
            self.la_clock.configure(font=ctki.CTkFont(size=160, weight="normal") )

        self.la_clock.configure(text=current_datetime)
        self.timer += 1
        if self.timer > 10:
            self.timer = 0

        self.tid_update_time = self.after(1000, self.update_time)

    def activate(self):
        super().grid(row=0, column=0, padx=0, pady=0, sticky="news")
        self.brightness = _max_brightness
        self.update_time()

    
    def update_titel_info(self, station, title, logo):
        pass


class FrameScreensaverPlayingContent(ctki.CTkFrame):

    def __init__(self, parent, return_func, logos, media_player):
        super().__init__(parent)

        self.parent = parent
        self.return_to_radio_func = return_func
        self.logos = logos
        self.media_player = media_player
        self.bind(sequence="<Button-1>", command=self.stop, add='+')

        self.max_cols = 5
        self.grid_columnconfigure((0,1,2,3,4,self.max_cols), weight=0)
        self.grid_rowconfigure((0,1,2,3), weight=0)
       
        self.current_col = 4

        for i in range(0,6):
            la_col = ctki.CTkLabel(master=self, text="", height=1, width=200)
            la_col.grid(row=0, column=i)

        # create date-time label
        self.la_dtime = ctki.CTkLabel(master=self, text="Datetime", font=ctki.CTkFont(size=18, weight="normal"))
        self.la_dtime.grid(row=0, column=self.current_col, padx=5, pady=0, sticky="")
        self.la_dtime.bind(sequence="<Button-1>", command=self.stop, add='+')
        
        self.la_logo = ctki.CTkLabel(master=self, text="", image=self.logos[_dummy_logo_fn])
        self.la_logo.grid(row=1, column=self.current_col, padx=5, pady=40, sticky="")
        self.la_logo.bind(sequence="<Button-1>", command=self.stop, add='+')

        self.la_name = ctki.CTkLabel(master=self, text="Station", font=ctki.CTkFont(size=18, weight="normal") )
        self.la_name.grid(row=2, column=self.current_col, padx=5, pady=40, sticky="")
        self.la_name.bind(sequence="<Button-1>", command=self.stop, add='+')

        self.la_title = ctki.CTkLabel(master=self, text="Title-Info", height=30, width=50, font=ctki.CTkFont(size=22, weight="bold"))
        self.la_title.grid(row=3, column=self.current_col, padx=5, pady=0, sticky="")
        self.la_title.bind(sequence="<Button-1>", command=self.stop, add='+')

    def stop(self, event):
        print("Stop Screensaver")
        self.after_cancel(self.tid_move_content)
        self.after_cancel(self.tid_update_datetime)
        self.return_to_radio_func()
        
    def activate(self):
        self.grid(row=0, column=0, padx=0, pady=0, sticky="news")
        self.tid_move_content = self.after(ms=2000, func=self.move_content)
        self.update_datetime()

    def move_content(self):
        #self.current_col = (self.current_col + 1) % 5
        self.current_col = random.randint(0, self.max_cols)

        self.la_dtime.grid_forget()
        self.la_dtime.grid(column=self.current_col)
        self.la_logo.grid_forget()
        self.la_logo.grid(column=self.current_col)
        self.la_name.grid_forget()
        self.la_name.grid(column=self.current_col)
        self.la_title.grid_forget()
        self.la_title.grid(column=self.current_col)
        self.tid_move_content = self.after(ms=_screensaver_jump_ms, func=self.move_content)
    
    def update_titel_info(self, station, title, logo):
        if (not self.media_player.is_playing()):
            title = _str_stopped
        
        self.la_logo.configure(image=self.logos[logo])
        self.la_name.configure(text=station)
        self.la_title.configure(text=title)

    def update_datetime(self):
        self.la_dtime.configure(text=time.asctime())
        self.tid_update_datetime = self.after(ms=1000, func=self.update_datetime) 


# --- Radio Frame Classes

class FrameRadioContent(ctki.CTkFrame):

    def __init__(self, parent, my_config, vlc_instance, media_player, logos, favorite_data, func_update_titel_info, func_reset_timestamp ):
        super().__init__(parent)

        self.my_config = my_config
        self.vlc_instance = vlc_instance
        self.media_player = media_player
        self.logos = logos
        self.favorite_data = favorite_data

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0,1,2,3), weight=1)
        #self.grid(row=0, column=0, padx=0, pady=0, sticky="ew")
        self.activate()

        # configure grid layout
        self.fr_info = FrameInfo(self)
        self.fr_volume = FrameVolume(self, self.my_config, self.media_player, self.fr_info)
        self.fr_stations = FrameStations(self, self.fr_info.update_media, func_update_titel_info, 
                                         self.my_config, self.favorite_data, self.logos, self.media_player, self.vlc_instance, func_reset_timestamp,
                                         self.fr_volume.change_is_playing)
        self.fr_favs = FrameFavs(self, self.my_config, self.fr_stations)
                
        self.fr_favs.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        self.fr_stations.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.fr_volume.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        self.fr_info.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

    def activate(self):
        self.grid(row=0, column=0, padx=0, pady=0, sticky="news")

class FrameInfo(ctki.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent)
        
        #self.grid(row=2, column=0, padx=10, pady=10, sticky="new")
        self.grid_columnconfigure(0, weight=1)

        # create station-title-meta-data label
        self.la_title = ctki.CTkLabel(master=self, text=_str_stopped, fg_color="transparent", font= ctki.CTkFont(size=20, weight="bold"))
        self.la_title.grid(row=0, column=0, sticky="w")

        # create date-time label
        self.la_datetime = ctki.CTkLabel(master=self, text="Datetime", fg_color="transparent", font= ctki.CTkFont(size=20, weight="bold"))
        self.la_datetime.grid(row=0, column=1)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.update_datetime()

    def update_media_stopped(self):
        self.update_media(self.station_name, _str_stopped)

    def update_media(self, station_name, title):
        self.station_name = station_name
        self.title = title
        self.la_title.configure(text=f"{station_name}: {title}")

    def update_datetime(self):
        self.la_datetime.configure(text=time.asctime())
        self.after(ms=1000, func=self.update_datetime) 



class FrameFavs(ctki.CTkFrame):

    def __init__(self, parent, my_config, fr_stations):
        super().__init__(parent)

        self.my_config = my_config
        self.fav_list = my_config.get("favorites")
        self.radio_var = ctki.IntVar(value=my_config.get("last_favlist"))
        self.fr_stations = fr_stations

        # create fav buttons
        for i in range(len(self.fav_list)):
            self.grid_columnconfigure(i, weight=1)
            btn = ctki.CTkRadioButton(master=self, text=self.fav_list[i]["name"], 
                font=ctki.CTkFont(size=20, weight="bold"),
                height=35, radiobutton_width=12, radiobutton_height=12, border_width_unchecked=2,
                value=i, variable=self.radio_var, command=self.select_fav)
            btn.grid(row=0, column=i, padx=3, pady=0, sticky="ew")
    
    def select_fav(self):
        print(f"Change to favorit list {self.radio_var.get()} with name={self.fav_list[self.radio_var.get()]['name']}")
        self.master.master.reset_timestamp()
        self.fr_stations.change_station_data(self.radio_var.get())
        
   

class FrameStations(ctki.CTkScrollableFrame):
                               
    def __init__(self, parent, func_update_meta_info, func_update_screensaver, my_config, favorite_data, logos, media_player, VlcInstance, func_reset_timestamp, func_change_is_playing):
        super().__init__(parent, orientation='horizontal')

        self.my_config = my_config
        self.favorite_data = favorite_data
        self.logos = logos
        self.media_player = media_player
        self.VlcInstance = VlcInstance
        self.func_reset_timestamp = func_reset_timestamp
        self.func_change_is_playing = func_change_is_playing
        self.func_update_meta_info = func_update_meta_info
        self.func_update_screensaver = func_update_screensaver

        self.now_playing_idx = self.my_config.get("last_station")
        self.active_fav_list_idx = self.my_config.get("last_favlist")

        self.Media = None

        self.btn_station_slot = []

        self.prev = ""

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid(row=0, column=0, sticky="news")

        self.setup_station_slots()
        self.select_station(self.now_playing_idx)
        self.update_meta()

    def change_station_data(self, new_favorites_list_idx):
        self.active_fav_list_idx = new_favorites_list_idx
        for btn_station_slot in self.btn_station_slot:
            btn_station_slot.destroy()

        self.setup_station_slots()

    def get_station_data(self):
        return self.favorite_data[self.active_fav_list_idx]

    def setup_station_slots(self):
        """create station slot buttons"""
        
        for i, station in enumerate(self.get_station_data()):
            logo_fn = station["logo"]
            logo_img = self.logos[logo_fn]
            btn_text = station["name"]
            
            btn_station_slot = ctki.CTkButton(master=self, compound="top", text=btn_text, image=logo_img, command=partial(self.btn_play_station, i))
            btn_station_slot.grid(row=0, column=i, padx=5, pady=7)

            if (logo_fn == _station_empty_logo_fn):
                btn_station_slot.configure(state = "disabled")

            self.btn_station_slot.append(btn_station_slot)


    def select_station(self, station_idx):
        print(f'selected station_idx={station_idx}, station={self.get_station_data()[station_idx]["name"]}')
        if (_station_empty != self.get_station_data()[station_idx]["name"]):
            self.media_player.stop()
            self.Media = self.VlcInstance.media_new(self.get_station_data()[station_idx]["url"])
            self.Media.get_mrl()
            self.media_player.set_media(self.Media)
            self.now_playing_idx = station_idx
            self.prev = ""
            self.my_config.change("last_station", self.now_playing_idx)
            self.my_config.change("last_favlist", self.active_fav_list_idx)

    def btn_play_station(self, i):
        self.func_reset_timestamp()
        self.select_station(i)
        self.media_player.play()
        self.func_change_is_playing(True)

    # https://stackoverflow.com/questions/70509728/how-to-get-audiostream-metadata-using-vlc-py
    def update_meta(self):
        '''Update GUI meta data (e.g. title-info) that comes with the stream'''

        if self.Media is not None:
            meta = self.Media.get_meta(12) # vlc.Meta 12: 'NowPlaying',
            if meta != self.prev:
                self.prev = meta
                station_name = self.get_station_data()[self.now_playing_idx]["name"]
                if meta is None:
                    print("if meta is None:")
                    meta = _str_no_info
                
                if not self.media_player.is_playing():
                    print("if not self.media_player.is_playing():")
                    meta = _str_stopped
                    
                print(f"Now playing {station_name}: {meta}")
                self.func_update_meta_info(station_name, meta)
                self.func_update_screensaver(station_name, meta, self.get_station_data()[self.now_playing_idx]["logo"])

        self.after(ms = 1000, func=self.update_meta)



class FrameVolume(ctki.CTkFrame):

    def __init__(self, parent, my_config, media_player, fr_info):
        super().__init__(parent)

        self.fr_info = fr_info
        self.media_player = media_player
        self.my_config = my_config
        self.is_muted = False
        self.is_playing = False

        self.grid(row=3, column=0, padx=0, pady=0, sticky="esw")
        self.grid_columnconfigure((0,1,2), weight=1)
        self.grid_rowconfigure(0, weight=1)

        # create mute button
        self.btn_mute = ctki.CTkButton(master=self, text=_str_mute, width=_station_btn_size, height=40, 
                                       command=self.btn_mute, state='disabled',
                                       font=ctki.CTkFont(size=18, weight="bold"))
        self.btn_mute.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        # create volume slider
        self.sl_volume = ctki.CTkSlider(master=self, from_=0, to=100, width=250, command=self.slider_event)
        self.sl_volume.configure(number_of_steps=25)
        self.sl_volume.set(self.my_config.get("last_volume"))
        self.sl_volume.grid(row=0, column=1, padx=0, pady=0, sticky="ew")
        
        self.media_player.audio_set_volume(self.my_config.get("last_volume"))

        # create stop button
        self.btn_play_stop = ctki.CTkButton(master=self, text=_str_play, width=_station_btn_size, height=40, 
                                       command=self.btn_play_stop,
                                       font=ctki.CTkFont(size=18, weight="bold"))
        self.btn_play_stop.grid(row=0, column=3, padx=5, pady=5, sticky="e")

    def change_is_playing(self, is_playing):
        self.is_playing = is_playing
        self.btn_mute.configure(state=state_by_bool(is_playing))
        #self.btn_play_stop.configure(state=state_by_bool(is_playing))
        if (is_playing):
            self.btn_play_stop.configure(text=_str_stop)
        else:
            self.btn_play_stop.configure(text=_str_play )

    def btn_mute(self):
        print(f"self.is_playing()={self.is_playing}, self.is_muted()={self.is_muted}")
        print(f"media_player.audio_get_volume()={self.media_player.audio_get_volume()}, media_player.is_playing()={self.media_player.is_playing()}")

        if (self.is_muted):
            self.media_player.audio_set_volume(self.my_config.get("last_volume"))
            self.sl_volume.set(self.my_config.get("last_volume"))
            self.btn_mute.configure(text=_str_mute)
        else:
            self.my_config.change("last_volume", self.media_player.audio_get_volume())
            self.media_player.audio_set_volume(0)
            self.sl_volume.set(0)
            self.btn_mute.configure(text=_str_unmute)

        self.is_muted = not self.is_muted
        self.master.master.reset_timestamp()

    def btn_play_stop(self):
        if self.media_player.is_playing():
            self.media_player.stop()
            self.change_is_playing(False)
            self.fr_info.update_media_stopped()
        else:
            self.media_player.play()
            self.change_is_playing(True)

        self.master.master.reset_timestamp()
        
    def slider_event(self, value):
        self.media_player.audio_set_volume(int(value))
        if ((int(value) > 0)):
            self.btn_mute.configure(text=_str_mute)
        self.master.master.reset_timestamp()
        self.my_config.change("last_volume", int(value))


# ---- App Class ------

class App(ctki.CTk):
    
    def __init__(self):
        super().__init__()

        # configure window
        self.title("RADIO & SHOWER")
        self.geometry(f"{_win_width}x{_win_height}")
        self.resizable(False, False)
        self.set_icon()

        print(f"self.winfo_width x self.winfo_height() = {self.winfo_width()}x{self.winfo_height()}")
        print(f"self._current_width x self._current_height = {self._current_width}x{self._current_height}")

        if not _kiosk_mode:
        # fixed window size 
            self.minsize(_win_width, _win_height)
            self.maxsize(_win_width, _win_height)

        self.vlc_instance = vlc.Instance()
        self.media_player = self.vlc_instance.media_player_new()

        self.favorite_data = []
        self.image_path_list = []
        self.logos = {}

        self.my_config = MyConfig(_check_config_is_dirty_s)

        self.load_station_logos()
        self.load_favorites()

        self.index = 0
        self.content_frames = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.content_frames.append(FrameScreensaverPlayingContent(self, self.show_radio_content, self.logos, self.media_player))
        self.content_frames.append(DiaShowCanvas(self, _win_width,_win_height, self.show_radio_content))
        #self.content_frames.append(FrameScreensaverDigiClockContent(self, self.show_radio_content))
        self.content_frames.append(FrameRadioContent(self, self.my_config, self.vlc_instance, self.media_player, self.logos, self.favorite_data, self.content_frames[0].update_titel_info, self.reset_timestamp))
        self.content_frames[2].grid()

        #start screensaver check
        self.reset_timestamp()
        self.check_for_screensaver()

    def set_icon(self):
        self.iconpath = tk.PhotoImage(file=os.path.join("", _icon_path))
        self.wm_iconbitmap()
        self.iconphoto(False, self.iconpath)

    def show_radio_content(self):
        self.content_frames[0].grid_forget()
        self.content_frames[1].grid_forget()
        self.content_frames[2].activate()
        self.reset_timestamp()
        self.tid_check_for_screensaver = self.after(_check_for_screensaver_ms, self.check_for_screensaver)

    def show_screensaver(self):
        print("Start Screensaver")
        self.content_frames[2].grid_forget()
        self.after_cancel(self.tid_check_for_screensaver)

        if self.media_player.is_playing():
            self.content_frames[0].activate()
        else:
            self.content_frames[1].activate()

    def reset_timestamp(self):
        self.current_timestamp = time.time()

    def check_for_screensaver(self):
        elapsed_time = time.time() - self.current_timestamp
        #print(f"Elapsed time (s) since last button pressed: {elapsed_time}")

        print(f"self.winfo_width x self.winfo_height() = {self.winfo_width()}x{self.winfo_height()}")
        print(f"self._current_width x self._current_height = {self._current_width}x{self._current_height}")


        if (elapsed_time > self.my_config.get("screensaver_after_s")):
            self.show_screensaver()
        else:
            self.tid_check_for_screensaver = self.after(_check_for_screensaver_ms, self.check_for_screensaver)

    def load_station_logos(self):
        '''load station logos'''

        default_logo = Image.open(_station_default_logo_path)
        self.logos[_dummy_logo_fn] = ctki.CTkImage(default_logo, size=(_logo_size, _logo_size))

        for filename in glob.glob(_stations_logos_glob, recursive=False):
            try:
                img = Image.open(filename)
            except OSError as e:
                print(f"Unable to open {filename}. Using {_station_default_logo_path} instead. Details : {e}", file=sys.stderr)
                img = default_logo
            
            self.logos[os.path.basename(filename)] = ctki.CTkImage(img, size=(_logo_size, _logo_size))
            print(f"added new logo '{os.path.basename(filename)}'")

        print(f"Loaded {len(self.logos)} logos")

    def load_favorites(self):
        '''load favorit files'''
        for fav_fn in self.my_config.get("favorites"):
            fav_path = os.path.join(_favorites_path, fav_fn["file"])
            print(f'Try to load favorite file {fav_path}')

            with open(fav_path) as json_file:
                station_data = json.load(json_file)

                self.favorite_data.append(station_data)
           
# --- functions ---

def on_escape(event=None):
    print("escaped")
    app.destroy()

# ---- Start -----
    
print(f"sys.argv={sys.argv}, len(sys.argv)={len(sys.argv)}")
_kiosk_mode = False

if (len(sys.argv) > 1):
    if (sys.argv[1]=='kiosk'):
        _kiosk_mode = True

if os.environ.get('DISPLAY','') == '':
    print('no display found. Using :0.0')
    os.environ.__setitem__('DISPLAY', ':0.0')

print(f"Running Env {platform.system()}")

print("_kiosk_mode=",_kiosk_mode)

if __name__ == "__main__":
    app = App()

    #photo = tk.PhotoImage(file = 'radio_icon.png')
    #app.wm_iconphoto(False, photo)


    # https://stackoverflow.com/questions/47856817/tkinter-canvas-based-kiosk-like-program-for-raspberry-pi
    # --- fullscreen ---

    #root.overrideredirect(True)  # sometimes it is needed to toggle fullscreen
                                # but then window doesn't get events from system
    #root.overrideredirect(False) # so you have to set it back

    if _kiosk_mode:
        print("Configure kiosk mode:")
        screen_width = app.winfo_screenwidth()
        screen_height = app.winfo_screenheight()
        app.attributes("-fullscreen", True) # run fullscreen
        app.wm_attributes("-topmost", True) # keep on top
    
        print(f"screen_width x screen_height = {screen_width}x{screen_height}")

    #root.focus_set() # set focus on window
    # --- closing methods ---

    # close window with key `ESC`
    app.bind("<Escape>", on_escape)

    # close window after 5s if `ESC` will not work
    #app.after(5000, app.destroy) 
    
    app.mainloop()
