import PySimpleGUI as sg
from threading import Thread

from utils.models import Class
from utils.utils import classes_by_archived, get_random_quote
from utils.recordings import get_recordings, get_uncategorized_recordings
from utils.google_drive import get_google_drive
from utils.obs import launch_obs
from utils.config import classes_to_config

from gui.upload_recordings import show_upload_window
from gui.upload_selected import upload_selected
from gui.uncategorized_recordings import show_uncategorized_window
from gui.manage_class import show_archive_window, show_delete_window, show_create_window
from gui.manage_archived import show_manage_archived_window
from gui.splash import show_splash


def show_main_window(
    classes: list[Class], drive_root_id: str, archived_dir: str
) -> None:

    if not classes_by_archived(classes, False):
        pass
    layout_main = [
        [sg.Text("Classi disponibili:", font=("Arial", 16))],
        [
            sg.Listbox(
                values=classes_by_archived(classes, False),
                size=(40, 10),
                key="classes",
                enable_events=True,
                select_mode=sg.SELECT_MODE_SINGLE,
                bind_return_key=False,
            )
        ],
        [
            sg.Button(
                "Avvia OBS",
                size=(33, 1),
                key="start_obs",
                disabled=True,
                button_color=("white", "grey"),
            )
        ],
        [
            sg.Button("Classi Archiviate", size=(15, 1), key="archived"),
            sg.Push(),
            sg.Button("Nuova Classe", size=(15, 1), key="new_class"),
        ],
        [
            sg.Button(
                "Archivia Classe",
                size=(15, 1),
                key="archive",
                disabled=True,
                button_color=("white", "grey"),
            ),
            sg.Push(),
            sg.Button(
                "Rimuovi Classe",
                size=(15, 1),
                key="remove",
                disabled=True,
                button_color=("white", "grey"),
            ),
        ],
        [sg.Button("Gestisci Registrazioni", size=(33, 1), key="upload_recordings")],
        [
            sg.VPush(),
            [
                sg.Text(
                    "Designed by Alessandro Modica in Pavia, Italy.\n"
                    "© SmiderPan 2022. All Rights Reserved.",
                    size=(34, 3),
                    text_color="medium purple",
                ),
                sg.Push(),
            ],
        ],
    ]

    main_window = sg.Window("Classi", layout_main, size=(300, 400), finalize=True)

    bring_to_front = True
    while True:
        event, values = main_window.read()
        if bring_to_front:
            main_window.BringToFront()
            bring_to_front = False
        if event == "classes":
            if not values["classes"]:
                continue
            selected_class: Class = values["classes"][0]
            main_window["start_obs"].update(
                f'Avvia OBS per "{selected_class}"',
                disabled=False,
                button_color=("white", "green"),
            )
            main_window["archive"].update(
                disabled=False, button_color=("white", "orange")
            )
            main_window["remove"].update(disabled=False, button_color=("white", "red"))
        if event == "start_obs":
            main_window.close()
            obs_thread = Thread(target=launch_obs, args=(selected_class,))
            obs_thread.start()
            quote = get_random_quote()
            show_splash(f"{quote[0]}\n—{quote[1]}", time=5000)
            obs_thread.join()
            new_recordings = get_uncategorized_recordings(classes)
            if new_recordings:
                user_chose_subjects = show_uncategorized_window(
                    new_recordings, revert_on_close=True
                )
                if not user_chose_subjects:
                    sg.Popup(
                        "Sei uscita dalla selezione della materia. "
                        "Per caricare le registrazioni, devono essere categorizzate. "
                        'Puoi farlo in seguito da "Gestisci Registrazioni", '
                        "o ti verrà proposto di farlo la prossima volta che usi OBS."
                    )
                else:
                    wanna_upload_layout = [
                        [
                            sg.Text(
                                "Vuoi caricare le registrazioni su Drive? (CONSIGLIATO)"
                            )
                        ],
                        [
                            sg.Button(
                                "Sì",
                                key="yes",
                                button_color=("white", "green"),
                                size=(15, 1),
                            ),
                            sg.Button("No", key="no", size=(15, 1)),
                        ],
                    ]
                    wanna_upload_window = sg.Window(
                        "Carica registrazioni", wanna_upload_layout, finalize=True
                    )
                    while True:
                        (
                            wanna_upload_event,
                            wanna_upload_values,
                        ) = wanna_upload_window.read()
                        if wanna_upload_event == "yes":
                            drive = get_google_drive()
                            if drive is None:
                                sg.Popup(
                                    "Impossibile connettersi a Google Drive. "
                                    "Verifica che la connessione a internet sia disponibile.\n"
                                    'Puoi caricare le registrazioni in seguito da "Gestisci Registrazioni".\n\n'
                                    "Se il problema persiste, contatta SmiderPan."
                                )
                                break
                            else:
                                upload_selected(
                                    new_recordings,
                                    drive,
                                    drive_root_id,
                                    upload_window=wanna_upload_window,
                                )
                            break
                        elif (
                            wanna_upload_event == "no"
                            or wanna_upload_event == sg.WIN_CLOSED
                        ):
                            wanna_upload_window.close()
                            sg.Popup(
                                'Puoi caricare le registrazioni in seguito da "Gestisci Registrazioni".'
                            )
                            break
            break
        if event == "archive":
            if selected_class.is_empty():
                user_did_archive = show_archive_window(
                    selected_class, drive_root_id, archived_dir
                )
                if user_did_archive:
                    selected_class = None
                    classes_to_config()
                    main_window["classes"].update(
                        values=classes_by_archived(classes, False)
                    )
                    main_window["archive"].update(
                        disabled=True, button_color=("white", "grey")
                    )
                    main_window["remove"].update(
                        disabled=True, button_color=("white", "grey")
                    )
                    main_window["start_obs"].update(
                        "Avvia OBS", disabled=True, button_color=("white", "grey")
                    )
            else:
                sg.Popup(
                    "Ci sono ancora registrazioni non caricate.\n"
                    "Per archiviare la classe, devi prima caricarle o rimuoverle."
                )
        if event == "archived":
            main_window.Hide()
            show_manage_archived_window(classes)
            selected_class = None
            classes_to_config()
            main_window["classes"].update(values=classes_by_archived(classes, False))
            main_window["archive"].update(disabled=True, button_color=("white", "grey"))
            main_window["remove"].update(disabled=True, button_color=("white", "grey"))
            main_window["start_obs"].update(
                "Avvia OBS", disabled=True, button_color=("white", "grey")
            )
            main_window.UnHide()
        if event == "remove":
            user_did_delete = show_delete_window(selected_class)
            if user_did_delete:
                classes.remove(selected_class)
                selected_class = None
                classes_to_config()
                main_window["classes"].update(
                    values=classes_by_archived(classes, False)
                )
                main_window["archive"].update(
                    disabled=True, button_color=("white", "grey")
                )
                main_window["remove"].update(
                    disabled=True, button_color=("white", "grey")
                )
                main_window["start_obs"].update(
                    "Avvia OBS", disabled=True, button_color=("white", "grey")
                )
                selected_class = None
        if event == "new_class":
            main_window.Hide()
            user_did_create = show_create_window(classes, drive_root_id)
            if user_did_create:
                classes_to_config()
                main_window["classes"].update(
                    values=classes_by_archived(classes, False)
                )
                main_window["archive"].update(
                    disabled=True, button_color=("white", "grey")
                )
                main_window["remove"].update(
                    disabled=True, button_color=("white", "grey")
                )
                main_window["start_obs"].update(
                    "Avvia OBS", disabled=True, button_color=("white", "grey")
                )
            main_window.UnHide()
        if event == "upload_recordings":
            uncategorized_recordings = get_uncategorized_recordings(classes)
            if uncategorized_recordings:
                main_window.hide()
                user_wants_to_continue = show_uncategorized_window(
                    uncategorized_recordings, main_window
                )
                if not user_wants_to_continue:
                    main_window.UnHide()
                    main_window.bring_to_front()
                    continue
            recordings = get_recordings(classes)
            if not recordings:
                sg.popup("Nessuna registrazione presente")
                continue
            main_window.hide()
            show_upload_window(recordings, main_window, drive_root_id)

        if event == sg.WIN_CLOSED:
            break
