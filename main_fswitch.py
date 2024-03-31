import customtkinter as ctk

_win_width  = 1280
_win_height = 400

#ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
#ctk.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"

#https://www.youtube.com/watch?v=rG1SgFOzMqw

class App(ctk.CTk):
    def __init__(self):
        # main setup
        super().__init__()
        Content(self)


    def show_saver(self):
        print("show_saver")
        self.fr_saver.tkraise()
        self.after(5000, self.show_radio)

    def show_radio(self):
        print("show_radio")
        self.fr_radio.tkraise()
        self.after(5000, self.show_saver)


class Content():
    def __init__(self, parent):

        mainframe = ctk.CTkFrame(parent)
        mainframe.pack(expand=True, fill='both')
        self.index = 0

        self.frameList = [Radio(mainframe), Saver(mainframe)]
        self.frameList[1].forget()

        bottomframe =  ctk.CTkFrame(parent)
        bottomframe.pack(padx=10, pady=10)

        switch = ctk.CTkButton(master=bottomframe, text="SWITCH", command=self.changeFrame)
        switch.pack(padx=10, pady=10)

    def changeFrame(self):
        self.frameList[self.index].forget()
        self.index = (self.index + 1) % len(self.frameList)
        self.frameList[self.index].tkraise()
        self.frameList[self.index].pack(expand=True, fill='both')

class Radio(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color="blue")
                
        ctk.CTkLabel(master=self, text="Radio", width=60, height=15, text_color="white", fg_color="transparent", font=ctk.CTkFont(size=20, weight='bold', )).pack()
        self.pack(expand=True, fill='both')
        #self.pack(padx=10, pady=10)

        #ctk.CTkLabel(master=self, text="Title", fg_color="blue", font=ctk.CTkFont(size=20, weight='bold')).grid(row=1,column=1)
        #ctk.CTkLabel(master=self, text="Datetime", fg_color="blue", font=ctk.CTkFont(size=20, weight='bold')).grid(row=1,column=3)



class Saver(ctk.CTkFrame):
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="white")
        
        ctk.CTkLabel(master=self, text="Saver",  width=60, height=15, text_color="black", fg_color="transparent", font=ctk.CTkFont(size=20, weight='bold')).pack()
        self.pack(expand=True, fill='both')
        #self.pack(padx=10, pady=10)

app = App()
# run 
app.mainloop()