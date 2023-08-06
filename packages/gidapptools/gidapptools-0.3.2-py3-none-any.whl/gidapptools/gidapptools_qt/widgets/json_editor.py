"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from typing import Optional
from pathlib import Path

# * Qt Imports --------------------------------------------------------------------------------------->
import PySide6
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QGridLayout

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class JsonEditorWidget(QWidget):

    def __init__(self, parent: Optional[PySide6.QtWidgets.QWidget] = None, f: PySide6.QtCore.Qt.WindowFlags = None) -> None:
        super().__init__(parent, f or Qt.WindowFlags())
        self.setLayout(QGridLayout())

    def layout(self) -> QGridLayout:
        return super().layout()


# region[Main_Exec]

if __name__ == '__main__':
    pass

# endregion[Main_Exec]
