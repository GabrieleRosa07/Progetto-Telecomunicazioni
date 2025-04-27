#include <SPI.h>
#include <MFRC522.h>
#include <Keypad.h>

// Definizione delle costanti per il numero di righe e colonne della tastiera
#define ROWS 4
#define COLS 3
// Pin utilizzati per il modulo RFID
#define SS_PIN 10
#define RST_PIN 9

// Menu con le opzioni disponibili
const char* menu[] = {
  "1. Inserisci cash",
  "2. Ritira cash",
  "3. Estratto conto",
  "4. Esci"
};

// Inizializzazione del modulo RFID
MFRC522 rfid(SS_PIN, RST_PIN);

// Mappa dei tasti della tastiera
char keymap[ROWS][COLS] = {
  {'1', '2', '3'},
  {'4', '5', '6'},
  {'7', '8', '9'},
  {'*','0','#'},
};

// Pin della tastiera
byte rowPins[ROWS] = {8, 7, 6, 2};
byte colPins[COLS] = {5, 4, 3};

// Inizializzazione dell'oggetto tastiera
Keypad keypad = Keypad(makeKeymap(keymap), rowPins, colPins, ROWS, COLS);

// Codice predefinito per l'autenticazione (4 cifre)
char code[5] = "7643";

// Variabile per memorizzare il saldo totale
float totCash;

void setup() {
  Serial.begin(115200);
  //Serial.begin(9600); // Avvia la comunicazione seriale
  SPI.begin(); // Inizializza la comunicazione SPI
  rfid.PCD_Init(); // Inizializza il modulo RFID
}

void loop() {
  updateCashIfAvailable();

    if (readTag()) { // Se viene letto un tag RFID
      if (verifyCode()) { // Verifica se il codice inserito è corretto
        bool exitMenu = false; // Flag per uscire dal menu

        while (!exitMenu) { // Ciclo principale del menu
          updateCashIfAvailable();

          displayMenu(); // Mostra il menu
          exitMenu = handleSelection(); // Gestisce la selezione dell'utente
        }
        
        Serial.println("Grazie per aver usato il nostro servizio!"); // Messaggio di uscita
      } else {
        Serial.println("Codice errato. Accesso negato."); // Codice errato
      }
    }
}

// Funzione per leggere un tag RFID
bool readTag() {
  if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) { // Se è presente un nuovo tag
    Serial.println("BENVENUTO AL ATM"); // Messaggio di benvenuto
   
    
    rfid.PICC_HaltA(); // Ferma la lettura del tag
    return true;
  }
  return false;
}

// Funzione per verificare il codice inserito
bool verifyCode() {
  char key;
  char userCode[5] = ""; // Codice utente inserito
  int index = 0;
  int attempts = 3; // Numero di tentativi

  while (attempts > 0) {
    Serial.println("Inserisci il codice (4 cifre): "); // Richiesta del codice
    while (index < 4) {
      key = keypad.getKey(); // Legge il tasto premuto
      if (key && isDigit(key)) { // Se il tasto è un numero
        userCode[index++] = key; // Aggiunge il tasto al codice
        Serial.print('*'); // Nasconde il codice digitato
      }
    }
    userCode[index] = '\0'; // Termina la stringa

    if (strcmp(userCode, code) == 0) { // Se il codice inserito è corretto
      Serial.println("\nCodice corretto!"); // Codice corretto
      return true;
    } else {
      attempts--; // Diminuisce i tentativi
      Serial.println("\nCodice errato! Tentativi rimasti: " + String(attempts)); // Codice errato
      index = 0; // Resetta il codice inserito per un nuovo tentativo
    }
  }
  return false; // Se i tentativi sono finiti, ritorna falso
}

// Funzione per visualizzare il menu
void displayMenu() {
  Serial.println("Seleziona un'opzione:"); // Messaggio per selezionare un'opzione
  for (int i = 0; i < 4; i++) {
    Serial.println(menu[i]); // Mostra le opzioni del menu
  }
}

// Funzione per gestire la selezione del menu
bool handleSelection() {
  char key = NO_KEY; // Inizializza la variabile per la scelta

  while (key == NO_KEY) { // Attende che venga premuto un tasto
    updateCashIfAvailable();
    key = keypad.getKey(); // Legge il tasto premuto
  }

  switch (key) {
    case '1': { // Se l'utente seleziona "1" per inserire soldi
      Serial.println("Inserisci soldi: ");
      int cash = readNumber(); // Legge l'importo da inserire
      totCash += cash; // Aggiunge l'importo al saldo
      Serial.println("entrata 03/0472025 "+ String(cash) + " deposito");
      Serial.println("Saldo attuale: " + String(totCash)); // Mostra il saldo
      break;
    }
    case '2': { // Se l'utente seleziona "2" per ritirare soldi
      Serial.println("Inserisci l'importo da ritirare: ");
      int amount = readNumber(); // Legge l'importo da ritirare
      if (amount > totCash) { // Se il saldo è insufficiente
        Serial.println("Saldo insufficiente!"); // Mostra il messaggio di errore
      } else {
        totCash -= amount; // Sottrae l'importo dal saldo
        Serial.println("uscita 03/0472025 "+ String(amount) + " pagamento");
        Serial.println("Saldo attuale: " + String(totCash)); // Mostra il saldo
      }
      break;
    }
    case '3': { // Se l'utente seleziona "3" per visualizzare il saldo
      Serial.println("Saldo attuale: " + String(totCash)); // Mostra il saldo
      break;
    }
    case '4': { // Se l'utente seleziona "4" per uscire
      Serial.println("Uscita dal menu..."); // Messaggio di uscita
      return true; // Indica che l'utente vuole uscire
    }
    default: { // Se viene selezionata un'opzione non valida
      Serial.println("Scelta non valida."); // Messaggio di errore
      break;
    }
  }

  return false; // Continua a mostrare il menu se non è stata selezionata l'opzione di uscita
}

// Funzione per leggere un numero inserito dall'utente
int readNumber() {
  char key;
  char buffer[5]; // Spazio per 4 cifre + carattere terminatore
  int index = 0;

  Serial.println("Inserisci un numero (max 4 cifre) e premi # per confermare: "); // Richiesta di inserimento numero

  while (true) {
    updateCashIfAvailable();
    key = keypad.getKey(); // Legge il tasto premuto

    // Se è un numero e il limite di 4 cifre non è stato raggiunto
    if (key && isDigit(key)) {
      if (index < 4) {
        buffer[index++] = key; // Aggiunge il numero al buffer
        Serial.print(key); // Stampa il numero digitato
      } else {
        Serial.println("\nMassimo 4 cifre consentite!"); // Messaggio di errore se superato il limite
      }
    } 
    // Se viene premuto il tasto #
    else if (key == '#') {
      if (index == 0) { // Se non è stato inserito nessun numero
        Serial.println("\nInserimento non valido. Riprova."); // Messaggio di errore
        return 0;
      }
      buffer[index] = '\0'; // Termina la stringa
      Serial.println(); // Nuova riga
      return atoi(buffer); // Converte il buffer in un intero e lo ritorna
    }
  }
}

void updateCashIfAvailable() {
  if (Serial.available() > 0) {
    String received_data = Serial.readStringUntil('\n');
    totCash = received_data.toFloat();
  }
}

