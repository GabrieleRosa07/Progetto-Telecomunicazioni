import bluetooth

# UUID del servizio a cui ci vogliamo connettere
service_uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

print("Ricerca servizi Bluetooth...")

# Trova i servizi che espongono questo UUID
services = bluetooth.find_service(uuid=service_uuid)

if len(services) == 0:
    print("Nessun servizio trovato.")
    exit()

first_match = services[0]
host = first_match["host"]
port = first_match["port"]

print(f"Trovato servizio su {host}, porta {port}")

sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
sock.connect((host, port))
print("Connesso al server!")

try:
    # Ricevi messaggio dal server
    data = sock.recv(1024)
    print("Messaggio ricevuto:", data.decode())

    # Rispondi
    response = "Ciao server, ricevuto forte e chiaro!"
    sock.send(response)
    print("Risposta inviata al server.")

except OSError as e:
    print("Errore:", e)

print("Chiusura connessione")
sock.close()