import customtkinter as ctki
import tkinter as tk 
from PIL import Image
from functools import partial
import vlc
import json
import time
import glob
import platform
import sys
import os
import random


if os.environ.get('DISPLAY','') == '':
    print('no display found. Using :0.0')
    os.environ.__setitem__('DISPLAY', ':0.0')


ctki.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
ctki.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"

_win_width  = 1280
_win_height = 400

_icon_path          = "radio_icon.png"
_config_json_path   = "config.json"
_favorites_path     = "favorites"
_stations_logos_path = "logos"
_stations_logos_glob = os.path.join(_stations_logos_path, "*.??g")
_dummy_logo_fn         = "dummy.jpg"
_station_default_logo_path = os.path.join(_stations_logos_path, _dummy_logo_fn)
_station_empty_logo_fn = "empty.png"

_station_empty = "empty"

_station_slots      = 5
_screensaver_jump_ms = 15000

_station_btn_size = 200
_logo_size        = _station_btn_size - 30
_scroll_btn_width = 70

_check_for_screensaver_ms = 5000


class CTaFont(ctki.CTkFont):

    def __init__(self):
        super().__init__(size=20, weight="normal")

class FrameScreensaverDigiClockContent(ctki.CTkFrame):
    def __init__(self, parent, return_to_radio_func):
        super().__init__(parent)
        self.return_to_radio_func = return_to_radio_func
        self.la_clock = ctki.CTkLabel(master=self, text="HH:MM:SS", font=ctki.CTkFont(size=300, weight="normal"))
        self.la_clock.grid(row=0, column=0, sticky="news")
        self.grid_columnconfigure((0), weight=1)
        self.grid_rowconfigure((0), weight=1)
        self.la_clock.bind(sequence="<Button-1>", command=self.stop, add='+')

    def stop(self, event):
        print("Stop Screensaver")
        self.after_cancel(self.tid_update_time)
        self.return_to_radio_func()

    def update_time(self):
        current_time = time.strftime('%H:%M:%S')
        self.la_clock.configure(text=current_time)
        self.tid_update_time = self.after(1000, self.update_time)

    def grid(self):
        super().grid()
        self.update_time()

    def grid_forget(self):
        super().grid_forget()
    
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
        self.grid_rowconfigure((0,1,2,3), weight=1)
       
        self.current_col = 4

        for i in range(0,6):
            la_col = ctki.CTkLabel(master=self, text="", height=1, width=100, font=ctki.CTkFont(size=18, weight="normal"))
            la_col.grid(row=0, column=i, padx=50, pady=10, sticky="")

        # create date-time label
        self.la_dtime = ctki.CTkLabel(master=self, text="Datetime", height=30, width=50, font=ctki.CTkFont(size=18, weight="normal"))
        self.la_dtime.grid(row=0, column=self.current_col, padx=5, pady=20, sticky="ns")
        self.la_dtime.bind(sequence="<Button-1>", command=self.stop, add='+')
        
        self.la_logo = ctki.CTkLabel(master=self, text="", image=self.logos[_dummy_logo_fn])
        self.la_logo.grid(row=1, column=self.current_col, padx=5, pady=20, sticky="ns")
        self.la_logo.bind(sequence="<Button-1>", command=self.stop, add='+')

        self.la_name = ctki.CTkLabel(master=self, text="Station", font=ctki.CTkFont(size=18, weight="normal") )
        self.la_name.grid(row=2, column=self.current_col, padx=5, pady=20, sticky="ns")
        self.la_name.bind(sequence="<Button-1>", command=self.stop, add='+')

        self.la_title = ctki.CTkLabel(master=self, text="Title-Info", height=30, width=50, font=ctki.CTkFont(size=22, weight="bold"))
        self.la_title.grid(row=3, column=self.current_col, padx=5, pady=20, sticky="ns")
        self.la_title.bind(sequence="<Button-1>", command=self.stop, add='+')

    def stop(self, event):
        print("Stop Screensaver")
        self.after_cancel(self.tid_move_content)
        self.after_cancel(self.tid_update_datetime)
        self.return_to_radio_func()
        
    def grid(self):
        super().grid()
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
            title = "Stopped"
        
        self.la_logo.configure(image=self.logos[logo])
        self.la_name.configure(text=station)
        self.la_title.configure(text=title)

    def update_datetime(self):
        self.la_dtime.configure(text=time.asctime())
        self.tid_update_datetime = self.after(ms=1000, func=self.update_datetime) 


class FrameRadioContent(ctki.CTkFrame):

    def __init__(self, parent, config, vlc_instance, media_player, logos, favorite_data, func_update_titel_info ):
        super().__init__(parent)

        self.my_config = config
        self.vlc_instance = vlc_instance
        self.media_player = media_player
        self.logos = logos
        self.favorite_data = favorite_data

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0,1,2,3), weight=1)      

        # configure grid layout
        self.fr_info = FrameInfo(self)
        self.fr_stations = FrameStations(self, self.fr_info.update_media, func_update_titel_info, self.my_config, self.favorite_data, self.logos, self.media_player, self.vlc_instance)
        self.fr_favs = FrameFavs(self, self.my_config, self.fr_stations)
        self.fr_volume = FrameVolume(self, self.my_config, self.media_player, self.fr_info)
        
        self.fr_favs.grid(row=0, column=0, padx=10, pady=10, sticky="new")
        self.fr_stations.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.fr_info.grid(row=2, column=0, padx=10, pady=10, sticky="new")
        self.fr_volume.grid(row=3, column=0, padx=10, pady=10, sticky="esw")



class FrameInfo(ctki.CTkFrame):

    def __init__(self, master):
        super().__init__(master)
        
        #self.grid(row=2, column=0, padx=10, pady=10, sticky="new")
        self.grid_columnconfigure(0, weight=1)

        # create title-data label
        self.la_title = ctki.CTkLabel(master=self, text="Stopped", fg_color="transparent", font=CTaFont())
        self.la_title.grid(row=0, column=0, sticky="w")

        # create date-time label
        self.la_datetime = ctki.CTkLabel(master=self, text="Datetime", fg_color="transparent", font=CTaFont())
        self.la_datetime.grid(row=0, column=1)

        self.update_datetime()

    def update_media(self, station_name, title):
        self.la_title.configure(text=f"{station_name}: {title}")

    def update_datetime(self):
        self.la_datetime.configure(text=time.asctime())
        self.after(ms=1000, func=self.update_datetime) 



class FrameFavs(ctki.CTkFrame):

    def __init__(self, master, config, fr_stations):
        super().__init__(master)

        self.my_config = config
        self.fav_list = config["favorites"]
        self.radio_var = ctki.IntVar(value=config["last_favlist"])
        self.fr_stations = fr_stations

        #self.grid(row=0, column=0, padx=10, pady=10, sticky="new")

        # create fav buttons
        for i in range(len(self.fav_list)):
            self.grid_columnconfigure(i, weight=1)
            ctki.CTkRadioButton(master=self, text=self.fav_list[i]["name"], 
                font=ctki.CTkFont(size=20, weight="bold"),
                width=40, height=40, radiobutton_width=12, radiobutton_height=12, border_width_unchecked=2,
                value=i, variable=self.radio_var, command=self.select_fav).grid(row=0, column=i, padx=3, sticky="ew")
    
    def select_fav(self):
        print(f"Change to favorit list {self.radio_var.get()} with name={self.fav_list[self.radio_var.get()]['name']}")
        self.master.master.reset_timestamp()
        self.fr_stations.change_station_data(self.radio_var.get())
   


class FrameStations(ctki.CTkFrame):
                               
    def __init__(self, master, func_update_meta_info, func_update_screensaver, config, favorite_data, logos, media_player, VlcInstance):
        super().__init__(master)

        self.config = config
        self.favorite_data = favorite_data
        self.logos = logos
        self.media_player = media_player
        self.VlcInstance = VlcInstance

        self.func_update_meta_info = func_update_meta_info
        self.func_update_screensaver = func_update_screensaver

        self.now_playing_idx = config["last_station"]
        self.active_fav_list_idx = config["last_favlist"]

        self.Media = None
        self.slot_first_sta = 0
        self.btn_station_slot = []
        self.scrollbtn_inactive = (len(self.get_station_data()) <= _station_slots)

        self.prev = ""

        #self.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        # create scroll-left button
        self.btn_scroll_r = ctki.CTkButton(master=self, text="<<", width=_scroll_btn_width, height=_station_btn_size, state = self.scrollbtn_inactive, command=partial(self.btn_stations_scroll, -1))
        self.btn_scroll_r.grid(row=0, column=0, padx=3, sticky="e")

        # create scroll-right button
        self.btn_scroll_l = ctki.CTkButton(master=self, text=">>", width=_scroll_btn_width, height=_station_btn_size, state = self.scrollbtn_inactive, command=partial(self.btn_stations_scroll, 1))
        self.btn_scroll_l.grid(row=0, column=6, padx=3, pady=0, sticky="w")

        self.setup_station_slots(0)
        self.select_station(self.active_fav_list_idx)
        self.update_meta()

    def change_station_data(self, i):
        self.active_fav_list_idx = i
        self.setup_station_slots(0)

    def get_station_data(self):
        return self.favorite_data[self.active_fav_list_idx]

    def setup_station_slots(self, start_idx):
        # create station slot buttons
        slot_idx = 0
        for i in range(start_idx, start_idx + _station_slots):
                logo_fn = self.get_station_data()[i]["logo"]
                #if (logo_fn == _dummy_logo_fn):
                btn_text = self.get_station_data()[i]["name"]
           
                logo_img = self.logos[logo_fn]
                btn_station_slot = ctki.CTkButton(master=self, compound="top", text=btn_text, image=logo_img, command=partial(self.btn_play_station, i))
                btn_station_slot.grid(row=0, column=slot_idx+1, padx=3, pady=0)

                if (logo_fn == _station_empty_logo_fn):
                    btn_station_slot.configure(state = "disabled")
                
                slot_idx += 1

        if (len(self.get_station_data()) <= _station_slots):
            self.btn_scroll_l.configure(state="disabled")
            self.btn_scroll_r.configure(state="disabled")
        else:
            self.btn_scroll_l.configure(state="normal")
            self.btn_scroll_r.configure(state="normal")

    def select_station(self, i):
        print(f'selected i={i}, station={self.get_station_data()[i]["name"]}')
        if (_station_empty != self.get_station_data()[i]["name"]):
            self.media_player.stop()
            self.Media = self.VlcInstance.media_new(self.get_station_data()[i]["url"])
            self.Media.get_mrl()
            self.media_player.set_media(self.Media)
            self.now_playing_idx = i
            self.prev = ""

    def btn_play_station(self, i):
        self.master.master.reset_timestamp()
        self.select_station(i)
        self.media_player.play()

    def btn_stations_scroll(self, inc):
        '''value of inc can be on of {-1, +1} depending on which button was pressed'''
        self.master.master.reset_timestamp()
        t = self.slot_first_sta + inc 
        if (t >= 0) and (t <= len(self.get_station_data()) - _station_slots):
            self.slot_first_sta = t
            self.setup_station_slots(self.slot_first_sta)

        #todo: change of state does not work, is always active/normal
        #self.btn_scroll_l.configure(state=(t==0))
        #self.btn_scroll_l.configure(state=(t!=0))
        #self.btn_scroll_r.configure(state=(t == len(self.get_station_data()) - _station_slots))
        #self.btn_scroll_r.configure(state=(t != len(self.get_station_data()) - _station_slots))

    # https://stackoverflow.com/questions/70509728/how-to-get-audiostream-metadata-using-vlc-py
    def update_meta(self):
        '''Update GUI meta data (e.g. title-info) that comes with the stream'''

        # print (f"Is player playing? {self.media_player.is_playing()}")

        if self.Media is not None:
            meta = self.Media.get_meta(12) # vlc.Meta 12: 'NowPlaying',
            if meta != self.prev:
                self.prev = meta
                station_name = self.get_station_data()[self.now_playing_idx]["name"]
                if meta is None:
                    meta = "no info"
                print(f"Now playing {station_name}: {meta}")
                self.func_update_meta_info(station_name, meta)
                self.func_update_screensaver(station_name, meta, self.get_station_data()[self.now_playing_idx]["logo"])

        self.after(ms = 1000, func=self.update_meta)



class FrameVolume(ctki.CTkFrame):

    def __init__(self, master, config, media_player, fr_head):
        super().__init__(master)

        self.fr_head = fr_head
        self.media_player = media_player
        self.my_config = config

        #self.grid(row=3, column=0, padx=10, pady=10, sticky="esw")
        self.grid_columnconfigure((0,1,2), weight=1)

        # create mute button
        self.btn_mute = ctki.CTkButton(master=self, text="mute", width=_station_btn_size, height=50, command=self.btn_mute,
                                       font=ctki.CTkFont(size=18, weight="bold"))
        self.btn_mute.grid(row=0, column=0, padx=0, pady=0, sticky="w")

        # create volume slider
        self.sl_volume = ctki.CTkSlider(master=self, from_=0, to=100, width=250, command=self.slider_event)
        self.sl_volume.configure(number_of_steps=25)
        self.sl_volume.set(self.my_config["last_volume"])
        self.sl_volume.grid(row=0, column=1, padx=0, pady=0, sticky="ew")
        
        self.media_player.audio_set_volume(self.my_config["last_volume"])

        # create stop button
        self.btn_stop = ctki.CTkButton(master=self, text="stop", width=_station_btn_size, height=50, command=self.btn_stop,
                                       font=ctki.CTkFont(size=18, weight="bold"))
        self.btn_stop.grid(row=0, column=3, padx=0, pady=0, sticky="e")

    def btn_mute(self):
        self.media_player.audio_set_volume(0)
        self.sl_volume.set(0)
        self.master.master.reset_timestamp()

    def btn_stop(self):
        self.media_player.stop()
        self.fr_head.update_media("", "Stopped")
        self.master.master.reset_timestamp()
        
    def slider_event(self, value):
        self.media_player.audio_set_volume(int(value))
        self.master.master.reset_timestamp()



class App(ctki.CTk):
    
    def __init__(self, kiosk_mode):
        super().__init__()

        # configure window
        self.title("RADIO & SHOWER")
        self.geometry(f"{_win_width}x{_win_height}")
        #self.configure(fg_color="#080808")
        self.set_icon()

        if not kiosk_mode:
        # fixed window size 
            self.minsize(_win_width, _win_height)
            self.maxsize(_win_width, _win_height)

        self.vlc_instance = vlc.Instance()
        self.media_player = self.vlc_instance.media_player_new()

        self.favorite_data = []
        self.logos = {}

        self.load_config()
        self.load_station_logos()
        self.load_favorites()

        self.index = 0
        self.content_frames = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.content_frames.append(FrameScreensaverPlayingContent(self, self.show_radio_content, self.logos, self.media_player))
        self.content_frames.append(FrameScreensaverDigiClockContent(self, self.show_radio_content))
        self.content_frames.append(FrameRadioContent(self, self.my_config, self.vlc_instance, self.media_player, self.logos, self.favorite_data, self.content_frames[0].update_titel_info))
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
        self.content_frames[2].grid()
        self.reset_timestamp()
        self.tid_check_for_screensaver = self.after(_check_for_screensaver_ms, self.check_for_screensaver)

    def show_screensaver(self):
        print("Start Screensaver!")
        self.content_frames[2].grid_forget()
        self.after_cancel(self.tid_check_for_screensaver)

        if self.media_player.is_playing():
            self.content_frames[0].grid()
        else:
            self.content_frames[1].grid()

    def reset_timestamp(self):
        self.current_timestamp = time.time()

    def check_for_screensaver(self):
        elapsed_time = time.time() - self.current_timestamp
        print(f"Elapsed time (s) since last button pressed: {elapsed_time}")
        if (elapsed_time > self.my_config["screensaver_after_s"]):
            self.show_screensaver()
        else:
            self.tid_check_for_screensaver = self.after(_check_for_screensaver_ms, self.check_for_screensaver)



    def load_config(self):
        '''read config from JSON file'''
        with open(_config_json_path) as json_file:
            self.my_config = json.load(json_file)
        
        # Print the type of data variable
        print(f"Loaded config {self.my_config} from {_config_json_path}")
        

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
            print(f"added new logo 'f{os.path.basename(filename)}'")

        print(f"All logos loaded {self.logos}")

    def load_favorites(self):
        '''load favorit files'''
        for fav_fn in self.my_config["favorites"]:
            fav_path = os.path.join(_favorites_path, fav_fn["file"])
            print(f'Try to load favorite file {fav_path}')

            with open(fav_path) as json_file:
                station_data = json.load(json_file)

                # fill station_data with dummy data (empty logos) when less than _station_slots loaded from json
                if (len(station_data) <= _station_slots):
                    print(f"Found only {_station_slots - len(station_data)} stations fill up to match {_station_slots} ")
                    for _ in range(_station_slots - len(station_data) ):
                        station_data.append(dict(name=_station_empty, url="", logo=_station_empty_logo_fn))

                self.favorite_data.append(station_data)

            
# --- functions ---

def on_escape(event=None):
    print("escaped")
    app.destroy()


print(f"Running Env {platform.system()}")
_kiosk_mode= (platform.system() == "Linux")
print("_kiosk_mode=",_kiosk_mode)

if __name__ == "__main__":
    app = App(_kiosk_mode)

    #photo = tk.PhotoImage(file = 'radio_icon.png')
    #app.wm_iconphoto(False, photo)


    # https://stackoverflow.com/questions/47856817/tkinter-canvas-based-kiosk-like-program-for-raspberry-pi
    # --- fullscreen ---

    #root.overrideredirect(True)  # sometimes it is needed to toggle fullscreen
                                # but then window doesn't get events from system
    #root.overrideredirect(False) # so you have to set it back

    if _kiosk_mode:
        screen_width = app.winfo_screenwidth()
        screen_height = app.winfo_screenheight()
        app.attributes("-fullscreen", True) # run fullscreen
        app.wm_attributes("-topmost", True) # keep on top
    
    #root.focus_set() # set focus on window
    # --- closing methods ---

    # close window with key `ESC`
    app.bind("<Escape>", on_escape)

    # close window after 5s if `ESC` will not work
    #app.after(5000, app.destroy) 
    
    app.mainloop()
