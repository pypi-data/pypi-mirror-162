"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import os
from time import time_ns, thread_time_ns, perf_counter_ns, process_time_ns
from typing import Union, Callable
from pathlib import Path
from functools import wraps
from threading import RLock
from contextlib import contextmanager

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.general_helper.conversion import seconds2human

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


TIME_NS_FUNC_TYPE = Union[perf_counter_ns, process_time_ns, time_ns, thread_time_ns]


time_execution_path_locks: dict[Path, RLock] = {}


def get_time_execution_path_lock(path: Path) -> RLock:
    lock = time_execution_path_locks.get(path, None)
    if lock is None:
        lock = RLock()
        time_execution_path_locks[path] = lock
    return lock


@contextmanager
def time_execution(identifier: str = None,
                   time_ns_func: TIME_NS_FUNC_TYPE = perf_counter_ns,
                   output: Union[Callable, Path] = print,
                   condition: Union[bool, Callable[[], bool]] = True,
                   as_seconds: bool = True,
                   decimal_places: Union[int, None] = None,
                   also_pretty: bool = False) -> None:
    if callable(condition):
        condition = condition()
    if condition is True:
        start_time = time_ns_func()
        yield
        end_time = time_ns_func()
        full_time = end_time - start_time
        if as_seconds is True:
            from gidapptools.general_helper.conversion import ns_to_s
            full_time = ns_to_s(full_time, decimal_places=decimal_places)
            unit = 's'
            pretty = "" if also_pretty is False else f" ({seconds2human(full_time)})"
        else:
            unit = 'ns'
            pretty = "" if also_pretty is False else f" ({seconds2human(ns_to_s(full_time))})"
        identifier = 'time_execution' if identifier is None else identifier

        if isinstance(output, Path):
            with get_time_execution_path_lock(output):
                with output.open('a', encoding='utf-8', errors='ignore') as f:
                    f.write(f"{identifier} took {full_time:f} {unit}{pretty}" + '\n')
        else:
            output(f"{identifier} took {full_time:f} {unit}{pretty}")
    else:
        yield


def time_func(time_ns_func: TIME_NS_FUNC_TYPE = perf_counter_ns,
              output: Callable = print,
              use_qualname: bool = True,
              condition: Union[bool, Callable[[], bool]] = True,
              as_seconds: bool = True,
              decimal_places: int = None,
              also_pretty: bool = False):

    def _decorator(func):
        func_name = func.__name__ if use_qualname is False else func.__qualname__
        if callable(condition):
            _actual_condition = condition()
        else:
            _actual_condition = condition

        @wraps(func)
        def _wrapped(*args, **kwargs):
            with time_execution(f"executing {func_name!r}", time_ns_func=time_ns_func, output=output, as_seconds=as_seconds, decimal_places=decimal_places, condition=True, also_pretty=also_pretty):
                return func(*args, **kwargs)

        if _actual_condition:
            return _wrapped
        return func

    return _decorator


# def profile(func):
#     """
#     from `https://gist.github.com/pavelpatrin/5a28311061bf7ac55cdd`
#     """

#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         from line_profiler import LineProfiler
#         prof = LineProfiler()
#         try:
#             return prof(func)(*args, **kwargs)
#         finally:
#             prof.print_stats()

#     return wrapper


def profile(func):
    """
    Dummy decorator to be able to leave the `line_profiler`-decorator `@profile` in place,
    even when not line-profiling.
    """
    return func


def get_dummy_profile_decorator_in_globals():

    if os.getenv("LINE_PROFILE_RUNNING", "0") == "1" or __debug__ is not True:
        return

    if not isinstance(__builtins__, dict) or 'profile' not in __builtins__:
        __builtins__["profile"] = profile
    # stk = inspect.stack()[1]
    # mod = inspect.getmodule(stk[0])
    # if mod is not None:
    #     setattr(mod, "profile", profile)


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
