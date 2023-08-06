import attr
from typing import Optional

from .base import __compiler__, Element, render

__t__ = __compiler__.compile(
    """output "{{{name}}}" {
    value = {{{render value}}}
    {{#if sensitive}}sensitive = yes{{/if}}
}
"""
)


@attr.define
class AstOutput(Element):
    name: str
    value: Optional[Element] = None
    description: Optional[str] = None
    sensitive: Optional[bool] = None

    def render(self) -> str:
        return __t__(self, helpers={"render": render})
