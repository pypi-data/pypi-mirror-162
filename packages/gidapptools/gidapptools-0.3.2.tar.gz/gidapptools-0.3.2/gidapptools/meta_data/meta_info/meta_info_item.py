"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import os
import sys
import platform
from typing import Any, Union, Callable, Optional, TYPE_CHECKING
from pathlib import Path
from datetime import datetime, timezone
from functools import cached_property

# * Third Party Imports --------------------------------------------------------------------------------->
import attr
from yarl import URL
from tzlocal import get_localzone

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.gid_utility import VersionItem
from gidapptools.utility.enums import OperatingSystem
from gidapptools.utility.helper import utc_now, make_pretty, memory_in_use
from gidapptools.general_helper.general import is_frozen
from gidapptools.general_helper.date_time import DatetimeFmt
from gidapptools.general_helper.conversion import bytes2human
from gidapptools.general_helper.string_helper import StringCase, StringCaseConverter
from gidapptools.abstract_classes.abstract_meta_item import AbstractMetaItem

if TYPE_CHECKING:
    from gidapptools.meta_data.meta_info.meta_info_factory import License
# endregion[Imports]

# region [TODO]

# - Make into a class

# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()


# endregion[Constants]

def url_converter(in_url: Optional[str]) -> Optional[URL]:
    if in_url is None:
        return in_url
    return URL(in_url)


def many_url_converter(in_urls: Optional[dict[str, str]]) -> Optional[dict[str, URL]]:
    if in_urls is None:
        return in_urls
    return {k: URL(v) for k, v in in_urls.items()}


def version_converter(in_version: Union[str, VersionItem]) -> VersionItem:
    if isinstance(in_version, VersionItem):
        return in_version
    return VersionItem.from_string(in_version)


@attr.s(auto_attribs=True, auto_detect=True, kw_only=True, frozen=True)
class MetaInfo(AbstractMetaItem):
    app_name: str = attr.ib(default="python_script")
    app_author: str = attr.ib(default=None)
    version: VersionItem = attr.ib(default=None, converter=version_converter)
    url: URL = attr.ib(converter=url_converter, default=None)
    other_urls: dict[str, URL] = attr.ib(converter=many_url_converter, default=dict())
    pid: int = attr.ib(factory=os.getpid)
    os: OperatingSystem = attr.ib(factory=OperatingSystem.determine_operating_system)
    os_release: str = attr.ib(factory=platform.release)
    python_version: VersionItem = attr.ib(factory=platform.python_version, converter=version_converter)
    started_at: datetime = attr.ib(factory=utc_now)
    base_mem_use: int = attr.ib(default=memory_in_use())
    is_dev: bool = attr.ib(default=None, converter=attr.converters.default_if_none(False))
    is_gui: bool = attr.ib(default=None, converter=attr.converters.default_if_none(False))
    local_tz: timezone = attr.ib(default=get_localzone())
    summary: str = attr.ib(default=None)
    app_license: "License" = attr.ib(default=None)
    description: str = attr.ib(default=None)

    @cached_property
    def is_frozen_app(self) -> bool:
        return is_frozen()

    @cached_property
    def frozen_folder_path(self) -> Optional[Path]:
        if self.is_frozen_app is True:
            return Path(sys._MEIPASS)

    @cached_property
    def cli_name(self) -> str:
        return self.app_name.replace(" ", "-").replace("_", '-')

    @classmethod
    @property
    def __default_configuration__(cls) -> dict[str, Any]:
        default_configuration = {}
        return default_configuration

    @cached_property
    def pretty_is_dev(self) -> str:
        return "Yes" if self.is_dev else "No"

    @cached_property
    def pretty_app_name(self) -> str:
        if self.app_name:
            return StringCaseConverter.convert_to(self.app_name, StringCase.TITLE)

    @cached_property
    def pretty_app_author(self) -> str:
        if self.app_author:
            return StringCaseConverter.convert_to(self.app_author, StringCase.TITLE)

    @cached_property
    def pretty_base_mem_use(self) -> str:
        return bytes2human(self.base_mem_use)

    @cached_property
    def pretty_started_at(self) -> str:
        return DatetimeFmt.STANDARD.strf(self.started_at)

    def as_dict(self, pretty: bool = False) -> dict[str, Any]:

        if pretty is True:
            return make_pretty(self)
        return attr.asdict(self)

    def to_storager(self, storager: Callable = None) -> None:
        if storager is None:
            return
        storager(self)

    def clean_up(self, **kwargs) -> None:
        pass

    # region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
