"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from pathlib import Path

# * Qt Imports --------------------------------------------------------------------------------------->
from PySide6.QtCore import QObject

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


def set_std_object_name(obj: QObject):
    name = obj.__class__.__name__
    obj.setObjectName(name)


# region[Main_Exec]

if __name__ == '__main__':
    pass

# endregion[Main_Exec]
