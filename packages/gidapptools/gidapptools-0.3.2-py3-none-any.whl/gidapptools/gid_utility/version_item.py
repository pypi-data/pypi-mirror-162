"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import re
from typing import Union, ClassVar, Optional
from pathlib import Path
from functools import total_ordering

# * Third Party Imports --------------------------------------------------------------------------------->
import attr

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


__all__ = ["VersionItem"]


def try_convert_int(data: Union[str, int, None]) -> Union[str, int, None]:
    if data is None:
        return None
    if isinstance(data, str) and data in {"", "MISSING"}:
        return None
    try:
        return int(data)
    except ValueError:
        return data


@attr.s(slots=True, auto_attribs=True, auto_detect=True, frozen=True)
@total_ordering
class VersionItem:
    major: int = attr.ib(converter=int)
    minor: int = attr.ib(converter=int)
    patch: int = attr.ib(default=None, converter=try_convert_int)
    extra: Union[str, int] = attr.ib(default=None, converter=try_convert_int)
    version_regex: ClassVar = re.compile(r"(?P<major>\d+)\.(?P<minor>\d+)\.?(?P<patch>\d+|MISSING)?\-?(?P<extra>.*)?")

    def __str__(self) -> str:
        _out = f"{self.major}.{self.minor}"
        if self.patch is not None:
            _out += f".{self.patch}"
        if self.extra is not None:
            _out += f"-{self.extra}"
        return _out

    @classmethod
    def from_string(cls, string: Optional[str]) -> Optional["VersionItem"]:
        if string is None:
            return
        match = cls.version_regex.match(string.strip())
        if match is not None:
            return cls(**match.groupdict())

    def as_tuple(self, include_extra: bool = True) -> tuple[Union[str, int]]:
        if include_extra is False:
            return (self.major, self.minor, self.patch)
        return (self.major, self.minor, self.patch, self.extra)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return self.as_tuple() == other.as_tuple()

        if isinstance(other, str):
            return False
        return NotImplemented

    def __lt__(self, other: object) -> bool:
        if other is None:
            return False
        if isinstance(other, self.__class__):

            if (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch):
                if self.extra is None and other.extra is not None:
                    return True
                return False

            if self.major < other.major:
                return True
            elif self.major == other.major and self.minor < other.minor:
                return True
            elif self.major == other.major and self.minor == other.minor and (self.patch is None and other.patch is not None):
                return True
            elif self.major == other.major and self.minor == other.minor and (all([self.patch is not None, other.patch is not None]) and self.patch < other.patch):
                return True
            elif self.major == other.major and self.minor == other.minor and (all([self.patch is not None, other.patch is not None]) and self.patch == other.patch) and (self.extra is None and other.extra is not None):
                return True
            return False

        if isinstance(other, str):
            return False
        return NotImplemented

# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
