"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import os
import sys
import argparse
from typing import IO, TYPE_CHECKING, Any, Union, Literal, TypeVar, Optional, Sequence
from pathlib import Path
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor

# * Third Party Imports --------------------------------------------------------------------------------->
from yarl import URL
from jinja2 import Template, BaseLoader, Environment
from rich.console import Console as RichConsole

# * Qt Imports --------------------------------------------------------------------------------------->
import PySide6
from PySide6.QtGui import QIcon, QImage, QPixmap
from PySide6.QtCore import Qt, Slot, QEvent, QObject, QSettings
from PySide6.QtWidgets import QWidget, QMainWindow, QMessageBox, QApplication, QSplashScreen, QSystemTrayIcon

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.errors import NotSetupError, MetaItemNotFoundError, ApplicationExistsError
from gidapptools.general_helper.enums import MiscEnum
from gidapptools.gid_utility.version_item import VersionItem
from gidapptools.general_helper.class_helper import make_repr
from gidapptools.general_helper.string_helper import StringCase, StringCaseConverter
from gidapptools.gidapptools_qt.basics.sys_tray import GidBaseSysTray
from gidapptools.gidapptools_qt.basics.main_window import GidBaseMainWindow
from gidapptools.meta_data.meta_info.meta_info_item import MetaInfo
from gidapptools.gidapptools_qt.resources.placeholder import QT_PLACEHOLDER_IMAGE

# * Local Imports --------------------------------------------------------------------------------------->
from gidapptools import get_meta_info

# * Type-Checking Imports --------------------------------------------------------------------------------->
if TYPE_CHECKING:
    from gidapptools.gidapptools_qt.resources.resources_helper import PixmapResourceItem

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]-uz1


class AppArgParserResult:

    def __init__(self) -> None:
        self.exec_file: Path = None
        self.main_window_flags = Qt.WindowFlags()
        self.main_window_states = Qt.WindowStates()
        self.show_window: bool = True


ARG_DOC_MARKDOWN_TEMPLATE = """

# {name}

---

## Description


> {help_text}

---

## Arguments

{argument_strings}

---

## Default

{default_value}

---

## Required

{is_required}

---

## Flag

{is_flag}


""".strip()


_ARG_DOC_HTML_TEMPLATE: str = """



<a id="{{name}}"><b><u>{{name}}</b></u></a>

<dl>
<dt>Description</dt>
<dd>
<blockquote>
<div class="description">
{{help_text}}
</div>
</blockquote>

</dd>

<dt>Arguments</dt>
<dd>
<ul>
{%for arg in argument_strings%}
<li> <pre><code>{{arg}}</code></pre>
{% endfor %}
</ul>
</dd>
{% if default_value is not none %}
<dt>Default</dt>
<dd>{{default_value}}</dd>
{% endif %}
<dt>Required</dt>
<dd>{{is_required}}</dd>

<dt>Flag</dt>
<dd>{{is_flag}}</dd>
</dl>

"""


class CommandLineArgDoc:

    suppress_indicators: set[str] = {"==SUPPRESS=="}
    single_line_text_template: str = "{name} - {help_text} - {argument_strings} - default: {default_value} - required: {is_required} - is flag:{is_flag}"
    text_template: str = "{name}\n{help_text}\n{argument_strings}\ndefault: {default_value}\nrequired: {is_required}\nis flag:{is_flag}"
    markdown_template: str = ARG_DOC_MARKDOWN_TEMPLATE
    html_template: Template = Environment(loader=BaseLoader).from_string(_ARG_DOC_HTML_TEMPLATE)

    def __init__(self, argument: Union["BaseAppArgParseAction", argparse.Action], app_meta_info: "MetaInfo") -> None:
        self.argument = argument
        self.app_meta_info = app_meta_info

    @property
    def name(self) -> str:
        name = self.argument.metavar or self.argument.dest
        return StringCaseConverter.convert_to(name, StringCase.TITLE)

    @property
    def help_text(self) -> str:
        help_text = self.argument.help.replace("%(prog)r", "{prog}").replace("%(prog)s", "{prog}")
        return help_text

    @property
    def default_value(self) -> Optional[Any]:
        default_value = self.argument.default
        if str(default_value) in self.suppress_indicators:
            return None

        return default_value

    @property
    def is_required(self) -> bool:
        return self.argument.required

    @property
    def is_flag(self) -> bool:
        try:
            return self.argument.is_flag
        except AttributeError:
            return isinstance(self.argument, argparse._StoreAction)

    @property
    def choices(self) -> Optional[Iterable]:
        return self.argument.choices

    @property
    def argument_strings(self) -> tuple[str]:
        return tuple(self.argument.option_strings)

    def get_text(self, single_line: bool = False) -> str:
        bool_values = {True: "Yes", False: "No"}
        help_text = self.help_text.format(prog=self.app_meta_info.pretty_app_name)
        is_required = bool_values[self.is_required]
        is_flag = bool_values[self.is_flag]
        default_value = bool_values.get(self.default_value, self.default_value)

        argument_strings = self.argument_strings
        template = self.single_line_text_template if single_line is True else self.text_template
        return template.format(name=self.name,
                               help_text=help_text,
                               is_required=is_required,
                               is_flag=is_flag,
                               default_value=default_value,
                               argument_strings=argument_strings,
                               prog=self.app_meta_info.pretty_app_name)

    def get_markdown(self) -> str:
        bool_values = {True: "✅", False: "❎"}
        help_text = self.help_text.format(prog="`" + self.app_meta_info.pretty_app_name + "`")
        is_required = bool_values[self.is_required]
        is_flag = bool_values[self.is_flag]
        default_value = bool_values.get(self.default_value, self.default_value)

        argument_strings = '\n'.join(f"- {arg}" for arg in self.argument_strings)

        return self.markdown_template.format(name=self.name,
                                             help_text=help_text,
                                             is_required=is_required,
                                             is_flag=is_flag,
                                             default_value=default_value,
                                             argument_strings=argument_strings,
                                             prog=self.app_meta_info.pretty_app_name)

    def get_html(self) -> str:
        bool_values = {True: '✔️', False: '❌'}
        help_text = self.help_text.format(prog=f'<div class="app_name">{self.app_meta_info.pretty_app_name}</div>')
        is_required = bool_values[self.is_required]
        is_flag = bool_values[self.is_flag]
        default_value = bool_values.get(self.default_value, self.default_value)

        return self.html_template.render(name=self.name,
                                         help_text=help_text,
                                         is_required=is_required,
                                         is_flag=is_flag,
                                         default_value=default_value,
                                         argument_strings=self.argument_strings,
                                         prog=self.app_meta_info.pretty_app_name)

    def __str__(self) -> str:
        return self.get_text(single_line=True)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(action={self.action!r})"


class BaseAppArgParseAction(argparse.Action):

    def __init__(self,
                 option_strings,
                 dest,
                 nargs=None,
                 const=None,
                 default=None,
                 type=None,
                 choices=None,
                 required=False,
                 help=None,
                 metavar=None):
        self.option_strings = option_strings
        self.dest = dest
        self.nargs = nargs
        self.const = const
        self.default = default
        self.type = type
        self.choices = choices
        self.required = required
        self.help = help
        self.metavar = metavar

    def get_doc_item(self, app_meta_info: MetaInfo) -> CommandLineArgDoc:
        return CommandLineArgDoc(self, app_meta_info)

    @property
    def is_flag(self) -> bool:
        return False


class FlagAction(BaseAppArgParseAction):
    def __init__(self,
                 option_strings,
                 dest,
                 default=None,
                 type=None,
                 choices=None,
                 required=False,
                 help=None,
                 metavar=None):

        _option_strings = []
        for option_string in option_strings:
            _option_strings.append(option_string)

        if help is not None and default is not None:
            help += " (default: %(default)s)"

        super().__init__(option_strings=_option_strings,
                         dest=dest,
                         nargs=0,
                         default=default,
                         type=type,
                         choices=choices,
                         required=required,
                         help=help,
                         metavar=metavar)

    @property
    def is_flag(self) -> bool:
        return True

    def format_usage(self):
        return ' | '.join(self.option_strings)

    def __call__(self, parser, namespace, values, option_string=None):
        if option_string in self.option_strings:
            setattr(namespace, self.dest, not option_string.startswith('--no-'))


class MainWindowMaximizedAction(FlagAction):

    def __call__(self, parser: argparse.ArgumentParser, namespace: argparse.Namespace, values: str | Sequence[Any] | None, option_string: str | None = ...) -> None:

        namespace.main_window_states |= Qt.WindowMaximized
        values = Qt.WindowMaximized
        super().__call__(parser=parser, namespace=namespace, values=values, option_string=option_string)


class MainWindowMinimizedAction(FlagAction):

    def __call__(self, parser: argparse.ArgumentParser, namespace: argparse.Namespace, values: str | Sequence[Any] | None, option_string: str | None = ...) -> None:

        namespace.main_window_states |= Qt.WindowMinimized
        values = Qt.WindowMinimized
        super().__call__(parser=parser, namespace=namespace, values=values, option_string=option_string)


class MainWindowAlwaysOnTopAction(FlagAction):

    def __call__(self, parser: argparse.ArgumentParser, namespace: argparse.Namespace, values: str | Sequence[Any] | None, option_string: str | None = ...) -> None:
        namespace.main_window_flags |= Qt.WindowStaysOnTopHint
        values = Qt.WindowStaysOnTopHint
        super().__call__(parser=parser, namespace=namespace, values=values, option_string=option_string)


class ClearAppSettingsAction(FlagAction):

    def __call__(self, parser: argparse.ArgumentParser, namespace: argparse.Namespace, values: str | Sequence[Any] | None, option_string: str | None = ...) -> None:
        parser.application.clear_settings()
        super().__call__(parser=parser, namespace=namespace, values=values, option_string=option_string)
        parser.exit(message="Cleared Application settings.")


class VersionFlagAction(FlagAction):

    def __init__(self,
                 option_strings,
                 version=None,
                 dest=argparse.SUPPRESS,
                 default=argparse.SUPPRESS,
                 help="show program's version number and exit"):
        super().__init__(
            option_strings=option_strings,
            dest=dest,
            default=default,
            nargs=0,
            help=help)
        self.version = version

    def __call__(self, parser, namespace, values, option_string=None):
        version = self.version
        if version is None:
            version = parser.version
        formatter = parser._get_formatter()
        formatter.add_text(version)
        parser._print_message(formatter.format_help(), sys.stdout)
        parser.exit()


class AppArgParser(argparse.ArgumentParser):

    def __init__(self, application: "GidQtApplication", result_item: AppArgParserResult = None, console: RichConsole = None):
        self.application = application
        self.result_item = result_item or AppArgParserResult()
        self.console = console or RichConsole(soft_wrap=True)
        self.raw_argvs = list(self.application.arguments())
        self.result_item.exec_file = Path(self.raw_argvs.pop(0))
        super().__init__(prog=self.application.pretty_name)
        self.unparsable_args: list[str] = None
        self.setup()

    def setup(self):
        self.application.argument_parse_result = self.result_item
        self.version = str(self.application.version)
        self.setup_std_args()

    @property
    def actions(self):
        return self._actions

    def setup_std_args(self):

        self.add_argument("-v", "--version", action=VersionFlagAction, version=self.version)
        self.add_argument("-max", "--maximized", action=MainWindowMaximizedAction)
        self.add_argument("-min", "--minimized", action=MainWindowMinimizedAction)
        self.add_argument("-t", "--always-on-top", action=MainWindowAlwaysOnTopAction)
        self.add_argument("-c", "--clear-settings", action=ClearAppSettingsAction)

    def parse_app_args(self):
        _, self.unparsable_args = super().parse_known_args(self.raw_argvs, self.result_item)

    def _print_message(self, message: str, file: IO[str] | None = None) -> None:
        self.console.file = file

        self.console.rule()
        self.console.print(message)
        self.console.rule()


class WindowHolder(QObject):
    windows: dict[str, QWidget] = {}

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

    def _determine_name(self, window: QWidget):
        if hasattr(window, "name"):
            return window.name

        object_name = window.objectName()
        if object_name:
            return object_name

        return window.__class__.__name__

    def _check_stored_windows_closed(self):
        for window in list(self.windows.values()):
            if window.isVisible() is False:
                self.remove_window(window)

    def add_window(self, window: QWidget):
        self._check_stored_windows_closed()
        name = self._determine_name(window)

        self.windows[name] = window
        try:
            window.close_signal.connect(self.remove_window)
        except AttributeError:
            pass

    @Slot(QWidget)
    def remove_window(self, window: QWidget):
        name = self._determine_name(window)
        try:
            del self.windows[name]
        except KeyError:
            pass

    def window_objects(self) -> list[QWidget]:
        return list(self.windows.values())

    def __getitem__(self, name: str) -> QWidget:
        self._check_stored_windows_closed()
        return self.windows[name]

    def __setitem__(self, name: str, window: QWidget) -> None:
        self._check_stored_windows_closed()
        self.add_window(window=window, name=name)

    def __delitem__(self, name: str) -> None:
        self._check_stored_windows_closed()
        del self.windows[name]

    def get(self, name: str, default=None) -> Optional[QWidget]:
        self._check_stored_windows_closed()
        return self.windows.get(name, default)

    def __len__(self) -> int:
        self._check_stored_windows_closed()
        return len(self.windows)

    def values(self):
        self._check_stored_windows_closed()
        return self.windows.values()

    def keys(self):
        self._check_stored_windows_closed()
        return self.windows.keys()

    def items(self):
        self._check_stored_windows_closed()
        return self.windows.items()

    def pop(self, name: str, default=None) -> Optional[QWidget]:
        self._check_stored_windows_closed()
        return self.windows.pop(name, default)

    def clear(self) -> None:
        self.windows.clear()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(parent={self.parent()!r})"


class GidQtApplication(QApplication):
    default_icon = QT_PLACEHOLDER_IMAGE

    def __init__(self,
                 argvs: list[str],
                 meta_info: "MetaInfo"):
        self.is_setup: bool = False
        super().__init__(argvs)
        self.setObjectName("Application")

        self.meta_info = meta_info

        self.main_window: GidBaseMainWindow = None
        self.sys_tray: GidBaseSysTray = None
        self.icon = None
        self.splash_screens: dict[str, QSplashScreen] = {"startup": None, "shutdown": None}
        self.argument_parse_result: AppArgParserResult = None
        self.extra_windows = WindowHolder()
        self._gui_thread_pool: ThreadPoolExecutor = None

    @property
    def name(self) -> str:
        return self.meta_info.app_name

    @property
    def pretty_name(self) -> str:
        if self.meta_info.pretty_app_name:
            return self.meta_info.pretty_app_name
        return self.name

    @property
    def organization_name(self) -> str:
        return self.meta_info.app_author

    @property
    def version(self) -> VersionItem:
        return self.meta_info.version

    @property
    def url(self) -> URL:
        return self.meta_info.url

    @property
    def settings(self) -> QSettings:
        return QSettings()

    @property
    def gui_thread_pool(self) -> ThreadPoolExecutor:
        if self._gui_thread_pool is None:
            self._gui_thread_pool = ThreadPoolExecutor(thread_name_prefix="gui_thread")

        return self._gui_thread_pool

    @classmethod
    def set_pre_flags(cls, pre_flags: dict[Qt.ApplicationAttribute:bool]):
        if cls.instance() is not None:
            ApplicationExistsError(existing_application=cls.instance(), msg="Pre Flags can only be set, before an application is instantiated")

        if pre_flags is None:
            return

        for flag, value in pre_flags.items():
            cls.setAttribute(flag, value)

    def set_icon(self, icon=Union["PixmapResourceItem", QPixmap, QImage, str, QIcon, Path]):
        self.icon = self._icon_conversion(icon)
        self.setWindowIcon(self.icon)

    def setup(self) -> "GidQtApplication":
        if self.is_setup is False:
            self.setup_meta_data()
            self.is_setup = True
        return self

    def setup_meta_data(self):
        self.setApplicationName(self.meta_info.app_name)
        self.setApplicationDisplayName(self.meta_info.pretty_app_name)
        self.setOrganizationName(self.meta_info.app_author)
        if self.meta_info.url:
            self.setOrganizationDomain(str(self.meta_info.url))
        version = str(self.meta_info.version) if self.meta_info.version else "-"
        self.setApplicationVersion(version)

    def clear_settings(self):
        self.settings.clear()

    def _icon_conversion(self, icon: Union["PixmapResourceItem", QPixmap, QImage, str, QIcon, Path] = None) -> Optional[QIcon]:
        if icon is None:
            icon = self.default_icon

        if isinstance(icon, QIcon):
            return icon

        if isinstance(icon, (QPixmap, QImage, str, Path)):
            if isinstance(icon, Path):
                icon = str(icon)
            return QIcon(icon)

        return icon.get_as_icon()

    def show_about_qt(self) -> None:
        self.aboutQt()

    def _get_about_text(self) -> str:
        sort_order = ["Name", "Author", "Link", "Version"]
        text_parts = {"Name": self.applicationDisplayName(),
                      "Version": self.applicationVersion()}
        if self.organizationName():
            text_parts["Author"] = self.organizationName()
        if self.organizationDomain():
            text_parts["Link"] = f'<a href="{self.organizationDomain()}">{self.organizationDomain()}</a>'

        text_parts = dict(sorted(text_parts.items(), key=lambda x: sort_order.index(x[0])))
        return '<br>'.join(f"<b>{k:<20}:</b>{v:>50}" for k, v in text_parts.items())

    def show_about(self) -> None:
        title = f"About {self.applicationDisplayName()}"
        text = self._get_about_text()
        QMessageBox.about(self.main_window, title, text)

    def start(self):
        self.setup()

        if self.splash_screens["startup"] and self.main_window:
            self.splash_screens["startup"].show()
            self.splash_screens["startup"].finish(self.main_window)

        if self.sys_tray:
            self.sys_tray.show()

        if self.main_window:
            self.main_window.show()
        return self.exec()

    def on_quit(self, event: QEvent):
        self.extra_windows.clear()
        self.closeAllWindows()
        if self._gui_thread_pool is not None:
            self._gui_thread_pool.shutdown(wait=False, cancel_futures=True)

    def event(self, event: PySide6.QtCore.QEvent) -> bool:
        if event.type() is QEvent.Quit:
            self.on_quit(event)

        return super().event(event)

    def __repr__(self) -> str:
        return make_repr(self, exclude_none=False, attr_names=["name", "organization_name", "version", "url", "arguments", "main_window", "sys_tray"])


T = TypeVar("T")


class ClassHolder:

    def __init__(self, klass: T, **kwargs) -> None:
        self.klass = klass
        self.kwargs = kwargs
        self.instance: T = None

    def create(self):
        self.instance = self.klass(**self.kwargs)
        return self.instance


class ApplicationBuilder:

    def __init__(self) -> None:
        self.application_pre_flags: dict[Qt.ApplicationAttribute:bool] = {Qt.AA_EnableHighDpiScaling: True, Qt.AA_UseHighDpiPixmaps: True}
        self.application_class: ClassHolder = ClassHolder(GidQtApplication)
        self.main_window_class: ClassHolder = ClassHolder(GidBaseMainWindow)
        self.argument_parser_class: ClassHolder = ClassHolder(AppArgParser)
        self.sys_tray_class: ClassHolder = None

        self.app_icon = None
        self.meta_info: "MetaInfo" = self._get_default_meta_info()
        self.style_sheet_file: Path = None

    def set_app_icon(self, icon: Union["PixmapResourceItem", QPixmap, QImage, str, QIcon]):
        self.app_icon = icon

    def set_application_class(self, application_class: type[GidQtApplication], **kwargs):
        self.application_class = ClassHolder(application_class, **kwargs)

    def set_main_window_class(self, main_window_class: type[QMainWindow], **kwargs):
        self.main_window_class = ClassHolder(main_window_class, **kwargs)

    def set_sys_tray_class(self, sys_tray_class: Union[type[QSystemTrayIcon], Literal[MiscEnum.DEFAULT], None] = MiscEnum.DEFAULT, **kwargs):
        if sys_tray_class is None:
            self.sys_tray_class = None
        elif sys_tray_class is MiscEnum.DEFAULT:
            self.sys_tray_class = ClassHolder(GidBaseSysTray, **kwargs)

        else:
            self.sys_tray_class = ClassHolder(sys_tray_class, **kwargs)

    def set_meta_info(self, meta_info: type[MetaInfo]):
        self.meta_info = meta_info

    def set_application_pre_flags(self, pre_flags: dict[Qt.ApplicationAttribute:bool]):
        self.application_pre_flags = pre_flags

    def set_style_sheet_file(self, file_path: Union[str, os.PathLike]):
        self.style_sheet_file = Path(file_path)

    def _get_default_meta_info(self):
        try:
            return get_meta_info()
        except (MetaItemNotFoundError, NotSetupError):
            return MetaInfo(app_name=Path(sys.argv[0]).stem.title())

    def _build_application(self) -> QApplication:
        self.application_class.klass.set_pre_flags(self.application_pre_flags)
        if "meta_info" not in self.application_class.kwargs:
            self.application_class.kwargs["meta_info"] = self.meta_info
        if "argvs" not in self.application_class.kwargs:
            self.application_class.kwargs["argvs"] = sys.argv
        application = self.application_class.create()
        application.set_icon(self.app_icon)
        return application

    def _build_argument_parser(self) -> AppArgParser:
        self.argument_parser_class.kwargs["application"] = self.application_class.instance
        parser = self.argument_parser_class.create()
        parser.parse_app_args()

        return parser

    def _build_main_window(self) -> QMainWindow:
        main_window: QMainWindow = self.main_window_class.create()
        main_window.setWindowFlags(main_window.windowFlags() | self.argument_parser_class.instance.result_item.main_window_flags)
        main_window.setWindowState(main_window.windowState() | self.argument_parser_class.instance.result_item.main_window_states)
        return main_window

    def _build_sys_tray(self) -> QSystemTrayIcon:
        if "icon" not in self.sys_tray_class.kwargs:
            self.sys_tray_class.kwargs["icon"] = self.application_class.instance.icon
        if "title" not in self.sys_tray_class.kwargs:
            self.sys_tray_class.kwargs["title"] = self.application_class.instance.pretty_name
        if "tooltip" not in self.sys_tray_class.kwargs:
            self.sys_tray_class.kwargs["tooltip"] = self.application_class.instance.pretty_name
        return self.sys_tray_class.create().setup()

    def build(self) -> GidQtApplication:
        application = self._build_application()
        parser = self._build_argument_parser()

        if self.sys_tray_class:
            sys_tray = self._build_sys_tray()

            application.sys_tray = sys_tray
        if self.main_window_class:

            main_window = self._build_main_window()
            application.main_window = main_window
        if self.style_sheet_file:
            application.setStyleSheet(self.style_sheet_file.read_text(encoding='utf-8', errors='ignore'))
        return application


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
