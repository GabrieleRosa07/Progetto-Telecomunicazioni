import customtkinter as ctk
from tkinter import messagebox as ms

database = {
    "user1": {"nome": "Andrea","password": "pass1", "saldo": 1000, "transazioni": []},
    "user2": {"nome": "Marco","password": "pass2", "saldo": 500, "transazioni": []},
}

class FrameMenu(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.lbl_titolo = ctk.CTkLabel(self, text="MENU", anchor="center")
        self.lbl_titolo.grid(row=0, column=0, padx=20, pady=20, sticky="nsew" )

        self.button1 = ctk.CTkButton(self, text="Bottone 1", command=self.button_callback)
        self.button1.grid(row=1, column=0, padx=20, pady=(50, 20), sticky="nw")

        self.button2 = ctk.CTkButton(self, text="Bottone 2")
        self.button2.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nw")

    def button_callback(self):
        print("ciao")

class FrameHome(ctk.CTkFrame):
    def __init__(self, master, user):
        super().__init__(master)

        self.user = user

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.configure(fg_color=master.cget("bg"))

        self.lbl_titolo = ctk.CTkLabel(self, text=f"Benvenuto {self.user['nome']}", anchor="center", font=("Helvetica", 40))
        self.lbl_titolo.grid(row=0, column=0, padx=20, pady=(20, 0), columnspan=1, sticky="new")



class App(ctk.CTk):
    def __init__(self, user):
        super().__init__()

        self.title("prova")
        self.geometry("1200x800")
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=10)
        self.grid_rowconfigure(0, weight=1)
        ctk.set_appearance_mode("dark")

        self.user = user

        self.menu_frame = FrameMenu(self)
        self.menu_frame.grid(row=0, column=0, padx=(10,0), pady=10, sticky="nws")

        self.home_frame = FrameHome(self,user)
        self.home_frame.grid(row=0, column=1, padx=0, pady=0, sticky="nsew",columnspan=1)

class Login(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("login")
        self.geometry("500x300")
        self.resizable(False, False)
        ctk.set_appearance_mode("dark")

        self.grid_columnconfigure(0, weight=1)

        self.login_label = ctk.CTkLabel(self, text="Login", anchor="center", font=("Helvetica", 30))
        self.login_label.grid(row=0, column=0, padx=0, pady=(30, 40), sticky="nsew", columnspan=1)

        self.user_label = ctk.CTkLabel(self, text="username")
        self.user_label.grid(row=1, column=0, padx=(120,20), pady=(0,20), sticky="nsw")

        self.user_entry = ctk.CTkEntry(self)
        self.user_entry.grid(row=1, column=0, padx=(200,100), pady=(0, 20), sticky="nsew")

        self.psw_label = ctk.CTkLabel(self, text="password")
        self.psw_label.grid(row=2, column=0, padx=(120,20), pady=(0,20), sticky="nsw")

        self.psw_entry = ctk.CTkEntry(self, show="*")
        self.psw_entry.grid(row=2, column=0, padx=(200,100), pady=(0, 20), sticky="nsew")

        self.login_button = ctk.CTkButton(self, text="Accedi", command = self.login)
        self.login_button.grid(row=3, column=0, padx=50, pady=0, sticky="nsew")

    def login(self):
        user = self.user_entry.get()
        psw = self.psw_entry.get()

        if user=="" or psw=="":
            ms.showerror("Errore", "Inserisci le credenziali")
        elif user in database and database[user]["password"] == psw:
            
            self.user = database[user]
            self.destroy()
            app = App(self.user)
            app.mainloop()
        else:
            ms.showerror("Errore", "Credenziali errate")
        

app = Login()
app.mainloop()