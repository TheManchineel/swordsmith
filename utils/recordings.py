from pathlib import Path
from threading import Thread
from pydrive2.drive import GoogleDrive
import PySimpleGUI as sg

from .utils import recordings_path
from .models import Class, Recording
from .google_drive import (
    list_directory,
    try_create_or_return_id_of_existing_directory,
    upload_file,
)


def get_recordings(
    classes: list[Class], recordings_path: Path = recordings_path
) -> list[Recording]:
    recordings = []
    for classroom in recordings_path.iterdir():
        if classroom.is_dir():
            try:
                current_class = [
                    i for i in classes if str(i.uuid) == classroom.name[-36:]
                ][0]
                for subject in classroom.iterdir():
                    if subject.is_dir():
                        for recording in subject.iterdir():
                            if recording.is_file():
                                current_recording = Recording(
                                    path=recording,
                                    classroom=current_class,
                                    subject=subject.name,
                                )
                                recordings.append(current_recording)
            except IndexError:
                print(f"Cartella estranea: {classroom.name}")
        return recordings


def get_uncategorized_recordings(
    classes: list[Class], recordings_path: Path = recordings_path
) -> list[Recording]:
    uncategorized_recordings = []
    for classroom in recordings_path.iterdir():
        if classroom.is_dir():
            try:
                current_class = [
                    i for i in classes if str(i.uuid) == classroom.name[-36:]
                ][0]
                for bulk_recording in classroom.iterdir():
                    if bulk_recording.is_file():
                        current_recording = Recording(
                            path=bulk_recording,
                            classroom=current_class,
                            subject=None,
                        )
                        uncategorized_recordings.append(current_recording)
            except IndexError:
                print(f"Cartella estranea: {classroom.name}")
        return uncategorized_recordings


def recording_from_path(recordings: list[Recording], path: Path | str) -> Recording:
    if isinstance(path, str):
        path = Path(path)
    for recording in recordings:
        if recording.path == path:
            return recording
    raise FileNotFoundError("Recording not found")


def upload_recordings(
    recordings: list[Recording], drive: GoogleDrive, drive_root_id: str
) -> dict:
    upload_results = {"success": [], "failure": [], "skipped": []}
    found_class_ids: dict = {}
    for recording in recordings:
        if str(recording.classroom.uuid) not in found_class_ids:
            directories = list_directory(drive, drive_root_id)
            for directory in directories:
                if directory["title"][-36:] == str(recording.classroom.uuid):
                    found_class_ids[recording.classroom.uuid] = directory["id"]
                    break
        subject_dir = try_create_or_return_id_of_existing_directory(
            drive, found_class_ids[recording.classroom.uuid], recording.subject
        )

        def upload_recording(
            drive: GoogleDrive,
            subject_dir: str,
            recording: Recording,
            upload_results: dict,
            uploading_window: sg.Window,
        ):
            try:
                upload_file(drive, subject_dir, recording.path.name, recording.path)
                upload_results["success"].append(recording)
            except FileExistsError:
                upload_results["skipped"].append(recording)
            except Exception as e:
                upload_results["failure"].append(recording)
                print(e)
            uploading_window.write_event_value("thread_done", True)

        print(f"Uploading {recording.path}")
        uploading_layout = [
            [sg.Text("Caricamento in corso...")],
            [sg.Text(f"{recording.path.name}")],
            [sg.ProgressBar(max_value=300, size=(30, 10), key="bar", metadata=5)],
        ]
        uploading_window = sg.Window(
            "Caricamento in corso",
            layout=uploading_layout,
            no_titlebar=True,
            finalize=True,
        )
        uploading_window["bar"].Widget.config(mode="indeterminate")

        upload_thread = Thread(
            target=upload_recording,
            args=(
                drive,
                subject_dir,
                recording,
                upload_results,
                uploading_window,
            ),
        )
        upload_thread.start()

        progress = 0
        while True:
            upload_events = uploading_window.read(timeout=33)[0]
            if upload_events == "thread_done":
                break
            progress = (progress + 10) % 310
            uploading_window["bar"].update(progress)
        uploading_window.close()
    return upload_results
