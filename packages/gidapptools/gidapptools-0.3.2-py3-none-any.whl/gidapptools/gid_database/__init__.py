import os
import sys
from gidapptools.errors import MissingOptionalDependencyError

with MissingOptionalDependencyError.try_import("peewee"):
    import peewee


try:
    import apsw
    os.environ["_APSW_AVAILABLE"] = "1"
except ImportError:
    try:
        from ._compiled_apsw import apsw
        sys.modules["apsw"] = apsw
        os.environ["_APSW_AVAILABLE"] = "1"
    except ImportError:
        os.environ["_APSW_AVAILABLE"] = "0"
