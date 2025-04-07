#!/usr/bin/env python3
import sys
from time import sleep

import bluetooth


addr = None

def connect_to_server(addr, name = None):
    uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
    service_matches = bluetooth.find_service(uuid=uuid, address=addr)
    # Prendo i parametri presenti nell'oggetto del servizio
    first_match = service_matches[0]
    print("[!] Servizio trovato!\n\t" + str(service_matches[0]))
    port = first_match["port"]
    name = first_match["name"]
    host = first_match["host"]

    # Create the client socket
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((host, port))

    print("Connected. Type something...")
    while True:
        data = input()
        if not data:
            break
        sock.send(data)

    sock.close()

if len(sys.argv) < 2:
    print("Nessun dispositivo specificato.")
else:
    try:
        addr = sys.argv[1]
        print("Mi connetto al server {}...".format(addr))
        connect_to_server(addr)
    except Exception as e:
        print(str(e))
        exit

wait_sec = 15
while True:
    print("--- Inizio la ricerca dei dispositivi vicini ---")
    # search for the SampleServer service
    try:
        nearby_devices = bluetooth.discover_devices(lookup_names=True, duration=5)
    except Exception as e:
        print("[/] Errore nella scansione dei dispositivi vicini\n\t" + str(e))
    finally:
        if len(nearby_devices) == 0: 
            print("[-] Nessun dispositivo trovato... aspetto 15s e riprovo")
            sleep(wait_sec)
            continue
        devices = []
        for addr, name in nearby_devices:
            try:
                tmp_dict = {"address": addr, "name": name}
                print("[!] Dispositivo trovato: " + str(tmp_dict))
                devices.append(tmp_dict)
                print("[+] Aggiunto alla lista dei dispositivi trovati")
                # Per ogni dispositivo trovato, provo a connettermi
                print("[+] Tentativo di connessione all'host...")
                connect_to_server(addr, name)
            except Exception as e:
                print("[/] Errore nell'iterazione del dispositivo")

