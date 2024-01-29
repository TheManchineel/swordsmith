from configparser import ConfigParser as cp
from uuid import UUID
from base64 import b64encode

from .utils import data_path, root_path
from .models import Class

config = cp()
config.read((data_path / "config.ini").absolute())
drive_root_id = config["Drive"]["root"]
archived_dir = config["Drive"]["archived_dir"]

if config["Drive"]["fix_missing_folders"] == "True":
    fix_missing = True
else:
    fix_missing = False

classes_conf = cp()
classes_conf.read((data_path / "classes.ini").absolute())

classes_conf_list = classes_conf.sections()

classes: list[Class] = []


def config_to_classes() -> None:
    global classes, classes_conf, classes_conf_list
    classes.clear()
    for i in classes_conf_list:
        class_dict = dict(classes_conf[i])
        class_dict["uuid"] = UUID(i)
        new_class = Class.parse_obj(class_dict)
        classes.append(new_class)


def classes_to_config() -> None:
    global classes, classes_conf, classes_conf_list
    classes_conf.clear()
    for i in classes:
        uuid = str(i.uuid)
        values = i.dict()
        del values["uuid"]
        classes_conf[uuid] = values
    with open((data_path / "classes.ini").absolute(), "w") as f:
        classes_conf.write(f)


with open(root_path / ".swordsmith" / "assets" / "logo.png", "rb") as logo_file:
    encoded_icon = b64encode(logo_file.read())
