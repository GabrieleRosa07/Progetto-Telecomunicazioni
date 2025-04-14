import bluetooth

server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
server_sock.bind(("", bluetooth.PORT_ANY))
server_sock.listen(1)

print("In attesa di connessioni Bluetooth...")
client_sock, client_info = server_sock.accept()
print(f"Connessione accettata da {client_info}")

while True:
    data = client_sock.recv(1024)
    if not data:
        break
    print(f"Ricevuto: {data.decode()}")

client_sock.close()
server_sock.close()
