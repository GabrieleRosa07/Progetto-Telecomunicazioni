import bluetooth

server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
server_sock.bind(("", bluetooth.PORT_ANY))
server_sock.listen(1)

port = server_sock.getsockname()[1]
print(f"[SERVER] In ascolto sulla porta {port}")

bluetooth.advertise_service(
    server_sock,
    "SimpleServer",
    service_classes=[bluetooth.SERIAL_PORT_CLASS],
    profiles=[bluetooth.SERIAL_PORT_PROFILE]
)

print("[SERVER] In attesa di connessioni Bluetooth...")
client_sock, client_info = server_sock.accept()
print(f"[SERVER] Connesso a: {client_info}")

try:
    while True:
        data = client_sock.recv(1024)
        if not data:
            print("[SERVER] Connessione chiusa dal client.")
            break
        print(f"[SERVER] Dato ricevuto: {data.decode()}")
except Exception as e:
    print(f"[SERVER] Errore: {e}")
finally:
    client_sock.close()
    server_sock.close()
    print("[SERVER] Connessioni chiuse.")

