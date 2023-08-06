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
from gidapptools.general_helper.enums import MiscEnum
import pyparsing as ppa
from pyparsing import common as ppc
from gidapptools.errors import InvalidConverterValue
from gidapptools.general_helper.timing import get_dummy_profile_decorator_in_globals
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]
get_dummy_profile_decorator_in_globals()
THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


REPLACE_WORDS = {"$comma$": ",",
                 "$equals$": "="}


def replace_value_words(in_tok: ppa.ParseResults) -> str:
    text = str(in_tok[0])
    for k, v in REPLACE_WORDS.items():
        text = text.replace(k, v)

    return text


def reverse_replace_value_words(in_value: str) -> str:
    text = str(in_value)
    for k, v in REPLACE_WORDS.items():
        text = text.replace(v, k)
    return text


def get_converter_specification_grammar() -> ppa.ParserElement:
    parenthesis_open = ppa.Literal("(").suppress()
    parenthesis_close = ppa.Literal(")").suppress()

    equal_sign = ppa.Literal("=").suppress()
    comma = ppa.Literal(",").suppress()

    word_value = ppa.Word(''.join(c for c in ppa.printables if c not in {"=", ",", "(", ")"})).set_parse_action(replace_value_words)
    bool_value = ppa.CaselessLiteral("true").set_parse_action(lambda x: True) | ppa.CaselessKeyword("false").set_parse_action(lambda x: False)
    kw_value = ppc.number | bool_value | word_value

    kw_argument = ppa.Group(ppc.identifier + equal_sign + kw_value)

    arguments = ppa.Dict(ppa.ZeroOrMore(kw_argument + ppa.Opt(comma)), asdict=True).set_parse_action(lambda x: x[0])("kw_arguments")

    typus = ppa.Word(ppa.alphas + "_", ppa.alphanums + '_')

    sub_arguments = parenthesis_open + arguments + parenthesis_close

    grammar = typus("typus") + ppa.Opt(sub_arguments)

    return grammar


CONVERTER_SPECIFICATION_GRAMMAR = get_converter_specification_grammar()


class ConverterSpecData(TypedDict):
    typus: str
    kw_arguments: dict[str, Union[str, int, float]]


def parse_specification(raw_specification: str) -> ConverterSpecData:
    try:
        result = CONVERTER_SPECIFICATION_GRAMMAR.parse_string(raw_specification, parse_all=True).as_dict()
        return ConverterSpecData(typus=result["typus"], kw_arguments=result.get("kw_arguments", dict()))
    except ppa.ParseException as error:
        raise InvalidConverterValue(f"{raw_specification!r} is not a valid converter specification") from error


# region[Main_Exec]
if __name__ == '__main__':
    pass
# endregion[Main_Exec]
