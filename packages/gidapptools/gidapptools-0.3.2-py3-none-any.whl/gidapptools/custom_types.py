"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import os
import threading
from typing import Union, TypeAlias
from pathlib import Path

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


PATH_TYPE: TypeAlias = Union[str, os.PathLike[str], Path]

LOCK_TYPE: TypeAlias = Union[type[threading.Lock], type[threading.RLock]]

# region[Main_Exec]

if __name__ == '__main__':
    pass

# endregion[Main_Exec]
