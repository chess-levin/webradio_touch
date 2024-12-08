import os
import random

import customtkinter as ctk
from PIL import Image, ImageTk
from screeninfo import get_monitors
import platform
import sys
import time

_kiosk_screen_size = (1280, 400)
_check_inactivity_ms = 1000

_image_path = "gallery/private/"
# aspect ratio 1280 x 400
_images = ["20220809_144810.jpg", "20230818_121739.jpg", "20230910_165329-01.jpg"]
_img_timeout_ms = 5000

class ImageCanvasFrame(ctk.CTkCanvas):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.original_image = None
        self.font = ctk.CTkFont(size=45, weight="bold")
        self.datetime_format_str = '%A, %d. %B %H:%M:%S'
        self.img_no = 0
        self.photo_image = None
        self.datetime_text = None
        self.dia_image = None
        self.tid_tick = None
        self.tid_dia_show = None
        self.text_positions = ['sw', 'se', 'nw', 'ne', 'center']
        self.current_text_pos = 'sw'
        self.bind("<Configure>", self.resize_canvas)

    def grid(self, *args, **kwargs):
        super().grid(*args, **kwargs)
        self.start()

    def grid_remove(self):
        self.stop()
        super().grid_remove()

    def start(self):
        if not self.tid_dia_show:
            self.next_image()
            print("Started next_image of ImageCanvasFrame")
        if not self.tid_tick:
            self.next_tick()
            print("Started next_tick of ImageCanvasFrame")

    def stop(self):
        self.after_cancel(self.tid_tick)
        self.after_cancel(self.tid_dia_show)
        print("Stopped timers of ImageCanvasFrame")

    def resize_canvas(self, event=None):
        wininfo_width = self.winfo_width()
        wininfo_height = self.winfo_height()
        print(f"resize_canvas(): wininfo_width x wininfo_height {wininfo_width}x{wininfo_height}")
        resized_image = self.original_image.resize((wininfo_width, wininfo_height), Image.Resampling.LANCZOS)
        self.photo_image = ImageTk.PhotoImage(resized_image)
        self.dia_image = self.create_image(0, 0, anchor="nw", image=self.photo_image)
        self.datetime_text = None
        self.show_datetime()

    def load_image(self, image_name):
        self.original_image = Image.open(os.path.join(_image_path, _images[self.img_no]))
        self.resize_canvas()

    def next_image(self):
        self.datetime_text = None
        self.load_image(_images[self.img_no])
        self.current_text_pos = self.text_positions[random.randint(0, len(self.text_positions)-1)]

        self.img_no += 1
        if self.img_no >= len(_images):
            self.img_no = 0

        self.tid_dia_show = self.after(_img_timeout_ms, self.next_image)

    def show_datetime(self):
        time_string = time.strftime(self.datetime_format_str)

        if self.datetime_text:
            self.itemconfig(self.datetime_text, text=time_string)
        else:
            wininfo_width = self.winfo_width()
            wininfo_height = self.winfo_height()
            print(f"show_datetime(): wininfo_width x wininfo_height {wininfo_width}x{wininfo_height}")

            if self.current_text_pos == 'se':
                ref_point = (wininfo_width - 10, wininfo_height)
            elif self.current_text_pos == 'sw':
                ref_point = (10, wininfo_height)
            elif self.current_text_pos == 'nw':
                ref_point = (10, 10)
            elif self.current_text_pos == 'ne':
                ref_point = (wininfo_width - 10, 10)
            else:
                ref_point = (wininfo_width / 2, wininfo_height / 2)

            self.datetime_text = self.create_text(ref_point , text=time_string, font=self.font,  fill="white", anchor=self.current_text_pos)

    def next_tick(self):
        self.show_datetime()
        self.tid_tick = self.after(1000, self.next_tick)


class ImageLabelFrame(ctk.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.img_no = 0

        self.ctk_image = ctk.CTkImage(light_image=self.load_image(_images[self.img_no]), size=_kiosk_screen_size)
        self.label = ctk.CTkLabel(self, image=self.ctk_image, text="", font=ctk.CTkFont(size=100, weight="normal"),
                                  anchor="sw")
        self.label.grid(row=0, column=0, sticky="news")

        self.time_label = ctk.CTkLabel(self, text="HH:MM:SS", fg_color="transparent", font=ctk.CTkFont(size=75, weight="normal"))
        self.time_label.place(relx=0.5, rely=1.0, anchor="s")  # Adjust relx and rely for positioning

        #self.text_label.place(relx=0.0, rely=0.0, anchor="nw") for top left.
        #self.text_label.place(relx=1.0, rely=0.0, anchor="ne") for top right.
        #self.text_label.place(relx=0.0, rely=1.0, anchor="sw") for bottom left.
        #self.text_label.place(relx=1.0, rely=1.0, anchor="se") for bottom right.

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def load_image(self, image_name ):
        return Image.open(os.path.join(_image_path, image_name))

    def set_image(self, image_name):
        self.ctk_image = ctk.CTkImage(light_image=self.load_image(image_name), size=_kiosk_screen_size)
        self.label.configure(image=self.ctk_image)

    def next_image(self):
        self.set_image(_images[self.img_no])

        self.img_no += 1
        if self.img_no >= len(_images):
            self.img_no = 0

        self.after(_img_timeout_ms, self.next_image)

    def next_tick(self):
        time_string = time.strftime('%H:%M:%S')
        #self.label.configure(anchor="ne")
        self.time_label.configure(text=time_string)
        self.after(1000, self.next_tick)

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
        self.is_screensaver_on = False
        self.attributes("-fullscreen", kiosk_mode) # run fullscreen
        self.wm_attributes("-topmost", kiosk_mode) # keep on top

        self.last_activity_time = time.time()
        self.inactivity_period_s = 5  # in seconds
        self.title("Screensaver")
        self.geometry(f"{_kiosk_screen_size[0]}x{_kiosk_screen_size[1]}")

        print(f"App Window Size start ({self.winfo_width()}, {self.winfo_height()})")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.image_frame = ImageCanvasFrame(self, width=_kiosk_screen_size[0], height=_kiosk_screen_size[1])

        self.update_size()

        self.radio_frame = RadioFrame(self, width=_kiosk_screen_size[0], height=_kiosk_screen_size[1])
        self.radio_frame.grid(row=0, column=0, padx=0, pady=0, sticky="news")

        self.bind("<Escape>", self.on_escape)
        self.bind("<Configure>", self.update_size)

        self.bind_all("<Key>", self.reset_timer)
        self.bind_all("<Motion>", self.reset_timer)

        self.check_inactivity()

    def reset_timer(self, event=None):
        self.last_activity_time = time.time()
        if self.is_screensaver_on:
            #self.image_frame.stop()
            self.image_frame.grid_remove()
            self.is_screensaver_on = False
            print("Image screensaver stopped")
            self.radio_frame.grid(row=0, column=0, padx=0, pady=0, sticky="news")
        else:
            None

    def check_inactivity(self):
        current_time = time.time()
        if current_time - self.last_activity_time > self.inactivity_period_s:
            self.on_inactivity()
        self.after(_check_inactivity_ms, self.check_inactivity)

    def on_inactivity(self):
        if not self.is_screensaver_on:
            print(f"No activity within the last period of {self.inactivity_period_s} seconds, switching to screensaver mode")
            self.is_screensaver_on = True
            #self.image_frame.start()
            self.radio_frame.grid_remove()
            self.image_frame.grid(row=0, column=0, padx=0, pady=0, sticky="news")

    def update_size(self, event=None):
        width = self.winfo_width()
        height = self.winfo_height()
        #print(f"Windowsize: {width}x{height}")

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