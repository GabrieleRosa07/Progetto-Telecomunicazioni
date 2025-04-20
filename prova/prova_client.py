import bluetooth
import pickle
import time

server_address = "B8:27:EB:62:DD:D0"

def send_transaction():
    client_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

    try:
        client_sock.connect((server_address, 1))
        print(f"[CLIENT] Connesso al server {server_address}")

        time.sleep(500)
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
        print("[CLIENT] Connessione chiusa")

if __name__ == "__main__":
    send_transaction()