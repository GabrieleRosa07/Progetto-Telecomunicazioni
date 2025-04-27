import threading
import time
import io
import sqlite3
import bluetooth
import serial
from tkinter import Tk, Text, Scrollbar, RIGHT, LEFT, BOTH, Y, END
from PIL import Image
from flask import Flask, send_file, render_template_string

DB_PATH = "finanza.db"

app = Flask(__name__)
latest_snapshot = None
snapshot_lock = threading.Lock()

HTML_PAGE = """
<html>
  <head><meta http-equiv="refresh" content="1"><title>Server Monitor</title></head>
  <body style="margin:0; padding:0; overflow:hidden;">
    <img src="/snapshot.png" style="width:100vw; height:100vh; object-fit:contain;"/>
  </body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/snapshot.png')
def snapshot_png():
    with snapshot_lock:
        data = latest_snapshot
    if data is None:
        # placeholder nera
        img = Image.new('RGB', (800,600), 'black')
        buf = io.BytesIO()
        img.save(buf, 'PNG'); buf.seek(0)
        return send_file(buf, mimetype='image/png')
    return send_file(io.BytesIO(data), mimetype='image/png')

def run_flask():
    app.run(host='0.0.0.0', port=5000, threaded=True)


def setup_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS transazioni (
            tipo TEXT, 
            data TEXT, 
            importo REAL, 
            descrizione TEXT
        )
    """)
    con.commit()
    con.close()

def aggiungi_transazione(t):
    parole = t.split()
    tipo, data, importo = parole[0], parole[1], float(parole[2])
    descrizione = ' '.join(parole[3:])
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(
        "INSERT INTO transazioni (tipo, data, importo, descrizione) VALUES (?, ?, ?, ?)",
        (tipo, data, importo, descrizione)
    )
    con.commit()
    con.close()

def calcolaTotale():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        SELECT 
            COALESCE(SUM(CASE WHEN tipo='entrata' THEN importo ELSE 0 END),0)
            - COALESCE(SUM(CASE WHEN tipo='uscita' THEN importo ELSE 0 END),0)
        FROM transazioni
    """)
    bilancio = cur.fetchone()[0] or 0.0
    con.close()
    return bilancio

class SerialMonitorGUI:
    def __init__(self):
        self.root = Tk()
        self.root.title("Server Serial Monitor")
        self.text = Text(self.root, wrap='none')
        sb = Scrollbar(self.root, command=self.text.yview)
        self.text.configure(yscrollcommand=sb.set)
        sb.pack(side=RIGHT, fill=Y)
        self.text.pack(side=LEFT, fill=BOTH, expand=True)

    def append_line(self, line: str):
        self.text.insert(END, line + "\n")
        self.text.see(END)
        self.capture_snapshot()

    def capture_snapshot(self):
        # Genera PostScript e converte in PNG via PIL
        ps = self.text.postscript(colormode='color')
        img = Image.open(io.BytesIO(ps.encode('utf-8')))
        buf = io.BytesIO()
        img.save(buf, 'PNG')
        with snapshot_lock:
            global latest_snapshot
            latest_snapshot = buf.getvalue()

    def mainloop(self):
        self.root.mainloop()


def avvioSistema(gui: SerialMonitorGUI):
    setup_db()
    # Inizialmente calcola saldo
    saldo = calcolaTotale()

    # Apri seriale Arduino
    try:
        ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=0.5)
        time.sleep(2)
    except Exception as e:
        return

    # Avvia server Bluetooth su porta 1
    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_sock.bind(("", 1))
    server_sock.listen(1)
    bluetooth.advertise_service(
        server_sock, "TransactionServer",
        service_id="94f39d29-7d6d-437d-973b-fba39e49d4ee",
        service_classes=[bluetooth.SERIAL_PORT_CLASS],
        profiles=[bluetooth.SERIAL_PORT_PROFILE]
    )
    client_sock, addr = server_sock.accept()
    client_sock.settimeout(0.5)

    # Invia subito saldo iniziale come stringa
    client_sock.send(f"{saldo}".encode('utf-8'))
    time.sleep(0.5)  # aspetta un pochino per evitare collisione

    # Invia lista transazioni
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT tipo, data, importo, descrizione FROM transazioni")
    righe = cur.fetchall()
    con.close()

    # Prepara tutte le transazioni come stringhe
    transazioni = [f"{tipo} {data} {importo} {descrizione}" for tipo, data, importo, descrizione in righe]
    # Unisci tutte le transazioni separandole con il carattere speciale ###
    pacchetto = "###".join(transazioni)
    client_sock.send(pacchetto.encode('utf-8'))

    try:
        while True:
            saldo = calcolaTotale()
            # 1) Serial
            try:
                ser.write((str(saldo) + '\n').encode('utf-8'))
            except Exception as e:
                pass

            try:
                line = ser.readline().decode(errors='ignore').strip()
                if line: 
                    gui.append_line(line)                   
                    if "entrata" in line or "uscita" in line:
                        aggiungi_transazione(line)
                        saldo = calcolaTotale()
                        client_sock.send(f"{saldo}".encode('utf-8'))
            except Exception as e:
                pass

            # 2) Bluetooth
            try:
                data = client_sock.recv(1024)
                if data:
                    stringa = data.decode(errors='ignore').strip()
                    if "entrata" in stringa or "uscita" in stringa:
                        aggiungi_transazione(stringa)
                        saldo = calcolaTotale()
                        client_sock.send(f"{saldo}".encode('utf-8'))
                        ser.write((str(calcolaTotale()) + '\n').encode('utf-8'))
            except bluetooth.btcommon.BluetoothError:
                pass

            saldo = calcolaTotale()
            try:
                client_sock.send(str(saldo).encode('utf-8'))
            except Exception as e:
                pass

            time.sleep(0.5)

    except KeyboardInterrupt:
        pass

    finally:
        client_sock.close()
        server_sock.close()
        ser.close()

if __name__ == "__main__":
    gui = SerialMonitorGUI()

    threading.Thread(target=run_flask, daemon=True).start()
    threading.Thread(target=avvioSistema, args=(gui,), daemon=True).start()
    gui.mainloop()
