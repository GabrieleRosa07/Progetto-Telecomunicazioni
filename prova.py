import customtkinter as ctk
from tkinter import messagebox as ms
from tkcalendar import Calendar

database = {
    "user1": {"nome": "Andrea","password": "pass1", "saldo": 1000, "transazioni": []},
    "user2": {"nome": "Marco","password": "pass2", "saldo": 500, "transazioni": []},
}

class FrameMenu(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.lbl_titolo = ctk.CTkLabel(self, text="MENU", anchor="center")
        self.lbl_titolo.grid(row=0, column=0, padx=20, pady=20, sticky="nsew" )

        self.button_preleva = ctk.CTkButton(self, text="Preleva", command=self.preleva)
        self.button_preleva.grid(row=1, column=0, padx=20, pady=(50, 20), sticky="nw")

        self.button_deposita = ctk.CTkButton(self, text="Deposita")
        self.button_deposita.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nw")

        self.button_transazione = ctk.CTkButton(self, text="Visualizza Transazioni")
        self.button_transazione.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="nw")

        self.button_settings = ctk.CTkButton(self, text="Impostazioni")
        self.button_settings.grid(row=4, column=0, padx=20, pady=(0, 20), sticky="nw")

    def preleva(self):
        if hasattr(self.master, "principal_frame"):
            self.master.principal_frame.destroy()

        self.master.principal_frame = PrelevaFrame(self.master)
        self.master.principal_frame.grid(row=0, column=1, padx=0, pady=0, sticky="nsew", columnspan=1)

class PrelevaFrame(ctk.CTkFrame):
    def __init__(self,master):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)

        self.configure(fg_color=master.cget("bg"))

        self.lbl_titolo = ctk.CTkLabel(self, text="Effettua prelievo", font=("Helvetica", 30), anchor="center")
        self.lbl_titolo.grid(row=0, column=0, padx=20, pady=20, sticky="new")

        self.frame_importo = FrameImporto(self)
        self.frame_importo.grid(row=3, column=0, padx=30, pady=(100, 0), sticky="new")

class FrameImporto(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.lbl_importo = ctk.CTkLabel(self, text="Inserisci l'importo del prelievo", font=("Helvetica", 15), anchor="center")
        self.lbl_importo.grid(row=0, column=0, padx=0, pady=(20, 30), sticky="ew")

        self.importo_entry = ctk.CTkEntry(self)
        self.importo_entry.grid(row=1, column=0, padx=20, pady=(0, 30), sticky="ew")

        self.lbl_data = ctk.CTkLabel(self, text="Seleziona la data del prelievo", font=("Helvetica", 15), anchor="center")
        self.lbl_data.grid(row=2, column=0, padx=0, pady=(0, 20), sticky="new")
        
        self.button_open_calendar = ctk.CTkButton(self, text="Apri Calendario", command=self.open_calendar)
        self.button_open_calendar.grid(row=3, column=0, padx=20, pady=10, sticky="new")
        
        self.descrizione_area = ctk.CTkTextbox(self)
        self.descrizione_area.insert("0.0","Descrizione del prelievo")
        self.descrizione_area.grid(row=0, column=1, padx=20, pady=20, sticky="nsew", rowspan=4)

       
    def open_calendar(self):
        DatePicker(self, self.set_date)

    def set_date(self, date):
        self.button_open_calendar.configure(text=date)

class DatePicker(ctk.CTkToplevel):  
    def __init__(self, master, callback):
        super().__init__(master)
        self.title("Seleziona la data")
        self.geometry("300x300")

        self.cal = Calendar(self, selectmode="day", date_pattern="dd/mm/yyyy")
        self.cal.pack(pady=20)

        self.btn_ok = ctk.CTkButton(self, text="Conferma", command=lambda: self.select_date(callback))
        self.btn_ok.pack(pady=10)

    def select_date(self, callback):
        selected_date = self.cal.get_date()
        callback(selected_date)  
        self.destroy()

       

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
        self.grid_columnconfigure(1, weight=20)
        self.grid_rowconfigure(0, weight=1)
        ctk.set_appearance_mode("dark")

        self.user = user

        self.menu_frame = FrameMenu(self)
        self.menu_frame.grid(row=0, column=0, padx=(10,0), pady=10, sticky="nws")

        self.principal_frame = FrameHome(self,user)
        self.principal_frame.grid(row=0, column=1, padx=0, pady=0, sticky="nsew",columnspan=1)

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