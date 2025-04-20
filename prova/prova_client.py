import bluetooth
import pickle


server_address = "B8:27:EB:62:DD:D0"

def send_transaction():
    client_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

    try:
        client_sock.connect((server_address, 1))
        print(f"[CLIENT] Connesso al server {server_address}")

        transaction = "entrata 2024-04-20 200.00 Pagamento freelance"
        serialized = pickle.dumps(transaction)

        # Invia prima la lunghezza (4 byte), poi i dati
        client_sock.send(struct.pack(">I", len(serialized)))
        client_sock.send(serialized)

        print(f"[CLIENT] Transazione inviata: {transaction}")

        # Ricevi la risposta (lunghezza + dati)
        raw_len = client_sock.recv(4)
        if not raw_len:
            raise Exception("Nessuna risposta dal server.")
        data_len = struct.unpack(">I", raw_len)[0]
        data = client_sock.recv(data_len)

        saldo = pickle.loads(data)
        print(f"[CLIENT] Saldo aggiornato ricevuto: {saldo} €")
    
    except Exception as e:
        print(f"[CLIENT] Errore: {e}")

    finally:
        client_sock.close()
        print("[CLIENT] Connessione chiusa")

if __name__ == "__main__":
    send_transaction()