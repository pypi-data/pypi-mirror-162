"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import re
from string import punctuation
from typing import TYPE_CHECKING, Any, Union, Callable, Optional
from pathlib import Path

# * Qt Imports --------------------------------------------------------------------------------------->
from PySide6.QtGui import QIcon, QAction, QPixmap
from PySide6.QtCore import Qt, QSize, QObject
from PySide6.QtWidgets import QMenu, QFrame, QLabel, QHBoxLayout, QApplication, QWidgetAction, QSystemTrayIcon

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.errors import ApplicationNotExistingError
from gidapptools.general_helper.enums import MiscEnum

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


class MenuTitle(QFrame):

    def __init__(self, text: str = None, icon: Union[QIcon, QPixmap] = None, parent=None):
        super().__init__(parent=parent)
        self.setup_styling()

        self.setLayout(QHBoxLayout())
        self.layout.setContentsMargins(5, 5, 5, 5)

        self.text_label = QLabel()
        if text:
            self.set_text(text)
        self.text_label.setAlignment(Qt.AlignCenter)

        self.icon_label = QLabel()

        if icon:
            self.set_icon(icon)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.icon_label)
        self.layout.addWidget(self.text_label)
        self.widget_action = QWidgetAction(self)
        self.widget_action.setDefaultWidget(self)

    def setup_styling(self):
        self.setVisible(False)

        self.setFrameShape(QFrame.Panel)
        self.setFrameShadow(QFrame.Sunken)
        self.setMidLineWidth(1)
        self.setLineWidth(1)
        font = self.font()

        font.setPointSize(int(font.pointSize() * 0.9))
        font.setBold(True)

        font.setLetterSpacing(font.AbsoluteSpacing, 2)
        self.setFont(font)

    @property
    def layout(self) -> QHBoxLayout:
        return super().layout()

    @property
    def icon_size(self) -> QSize:
        if self.text_label.text():
            fm = self.fontMetrics()
            fm.horizontalAdvance(self.text_label.text())
            size = int(fm.height() * 0.9)
            return QSize(size, size)
        return QSize(20, 20)

    def set_text(self, text: str):
        self.text_label.setText(text)
        self.setVisible(True)

    def set_icon(self, icon: Union[QIcon, QPixmap]):
        if isinstance(icon, QIcon):
            icon = icon.pixmap(self.icon_size)

        else:
            icon = icon.scaled(self.icon_size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        self.icon_label.setPixmap(icon)
        self.setVisible(True)


class GidBaseSysTray(QSystemTrayIcon):
    name_normalization_regex = re.compile(rf"[{punctuation}\s]+")

    def __init__(self, icon: Union[QIcon, QPixmap], title: str = None, tooltip: str = None, parent: Optional[QObject] = None):
        super().__init__(icon, parent=parent)
        self.setToolTip(tooltip)
        self.menu: QMenu = QMenu()
        self.setContextMenu(self.menu)
        self.menu_title = MenuTitle(title)
        self.actions: dict[str, QAction] = {}

    @property
    def app(self) -> "GidQtApplication":
        return QApplication.instance()

    @property
    def title(self) -> Optional[str]:
        return self.menu_title.text()

    @title.setter
    def title(self, value: str) -> None:
        self.menu_title.set_text(value)

    def setup(self) -> "GidBaseSysTray":
        if self.app is None:
            raise ApplicationNotExistingError(f"Setting up {self} before the application has been instantiated is forbidden.")
        self.menu.addAction(self.menu_title.widget_action)
        self.menu.addSeparator()

        self.setup_custom_actions()
        self.setup_standard_actions()
        self.menu.repaint()
        return self

    def setup_custom_actions(self):
        pass

    def setup_standard_actions(self):
        self.add_action("Close", self.app.quit)

    def _normalize_action_name(self, name: str) -> str:
        name = name.strip().casefold()
        name = self.name_normalization_regex.sub("_", name)
        return name

    def add_action(self, text: str, connect_to: Callable = None, icon: QIcon = None, enabled: bool = True, tooltip: str = None):
        name = self._normalize_action_name(text)
        if name in self.actions:
            raise KeyError(f"An action with the name {text!r} or the normalized name {name!r} already exists.")
        action = QAction(text, self.menu)
        action.setIconText(text)
        if icon:
            action.setIcon(icon)
        if tooltip:
            action.setToolTip(tooltip)
        action.setEnabled(enabled)

        self.actions[name] = action
        self.menu.addAction(action)
        if connect_to:
            action.triggered.connect(connect_to)

    def remove_action(self, name: str, error_on_missing: bool = False):
        if error_on_missing is True:
            action = self[name]
        else:
            action = self.get(name, MiscEnum.NOT_FOUND)
            if action is MiscEnum.NOT_FOUND:
                return

        self.menu.removeAction(action)
        self.actions.pop(self._normalize_action_name(name))

    def clear(self):
        for action_name in list(self.actions):
            self.remove_action(action_name)

    def __getitem__(self, key: str) -> QAction:
        try:
            return self.actions[self._normalize_action_name(key)]
        except KeyError as error:
            raise KeyError(f"No action named {key!r}") from error

    def get(self, key: str, default: Any = None) -> Union[QAction, Any]:
        return self.actions.get(key, default)
# region[Main_Exec]


if __name__ == '__main__':
    pass
    # endregion[Main_Exec]
