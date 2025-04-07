import bluetooth

def run_client(server_mac_address):
    uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

    service_matches = bluetooth.find_service(uuid=uuid, address=server_mac_address)

    if not service_matches:
        print("[-] Servizio non trovato.")
        return

    first_match = service_matches[0]
    port = first_match["port"]
    host = first_match["host"]

    print(f"[*] Connessione al server {host} sulla porta {port}...")

    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((host, port))

    try:
        while True:
            message = input("[Tu]: ")
            if message.lower() == "exit":
                break
            sock.send(message)
            data = sock.recv(1024)
            print(f"[Server]: {data.decode('utf-8')}")
    except OSError:
        pass

    print("[-] Connessione terminata.")
    sock.close()

if __name__ == "__main__":
    server_mac_address = "B8:27:EB:62:DD:D0"
    run_client(server_mac_address)
