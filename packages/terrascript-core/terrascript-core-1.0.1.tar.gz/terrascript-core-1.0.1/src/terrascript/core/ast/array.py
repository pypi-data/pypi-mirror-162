import attr
from typing import List

from .base import Element, __compiler__, render

__t__ = __compiler__.compile(
    "[{{#each list}}{{{render this}}}{{#unless @last}},{{/unless}}{{/each}}]"
)


@attr.define
class AstArray(Element):
    list: List[Element] = attr.field(factory=list)

    def add(self, el: Element) -> None:
        self.list.append(el)

    def render(self) -> str:
        return __t__(self, helpers={"render": render})
