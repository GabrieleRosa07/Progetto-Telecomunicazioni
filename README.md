# Progetto-Telecomunicazioni

## Sistema bancario
### creare un'applicazione Python che simula un sistema bancario:
Con Arduino Freenove (usiamo come base il progetto già ralizzato con Freenove):
 - tastierino 4x4 (per l'inserimento password)
 - scanner + tag RFID (per attivare le funzionalità)
 - bottoni (per selezionare l'opzione)
 - buzzer (per creare l'effetto sonoro dell'inserimento password)
 - ???

Utilizziamo due Raspberry ???

ipotesi:
 
 - **Raspberry 1:** raccoglie i dati dall'Arduino tramite collegamento seriale, li invia al Raspberry 2 tramite connessione Bluetooth. gestisce un database e un file csv contendendo tutte le transazioni. questi dati li invia a arduino e all'altro Raspberry.
 - **Raspberry 2:** su un server Flask carica un'applicazione Python che presenta la Home della banca con le transizioni effettuate. Questa applicazione può essere visitata anche da smartphone, autenticandosi con un tag NFC/RFID ???


link del canale per realizzare app grafica da pc e da smartphone: https://www.programmareinpython.it/corsi-e-lezioni-python-dal-nostro-canale-youtube/
