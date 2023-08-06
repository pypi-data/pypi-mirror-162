"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from pathlib import Path

# * Third Party Imports --------------------------------------------------------------------------------->
import pyparsing as pp

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class BaseElements:
    comma = pp.Literal(",").suppress()
    colon = pp.Literal(":").suppress()
    semi_colon = pp.Literal(";").suppress()
    period = pp.Literal(".").suppress()
    pipe = pp.Literal("|").suppress()
    at = pp.Literal("@").suppress()
    hyhphen = pp.Literal("-").suppress()

    octothorp = pp.Literal("#").suppress()
    tilde = pp.Literal("~").suppress()

    plus = pp.Literal("+").suppress()
    minus = pp.Literal("-").suppress()
    asterisk = pp.Literal("*").suppress()
    equals = pp.Literal("=").suppress()

    forward_slash = pp.Literal("/").suppress()
    back_slash = pp.Literal("/").suppress()

    single_quote = pp.Literal("'").suppress()
    double_quote = pp.Literal('"').suppress()
    any_quote = single_quote | double_quote

    parentheses_open = pp.Literal("(").suppress()
    parentheses_close = pp.Literal(")").suppress()

    brackets_open = pp.Literal("[").suppress()
    brackets_close = pp.Literal("]").suppress()

    braces_open = pp.Literal("{").suppress()
    braces_close = pp.Literal("}").suppress()


class Ligatures:
    arrow_right = pp.Literal("->").suppress()
    arrow_left = pp.Literal("<-").suppress()

    big_arrow_right = pp.Literal("-->").suppress()
    big_arrow_left = pp.Literal("<--").suppress()


# region[Main_Exec]
if __name__ == '__main__':
    x = "-"
    y = "\u2212"
    print(y)
    print(x == y)

# endregion[Main_Exec]
