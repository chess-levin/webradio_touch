import tkinter as tk
import customtkinter as ctki
from PIL import Image, ImageTk
import time
import os
import random
import platform
import sys
import glob


_win_width  = 1280
_win_height = 400

_gallery_glob = os.path.join("../gallery", "private", "*.??g")

ctki.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
ctki.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"

class MyCanvas(tk.Canvas):
    
    def __init__(self, root, **kwargs):

        super().__init__(root, width=_win_width, height=_win_height)

        self.image_path_list = []
        self.counter = 0
        self.image_index = 0

        self.scan_gallery()

        self.bg_image = self.load_bg_image(self.image_path_list[self.image_index])
        #self.canvas = tk.Canvas(root, width=_win_width, height=_win_height)

        self.grid(row=0, column=0, sticky="nsew")

        self.c_bg_img = self.create_image(0, 0, image=self.bg_image, anchor="nw")

        self.tag_bind(self.c_bg_img, '<Button-1>', self.stop)

        self.c_text_dt = self.create_text( int(_win_width/2), 10, text = "HH:MM:SS", font = ctki.CTkFont(size=28, weight="bold"), fill='white', anchor="n") 

        self.after(1000, self.update_datetime)

    def load_bg_image(self, path):
        img =  Image.open(path)
        print (f"Loaded {path} dim: ({img.width}x{img.height}), 1:{(img.width / img.height):.2f}")
        img = img.resize((_win_width, _win_height))
        print (f"resized to ({img.width}x{img.height})")
        return ImageTk.PhotoImage(img)
    
    def show_next_image(self):
        self.image_index = random.randint(0, len(self.image_path_list)-1)
        print("self.image_index=",self.image_index)
        self.bg_image = self.load_bg_image(self.image_path_list[self.image_index])
        self.itemconfig(self.c_bg_img, image=self.bg_image)

    def update_datetime(self):
        self.counter += 1

        t = time.strftime('%H:%M:%S, %A, %B %d')
        self.itemconfig(self.c_text_dt, text=t)

        if (self.counter == 5):
            self.show_next_image()
            self.counter = 0

        self.after(1000, self.update_datetime)
    
    def scan_gallery(self):
        print("Scanning galerie folder")

        for filename in glob.glob(_gallery_glob, recursive=False):
            try:
                img = Image.open(filename)
                print (f"registered {filename} dim: ({img.width}x{img.height}), 1:{(img.width / img.height):.2f}")
                self.image_path_list.append(filename)
            except OSError as e:
                print(f"Unable to open image {filename}. Check image format. Details : {e}", file=sys.stderr)

        print(f"Galerie contains {len(self.image_path_list)} pictures")
        return len(self.image_path_list)

    def stop(self, event=None):
        print("click stop")

    
    def switch_to_frame(self):
        self.canvas.grid_forget()
        self.content_frame.grid(row=0, column=0, sticky="nsew")

    def switch_to_canvas(self):
        self.content_frame.grid_forget()
        self.canvas.grid(row=0, column=0, sticky="nsew")


class MyFrame(ctki.CTkFrame):

     def __init__(self, root):
        super().__init__(root)

        self.grid_columnconfigure(0)
        self.grid_rowconfigure(0)
        self.grid(row=0, column=0, padx=0, pady=0)

        ctki.CTkLabel(self, text="TEST").grid(row=0, column=0, padx=0, pady=0, sticky="news")


class App(ctki.CTk):

    def __init__(self, fullscreen):
        super().__init__()

        self.fullscreen = fullscreen
        self.cont = 0

        self.title("RADIO & SHOWER")
        
        #self.geometry(f"{_win_width}x{_win_height}")
        self.geometry("1280x400")
        self.resizable(False, False)

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        print(f"screen_width x screen_height = {screen_width}x{screen_height}")

        print("Configure kiosk fullscrenn mode:", self.fullscreen)

        if self.fullscreen:
            self.attributes("-fullscreen", True) # run fullscreen
            self.wm_attributes("-topmost", True) # keep on top
        

        #self.minsize(_win_width, _win_height)
        #self.maxsize(_win_width, _win_height)

        self.resizable(False, False)

        self.grid_rowconfigure(0)
        self.grid_columnconfigure(0)

        self.content = []

        self.content.append(MyCanvas(self))
        self.content.append(MyFrame(self))

        self.switch()

    def switch(self):
        self.content[self.cont].grid(row=0, column=0, padx=0, pady=0) #, sticky="news"
        
        self.cont += 1
        if self.cont > 1:
            self.cont = 0

        self.content[self.cont].grid_forget()

        self.after(5000, self.switch)


def on_escape(event=None):
    print("escaped")
    app.destroy()


print(f"sys.argv={sys.argv}, len(sys.argv)={len(sys.argv)}")
_kiosk_mode = False

if (len(sys.argv) > 1):
    if (sys.argv[1]=='kiosk'):
        _kiosk_mode = True

if os.environ.get('DISPLAY','') == '':
    print('no display found. Using :0.0')
    os.environ.__setitem__('DISPLAY', ':0.0')


if __name__ == "__main__":
    app = App(_kiosk_mode)

    print(f"Running Env {platform.system()}")

    print("_kiosk_mode=",_kiosk_mode)



    #root.focus_set() # set focus on window
    # --- closing methods ---

    # close window with key `ESC`
    app.bind("<Escape>", on_escape)
    app.mainloop()

