import PySimpleGUI as sg

from utils.models import Recording, get_video_length
from utils.utils import check_illegal_characters_in_path


def show_uncategorized_window(
    recordings: list[Recording],
    main_window: sg.Window | None = None,
    revert_on_close: bool = False,
) -> bool:  # returns True if the user wants to continue
    categorized_recordings: list[Recording] = []
    if main_window is not None:
        uncategorized_window_layout = [
            [sg.Text("Registrazioni non categorizzate", font=("Arial", 16))],
            [
                sg.Text(
                    "Per poterle gestire, devi prima indicare la materia delle registrazioni non categorizzate."
                )
            ],
            [
                sg.Text("Registrazione non categorizzata: "),
                sg.Text("1/1", key="uncategorized_count"),
            ],
        ]
    else:
        uncategorized_window_layout = [
            [sg.Text("Nuove registrazioni", font=("Arial", 16))],
            [sg.Text("Devi indicare la materia delle nuove registrazioni.")],
            [
                sg.Text("Nuova registrazione: "),
                sg.Text("1/1", key="uncategorized_count"),
            ],
        ]
    current_recording_count = -1
    uncategorized_window_layout += [
        [
            sg.Text(
                "recording_name",
                size=(60, 1),
                key="recording_name",
            ),
            sg.Combo(
                ["Storia", "Filosofia", "Educazione Civica", "Generale"],
                default_value=None,
                key="subject",
                tooltip="Seleziona o digita una materia",
            ),
        ],
        [
            sg.Push(),
            sg.Button(
                "OK",
                size=(15, 1),
                key="ok",
                button_color=("white", "green"),
            ),
        ],
    ]
    uncategorized_window = sg.Window(
        "Nuove registrazioni", uncategorized_window_layout, finalize=True
    )
    uncategorized_window.BringToFront()

    def update_uncategorized_window(
        window: sg.Window, recordings: list[Recording], index: int
    ) -> None:
        recording = recordings[current_recording_count]
        window.Element("recording_name").Update(
            f"{recording.path.name} ({get_video_length(recording.path)})"
        )
        window.Element("uncategorized_count").Update(f"{index+1}/{len(recordings)}")

    advance: bool = True
    while True:
        if advance:
            current_recording_count += 1
            if current_recording_count >= len(recordings):
                break
            update_uncategorized_window(
                uncategorized_window, recordings, current_recording_count
            )
            advance = False

        event, values = uncategorized_window.read()

        if event == "ok":
            if values["subject"].strip() == "":
                sg.Popup(
                    "Devi indicare la materia della registrazione. Usa il menù a tendina o digita una materia."
                )
                continue
            elif check_illegal_characters_in_path(values["subject"]):
                sg.Popup(
                    "La materia indicata contiene sequenze o caratteri non consentiti. "
                    "Usa il menù a tendina o digita una materia valida."
                )
                continue
            recordings[current_recording_count].categorize(values["subject"])
            categorized_recordings.append(recordings[current_recording_count])
            advance = True
            uncategorized_window["subject"].Update(value="")
            continue

        if event == sg.WIN_CLOSED:
            if revert_on_close:
                for recording in categorized_recordings:
                    recording.revert_categorization()
            return False
    uncategorized_window.close()
    return True
