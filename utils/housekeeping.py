from pathlib import Path

from .google_drive import (
    get_google_drive,
    list_directory,
    create_directory,
    id_from_path,
)
from .models import Class
from .utils import classes_by_archived, root_path


def check_drive_folders(
    classes: list[Class], drive_root_id: str, fix: bool, archived_name: str
) -> None:
    drive = get_google_drive()
    if drive is None:
        print("Did not check: no Google Drive")
        return
    drive_list = list_directory(drive, drive_root_id)
    drive_list_uuids = [i.metadata["title"][-36:] for i in drive_list]
    try:
        drive_archived_id = id_from_path(drive, drive_root_id, archived_name)
    except FileNotFoundError:
        if fix:
            print(f"Creo cartella {archived_name}")
            drive_archived_id = create_directory(drive, drive_root_id, archived_name)
        else:
            print(f"Cartella {archived_name} non presente")
            exit(1)
    drive_archived_list = list_directory(drive, drive_archived_id)
    drive_archived_list_uuids = [i.metadata["title"][-36:] for i in drive_archived_list]
    for i in classes_by_archived(classes, False):
        if str(i.uuid) not in drive_list_uuids:
            if fix:
                print(f"Creo cartella {i.dir_name}")
                create_directory(drive, drive_root_id, i.dir_name)
            else:
                print(f"Cartella {i.dir_name} non presente")
    for i in classes_by_archived(classes, True):
        if str(i.uuid) not in drive_archived_list_uuids:
            if fix:
                print(f"Creo cartella archiviata {i.dir_name}")
                create_directory(drive, drive_archived_id, i.dir_name)
            else:
                print(f"Cartella archiviata {i.dir_name} non presente")


def delete_ds_store_and_metadata(root_path: Path = root_path) -> None:
    for i in root_path.glob("**/*"):
        if i.is_file():
            if i.name == ".DS_Store" or i.name.startswith("._"):
                print(f"{i.absolute()} deleted!")
                i.unlink()
