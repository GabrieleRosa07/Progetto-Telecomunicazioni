import os
# Use mock window for headless Kivy (no X server)
os.environ['KIVY_WINDOW'] = 'mock'

import threading
import time
import io
import sqlite3
import bluetooth
import uuid

from kivy.app import App
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Fbo, ClearColor, ClearBuffers, Scale, Translate
from kivy.core.image import Image as CoreImage

from flask import Flask, Response, render_template_string

# Shared buffer for latest frame
current_frame = io.BytesIO()

# Flask app definition
def create_flask_app():
    app = Flask(__name__)
    html = '''
    <html>
      <head><meta http-equiv="refresh" content="1"><title>Server Monitor</title></head>
      <body style="margin:0;padding:0;overflow:hidden;">
        <img src="/stream" style="width:100vw;height:100vh;object-fit:contain;" />
      </body>
    </html>'''

    @app.route('/')
    def index():
        return render_template_string(html)

    @app.route('/stream')
    def stream():
        boundary = 'frame'
        def gen():
            while True:
                try:
                    frame = current_frame.getvalue()
                    yield (b'--%b\r\nContent-Type: image/png\r\n\r\n' % boundary.encode() + frame + b'\r\n')
                except Exception:
                    pass
                time.sleep(0.5)
        return Response(gen(), mimetype=f'multipart/x-mixed-replace; boundary={boundary}')

    return app

# Database setup
DB_PATH = 'finanza.db'
def setup_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute('''
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
    con.execute('INSERT INTO transazioni VALUES (?,?,?,?)', (tipo, data_str, importo, descr))
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
    con.close(); return saldo

# Kivy Screen to display serial log
txt_log = None
class SerialScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        global txt_log
        layout = BoxLayout(orientation='vertical')
        scroll = ScrollView()
        txt_log = Label(size_hint_y=None, markup=True)
        txt_log.bind(texture_size=lambda _, ts: setattr(txt_log, 'height', ts[1]))
        scroll.add_widget(txt_log)
        layout.add_widget(scroll)
        self.add_widget(layout)

class MonitorApp(App):
    def build(self):
        setup_db()
        # schedule capture via FBO
        Clock.schedule_interval(capture_fbo, 1/2)  # 2 fps
        # start Flask stream
        threading.Thread(target=lambda: create_flask_app().run(host='0.0.0.0', port=5000), daemon=True).start()
        # start serial and bluetooth threads
        threading.Thread(target=serial_bluetooth_loop, daemon=True).start()
        sm = ScreenManager()
        sm.add_widget(SerialScreen(name='monitor'))
        return sm

# Capture Kivy window to buffer via FBO
def capture_fbo(dt):
    fbo = Fbo(size=Window.size)
    with fbo:
        ClearColor(0,0,0,1); ClearBuffers()
        Scale(1, -1, 1); Translate(0, -Window.height, 0)
        Window.canvas.ask_update(); fbo.add(Window.canvas)
    fbo.draw()
    img = CoreImage(fbo.texture)
    buf = io.BytesIO(); img.save(buf, fmt='png'); buf.seek(0)
    global current_frame; current_frame = buf

# Serial & Bluetooth loop
def serial_bluetooth_loop():
    saldo = calcola_totale()
    try:
        ser = serial.Serial('/dev/ttyUSB0',115200,timeout=0.5)
        time.sleep(2)
    except:
        ser = None
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.bind(('',1)); sock.listen(1)
    bluetooth.advertise_service(sock,'TransServ',service_id=str(uuid.uuid4()),
                                 service_classes=[bluetooth.SERIAL_PORT_CLASS],
                                 profiles=[bluetooth.SERIAL_PORT_PROFILE])
    client, addr = sock.accept(); client.settimeout(0.5)
    client.send(f"{saldo}".encode()); time.sleep(0.5)

    # send history
    rows = sqlite3.connect(DB_PATH).cursor().execute('SELECT * FROM transazioni').fetchall()
    packet = '###'.join(f"{r[0]} {r[1]} {r[2]} {r[3]}" for r in rows)
    client.send(packet.encode())

    while True:
        saldo = calcola_totale()
        if ser:
            try: ser.write(f"{saldo}\n".encode())
            except: pass
            try:
                line = ser.readline().decode().strip()
                if line: process_line(line, client)
            except: pass
        try:
            data = client.recv(1024)
            if data: process_line(data.decode().strip(), client)
        except: pass
        try: client.send(f"{saldo}".encode())
        except: pass
        time.sleep(0.5)

# Process incoming lines
def process_line(line, client):
    global txt_log
    txt_log.text += line + '\n'
    aggiungi_transazione(line)
    saldo = calcola_totale()
    try: client.send(f"{saldo}".encode())
    except: pass

if __name__=='__main__':
    MonitorApp().run()

