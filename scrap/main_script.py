import customtkinter
from PIL import Image, ImageTk
import vlc
import json
import time
import sys
from functools import partial
 
_isMacOS   = sys.platform.startswith('darwin')
_isWindows = sys.platform.startswith('win')
_isLinux   = sys.platform.startswith('linux')

Instance = vlc.Instance()
media_player = Instance.media_player_new()
#media_player = vlc.MediaPlayer()
Media = Instance.media_new("http://icecast.radiobremen.de/rb/bremeneins/live/mp3/128/stream.mp3")

app = customtkinter.CTk()  # create CTk window like you do with the Tk window
button_image = []
prev = ""


# Opening JSON file
with open('stations.json') as json_file:
    station_data = json.load(json_file)
 
    # Print the type of data variable
    print("Type:", type(station_data))
 
for i in range(len(station_data)):
    print(station_data[i])

customtkinter.set_appearance_mode("dark")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green


for i in range(len(station_data)):
    button_image.append(
        customtkinter.CTkImage(Image.open("logos/"+station_data[i]["logo"]), size=(200, 200)))
 
# https://stackoverflow.com/questions/70509728/how-to-get-audiostream-metadata-using-vlc-py
def change_text():
    global prev
    global Media
    global media_player
    label.configure(text=time.asctime())
    print(time.asctime())
    m = Media.get_meta(12) # vlc.Meta 12: 'NowPlaying',
    if m != prev:
        print("Now playing ", m)
        prev = m
        print("data ", media_player.audio_get_track_description())
    
    app.after(ms = 1000, func=change_text)


def btn_play_station(func):
    global prev
    global Instance
    global media_player
    print(func)
    i = func
    print("selected " + station_data[i]["name"])
    media_player.stop()

    Media = Instance.media_new(station_data[i]["url"])
    Media.get_mrl()
    media_player.set_media(Media)
    media_player.play()
    prev = ""

for i in range(len(station_data)):
    button = customtkinter.CTkButton(master=app, text="", image=button_image[i], command=partial(btn_play_station, i))
    button.grid(row=0, column=i, padx=10, pady=10)
    # button.place(relx=0.5, rely=0.5, anchor=customtkinter.CENTER)

def slider_event(value):
    media_player.audio_set_volume(int(value)) 

slider = customtkinter.CTkSlider(master=app, from_=0, to=100, command=slider_event)
slider.configure(number_of_steps=25)
slider.grid(row=1, column=0, padx=20, pady=20, sticky="ew", columnspan=5)

label = customtkinter.CTkLabel(app, text="CTkLabel", fg_color="transparent")
label.grid(row=2, column=0, padx=20, pady=20, sticky="ew", columnspan=5)


app.geometry("1280x400")
app.title("RADIO & SHOWER")
#app.grid_columnconfigure((0, 1), weight=1)
change_text()

app.mainloop()