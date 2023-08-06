"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import os
import string
import subprocess
from glob import iglob
from ctypes import windll
from typing import TYPE_CHECKING, Union, Optional, Generator
from pathlib import Path
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor

# * Third Party Imports --------------------------------------------------------------------------------->
from psutil import disk_partitions

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.utility.enums import OperatingSystem

# * Type-Checking Imports --------------------------------------------------------------------------------->
if TYPE_CHECKING:
    from gidapptools.custom_types import PATH_TYPE

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


def get_all_drives(also_non_physical: bool = False) -> tuple[Path]:
    return tuple(Path(drive.mountpoint) for drive in disk_partitions(all=also_non_physical))


def get_all_drives_non_psutil(*args):
    drives = []
    bitmask = windll.kernel32.GetLogicalDrives()
    for letter in string.ascii_uppercase:
        if bitmask & 1:
            drives.append(Path(f"{letter}:\\ ").resolve())
        bitmask >>= 1

    return tuple(drives)


def find_file(file_name: str, return_first: bool = True, case_sensitive: bool = False) -> Optional[Union[Path, tuple[Path]]]:
    if case_sensitive is False:
        file_name = file_name.casefold()
    _out = []
    for drive in get_all_drives():
        for dirname, folderlist, filelist in os.walk(drive):
            for file in filelist:
                if file.casefold() == file_name:
                    file_path = Path(dirname, file)
                    if return_first is True:
                        return file_path
                    else:
                        _out.append(file_path)
    if _out != []:
        return tuple(_out)
    return None


def find_file_alternative(file_name: str, return_first: bool = True) -> Optional[Union[Path, tuple[Path]]]:
    def _helper(args) -> Generator[Path, None, None]:
        _drive = args[0]
        _file_name = args[1]
        for _found_file in iglob(f"{_drive.as_posix().rstrip('/')}/**/{_file_name}", recursive=True):
            yield Path(_found_file)
    _out = []
    with ThreadPoolExecutor(3) as pool:
        for gen in pool.map(_helper, ((drive, file_name) for drive in get_all_drives())):
            for file in gen:
                if return_first is True:
                    return file
                else:
                    _out.append(file)
    if _out != []:
        return tuple(_out)
    return None


@contextmanager
def change_cwd(target_cwd: "PATH_TYPE"):
    old_cwd = Path.cwd()
    new_cwd = Path(target_cwd)
    if new_cwd.is_dir() is False:
        raise FileNotFoundError(f"The target_cwd({new_cwd.as_posix()!r}) either does not exist or is a file and not a directory.")
    os.chdir(new_cwd)
    yield
    os.chdir(old_cwd)


def open_folder_in_explorer(in_folder: Union[str, os.PathLike]) -> None:
    in_folder = Path(in_folder)
    if not in_folder.exists():
        raise FileNotFoundError(f"No such file or directory: {in_folder.as_posix()!r}.")
    if not in_folder.is_dir():
        raise TypeError(f"Path {in_folder.as_posix()!r} needs to be a folder.")

    operating_system = OperatingSystem.determine_operating_system()

    match operating_system:

        case OperatingSystem.WINDOWS:
            subprocess.run(["explorer", in_folder], check=False, start_new_session=True)

        case OperatingSystem.LINUX:
            subprocess.run(['xdg-open', in_folder], check=False)

        case OperatingSystem.MAC_OS:
            subprocess.run(['open', in_folder], check=False)

        case _:
            raise RuntimeError(f"Not able to open folder {in_folder.as_posix()!r}, because no known procedure for Operating System {operating_system!s}.")


# region[Main_Exec]
if __name__ == '__main__':
    pass
# endregion[Main_Exec]
