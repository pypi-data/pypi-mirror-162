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
from gidapptools.gid_utility.version_item import VersionItem
# * Qt Imports --------------------------------------------------------------------------------------->
import PySide6
from PySide6.QtGui import QIcon, QImage, QPixmap
from PySide6.QtCore import Qt, Slot, QEvent, QObject, QSettings, QUrl
from PySide6.QtWidgets import QWidget, QMainWindow, QMessageBox, QApplication, QSplashScreen, QSystemTrayIcon, QGridLayout, QTabWidget, QTabBar


from yarl import URL


if TYPE_CHECKING:
    from gidapptools.gidapptools_qt.basics.application import GidQtApplication

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class ApplicationInfoData:
    __slots__ = ("_application", "name", "author", "link", "version", "icon")

    def __init__(self, application: Union[QApplication, "GidQtApplication"]) -> None:
        self._application = application
        self.name: str = None
        self.author: Optional[str] = None
        self.link: Optional[URL] = None
        self.version: Optional[VersionItem] = None
        self.icon: Optional[QIcon] = None

    def collect(self) -> "ApplicationInfoData":
        for attr_name in (n for n in self.__slots__ if not n.startswith("_") and n not in {"application"}):
            get_method = getattr(self, f"_get_{attr_name}", None)
            if get_method:
                setattr(self, attr_name, get_method())
        return self

    def _get_name(self) -> str:
        return self._application.applicationDisplayName()

    def _get_author(self) -> str:
        return self._application.organizationName()

    def _get_link(self) -> Optional[URL]:
        raw_link = self._application.organizationDomain()
        if raw_link:
            return URL(raw_link)

    def _get_version(self) -> Optional[VersionItem]:
        raw_version = self._application.applicationVersion()
        if raw_version:
            return VersionItem.from_string(raw_version)

    def _get_icon(self) -> Optional[QIcon]:
        try:
            return self._application.icon
        except AttributeError:
            return self._application.windowIcon()

            # region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
