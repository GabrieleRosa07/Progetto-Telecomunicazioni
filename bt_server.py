import bluetooth

# Crea socket Bluetooth RFCOMM
server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
server_sock.bind(("", bluetooth.PORT_ANY))
server_sock.listen(1)

port = server_sock.getsockname()[1]
uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

# Pubblica il servizio Bluetooth
bluetooth.advertise_service(
    server_sock,
    "RPiChat",
    service_id=uuid,
    service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
    profiles=[bluetooth.SERIAL_PORT_PROFILE]
)

print(f"[SERVER] In ascolto sulla porta {port}. Attendi connessione...")

client_sock, client_info = server_sock.accept()
print(f"[SERVER] Connesso a {client_info}")

try:
    while True:
        # Ricevi dal client
        data = client_sock.recv(1024)
        if not data:
            break
        print(f"[CLIENT]: {data.decode()}")

        # Invia al client
        reply = input("[TU (SERVER)]: ")
        client_sock.send(reply.encode())

except OSError:
    print("[SERVER] Connessione terminata.")

client_sock.close()
server_sock.close()
