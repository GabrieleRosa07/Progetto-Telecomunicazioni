import bluetooth

# UUID del servizio cercato
uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

print("[CLIENT] Ricerca servizi Bluetooth...")
services = bluetooth.find_service(uuid=uuid)

if not services:
    print("[CLIENT] Nessun servizio trovato.")
    exit()

# Connessione al primo servizio trovato
service = services[0]
host = service["host"]
port = service["port"]

print(f"[CLIENT] Connessione a {host} sulla porta {port}...")

sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
sock.connect((host, port))

try:
    while True:
        # Invia messaggio
        msg = input("[TU (CLIENT)]: ")
        sock.send(msg.encode())

        # Riceve risposta
        data = sock.recv(1024)
        print(f"[SERVER]: {data.decode()}")

except OSError:
    print("[CLIENT] Connessione chiusa.")

sock.close()

