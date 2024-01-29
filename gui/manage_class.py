import PySimpleGUI as sg
from uuid import uuid4

from utils.models import Class
from utils.google_drive import (
    create_directory,
    get_google_drive,
    move_file,
    id_from_path,
)
from utils.utils import check_illegal_characters_in_path


def show_create_window(
    classes: list[Class],
    drive_root_id: str,
) -> bool:
    layout = [
        [
            sg.Text("Nome della classe (es. 5F):"),
            sg.Push(),
            sg.InputText(size=(30, 1), key="name"),
        ],
        [
            sg.Text("Anno d'inizio della classe (es. 2021):"),
            sg.Push(),
            sg.InputText(size=(4, 1), key="year"),
        ],
        [
            sg.Button(
                "Crea", size=(15, 1), key="create", button_color=("white", "green")
            ),
            sg.Button("Annulla", size=(15, 1), key="cancel"),
        ],
    ]
    window = sg.Window(layout=layout, title="Crea classe", finalize=True)
    while True:
        event, values = window.read()
        if event == "create":
            name = values["name"].strip()
            if name == "" or check_illegal_characters_in_path(name):
                sg.Popup(
                    "Nome della classe non valido. Inserisci il nome della classe in cifra e lettera "
                    "(es. per la Quinta F, inserisci 5F)."
                )
                continue
            year = values["year"].strip()
            try:
                year = int(year)
            except ValueError:
                sg.Popup(
                    "Anno non valido. Indica l'anno di inizio in cifre "
                    "(es. per A.S. 2021-2022, inserisci 2021)."
                )
                continue
            uuid_found = False
            while not uuid_found:
                uuid = uuid4()
                if uuid not in [c.uuid for c in classes]:
                    uuid_found = True  # UUIDs are unique, therefore this is utterly useless; that said, I have OCD
            new_class = Class(uuid=uuid, name=values["name"], year=year)
            classes.append(new_class)
            drive = get_google_drive()
            if drive is not None:
                try:
                    create_directory(
                        drive, drive_root_id, new_class.dir_name, safe=True
                    )
                except Exception as e:
                    sg.Popup(e)
            sg.Popup(
                "Classe creata con successo! Devi ora condividere la cartella con la classe su Drive."
            )
            window.close()
            return True
        elif event == "cancel" or event == sg.WIN_CLOSED:
            window.close()
            return False


def show_archive_window(
    classroom: Class, drive_root_id: str, archived_dir: str
) -> bool:
    layout = [
        [
            sg.Text(
                f"Sei sicura di voler archiviare la classe {classroom}?\n\n"
                f"La cartella su Drive sarà spostata in {archived_dir} "
                "e non potrai più registrare su questa classe."
            )
        ],
        [
            sg.Button(
                "Archivia", size=(15, 1), key="archive", button_color=("white", "red")
            ),
            sg.Button("Annulla", size=(15, 1), key="cancel"),
        ],
    ]
    window = sg.Window(layout=layout, title="Archivia classe", finalize=True)
    while True:
        event, values = window.read()
        if event == "archive":
            drive = get_google_drive()
            if drive is None:
                sg.Popup(
                    "Impossibile connettersi a Google Drive. "
                    "Verifica che la connessione a internet sia disponibile.\n"
                    "Se il problema persiste, contatta SmiderPan."
                )
                window.close()
                return False
            else:
                try:
                    move_file(
                        drive,
                        classroom.get_dir_id(drive, drive_root_id, archived_dir),
                        id_from_path(drive, drive_root_id, archived_dir),
                    )
                    classroom.archived = True
                    classroom.delete()
                    window.close()
                    return True
                except Exception as e:
                    print(e)
                    sg.Popup(
                        "Impossibile archiviare la classe.\nSe il problema persiste, contatta SmiderPan."
                    )
                    window.close()
                    return False
        elif event == "cancel" or event == sg.WIN_CLOSED:
            window.close()
            return False


def show_delete_window(classroom: Class) -> bool:
    layout = [
        [
            sg.Text(
                f"Sei sicura di voler eliminare la classe {classroom}?\n\n"
                "Non potrai più registrare su questa classe. Drive rimarrà invariato."
            )
        ],
        [
            sg.Button(
                "Elimina", size=(15, 1), key="delete", button_color=("white", "red")
            ),
            sg.Button("Annulla", size=(15, 1), key="cancel"),
        ],
    ]
    window = sg.Window(layout=layout, title="Elimina classe", finalize=True)
    while True:
        event, values = window.read()
        if event == "delete":
            if classroom.is_empty():
                classroom.delete()
            else:
                sg.Popup(
                    "Impossibile eliminare la classe.\n"
                    "Devi prima caricare tutte le registrazioni o eliminarle."
                )

            window.close()
            return True
        elif event == "cancel" or event == sg.WIN_CLOSED:
            window.close()
            return False
