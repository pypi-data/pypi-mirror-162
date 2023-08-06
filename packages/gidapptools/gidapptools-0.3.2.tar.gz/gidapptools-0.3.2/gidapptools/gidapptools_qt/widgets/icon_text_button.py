"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import sys
from typing import Union, Optional
from pathlib import Path

# * Qt Imports --------------------------------------------------------------------------------------->
import PySide6
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QLabel, QBoxLayout, QHBoxLayout, QPushButton, QVBoxLayout, QApplication

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class ImageTextButton(QPushButton):

    def __init__(self, icon: QPixmap = None, text: str = None, direction: Union[type[Qt.Vertical], type[Qt.Horizontal]] = Qt.Vertical, parent=None):
        super().__init__(parent=parent)
        layout = QVBoxLayout() if direction == Qt.Vertical else QHBoxLayout()
        self.setLayout(layout)
        self.text_label = QLabel()
        self.text_label.setAlignment(Qt.AlignCenter)
        self.set_text(text)
        self.layout.addWidget(self.text_label)

        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.set_icon(icon)
        self.layout.addWidget(self.icon_label)

    @property
    def direction(self):
        if isinstance(self.layout, QVBoxLayout):
            return Qt.Vertical
        return Qt.Horizontal

    @property
    def text(self) -> Optional[str]:
        return self.text_label.text()

    @property
    def icon(self) -> Optional[QIcon]:
        return QIcon(self.icon_label.pixmap())

    def _get_correct_image_size(self) -> QSize:
        if not self.text:
            print("self.text is None")
            return self.sizeHint()

        fm = self.text_label.fontMetrics()
        widths = []
        heights = []
        for line in self.text.splitlines():
            br = fm.boundingRect(line)
            widths.append(br.width())
            heights.append(br.height())
        # if self.direction == Qt.Vertical:
        #     return QSize(max(widths), max(heights))
        # else:
        #     return QSize(max(widths), sum(heights))
        return QSize(max(widths), sum(heights))

    def set_text(self, text: str):
        if text is None:
            self.text_label.clear()
            return

        self.text_label.setText(text)

    def set_icon(self, icon: Union[QIcon, QPixmap]):
        if icon is None:
            self.icon_label.clear()
            return

        if isinstance(icon, QIcon):
            icon = icon.pixmap(self._get_correct_image_size(), QIcon.Normal, QIcon.On)
        elif isinstance(icon, QPixmap):
            icon = icon.scaled(self._get_correct_image_size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        self.icon_label.setPixmap(icon)

    def sizeHint(self) -> PySide6.QtCore.QSize:
        return self.layout.sizeHint()

    @property
    def layout(self) -> QBoxLayout:
        return super().layout()
# region[Main_Exec]


if __name__ == '__main__':
    app = QApplication()
    w = ImageTextButton(icon=QPixmap(r"D:\Dropbox\hobby\Modding\Programs\Github\My_Repos\GidAppTools\gidapptools\data\images\placeholder.png"), text="this is a test" + ('\n' + "this is a test") * 10, direction=Qt.Vertical)
    w.show()
    sys.exit(app.exec())

# endregion[Main_Exec]
