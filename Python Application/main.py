from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView


database = {
    "user1": {"nome": "Andrea", "password": "pass1", "saldo": 1000, "transazioni": []},
    "user2": {"nome": "Marco", "password": "pass2", "saldo": 500, "transazioni": []},
}

dynamicDatabase = []

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
        user = self.username.text
        psw = self.password.text

        if user in database and database[user]["password"] == psw:
            self.manager.user = database[user]  
            self.manager.current = "menu"
        else:
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
        user = self.username.text
        psw = self.password.text

        dynamicDatabase.append({user, psw})

        """ if user in database and database[user]["password"] == psw:
            self.manager.user = database[user]  
            self.manager.current = "login"
        else:
            popup = Popup(title="Errore", content=Label(text="Credenziali errate!"), size_hint=(0.6, 0.3))
            popup.open() """

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
            user_data = self.manager.user

            if importo > user_data["saldo"] or self.descrizione.text == "":
                popup = Popup(title="Errore", content=Label(text="Saldo insufficiente o descrizione mancante!"), size_hint=(0.6, 0.3))
                popup.open()
            else:
                user_data["saldo"] -= importo
                user_data["transazioni"].append(f"Prelievo: -{importo}€")
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
            user_data = self.manager.user

            if importo > 0:
                user_data["saldo"] += importo
                user_data["transazioni"].append(f"Deposito: +{importo}€")
                popup = Popup(title="Successo", content=Label(text="Deposito effettuato!"), size_hint=(0.6, 0.3))
                popup.open()
                self.manager.current = "menu"
        except ValueError:
            popup = Popup(title="Errore", content=Label(text="Inserisci un importo valido!"), size_hint=(0.6, 0.3))
            popup.open()


class VisualizzaScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)

        layout.add_widget(Label(text="Visualizza conto", font_size=24))

        self.balance_label = Label(text="Saldo: 0€", font_size=20)
        layout.add_widget(self.balance_label)

        """ confirm_button = Button(text="Conferma", on_press=self.deposita)
        layout.add_widget(confirm_button)"""

        back_button = Button(text="Indietro", on_press=lambda x: setattr(self.manager, "current", "menu"))
        layout.add_widget(back_button) 

        self.add_widget(layout)

    def fetchData(self, instance):
        try:
            importo = float(self.importo.text)
            user_data = self.manager.user

            if importo > 0:
                user_data["saldo"] += importo
                user_data["transazioni"].append(f"Deposito: +{importo}€")
                popup = Popup(title="Successo", content=Label(text="Deposito effettuato!"), size_hint=(0.6, 0.3))
                popup.open()
                self.manager.current = "menu"
        except ValueError:
            popup = Popup(title="Errore", content=Label(text="Inserisci un importo valido!"), size_hint=(0.6, 0.3))
            popup.open()
        


# Screen Manager
class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(RegisterScreen(name="register"))
        sm.add_widget(MenuScreen(name="menu"))
        sm.add_widget(PrelevaScreen(name="preleva"))
        sm.add_widget(DepositaScreen(name="deposita"))
        sm.add_widget(VisualizzaScreen(name="visualizza"))
        sm.user = None  # Store logged-in user
        return sm


if __name__ == "__main__":
    MyApp().run()
