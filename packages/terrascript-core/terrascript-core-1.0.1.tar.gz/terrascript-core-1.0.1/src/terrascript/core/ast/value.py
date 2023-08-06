import attr
from typing import Union

from .base import __compiler__, Element, is_literal, is_heredoc, strip_literal, quote, clear_literal

__t__ = __compiler__.compile("{{{value}}}")


@attr.define
class AstNumber(Element):
    value: Union[int, float]

    def render(self) -> str:
        return __t__(self)


@attr.define
class AstString(Element):
    value: str

    def render(self) -> str:
        s = self.value
        if is_heredoc(s):
            pass

        if is_literal(self.value):
            s = strip_literal(self.value)

        else:
            s = quote(clear_literal(self.value))

        self.value = s

        return __t__(self)
