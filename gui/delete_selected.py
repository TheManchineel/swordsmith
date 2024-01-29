import PySimpleGUI as sg

from utils.models import Recording
from utils.recordings import recording_from_path


def delete_selected_recording(
    upload_window: sg.Window,
    main_window: sg.Window,
    values_upload: dict,
    recordings: list[Recording],
) -> None:
    upload_window.Hide()
    delete_message = "Sei sicura di voler eliminare "
    planned_deletes = []
    for i in [i for i in values_upload if values_upload[i]]:
        i = i[11:]
        recording_to_delete: Recording = recording_from_path(recordings, i)
        print(str(recording_to_delete.path) + " will be deleted")
        planned_deletes.append(recording_to_delete)
    if len(planned_deletes) == 1:
        delete_message += "la registrazione selezionata?"
    else:
        delete_message += f"{len(planned_deletes)} registrazioni selezionate?"
    delete_message += (
        "\n\nLe registrazioni verranno eliminate per sempre (un sacco di tempo!) dalla chiavetta."
        "\nDrive non verrà influenzato."
    )
    are_you_sure_window = sg.Window(
        "Conferma eliminazione",
        [
            [
                sg.Text(
                    delete_message,
                    size=(33, 7),
                )
            ],
            [
                sg.Button(
                    "Sì",
                    size=(10, 1),
                    key="yes",
                    button_color=("white", "red"),
                ),
                sg.Button("No", size=(10, 1), key="no"),
            ],
        ],
        # size=(300, 130),
        finalize=True,
    )
    while True:
        (
            event_are_you_sure,
            values_are_you_sure,
        ) = are_you_sure_window.read()
        if event_are_you_sure == "yes":
            deleted_count = 0
            for i in planned_deletes:
                try:
                    i.delete()
                    deleted_count += 1
                except Exception as e:
                    print(e)
            if deleted_count == 1:
                sg.Popup("Registrazione eliminata con successo")
            else:
                sg.Popup(f"{deleted_count} registrazioni eliminate con successo")
            are_you_sure_window.close()
            upload_window.close()
            main_window.UnHide()
            break
        if event_are_you_sure == "no" or event_are_you_sure == sg.WIN_CLOSED:
            are_you_sure_window.close()
            upload_window.UnHide()
            upload_window.bring_to_front()
            break
