import sqlite3

def setup_db():
    connection = sqlite3.connect("finanza.db")
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS transazioni (tipo TEXT, data TEXT, importo REAL)")

    connection.commit()
    connection.close()

def aggiungi_transazione():
    tipo = input("Inserisci il tipo di transazione (entrata/uscita): ")
    data = input("Inserisci la data della transazione: ")
    importo = float(input("Inserisci l'importo della transazione: "))

    connection = sqlite3.connect("finanza.db")
    cursor = connection.cursor()
    cursor.execute("INSERT INTO transazioni (tipo, data, importo) VALUES (?, ?, ?)", (tipo, data, importo))
    connection.commit()
    connection.close()

def stampa():
    setup_db()

    print("Transazioni attuali:\n")
    connection = sqlite3.connect("finanza.db")
    cursor = connection.cursor()
    stampa = cursor.execute("SELECT * FROM transazioni")
    
    for row in stampa:
        print(row)

def menu():
    setup_db()
    while True:
        scelta = int(input("""Seleziona un'opzione:\n
                        1. aggiungi transazione\n
                        2. visualizza transazioni\n
                        3. esci """))
                
        if(scelta == 1):
            aggiungi_transazione()
        elif(scelta == 2):
            stampa()
        elif(scelta == 3):
            break

if __name__ == "__main__":
    menu()