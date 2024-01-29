import PySimpleGUI as sg

from pydrive2.drive import GoogleDrive

from utils.recordings import Recording, recording_from_path, upload_recordings


def upload_selected(
    recordings: list[Recording],
    drive: GoogleDrive,
    drive_root_id: str,
    values_upload: dict | None = None,
    upload_window: sg.Window | None = None,
    main_window: sg.Window | None = None,
) -> None:
    if values_upload is not None:
        planned_uploads = []
        for i in [i for i in values_upload if values_upload[i]]:
            i = i[11:]
            recording_to_upload: Recording = recording_from_path(recordings, i)
            print(str(recording_to_upload.path) + " will be uploaded")
            planned_uploads.append(recording_to_upload)
    else:
        planned_uploads = recordings
    if upload_window is not None:
        upload_window.hide()
    results = upload_recordings(planned_uploads, drive, drive_root_id)
    if len(results["skipped"]) > 0:
        text_results = sg.Text(
            f"{len(results['success'])} registrazioni caricate con successo.\n"
            f"{len(results['skipped'])} registrazioni già esistenti."
        )
    else:
        text_results = sg.Text(
            f"{len(results['success'])} registrazioni caricate con successo"
        )

    layout_upload_results = [
        [text_results],
        [
            sg.Text(
                "Vuoi eliminare le registrazioni già caricate dalla chiavetta? (CONSIGLIATO)",
                size=(33, 2),
            )
        ],
        [
            sg.Button(
                "Si",
                size=(10, 1),
                key="yes",
                button_color=("white", "green"),
            ),
            sg.Button("No", size=(10, 1), key="no"),
        ],
    ]
    upload_results_window = sg.Window(
        "Esito caricamento",
        layout_upload_results,
        size=(300, 130),
        finalize=True,
    )
    while True:
        (
            event_upload_results,
            values_upload_results,
        ) = upload_results_window.read()
        if event_upload_results == "yes":
            for i in results["success"] + results["skipped"]:
                i.delete()
            break
        if event_upload_results == "no":
            break
    upload_results_window.close()
    if upload_window is not None:
        upload_window.close()
    if main_window is not None:
        main_window.UnHide()
        main_window.bring_to_front()
    return
