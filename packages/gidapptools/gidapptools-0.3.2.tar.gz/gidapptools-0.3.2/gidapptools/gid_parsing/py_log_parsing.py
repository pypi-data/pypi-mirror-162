"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from pathlib import Path

# * Third Party Imports --------------------------------------------------------------------------------->
import pyparsing as ppa
import pyparsing.common as ppc

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.gid_parsing.tokens.base_tokens import BaseTokenWithPos
from gidapptools.gid_parsing.universal.datetime_elements import get_grammar_from_dt_format
from gidapptools.gid_parsing.universal.character_elements import Ligatures, BaseElements

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class LineNumberToken(BaseTokenWithPos):

    def __init__(self, start: int, end: int, value: int) -> None:
        super().__init__(start, end)
        self.line_number = value


class LogLevelToken(BaseTokenWithPos):

    def __init__(self, start: int, end: int, value: str) -> None:
        super().__init__(start, end)
        self.log_level = value


class ThreadNameToken(BaseTokenWithPos):

    def __init__(self, start: int, end: int, value: str) -> None:
        super().__init__(start, end)
        self.thread_name = value


class ModuleNameToken(BaseTokenWithPos):

    def __init__(self, start: int, end: int, value: str) -> None:
        super().__init__(start, end)
        self.module_name = value
        self.module_name_parts = tuple(self.module_name.split('.'))

    @property
    def parent_module_name(self) -> str:
        try:
            return self.module_name_parts[-2]
        except IndexError:
            return "__main__"


class FunctionNameToken(BaseTokenWithPos):

    def __init__(self, start: int, end: int, value: str) -> None:
        super().__init__(start, end)
        self.function_name = value


class MessageToken(BaseTokenWithPos):

    def __init__(self, start: int, end: int, value: str) -> None:
        super().__init__(start, end)
        self.message = value


class GeneralGrammar:
    _cached_grammar: ppa.ParserElement = None

    @property
    def ___grammar___(self) -> ppa.ParserElement:
        if self._cached_grammar is None:
            self.__class__._cached_grammar = self._construct_grammar()
        return self._cached_grammar

    def _construct_grammar(self):
        non_pipe_printables = ppa.printables.replace("|", "")
        time_stamp_part = get_grammar_from_dt_format("%Y-%m-%d %H:%M:%S.%f %Z")("time_stamp")
        line_number_part = ppa.locatedExpr(ppa.Word(ppa.nums).set_parse_action(ppc.convert_to_integer)).set_parse_action(LineNumberToken.from_parse_action)("line_number")
        level_part = ppa.locatedExpr(ppa.Keyword("DEBUG") | ppa.Keyword("INFO") | ppa.Keyword("CRITICAL") | ppa.Keyword("ERROR")).set_parse_action(LogLevelToken.from_parse_action)("level")
        thread_name_part = ppa.locatedExpr(ppa.Word(non_pipe_printables)("thread")).set_parse_action(ThreadNameToken.from_parse_action)("thread")
        module_name_part = ppa.locatedExpr(ppa.Word(non_pipe_printables)).set_parse_action(ModuleNameToken.from_parse_action)("module")
        function_name_part = ppa.locatedExpr(ppa.Word(non_pipe_printables)).set_parse_action(FunctionNameToken.from_parse_action)("function")
        return time_stamp_part + BaseElements.pipe + line_number_part + BaseElements.pipe + level_part + BaseElements.pipe + thread_name_part + BaseElements.pipe + \
            module_name_part + BaseElements.pipe + function_name_part + BaseElements.pipe + BaseElements.pipe + Ligatures.big_arrow_right + ppa.locatedExpr(ppa.rest_of_line).set_parse_action(MessageToken.from_parse_action)("message")

    def __call__(self, text: str) -> dict[str, BaseTokenWithPos]:
        return self.___grammar___.parse_string(text, parse_all=True).as_dict()


# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
