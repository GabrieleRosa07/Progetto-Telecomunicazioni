import bluetooth


# Creazione del socket Bluetooth
server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
server_sock.bind(("", bluetooth.PORT_ANY))
server_sock.listen(1)
print("[+] Socket bluetooth creato e in ascolto")

# Ottieni la porta
port = server_sock.getsockname()[1]
uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
print("[+] Porta relativa al socket : " + str(port))

# Pubblicazione del servizio
try:
    bluetooth.advertise_service(
        server_sock,
        "AutoAcceptServer",
        service_id=uuid,
        service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
        profiles=[bluetooth.SERIAL_PORT_PROFILE]
    )
    print("[!] Servizio disponibile all'esterno")
except bluetooth.BluetoothError as e:
    print("[-] Errore nella pubblicazione del servizio\n\t" + str(e))

while True:
    print("[ Server in attesa di connessioni dall'esterno ]")
    try:
        client_sock, client_info = server_sock.accept()
        print("[+] Client connesso : " + str(client_info))
        print("[START Chat]")
        while True:
            data = client_sock.recv(1024)
            if not data:
                break
            print("Ricevuto:", data.decode())

    except OSError:
        pass

    client_sock.close()
    print("[END Chat]")
    print("[-] Client disconnesso")
server_sock.close()
print("[Server terminato.]")

