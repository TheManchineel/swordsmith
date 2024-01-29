import PySimpleGUI as sg
from uuid import UUID

from utils.models import Class
from utils.utils import classes_by_archived
from utils.config import drive_root_id, archived_dir
from utils.google_drive import get_google_drive, move_file


def class_from_uuid(classes: list[Class], uuid: UUID | str) -> Class:
    if isinstance(uuid, str):
        uuid = UUID(uuid)
    for i in classes:
        if i.uuid == uuid:
            return i
    raise ValueError(f"Class with uuid {uuid} not found")


def make_checkbox_from_list_of_classes(classes: list[Class]) -> list[sg.Checkbox]:
    checkboxes = []
    if classes:
        classes.sort(key=lambda cla: str(cla))
        for i in classes:
            checkboxes.append(
                [
                    sg.Checkbox(
                        i,
                        default=False,
                        key=f"Class: {i.uuid}",
                        size=(66, 1),
                        enable_events=True,
                    )
                ]
            )
    return checkboxes


def show_manage_archived_window(classes: list[Class]) -> None:
    archived_classes = classes_by_archived(classes, True)
    checkboxes = make_checkbox_from_list_of_classes(archived_classes)
    layout = [
        [sg.Text("Classi archiviate:", font=("Arial", 16))],
        [
            sg.Column(
                checkboxes,
                scrollable=True,
                vertical_scroll_only=True,
                size=(590, 200),
                key="class_checkboxes",
            )
        ],
        [
            sg.Button(
                "Rimuovi selezionate",
                size=(16, 1),
                key="remove_selected",
                disabled=True,
            ),
            sg.Button(
                "Ripristina selezionate",
                size=(16, 1),
                key="restore_selected",
                disabled=True,
            ),
            sg.Button("Indietro", size=(16, 1), key="back", disabled=False),
        ],
    ]
    window = sg.Window(
        "Gestisci classi archiviate",
        layout,
        finalize=True,
    )
    while True:
        event, values = window.read()
        if isinstance(event, str) and event.startswith("Class: "):
            if sum(i for i in values.values() if i) > 0:
                window["remove_selected"].update(disabled=False)
                window["restore_selected"].update(disabled=False)
            else:
                window["remove_selected"].update(disabled=True)
                window["restore_selected"].update(disabled=True)
        if event == "remove_selected":
            print(values)
            for i in values:
                if isinstance(i, str) and i.startswith("Class: "):
                    uuid = UUID(i.split(": ")[1])
                    class_to_remove = class_from_uuid(classes, uuid)
                    classes.remove(class_to_remove)
            window.close()
            show_manage_archived_window(classes)
            continue
        elif event == "restore_selected":
            for i in values:
                if isinstance(i, str) and i.startswith("Class: "):
                    uuid = UUID(i.split(": ")[1])
                    class_to_restore = class_from_uuid(classes, uuid)
                    drive = get_google_drive()
                    if drive is not None:
                        move_file(
                            drive,
                            class_to_restore.get_dir_id(
                                drive, drive_root_id, archived_dir
                            ),
                            drive_root_id,
                        )
                        class_to_restore.archived = False
            window.close()
            show_manage_archived_window(classes)
            break
        elif event == "back" or event == sg.WIN_CLOSED:
            window.close()
            break
