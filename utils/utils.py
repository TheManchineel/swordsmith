from os import chdir as cd
from contextlib import contextmanager
from pathlib import Path, WindowsPath
from random import choice


@contextmanager
def run_in_dir(path: Path):
    old_dir = Path.cwd()
    cd(path)
    yield
    cd(old_dir)


def check_illegal_characters_in_path(path: Path | str) -> bool:
    if isinstance(path, Path):
        path = path.absolute()
    illegal_names = [
        "CON",
        "PRN",
        "AUX",
        "NUL",
        "COM1",
        "COM2",
        "COM3",
        "COM4",
        "COM5",
        "COM6",
        "COM7",
        "COM8",
        "COM9",
        "LPT1",
        "LPT2",
        "LPT3",
        "LPT4",
        "LPT5",
        "LPT6",
        "LPT7",
        "LPT8",
        "LPT9",
    ]
    illegal_characters = ['"', "'", ":", "*", "?", "\\", "/", "<", ">", "|"]

    for i in illegal_characters:
        if i in path:
            return True
    for i in illegal_names:
        if path.upper() == i:
            return True
    return False


def classes_by_archived(classes: list, archived: bool) -> list:
    return [i for i in classes if i.archived == archived]


root_path = Path(__file__).parents[2]

data_path = root_path / ".data"

obs_path = root_path / ".obs" / "bin" / "64bit" / "obs64.exe"

recordings_path = root_path / "Registrazioni"


def capitalize_drive_letter(input: str | WindowsPath) -> str:
    if isinstance(input, WindowsPath):
        input = str(input.absolute())
    return input[0].upper() + input[1:]


def get_all_quotes() -> list[tuple[str, str]]:
    with open(root_path / ".swordsmith" / "assets" / "quotes.txt", encoding="utf-8") as f:
        quote_lines = f.readlines()
        quotes = []
        for line in quote_lines:
            if line.strip() == "" or line.strip().startswith("#"):
                continue
            raw_quote = line.strip()
            quote_text = (" — ".join((raw_quote.split(" - ")[:-1]))).replace(
                "\\n", "\n"
            )
            quote_author = raw_quote.split(" - ")[-1]
            quotes.append((quote_text, quote_author))
        return quotes


def get_random_quote():
    quotes = get_all_quotes()
    return choice(quotes)
