"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import argparse
from typing import TYPE_CHECKING, Any
from pathlib import Path

# * Type-Checking Imports --------------------------------------------------------------------------------->
if TYPE_CHECKING:
    pass

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class GidBaseCommandLineParser(argparse.ArgumentParser):

    def __init__(self,
                 prog: str = None,
                 fromfile_prefix_chars: str = None,
                 argument_default: Any = None,
                 conflict_handler: str = 'error',
                 add_help: bool = True,
                 allow_abbrev: bool = True,
                 exit_on_error: bool = True) -> None:
        super().__init__(prog=prog,
                         fromfile_prefix_chars=fromfile_prefix_chars,
                         argument_default=argument_default,
                         conflict_handler=conflict_handler,
                         add_help=add_help,
                         allow_abbrev=allow_abbrev,
                         exit_on_error=exit_on_error)


# region[Main_Exec]

if __name__ == '__main__':
    pass

# endregion[Main_Exec]
