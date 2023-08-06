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
from PySide6.QtWidgets import QWidget, QStatusBar, QMainWindow, QApplication

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.errors import ApplicationNotExistingError
from gidapptools.gidapptools_qt.basics.menu_bar import BaseMenuBar
from gidapptools.gidapptools_qt.basics.status_bar import GidBaseStatusBar

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


class GidBaseMainWindow(QMainWindow):

    def __init__(self, parent: Optional[PySide6.QtWidgets.QWidget] = None, flags: PySide6.QtCore.Qt.WindowFlags = None, menu_bar: BaseMenuBar = None, status_bar: GidBaseStatusBar = None) -> None:
        super().__init__(*(i for i in [parent, flags] if i))
        self.setObjectName("MainWindow")
        self.menu_bar = menu_bar or BaseMenuBar(auto_connect_standard_actions=True)
        self.status_bar = status_bar or GidBaseStatusBar()

    @property
    def app(self) -> "GidQtApplication":
        app = QApplication.instance()
        if app is None:
            raise ApplicationNotExistingError()
        return app

    @property
    def central_widget(self) -> QWidget:
        return super().centralWidget()

    @central_widget.setter
    def central_widget(self, widget: QWidget):
        self.setCentralWidget(widget)

    @property
    def menu_bar(self) -> BaseMenuBar:
        return super().menuBar()

    @menu_bar.setter
    def menu_bar(self, menu_bar: BaseMenuBar):
        menu_bar.setParent(self)
        try:
            menu_bar.setup()
        except AttributeError:
            pass
        self.setMenuBar(menu_bar)

    @property
    def status_bar(self) -> QStatusBar:
        return super().statusBar()

    @status_bar.setter
    def status_bar(self, status_bar: QStatusBar):
        status_bar.setParent(self)
        try:
            status_bar.setup()
        except AttributeError:
            pass
        self.setStatusBar(status_bar)
# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
