"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from typing import TYPE_CHECKING, Optional
from pathlib import Path

# * Qt Imports --------------------------------------------------------------------------------------->
import PySide6
from PySide6.QtWidgets import QStatusBar, QApplication

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.errors import ApplicationNotExistingError

# * Type-Checking Imports --------------------------------------------------------------------------------->
if TYPE_CHECKING:
    from gidapptools.gidapptools_qt.basics.application import GidQtApplication

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class GidBaseStatusBar(QStatusBar):

    def __init__(self, parent: Optional[PySide6.QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)

    @property
    def app(self) -> "GidQtApplication":
        app = QApplication.instance()
        if app is None:
            raise ApplicationNotExistingError()
        return app
# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
