"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from typing import Any, Union, Callable, Iterable, Optional, TYPE_CHECKING, Literal
from pathlib import Path
from functools import partial
import os
from threading import RLock
import pp
from datetime import datetime, timedelta
# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.errors import EntryMissingError, SectionMissingError, ValueValidationError, MissingTypusOrSpecError, MissingDefaultValue, UnconvertableTypusError
from gidapptools.gid_config.enums import SpecialTypus
from gidapptools.general_helper.enums import MiscEnum
from gidapptools.gid_config.parser.tokens import Section
from gidapptools.gid_config.parser.ini_parser import BaseIniParser
from gidapptools.gid_config.parser.config_data import ConfigFile
from gidapptools.gid_config.conversion.spec_data import SpecFile, SpecEntry, SpecSection, SpecLoader
from gidapptools.gid_config.conversion.converter_grammar import ConverterSpecData
from gidapptools.gid_config.conversion.conversion_table import ConversionTable, ConfigValueConverter
from gidapptools.general_helper.timing import get_dummy_profile_decorator_in_globals
from gidapptools.gid_signal.interface import get_signal
if TYPE_CHECKING:
    from gidapptools.meta_data.meta_paths.meta_paths_item import MetaPaths
    from gidapptools.custom_types import PATH_TYPE
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]
get_dummy_profile_decorator_in_globals()
THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class SectionAccessor:

    def __init__(self, config: "GidIniConfig", section_name: str) -> None:
        self.config = config
        self.section_name = section_name

    def get(self,
            entry_key: str,
            fallback_entry: Iterable[str] = None,
            default: Any = MiscEnum.NOTHING) -> Any:
        return self.config.get(section_name=self.section_name, entry_key=entry_key, fallback_entry=fallback_entry, default=default)

    def set(self,
            entry_key: str,
            entry_value: Any,
            create_missing_section: bool = False,
            spec_typus: str = None) -> None:
        return self.config.set(section_name=self.section_name, entry_key=entry_key, entry_value=entry_value, create_missing_section=create_missing_section, spec_typus=spec_typus)


class ResolvedSection:

    def __init__(self, config: "GidIniConfig", section_name: str, section_item: Section, spec_Section: SpecSection) -> None:
        self.config = config
        self.name = section_name
        self.item = section_item
        self.spec = spec_Section

    @property
    def entries(self) -> tuple["ResolvedEntry"]:
        _out = []
        for entry in self.spec.entries.values():

            _out.append(self.config.get_entry_item(self.name, entry.name))

        return tuple(_out)

    def __getattr__(self, name: str):
        for sub_item in [self.spec, self.item]:
            try:
                return getattr(sub_item, name)
            except AttributeError:
                pass
        raise AttributeError(name)

    def __repr__(self) -> str:

        return f'{self.__class__.__name__}(section_name={self.name!r})'


class ResolvedEntry:

    def __init__(self, section_name: str, entry_name: str, spec_entry: SpecEntry, converter: ConfigValueConverter, raw_value: str = MiscEnum.NOTHING) -> None:
        self.section_name = section_name
        self.entry_name = entry_name
        self.spec_entry = spec_entry
        self.converter = converter
        self.raw_value = raw_value

    @property
    def value_typus(self) -> str:
        return self.converter.value_typus

    @property
    def description(self) -> str:
        return self.spec_entry.description

    @property
    def verbose_name(self) -> str:
        return self.spec_entry.verbose_name

    @property
    def gui_visible(self) -> bool:
        return self.spec_entry.gui_visible

    @property
    def implemented(self) -> bool:
        return self.spec_entry.implemented

    @property
    def default(self) -> str:
        return self.spec_entry.default

    @property
    def value(self) -> Any:
        _value = self.raw_value

        if _value in {MiscEnum.NOTHING, None} and self.default is not MiscEnum.NOTHING:
            _value = self.spec_entry.default
        if _value is MiscEnum.NOTHING:
            raise MissingDefaultValue(f"No value or default value found for '{self.section_name}.{self.entry_name}'.")
        return self.converter.to_python_value(_value)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(section_name={self.section_name!r}, entry_name={self.entry_name!r})'


class GidIniConfig:
    access_locks_storage: dict[tuple, RLock] = {}

    __slots__ = ("spec",
                 "config",
                 "conversion_table",
                 "empty_is_missing",
                 "_resolve_entry_cache",
                 "changed_signal",
                 "__weakref__")

    def __init__(self,
                 spec_file: SpecFile,
                 config_file: ConfigFile,
                 conversion_table: ConversionTable,
                 empty_is_missing: bool = True) -> None:
        self._resolve_entry_cache: dict[tuple[str, str], ResolvedEntry] = {}
        self.spec = spec_file
        self.config = config_file
        self.conversion_table = conversion_table
        self.empty_is_missing = empty_is_missing
        self.changed_signal = get_signal(key=self.config.name)
        self.spec.changed_signal.connect(self.on_any_changed)
        self.config.add_on_reload_target(self.on_any_changed)

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def is_dev(self) -> bool:
        return os.getenv("is_dev", "false") != "false"

    @property
    def sections(self) -> tuple[ResolvedSection]:
        return tuple(self.get_section(i) for i in self.spec.sections)

    @property
    def section_names(self) -> tuple[str]:
        return tuple(self.spec.sections)

    def clear_cache(self) -> None:
        self._resolve_entry_cache = {}

    def get_section(self, section_name: str) -> ResolvedSection:
        spec_section = self.spec.sections[section_name]
        section_item = self.config.get_section(section_name)

        return ResolvedSection(self, section_name, section_item, spec_section)

    def get_spec_item(self, section_name: str, entry_name: str) -> SpecEntry:
        return self.spec.get_spec_entry(section_name=section_name, entry_name=entry_name)

    def get_converter(self, converter_data: ConverterSpecData) -> ConfigValueConverter:
        return self.conversion_table.get_converter(converter_data=converter_data)

    def get_entry_item(self, section_name: str, entry_name: str) -> ResolvedEntry:
        self.spec.reload_if_changed()
        self.config.reload_if_changed()
        try:
            return self._resolve_entry_cache[(section_name, entry_name)]
        except KeyError:
            pass

        spec_item = self.get_spec_item(section_name=section_name, entry_name=entry_name)
        converter = self.get_converter(spec_item.converter)

        entry_item = ResolvedEntry(section_name=section_name, entry_name=entry_name, spec_entry=spec_item, converter=converter)
        try:
            entry = self.config.get_entry(section_name=section_name, entry_key=entry_name)
            entry_item.raw_value = entry.value
        except EntryMissingError:
            pass
        self._resolve_entry_cache[(section_name, entry_name)] = entry_item
        return entry_item

    def get(self, section_name: str, entry_name: str, default=MiscEnum.NOTHING) -> Any:
        try:
            entry_item = self.get_entry_item(section_name=section_name, entry_name=entry_name)
            return entry_item.value
        except MissingDefaultValue:
            if default is not MiscEnum.NOTHING:
                return default
            raise

    def set(self, section_name: str, entry_name: str, value: Any) -> None:
        spec_item = self.get_spec_item(section_name=section_name, entry_name=entry_name)
        converter = self.get_converter(spec_item.converter)
        self.config.set_value(section_name=section_name, entry_key=entry_name, entry_value=converter.to_config_value(value))
        self.spec.reload_if_changed()
        self.config.reload_if_changed()

    def ensure_section(self, section_name: str) -> None:
        section = Section(section_name)
        self.config.add_section(section)

    def set_if_not_exists(self, section_name: str, entry_name: str, value: Any) -> None:
        existing = self.config.has_key(section_name=section_name, key_name=entry_name)
        if existing is False:
            self.set(section_name=section_name, entry_name=entry_name, value=value)

    def reload(self) -> None:
        self.config.reload()
        self.spec.reload()

    def on_any_changed(self, changeling: Union[ConfigFile, SpecFile] = None) -> None:
        self.clear_cache()
        self.changed_signal.emit(self)

    def __repr__(self) -> str:
        """
        Basic Repr
        !REPLACE!
        """
        return f'{self.__class__.__name__}(name={self.name!r}, spec={self.spec!r}, config={self.config!r}, converter={self.conversion_table!r}, empty_is_missing={self.empty_is_missing!r})'


def preload_config(in_config: "GidIniConfig") -> None:
    for section in in_config.sections:
        in_config.ensure_section(section.name)
        if section.spec.dynamic_entries_allowed is False:
            for entry in section.entries:
                try:
                    in_config.set_if_not_exists(section.name, entry.entry_name, entry.value)
                except MissingDefaultValue:
                    continue
    in_config.config.save()


def get_config(spec_path: "PATH_TYPE",
               config_path: "PATH_TYPE",
               spec_loader: SpecLoader = None,
               config_parser: BaseIniParser = None,
               config_auto_write: bool = True,
               changed_parameter: Union[Literal['size'], Literal['file_hash'], Literal["changed_time"]] = 'changed_time',
               extra_converter: Iterable[ConfigValueConverter] = None,
               empty_is_missing: bool = True,
               preload_ini_file: bool = False):
    conversion_table = ConversionTable(extra_converter=extra_converter)
    spec = SpecFile(spec_path, loader=spec_loader or SpecLoader(), changed_parameter=changed_parameter)
    config = ConfigFile(config_path, parser=config_parser or BaseIniParser(), changed_parameter=changed_parameter, auto_write=config_auto_write)
    config_item = GidIniConfig(spec, config, conversion_table=conversion_table, empty_is_missing=empty_is_missing)

    if preload_ini_file is True:
        preload_config(config_item)
    return config_item


# region[Main_Exec]
if __name__ == '__main__':
    x = get_config(r"D:\Dropbox\hobby\Modding\Programs\Github\My_Repos\GidAppTools\tests\gid_config_tests\data\basic_configspec.json",
                   r"D:\Dropbox\hobby\Modding\Programs\Github\My_Repos\GidAppTools\tests\gid_config_tests\data\basic.ini",
                   preload_ini_file=True)

    print(repr(x.get("first_section", "entry_two")))
# endregion[Main_Exec]
