import bluetooth

# Configurazione del server
server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
port = bluetooth.PORT_ANY # Assegna una porta disponibile automaticamente
server_socket.bind(("", port))
server_socket.listen(1)

# Pubblica il servizio
bluetooth.advertise_service(
    server_socket,
    "Piserver",
    service_classes = [bluetooth.SERIAL_PORT_CLASS],
    profiles = [bluetooth.SERIAL_PORT_PROFILE],
)

print(f"Server in attesa di connessioni sulla porta {port}...")

try:
    client_socket, client_address = server_socket.accept()
    print(f"Connessione stabilita con: {client_address}")

    while True:
        data = client_socket.recv(1024).decode("utf-8")
        if data.lower() == "exit":
            print("Connessione terminata dal client.")
            break
        print(f"Ricevuto: {data}")
        client_socket.send("Messaggio ricevuto!".encode("utf-8"))
except Exception as e:
    print(f"Errore: {e}")
finally:
    client_socket.close()
    server_socket.close()
