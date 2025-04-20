import bluetooth
import struct  # Aggiungi questa importazione

server_address = "B8:27:EB:62:DD:D0"

def send_transaction():
    client_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

    try:
        client_sock.connect((server_address, 1))
        print(f"[CLIENT] Connesso al server {server_address}")

        transaction = "entrata 2024-03-31 150.75 Versamento stipendio"
        serialized = struct.pack('!50s', transaction.encode('utf-8'))  # Esempio di come usare struct

        client_sock.send(serialized)
        print(f"[CLIENT] Transazione inviata: {transaction}")

        data = client_sock.recv(1024)
        saldo = struct.unpack('!d', data)  # Esempio di come usare struct per deserializzare un saldo
        print(f"[CLIENT] Saldo aggiornato ricevuto: {saldo[0]} €")

    except Exception as e:
        print(f"[CLIENT] Errore: {e}")

    finally:
        #client_sock.close()
        print("[CLIENT] Connessione chiusa")

if __name__ == "__main__":
    send_transaction()
