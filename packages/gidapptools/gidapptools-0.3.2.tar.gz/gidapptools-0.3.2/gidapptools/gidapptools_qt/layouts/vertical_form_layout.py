"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from typing import Optional
from pathlib import Path

# * Qt Imports --------------------------------------------------------------------------------------->
from PySide6.QtWidgets import QLayout, QWidget

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class VerticalFormLayout(QLayout):

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)


# region[Main_Exec]

if __name__ == '__main__':
    pass

# endregion[Main_Exec]
