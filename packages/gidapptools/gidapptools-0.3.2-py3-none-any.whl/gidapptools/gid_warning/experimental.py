"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from pathlib import Path
from warnings import warn
from functools import wraps

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


def make_experimental_warning(func_name: str):
    msg = f"The function {func_name!r} is still experimentel and there is no guarantee that it works or does what it says."
    warn(message=msg, category=UserWarning, stacklevel=3)


def experimental_function(func):
    func_name = func.__name__

    @wraps(func)
    def _wrapped(*args, **kwargs):
        make_experimental_warning(func_name=func_name)
        return func(*args, **kwargs)

    return _wrapped
# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
