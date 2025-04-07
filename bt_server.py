import bluetooth
import pickle

def start_server():
    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_sock.bind(("", bluetooth.PORT_ANY))
    server_sock.listen(1)

    port = server_sock.getsockname()[1]
    print(f"[SERVER] In ascolto sulla porta RFCOMM {port}")

    uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

    try:
	print("[SERVER] Pronto a pubblicare il servizio")
    	bluetooth.advertise_service(
            server_sock,
	    "TransactionServer",
            service_id=uuid,
	    service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
            profiles=[bluetooth.SERIAL_PORT_PROFILE]
	)

	print("[SERVER] Servizio pubblicato con successo")

    except Exception as e:
	print("[SERVER] Errore")

    print("[SERVER] In attesa di connessioni...")

    client_sock, client_info = server_sock.accept()
    print(f"[SERVER] Connesso a {client_info}")

    try:
        data = client_sock.recv(1024)
        if data:
            msg = pickle.loads(data)
            print(f"[SERVER] Ricevuto: {msg}")

            saldo = 999.99  # esempio
            client_sock.send(pickle.dumps(saldo))
            print(f"[SERVER] Inviato saldo: {saldo}")

    except Exception as e:
        print(f"[SERVER] Errore: {e}")

    finally:
        client_sock.close()
        server_sock.close()
        print("[SERVER] Connessione chiusa")

if __name__ == "__main__":
    start_server()
