from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive, GoogleDriveFile
from oauth2client.service_account import ServiceAccountCredentials
from pathlib import Path
from dns import resolver
import requests

from .utils import run_in_dir, data_path

FOLDER_MIME_TYPE = "application/vnd.google-apps.folder"

OAUTH_SCOPE = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.install",
]


def check_if_drive_is_accessible(drive: GoogleDrive) -> bool:
    if drive is None:
        return False
    endpoint_url = "https://www.googleapis.com/drive/v3/about"
    test_directory_id = "1JaKxZGX9R_UKWSCO1UETLv9bTVyEO6DV"
    try:
        if requests.get(endpoint_url).status_code == 401:
            try:
                test_directory = drive.CreateFile({"id": test_directory_id})
                test_directory.FetchMetadata()
                return test_directory.metadata["mimeType"] == FOLDER_MIME_TYPE
            except Exception:
                return False
        else:
            return False
    except Exception:
        return False


drive = None


def _connect_to_drive() -> GoogleDrive:
    with run_in_dir(data_path):
        gauth = GoogleAuth()
        gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(
            "./service_credentials.json", OAUTH_SCOPE
        )
        gauth.auth_method = "service"
        drive = GoogleDrive(gauth)
        return drive


def get_google_drive() -> GoogleDrive:
    global drive
    if check_if_drive_is_accessible(drive):
        print("Successfully connected to Drive! (using existing session)")
        return drive
    else:
        with run_in_dir(data_path):
            try:
                drive = _connect_to_drive()
                if check_if_drive_is_accessible(drive):
                    print("Successfully connected to Drive! (authenticated)")
                    return drive
                else:
                    drive = None
                    return None
            except Exception as e:
                drive = None
                print("Failed to connect to Drive")
                print(e)


# def delete_credentials() -> None:
#     with run_in_dir(data_path):
#         print("Test")
#         (Path.cwd() / "credentials.json").unlink()


def list_directory(drive: GoogleDrive, parent_id: str) -> list:
    parent = drive.CreateFile({"id": parent_id})
    parent.FetchMetadata()
    if parent.metadata["mimeType"] == FOLDER_MIME_TYPE:
        return drive.ListFile(
            {"q": "'{}' in parents and trashed=false".format(parent_id)}
        ).GetList()
    else:
        raise FileNotFoundError("Parent is not a directory")


def create_directory(
    drive: GoogleDrive, parent_id: str, name: str, safe: bool = True
) -> str:
    if safe:
        parent_children = list_directory(drive, parent_id)
        for child in parent_children:
            if child.metadata["title"] == name:
                raise FileExistsError("File already exists")
    parent = {"id": parent_id}
    item = drive.CreateFile(
        {"title": name, "mimeType": FOLDER_MIME_TYPE, "parents": [parent]}
    )
    item.Upload()
    return item.metadata["id"]


def upload_file(
    drive: GoogleDrive, parent_id: str, name: str, filepath: Path, safe: bool = True
):
    if safe:
        parent_children = list_directory(drive, parent_id)
        for child in parent_children:
            if child.metadata["title"] == name:
                raise FileExistsError("File already exists")
    parent = {"id": parent_id}
    item = drive.CreateFile({"title": name, "parents": [parent]})
    item.SetContentFile(filepath)
    item.Upload()
    return item.metadata["id"]


def list_subdirectory_ids(drive: GoogleDrive, parent_id: str) -> list:
    output = []
    for j in list_directory(drive, parent_id):
        if j.metadata["mimeType"] == FOLDER_MIME_TYPE:
            output.append(j.metadata["id"])
    return output


def trash_file(drive: GoogleDrive, file_id: str):
    file = drive.CreateFile({"id": file_id})
    file.Trash()


def delete_file(drive: GoogleDrive, file_id: str):
    file = drive.CreateFile({"id": file_id})
    file.Delete()


def rename_file(drive: GoogleDrive, file_id: str, new_name: str, safe: bool = True):
    file = drive.CreateFile({"id": file_id})
    file.FetchMetadata({"title", "parents"})
    if safe:
        parent_id = file_from_id(drive, file_id).metadata["parents"][0]["id"]
        parent_children = list_directory(drive, parent_id)
        for child in parent_children:
            if child.metadata["title"] == new_name:
                raise FileExistsError("File already exists")
    file.UpdateMetadata({"title": new_name})
    file.Upload()
    return file.metadata["id"]


def move_file(drive: GoogleDrive, file_id: str, new_parent_id: str, safe: bool = True):
    file = drive.CreateFile({"id": file_id})
    file.FetchMetadata()
    if safe:
        new_parent_children = list_directory(drive, new_parent_id)
        for child in new_parent_children:
            if child.metadata["title"] == file.metadata["title"]:
                raise FileExistsError("File already exists")
    file["parents"] = [{"kind": "drive#parentReference", "id": new_parent_id}]
    file.Upload()
    return file.metadata["id"]


def file_from_id(drive: GoogleDrive, file_id: str) -> GoogleDriveFile:
    output = drive.CreateFile({"id": file_id})
    output.FetchMetadata()
    return output


def id_from_path(drive: GoogleDrive, start_dir_id: str, path: str):
    nodes = path.split("/")
    current_dir_id = start_dir_id
    for node in nodes:
        if node.strip() == "":

            continue
        else:
            hit = False
            d = list_directory(drive, current_dir_id)
            for item in d:
                if item.metadata["title"] == node:
                    current_dir_id = item.metadata["id"]
                    hit = True
                    break
            if not hit:
                raise FileNotFoundError("File not found")
    return current_dir_id


def try_create_or_return_id_of_existing_directory(
    drive: GoogleDrive, parent_id: str, name: str
) -> str:
    parent_children = list_directory(drive, parent_id)
    for child in parent_children:
        if child.metadata["title"] == name:
            return child.metadata["id"]
    # this can be a race condition, but it works
    return create_directory(drive, parent_id, name, False)
