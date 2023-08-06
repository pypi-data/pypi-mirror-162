"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import os
from typing import Union
from pathlib import Path

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.custom_types import PATH_TYPE

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


def amount_lines_in_file(in_file: PATH_TYPE):
    in_file = Path(in_file)
    if in_file.is_file() is False:
        raise FileNotFoundError(f"The path {in_file.as_posix()!r} is not a file.")
    with in_file.open("r", encoding='utf-8', errors='ignore') as f:

        count = sum(1 for _ in f)

    return count


def get_last_line(in_file: PATH_TYPE, decode: bool = True, encoding: str = "utf-8", errors: str = "ignore") -> str:
    in_file = Path(in_file)
    if in_file.is_file() is False:
        raise FileNotFoundError(f"The path {in_file.as_posix()!r} is not a file.")
    with in_file.open('rb') as f:
        f.seek(-2, os.SEEK_END)
        while f.read(1) != b'\n':
            f.seek(-2, os.SEEK_CUR)
        last_line = f.readline()
        if last_line == b"\r\n":
            last_line = b""
        if decode is True:
            last_line = last_line.decode(encoding=encoding, errors=errors)
        return last_line


def escalating_find_file(file_name: str, directory: Union[str, os.PathLike], case_sensitive: bool = False) -> Path:

    def _case_sensitive_compare(in_file_name: str, target_file_name: str) -> bool:
        return in_file_name == target_file_name

    def _case_insensitive_compare(in_file_name: str, target_file_name: str) -> bool:
        return in_file_name.casefold() == target_file_name

    directory = Path(directory).resolve()
    if directory.is_dir() is False:
        raise NotADirectoryError(f"The path {directory.as_posix()!r} is not a directory.")

    compare_func = _case_sensitive_compare

    if case_sensitive is False:
        file_name = file_name.casefold()
        compare_func = _case_insensitive_compare
    for file in directory.iterdir():
        if not file.is_file():
            continue
        if compare_func(file.name, file_name) is True:
            return file.resolve()

    if len(directory.parts) <= 1:
        raise FileNotFoundError(f"Unable to find the file with the name {file_name!r}.")

    return escalating_find_file(file_name=file_name, directory=directory.parent, case_sensitive=case_sensitive)


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
