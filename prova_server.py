import bluetooth

server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
port = 1
server_socket.bind(("", port))
server_socket.listen(1)

print("In attesa di connessione...")
client_socket, client_info = server_socket.accept()
print(f"Connessione stabilita con: {client_info}")

try:
    while True:
        data = client_socket.recv(1024)
        if not data:
            break
        print(f"Ricevuto: {data.decode('utf-8')}")
except OSError:
    pass

print("Connessione terminata")
client_socket.close()
server_socket.close()
