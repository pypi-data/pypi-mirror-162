"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import os
import re
import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Union
from pathlib import Path
from datetime import datetime, timezone
from collections import deque
from logging.handlers import BaseRotatingHandler

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.general_helper.enums import MiscEnum
from gidapptools.general_helper.conversion import human2bytes
from gidapptools.general_helper.regex.datetime_regex import datetime_format_to_regex

# * Type-Checking Imports --------------------------------------------------------------------------------->
if TYPE_CHECKING:
    from gidapptools.custom_types import PATH_TYPE
    from gidapptools.gid_logger.records import LOG_RECORD_TYPES

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


DEFAULT_MAX_BYTES = human2bytes("5 mb")


class BaseFileNameTemplate(ABC):

    def __init__(self, base_name: str, suffix: str = ".log") -> None:
        self.base_name = base_name
        self.suffix = suffix

    @abstractmethod
    def format(self) -> str:
        ...

    @abstractmethod
    def make_backup_file_path(self, in_name: str, backup_folder: Path) -> Path:
        ...

    @abstractmethod
    def is_same_kind_log_file(self, other_file: Path) -> bool:
        ...

    @abstractmethod
    def is_backup_log_file(self, other_file: Path) -> bool:
        ...


class TimestampFileNameTemplate(BaseFileNameTemplate):
    format_template: str = "{base_name}_{timestamp}{suffix}"

    def __init__(self, base_name: str, suffix: str = ".log", time_zone: timezone = None, timestamp_format: str = None) -> None:
        super().__init__(base_name=base_name, suffix=suffix)
        self.time_zone = time_zone
        self.timestamp_format = timestamp_format or self._get_default_timestamp_format()
        self.timestamp_regex = datetime_format_to_regex(self.timestamp_format, re.IGNORECASE)

    def _get_default_timestamp_format(self) -> str:
        return "%Y-%m-%d_%H-%M-%S_%Z" if self.time_zone is not None else "%Y-%m-%d_%H-%M-%S"

    def get_timestamp(self) -> str:
        now = datetime.now(tz=self.time_zone)
        return now.strftime(self.timestamp_format)

    def format(self) -> str:
        return self.format_template.format(base_name=self.base_name, timestamp=self.get_timestamp(), suffix=self.suffix)

    def make_backup_file_path(self, in_name: str, backup_folder: Path) -> Path:
        return backup_folder.joinpath(in_name)

    def is_same_kind_log_file(self, other_file: Path) -> bool:
        if other_file.suffix != self.suffix:
            return False

        date_time_match = self.timestamp_regex.search(other_file.stem)
        if not date_time_match:
            return False
        base_name = other_file.stem[:date_time_match.start()].rstrip("_")

        if base_name == self.base_name:
            return True

        return False

    def is_backup_log_file(self, other_file: Path) -> bool:
        return self.is_same_kind_log_file(other_file=other_file)


class GidBaseRotatingFileHandler(BaseRotatingHandler):

    def __init__(self,
                 base_name: str,
                 log_folder: "PATH_TYPE",
                 file_name_template: Union[str, Any] = None,
                 backup_folder: "PATH_TYPE" = MiscEnum.AUTO,
                 rotate_on_start: bool = True,
                 backup_amount_limit: int = 3) -> None:
        self.base_name = base_name
        self.file_name_template = TimestampFileNameTemplate(self.base_name) if file_name_template is None else file_name_template
        self.log_folder = Path(log_folder)
        self.backup_folder = self.log_folder.joinpath("old_logs") if backup_folder is MiscEnum.AUTO else Path(backup_folder)
        self.rotate_on_start = rotate_on_start
        self.backup_amount_limit = backup_amount_limit
        self.full_file_path: Path = self._construct_full_file_path()
        self.first_record_emited: bool = False
        super().__init__(self.full_file_path, "a", encoding="utf-8", delay=True, errors="ignore")

    def emit(self, record) -> None:
        with self.lock:
            if self.first_record_emited is False:
                self.on_start_rotation()
                self.first_record_emited = True

        return super().emit(record)

    def _construct_full_file_path(self) -> Path:
        name = self.file_name_template.format()
        full_path = self.log_folder.joinpath(name)

        return full_path

    def _get_old_logs(self) -> tuple[Path]:
        def _is_old_log(_in_file: Path) -> bool:
            return _in_file.is_file() and self.file_name_template.is_same_kind_log_file(_in_file)

        _out = tuple(file for file in tuple(self.log_folder.iterdir()) if _is_old_log(file) is True)

        return _out

    def _get_backup_logs(self) -> list[Path]:
        if self.backup_folder.exists() is False:
            return []

        def _is_old_backup(_in_file: Path) -> bool:
            return _in_file.is_file() and self.file_name_template.is_backup_log_file(_in_file)

        _out = sorted((file for file in self.backup_folder.iterdir() if _is_old_backup(file)), key=lambda x: x.stat().st_mtime)
        return _out

    def on_start_rotation(self) -> None:
        try:
            self.acquire()
            self.full_file_path.parent.mkdir(exist_ok=True, parents=True)
            for file in self._get_old_logs():
                self.move_file_to_backup_folder(file)
            self.remove_excess_backup_files()

        finally:
            self.release()

    def remove_excess_backup_files(self) -> None:
        if self.backup_amount_limit is None:
            return
        backup_logs = self._get_backup_logs()
        while len(backup_logs) > self.backup_amount_limit:
            to_delete: Path = backup_logs.pop(0)
            to_delete.unlink(missing_ok=True)

    def move_file_to_backup_folder(self, file: Path) -> None:
        self.backup_folder.mkdir(parents=True, exist_ok=True)
        number = 0
        target_path = self.file_name_template.make_backup_file_path(file.name, self.backup_folder)

        while target_path.exists() is True:
            number += 1
            name = f"{file.stem}_{number}{file.suffix}"
            target_path = self.backup_folder.joinpath(name)
        os.rename(src=file, dst=target_path)

    def shouldRollover(self, record: logging.LogRecord) -> bool:
        return False


class GidBaseStreamHandler(logging.StreamHandler):

    def __init__(self, stream=None):
        super().__init__(stream=stream)


LOG_DEQUE_TYPE = deque["LOG_RECORD_TYPES"]


class GidStoringHandler(logging.Handler):

    def __init__(self, max_storage_size: int = None) -> None:
        super().__init__()
        self.debug_messages: "LOG_DEQUE_TYPE" = deque(maxlen=max_storage_size)
        self.info_messages: "LOG_DEQUE_TYPE" = deque(maxlen=max_storage_size)
        self.warning_messages: "LOG_DEQUE_TYPE" = deque(maxlen=max_storage_size)
        self.critical_messages: "LOG_DEQUE_TYPE" = deque(maxlen=max_storage_size)
        self.error_messages: "LOG_DEQUE_TYPE" = deque(maxlen=max_storage_size)
        self.other_messages: "LOG_DEQUE_TYPE" = deque(maxlen=max_storage_size)

        self.table = {'CRITICAL': self.critical_messages,
                      'FATAL': self.critical_messages,
                      'ERROR': self.error_messages,
                      'WARN': self.warning_messages,
                      'WARNING': self.warning_messages,
                      'INFO': self.info_messages,
                      'DEBUG': self.debug_messages,
                      "OTHER": self.other_messages}

    def set_max_storage_size(self, max_storage_size: int = None):
        for store in self.table.values():
            store.maxlen = max_storage_size

    def emit(self, record: "LOG_RECORD_TYPES") -> None:

        target = self.table.get(record.levelname, self.other_messages)

        target.append(record)

    def get_stored_messages(self) -> dict[str, tuple["LOG_RECORD_TYPES"]]:
        _out = {}
        for level, store in self.table.items():
            _out[level] = tuple(store)

        return _out

    def get_formated_messages(self) -> dict[str, tuple[str]]:
        _out = {}
        for level, store in self.table.items():
            _out[level] = tuple(self.format(r) for r in store)
        return _out

    def __len__(self) -> int:
        _out = 0
        for store in self.table.values():
            _out += len(store)
        return _out
# region[Main_Exec]


if __name__ == '__main__':
    pass
# endregion[Main_Exec]
