"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from pathlib import Path

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class BaseToken:

    def __repr__(self) -> str:
        var_parts = [f"{k}={v!r}" for k, v in vars(self).items()]
        return f"{self.__class__.__name__}({', '.join(var_parts)})"


class BaseTokenWithPos(BaseToken):

    def __init__(self,
                 start: int,
                 end: int) -> None:
        self.start = start
        self.end = end
        self.span = end - start

    @classmethod
    def from_parse_action(cls, s, l, t) -> "BaseTokenWithPos":
        data_dict = t[0].as_dict()
        data_dict["start"] = data_dict.pop("locn_start")
        data_dict["end"] = data_dict.pop("locn_end")
        return cls(**data_dict)


# region[Main_Exec]

if __name__ == '__main__':
    pass

# endregion[Main_Exec]
