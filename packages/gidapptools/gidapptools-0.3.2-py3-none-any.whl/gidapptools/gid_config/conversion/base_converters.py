"""
WiP.

Soon.
"""

# region [Imports]

import os
import re
import sys
import json
import queue
import math
import base64
import pickle
import random
import shelve
import dataclasses
import shutil
import asyncio
import logging
import sqlite3
import platform
import importlib
import subprocess
import inspect
from frozendict import frozendict
from time import sleep, process_time, process_time_ns, perf_counter, perf_counter_ns
from io import BytesIO, StringIO
from abc import ABC, ABCMeta, abstractmethod
from copy import copy, deepcopy
from enum import Enum, Flag, auto, unique
from time import time, sleep
from pprint import pprint, pformat
from pathlib import Path
from string import Formatter, digits, printable, whitespace, punctuation, ascii_letters, ascii_lowercase, ascii_uppercase
from timeit import Timer
from typing import TYPE_CHECKING, Union, Callable, Iterable, Optional, Mapping, Any, IO, TextIO, BinaryIO, Hashable, Generator, Literal, TypeVar, TypedDict, AnyStr, Generic
from zipfile import ZipFile, ZIP_LZMA
from datetime import datetime, timezone, timedelta
from tempfile import TemporaryDirectory
from textwrap import TextWrapper, fill, wrap, dedent, indent, shorten
from functools import wraps, partial, lru_cache, singledispatch, total_ordering, cached_property
from importlib import import_module, invalidate_caches
from contextlib import contextmanager, asynccontextmanager, nullcontext, closing, ExitStack, suppress
from statistics import mean, mode, stdev, median, variance, pvariance, harmonic_mean, median_grouped
from collections import Counter, ChainMap, deque, namedtuple, defaultdict
from urllib.parse import urlparse
from gidapptools.general_helper.conversion import bytes2human, human2bytes, str_to_bool, seconds2human, human2timedelta
from importlib.util import find_spec, module_from_spec, spec_from_file_location
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from importlib.machinery import SourceFileLoader
from gidapptools.gid_config.conversion.extra_base_typus import NonTypeBaseTypus
from gidapptools.general_helper.enums import MiscEnum
import weakref
if TYPE_CHECKING:
    from gidapptools.gid_config.conversion.conversion_table import ConversionTable

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class ConfigValueConverter(ABC):
    __slots__ = ("conversion_table",)
    is_standard_converter: bool = False
    value_typus: str = None
    value_typus_aliases: tuple[str] = tuple()
    named_arguments_options: frozendict[str, object] = frozendict()

    def __init__(self, conversion_table: "ConversionTable") -> None:
        self.conversion_table = conversion_table

    def __init_subclass__(cls) -> None:
        if cls.value_typus in {None, ..., "", MiscEnum.NOTHING}:
            raise ValueError(f"{cls.__name__!r} has an invalid value_typus({cls.value_typus!r})")

    @property
    def encode(self):
        return self.to_config_value

    @property
    def decode(self):
        return self.to_python_value

    @abstractmethod
    def to_config_value(self, value: Any) -> str:
        ...

    @abstractmethod
    def to_python_value(self, value: str) -> Any:
        ...

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}'


class IntegerConfigValueConverter(ConfigValueConverter):
    __slots__ = tuple()
    is_standard_converter: bool = True
    value_typus = "integer"
    value_typus_aliases = ("integer",)
    is_default: bool = True

    def to_config_value(self, value: int) -> str:
        if value is None:
            return ""
        return str(value)

    def to_python_value(self, value: str) -> int:
        if value is None:
            return None
        return int(value)


class FloatConfigValueConverter(ConfigValueConverter):
    __slots__ = tuple()
    is_standard_converter: bool = True
    value_typus = "float"
    value_typus_aliases = ("floating_point",)

    def to_config_value(self, value: float) -> str:
        if value is None:
            return ""
        return str(value)

    def to_python_value(self, value: str) -> float:
        if value is None:
            return None
        return float(value)


class BooleanConfigValueConverter(ConfigValueConverter):
    __slots__ = tuple()
    is_standard_converter: bool = True
    value_typus = "boolean"
    value_typus_aliases = ("bool",)
    true_string_value = "yes"
    false_string_value = "no"

    def to_config_value(self, value: bool) -> str:
        if value is None:
            return ""
        if value is True:
            return self.true_string_value

        if value is False:
            return self.false_string_value

    def to_python_value(self, value: str) -> int:
        if value is None:
            return None
        return str_to_bool(str(value))


class StringConfigValueConverter(ConfigValueConverter):
    __slots__ = tuple()
    is_standard_converter: bool = True
    value_typus = "string"
    value_typus_aliases = ("str",)

    def to_config_value(self, value: str) -> str:
        if value is None:
            return ""
        return value

    def to_python_value(self, value: str) -> str:
        if value is None:
            return None
        return value


class DateTimeConfigValueConverter(ConfigValueConverter):
    __slots__ = tuple()
    is_standard_converter: bool = True
    value_typus = "datetime"

    def to_config_value(self, value: datetime) -> str:
        if value is None:
            return ""
        return value.isoformat(timespec="seconds")

    def to_python_value(self, value: str) -> datetime:
        if value is None:
            return None
        return datetime.fromisoformat(value)


class TimedeltaConfigValueConverter(ConfigValueConverter):
    __slots__ = tuple()
    is_standard_converter: bool = True
    value_typus = "timedelta"

    def to_config_value(self, value: timedelta) -> str:
        if value is None:
            return ""
        return seconds2human(value)

    def to_python_value(self, value: str) -> timedelta:
        if value is None:
            return None
        return human2timedelta(value)


class PathConfigValueConverter(ConfigValueConverter):
    __slots__ = ("resolve",)
    is_standard_converter: bool = True
    value_typus = "path"
    value_typus_aliases = ("file_path", "folder_path", "file_system_path")

    def __init__(self, conversion_table: "ConversionTable", resolve: bool = False) -> None:
        super().__init__(conversion_table)
        self.resolve = resolve

    def to_config_value(self, value: Path) -> str:
        if value is None:
            return ""
        path = Path(value)
        if self.resolve is True:
            path = path.resolve()
        return path.as_posix()

    def to_python_value(self, value: str) -> Path:
        if value is None:
            return None
        path = Path(value)
        if self.resolve is True:
            path = path.resolve()
        return path


class FileSizeConfigValueConverter(ConfigValueConverter):
    __slots__ = ()
    is_standard_converter: bool = True
    value_typus: str = "file_size"

    def to_config_value(self, value: int) -> str:
        if value is None:
            return ""
        return bytes2human(value)

    def to_python_value(self, value: str) -> int:
        if value is None:
            return None

        return human2bytes(value)


class ListConfigValueConverter(ConfigValueConverter):
    __slots__ = ("sub_typus", "split_char")
    is_standard_converter: bool = True
    value_typus = "list"

    def __init__(self, conversion_table: "ConversionTable", sub_typus: str = "string", split_char: str = ",") -> None:
        super().__init__(conversion_table)
        self.sub_typus = sub_typus
        self.split_char = split_char

    def to_config_value(self, value: list) -> str:
        if value is None:
            return ""
        sub_converter: "ConfigValueConverter" = self.conversion_table.converters[self.sub_typus](self.conversion_table)
        return f"{self.split_char} ".join(sub_converter.to_config_value(item) for item in value)

    def to_python_value(self, value: str) -> list:
        if value is None:
            return None
        sub_converter: "ConfigValueConverter" = self.conversion_table.converters[self.sub_typus](self.conversion_table)
        return [sub_converter.to_python_value(item) for item in value.split(self.split_char) if item.strip()]


def get_standard_converter() -> tuple[type["ConfigValueConverter"]]:
    return tuple(sc for sc in ConfigValueConverter.__subclasses__() if sc.is_standard_converter is True)


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
