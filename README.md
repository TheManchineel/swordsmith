# Swordsmith

Swordsmith è un programma ausiliario per registrare lezioni scolastiche mediante [OBS Studio](https://obsproject.com/) e caricarle automaticamente su [Google Drive](https://www.google.com/drive/).

Il software, costruito in Python 3 con PySimpleGUI e pydrive2, è compatibile esclusivamente con sistemi Windows a 64 bit, dotati di webcam USB (anche integrata, in quanto la maggior parte dei laptop usa internamente una webcam USB) e di un microfono. È pensato per essere totalmente portatile, quindi non richiede installazione e può essere eseguito da una chiavetta USB. Swordsmith si occupa di identificare automaticamente la webcam del computer e la directory in cui è installato, e configurare OBS Studio opportunamente, in modo da semplificare il processo di registrazione su macchine diverse.

## Installazione

Il setup di Swordsmith su una chiavetta USB o in una qualsiasi cartella prevede la creazione della seguente struttura:

```
Root/
├───START.lnk (copiare da /example/START.lnk in questa repository)
├───Registrazioni/ (cartella vuota, le registrazioni vengono salvate qui)
├───.swordsmith/ (una copia di questa repository)
├───.data/ (vedi /example/.data/ come esempio)
│   ├───config.ini (vedi sezione Configurazione)
│   └───service_account.json (vedi sezione Configurazione)
├───.obs/ (una copia di OBS Studio per Windows)
│   ├───bin/
│   │   └───64bit/
│   │       │   ...
│   │       └───obs64.exe
│   │   ...
│   └───config/...
└───.python/ (una copia di Python per Windows, testato con Python 3.10.5)
    ├───DLLs/
    │   ...
    ├───python.exe
    └───pythonw.exe
```

Python è scaricabile come file zip dal [sito ufficiale](https://www.python.org/downloads/windows/). OBS Studio è scaricabile dal [sito ufficiale](https://obsproject.com/download), anch'esso come archivio zip. Una volta estratti/installati entrambi i programmi, doverebbero avere la struttura mostrata sopra. Per quanto riguarda la cartella `.data`, è necessario creare un file `config.ini` e un file `service_account.json` (vedi sezione Configurazione).

In seguito, è necessario installare le dipendenze di Swordsmith. Per farlo, aprire un prompt dei comandi nella cartella `.python` e digitare:

```powershell
./python -m pip install -r ../.swordsmith/requirements.txt
```

Dove `../.swordsmith/requirements.txt` è il percorso del file `requirements.txt` nella cartella `.swordsmith` precedentemente predisposta.

## Configurazione

È necessario disporre di un [Google Service Account](https://developers.google.com/identity/protocols/oauth2/service-account) per poter caricare i video su Google Drive. Per crearne uno, seguire la [guida ufficiale](https://developers.google.com/identity/protocols/oauth2/service-account#creatinganaccount). Una volta creato, scaricare il file JSON contenente le credenziali e rinominarlo `service_account.json`. Copiarlo nella cartella `.data` precedentemente predisposta. Bisogna inoltre condividere la cartella in cui si vogliono caricare i video con l'indirizzo email del Service Account, e copiare l'ID della cartella in `config.ini` (vedi sotto).

Aprire il file `config.ini` nella cartella `.data` e modificare i parametri come segue:

```ini
[Drive]
root = ID-DELLA-CARTELLA-CONDIVISA
fix_missing_folders = True
archived_dir = Archiviati

[General]
language = it
user_gender = female
```

Per trovare l'ID della cartella nella quale caricare i video, aprire Google Drive nel browser ed entrare nella cartella. L'ID è l'ultima parte dell'URL, dopo `https://drive.google.com/drive/folders/` (es. qualcosa come `JtXC4Ra_CHQTqA1Nq4X`).

Se si vuole che le cartelle mancanti su Drive vengano create automaticamente, impostare `fix_missing_folders` a `True`.

È necessario definire un titolo per la cartella in cui verranno archiviati i video delle vecchie classi, ad esempio "Archiviati".

Attualmente non sono in uso i parametri `language` e `user_gender`, ma in futuro potrebbero essere utilizzati per localizzare il software.

Se si vuole predisporre Swordsmith per ricevere aggiornamenti, è possibile copiare la cartella `/example/.update` come "`.update`" nella root, nonché la shortcut `UPDATER.lnk`.

È infine consigliato impostare tutte le cartelle create (tranne `Registrazione`) come nascoste sulla chiavetta.