import sqlite3
import bluetooth
import time
import serial
import pickle

DB_PATH = "finanza.db"

# ----------------------------- DATABASE -----------------------------

def setup_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS transazioni (
            tipo TEXT,
            data TEXT,
            importo REAL,
            descrizione TEXT
        )
    """)
    conn.commit()
    conn.close()

def aggiungi_transazione(t):
    parole = t.split()
    if len(parole) < 4:
        print(f"[SERVER] Formato transazione non valido: {t}")
        return

    tipo = parole[0]
    data = parole[1]
    try:
        importo = float(parole[2])
    except ValueError:
        print(f"[SERVER] Importo non valido: {parole[2]}")
        return

    descrizione = ' '.join(parole[3:])

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO transazioni (tipo, data, importo, descrizione) VALUES (?, ?, ?, ?)",
                (tipo, data, importo, descrizione))
    conn.commit()
    conn.close()
    print(f"[SERVER] Transazione salvata: {t}")

def calcola_totale():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            SUM(CASE WHEN tipo = 'entrata' THEN importo ELSE 0 END) -
            SUM(CASE WHEN tipo = 'uscita' THEN importo ELSE 0 END)
        FROM transazioni
    """)
    result = cur.fetchone()
    conn.close()
    saldo = result[0] if result[0] is not None else 0.0
    return round(saldo, 2)

# -------------------------- BLUETOOTH SERVER --------------------------

def avvia_bluetooth_server(ser):
    setup_db()

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

    print(f"[SERVER] In ascolto sulla porta {port}")
    print("[SERVER] In attesa di connessioni Bluetooth...")

    try:
        client_sock, client_info = server_sock.accept()
        print(f"[SERVER] Connesso a: {client_info}")

        while True:
            # Leggi da Arduino
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                print(f"[SERVER] Dato ricevuto da Arduino: {line}")
                if "entrata" in line or "uscita" in line:
                    aggiungi_transazione(line)
                    saldo = calcola_totale()
                    print(f"[SERVER] Saldo aggiornato: {saldo} €")
                    client_sock.send(pickle.dumps(saldo))
                else:
                    print(f"[SERVER] Ignorato: {line}")

            # Leggi eventuali dati dal client Bluetooth
            client_sock.settimeout(0.01)
            try:
                data = client_sock.recv(1024)
                if data:
                    messaggio = pickle.loads(data)
                    print(f"[SERVER] Ricevuto da client: {messaggio}")
                    aggiungi_transazione(messaggio)
                    saldo = calcola_totale()
                    client_sock.send(pickle.dumps(saldo))
            except bluetooth.BluetoothError:
                pass

    except Exception as e:
        print(f"[SERVER] Errore: {e}")

    finally:
        client_sock.close()
        server_sock.close()
        ser.close()
        print("[SERVER] Connessioni chiuse.")

# -------------------------- AVVIO SISTEMA --------------------------

def avvio_sistema():
    print("[SERVER] Avvio ATM...")
    try:
        ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
        time.sleep(2)
    except serial.SerialException as e:
        print(f"[SERVER] Errore apertura porta seriale: {e}")
        return

    # Invia inizialmente il saldo ad Arduino
    saldo = str(calcola_totale())
    for _ in range(3):
        ser.write((saldo + '\n').encode('utf-8'))
        time.sleep(0.5)

    print("[SERVER] Avvicina Tessera o invia dati Bluetooth")
    avvia_bluetooth_server(ser)

# -------------------------- MAIN --------------------------

if __name__ == "__main__":
    avvio_sistema()
