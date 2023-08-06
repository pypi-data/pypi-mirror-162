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
from typing import TYPE_CHECKING, Union, Callable, Iterable, Optional, Mapping, Any, IO, TextIO, BinaryIO, Hashable, Generator, Literal, TypeVar, TypedDict, AnyStr
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
from importlib.util import find_spec, module_from_spec, spec_from_file_location
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from importlib.machinery import SourceFileLoader
import attrs
from gidapptools.general_helper.enums import MiscEnum
from gidapptools.gid_config.conversion.converter_grammar import ConverterSpecData, reverse_replace_value_words
if TYPE_CHECKING:
    from gidapptools.gid_config.conversion.base_converters import ConfigValueConverter

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class SpecSection:
    __slots__ = ("name",
                 "default_converter",
                 "description",
                 "dynamic_entries_allowed",
                 "gui_visible",
                 "implemented",
                 "verbose_name",
                 "entries")

    def __init__(self,
                 name: str,
                 default_converter: ConverterSpecData = MiscEnum.NOTHING,
                 description: str = "",
                 dynamic_entries_allowed: bool = False,
                 gui_visible: bool = True,
                 implemented: bool = True,
                 verbose_name: str = MiscEnum.NOTHING) -> None:
        self.name = name
        self.default_converter = default_converter
        self.description = description
        self.dynamic_entries_allowed = dynamic_entries_allowed
        self.gui_visible = gui_visible
        self.implemented = implemented
        self.verbose_name = verbose_name if verbose_name is not MiscEnum.NOTHING else self.name.replace("_", " ").title()
        self.entries: dict[str, "SpecEntry"] = {}

    def __getitem__(self, name: str) -> "SpecEntry":
        return self.entries[name]

    def add_entry(self, entry: "SpecEntry") -> None:
        entry.set_section(self)
        self.entries[entry.name] = entry

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(name={self.name!r})'


def converter_data_to_string(converter_data: "ConverterSpecData") -> str:
    text = converter_data["typus"]
    if converter_data["kw_arguments"]:
        sub_args = []
        for k, v in converter_data["kw_arguments"].items():
            sub_args.append(f"{k}={reverse_replace_value_words(v)}")

        text += "(" + ', '.join(sub_args) + ")"
    return text


class SpecEntry:
    __slots__ = ("name",
                 "converter",
                 "default",
                 "description",
                 "gui_visible",
                 "implemented",
                 "verbose_name",
                 "_section")

    def __init__(self,
                 name: str,
                 converter: ConverterSpecData = MiscEnum.NOTHING,
                 default: str = MiscEnum.NOTHING,
                 description: str = "",
                 verbose_name: str = MiscEnum.NOTHING,
                 implemented: bool = True,
                 gui_visible: bool = True) -> None:
        self.name = name
        self.converter = converter
        self.default = default
        self.description = description
        self.verbose_name = verbose_name if verbose_name is not MiscEnum.NOTHING else self.name.replace("_", " ").title()
        self.implemented = implemented
        self.gui_visible = gui_visible
        self._section: SpecSection = None

    @property
    def section(self) -> Optional[SpecSection]:
        return self._section

    def set_section(self, section: SpecSection) -> None:
        self._section = section
        if self.converter is MiscEnum.NOTHING and self.section.default_converter is not MiscEnum.NOTHING:
            self.converter = self.section.default_converter

        if self.section.gui_visible is False:
            self.gui_visible = False

        if self.section.implemented is False:
            self.implemented = False

    def __getitem__(self, name: str):
        if name in {"name", "converter", "default", "description", "verbose_name", "implemented", "gui_visible"}:
            return getattr(self, name)
        raise KeyError(name)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(name={self.name!r})'


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
