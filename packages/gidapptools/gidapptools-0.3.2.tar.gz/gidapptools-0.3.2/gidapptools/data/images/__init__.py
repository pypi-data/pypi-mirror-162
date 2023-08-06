from pathlib import Path
import os
from functools import cache
IMAGES_DIR = Path(__file__).parent.absolute()


class StoredImage:
    allowed_extensions: frozenset[str] = frozenset(["png", "jpg", "jpeg"])

    def __init__(self, path: Path):
        self.path = path.resolve()
        self.name = self.path.stem
        self.image_format = self.path.suffix.removeprefix('.')
        self._bytes: bytes = None

    @property
    def bytes(self) -> bytes:
        if self._bytes is None:
            self._bytes = self.path.read_bytes()
        return self._bytes


PLACEHOLDER_IMAGE = StoredImage(IMAGES_DIR.joinpath("placeholder.png"))


@cache
def get_image(name: str) -> StoredImage:
    cleaned_name = name.rsplit(".", 1)
    for dirname, folderlist, filelist in os.walk(IMAGES_DIR):
        for file in filelist:
            if file.rsplit(".", 1)[-1] in StoredImage.allowed_extensions and file.casefold().rsplit(".", 1)[0] == cleaned_name:
                path = Path(dirname, file)
                image = StoredImage(path)

                return image
    raise FileNotFoundError(f"No gif with name {name!r} found.")
