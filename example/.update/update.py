import PySimpleGUI as sg
import validators
import os
from validators import ValidationFailure
from pathlib import Path
from shutil import rmtree
from urllib import request
from zipfile import ZipFile
from zc.lockfile import LockFile, LockError

sg.theme("Dark Black")

# set cwd to script's directory
os.chdir(os.path.dirname(os.path.realpath(__file__)))
# create "../.swordsmith" directory if it doesn't exist
Path("../.swordsmith").mkdir(parents=True, exist_ok=True)


# check if program is running and cancel if it is
def check_and_obtain_lock() -> LockFile:
    try:
        lock_path = Path(__file__).parents[1] / ".swordsmith" / "lock"
        lock = LockFile(lock_path.absolute())
        return lock
    except LockError:
        sg.popup("Devi prima chiudere il programma per aggiornare!")
        exit(1)


def do_update(url) -> str:
    global lock
    if isinstance(validators.url(url), ValidationFailure):
        return "invalid_url"
    else:
        # download the new version of Swordsmith
        try:
            request.urlretrieve(url, "./new_swordsmith.zip")
        except Exception:
            return "download_error"
        # unlock the lockfile
        lock.close()
        # unzip the new version of Swordsmith to ./new_swordsmith
        with ZipFile("./new_swordsmith.zip", "r") as zip_ref:
            zip_ref.extractall("./new_swordsmith")
        # if "./new_swordsmith" contains ".exec_only" file, only execute "post_update.py"
        if Path("./new_swordsmith/.exec_only").exists():
            # move "./new_swordsmith/post_update.py" to "../.swordsmith/post_update.py"
            Path("./new_swordsmith/post_update.py").rename("../.swordsmith/post_update.py")
            # delete the "new_swordsmith" directory
            rmtree("./new_swordsmith")
        else:
            # if there's a directory "backup" in the current directory, delete it
            if Path("./backup").exists():
                rmtree("./backup")
            # move ../.swordsmith to ./backup
            Path("../.swordsmith").rename("./backup")
            # move ./new_swordsmith to ../.swordsmith
            Path("./new_swordsmith").rename("../.swordsmith")

        # delete the zip file
        Path("./new_swordsmith.zip").unlink()
        # if there's a post_update.py file in the new version of Swordsmith, run it
        if Path("../.swordsmith/post_update.py").exists():
            os.chdir("../.swordsmith")
            os.system("powershell ../.python/python.exe ./post_update.py")
            # delete the post_update.py file
            Path("./post_update.py").unlink()
        return "success"


def do_restore() -> str:
    # if there's a backup, move it to ../.swordsmith, and make ../.swordsmith the new backup
    if Path("backup").exists():
        # unlock the lockfile
        lock.close()
        Path("../.swordsmith").rename("./backup_old")
        Path("backup").rename("../.swordsmith")
        Path("backup_old").rename("backup")
        return "success"
    else:
        return "no_backup"


def update_swordsmith_from_remote():
    global lock
    update_window_layout = [
        [sg.Text("Aggiorna Swordsmith", font=("Helvetica", 16))],
        [sg.Text("Per aggiornare a una nuova versione del software, inserisci l'URL dell'aggiornamento:")],
        [
            sg.InputText(key="url"),
        ],
        [
            sg.Button("Aggiorna", key="update", button_color=("white", "green"), size=(16, 1)),
            sg.Button("Annulla", key="cancel", size=(16, 1)),
            sg.Button(
                "Ripristina la versione precedente",
                key="restore",
                button_color=("white", "blue"),
                size=(24, 1),
            ),
        ],
    ]
    lock = check_and_obtain_lock()
    window = sg.Window("Aggiorna Swordsmith", layout=update_window_layout, auto_size_text=True)
    while True:
        event, value = window.read()
        if event in ("cancel", sg.WIN_CLOSED):
            window.close()
            break
        if event == "update":
            window["update"].update(disabled=True)
            window["cancel"].update(disabled=True)
            window["restore"].update(disabled=True)
            window.perform_long_operation(lambda: do_update(value["url"]), "post_update")
        if event == "post_update":
            window["update"].update(disabled=False)
            window["cancel"].update(disabled=False)
            window["restore"].update(disabled=False)
            if value["post_update"] == "success":
                sg.popup("Aggiornamento completato!")
                window.close()
                break
            elif value["post_update"] == "invalid_url":
                sg.popup("URL non valido!")
                continue
            elif value["post_update"] == "download_error":
                sg.popup("Errore di download!")
                continue
        if event == "restore":
            window["restore"].update(disabled=True)
            window["update"].update(disabled=True)
            window["cancel"].update(disabled=True)
            window.perform_long_operation(do_restore, "post_restore")
        if event == "post_restore":
            window["restore"].update(disabled=False)
            window["update"].update(disabled=False)
            window["cancel"].update(disabled=False)
            if value["post_restore"] == "success":
                sg.popup("Ripristino completato!")
                window.close()
                break
            elif value["post_restore"] == "no_backup":
                sg.popup("Nessun backup presente!")
                continue


if __name__ == "__main__":
    update_swordsmith_from_remote()

# release the lock
lock.close()
