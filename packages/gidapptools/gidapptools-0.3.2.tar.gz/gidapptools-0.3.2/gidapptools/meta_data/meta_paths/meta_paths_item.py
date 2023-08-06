"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import shutil
import logging
from pprint import pformat
from typing import Any, Union, Callable, Optional, TypeVar
from pathlib import Path
from tempfile import mkdtemp
from contextlib import contextmanager
from gidapptools.errors import UnknownMetaPathIdentifier, NotImplementedMetaPath
# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.utility.enums import NamedMetaPath
from gidapptools.utility.helper import make_pretty
from gidapptools.abstract_classes.abstract_meta_item import AbstractMetaItem

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]
log = logging.getLogger(__name__)
THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]

_T = TypeVar("_T")


class TempPathStorage(set):

    def discard_non_existing(self) -> None:
        to_discard = tuple(i for i in self if i.exists() is False)

        for item in to_discard:
            self.discard(item)

    def add(self, item: _T) -> None:
        self.discard_non_existing()
        return super().add(item)


class MetaPaths(AbstractMetaItem):

    def __init__(self, code_base_dir: Path, paths: dict[NamedMetaPath, Path]) -> None:
        self.code_base_dir = Path(code_base_dir).resolve()
        self._paths: dict[Union[NamedMetaPath, str], Optional[Path]] = paths
        self._created_normal_paths: set[Path] = set()
        self._created_temp_dirs: TempPathStorage[Path] = TempPathStorage()

    def get_path(self, identifier: Union[NamedMetaPath, str], default: Any = NotImplemented) -> Path:
        if isinstance(identifier, str):
            try:
                identifier = NamedMetaPath(identifier)
            except ValueError as e:
                raise UnknownMetaPathIdentifier(identifier=identifier) from e
        path = self._paths.get(identifier, None)
        if path is None:
            if default is NotImplemented:
                raise NotImplementedMetaPath(identifier=identifier)

            path = Path(default)

        if path.exists() is False:
            path.mkdir(parents=True, exist_ok=True)
            self._created_normal_paths.add(path)
        return path

    @property
    def running_pid_storage_file(self) -> Path:
        return self.get_path(NamedMetaPath.DATA).joinpath(".running_instance")

    @property
    def data_dir(self) -> Path:
        return self.get_path(NamedMetaPath.DATA)

    @property
    def cache_dir(self) -> Path:
        return self.get_path(NamedMetaPath.CACHE)

    @property
    def temp_dir(self) -> Path:
        return self.get_path(NamedMetaPath.TEMP)

    @property
    def log_dir(self) -> Path:
        return self.get_path(NamedMetaPath.LOG)

    @property
    def config_dir(self) -> Path:
        return self.get_path(NamedMetaPath.CONFIG)

    @property
    def config_spec_dir(self) -> Path:
        return self.get_path(NamedMetaPath.CONFIG_SPEC)

    @property
    def db_dir(self) -> Path:
        return self.get_path(NamedMetaPath.DB)

    def _generate_named_temp_dir_path(self, name: str, suffix: str = None, number: int = 0) -> Path:
        _suffix = f"_{suffix}" if suffix is not None else ""
        _number = f"_{number}" if number > 0 else ""
        full_name = f"{name}{_suffix}{_number}"
        return self.temp_dir.joinpath(full_name)

    def get_new_temp_dir(self, suffix: str = None, name: str = None, exists_ok: bool = False) -> Path:
        if name is not None:
            _number = 0
            temp_dir = self._generate_named_temp_dir_path(name, suffix=suffix, number=_number)
            while exists_ok is False and temp_dir.exists():
                _number += 1
                temp_dir = self._generate_named_temp_dir_path(name, suffix=suffix, number=_number)

        else:
            temp_dir = Path(mkdtemp(dir=self.temp_dir, suffix=suffix))

        temp_dir.mkdir(parents=True, exist_ok=True)
        self._created_temp_dirs.add(temp_dir)
        return temp_dir

    @contextmanager
    def context_new_temp_dir(self, suffix: str = None, name: str = None, exists_ok: bool = False):
        temp_dir = self.get_new_temp_dir(suffix=suffix, name=name, exists_ok=exists_ok)
        try:
            yield temp_dir
        finally:
            shutil.rmtree(temp_dir)

    def clean_all_temp(self) -> None:
        self._created_temp_dirs.discard_non_existing()
        while len(self._created_temp_dirs) != 0:
            temp_dir = self._created_temp_dirs.pop()

            shutil.rmtree(temp_dir)

    def as_dict(self, pretty: bool = False) -> dict[str, Any]:

        _out = vars(self)
        if pretty is True:
            _out = make_pretty(self)

        return pformat(_out)

    def to_storager(self, storager: Callable = None) -> None:
        if storager is None:
            return
        storager(self)

    def clean_up(self, remove_all_paths: bool = False, **kwargs) -> None:
        self.clean_all_temp()
        if remove_all_paths is True:
            for path in self._created_normal_paths:
                if path.exists():
                    if kwargs.get('dry_run', False) is True:
                        log.debug("Simulating deleting of temp-folder %r and its contents.", path.as_posix())
                    else:
                        log.info("Deleting temp-folder %r and its contents.", path.as_posix())
                        shutil.rmtree(path)

        self.running_pid_storage_file.unlink(missing_ok=True)
        # TODO: find a way to clean shit up, but completely, also add optional kwarg that also removes the author folder


# region[Main_Exec]
if __name__ == '__main__':
    pass
# endregion[Main_Exec]
