import bluetooth

server_mac_address = 'B8:27:EB:62:DD:D0' 
port = 1  # Stesso numero di porta del server

sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

try:
    print(f"Connessione al server {server_mac_address}...")
    sock.connect((server_mac_address, port))
    print("Connesso!")

    while True:
        message = input("Scrivi un messaggio ('exit' per terminare): ")
        if message.lower() == "exit":
            break
        sock.send(message)

except bluetooth.btcommon.BluetoothError as err:
    print(f"Errore di connessione: {err}")

finally:
    print("Disconnessione...")
    sock.close()


