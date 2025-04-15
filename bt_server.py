import bluetooth
import uuid

server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
server_sock.bind(("", bluetooth.PORT_ANY))
server_sock.listen(1)

port = server_sock.getsockname()[1]

# UUID del servizio che vogliamo pubblicare
service_uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

bluetooth.advertise_service(
    server_sock,
    "ChatService",
    service_id=service_uuid,
    service_classes=[service_uuid, bluetooth.SERIAL_PORT_CLASS],
    profiles=[bluetooth.SERIAL_PORT_PROFILE],
)

print(f"In attesa di connessione su UUID {service_uuid}, porta {port}...")

client_sock, client_info = server_sock.accept()
print(f"Connessione accettata da {client_info}")

try:
    # Invia messaggio iniziale
    msg = "Benvenuto, client!"
    client_sock.send(msg)
    print("Messaggio inviato:", msg)

    # Ricevi risposta
    data = client_sock.recv(1024)
    print("Risposta del client:", data.decode())

except OSError as e:
    print("Errore:", e)

print("Chiusura connessione")
client_sock.close()
server_sock.close()

