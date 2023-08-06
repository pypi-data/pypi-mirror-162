from pathlib import Path
import os
from functools import cache
from gidapptools.errors import MissingOptionalDependencyError
GIFS_DIR = Path(__file__).parent.absolute()


class StoredGif:
    allowed_extensions: frozenset[str] = frozenset(["gif"])

    def __init__(self, path: Path):
        self.path = path.resolve()
        self.name = self.path.stem
        self._bytes: bytes = None

    @property
    def bytes(self) -> bytes:
        if self._bytes is None:
            self._bytes = self.path.read_bytes()
        return self._bytes


@cache
def get_gif(name: str) -> StoredGif:
    cleaned_name = name.casefold().rsplit(".", 1)[0]
    for dirname, folderlist, filelist in os.walk(GIFS_DIR):
        for file in filelist:
            if file.rsplit(".", 1)[-1] in StoredGif.allowed_extensions and file.casefold().rsplit(".", 1)[0] == cleaned_name:
                path = Path(dirname, file)
                return StoredGif(path)
    raise FileNotFoundError(f"No gif with name {name!r} found.")
