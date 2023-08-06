from gidapptools.errors import MissingOptionalDependencyError


with MissingOptionalDependencyError.try_import("dateutil"):
    import dateutil
