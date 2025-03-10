# Progetto-Telecomunicazioni

## Sistema bancario
### creare un'applicazione Python che simula un sistema bancario:
Con Arduino Freenove (usiamo come base il progetto già ralizzato con Freenove):
 - tastierino 4x4
 - scanner + tag RFID
 - bottoni
 - buzzer
 - ???

Utilizziamo due Raspberry ???

ipotesi:
 
 - **Raspberry 1:** raccoglie i dati dall'Arduino tramite collegamento seriale, li invia al Raspberry 2 tramite connessione Bluetooth
 - **Raspberry 2:** su un server Flask carica un'applicazione Python che presenta la Home della banca con le transizioni effettuate. Questa applicazione può essere visitata anche da smartphone, autenticandosi con un tag NFC/RFID ???
