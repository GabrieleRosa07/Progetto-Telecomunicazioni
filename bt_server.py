import bluetooth
import uuid

# Creazione del socket Bluetooth per il server
server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

# Lega il socket a una porta specifica
server_sock.bind(("", bluetooth.PORT_ANY))
server_sock.listen(1)

# UUID per il servizio Bluetooth
service_uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

# Pubblica il servizio Bluetooth in ascolto per connessioni
bluetooth.advertise_service(
    server_sock,
    "TestServer",
    service_id=service_uuid,
    service_classes=[service_uuid, bluetooth.SERIAL_PORT_CLASS],
    profiles=[bluetooth.SERIAL_PORT_PROFILE],
)

print("Server in attesa di connessione...")

# Attende una connessione da un client
client_sock, address = server_sock.accept()
print(f"Connessione stabilita con {address}")

# Invio di un messaggio al client
client_sock.send("Ciao dal server!\n")

# Riceve il messaggio dal client
data = client_sock.recv(1024)
print(f"Ricevuto dal client: {data.decode()}")

# Chiude la connessione
client_sock.close()
server_sock.close()

