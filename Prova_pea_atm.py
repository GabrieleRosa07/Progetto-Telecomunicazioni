import customtkinter as ctk
from tkinter import messagebox

# Configurazione dello stile
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Database simulato
database = {
    "user1": {"password": "pass1", "saldo": 1000},
    "user2": {"password": "pass2", "saldo": 500}
}

class BancaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Banca Virtuale - ATM")
        self.root.geometry("400x500")
        
        self.frame = ctk.CTkFrame(root)
        self.frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        self.user_label = ctk.CTkLabel(self.frame, text="Username:")
        self.user_label.pack(pady=5)
        self.user_entry = ctk.CTkEntry(self.frame)
        self.user_entry.pack(pady=5)
        
        self.pass_label = ctk.CTkLabel(self.frame, text="Password:")
        self.pass_label.pack(pady=5)
        self.pass_entry = ctk.CTkEntry(self.frame, show="*")
        self.pass_entry.pack(pady=5)
        
        self.login_button = ctk.CTkButton(self.frame, text="Login", command=self.login)
        self.login_button.pack(pady=10)
        
    def login(self):
        user = self.user_entry.get()
        password = self.pass_entry.get()
        if user in database and database[user]["password"] == password:
            self.user = user
            self.main_menu()
        else:
            messagebox.showerror("Errore", "Credenziali errate")
        
    def main_menu(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
        
        self.saldo_label = ctk.CTkLabel(self.frame, text=f"Saldo: {database[self.user]['saldo']}€", font=("Arial", 20))
        self.saldo_label.pack(pady=20)
        
        self.deposito_button = ctk.CTkButton(self.frame, text="Deposita", command=self.deposita)
        self.deposito_button.pack(pady=10)
        
        self.prelievo_button = ctk.CTkButton(self.frame, text="Preleva", command=self.preleva)
        self.prelievo_button.pack(pady=10)
        
        self.logout_button = ctk.CTkButton(self.frame, text="Logout", command=self.logout)
        self.logout_button.pack(pady=20)
        
    def deposita(self):
        self.operazione("Deposito")
    
    def preleva(self):
        self.operazione("Prelievo")
    
    def operazione(self, tipo):
        def conferma():
            try:
                amount = float(entry.get())
                if tipo == "Prelievo" and amount > database[self.user]['saldo']:
                    messagebox.showerror("Errore", "Saldo insufficiente")
                else:
                    if tipo == "Deposito":
                        database[self.user]['saldo'] += amount
                    else:
                        database[self.user]['saldo'] -= amount
                    messagebox.showinfo("Successo", f"{tipo} di {amount}€ completato!")
                    self.main_menu()
            except ValueError:
                messagebox.showerror("Errore", "Importo non valido")
        
        window = ctk.CTkToplevel(self.root)
        window.title(tipo)
        window.geometry("300x200")
        
        ctk.CTkLabel(window, text=f"Inserisci importo per {tipo.lower()}: ").pack(pady=10)
        entry = ctk.CTkEntry(window)
        entry.pack(pady=5)
        ctk.CTkButton(window, text="Conferma", command=conferma).pack(pady=10)
    
    def logout(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.__init__(self.root)

if __name__ == "__main__":
    root = ctk.CTk()
    app = BancaGUI(root)
    root.mainloop()
