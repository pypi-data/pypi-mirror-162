import attr
from typing import List, Optional, Union

from .attribute import AstAttribute
from .base import Element
from .object import AstObject


@attr.define
class AstArgument(Element):
    key: str
    op: Optional[str] = None
    label: Optional[str] = None
    value: Optional[Union[List[Element], Element]] = None

    def render(self) -> str:
        ast: Element
        if isinstance(self.value, list):
            ast = AstObject(
                self.key, op=self.op if self.op else "", elements=self.value, label=self.label
            )
        else:
            ast = AstAttribute(self.key, op=self.op if self.op else "=", value=self.value)

        return ast.render()
