"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import os
from typing import ClassVar
from pathlib import Path

# * Third Party Imports --------------------------------------------------------------------------------->
import attrs
import psutil

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.errors import ApplicationInstanceAlreadyRunningError
from gidapptools.custom_types import PATH_TYPE

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


@attrs.define(frozen=True, slots=True)
class LockFileData:
    text_separator: ClassVar[str] = "|:|"
    app_name: str = attrs.field()
    pid: int = attrs.field()

    @property
    def is_running(self) -> bool:
        return psutil.pid_exists(self.pid)

    @classmethod
    def from_file(cls, file_path: PATH_TYPE) -> "LockFileData":
        content = Path(file_path).resolve().read_text(encoding='utf-8', errors='ignore').strip()
        app_name, raw_pid = (p.strip() for p in content.split(cls.text_separator))
        pid = int(raw_pid)
        return cls(app_name=app_name, pid=pid)

    def to_text(self) -> str:
        return f"{self.app_name}{self.text_separator}{self.pid}"


class SingleRunningInstanceRestrictor:
    _lock_file_name: str = ".running_instance"

    def __init__(self, storage_folder: PATH_TYPE, app_name: str) -> None:
        self._storage_folder = Path(storage_folder).resolve()
        self._app_name = app_name
        self._pid = os.getpid()
        self._current_process_lock_file_data = LockFileData(app_name=self._app_name, pid=self._pid)

    @property
    def lock_file_path(self) -> Path:
        return self._storage_folder / self._lock_file_name

    @property
    def lock_file_exists(self) -> bool:
        return self.lock_file_path.is_file()

    def get_existing_lock_file_data(self) -> LockFileData:
        return LockFileData.from_file(self.lock_file_path)

    def store_in_lock_file(self) -> None:
        self.lock_file_path.parent.mkdir(exist_ok=True, parents=True)
        self.lock_file_path.write_text(self._current_process_lock_file_data.to_text())

    def on_other_instance_running(self):
        other_instance_data = self.get_existing_lock_file_data()
        raise ApplicationInstanceAlreadyRunningError(app_name=other_instance_data.app_name, running_pid=other_instance_data.pid)

    def aquire(self):
        if self.lock_file_exists is True:
            existing_instance_data = self.get_existing_lock_file_data()
            if existing_instance_data.is_running is True and existing_instance_data.app_name == self._app_name:
                self.on_other_instance_running()
        else:
            self.store_in_lock_file()

    def release(self):
        self.lock_file_path.unlink(missing_ok=True)

    def __enter__(self) -> None:
        self.aquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
