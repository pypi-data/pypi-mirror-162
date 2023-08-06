import attr
from typing import Dict, Optional

from .base import __compiler__, Element, render

__t__ = __compiler__.compile(
    """{
{{#each map}}
    {{{@key}}} = {{{render this}}}
{{/each}}
}"""
)


@attr.define
class AstMap(Element):
    map: Dict[str, Element] = attr.field(factory=dict)

    def set(self, key: str, el: Element) -> None:
        self.map[key] = el

    def get(self, key: str) -> Optional[Element]:
        return self.map.get(key)

    def render(self) -> str:
        return __t__(self, helpers={"render": render})
