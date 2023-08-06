"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import re
import sys
import logging
from typing import TYPE_CHECKING, Any
from pathlib import Path

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.gid_logger.logger import get_logger

# * Type-Checking Imports --------------------------------------------------------------------------------->
if TYPE_CHECKING:
    from gidapptools.gid_logger.records import LOG_RECORD_TYPES

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class ProhibitiveSingletonMeta(type):
    _instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is not None:
            raise RuntimeError(f"There can only be one instance of {cls.__name__}")
        cls._instance = super(ProhibitiveSingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instance


class QtMessageHandler(metaclass=ProhibitiveSingletonMeta):
    received_records: list["LOG_RECORD_TYPES"] = []

    def __init__(self) -> None:
        self.msg_split_regex = re.compile(r"(?P<q_class>.*)\:\:(?P<q_method>.*)\:(?P<actual_message>.*)")

    def install(self) -> "QtMessageHandler":
        from PySide6.QtCore import qInstallMessageHandler
        qInstallMessageHandler(self)
        return self

    def mode_to_log_level(self, in_mode):
        in_mode = str(in_mode).rsplit('.', maxsplit=1)[-1].strip().removeprefix("Qt").removesuffix("Msg").upper()
        if in_mode == "FATAL":
            in_mode = "ERROR"
        elif in_mode == "SYSTEM":
            in_mode = "INFO"
        return logging.getLevelName(in_mode)

    def get_context(self, in_context: None):
        frame = sys._getframe(2)
        _context_data = {"fn": in_context.file or frame.f_code.co_filename,
                         "func": in_context.function or frame.f_code.co_name,
                         "lno": in_context.line or frame.f_lineno}

        _logger = get_logger(frame.f_globals["__name__"])
        return _context_data, _logger

    def modify_message(self, in_msg: str) -> str:

        if re_match := self.msg_split_regex.match(in_msg):
            named_parts = re_match.groupdict()
            _message = named_parts.pop("actual_message").strip()
            return _message, {"is_qt": True} | named_parts

        return in_msg, {"is_qt": True}

    def __call__(self, mode, context, message) -> Any:
        context_data, logger = self.get_context(context)
        log_level = self.mode_to_log_level(mode)
        msg, extras = self.modify_message(message)
        record = logger.makeRecord(logger.name, log_level, msg=msg, extra=extras, exc_info=None, args=None, ** context_data)
        logger.handle(record)
        self.received_records.append(record)


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
