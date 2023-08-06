"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import re
from pathlib import Path

# * Third Party Imports --------------------------------------------------------------------------------->
from frozendict import frozendict

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]

DATETIME_FORMAT_REGEX_MAPPING: frozendict[str, str] = frozendict(**{r"%Y": r"(?P<year>\d{4})",
                                                                    r"%m": r"(?P<month>[01]?\d)",
                                                                    r"%d": r"(?P<day>[0123]?\d)",
                                                                    r"%H": r"(?P<hour>[012]?\d)",
                                                                    r"%M": r"(?P<minute>[0-5]?\d)",
                                                                    r"%S": r"(?P<second>[0-5]?\d)",
                                                                    r"%f": r"(?P<microsecond>\d+)",
                                                                    r"%Z": r"(?P<tzinfo>[a-zA-Z]+([+-]\d{2}(\:\d{2})?)?)"})


def datetime_format_to_regex(in_format: str, flags: re.RegexFlag) -> re.Pattern:
    pattern_string = in_format
    for k, v in DATETIME_FORMAT_REGEX_MAPPING.items():
        pattern_string = pattern_string.replace(k, v)
    return re.compile(pattern_string, flags)

    # region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
