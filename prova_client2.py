import bluetooth

# Indirizzo MAC del server
server_address = "B8:27:EB:62:DD:D0"  
port = 1  # Assicurati di utilizzare la stessa porta del server

# Creazione del socket client
client_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

try:
    print("Tentativo di connessione al server...")
    client_socket.connect((server_address, port))
    print("Connessione stabilita con il server.")

    while True:
        message = input("Inserisci il messaggio da inviare ('exit' per terminare): ")
        client_socket.send(message.encode("utf-8"))
        if message.lower() == "exit":
            print("Connessione terminata.")
            break
        # Ricezione della risposta dal server
        response = client_socket.recv(1024).decode("utf-8")
        print(f"Risposta dal server: {response}")
except bluetooth.btcommon.BluetoothError as e:
    print(f"Errore nella connessione: {e}")
finally:
    client_socket.close()
    print("Socket chiuso.")
