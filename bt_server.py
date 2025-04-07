import bluetooth

def run_server():
    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_sock.bind(("", bluetooth.PORT_ANY))
    server_sock.listen(1)

    port = server_sock.getsockname()[1]
    uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

    bluetooth.advertise_service(
        server_sock,
        "EchoServer",
        service_id=uuid,
        service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
        profiles=[bluetooth.SERIAL_PORT_PROFILE],
    )

    print(f"[*] In attesa di connessioni su porta {port}...")

    client_sock, client_info = server_sock.accept()
    print(f"[+] Connessione accettata da {client_info}")

    try:
        while True:
            data = client_sock.recv(1024)
            if not data:
                break
            print(f"[Client]: {data.decode('utf-8')}")
            response = input("[Tu]: ")
            client_sock.send(response)
    except OSError:
        pass

    print("[-] Connessione terminata.")
    client_sock.close()
    server_sock.close()

if __name__ == "__main__":
    run_server()
