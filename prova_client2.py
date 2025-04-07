import bluetooth

server_address = "B8:27:EB:62:DD:D0"
port = 1

client_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
try:
    client_socket.connect((server_address, port))
    print("Connessione stabilita con il server")

    while True:
        message = input("Inserisci il messaggio da inviare (q per uscire): ")
        if message.lower() == 'q':
            break
        client_socket.send(message)

except OSError:
    print("Errore nella connessione")
finally:
    print("Connessione terminata")
    client_socket.close()
