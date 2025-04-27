import threading
import time
import sqlite3
import bluetooth
import serial
import uuid

from flask import Flask, Response, render_template_string

# 1) Buffer thread-safe per le ultime linee
lines = []
lines_lock = threading.Lock()

DB_PATH = 'finanza.db'

def setup_db():
    con = sqlite3.connect(DB_PATH)
    con.execute('''
        CREATE TABLE IF NOT EXISTS transazioni (
            tipo TEXT, data TEXT, importo REAL, descrizione TEXT
        )
    ''')
    con.commit(); con.close()

def aggiungi_transazione(line):
    parts = line.split()
    tipo, data_str, importo = parts[0], parts[1], float(parts[2])
    descr = ' '.join(parts[3:])
    con = sqlite3.connect(DB_PATH)
    con.execute('INSERT INTO transazioni VALUES (?,?,?,?)',
                (tipo, data_str, importo, descr))
    con.commit(); con.close()

def calcola_totale():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute('''
        SELECT COALESCE(SUM(CASE WHEN tipo='entrata' THEN importo ELSE 0 END),0)
             - COALESCE(SUM(CASE WHEN tipo='uscita' THEN importo ELSE 0 END),0)
        FROM transazioni
    ''')
    saldo = cur.fetchone()[0] or 0.0
    con.close()
    return saldo

# 2) Flask + SSE
app = Flask(__name__)

INDEX_HTML = """
<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="UTF-8">
  <title>Monitor Serial</title>
  <style> body { margin: 0; background: #000; color: #0f0; font-family: monospace; } 
           pre { padding: 1em; } </style>
</head>
<body>
  <pre id="serial-output"></pre>
  <script>
    const evtSource = new EventSource("/stream-lines");
    const out = document.getElementById("serial-output");
    evtSource.onmessage = e => {
      out.textContent += e.data + "\\n";
      out.scrollTop = out.scrollHeight;
    };
  </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(INDEX_HTML)

@app.route('/stream-lines')
def stream_lines():
    def generator():
        last = 0
        while True:
            with lines_lock:
                new = lines[last:]
            for line in new:
                yield f"data: {line}\n\n"
            last += len(new)
            time.sleep(0.2)
    return Response(generator(), mimetype='text/event-stream')

# 3) Loop seriale & Bluetooth che popola `lines`
def serial_bluetooth_loop():
    setup_db()
    saldo = calcola_totale()

    # Serial port
    try:
        ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=0.5)
        time.sleep(2)
    except:
        ser = None

    # Bluetooth server
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.bind(('', 1)); sock.listen(1)
    bluetooth.advertise_service(sock, 'TransServ',
        service_id=str(uuid.uuid4()),
        service_classes=[bluetooth.SERIAL_PORT_CLASS],
        profiles=[bluetooth.SERIAL_PORT_PROFILE]
    )
    client, addr = sock.accept(); client.settimeout(0.5)

    # Manda saldo iniziale + storico
    client.send(f"{saldo}".encode())
    time.sleep(0.2)
    rows = sqlite3.connect(DB_PATH).cursor().execute(
        'SELECT tipo,data,importo,descrizione FROM transazioni'
    ).fetchall()
    packet = "###".join(f"{r[0]} {r[1]} {r[2]} {r[3]}" for r in rows)
    client.send(packet.encode())

    while True:
        saldo = calcola_totale()
        # 3a) Serial
        if ser:
            try: ser.write(f"{saldo}\n".encode())
            except: pass
            try:
                line = ser.readline().decode().strip()
                if line:
                    with lines_lock:
                        lines.append(line)
                    aggiungi_transazione(line)
                    client.send(f"{calcola_totale()}".encode())
            except: pass

        # 3b) Bluetooth
        try:
            data = client.recv(1024)
            if data:
                line = data.decode().strip()
                with lines_lock:
                    lines.append(line)
                aggiungi_transazione(line)
                client.send(f"{calcola_totale()}".encode())
                if ser:
                    ser.write(f"{calcola_totale()}\n".encode())
        except: pass

        # invia sempre saldo aggiornato
        try: client.send(f"{saldo}".encode())
        except: pass

        time.sleep(0.5)

if __name__ == '__main__':
    # Parte Flask in thread
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000, threaded=True),
                     daemon=True).start()
    # Loop seriale
    serial_bluetooth_loop()


