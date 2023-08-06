"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from pathlib import Path
from threading import Lock, RLock


# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.custom_types import LOCK_TYPE, PATH_TYPE

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class FileLocksManager:

    def __init__(self, lock_type: LOCK_TYPE):
        self._lock_type = lock_type
        self._interaction_lock: Lock = Lock()
        self._file_locks: dict[Path, LOCK_TYPE] = {}

    def _handle_file_path(self, file_path: PATH_TYPE) -> Path:
        return Path(file_path).resolve()

    def _get_or_create(self, file_path: PATH_TYPE) -> LOCK_TYPE:
        file_path = self._handle_file_path(file_path=file_path)
        with self._interaction_lock:
            try:
                return self._file_locks[file_path]
            except KeyError:
                file_lock = self._lock_type()
                self._file_locks[file_path] = file_lock
                return file_lock

    def get_file_lock(self, file_path: PATH_TYPE) -> LOCK_TYPE:
        return self._get_or_create(file_path=file_path)

    def __getitem__(self, file_path: PATH_TYPE) -> LOCK_TYPE:
        return self.get_file_lock(file_path=file_path)

    def __len__(self) -> int:
        with self._interaction_lock:
            return len(self._file_locks)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(lock_type={self._lock_type!r})"


GLOBAL_LOCK_MANAGER = FileLocksManager(Lock)
GLOBAL_RLOCK_MANAGER = FileLocksManager(RLock)


class PathSpecificLock:
    _selection_lock = Lock()
    _lock_registry: dict[Path, "PathSpecificLock"] = {}

    def __new__(cls, path: Path) -> Lock:
        with cls._selection_lock:
            if path not in cls._lock_registry:
                cls._lock_registry[path] = Lock()

            return cls._lock_registry[path]


class PathSpecificRLock:
    _selection_lock = Lock()
    _lock_registry: dict[Path, "PathSpecificLock"] = {}

    def __new__(cls, path: Path) -> RLock:
        with cls._selection_lock:
            if path not in cls._lock_registry:
                cls._lock_registry[path] = RLock()

            return cls._lock_registry[path]


# region[Main_Exec]
if __name__ == '__main__':
    pass
# endregion[Main_Exec]
