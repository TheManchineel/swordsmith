import subprocess
import wmi
import configparser
from json import load, dump
import pythoncom

from .models import Class
from .utils import obs_path, recordings_path, run_in_dir, capitalize_drive_letter


def get_webcam_id() -> str:
    c = wmi.WMI()
    wql = 'SELECT * FROM Win32_PnPEntity WHERE Service = "usbvideo"'
    camera = c.query(wql)[0]
    guid = "{65e8773d-8f56-11d0-a3b9-00a0c9223196}"
    og_id: str = camera.DeviceID.lower()
    id = (
        camera.Name
        + ":\\\\?\\"
        + og_id.replace("\\", "#22")
        + "#22"
        + guid
        + "\\global"
    )
    print(id)
    return id


def check_create_recordings_folder(classroom: Class) -> None:
    if not str(classroom.uuid) in [i.name[-36:] for i in recordings_path.iterdir()]:
        (recordings_path / classroom.dir_name).mkdir()


def update_config_file(classroom: Class):

    try:
        target_recordings_dir = [
            i for i in recordings_path.iterdir() if i.name[-36:] == str(classroom.uuid)
        ][0]
    except IndexError:
        target_recordings_dir = recordings_path / classroom.dir_name
        target_recordings_dir.mkdir()

    basic_config_ini_path = (
        obs_path.parents[2].absolute()
        / "config"
        / "obs-studio"
        / "basic"
        / "profiles"
        / "Swordsmith"
        / "basic.ini"
    )

    basic_config = configparser.ConfigParser()
    basic_config.optionxform = str
    basic_config.read(str(basic_config_ini_path.absolute()), encoding="utf-8-sig")

    basic_config["SimpleOutput"]["FilePath"] = str(
        capitalize_drive_letter(target_recordings_dir.absolute())
    ).replace("\\", "\\\\")

    with open(basic_config_ini_path.absolute(), "w") as config_file:
        basic_config.write(config_file, space_around_delimiters=False)

    scenes_json_path = (
        obs_path.parents[2]
        / "config"
        / "obs-studio"
        / "basic"
        / "scenes"
        / "Swordsmith.json"
    )

    try:
        webcam_id = get_webcam_id()
    except Exception:
        webcam_id = None

    with open(scenes_json_path, "r") as f:
        scenes = load(f)
        if webcam_id is not None:
            for source in scenes["sources"]:
                if source["id"] == "dshow_input":
                    settings = source["settings"]
                    settings["video_device_id"] = settings[
                        "last_video_device_id"
                    ] = webcam_id
    with open(scenes_json_path, "w") as f:
        dump(scenes, f, indent=4)


def launch_obs(classroom: Class):
    pythoncom.CoInitialize()  # Initialize COM for the current thread, required by WMI called in get_webcam_id()
    check_create_recordings_folder(classroom)
    with run_in_dir(obs_path.parent):
        update_config_file(classroom)
        subprocess.call([f"{obs_path}", "-p"])
