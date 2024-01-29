import PySimpleGUI as sg
from zc.lockfile import LockFile, LockError
from pathlib import Path

from utils.config import (
    config_to_classes,
    classes_to_config,
    classes,
    drive_root_id,
    fix_missing,
    archived_dir,
    encoded_icon,
)

from utils.models import Class, Recording
from utils.recordings import get_recordings
from utils.housekeeping import check_drive_folders, delete_ds_store_and_metadata

from gui.main_screen import show_main_window
from gui.splash import show_splash

# DEFINITIONS ##################################################################

sg.theme("Dark Black")
sg.set_options(icon=encoded_icon)


def check_lock() -> LockFile:
    try:
        lock_path = Path(__file__).parent / "lock"
        lock = LockFile(lock_path.absolute())
        return lock
    except LockError as e:
        sg.popup(f"Il programma risulta già avviato. Forse devi solo attendere?\n\n{e}")
        exit(1)


lock = check_lock()


def update_recordings_list(
    classes: list[Class], recordings_list: list[Recording]
) -> None:
    recordings_list.clear()
    recordings_list.extend(get_recordings(classes))


# LOGIC ######################################################################

# Load classes from config
config_to_classes()

# Housekeeping
check_drive_folders(classes, drive_root_id, fix_missing, archived_dir)
delete_ds_store_and_metadata()

# Main window

show_main_window(classes, drive_root_id, archived_dir)

# Save updated classes
classes_to_config()

lock.close()

show_splash("Ricordati di espellere la chiavetta!", title="Promemoria", time=2000)
