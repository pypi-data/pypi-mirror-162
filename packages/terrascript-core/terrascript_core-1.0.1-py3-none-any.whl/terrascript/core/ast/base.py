from abc import abstractmethod, ABC
from pybars import Compiler
from typing import Any

from pydash import starts_with, is_blank, trim, ends_with, replace, lines


__compiler__ = Compiler()


class Element(ABC):
    @abstractmethod
    def render(self) -> str:
        pass


def quote(s: str) -> str:
    return f'"{s}"'


def heredoc(s: str) -> str:
    return f"<<EOF\n{s}\nEOF"


def heredoci(s: str) -> str:
    return f"<<-EOF\n{s}\nEOF"


def is_heredoc(s: str) -> bool:
    lns = lines(s)
    if len(lns) > 0:
        line = lns[0]

        token = None
        if starts_with(line, "<<"):
            token = line[2:]
        elif starts_with(line, "<<-"):
            token = line[:-3]

        if not is_blank(token) and ends_with(s, token):
            return True

    return False


def interpolate(s: str) -> str:
    return f"${{{s}}}"


def literal(s: str) -> str:
    return f"{{%l {s} %}}"


def is_literal(s: str) -> bool:
    s = trim(s)
    return starts_with(s, "{%l") and ends_with(s, "%}")


def strip_literal(s: str) -> str:
    if is_literal(s):
        return s[3:-2]

    return s


def clear_literal(s: str) -> str:
    s = trim(s)
    if starts_with(s, "${") and ends_with(s, "}"):
        return replace(replace(s, "{%l", ""), "%}", "")

    return s


def render(_this: Any, el: Element) -> str:
    return el.render()
