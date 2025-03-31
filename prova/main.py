import sqlite3
import bluetooth

def setup_db():
    connection = sqlite3.connect("finanza.db")
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS transazioni (tipo TEXT, data TEXT, importo REAL, descrizione TEXT)")

    connection.commit()
    connection.close()

def aggiungi_transazione():
    tipo = input("Inserisci il tipo di transazione (entrata/uscita): ")
    data = input("Inserisci la data della transazione: ")
    importo = float(input("Inserisci l'importo della transazione: "))
    descrizione = input("Inserisci la descrizione della transazione: ")

    connection = sqlite3.connect("finanza.db")
    cursor = connection.cursor()
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

# def menu():
#     setup_db()
#     while True:
#         scelta = int(input("""Seleziona un'opzione:\n
#                         1. aggiungi transazione\n
#                         2. visualizza transazioni\n
#                         3. esci """))
                
#         if(scelta == 1):
#             aggiungi_transazione()
#         elif(scelta == 2):
#             stampa()
#         elif(scelta == 3):
#             break

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

if __name__ == "__main__":
    connetti()