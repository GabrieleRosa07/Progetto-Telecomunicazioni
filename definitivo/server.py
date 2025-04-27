import threading
import time
import io
import sqlite3
import bluetooth
import serial
from PIL import Image
from flask import Flask, send_file, render_template_string

# Use a virtual display for headless operation
from pyvirtualdisplay import Display
from tkinter import Tk, Text, Scrollbar, RIGHT, LEFT, BOTH, Y, END

# Start a virtual X server before any Tkinter GUI is created
display = Display(visible=0, size=(1024, 768), backend="xvfb", use_xauth=True)
display.start()

DB_PATH = "finanza.db"

# Flask setup
template_page = """
<html>
  <head>
    <meta http-equiv="refresh" content="1">
    <title>Server Monitor</title>
  </head>
  <body style="margin:0; padding:0; overflow:hidden;">
    <img src="/snapshot.png" style="width:100vw; height:100vh; object-fit:contain;"/>
  </body>
</html>
"""
app = Flask(__name__)
latest_snapshot = None
snapshot_lock = threading.Lock()

@app.route('/')
def index():
    return render_template_string(template_page)

@app.route('/snapshot.png')
def snapshot_png():
    with snapshot_lock:
        data = latest_snapshot
    if data is None:
        img = Image.new('RGB', (1024, 768), 'black')
        buf = io.BytesIO()
        img.save(buf, 'PNG')
        buf.seek(0)
        return send_file(buf, mimetype='image/png')
    return send_file(io.BytesIO(data), mimetype='image/png')

def run_flask():
    app.run(host='0.0.0.0', port=5000, threaded=True)


def setup_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS transazioni (
            tipo TEXT,
            data TEXT,
            importo REAL,
            descrizione TEXT
        )"""
    )
    con.commit()
    con.close()


def aggiungi_transazione(t):
    parts = t.split()
    tipo, data_str, importo = parts[0], parts[1], float(parts[2])
    descrizione = ' '.join(parts[3:])
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(
        "INSERT INTO transazioni (tipo, data, importo, descrizione) VALUES (?, ?, ?, ?)",
        (tipo, data_str, importo, descrizione)
    )
    con.commit()
    con.close()


def calcola_totale():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(
        """
        SELECT
            COALESCE(SUM(CASE WHEN tipo='entrata' THEN importo ELSE 0 END), 0)
            - COALESCE(SUM(CASE WHEN tipo='uscita' THEN importo ELSE 0 END), 0)
        FROM transazioni
        """
    )
    saldo = cur.fetchone()[0] or 0.0
    con.close()
    return saldo


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
        ps = self.text.postscript(colormode='color')
        img = Image.open(io.BytesIO(ps.encode('utf-8')))
        buf = io.BytesIO()
        img.save(buf, 'PNG')
        with snapshot_lock:
            global latest_snapshot
            latest_snapshot = buf.getvalue()

    def mainloop(self):
        self.root.mainloop()


def avvio_sistema(gui: SerialMonitorGUI):
    setup_db()
    saldo = calcola_totale()

    try:
        ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=0.5)
        time.sleep(2)
    except Exception:
        ser = None

    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_sock.bind(("", 1))
    server_sock.listen(1)
    bluetooth.advertise_service(
        server_sock,
        "TransactionServer",
        service_id="94f39d29-7d6d-437d-973b-fba39e49d4ee",
        service_classes=[bluetooth.SERIAL_PORT_CLASS],
        profiles=[bluetooth.SERIAL_PORT_PROFILE]
    )
    client_sock, addr = server_sock.accept()
    client_sock.settimeout(0.5)

    client_sock.send(f"{saldo}".encode())
    time.sleep(0.5)

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT tipo, data, importo, descrizione FROM transazioni")
    rows = cur.fetchall()
    con.close()
    packet = "###".join(f"{t[0]} {t[1]} {t[2]} {t[3]}" for t in rows)
    client_sock.send(packet.encode())

    try:
        while True:
            saldo = calcola_totale()

            if ser:
                try:
                    ser.write((str(saldo) + '\n').encode())
                except Exception:
                    pass

                try:
                    line = ser.readline().decode(errors='ignore').strip()
                    if line:
                        gui.append_line(line)
                        if 'entrata' in line or 'uscita' in line:
                            aggiungi_transazione(line)
                            saldo = calcola_totale()
                            client_sock.send(f"{saldo}".encode())
                except Exception:
                    pass

            try:
                data = client_sock.recv(1024)
                if data:
                    s = data.decode(errors='ignore').strip()
                    if 'entrata' in s or 'uscita' in s:
                        aggiungi_transazione(s)
                        saldo = calcola_totale()
                        client_sock.send(f"{saldo}".encode())
                        if ser:
                            ser.write((str(saldo) + '\n').encode())
            except Exception:
                pass

            try:
                client_sock.send(f"{saldo}".encode())
            except Exception:
                pass

            time.sleep(0.5)

    except KeyboardInterrupt:
        pass

    finally:
        client_sock.close()
        server_sock.close()
        if ser:
            ser.close()

if __name__ == '__main__':
    gui = SerialMonitorGUI()
    threading.Thread(target=run_flask, daemon=True).start()
    threading.Thread(target=avvio_sistema, args=(gui,), daemon=True).start()
    gui.mainloop()
    # Stop the virtual display on exit
display.stop()