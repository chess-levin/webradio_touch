import tkinter as tk
from PIL import Image, ImageTk
import os

_kiosk_screen_size = (1280, 400)

_image_path = "../gallery/private/"
_images = ["20220809_144810.jpg", "20230818_121739.jpg", "20230910_165329-01.jpg"]

class CustomCanvas(tk.Canvas):
    def __init__(self, master, image_path, **kwargs):
        super().__init__(master, **kwargs)
        self.image_path = os.path.join(_image_path, "20220809_144810.jpg")
        self.bg_image = None
        self.bind("<Configure>", self.resize_image)
        self.load_image()

    def load_image(self):
        self.original_image = Image.open(self.image_path)
        self.bg_image = ImageTk.PhotoImage(self.original_image)
        self.create_image(0, 0, anchor="nw", image=self.bg_image)

    def resize_image(self, event):
        new_width = event.width
        new_height = event.height
        resized_image = self.original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.bg_image = ImageTk.PhotoImage(resized_image)
        self.create_image(0, 0, anchor="nw", image=self.bg_image)

class MyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("800x600")
        #self.geometry(f"{_kiosk_screen_size[0]}x{_kiosk_screen_size[1]}")
        self.custom_canvas = CustomCanvas(self, "path_to_your_image.png")
        self.custom_canvas.pack(fill="both", expand=True)

app = MyApp()
app.mainloop()