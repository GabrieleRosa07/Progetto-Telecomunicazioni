import bluetooth

server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
port = 1  # Standard RFCOMM port

try:
    server_socket.bind(("", port))
    server_socket.listen(1)

    print("In attesa di connessione Bluetooth su RFCOMM...")

    client_socket, client_address = server_socket.accept()
    print(f"Connessione stabilita con: {client_address}")

    while True:
        data = client_socket.recv(1024)
        if not data:
            break
        print(f"Messaggio ricevuto: {data.decode('utf-8')}")

except OSError as e:
    print(f"Errore: {e}")

finally:
    print("Chiusura socket...")
    client_socket.close()
    server_socket.close()
