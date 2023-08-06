"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from time import sleep, process_time_ns
from pathlib import Path
from contextlib import contextmanager

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.gid_warning.experimental import experimental_function

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


@experimental_function
@contextmanager
def download_limit():
    start = process_time_ns()
    yield
    if (duration := (process_time_ns() - start) / 1_000_000_000) < 1:
        sleep(1 - duration)


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
