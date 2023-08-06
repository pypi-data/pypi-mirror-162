"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from enum import Enum, auto
from pathlib import Path

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]
SPEC_BASE_DATA = {
    "__env__": {
        "__default__": {"converter": "string"},
        "PATH": {"converter": "list(sub_typus=path, split_char=;)"},
        "APPDATA": {"converter": "path"},
        "LOCALAPPDATA": {"converter": "path"},
        "PROGRAMFILES(X86)": {"converter": "path"},
        "PROGRAMFILES": {"converter": "path"},
        "PROGRAMDATA": {"converter": "path"},
        "PATHEXT": {"converter": "list(sub_typus=string, split_char=;)"},
        "USERPROFILE": {"converter": "path"},
        "IS_DEV": {"converter": "boolean",
                   "default": "false"},
        "TMP": {"converter": "path"},
        "TEMP": {"converter": "path"},
        "WINDIR": {"converter": "path"}
    }
}


class NonTypeBaseTypus(Enum):
    DEFAULT = auto()
    FILE_SIZE = auto()
    STRING_CHOICE = auto()


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
