import bluetooth
import pickle

server_address = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

def send_transaction():
    client_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

    try:
        client_sock.connect((server_address, 1))
        print(f"[CLIENT] Connesso al server {server_address}")

        transaction = "Deposito 2024-03-31 150.75 Versamento stipendio"
        serialized = pickle.dumps(transaction)
        client_sock.send(serialized)
        print(f"[CLIENT] Transazione inviata: {transaction}")

        data = client_sock.recv(1024)
        saldo = pickle.loads(data)
        print(f"[CLIENT] Saldo aggiornato ricevuto: {saldo} €")

    except Exception as e:
        print(f"[CLIENT] Errore: {e}")

    finally:
        client_sock.close()
        print("[CLIENT] Connessione chiusa.")

if __name__ == "__main__":
    send_transaction()