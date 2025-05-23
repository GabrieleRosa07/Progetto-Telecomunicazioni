
# Specifiche Tecniche Dettagliate

Questa documentazione descrive in profondità l’architettura, i componenti e il flusso di funzionamento del sistema che integra:

- Lettore RFID e tastiera fisica collegati ad Arduino

- Gestione delle transazioni e saldo su server Python

- Visualizzazione in tempo reale tramite interfaccia web (Flask + Server-Sent Events)



---

## 1. Panoramica Architetturale
```
ATM-System/
├── server.py        # Riceve da Arduino via seriale, aggiorna DB SQLite, invia dati all'app,Server Flask + SSE per mostrare transazioni live e pagina web HTML che funge da monitor ATM
├── app.py           # Implementa l'interfaccia grafica Kivy dell'home banking, comunica con il server tramite bluetooth
├── database.db      # SQLite con tabella delle transazioni
└── arduino/
    └── atm_rfid.ino # Codice per Arduino con RFID e Keypad e connessione seriale

```
**Requisiti e componenti**
  - *Due Raspberry pi*: uno collegato alla LAN
  - *Python* e tutte le librerie necessarie
  - *Arduino*: modulo RFID RC522, Keypad 4x4

**Funzionalità**
  - **Arduino**
      - Rileva RFID
      - Chiede codice PIN
      - Menu:
          - Inserisci contanti
          - Preleva contanti
          - Mostra saldo
          - Esci
      - Invia le operazioni al server tramite USB Serial
      - Riceve e mostra saldo aggiornato
        
  - **Server**
      - Legge le stringhe inviate da Arduino
      - Analizza le operazioni (entrata/uscita)
      - Salva le transazioni in SQLite
      - Ricalcola il saldo
      - Invia il nuovo saldo ad Arduino
      - Invia il saldo e ogni transazione di Arduino all'app tramite bluetooth
      - riceve dall'app le transazioni effettuate dall'home banking
      - Fornisce una pagina web con movimenti live via SSE (Server-Sent Events) per simulare il monitor dell'ATM
        
  - **App**
      - Genera l'interfaccia grafica utilizzando il framework Kivy (in modo da poter essere usato anche da smartphone)
      - Gestisce l'accesso con username e password
      - Permette la visualizzazione del saldo con la lista delle transazioni e di effettuare i movimenti (depoiti e incassi)
      - Riceve e trasmette tramite bluetooth tutte le informazioni riguardanti le transazioni effettuate sia da app che da ATM
---

## 2. Database Layer

### 2.1 Costanti e Inizializzazione

```python
DB_PATH = 'finanza.db'
# DB_PATH: percorso file SQLite.
```

### 2.2 setup_db()

```python
def setup_db():
    con = sqlite3.connect(DB_PATH)
    con.execute('''
      CREATE TABLE IF NOT EXISTS transazioni (
        tipo TEXT, data TEXT, importo REAL, descrizione TEXT
      )
    ''')
    con.commit()
    con.close()
```
Scopo: creare la tabella transazioni se non esiste.

Locking: usa la modalità di default di SQLite (serialized).

### 2.3 aggiungi_transazione(line)

```python
def aggiungi_transazione(line):
    parts = line.split()
    tipo, data_str, importo = parts[0], parts[1], float(parts[2])
    descr = ' '.join(parts[3:])
    con = sqlite3.connect(DB_PATH)
    con.execute('INSERT INTO transazioni VALUES (?,?,?,?)',
                (tipo, data_str, importo, descr))
    con.commit()
    con.close()
```
Input: stringa line formattata come "tipo data importo descrizione".

Output: nessuno (side-effect su DB).

Atomicità: ogni connect–execute–commit è transazione autonoma.

### 2.4 calcola_totale()

```python
def calcola_totale():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute('''
      SELECT
        COALESCE(SUM(CASE WHEN tipo='entrata' THEN importo ELSE 0 END),0)
      - COALESCE(SUM(CASE WHEN tipo='uscita'  THEN importo ELSE 0 END),0)
      FROM transazioni
    ''')
    saldo = cur.fetchone()[0] or 0.0
    con.close()
    return saldo
```
Scopo: ritorna entrate – uscite.

Efficienza: calcolo SQL aggregato.

---

## 3. Web Layer (Flask + SSE)

### 3.1 INDEX_HTML

```html
<!DOCTYPE html>
<html> … 
<script>
  const evtSource = new EventSource("/stream-lines");
  evtSource.onmessage = e => { … }
</script>
</html>
```
Stile: terminale ASCII—nero e verde.

Client-side: EventSource gestisce connessione SSE.

### 3.2 @app.route('/') → index()

```python
@app.route('/')
def index():
    return render_template_string(INDEX_HTML)
```
Output: pagina HTML statica.

### 3.3 @app.route('/stream-lines') → stream_lines()

```python
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
```
Generator SSE:

Tiene last come indice di lettura.

Usa lines_lock per garantire coerenza tra thread.

yield invia ogni riga come messaggio SSE.

MIME type: text/event-stream.

---

## 4. Communication Loop: Serial + Bluetooth

### 4.1 Setup iniziale

```python
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=0.5)
sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
sock.bind(('', 1)); sock.listen(1)
bluetooth.advertise_service(…)
client, addr = sock.accept(); client.settimeout(0.5)
```
Porta seriale: /dev/ttyUSB0, baud=115200.

Bluetooth RFCOMM:

bind+listen: socket server.

advertise_service: rende riconoscibile il servizio.

accept(): blocca finché non arriva client.

### 4.2 Invio Saldo e Storico

```python
client.send(f"{saldo}".encode())
time.sleep(0.2)
packet = "###".join(f"{tipo} {data} {imp} {desc}" for …)
client.send(packet.encode())
```
Formato:

Primo messaggio: solo saldo.

Secondo: pacchetto unico con separatore ###.

### 4.3 Ciclo Principale

```python
while True:
    saldo = calcola_totale()
    # Serial → invia e ricevi
    if ser:
        ser.write(f"{saldo}\n".encode())
        line = ser.readline().decode().strip()
        if line: …  # lock, DB, client.send

    # Bluetooth → ricevi e invia
    data = client.recv(1024)
    if data: …  # lock, DB, serial.write

    # invia saldo aggiornato
    client.send(f"{saldo}".encode())
    time.sleep(0.5)
```
Step:

Ricalcola saldo.

Serial:

Scrive saldo su porta.

Legge eventuale line; se presente:

Acquisisce lines_lock, append, DB insert, invia saldo al client.

Bluetooth:

Legge data; se presente: analogo a serial.

Invia saldo ogni ciclo.

sleep(0.5) regola frequenza.

---

## 5. Threading & Concorrenza

### lines Buffer:

Lista condivisa tra thread Flask e thread principale.

lines_lock (istanza threading.Lock) usato:

dal ciclo principale per append

da stream_lines() per leggere nuove righe

### Sessioni DB Multiple:

Ogni thread/operazione DB apre e chiude la propria connessione.

SQLite supporta accesso concorrente in modalità serialized.

---

## 6. Gestione Errori & Robustezza

- **Serial Init**: cattura eccezioni, setta ser=None.
- **Bluetooth I/O**: blocchi try/except attorno a send() e recv().
- **Timeout Client**: client.settimeout(0.5) per non bloccare sul recv().
- **Recupero Automatico**: loop infinito garantisce continuità—errori temporanei ignorati.

---

## 7. Sicurezza & Considerazioni Future

- **Validazione Input**: attualmente minima; aggiungere sanitizzazione di line.
- **Autenticazione Bluetooth**: implementare pairing sicuro o PIN.
- **Lock DB Migliorati**: usare WAL mode o connection pooling per scalabilità.
- **Logging & Monitoring**: integrare logging strutturato per debug e audit.
- **Test Unitari**: stub seriale/Bluetooth per test in isolamento.

---

## 8. Flusso Completo di Dati

### Avvio:

- `setup_db()`
- `app.run()` in thread separato
- `serial_bluetooth_loop()` nel main thread

### Connessione Client Bluetooth:

- Invio saldo iniziale + storico

### Ricezione Transazioni (Serial/Bluetooth):

- Aggiorna lines[] + DB
- Aggiorna saldo calcolato
- Notifica client e client seriale

### Visualizzazione Web:

- Browser si connette a `/stream-lines`
- Ogni nuova riga in `lines[]` viene pushata in tempo reale

---

## Note finali:

La separazione netta tra i thread semplifica manutenzione e permette estensioni future (es. WebSocket, API REST).

L’uso di SSE è ideale per flussi unidirezionali di log/monitoring, ma per bidirezionalità spinta valutare WebSocket.
```

