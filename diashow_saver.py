import customtkinter as ctki
import tkinter as tk 
from PIL import Image, ImageTk
import time
import glob
import sys
import os
import random

_gallery_glob     = os.path.join("gallery","private","*.??g")
_next_dia_after_s = 20


class DiaShowCanvas(tk.Canvas):
    
    def __init__(self, root, window_width, window_height, return_to_radio_func):

        self.win_width = window_width
        self.win_height = window_height

        super().__init__(root, width=self.win_width, height=self.win_height)
        
        self.return_to_radio_func = return_to_radio_func
        self.image_path_list = []
        self.counter = 0
        self.image_index = 0

        self.scan_gallery()

        self.bg_image = self.load_bg_image(self.image_path_list[self.image_index])
        self.c_bg_img = self.create_image(0, 0, image=self.bg_image, anchor="nw")
        self.tag_bind(self.c_bg_img, '<Button-1>', self.stop)

        self.c_text_dt = self.create_text(self.win_width/2, 10, text = "HH:MM:SS", font = ctki.CTkFont(size=28, weight="bold"), fill='white', anchor="n") 


    def load_bg_image(self, path):
        img =  Image.open(path)
        print (f"Loaded {path} dim: ({img.width}x{img.height}), 1:{(img.width / img.height):.2f}")
        
        if (img.width != self.win_width) or (img.height != self.win_height):
            img = img.resize((self.win_width, self.win_height))
            print (f"Image resized to ({img.width}x{img.height})")

        return ImageTk.PhotoImage(img)
    
    def show_next_image(self):
        self.image_index = random.randint(0, len(self.image_path_list)-1)
        print("self.image_index=",self.image_index)
        self.bg_image = self.load_bg_image(self.image_path_list[self.image_index])
        self.itemconfig(self.c_bg_img, image=self.bg_image)

    def update_time(self):
        self.counter += 1

        t = time.strftime('%H:%M:%S, %A, %B %d')
        self.itemconfig(self.c_text_dt, text=t)

        s = time.strftime('%S')
        if (int(s) % _next_dia_after_s == 0):
            self.show_next_image()

        self.tid_update_time = self.after(1000, self.update_time)
    
    def scan_gallery(self):
        print(f"Scanning galerie folder {_gallery_glob}")

        for filename in glob.glob(_gallery_glob, recursive=False):
            try:
                img = Image.open(filename)
                print (f"registered {filename} dim: ({img.width}x{img.height}), 1:{(img.width / img.height):.2f}")
                self.image_path_list.append(filename)
            except OSError as e:
                print(f"Unable to open image {filename}. Check image format. Details : {e}", file=sys.stderr)

        print(f"Galerie contains {len(self.image_path_list)} pictures")
        return len(self.image_path_list)

    def stop(self, event):
        print("Stop Screensaver")
        self.after_cancel(self.tid_update_time)
        self.return_to_radio_func()

    def activate(self):
        self.grid(row=0, column=0, padx=0, pady=0, sticky="news")
        self.counter = 0
        self.tid_update_time = self.update_time()