from gidapptools.errors import MissingOptionalDependencyError


with MissingOptionalDependencyError.try_import("PySide6"):
    import PySide6


with MissingOptionalDependencyError.try_import("jinja2"):
    import jinja2
