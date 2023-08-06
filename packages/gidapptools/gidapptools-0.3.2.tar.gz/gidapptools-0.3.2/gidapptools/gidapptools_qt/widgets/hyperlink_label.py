"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from pathlib import Path

# * Qt Imports --------------------------------------------------------------------------------------->
from PySide6.QtGui import QPalette, QMouseEvent, QDesktopServices
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QApplication

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class HyperlinkLabel(QLabel):

    def __init__(self, link: str = None, validate: bool = False, parent=None):
        super().__init__(parent=parent)
        self.validate = validate
        self.link: str = None
        if link:
            self.set_link(link)
        self._set_link_color()

    def _validate_link(self, link: str):
        pass

    def _modify_link(self, link: str) -> str:
        return link

    def set_link(self, link: str):
        link = self._modify_link(link)
        if self.validate is True:
            self._validate_link(link)
        self.link = link
        self.setText(link)

    def _set_link_color(self):
        link_color = QApplication.instance().palette().color(QPalette.Button.Link)
        r = link_color.red()
        g = link_color.green()
        b = link_color.blue()
        self.setStyleSheet(f"color: rgb({', '.join(str(i) for i in [r,g,b])})")
        self.setCursor(Qt.PointingHandCursor)

    def _open_link(self):
        QDesktopServices.openUrl(self.link)

    def mousePressEvent(self, ev: QMouseEvent) -> None:
        if ev.button() == Qt.LeftButton:
            self._open_link()
        else:
            super().mousePressEvent(ev)
# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
