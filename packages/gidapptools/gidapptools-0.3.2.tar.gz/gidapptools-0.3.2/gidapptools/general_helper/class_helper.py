"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import inspect
from typing import TYPE_CHECKING, Any, Union, Callable, Iterable
from pathlib import Path
from weakref import WeakSet, WeakMethod, ref

# * Type-Checking Imports --------------------------------------------------------------------------------->
if TYPE_CHECKING:
    from weakref import ReferenceType

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


def ref_or_weakmethod(item, callback: Callable[["ReferenceType"], Any]) -> "ReferenceType":
    if inspect.ismethod(item):
        return WeakMethod(item, callback)
    return ref(item, callback)


class MethodEnabledWeakSet(WeakSet):

    def add(self, item) -> None:
        if self._pending_removals:
            self._commit_removals()
        ref_item = ref_or_weakmethod(item, self._remove)
        self.data.add(ref_item)


def make_repr(instance: object, attr_names: Union[Callable, Iterable[str]] = None, exclude_none: bool = True) -> str:
    attr_names = attr_names or vars
    if callable(attr_names):
        attr_dict = attr_names(instance)
    else:
        attr_dict = {}
        for name in attr_names:
            try:
                attr_value = getattr(instance, name)
                if callable(attr_value):
                    attr_value = attr_value()
            except Exception as e:

                attr_value = f"<{e.__class__.__name__}>"
            attr_dict[name] = attr_value

    if exclude_none is True:
        attr_dict = {k: v for k, v in attr_dict.items() if v is not None}

    return f"{instance.__class__.__name__}(" + ', '.join(f"{k}={v!r}" for k, v in attr_dict.items()) + ')'

# TODO: Unfinished


class CachedClassProperty:
    def __init__(self, fget=None, doc=None):
        self.fget = fget
        if doc is None and fget is not None:
            doc = fget.__doc__
        self.__doc__ = doc
        self._name = ""

    def __set_name__(self, owner, name):
        self._name = name

    def __get__(self, obj, cls=None):
        if obj is None:
            return self
        if self.fget is None:
            raise AttributeError(f'unreadable attribute {self._name}')
        return self.fget(obj)


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
