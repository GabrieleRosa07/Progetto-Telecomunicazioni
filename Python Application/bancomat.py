from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Fbo, ClearColor, ClearBuffers, Scale, Translate
from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image
import bluetooth
import time
import threading
from datetime import datetime

database = {
    "user1": {"nome": "Andrea", "password": "pass1", "saldo": 1000, "transazioni": []},
    "user2": {"nome": "Marco", "password": "pass2", "saldo": 500, "transazioni": []},
}
bt_socket = None

def connetti_server():
    global bt_socket
    
    server_address = "D8:3A:DD:ED:86:AE"
    port = 1

    try:
        bt_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        bt_socket.connect((server_address, port))
        print("Connessione riuscita")
        
        saldo_iniziale = bt_socket.recv(1024).decode()
        print("saldo ricevuto:", saldo_iniziale)

        database["user1"]["saldo"] = float(saldo_iniziale)
        
    except Exception as e:
        print(f"Errore nella connessione: {e}")

    
def gestisci_bluetooth():
        while True:
            try:
                saldo_iniziale = bt_socket.recv(1024).decode()
                print("saldo ricevuto:", saldo_iniziale)

                database["user1"]["saldo"] = float(saldo_iniziale)
            except Exception as e:
                print(f"Errore {e}")
                time.sleep(1)

class MyScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user = None

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)

        layout.add_widget(Label(text="Login", font_size=24))
        
        self.username = TextInput(hint_text="Username", multiline=False)
        layout.add_widget(self.username)

        self.password = TextInput(hint_text="Password", password=True, multiline=False)
        layout.add_widget(self.password)

        login_button = Button(text="Accedi", on_press=self.validate_login)
        layout.add_widget(login_button)

        register_button = Button(text="Registrati ora!", on_press=lambda x: setattr(self.manager, "current", "register"))
        layout.add_widget(register_button)

        self.add_widget(layout)

    def validate_login(self, instance):
        user = self.username.text.strip()
        psw = self.password.text.strip()

        # Cerca per nome (case insensitive)
        for key, data in database.items():
            if data["nome"].lower() == user.lower() and data["password"] == psw:
                self.manager.user = data
                self.manager.current = "menu"
                return
    
        popup = Popup(title="Errore", content=Label(text="Credenziali errate!"), size_hint=(0.6, 0.3))
        popup.open()


class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)

        layout.add_widget(Label(text="Pagina di registrazione", font_size=24))
        
        self.username = TextInput(hint_text="Username", multiline=False)
        layout.add_widget(self.username)

        self.password = TextInput(hint_text="Password", password=True, multiline=False)
        layout.add_widget(self.password)

        login_button = Button(text="Registrati", on_press=self.validate_register)
        layout.add_widget(login_button)

        rgs_button = Button(text="Torna il login", on_press=lambda x: setattr(self.manager, "current", "login"))
        layout.add_widget(rgs_button)

        self.add_widget(layout)

    def validate_register(self, instance):
        user = self.username.text.strip()
        psw = self.password.text.strip()
        
        if not user or not psw:
            popup = Popup(title="Errore", content=Label(text="Inserisci username e password"), size_hint=(0.6, 0.3))
            popup.open()
            return
            
        if user in database:
            popup = Popup(title="Errore", content = Label(text="Utente già esistente"), size_hint=(0.6, 0.3))
            popup.open()
        else:
            database[user] = {"nome":user, "password":psw, "saldo":0, "transazioni":[]}
            popup = Popup(title="Successo", content = Label(text="Registrazione avvenuta con successo"), size_hint=(0.6, 0.3))
            popup.open()
            self.manager.current = "login"

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)

        self.welcome_label = Label(text="Benvenuto!", font_size=24)
        layout.add_widget(self.welcome_label)

        layout.add_widget(Button(text="Preleva", on_press=lambda x: setattr(self.manager, "current", "preleva")))
        layout.add_widget(Button(text="Deposita", on_press=lambda x: setattr(self.manager, "current", "deposita")))
        layout.add_widget(Button(text="Visualizza Transazioni", on_press=lambda x: setattr(self.manager, "current", "visualizza")))

        self.add_widget(layout)

    def on_pre_enter(self, *args):
        self.welcome_label.text = f"Benvenuto {self.manager.user['nome']}"


class PrelevaScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)

        layout.add_widget(Label(text="Effettua Prelievo", font_size=24))

        self.importo = TextInput(hint_text="Importo", multiline=False)
        layout.add_widget(self.importo)

        self.descrizione = TextInput(hint_text="Descrizione", multiline=False)
        layout.add_widget(self.descrizione)

        confirm_button = Button(text="Conferma", on_press=self.preleva)
        layout.add_widget(confirm_button)

        back_button = Button(text="Indietro", on_press=lambda x: setattr(self.manager, "current", "menu"))
        layout.add_widget(back_button)

        self.add_widget(layout)

    def preleva(self, instance):
        try:
            importo = float(self.importo.text)
            descrizione = self.descrizione.text
            user_data = self.manager.user
            data_corrente = datetime.now().strftime("%Y-%m-%d")

            if importo > user_data["saldo"] or self.descrizione.text == "":
                popup = Popup(title="Errore", content=Label(text="Saldo insufficiente o descrizione mancante!"), size_hint=(0.6, 0.3))
                popup.open()
            else:
                user_data["saldo"] -= importo
                transazione = f"uscita 2024-03-31 {importo} {descrizione}"
                user_data["transazioni"].append(transazione)
                if bt_socket:
                    try:
                        bt_socket.send(transazione.encode('utf-8')) 
                    except:
                        print("Errore nell'invio transazione")

                popup = Popup(title="Successo", content=Label(text="Prelievo effettuato!"), size_hint=(0.6, 0.3))
                popup.open()
                self.manager.current = "menu"
        except ValueError:
            popup = Popup(title="Errore", content=Label(text="Inserisci un importo valido!"), size_hint=(0.6, 0.3))
            popup.open()

class DepositaScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)

        layout.add_widget(Label(text="Effettua Deposito", font_size=24))

        self.importo = TextInput(hint_text="Importo", multiline=False)
        layout.add_widget(self.importo)

        self.descrizione = TextInput(hint_text="Descrizione", multiline=False)
        layout.add_widget(self.descrizione)

        confirm_button = Button(text="Conferma", on_press=self.deposita)
        layout.add_widget(confirm_button)

        back_button = Button(text="Indietro", on_press=lambda x: setattr(self.manager, "current", "menu"))
        layout.add_widget(back_button)

        self.add_widget(layout)

    def deposita(self, instance):
        try:
            importo = float(self.importo.text)
            descrizione = self.descrizione.text
            user_data = self.manager.user

            if importo > 0:
                user_data["saldo"] += importo
                transazione = f"entrata 2024-03-31 {importo} {descrizione}"
                user_data["transazioni"].append(transazione)
                if bt_socket:
                    try:
                        bt_socket.send(transazione.encode('utf-8')) 
                    except:
                        print("Errore nell'invio transazione")

                popup = Popup(title="Successo", content=Label(text="Deposito effettuato!"), size_hint=(0.6, 0.3))
                popup.open()
                self.manager.current = "menu"
        except ValueError:
            popup = Popup(title="Errore", content=Label(text="Inserisci un importo valido!"), size_hint=(0.6, 0.3))
            popup.open()


class VisualizzaScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.layout = BoxLayout(orientation="vertical", padding=20, spacing=10)

        self.layout.add_widget(Label(text="Visualizza conto", font_size=24))

        self.balance_label = Label(text="Saldo: 0€", font_size=20)
        self.layout.add_widget(self.balance_label)

        # ScrollView per le transazioni
        self.scroll = ScrollView(size_hint=(1, 1))
        self.transazioni_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=10)
        self.transazioni_box.bind(minimum_height=self.transazioni_box.setter("height"))
        self.scroll.add_widget(self.transazioni_box)
        self.layout.add_widget(self.scroll)

        back_button = Button(text="Indietro", size_hint_y=None, height=50, on_press=lambda x: setattr(self.manager, "current", "menu"))
        self.layout.add_widget(back_button)

        self.add_widget(self.layout)

    def on_pre_enter(self, *args):
        user_data = self.manager.user
        self.balance_label.text = f"Saldo: {user_data['saldo']}€"

        # Pulisce vecchie transazioni
        self.transazioni_box.clear_widgets()

        # Aggiunge le transazioni attuali
        if user_data["transazioni"]:
            for transazione in user_data["transazioni"]:
                self.transazioni_box.add_widget(Label(text=transazione, size_hint_y=None, height=30))
        else:
            self.transazioni_box.add_widget(Label(text="Nessuna transazione effettuata.", size_hint_y=None, height=30))

        


# Screen Manager
class MyApp(App):
    def build(self):
        sm = MyScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(RegisterScreen(name="register"))
        sm.add_widget(MenuScreen(name="menu"))
        sm.add_widget(PrelevaScreen(name="preleva"))
        sm.add_widget(DepositaScreen(name="deposita"))
        sm.add_widget(VisualizzaScreen(name="visualizza"))
        return sm


if __name__ == "__main__":
    connetti_server()
    threading.Thread(target=gestisci_bluetooth, daemon=True).start()
    time.sleep(1)
    MyApp().run()
