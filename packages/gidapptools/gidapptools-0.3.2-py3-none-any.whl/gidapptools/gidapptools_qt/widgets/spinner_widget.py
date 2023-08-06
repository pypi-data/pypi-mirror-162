"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from typing import Union
from pathlib import Path
from concurrent.futures import Future

# * Qt Imports --------------------------------------------------------------------------------------->
import PySide6
from PySide6.QtGui import QMovie
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtWidgets import QLabel, QWidget, QPushButton, QSizePolicy, QVBoxLayout, QApplication

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.data.gifs import StoredGif, get_gif

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class BusySpinnerWidget(QLabel):
    default_gif_name: str = "busy_spinner_4.gif"
    default_spinner_size: tuple[int, int] = (75, 75)

    def __init__(self, parent: QWidget = None, spinner_gif: Union[QMovie, str, Path, StoredGif] = None, spinner_size: QSize = None):
        super().__init__(parent)
        self.spinner_size = spinner_size or QSize(*self.default_spinner_size)
        self.spinner_gif_item, self.spinner_gif = self.setup_spinner_gif(spinner_gif=spinner_gif)
        self.setAlignment(Qt.AlignCenter)

        self.running: bool = False

    @property
    def app(self) -> QApplication:
        return QApplication.instance()

    def set_spinner_size(self, size: QSize) -> None:
        self.spinner_size = size
        self.spinner_gif.setScaledSize(self.spinner_size)

    def setup_spinner_gif(self, spinner_gif: Union[QMovie, str, Path, StoredGif]) -> tuple[StoredGif, QMovie]:
        if isinstance(spinner_gif, str):
            if Path(spinner_gif).is_file() is True:
                spinner_gif = StoredGif(spinner_gif)
            else:
                spinner_gif = get_gif(spinner_gif)
        elif isinstance(spinner_gif, Path):
            spinner_gif = StoredGif(spinner_gif)

        spinner_gif_item = spinner_gif or get_gif(self.default_gif_name)
        spinner_gif = QMovie(str(spinner_gif_item.path))
        spinner_gif.setScaledSize(self.spinner_size)
        spinner_gif.setCacheMode(QMovie.CacheAll)
        self.setMovie(spinner_gif)
        return spinner_gif_item, spinner_gif

    def start(self):
        self.spinner_gif.start()
        self.running = True

    def stop(self):
        self.spinner_gif.stop()
        self.running = False


class BusyPushButton(QPushButton):
    _stop_signal = Signal(Future)

    def __init__(self,
                 parent: QWidget = None,
                 text: str = None,
                 spinner_gif: Union[QMovie, str] = None,
                 spinner_size: QSize = None,
                 disable_while_spinning: bool = True):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        self.setLayout(QVBoxLayout())
        self.disable_while_spinning = disable_while_spinning
        self.text_widget = QLabel(self)
        self.text_widget.setScaledContents(True)
        self.text_widget.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.text_widget)
        self.busy_spinner_widget = BusySpinnerWidget(self, spinner_gif=spinner_gif, spinner_size=spinner_size or QSize(self.sizeHint().height(), self.sizeHint().height()))
        self.layout.addWidget(self.busy_spinner_widget)
        self.set_text(text)
        self.busy_spinner_widget.setVisible(False)
        self._stop_signal.connect(self.stop_spinner)

    @property
    def layout(self) -> QVBoxLayout:
        return super().layout()

    def resize(self, size: QSize):
        super().resize(size)
        self.set_spinner_size(QSize(self.size().height(), self.size().height()))

    def set_spinner_size(self, size: QSize):
        self.busy_spinner_widget.set_spinner_size(size)

    def set_text(self, text: str):
        text = text or ""
        self.text_widget.setText(text)

    def sizeHint(self) -> PySide6.QtCore.QSize:
        return self.layout.sizeHint()

    def hide_text(self):

        self.text_widget.setVisible(False)

    def show_text(self):

        self.text_widget.setVisible(True)

    def start_spinner(self):
        self.hide_text()
        self.busy_spinner_widget.setVisible(True)

        self.busy_spinner_widget.start()
        if self.disable_while_spinning is True:
            self.setEnabled(False)

    def stop_spinner(self, *args):
        if self.disable_while_spinning is True:
            self.setEnabled(True)
        self.busy_spinner_widget.stop()
        self.busy_spinner_widget.setVisible(False)
        self.show_text()

    def start_spinner_while_future(self, future: Future):
        self.start_spinner()

        future.add_done_callback(self._stop_signal.emit)

    def start_spinner_with_stop_signal(self, stop_signal: Signal):
        self.start_spinner()
        stop_signal.connect(self.stop_spinner)


# region[Main_Exec]
if __name__ == '__main__':
    app = QApplication()
    x = BusySpinnerWidget()
    x.show()
    app.exec()

# endregion[Main_Exec]
