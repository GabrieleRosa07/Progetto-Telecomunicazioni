import bluetooth
import uuid

# Genera un UUID specifico per il servizio
service_uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
server_sock.bind(("", bluetooth.PORT_ANY))
server_sock.listen(1)

bluetooth.advertise_service(server_sock, "RaspberryPiService",
                            service_id=service_uuid,
                            service_classes=[service_uuid, bluetooth.SERIAL_PORT_CLASS],
                            profiles=[bluetooth.SERIAL_PORT_PROFILE])

print(f"Server in attesa di connessioni... (UUID: {service_uuid})")

client_sock, client_info = server_sock.accept()
print(f"Connessione accettata da {client_info}")

while True:
    data = client_sock.recv(1024)
    if not data:
        break
    print(f"Ricevuto: {data.decode()}")

client_sock.close()
server_sock.close()
