"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from typing import Iterable
from pathlib import Path

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class Color:

    def __init__(self, values: Iterable[float], name: str = None) -> None:
        self._values = tuple(values)
        self._name = name
        self._red: float = self._values[0]
        self._green: float = self._values[1]
        self._blue: float = self._values[2]
        self._alpha: float = self._values[3]

    @property
    def values(self) -> tuple[float]:
        return self._values

    @property
    def name(self) -> str:
        return self._name

    @property
    def red(self) -> float:
        return self._red

    @property
    def green(self) -> float:
        return self._green

    @property
    def blue(self) -> float:
        return self._blue

    @property
    def alpha(self) -> float:
        return self._alpha

    def with_alpha(self, new_alpha: float, new_name: str = None) -> "Color":
        new_values = (self.red, self.green, self.blue, new_alpha)
        return self.__class__(new_values, name=new_name)

    def with_red(self, new_red: float, new_name: str = None) -> "Color":
        new_values = (new_red, self.green, self.blue, self.alpha)
        return self.__class__(new_values, name=new_name)

    def with_green(self, new_green: float, new_name: str = None) -> "Color":
        new_values = (self.red, new_green, self.blue, self.alpha)
        return self.__class__(new_values, name=new_name)

    def with_blue(self, new_blue: float, new_name: str = None) -> "Color":
        new_values = (self.red, self.green, new_blue, self.alpha)
        return self.__class__(new_values, name=new_name)

    def to_int_rgba(self) -> tuple(int):
        ...

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(values={self.values!r}, name={self.name!r})'
# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
