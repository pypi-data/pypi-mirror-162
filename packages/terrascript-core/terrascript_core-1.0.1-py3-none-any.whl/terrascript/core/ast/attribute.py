import attr
from typing import List, Optional, Union

from .base import Element, __compiler__, render

__t__ = __compiler__.compile("{{{key}}}{{#if op}} {{{op}}} {{/if}}{{{render value}}}")


@attr.define
class AstAttribute(Element):
    key: str
    op: str = "="
    value: Optional[Union[List[Element], Element]] = None

    def render(self) -> str:
        return __t__(self, helpers={"render": render})
