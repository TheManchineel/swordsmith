import PySimpleGUI as sg

from .delete_selected import delete_selected_recording
from .upload_selected import upload_selected

from utils.models import Recording
from utils.google_drive import get_google_drive


def make_checkbox_from_list_of_recordings(
    recordings: list[Recording],
) -> list[sg.Checkbox]:
    checkboxes = []
    if recordings:
        recordings.sort(key=lambda rec: rec.path.name, reverse=True)
        for i in recordings:
            checkboxes.append(
                [
                    sg.Checkbox(
                        i,
                        default=False,
                        key=f"Recording: {i.path}",
                        size=(66, 1),
                        enable_events=True,
                    )
                ]
            )
    return checkboxes


def show_upload_window(
    recordings: list[Recording],
    main_window: sg.Window,
    drive_root_id: str,
) -> None:
    total_recordings = len(recordings)
    checkboxes = make_checkbox_from_list_of_recordings(recordings)
    layout_upload = [
        [sg.Text("Registrazioni:", font=("Arial", 16))],
        [
            sg.Column(
                checkboxes,
                scrollable=True,
                vertical_scroll_only=True,
                size=(590, 200),
                key="recording_checkboxes",
            )
        ],
        [
            sg.Button(
                "Carica selezionati",
                size=(16, 1),
                key="upload_selected",
                disabled=True,
            ),
            sg.Button(
                "Elimina selezionati",
                size=(16, 1),
                key="delete_selected",
                disabled=True,
            ),
            sg.Push(),
            sg.Button(
                "Seleziona tutti", size=(16, 1), key="select_all", disabled=False
            ),
            sg.Button(
                "Deseleziona tutti",
                size=(16, 1),
                key="deselect_all",
                disabled=True,
            ),
        ],
        [sg.Push(), sg.Button("Annulla", size=(16, 1), key="cancel")],
    ]
    upload_window = sg.Window(
        "Gestisci registrazioni", layout_upload, size=(630, 320), finalize=True
    )
    while True:
        event_upload, values_upload = upload_window.read()
        if isinstance(event_upload, str) and event_upload.startswith("Recording: "):
            true_values_upload_count = sum(
                i for i in values_upload.values() if i is True
            )
            if true_values_upload_count != 0:
                upload_window["deselect_all"].update(disabled=False)
                if true_values_upload_count == total_recordings:
                    upload_window["select_all"].update(disabled=True)
                else:
                    upload_window["select_all"].update(disabled=False)
                upload_window["upload_selected"].update(
                    disabled=False, button_color=("white", "green")
                )
                upload_window["delete_selected"].update(
                    disabled=False, button_color=("white", "red")
                )
                if true_values_upload_count == 1:
                    upload_window["upload_selected"].update("Carica selezionato")
                    upload_window["delete_selected"].update("Elimina selezionato")
                else:
                    upload_window["upload_selected"].update(
                        f"Carica {true_values_upload_count} selezionati"
                    )
                    upload_window["delete_selected"].update(
                        f"Elimina {true_values_upload_count} selezionati"
                    )
            else:
                upload_window["upload_selected"].update(
                    "Carica selezionati",
                    disabled=True,
                    button_color=("white", "grey"),
                )
                upload_window["delete_selected"].update(
                    "Elimina selezionati",
                    disabled=True,
                    button_color=("white", "grey"),
                )
                upload_window["select_all"].update(disabled=False)
                upload_window["deselect_all"].update(disabled=True)
                upload_window["deselect_all"].update(disabled=True)

        if event_upload == "upload_selected":
            drive = get_google_drive()
            if drive is None:
                sg.popup(
                    "Impossibile connettersi a Google Drive. Verifica che la connessione a internet sia disponibile. "
                    "Se il problema persiste, contatta SmiderPan."
                )
                continue
            else:
                upload_selected(
                    recordings,
                    drive,
                    drive_root_id,
                    values_upload=values_upload,
                    upload_window=upload_window,
                    main_window=main_window,
                )
                break

        if event_upload == "cancel" or event_upload == sg.WIN_CLOSED:
            upload_window.close()
            main_window.UnHide()
            main_window.bring_to_front()
            break

        if event_upload == "select_all":

            for i in values_upload.keys():
                if i.startswith("Recording: "):
                    upload_window[i].update(True)
            if total_recordings > 1:
                upload_window["upload_selected"].update(
                    f"Carica {total_recordings} selezionati",
                    disabled=False,
                    button_color=("white", "green"),
                )
                upload_window["delete_selected"].update(
                    f"Elimina {total_recordings} selezionati",
                    disabled=False,
                    button_color=("white", "red"),
                )
            else:
                upload_window["upload_selected"].update(
                    "Carica selezionato",
                    disabled=False,
                    button_color=("white", "green"),
                )
                upload_window["delete_selected"].update(
                    "Elimina selezionato",
                    disabled=False,
                    button_color=("white", "red"),
                )
            upload_window["deselect_all"].update(disabled=False)
            upload_window["select_all"].update(disabled=True)
            continue

        if event_upload == "deselect_all":
            for i in values_upload.keys():
                if i.startswith("Recording: "):
                    upload_window[i].update(False)
            upload_window["deselect_all"].update(disabled=True)
            upload_window["select_all"].update(disabled=False)
            upload_window["upload_selected"].update(
                "Carica selezionati",
                disabled=True,
                button_color=("white", "grey"),
            )
            upload_window["delete_selected"].update(
                "Carica selezionati",
                disabled=True,
                button_color=("white", "grey"),
            )
            continue

        if event_upload == "delete_selected":
            delete_selected_recording(
                upload_window, main_window, values_upload, recordings
            )
            continue
