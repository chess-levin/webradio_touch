import customtkinter

class App(customtkinter.CTk):
    
    def __init__(self):
        super().__init__()

        #self.my_v = 1

        self.t(4)
        self.t2()

    
    def t(self, x):
        self.my_v = x

    def t2(self):
        print(self.my_v)


if __name__ == "__main__":
    app = App()
    app.mainloop()