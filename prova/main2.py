import bluetooth
import pickle
import sqlite3
import time
import serial

# Funzione per inizializzare il database
def setup_db():
    connection = sqlite3.connect("finanza.db")
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transazioni (
            tipo TEXT,
            data TEXT,
            importo REAL,
            descrizione TEXT
        )
    """)
    connection.commit()
    connection.close()

# Funzione per aggiungere una transazione al database
def aggiungi_transazione(t):
    connection = sqlite3.connect("finanza.db")
    cursor = connection.cursor()

    parole = t.split()
    tipo = parole[0]
    data = parole[1]
    importo = float(parole[2])
    descrizione = ' '.join(parole[3:])

    cursor.execute("INSERT INTO transazioni (tipo, data, importo, descrizione) VALUES (?, ?, ?, ?)", (tipo, data, importo, descrizione))

    connection.commit()
    connection.close()

# Funzione per stampare tutte le transazioni nel database
def stampa():
    setup_db()

    print("Transazioni attuali:\n")
    connection = sqlite3.connect("finanza.db")
    cursor = connection.cursor()
    stampa = cursor.execute("SELECT * FROM transazioni")
    
    for row in stampa:
        print(row)

# Funzione per calcolare il saldo totale
def calcolaTotale():
    connection = sqlite3.connect("finanza.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT 
            SUM(CASE WHEN tipo = 'entrata' THEN importo ELSE 0 END) - 
            SUM(CASE WHEN tipo = 'uscita' THEN importo ELSE 0 END) AS bilancio
        FROM transazioni;
    """)

    bilancio = cursor.fetchone()[0]
    connection.close()

    return str(bilancio)

# Funzione per connettere e gestire la comunicazione con Arduino
def connetti_arduino():
    try:
        # Inizializzazione della connessione seriale con Arduino
        ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
        
        # Leggere i dati da Arduino
        while True:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                if "entrata" in line or "uscita" in line:
                    aggiungi_transazione(line)  # Aggiungi la transazione se trovata
                    print(f"[SERVER] Transazione salvata: {line}")
                else:
                    print(f"[SERVER] Ignorato: {line}")  # Stampa qualunque altro messaggio

    except KeyboardInterrupt:
        print("Chiusura della connessione con Arduino")
    finally:
        ser.close()  # Chiude la connessione seriale

# Funzione per avviare il server Bluetooth e gestire la connessione
def avvio_sistema():
    setup_db()
    saldo = calcolaTotale()
    
    ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
    time.sleep(2)
    
    print("[SERVER] Avvio ATM...")
    
    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_sock.bind(("", bluetooth.PORT_ANY))
    server_sock.listen(1)
    port = server_sock.getsockname()[1]
    
    uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
    
    bluetooth.advertise_service(
        server_sock,
        "TransactionServer",
        service_id=uuid,
        service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
        profiles=[bluetooth.SERIAL_PORT_PROFILE]
    )

    print("[SERVER] In attesa di connessioni Bluetooth...")
    client_sock, client_info = server_sock.accept()
    print(f"[SERVER] Connesso a: {client_info}")
    
    try:
        while True:
            # Leggere i dati inviati dal client
            data = client_sock.recv(1024)
            if data:
                stringa = data.decode('utf-8')
                print(f"[SERVER] Dato ricevuto: {stringa}")
                
                # try:
                #     # Deserializzare i dati ricevuti
                #     transaction = pickle.loads(data)
                #     print(f"[SERVER] Transazione ricevuta: {transaction}")
                    
                #     # Aggiungere la transazione al database
                #     aggiungi_transazione(transaction)
                #     print(f"[SERVER] Transazione salvata: {transaction}")

                #     # Calcolare il saldo aggiornato
                #     saldo = calcolaTotale()
                #     print(f"[SERVER] Nuovo saldo: {saldo} €")

                #     # Inviare il saldo al client
                #     client_sock.send(pickle.dumps(saldo))

                # except pickle.UnpicklingError:
                #     print("[SERVER] Errore durante la deserializzazione dei dati")

            else:
                print("[SERVER] Connessione chiusa dal client.")
                break
    except Exception as e:
        print(f"[SERVER] Errore: {e}")
    
    finally:
        client_sock.close()
        server_sock.close()
        ser.close()
        print("[SERVER] Connessioni chiuse")

# Funzione principale per avviare il sistema
if __name__ == "__main__":
    avvio_sistema()
