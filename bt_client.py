import bluetooth
import uuid

service_uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"  # Deve essere lo stesso del server

# Scansiona i dispositivi Bluetooth per trovare il server
nearby_devices = bluetooth.discover_devices(duration=8, lookup_names=True)

server_address = None

print("Dispositivi Bluetooth trovati:")
for addr, name in nearby_devices:
    print(f"{addr} - {name}")
    # Supponiamo che il server sia chiamato "RaspberryPiServer", cambialo in base alle tue esigenze
    if "RaspberryPiServer" in name:
        server_address = addr
        break

if server_address is None:
    print("Server non trovato. Assicurati che sia visibile.")
    exit()

print(f"Connessione al server con indirizzo: {server_address}")

client_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
client_sock.connect((server_address, 1))

print("Connessione stabilita!")

client_sock.send("Ciao! Questo messaggio usa UUID.".encode())

client_sock.close()




