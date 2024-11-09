import os

import customtkinter as ctk
from PIL import Image
from screeninfo import get_monitors
import platform
import sys
import time

_screen_size = (1280, 400)

_image_path = "gallery/private/"
_images = ["20220809_144810.jpg", "20230818_121739.jpg"]
_img_timeout_ms = 5000

class ImageFrame(ctk.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.img_no = 0
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.ctk_image = ctk.CTkImage(light_image=self.load_image(_images[self.img_no]), size=_screen_size)
        self.label = ctk.CTkLabel(self, image=self.ctk_image, text="")
        self.label.grid(row=0, column=0, sticky="news")

        self.next_image()

    def load_image(self, image_name ):
        return Image.open(os.path.join(_image_path, image_name))

    def set_image(self, image_name):
        self.ctk_image = ctk.CTkImage(light_image=self.load_image(image_name), size=_screen_size)
        self.label.configure(image=self.ctk_image)

    def next_image(self):
        self.set_image(_images[self.img_no])

        self.img_no += 1
        if self.img_no >= len(_images):
            self.img_no = 0

        self.after(_img_timeout_ms, self.next_image)

class RadioFrame(ctk.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.configure(fg_color="lightblue")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.label = ctk.CTkLabel(self, text="RADIO APP")
        self.label.grid(row=0, column=0, sticky="news")

class App(ctk.CTk):
    def __init__(self, kiosk_mode):
        super().__init__()

        self.kiosk_mode = kiosk_mode
        self.attributes("-fullscreen", kiosk_mode) # run fullscreen
        self.wm_attributes("-topmost", kiosk_mode) # keep on top

        self.last_activity_time = time.time()
        self.inactivity_period_s = 5  # in seconds
        self.title("Screensaver")
        self.geometry(f"{_screen_size[0]}x{_screen_size[1]}" )

        print(f"App Window Size start ({self.winfo_width()}, {self.winfo_height()})")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.image_frame = ImageFrame(self, width=_screen_size[0], height=_screen_size[1])
        self.image_frame.grid(row=0, column=0, padx=0, pady=0, sticky="news")
        self.image_frame.grid_remove()

        self.update_size()

        self.radio_frame = RadioFrame(self, width=_screen_size[0], height=_screen_size[1])
        self.radio_frame.grid(row=0, column=0, padx=0, pady=0, sticky="news")


        self.bind("<Escape>", self.on_escape)
        self.bind("<Configure>", self.update_size)

        self.bind_all("<Key>", self.reset_timer)
        self.bind_all("<Motion>", self.reset_timer)

        self.check_inactivity()

    def reset_timer(self, event=None):
        self.last_activity_time = time.time()
        self.image_frame.grid_remove()
        self.radio_frame.grid(row=0, column=0, padx=0, pady=0, sticky="news")

    def check_inactivity(self):
        current_time = time.time()
        if current_time - self.last_activity_time > self.inactivity_period_s:
            self.on_inactivity()
        self.after(1000, self.check_inactivity)

    def on_inactivity(self):
        print(f"No activity within the last period of {self.inactivity_period_s} seconds, switching to screensaver mode")
        self.radio_frame.grid_remove()
        self.image_frame.grid(row=0, column=0, padx=0, pady=0, sticky="news")

    def update_size(self, event=None):
        width = self.winfo_width()
        height = self.winfo_height()
        print(f"Windowsize: {width}x{height}")

    def on_escape(self, event=None):
        app.destroy()

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
    try:
        monitor = get_monitors()

        print(f"Monitor List: {monitor}")

        app = App(_kiosk_mode)

        screen_width = app.winfo_screenwidth()
        screen_height = app.winfo_screenheight()
        print(f"app.winfo_screenwidth() x  app.winfo_screenheight() = {screen_width}x{screen_height}")

        app.mainloop()

    except Exception as e:
        print(f"An error occurred: {e}")
        input("Press Enter to exit...")