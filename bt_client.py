import bluetooth

host = "B8:27:EB:62:DD:D0"
port = 1


print("[CLIENT] Ricerca servizi Bluetooth...")
services = bluetooth.find_service(uuid=uuid)

if not services:
    print("[CLIENT] Nessun servizio trovato.")
    exit()


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

