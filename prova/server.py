import sqlite3
import bluetooth
import time
import serial

DB_PATH = "finanza.db"

def setup_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS transazioni (
            tipo TEXT, 
            data TEXT, 
            importo REAL, 
            descrizione TEXT
        )
    """)
    con.commit()
    con.close()

def aggiungi_transazione(t):
    parole = t.split()
    tipo, data, importo = parole[0], parole[1], float(parole[2])
    descrizione = ' '.join(parole[3:])
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(
        "INSERT INTO transazioni (tipo, data, importo, descrizione) VALUES (?, ?, ?, ?)",
        (tipo, data, importo, descrizione)
    )
    con.commit()
    con.close()

def calcolaTotale():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        SELECT 
            COALESCE(SUM(CASE WHEN tipo='entrata' THEN importo ELSE 0 END),0)
            - COALESCE(SUM(CASE WHEN tipo='uscita' THEN importo ELSE 0 END),0)
        FROM transazioni
    """)
    bilancio = cur.fetchone()[0] or 0.0
    con.close()
    return bilancio

def avvioSistema():
    setup_db()
    # Inizialmente calcola saldo
    saldo = calcolaTotale()

    # Apri seriale Arduino
    try:
        ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=0.5)
        time.sleep(2)
        print("[SERVER] Serial ready")
    except Exception as e:
        print(f"[SERVER] Errore seriale: {e}")
        return

    # Avvia server Bluetooth su porta 1
    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_sock.bind(("", 1))
    server_sock.listen(1)
    bluetooth.advertise_service(
        server_sock, "TransactionServer",
        service_id="94f39d29-7d6d-437d-973b-fba39e49d4ee",
        service_classes=[bluetooth.SERIAL_PORT_CLASS],
        profiles=[bluetooth.SERIAL_PORT_PROFILE]
    )
    print("[SERVER] In attesa Bluetooth su RFCOMM 1...")
    client_sock, addr = server_sock.accept()
    client_sock.settimeout(0.5)
    print(f"[SERVER] Connesso a {addr}")

    # Invia subito saldo iniziale come stringa
    client_sock.send(f"{saldo}".encode('utf-8'))
    time.sleep(0.5)  # aspetta un pochino per evitare collisione

    # Invia lista transazioni
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT tipo, data, importo, descrizione FROM transazioni")
    righe = cur.fetchall()
    con.close()

    # Prepara tutte le transazioni come stringhe
    transazioni = [f"{tipo} {data} {importo} {descrizione}" for tipo, data, importo, descrizione in righe]
    # Unisci tutte le transazioni separandole con il carattere speciale ###
    pacchetto = "###".join(transazioni)
    client_sock.send(pacchetto.encode('utf-8'))
    print(f"[SERVER] Inviato saldo iniziale: {saldo}")

    try:
        while True:
            saldo = calcolaTotale()
            # 1) Serial
            try:
                ser.write((str(saldo) + '\n').encode('utf-8'))
            except Exception as e:
                print(f"Errore scrittura seriale: {e}")

            try:
                line = ser.readline().decode(errors='ignore').strip()
                if line: 
                    print(f"{line}")
                    if "entrata" in line or "uscita" in line:
                        aggiungi_transazione(line)
                        saldo = calcolaTotale()
                        client_sock.send(f"{saldo}".encode('utf-8'))
            except Exception as e:
                print(f"[SERIALE] Errore: {e}")

            # 2) Bluetooth
            try:
                data = client_sock.recv(1024)
                if data:
                    stringa = data.decode(errors='ignore').strip()
                    if "entrata" in stringa or "uscita" in stringa:
                        aggiungi_transazione(stringa)
                        saldo = calcolaTotale()
                        client_sock.send(f"{saldo}".encode('utf-8'))
                        ser.write((str(calcolaTotale()) + '\n').encode('utf-8'))
            except bluetooth.btcommon.BluetoothError:
                pass

            saldo = calcolaTotale()
            try:
                client_sock.send(str(saldo).encode('utf-8'))
            except Exception as e:
                print("Terminato manualmente")

            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n[SERVER] Interrotto")

    finally:
        client_sock.close()
        server_sock.close()
        ser.close()
        print("[SERVER] Chiuso.")

if __name__ == "__main__":
    avvioSistema()
