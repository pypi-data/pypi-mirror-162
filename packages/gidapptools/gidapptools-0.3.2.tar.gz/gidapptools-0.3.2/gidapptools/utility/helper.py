"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import sys
import json
import inspect
from abc import abstractmethod
from enum import Enum
from typing import Any, Mapping, TypeVar, Callable, Optional
from pathlib import Path
from datetime import datetime, timezone
from importlib.metadata import metadata, PackageMetadata

# * Third Party Imports --------------------------------------------------------------------------------->
import psutil
from yarl import URL
from platformdirs import PlatformDirs

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.custom_types import PATH_TYPE
from gidapptools.utility.enums import NamedMetaPath
from gidapptools.general_helper.date_time import DatetimeFmt
import pp
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class PackageMetadataDict(dict):
    list_fields: set[str] = {"dynamic",
                             "platform",
                             "supported-platform",
                             "classifier",
                             "requires-dist",
                             "requires-external",
                             "project-url",
                             "provides-extra",
                             "provides-dist",
                             "obsoletes-dist"}

    get_fallback_keys: dict[str, tuple[str]] = {"maintainer": ("author",)}

    def add(self, k, v) -> None:
        k = k.casefold()

        if k in self.list_fields:
            try:
                v = self[k] + [v]
            except KeyError:
                v = [v]

        super().__setitem__(k, v)

    def __getitem__(self, k):
        try:
            return super().__getitem__(k)
        except KeyError as e:
            if k in self.get_fallback_keys:
                for fallback_k in self.get_fallback_keys[k]:
                    try:
                        return super().__getitem__(fallback_k)
                    except KeyError:
                        continue
        raise KeyError(k)

    @classmethod
    def from_meta_importlib_meta_data(cls, importlib_meta_data: PackageMetadata) -> "PackageMetadataDict":
        instance = cls()
        for k, v in importlib_meta_data.items():
            instance.add(k, v)
        return instance


def abstract_class_property(func):
    return property(classmethod(abstractmethod(func)))


def utc_now():
    return datetime.now(tz=timezone.utc)


def handle_path(path: Optional[PATH_TYPE]):
    if path is None:
        return path
    return Path(path).resolve()


def memory_in_use():
    memory = psutil.virtual_memory()
    return memory.total - memory.available


def meta_data_from_path(in_path: Path) -> dict[str, Any]:
    _init_module = inspect.getmodule(None, in_path)

    _metadata = metadata(_init_module.__package__)

    _out = PackageMetadataDict.from_meta_importlib_meta_data(_metadata)

    return _out


TCallable = TypeVar("TCallable", bound=Callable)


def mark_appdir_path(func: TCallable) -> TCallable:
    func._appdir_path_type = NamedMetaPath(func.__name__)
    return func


class PathLibAppDirs:
    mark_path = mark_appdir_path

    def __init__(self,
                 appname: str,
                 appauthor: str = None,
                 version: str = None,
                 roaming: bool = True,
                 multipath: bool = False) -> None:
        self.platform_dirs = PlatformDirs(appname=appname, appauthor=appauthor, version=version, roaming=roaming, multipath=multipath)

    @property
    def appname(self) -> str:
        return self.platform_dirs.appname

    @property
    def authorname(self) -> Optional[str]:
        return self.platform_dirs.appauthor

    @mark_appdir_path
    def user_data_dir(self) -> Path:
        return Path(self.platform_dirs.user_data_path)

    @mark_appdir_path
    def user_log_dir(self) -> Path:
        return Path(self.platform_dirs.user_log_path)

    @mark_appdir_path
    def user_cache_dir(self) -> Path:
        return Path(self.platform_dirs.user_cache_path)

    @mark_appdir_path
    def user_config_dir(self) -> Path:
        return Path(self.platform_dirs.user_config_path)

    @mark_appdir_path
    def user_state_dir(self) -> Path:
        return Path(self.platform_dirs.user_state_path)

    @mark_appdir_path
    def site_data_dir(self) -> Path:
        return Path(self.platform_dirs.user_data_path)

    @mark_appdir_path
    def site_config_dir(self) -> Path:

        return Path(self.platform_dirs.site_config_path)

    def as_path_dict(self) -> dict[NamedMetaPath, Optional[Path]]:
        path_dict = {named_path_item: None for named_path_item in NamedMetaPath.__members__.values()}
        for meth_name, meth_object in inspect.getmembers(self, inspect.ismethod):
            if hasattr(meth_object, '_appdir_path_type'):
                path_dict[meth_object._appdir_path_type] = meth_object()
        return path_dict


def make_pretty(inst) -> dict:

    # pylint: disable=too-many-return-statements
    def _make_pretty(obj):

        def _handle_iterable(in_obj):
            return [_make_pretty(item) for item in in_obj]

        if isinstance(obj, Enum):
            return str(obj)

        if isinstance(obj, Path):
            return obj.as_posix()
        if isinstance(obj, URL):
            return str(obj)
        if isinstance(obj, datetime):
            return DatetimeFmt.STANDARD.strf(obj)

        if isinstance(obj, Mapping):
            pretty_dict = {}
            for key, value in obj.items():
                pretty_dict[_make_pretty(key)] = getattr(inst, f"pretty_{key}", _make_pretty(value))
            return pretty_dict

        if isinstance(obj, list):
            return _handle_iterable(obj)

        if isinstance(obj, tuple):
            return tuple(_handle_iterable(obj))
        if isinstance(obj, set):
            return set(_handle_iterable(obj))
        if isinstance(obj, frozenset):
            return frozenset(_handle_iterable(obj))
        return obj
    return _make_pretty(vars(inst))


def get_qualname_or_name(in_object: Any) -> str:
    try:
        return in_object.__qualname__
    except AttributeError:
        return in_object.__name__


def merge_json_files(base_file: Path, file_to_merge: Path, content_type: type = dict):
    if content_type is not dict:
        raise TypeError(f"function not Implemented for type {content_type!r}")
    with base_file.open("r", encoding='utf-8', errors='ignore') as f_b:
        data_b = json.load(f_b)
    with file_to_merge.open("r", encoding='utf-8', errors='ignore') as f_m:
        data_m = json.load(f_m)

    combined = data_b | data_m

    with base_file.open("w", encoding='utf-8', errors='ignore') as f:
        json.dump(combined, f, default=str, sort_keys=False)


def merge_content_to_json_file(base_file: Path, content: str):
    base_data = json.loads(base_file.read_text(encoding='utf-8', errors='ignore'))
    merge_data = json.loads(content)
    combined_data = base_data | merge_data
    with base_file.open("w", encoding='utf-8', errors='ignore') as f:
        json.dump(combined_data, f, default=str, sort_keys=False, indent=4)


def get_main_module_path() -> Path:
    main_module = sys.modules["__main__"]

    return Path(main_module.__file__).resolve()


# region[Main_Exec]
if __name__ == '__main__':
    print(PathLibAppDirs("woof").as_path_dict())
# endregion[Main_Exec]
