import sqlite3
#import bluetooth
import time
import serial

def setup_db():
    connection = sqlite3.connect("finanza.db")
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS transazioni (tipo TEXT, data TEXT, importo REAL, descrizione TEXT)")

    connection.commit()
    connection.close()

# def aggiungi_transazione():
#     tipo = input("Inserisci il tipo di transazione (entrata/uscita): ")
#     data = input("Inserisci la data della transazione: ")
#     importo = float(input("Inserisci l'importo della transazione: "))
#     descrizione = input("Inserisci la descrizione della transazione: ")

#     connection = sqlite3.connect("finanza.db")
#     cursor = connection.cursor()
#     cursor.execute("INSERT INTO transazioni (tipo, data, importo, descrizione) VALUES (?, ?, ?, ?)", (tipo, data, importo, descrizione))
#     connection.commit()
#     connection.close()

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

def stampa():
    setup_db()

    print("Transazioni attuali:\n")
    connection = sqlite3.connect("finanza.db")
    cursor = connection.cursor()
    stampa = cursor.execute("SELECT * FROM transazioni")
    
    for row in stampa:
        print(row)

def menu():
    setup_db()
    while True:
        scelta = int(input("""Seleziona un'opzione:\n
                        1. aggiungi transazione\n
                        2. visualizza transazioni\n
                        3. visualizza saldo\n
                        4. esci """))
                
        if(scelta == 1):
            aggiungi_transazione()
        elif(scelta == 2):
            stampa()
        elif(scelta == 3):
            calcolaTotale()
        elif(scelta == 4):
            break

def conetti():
    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_sock.bind(("", bluetooth.PORT_ANY))
    server_sock.listen(1)

    port = server_sock.getsockname()[1]
    uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

    try:
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

        while True:
            data = client_sock.recv(1024)
            if not data:
                break
            transaction = pickle.loads(data)
            print(f"[SERVER] Errore: {e}")

    except Exception as e:
        print(f"[SERVER] Errore: {e}")

    finally:
        client_sock.close()
        server_sock.close()
        print("[SERVER] Chiuso.")

def calcolaTotale():
    connection = sqlite3.connect("finanza.db")
    cursor = connection.cursor()

    cursor.execute("""SELECT 
                        SUM(CASE WHEN tipo = 'entrata' THEN importo ELSE 0 END) - 
                        SUM(CASE WHEN tipo = 'uscita' THEN importo ELSE 0 END) AS bilancio
                    FROM transazioni;""")

    bilancio = cursor.fetchone()[0]

    connection.close()

    return str(bilancio)

def connettiArduino():
    try:
        while True:
            line = ser.readline().decode('utf-8').strip()
            if line:
                if("entrata" in line or "uscita" in line):
                    aggiungi_transazione(line)
                else:
                    print(f"{line}")
    except KeyboardInterrupt:
        print("chiusura della connessione")
    finally:
        ser.close()


if __name__ == "__main__":
    ser = serial.Serial('COM3', 115200, timeout=1)

    if ser.is_open:
        print("Avvio ATM...")
        time.sleep(2)  # Aspetta che Arduino completi il reset

    for _ in range(5):  # Invia più volte per sicurezza
        saldo = calcolaTotale()
        ser.write((saldo + '\n').encode('utf-8'))
        time.sleep(1)

    print("Avvicina Tessera")

    #connetti()
    connettiArduino()
    stampa()

    ser.close()
