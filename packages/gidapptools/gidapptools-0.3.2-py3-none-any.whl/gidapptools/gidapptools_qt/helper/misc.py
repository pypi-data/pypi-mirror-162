"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from pathlib import Path

# * Qt Imports --------------------------------------------------------------------------------------->
from PySide6.QtGui import QScreen
from PySide6.QtWidgets import QWidget, QApplication

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


def center_window(window: QWidget, allow_window_resize: bool = True) -> QWidget:
    app = QApplication.instance()
    if allow_window_resize is True:
        window.resize(window.sizeHint())

    screen = app.primaryScreen()
    screen_geo = QScreen.availableGeometry(screen)
    screen_center = screen_geo.center()

    window_geo = window.frameGeometry()
    window_geo.moveCenter(screen_center)
    window.move(window_geo.topLeft())
    return window

# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
