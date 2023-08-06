"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import os
import re
import sys
import queue
import atexit
import logging
import warnings
from typing import TYPE_CHECKING, Any, Union, Mapping, Callable, Iterable
from pathlib import Path
from weakref import WeakValueDictionary
from contextlib import contextmanager
from logging.handlers import QueueHandler, QueueListener

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.gid_logger.enums import LoggingLevel
from gidapptools.gid_logger.handler import GidBaseStreamHandler, GidBaseRotatingFileHandler
from gidapptools.gid_logger.formatter import GidLoggingFormatter, get_all_func_names, get_all_module_names

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


class GidLogger(logging.Logger):

    def __init__(self, name: str, level: "logging._Level" = logging.NOTSET) -> None:
        super().__init__(name, level)
        self.que_listener: QueueListener = None
        self._que_handlers: WeakValueDictionary[str, logging.Handler] = WeakValueDictionary()

    @property
    def all_handlers(self) -> dict[str, tuple[logging.Handler]]:
        return {"handlers": tuple(self.handlers),
                "que_handlers": dict(self._que_handlers)}

    def set_que_listener(self, que_listener: QueueListener):
        def _determine_handler_name(in_handler: logging.Handler) -> str:
            if hasattr(in_handler, "name") and in_handler.name is not None:
                return in_handler.name
            return in_handler.__class__.__name__

        self.que_listener = que_listener
        for handler in que_listener.handlers:
            self._que_handlers[_determine_handler_name(handler)] = handler

    def makeRecord(self,
                   name: str,
                   level: int,
                   fn: str,
                   lno: int,
                   msg: object,
                   args: "logging._ArgsType",
                   exc_info: "logging._SysExcInfoType" = None,
                   func: str = None,
                   extra: Mapping[str, object] = None,
                   sinfo: str = None) -> "LOG_RECORD_TYPES":
        rv = super().makeRecord(name, level, fn, lno, msg, args=args, exc_info=exc_info, func=func, extra=None, sinfo=sinfo)
        if not hasattr(rv, "extras"):
            setattr(rv, "extras", {})
        if extra is not None:
            rv.extras |= extra

        return rv


def make_library_logger(in_name: str) -> logging.Logger:
    logger = logging.getLogger(in_name)
    logger.addHandler(logging.NullHandler())
    return logger


@contextmanager
def switch_logger_klass(logger_klass: type[logging.Logger]):
    original_logger_klass = logging.getLoggerClass()
    try:
        logging.setLoggerClass(logger_klass)
        yield
    finally:
        logging.setLoggerClass(original_logger_klass)


def _modify_logger_name(name: str) -> str:
    if name == "__main__":
        return 'main'
    name = 'main.' + '.'.join(name.split('.')[1:])
    return name


def get_logger(name: str) -> Union[logging.Logger, GidLogger]:
    name = _modify_logger_name(name)
    with switch_logger_klass(GidLogger):
        return logging.getLogger(name)


def get_handlers(logger: Union[logging.Logger, GidLogger] = None) -> tuple[logging.Handler]:
    logger = logger or get_main_logger()
    handlers = logger.handlers
    all_handlers = []
    for handler in handlers:
        all_handlers.append(handler)
    return tuple(all_handlers)


func_pattern = re.compile(r"(^| )def (?P<func_name>[^\(\)\n\"\'\]\[]+)")


class WarningHandler:
    __slots__ = ("old_show_warnings_func",)

    def __init__(self, old_show_warnings_func: Callable = None):
        self.old_show_warnings_func = old_show_warnings_func

    def _error_fallback(self, error, message, category, filename, lineno, file=None, line=None) -> None:
        print(f"error with '_show_warnings', error: {error!r}, message: {message!r}, category: {category!r}, filename: {filename!r}, lineno: {lineno!r}, file: {file!r}, line: {line!r}")

    def _show_warnings(self, message, category, filename, lineno, file=None, line=None):
        try:
            path = Path(filename).resolve()
            sending_module = None
            for module in reversed(sys.modules.values()):
                try:
                    if Path(module.__file__).resolve() == path:
                        sending_module = module
                        break
                except (AttributeError, TypeError):
                    continue
            logger = get_logger(sending_module.__name__)
            import linecache

            temp_lineno = lineno
            while True:
                line = linecache.getline(filename, temp_lineno)
                if match := func_pattern.search(line):
                    func = match.group("func_name").strip()
                    break
                temp_lineno -= 1
                if temp_lineno < 0:
                    func = "module"
                    break

            record = logger.makeRecord(logger.name, level=logging.WARNING, fn=func, lno=lineno, msg=message.rstrip('\n'), args=[], exc_info=None, func=func)
            logger.handle(record)
        except Exception as e:
            if self.old_show_warnings_func:
                self.old_show_warnings_func(message, category, filename, lineno, file, line)
            else:
                self._error_fallback(e, message, category, filename, lineno, file, line)

    def __call__(self, message, category, filename, lineno, file=None, line=None) -> Any:
        self._show_warnings(message, category, filename, lineno, file, line)


def setup_main_logger(name: str,
                      path: Path,
                      log_level: LoggingLevel = LoggingLevel.DEBUG,
                      formatter: Union[logging.Formatter, GidLoggingFormatter] = None,
                      extra_logger: Iterable[str] = tuple(),
                      *,
                      determine_max_module_len: bool = False,
                      determine_max_func_name_len: bool = False) -> Union[logging.Logger, GidLogger]:
    if determine_max_func_name_len:
        os.environ["MAX_FUNC_NAME_LEN"] = str(min([max(len(i) for i in get_all_func_names(path, True)), 20]))
    if determine_max_module_len:
        os.environ["MAX_MODULE_NAME_LEN"] = str(min([max(len(i) for i in get_all_module_names(path)), 20]))

    handler = GidBaseStreamHandler(stream=sys.stdout)

    que = queue.Queue(-1)
    que_handler = QueueHandler(que)
    listener = QueueListener(que, handler)
    formatter = GidLoggingFormatter() if formatter is None else formatter
    handler.setFormatter(formatter)
    _log = get_logger(name)
    for logger in [_log] + [logging.getLogger(l) for l in extra_logger]:
        logger.addHandler(que_handler)

        logger.setLevel(log_level)
    _log.addHandler(que_handler)
    _log.setLevel(log_level)
    listener.start()
    atexit.register(listener.stop)
    return _log


def setup_main_logger_with_file_logging(name: str,
                                        log_file_base_name: str,
                                        path: Path,
                                        log_level: LoggingLevel = LoggingLevel.DEBUG,
                                        formatter: Union[logging.Formatter, GidLoggingFormatter] = None,
                                        log_folder: Path = None,
                                        extra_logger: Iterable[str] = tuple(),
                                        max_func_name_length: int = None,
                                        max_module_name_length: int = None,
                                        *,
                                        log_to_file: bool = True,
                                        log_to_stdout: bool = True) -> Union[logging.Logger, GidLogger]:
    if os.getenv('IS_DEV', "false") != "false":
        log_folder = path.parent.joinpath('logs')

    os.environ["MAX_FUNC_NAME_LEN"] = str(max_func_name_length) if max_func_name_length is not None else str(min([max(len(i) for i in get_all_func_names(path, True)), 25]))
    os.environ["MAX_MODULE_NAME_LEN"] = str(max_module_name_length) if max_module_name_length is not None else str(min([max(len(i) for i in get_all_module_names(path)), 25]))

    que = queue.Queue()
    que_handler = QueueHandler(que)

    formatter = GidLoggingFormatter() if formatter is None else formatter
    endpoints = []
    if log_to_stdout is True:
        handler = GidBaseStreamHandler()
        handler.setFormatter(formatter)
        endpoints.append(handler)
    if log_to_file is True:
        file_handler = GidBaseRotatingFileHandler(base_name=log_file_base_name, log_folder=log_folder)

        file_handler.setFormatter(formatter)
        endpoints.append(file_handler)
    # storing_handler = GidStoringHandler(50)
    # storing_handler.setFormatter(formatter)
    # endpoints.append(storing_handler)
    listener = QueueListener(que, *endpoints)
    _log = get_logger(name)
    log_level = LoggingLevel(log_level)
    if "py.warnings" in extra_logger:
        logging.captureWarnings(True)
        warning_handler = WarningHandler(warnings.showwarning)
        warnings.showwarning = warning_handler
    for logger in [_log] + [logging.getLogger(l) for l in extra_logger]:
        logger.addHandler(que_handler)

        logger.setLevel(log_level)
    listener.start()
    atexit.register(listener.stop)
    _log.set_que_listener(listener)
    return _log


def get_main_logger():
    return get_logger("__main__")
# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
