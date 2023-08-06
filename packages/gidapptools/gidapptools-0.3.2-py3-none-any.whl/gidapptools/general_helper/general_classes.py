"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import queue
import logging
from abc import ABC, abstractmethod
from typing import Any, TypeVar, Callable
from pathlib import Path
from threading import Lock
from contextlib import contextmanager

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]
log = logging.getLogger(__name__)
THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class AbstractThreadsafePool(ABC):
    __slots__ = ("_lock", "_max_size", "_prefill", "_objects", "_queue")

    def __init__(self, max_size: int = None, prefill: bool = False) -> None:
        self._lock = Lock()
        self._max_size: int = max_size or 10
        self._prefill = prefill
        self._objects: list[object] = []
        self._queue = queue.Queue(maxsize=self._max_size)
        if self._prefill is True:
            while True:
                created = self._create_if_possible()
                if created is False:
                    break

    @property
    def max_size(self) -> int:
        return self._max_size

    @property
    def amount_objects(self) -> int:
        return len(self._objects)

    @abstractmethod
    def _create_new_object(self) -> object:
        ...

    def _create_if_possible(self) -> bool:
        if self.amount_objects >= self.max_size:
            return False
        new_object = self._create_new_object()
        self._objects.append(new_object)
        self._queue.put_nowait(new_object)
        return True

    def _get_object(self) -> object:
        with self._lock:
            try:
                return self._queue.get_nowait()
            except queue.Empty:
                self._create_if_possible()
                return self._queue.get(block=True)

    @contextmanager
    def __call__(self) -> Any:
        obj = self._get_object()

        yield obj

        self._queue.put_nowait(obj)
        self._queue.task_done()

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(max_size={self.max_size!r}, prefill={self._prefill!r})'


class GenericThreadsafePool(AbstractThreadsafePool):
    __slots__ = ("_obj_creator",)

    def __init__(self, obj_creator: Callable, max_size: int = 0, prefill: bool = False) -> None:
        self._obj_creator = obj_creator
        super().__init__(max_size=max_size, prefill=prefill)

    def _create_new_object(self) -> object:

        return self._obj_creator()

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(obj_creator={self._obj_creator!r}, max_size={self.max_size!r}, prefill={self._prefill!r})'


T = TypeVar('T')


class DecorateAbleList(list):

    def decorate_append(self, item: T) -> T:
        self.append(item)
        return item

# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
