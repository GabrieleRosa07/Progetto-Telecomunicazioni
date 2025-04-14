import bluetooth

server_address = "D8:3A:DD:ED:86:AE"  # Inserisci l'indirizzo MAC del Raspberry server

client_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
client_sock.connect((server_address, 1))

print("Connessione avviata al server!")

client_sock.send("Ciao Raspberry!".encode())

client_sock.close()



