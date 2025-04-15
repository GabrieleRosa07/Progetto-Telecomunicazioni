import bluetooth
import uuid

# MAC address del dispositivo server (sostituisci con quello corretto)
target_address = "B8:27:EB:62:DD:D0"  # Es: "00:1A:7D:DA:71:13"

# UUID del servizio da cercare
service_uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

# Trova il servizio Bluetooth sul dispositivo target (server)
services = bluetooth.find_service(uuid=service_uuid, address=target_address)

if not services:
    print("Servizio non trovato!")
    exit()

# Se il servizio è trovato, ottieni la porta e l'indirizzo del servizio
first_match = services[0]
port = first_match["port"]
host = first_match["host"]

print(f"Servizio trovato su {host}:{port}")

# Connessione al server utilizzando l'indirizzo MAC e la porta
sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
sock.connect((host, port))

# Ricevi i dati dal server
data = sock.recv(1024)
print(f"Ricevuto dal server: {data.decode()}")

# Invia una risposta al server
sock.send("Ciao dal client!")

# Chiudi la connessione
sock.close()
