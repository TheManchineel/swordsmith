from pydantic import BaseModel, validator
from uuid import UUID
from pydrive2.drive import GoogleDrive
from pathlib import Path
from pymediainfo import MediaInfo
from shutil import rmtree

from .google_drive import id_from_path
from .utils import recordings_path


def get_video_length(file_path: Path | str) -> str | None:
    if isinstance(file_path, Path):
        file_path = str(file_path.absolute())
    try:
        media_info = MediaInfo.parse(file_path)
        duration_ms = media_info.tracks[0].duration
        duration_s = duration_ms / 1000
        duration_h_mm_ss = (
            int(duration_s // 3600),
            int(duration_s // 60 % 60),
            int(duration_s % 60),
        )
        hours = "ore"
        minutes = "minuti"
        seconds = "secondi"
        if duration_h_mm_ss[0] == 1:
            hours = "ora"
        if duration_h_mm_ss[1] == 1:
            minutes = "minuto"
        if duration_h_mm_ss[2] == 1:
            seconds = "secondo"
        return f"{duration_h_mm_ss[0]} {hours}, {duration_h_mm_ss[1]} {minutes}, {duration_h_mm_ss[2]} {seconds}"
    except Exception:
        return None


class Class(BaseModel):
    name: str
    archived: bool = False
    year: str
    uuid: UUID

    @validator("name")
    def validate_name(cls, v):
        return v.upper()

    @validator("year")
    def validate_year(cls, v):
        try:
            int(v)
        except ValueError:
            raise ValueError("Anno non valido")
        return v

    @property
    def year_pair(self):
        return f"{int(self.year)}-{int(self.year) + 1}"

    @property
    def dir_name(self) -> str:
        return f"{self.name} {self.year_pair} - {str(self.uuid)}"

    def get_dir_id(
        self, drive: GoogleDrive, drive_root_id: str, archived_dir: str
    ) -> str:
        if not self.archived:
            return id_from_path(drive, drive_root_id, self.dir_name)
        else:
            return id_from_path(drive, drive_root_id, f"{archived_dir}/{self.dir_name}")

    def is_empty(self):
        try:
            classroom_path = [
                i for i in recordings_path.iterdir() if i.name[-36:] == str(self.uuid)
            ][0]
            if classroom_path.is_dir():
                output = True
                for i in classroom_path.glob("**/*"):
                    if i.is_file():
                        output = False
                        break
                return output
            else:
                return True
        except IndexError:
            return True

    def delete(self):
        try:
            classroom_path = [
                i for i in recordings_path.iterdir() if i.name[-36:] == str(self.uuid)
            ][0]
            rmtree(classroom_path)
        except IndexError:
            pass

    def __str__(self):
        return f"{self.name} ({self.year_pair})"


class Recording(BaseModel):
    path: Path
    classroom: Class
    subject: str | None

    @property
    def duration(self):
        return get_video_length(self.path)

    def delete(self):
        self.path.unlink()

    def __str__(self):
        if self.subject is None:
            return f"{self.path.name} - {str(self.classroom)} ({self.duration})"
        return f"{self.path.name} - {str(self.classroom)} - {self.subject} ({self.duration})"

    def categorize(self, subject: str):
        self.subject = subject
        new_path = self.path.parent / subject / self.path.name
        if not new_path.parent.exists():
            new_path.parent.mkdir(parents=True)
        self.path = self.path.rename(new_path)

    def revert_categorization(self):
        if self.subject is None:
            return
        self.subject = None
        new_path = self.path.parents[1] / self.path.name
        self.path = self.path.rename(new_path)
