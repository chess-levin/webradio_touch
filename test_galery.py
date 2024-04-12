import customtkinter as ctki
from PIL import Image
import glob
import sys
import random
import time

_win_width  = 1280
_win_height = 400

_gallery_path_glob =  "gallery/private/*.jpg"

"""
app = ctki.CTk()
app.title("my app")
app.geometry(f"{_win_width}x{_win_height}")

img = Image.open("galerie/philosophie-1280x400.jpg")

la_image = ctki.CTkLabel(master=app, image=ctki.CTkImage(img, size=(_win_width, _win_height)), text='')
la_image.grid(row=0, column=0)

fr_frame = ctki.CTkFrame(master=app, bg_color='transparent', fg_color='transparent')
fr_frame.grid(row=0, column=0, sticky="n")

la_datetime = ctki.CTkLabel(master=fr_frame, bg_color='transparent', fg_color='transparent', text=time.strftime('%H:%M:%S'), 
                                         font=ctki.CTkFont(size=60, weight="normal"), text_color="white")
la_datetime.grid(row=0, column=0, sticky="n")

app.mainloop()"""


def return_func():
    print("return")

class FrameScreensaverPictureContent(ctki.CTkFrame):

    def __init__(self, parent, show_for_s, return_to_radio_func, show_randomly=False):
        print(type(parent))

        self.image_path_list = []
        self.scan_galery()

        img = Image.open(self.image_path_list[0])
        
        self.la_image = ctki.CTkLabel(master=parent, image=ctki.CTkImage(img, size=(_win_width, _win_height)), 
                                      fg_color='transparent', text=self.currentDatetime(), anchor="s",
                                      font=ctki.CTkFont(size=60, weight="normal"), text_color="white")
        self.la_image.grid(row=0, column=0)
        self.la_image.bind(sequence="<Button-1>", command=self.stop, add='+')

        super().__init__(parent)

        self.parent = parent
        self.return_to_radio_func = return_to_radio_func
        self.show_for_s = show_for_s
        self.time = 0
        self.show_randomly = show_randomly
        self.activate()

    def currentDatetime(self):
        return time.strftime('%H:%M:%S')+time.strftime('\n %A, %B %d')

    def scan_galery(self):
        print("Scanning gallery folder")

        for filename in glob.glob(_gallery_path_glob, recursive=False):
            try:
                print(f"found {filename}")
                Image.open(filename)
                self.image_path_list.append(filename)
            except OSError as e:
                print(f"Unable to open image {filename}. Check image format. Details : {e}", file=sys.stderr)

        print(f"Galerie contains {len(self.image_path_list)} pictures")

    def show_next_image(self, image_index):
        print("self.image_index=",image_index)
        next_image = ctki.CTkImage(Image.open(self.image_path_list[image_index]), size=(_win_width, _win_height))
        self.la_image.configure(image = next_image)
       

    def update_time(self):
        self.time += 1
        if (self.time > self.show_for_s):
            self.time = 0
            self.show_next_image(random.randint(0, len(self.image_path_list)-1))
        
        self.la_image.configure(text = self.currentDatetime())
        self.tid_update_time = self.after(1000, self.update_time)


    def stop(self, event):
        print("Stop Screensaver")
        self.after_cancel(self.tid_update_time)
        self.return_to_radio_func()

    def activate(self):
        #super().grid(row=0, column=0, padx=0, pady=0, sticky="news")
        self.time = 0
        self.update_time()


app = ctki.CTk()
app.title("Demo app")
app.geometry(f"{_win_width}x{_win_height}")

fr = FrameScreensaverPictureContent(app, 5, return_func)

app.mainloop()

"""
 # create login frame
login_frame = ctki.CTkFrame(app, corner_radius=0)
login_frame.grid(row=0, column=0, sticky="ns")
login_label = ctki.CTkLabel(login_frame, text="ctki\nLogin Page", font=ctki.CTkFont(size=20, weight="bold"))
login_label.grid(row=0, column=0, padx=30, pady=(150, 15))
username_entry = ctki.CTkEntry(login_frame, width=200, placeholder_text="username")
username_entry.grid(row=1, column=0, padx=30, pady=(15, 15))
password_entry = ctki.CTkEntry(login_frame, width=200, show="*", placeholder_text="password")
password_entry.grid(row=2, column=0, padx=30, pady=(0, 15))
login_button = ctki.CTkButton(login_frame, text="Login",  width=200)
login_button.grid(row=3, column=0, padx=30, pady=(15, 15))

 """



