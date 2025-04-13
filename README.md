# Progetto-Telecomunicazioni: Sistema Bancario Interattivo

## Introduzione

Questo progetto dimostrativo simula un sistema bancario avanzato, integrando interazione fisica tramite Arduino e un'interfaccia web dinamica su Raspberry Pi. L'obiettivo è creare un'esperienza utente completa, dalla gestione dell'autenticazione tramite RFID e password, alla visualizzazione delle transazioni e all'esecuzione di operazioni bancarie tramite un'applicazione web accessibile anche da smartphone.

## Architettura del Sistema

Il sistema è composto da:

* **Arduino Freenove**:
    * Funge da interfaccia utente fisica, gestendo l'inserimento della password tramite tastierino 4x4, l'autenticazione tramite scanner RFID, la selezione delle operazioni tramite bottoni e il feedback sonoro tramite buzzer.
* **Raspberry Pi (x2)**:
    * **Raspberry Pi 1**:
        * Raccoglie i dati dall'Arduino tramite comunicazione seriale.
        * Invia i dati al Raspberry Pi 2 tramite connessione Bluetooth.
        * Gestisce un database locale e un file CSV per la registrazione delle transazioni.
        * Invia aggiornamenti di stato all'Arduino e al Raspberry Pi 2.
    * **Raspberry Pi 2**:
        * Ospita un server Flask che esegue un'applicazione web Python.
        * L'applicazione web presenta la home page della banca, visualizza le transazioni e consente l'esecuzione di operazioni bancarie.
        * L'applicazione è accessibile anche da smartphone, con autenticazione tramite tag NFC/RFID.

## Flusso di Lavoro

1.  **Autenticazione**:
    * L'utente si autentica tramite RFID e inserisce la password sul tastierino Arduino.
    * I dati di autenticazione vengono inviati al Raspberry Pi 1 per la verifica.
2.  **Selezione Operazione**:
    * L'utente seleziona l'operazione desiderata tramite i bottoni sull'Arduino.
    * L'operazione selezionata viene inviata al Raspberry Pi 1.
3.  **Elaborazione Transazione**:
    * Il Raspberry Pi 1 elabora la transazione, aggiorna il database e invia i dati al Raspberry Pi 2.
4.  **Visualizzazione Web**:
    * Il Raspberry Pi 2 visualizza le transazioni aggiornate sull'applicazione web.
    * L'utente può visualizzare il saldo e la cronologia delle transazioni, ed effettuare operazioni bancarie tramite l'interfaccia web.

## Tecnologie Utilizzate

* **Arduino**:
    * Linguaggio C/C++.
    * Librerie per la gestione di tastierino, RFID, bottoni e buzzer.
* **Raspberry Pi**:
    * Python 3.x.
    * Librerie: Flask, customtkinter, tkcalendar, pyserial, bluetooth, pickle.
    * database locale.
* **Comunicazione**:
    * Comunicazione seriale (Arduino - Raspberry Pi 1).
    * Comunicazione Bluetooth (Raspberry Pi 1 - Raspberry Pi 2).
    * NFC/RFID.

## Configurazione e Esecuzione

1.  **Configurazione Arduino**:
    * Collegare i componenti hardware all'Arduino.
    * Caricare il codice Arduino sull'Arduino.
2.  **Configurazione Raspberry Pi**:
    * Installare Python 3.x e le librerie necessarie su entrambi i Raspberry Pi.
    * Configurare la comunicazione seriale e Bluetooth.
    * configurare il database.
    * configurare flask.
3.  **Esecuzione Applicazione**:
    * Avviare gli script Python sui Raspberry Pi.
    * Accedere all'applicazione web tramite browser o smartphone.

## Codice di esempio.

* Comunicazione Bluetooth tra raspberry pi.
* interfaccia grafica per la gestione delle operazioni bancarie.
* invio di transazioni tramite bluetooth.

## Autori

* \[I tuoi dati]

## Licenza

* \[La licenza del tuo progetto]

## Contributi

* \[Eventuali informazioni sui contributi]

## Risorse aggiuntive

* [link del canale per realizzare app grafica da pc e da smartphone](https://www.programmareinpython.it/corsi-e-lezioni-python-dal-nostro-canale-youtube/)

## Note

* Questo progetto è una simulazione a scopo didattico.
* L'implementazione finale può variare in base alle specifiche esigenze.

Spero che questa versione del README sia più adatta alla tua presentazione!
